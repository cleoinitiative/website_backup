"""Embedding generation using OpenAI API.

Much lower RAM usage than local models - no PyTorch required.
"""

from dataclasses import dataclass, field
from typing import Optional
import asyncio
import hashlib
import logging
import os
import time

import numpy as np
from openai import OpenAI, AsyncOpenAI

logger = logging.getLogger(__name__)


@dataclass
class OpenAIEmbeddingConfig:
    """Configuration for OpenAI embedding generation."""
    
    # Model options:
    # - "text-embedding-3-small" (1536d, cheapest, good quality)
    # - "text-embedding-3-large" (3072d, best quality)
    # - "text-embedding-ada-002" (1536d, legacy)
    model_name: str = "text-embedding-3-small"
    batch_size: int = 100  # OpenAI allows up to 2048
    
    # Caching
    cache_enabled: bool = True
    cache_max_size: int = 1000
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0


@dataclass
class EmbeddedChunk:
    """A chunk with its embedding vector."""
    
    text: str
    embedding: list[float]
    chunk_id: str
    chunk_index: int
    source_path: str
    token_count: int
    
    start_char: int = 0
    end_char: int = 0
    metadata: dict = field(default_factory=dict)


class EmbeddingCache:
    """LRU cache for query embeddings."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: dict[str, list[float]] = {}
        self._access_order: list[str] = []
    
    def _make_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[list[float]]:
        key = self._make_key(text)
        if key in self._cache:
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None
    
    def put(self, text: str, embedding: list[float]) -> None:
        key = self._make_key(text)
        if key in self._cache:
            self._access_order.remove(key)
            self._access_order.append(key)
            return
        while len(self._cache) >= self.max_size:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        self._cache[key] = embedding
        self._access_order.append(key)
    
    def clear(self) -> None:
        self._cache.clear()
        self._access_order.clear()
    
    @property
    def size(self) -> int:
        return len(self._cache)


class OpenAIEmbedder:
    """
    Generate embeddings using OpenAI's API.
    
    Benefits over local models:
    - Much lower RAM (~50MB vs ~1GB)
    - No PyTorch/transformers dependencies
    - Faster cold starts
    - High quality embeddings
    
    Cost: ~$0.00002 per 1K tokens with text-embedding-3-small
    """
    
    # Embedding dimensions by model
    DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }
    
    def __init__(self, config: OpenAIEmbeddingConfig | None = None):
        self.config = config or OpenAIEmbeddingConfig()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        self._cache = EmbeddingCache(max_size=self.config.cache_max_size) if self.config.cache_enabled else None
    
    @property
    def embedding_dimension(self) -> int:
        return self.DIMENSIONS.get(self.config.model_name, 1536)
    
    @property
    def cache(self) -> Optional[EmbeddingCache]:
        return self._cache
    
    def _embed_with_retry(self, texts: list[str]) -> np.ndarray:
        """Embed texts with retry logic."""
        last_error = None
        delay = self.config.retry_delay
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.client.embeddings.create(
                    model=self.config.model_name,
                    input=texts,
                )
                embeddings = [item.embedding for item in response.data]
                return np.array(embeddings)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    logger.warning(f"Embedding failed (attempt {attempt + 1}): {e}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay *= self.config.retry_backoff
        
        raise RuntimeError(f"Embedding failed after {self.config.max_retries + 1} attempts: {last_error}")
    
    async def _embed_with_retry_async(self, texts: list[str]) -> np.ndarray:
        """Embed texts with retry logic (async)."""
        last_error = None
        delay = self.config.retry_delay
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self.async_client.embeddings.create(
                    model=self.config.model_name,
                    input=texts,
                )
                embeddings = [item.embedding for item in response.data]
                return np.array(embeddings)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    logger.warning(f"Embedding failed (attempt {attempt + 1}): {e}. Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    delay *= self.config.retry_backoff
        
        raise RuntimeError(f"Embedding failed after {self.config.max_retries + 1} attempts: {last_error}")
    
    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        if not texts:
            return np.array([])
        
        # Process in batches
        all_embeddings = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            embeddings = self._embed_with_retry(batch)
            all_embeddings.append(embeddings)
        
        return np.vstack(all_embeddings) if all_embeddings else np.array([])
    
    def embed_chunks(self, chunks: list) -> list[EmbeddedChunk]:
        """Generate embeddings for Chunk objects."""
        if not chunks:
            return []
        
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embed_texts(texts)
        
        embedded_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            embedded_chunks.append(EmbeddedChunk(
                text=chunk.text,
                embedding=embedding.tolist(),
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                source_path=chunk.source_path,
                token_count=chunk.token_count,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
            ))
        
        return embedded_chunks
    
    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a search query."""
        if self._cache is not None:
            cached = self._cache.get(query)
            if cached is not None:
                return cached
        
        embeddings = self.embed_texts([query])
        result = embeddings[0].tolist()
        
        if self._cache is not None:
            self._cache.put(query, result)
        
        return result
    
    async def embed_texts_async(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings asynchronously."""
        if not texts:
            return np.array([])
        
        all_embeddings = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            embeddings = await self._embed_with_retry_async(batch)
            all_embeddings.append(embeddings)
        
        return np.vstack(all_embeddings) if all_embeddings else np.array([])
    
    async def embed_query_async(self, query: str) -> list[float]:
        """Generate embedding for a search query asynchronously."""
        if self._cache is not None:
            cached = self._cache.get(query)
            if cached is not None:
                return cached
        
        embeddings = await self._embed_with_retry_async([query])
        result = embeddings[0].tolist()
        
        if self._cache is not None:
            self._cache.put(query, result)
        
        return result
    
    async def embed_chunks_async(self, chunks: list) -> list[EmbeddedChunk]:
        """Generate embeddings for chunks asynchronously."""
        if not chunks:
            return []
        
        texts = [chunk.text for chunk in chunks]
        embeddings = await self.embed_texts_async(texts)
        
        embedded_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            embedded_chunks.append(EmbeddedChunk(
                text=chunk.text,
                embedding=embedding.tolist(),
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                source_path=chunk.source_path,
                token_count=chunk.token_count,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
            ))
        
        return embedded_chunks
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        if self._cache is not None:
            self._cache.clear()
