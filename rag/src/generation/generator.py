"""LLM-based response generation for RAG using OpenAI."""

from dataclasses import dataclass, field
from typing import Optional, Iterator, AsyncIterator, Any
import asyncio
import logging
import os
import time

from openai import OpenAI, AsyncOpenAI

logger = logging.getLogger(__name__)


@dataclass
class GeneratorConfig:
    """Configuration for LLM generation."""
    
    model_name: str = "gpt-4o-mini"  # Cost-effective default
    api_key: Optional[str] = None
    
    # Generation parameters
    temperature: float = 0.1  # Low for factual RAG
    max_tokens: int = 1024
    top_p: float = 1.0
    
    # Context formatting
    max_context_tokens: int = 4000
    chunk_separator: str = "\n\n---\n\n"
    include_source_in_context: bool = True
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")


@dataclass
class GeneratedResponse:
    """A generated response with metadata."""
    
    content: str
    model: str
    
    # Token usage
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Sources used
    sources: list[str] = field(default_factory=list)
    
    # Timing
    generation_time_ms: float = 0.0
    
    # Raw response for debugging
    raw_response: Optional[Any] = None


class Generator:
    """
    LLM-based response generator for RAG using OpenAI.
    
    Features:
    - Automatic context truncation
    - Source citation formatting
    - Streaming support (sync and async)
    - Retry with exponential backoff
    - Full async API support
    """
    
    def __init__(self, config: GeneratorConfig | None = None):
        self.config = config or GeneratorConfig()
        self._client: Optional[OpenAI] = None
        self._async_client: Optional[AsyncOpenAI] = None
    
    @property
    def client(self) -> OpenAI:
        """Lazy-initialize sync client."""
        if self._client is None:
            self._client = OpenAI(api_key=self.config.api_key)
        return self._client
    
    @property
    def async_client(self) -> AsyncOpenAI:
        """Lazy-initialize async client."""
        if self._async_client is None:
            self._async_client = AsyncOpenAI(api_key=self.config.api_key)
        return self._async_client
    
    def format_context(self, results: list) -> tuple[str, list[str]]:
        """
        Format retrieval results into context string.
        
        Args:
            results: List of RetrievalResult or SearchResult objects
            
        Returns:
            Tuple of (formatted_context, list_of_sources)
        """
        if not results:
            return "", []
        
        chunks = []
        sources = []
        
        for result in results:
            source = getattr(result, 'source_path', 'Unknown')
            source_name = source.split('/')[-1] if '/' in source else source
            
            if source not in sources:
                sources.append(source)
            
            if self.config.include_source_in_context:
                chunk_text = f"[Source: {source_name}]\n{result.text}"
            else:
                chunk_text = result.text
            
            chunks.append(chunk_text)
        
        context = self.config.chunk_separator.join(chunks)
        
        # Truncate if too long (~4 chars per token)
        max_chars = self.config.max_context_tokens * 4
        if len(context) > max_chars:
            context = context[:max_chars] + "\n\n[Context truncated...]"
        
        return context, sources
    
    def generate(
        self,
        query: str,
        results: list,
        prompt_template=None,
        system_message: Optional[str] = None,
        **extra_kwargs,
    ) -> GeneratedResponse:
        """
        Generate a response using retrieved context.
        
        Args:
            query: User's question
            results: Retrieved chunks (RetrievalResult or SearchResult)
            prompt_template: Optional PromptTemplate (uses RAG_PROMPT if not provided)
            system_message: Optional override for system message
            **extra_kwargs: Additional template variables
            
        Returns:
            GeneratedResponse with generated content and metadata
        """
        from .prompts import RAG_PROMPT
        
        template = prompt_template or RAG_PROMPT
        context, sources = self.format_context(results)
        
        sys_msg, user_msg = template.format(
            query=query,
            context=context,
            **extra_kwargs,
        )
        
        if system_message:
            sys_msg = system_message
        
        start_time = time.time()
        response = self._generate_with_retry(sys_msg, user_msg)
        generation_time = (time.time() - start_time) * 1000
        
        response.sources = sources
        response.generation_time_ms = generation_time
        
        return response
    
    def _generate_with_retry(self, system_msg: str, user_msg: str) -> GeneratedResponse:
        """Generate with retry logic."""
        last_error = None
        delay = self.config.retry_delay
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    top_p=self.config.top_p,
                )
                
                return GeneratedResponse(
                    content=response.choices[0].message.content,
                    model=self.config.model_name,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    raw_response=response,
                )
                
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    logger.warning(f"OpenAI error (attempt {attempt + 1}): {e}")
                    time.sleep(delay)
                    delay *= self.config.retry_backoff
        
        raise RuntimeError(f"OpenAI generation failed: {last_error}")
    
    def generate_stream(
        self,
        query: str,
        results: list,
        prompt_template=None,
    ) -> Iterator[str]:
        """
        Generate a streaming response.
        
        Yields content chunks as they arrive.
        """
        from .prompts import RAG_PROMPT
        
        template = prompt_template or RAG_PROMPT
        context, _ = self.format_context(results)
        sys_msg, user_msg = template.format(query=query, context=context)
        
        stream = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    # =========================================================================
    # Async API
    # =========================================================================
    
    async def generate_async(
        self,
        query: str,
        results: list,
        prompt_template=None,
        system_message: Optional[str] = None,
        **extra_kwargs,
    ) -> GeneratedResponse:
        """
        Generate a response asynchronously.
        
        Args:
            query: User's question
            results: Retrieved chunks (RetrievalResult or SearchResult)
            prompt_template: Optional PromptTemplate (uses RAG_PROMPT if not provided)
            system_message: Optional override for system message
            **extra_kwargs: Additional template variables
            
        Returns:
            GeneratedResponse with generated content and metadata
        """
        from .prompts import RAG_PROMPT
        
        template = prompt_template or RAG_PROMPT
        context, sources = self.format_context(results)
        
        sys_msg, user_msg = template.format(
            query=query,
            context=context,
            **extra_kwargs,
        )
        
        if system_message:
            sys_msg = system_message
        
        start_time = time.time()
        response = await self._generate_async_with_retry(sys_msg, user_msg)
        generation_time = (time.time() - start_time) * 1000
        
        response.sources = sources
        response.generation_time_ms = generation_time
        
        return response
    
    async def _generate_async_with_retry(self, system_msg: str, user_msg: str) -> GeneratedResponse:
        """Generate asynchronously with retry logic."""
        last_error = None
        delay = self.config.retry_delay
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self.async_client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    top_p=self.config.top_p,
                )
                
                return GeneratedResponse(
                    content=response.choices[0].message.content,
                    model=self.config.model_name,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    raw_response=response,
                )
                
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    logger.warning(f"OpenAI async error (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(delay)
                    delay *= self.config.retry_backoff
        
        raise RuntimeError(f"OpenAI async generation failed: {last_error}")
    
    async def generate_stream_async(
        self,
        query: str,
        results: list,
        prompt_template=None,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response asynchronously.
        
        Yields content chunks as they arrive.
        """
        from .prompts import RAG_PROMPT
        
        template = prompt_template or RAG_PROMPT
        context, _ = self.format_context(results)
        sys_msg, user_msg = template.format(query=query, context=context)
        
        stream = await self.async_client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
