"""Embedding generation using Sentence Transformers."""

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional
import asyncio
import hashlib
import logging
import time

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    
    # Default: all-MiniLM-L6-v2 (384d, fast, good quality)
    # Higher quality: "BAAI/bge-base-en-v1.5" (768d, slower)
    model_name: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    device: str = "cpu"  # "cpu", "cuda", "mps"
    normalize: bool = True  # L2 normalize embeddings
    
    # Caching
    cache_enabled: bool = True
    cache_max_size: int = 1000  # Max number of cached query embeddings
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 0.5  # Initial delay in seconds
    retry_backoff: float = 2.0  # Exponential backoff multiplier


@dataclass
class EmbeddedChunk:
    """A chunk with its embedding vector."""
    
    text: str
    embedding: list[float]
    chunk_id: str
    chunk_index: int
    source_path: str
    token_count: int
    
    # Optional metadata
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
        """Create a cache key from text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[list[float]]:
        """Get embedding from cache if present."""
        key = self._make_key(text)
        if key in self._cache:
            # Move to end (most recently used)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None
    
    def put(self, text: str, embedding: list[float]) -> None:
        """Add embedding to cache."""
        key = self._make_key(text)
        
        if key in self._cache:
            # Already in cache, just update access order
            self._access_order.remove(key)
            self._access_order.append(key)
            return
        
        # Evict oldest if at capacity
        while len(self._cache) >= self.max_size:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        self._cache[key] = embedding
        self._access_order.append(key)
    
    def clear(self) -> None:
        """Clear all cached embeddings."""
        self._cache.clear()
        self._access_order.clear()
    
    @property
    def size(self) -> int:
        """Current number of cached embeddings."""
        return len(self._cache)


class Embedder:
    """
    Generate embeddings for text chunks using Sentence Transformers.
    
    Features:
    - Local models - no API key required, runs on CPU/GPU/MPS
    - Query embedding caching for repeated queries
    - Retry logic with exponential backoff
    - Async support for non-blocking operations
    """
    
    def __init__(self, config: EmbeddingConfig | None = None):
        self.config = config or EmbeddingConfig()
        self.model = SentenceTransformer(
            self.config.model_name,
            device=self.config.device,
        )
        self._cache = EmbeddingCache(max_size=self.config.cache_max_size) if self.config.cache_enabled else None
    
    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model."""
        return self.model.get_sentence_embedding_dimension()
    
    @property
    def cache(self) -> Optional[EmbeddingCache]:
        """Access the embedding cache."""
        return self._cache
    
    def _embed_with_retry(self, texts: list[str]) -> np.ndarray:
        """
        Embed texts with retry logic and exponential backoff.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            NumPy array of embeddings
            
        Raises:
            RuntimeError: If all retries fail
        """
        last_error = None
        delay = self.config.retry_delay
        
        for attempt in range(self.config.max_retries + 1):
            try:
                embeddings = self.model.encode(
                    texts,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                    normalize_embeddings=self.config.normalize,
                )
                return np.array(embeddings)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    logger.warning(
                        f"Embedding failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= self.config.retry_backoff
        
        raise RuntimeError(f"Embedding failed after {self.config.max_retries + 1} attempts: {last_error}")
    
    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            NumPy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])
        
        return self._embed_with_retry(texts)
    
    def embed_chunks(self, chunks: list) -> list[EmbeddedChunk]:
        """
        Generate embeddings for a list of Chunk objects.
        
        Args:
            chunks: List of Chunk objects from the chunker
            
        Returns:
            List of EmbeddedChunk objects with embeddings
        """
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
        """
        Generate embedding for a search query.
        
        Uses cache for repeated queries if caching is enabled.
        
        Args:
            query: Search query string
            
        Returns:
            Embedding vector as a list of floats
        """
        # Check cache first
        if self._cache is not None:
            cached = self._cache.get(query)
            if cached is not None:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return cached
        
        # Generate embedding
        embeddings = self.embed_texts([query])
        result = embeddings[0].tolist()
        
        # Cache the result
        if self._cache is not None:
            self._cache.put(query, result)
        
        return result
    
    async def embed_texts_async(self, texts: list[str]) -> np.ndarray:
        """
        Generate embeddings asynchronously.
        
        Runs the embedding in a thread pool to avoid blocking the event loop.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            NumPy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed_texts, texts)
    
    async def embed_query_async(self, query: str) -> list[float]:
        """
        Generate embedding for a search query asynchronously.
        
        Args:
            query: Search query string
            
        Returns:
            Embedding vector as a list of floats
        """
        # Check cache first (synchronous, fast)
        if self._cache is not None:
            cached = self._cache.get(query)
            if cached is not None:
                return cached
        
        # Generate embedding in executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.embed_query, query)
        return result
    
    async def embed_chunks_async(self, chunks: list) -> list[EmbeddedChunk]:
        """
        Generate embeddings for chunks asynchronously.
        
        Args:
            chunks: List of Chunk objects from the chunker
            
        Returns:
            List of EmbeddedChunk objects with embeddings
        """
        if not chunks:
            return []
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed_chunks, chunks)
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        if self._cache is not None:
            self._cache.clear()
            logger.debug("Embedding cache cleared")
