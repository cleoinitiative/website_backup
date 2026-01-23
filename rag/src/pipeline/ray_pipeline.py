"""RAG pipeline for document processing.

Ray Data is optional - only needed for large-scale distributed processing.
For most use cases, use run_simple() which works without Ray.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any, AsyncIterator
import asyncio
import logging
import hashlib

# Ray is optional - only import if available
try:
    import ray
    from ray.data import Dataset
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False
    ray = None
    Dataset = None

from ..parsers import parse_file, get_supported_extensions, ParsedDocument
from ..chunking import TextChunker, ChunkingConfig, Chunk
from ..embeddings import Embedder, EmbeddingConfig, EmbeddedChunk, OpenAIEmbedder, OpenAIEmbeddingConfig
from ..storage import VectorStore, VectorStoreConfig


logger = logging.getLogger(__name__)


def compute_file_hash(file_path: Path) -> str:
    """Compute MD5 hash of file contents for change detection."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


@dataclass
class PipelineConfig:
    """Configuration for the RAG pipeline."""
    
    # Input
    input_path: str = "./documents"
    file_extensions: list[str] = field(default_factory=get_supported_extensions)
    recursive: bool = True
    
    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 50
    min_chunk_size: int = 100
    
    # Embeddings
    # Set use_openai_embeddings=True for low RAM usage (recommended for production)
    use_openai_embeddings: bool = True  # Use OpenAI API instead of local model
    openai_embedding_model: str = "text-embedding-3-small"  # OpenAI model
    
    # Local embeddings (only used if use_openai_embeddings=False)
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    embedding_batch_size: int = 32
    embedding_device: str = "cpu"  # "cpu", "cuda", "mps"
    
    # Storage
    db_path: str = "./rag_db"
    table_name: str = "documents"
    
    # Ray settings
    num_cpus: Optional[int] = None  # None = use all available
    num_gpus: Optional[int] = None
    ray_address: Optional[str] = None  # None = local, or "auto" for cluster
    
    # Batching for Ray
    parsing_concurrency: int = 4
    embedding_concurrency: int = 2
    write_batch_size: int = 100
    
    # Incremental ingestion
    incremental: bool = True  # Skip unchanged files
    
    # Retrieval settings
    use_reranking: bool = True
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    use_mmr: bool = True
    mmr_lambda: float = 0.7  # Balance relevance vs diversity
    initial_k: int = 20  # Candidates for reranking
    
    # Generation settings (OpenAI)
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024


class RAGPipeline:
    """
    Scalable RAG pipeline using Ray Data.
    
    Processes documents through:
    1. File discovery
    2. Parallel parsing (PDF, HTML, TXT)
    3. Chunking with overlap
    4. Batch embedding generation
    5. LanceDB storage
    
    Retrieval features:
    - Vector similarity search
    - Cross-encoder reranking
    - MMR for diversity
    - LLM-based response generation (OpenAI)
    
    Scales from laptop to cluster with the same code.
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self._ray_initialized = False
        self._embedder = None
        self._chunker = None
        self._vector_store = None
        self._retriever = None
        self._generator = None
        self._reranker = None
    
    @property
    def embedder(self):
        """Lazy-initialize embedder (OpenAI or local)."""
        if self._embedder is None:
            if self.config.use_openai_embeddings:
                logger.info(f"Using OpenAI embeddings: {self.config.openai_embedding_model}")
                self._embedder = OpenAIEmbedder(OpenAIEmbeddingConfig(
                    model_name=self.config.openai_embedding_model,
                    batch_size=self.config.embedding_batch_size,
                ))
            else:
                logger.info(f"Using local embeddings: {self.config.embedding_model}")
                self._embedder = Embedder(EmbeddingConfig(
                    model_name=self.config.embedding_model,
                    batch_size=self.config.embedding_batch_size,
                    device=self.config.embedding_device,
                ))
        return self._embedder
    
    @property
    def chunker(self) -> TextChunker:
        """Lazy-initialize chunker."""
        if self._chunker is None:
            self._chunker = TextChunker(ChunkingConfig(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
                min_chunk_size=self.config.min_chunk_size,
            ))
        return self._chunker
    
    @property
    def vector_store(self) -> VectorStore:
        """Lazy-initialize vector store."""
        if self._vector_store is None:
            self._vector_store = VectorStore(VectorStoreConfig(
                db_path=self.config.db_path,
                table_name=self.config.table_name,
                embedding_dim=self.embedder.embedding_dimension,
            ))
        return self._vector_store
    
    @property
    def retriever(self):
        """Lazy-initialize advanced retriever."""
        if self._retriever is None:
            from ..retrieval import Retriever, RetrievalConfig
            self._retriever = Retriever(
                embedder=self.embedder,
                vector_store=self.vector_store,
                config=RetrievalConfig(
                    initial_k=self.config.initial_k,
                    use_reranking=self.config.use_reranking,
                    rerank_model=self.config.rerank_model,
                    rerank_device=self.config.embedding_device,
                    use_mmr=self.config.use_mmr,
                    mmr_lambda=self.config.mmr_lambda,
                ),
            )
        return self._retriever
    
    @property
    def generator(self):
        """Lazy-initialize LLM generator."""
        if self._generator is None:
            from ..generation import Generator, GeneratorConfig
            self._generator = Generator(GeneratorConfig(
                model_name=self.config.llm_model,
                temperature=self.config.llm_temperature,
                max_tokens=self.config.llm_max_tokens,
            ))
        return self._generator
    
    @property
    def reranker(self):
        """Lazy-initialize reranker."""
        if self._reranker is None and self.config.use_reranking:
            from ..reranking import Reranker, RerankerConfig
            self._reranker = Reranker(RerankerConfig(
                model_name=self.config.rerank_model,
                device=self.config.embedding_device,
            ))
        return self._reranker
    
    def _init_ray(self) -> None:
        """Initialize Ray if not already running."""
        if not RAY_AVAILABLE:
            raise ImportError(
                "Ray is not installed. Install with: pip install 'ray[data]'\n"
                "Or use run_simple() which doesn't require Ray."
            )
        
        if self._ray_initialized:
            return
        
        if not ray.is_initialized():
            ray.init(
                address=self.config.ray_address,
                num_cpus=self.config.num_cpus,
                num_gpus=self.config.num_gpus,
                logging_level=logging.WARNING,
            )
        self._ray_initialized = True
    
    def discover_files(self) -> list[Path]:
        """Discover all supported files in input path."""
        input_path = Path(self.config.input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input path not found: {input_path}")
        
        if input_path.is_file():
            return [input_path]
        
        files = []
        pattern = "**/*" if self.config.recursive else "*"
        
        for ext in self.config.file_extensions:
            files.extend(input_path.glob(f"{pattern}{ext}"))
        
        return sorted(files)
    
    def run(self) -> dict:
        """
        Run the full pipeline.
        
        Returns:
            Statistics about the pipeline run
        """
        self._init_ray()
        
        # Discover files
        files = self.discover_files()
        if not files:
            logger.warning(f"No files found in {self.config.input_path}")
            return {"files_processed": 0, "chunks_created": 0}
        
        logger.info(f"Found {len(files)} files to process")
        
        # Create Ray dataset from file paths
        ds = ray.data.from_items([{"path": str(f)} for f in files])
        
        # Define processing functions
        def parse_document(row: dict) -> dict:
            """Parse a single document."""
            try:
                doc = parse_file(row["path"])
                return {
                    "content": doc.content,
                    "source_path": doc.source_path,
                    "file_type": doc.file_type,
                    "title": doc.title or "",
                    "parse_error": None,
                }
            except Exception as e:
                logger.warning(f"Failed to parse {row['path']}: {e}")
                return {
                    "content": "",
                    "source_path": row["path"],
                    "file_type": "",
                    "title": "",
                    "parse_error": str(e),
                }
        
        def chunk_document(row: dict) -> list[dict]:
            """Chunk a parsed document."""
            if row["parse_error"] or not row["content"]:
                return []
            
            chunks = self.chunker.chunk_text(row["content"], row["source_path"])
            return [
                {
                    "text": chunk.text,
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "source_path": chunk.source_path,
                    "token_count": chunk.token_count,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                }
                for chunk in chunks
            ]
        
        def embed_batch(batch: dict) -> dict:
            """Embed a batch of chunks."""
            texts = batch["text"]
            embeddings = self.embedder.embed_texts(list(texts))
            batch["embedding"] = [emb.tolist() for emb in embeddings]
            return batch
        
        # Build and execute pipeline
        processed_ds = (
            ds
            .map(parse_document, concurrency=self.config.parsing_concurrency)
            .filter(lambda row: not row["parse_error"])
            .flat_map(chunk_document)
        )
        
        # Embed in batches
        embedded_ds = processed_ds.map_batches(
            embed_batch,
            batch_size=self.config.embedding_batch_size,
            concurrency=self.config.embedding_concurrency,
        )
        
        # Collect results and write to LanceDB
        all_chunks = embedded_ds.take_all()
        
        if all_chunks:
            # Convert to EmbeddedChunk objects
            embedded_chunks = [
                EmbeddedChunk(
                    text=row["text"],
                    embedding=row["embedding"],
                    chunk_id=row["chunk_id"],
                    chunk_index=row["chunk_index"],
                    source_path=row["source_path"],
                    token_count=row["token_count"],
                    start_char=row["start_char"],
                    end_char=row["end_char"],
                )
                for row in all_chunks
            ]
            
            # Add to vector store
            self.vector_store.add(embedded_chunks)
        
        stats = {
            "files_found": len(files),
            "chunks_created": len(all_chunks),
            "db_path": self.config.db_path,
            "table_name": self.config.table_name,
        }
        
        logger.info(f"Pipeline complete: {stats}")
        return stats
    
    def run_simple(self) -> dict:
        """
        Run pipeline without Ray (simpler, for small datasets).
        
        Returns:
            Statistics about the pipeline run
        """
        files = self.discover_files()
        if not files:
            return {"files_processed": 0, "chunks_created": 0}
        
        files_processed = 0
        files_skipped = 0
        chunks_created = 0
        errors = []
        
        for file_path in files:
            try:
                # Check if file has changed (incremental mode)
                if self.config.incremental:
                    current_hash = compute_file_hash(file_path)
                    stored_hash = self.vector_store.get_file_hash(str(file_path.absolute()))
                    
                    if stored_hash == current_hash:
                        logger.debug(f"Skipping unchanged file: {file_path}")
                        files_skipped += 1
                        continue
                else:
                    current_hash = None
                
                # Parse
                doc = parse_file(file_path)
                
                # Chunk
                chunks = self.chunker.chunk_document(doc)
                
                # Embed
                embedded = self.embedder.embed_chunks(chunks)
                
                # Store with hash for incremental updates
                if self.config.incremental and current_hash:
                    self.vector_store.add_with_hash(
                        embedded, 
                        str(file_path.absolute()), 
                        current_hash
                    )
                else:
                    self.vector_store.add(embedded)
                
                chunks_created += len(embedded)
                files_processed += 1
                logger.debug(f"Processed {file_path}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")
                errors.append({"file": str(file_path), "error": str(e)})
        
        return {
            "files_found": len(files),
            "files_processed": files_processed,
            "files_skipped": files_skipped,
            "chunks_created": chunks_created,
            "errors": errors,
            "db_path": self.config.db_path,
        }
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filter_expr: Optional[str] = None,
    ) -> list:
        """
        Search for relevant chunks (basic vector search).
        
        Args:
            query: Search query
            limit: Number of results
            filter_expr: Optional filter (e.g., "source_path LIKE '%report%'")
            
        Returns:
            List of SearchResult objects
        """
        query_embedding = self.embedder.embed_query(query)
        return self.vector_store.search(query_embedding, limit, filter_expr)
    
    def retrieve(
        self,
        query: str,
        limit: int = 5,
        filter_expr: Optional[str] = None,
        use_reranking: Optional[bool] = None,
        use_mmr: Optional[bool] = None,
    ) -> list:
        """
        Advanced retrieval with reranking and MMR.
        
        Args:
            query: Search query
            limit: Number of final results
            filter_expr: Optional filter expression
            use_reranking: Override config for reranking (None = use config)
            use_mmr: Override config for MMR (None = use config)
            
        Returns:
            List of RetrievalResult objects with all scores
        """
        # Temporarily override config if specified
        original_rerank = self.config.use_reranking
        original_mmr = self.config.use_mmr
        
        if use_reranking is not None:
            self.retriever.config.use_reranking = use_reranking
        if use_mmr is not None:
            self.retriever.config.use_mmr = use_mmr
        
        try:
            results = self.retriever.retrieve(query, k=limit, filter_expr=filter_expr)
        finally:
            # Restore original config
            self.retriever.config.use_reranking = original_rerank
            self.retriever.config.use_mmr = original_mmr
        
        return results
    
    def ask(
        self,
        query: str,
        limit: int = 5,
        filter_expr: Optional[str] = None,
        prompt_template=None,
        stream: bool = False,
    ):
        """
        Ask a question and get an LLM-generated answer with sources.
        
        This is the main RAG interface - retrieves relevant chunks,
        then generates a response using OpenAI.
        
        Args:
            query: Question to answer
            limit: Number of chunks to retrieve for context
            filter_expr: Optional filter for retrieval
            prompt_template: Optional custom PromptTemplate
            stream: If True, returns an iterator of response chunks
            
        Returns:
            GeneratedResponse with answer and source citations,
            or Iterator[str] if stream=True
        """
        # Step 1: Retrieve relevant chunks
        results = self.retrieve(query, limit=limit, filter_expr=filter_expr)
        
        if not results:
            from ..generation import GeneratedResponse
            return GeneratedResponse(
                content="I couldn't find any relevant information in the documents to answer your question.",
                model=self.config.llm_model,
                sources=[],
            )
        
        # Step 2: Generate response
        if stream:
            return self.generator.generate_stream(query, results, prompt_template)
        else:
            return self.generator.generate(query, results, prompt_template)
    
    def search_and_rerank(
        self,
        query: str,
        limit: int = 5,
        initial_k: int = 20,
        filter_expr: Optional[str] = None,
    ) -> list:
        """
        Search with explicit reranking step.
        
        Useful when you want reranking without MMR.
        
        Args:
            query: Search query
            limit: Final number of results
            initial_k: Number of initial candidates
            filter_expr: Optional filter
            
        Returns:
            List of RankedResult objects
        """
        # Get initial candidates
        query_embedding = self.embedder.embed_query(query)
        candidates = self.vector_store.search(query_embedding, initial_k, filter_expr)
        
        if not candidates or not self.reranker:
            return candidates[:limit]
        
        # Rerank
        reranked = self.reranker.rerank(query, candidates, top_k=limit)
        return reranked
    
    def shutdown(self) -> None:
        """Shutdown Ray if we initialized it."""
        if RAY_AVAILABLE and self._ray_initialized and ray.is_initialized():
            ray.shutdown()
            self._ray_initialized = False
    
    # =========================================================================
    # Async API
    # =========================================================================
    
    async def retrieve_async(
        self,
        query: str,
        limit: int = 5,
        filter_expr: Optional[str] = None,
        use_reranking: Optional[bool] = None,
        use_mmr: Optional[bool] = None,
    ) -> list:
        """
        Async version of retrieve.
        
        Args:
            query: Search query
            limit: Number of final results
            filter_expr: Optional filter expression
            use_reranking: Override config for reranking (None = use config)
            use_mmr: Override config for MMR (None = use config)
            
        Returns:
            List of RetrievalResult objects with all scores
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.retrieve(
                query,
                limit=limit,
                filter_expr=filter_expr,
                use_reranking=use_reranking,
                use_mmr=use_mmr,
            )
        )
    
    async def ask_async(
        self,
        query: str,
        limit: int = 5,
        filter_expr: Optional[str] = None,
        prompt_template=None,
    ):
        """
        Ask a question asynchronously and get an LLM-generated answer.
        
        This is the async version of the main RAG interface.
        
        Args:
            query: Question to answer
            limit: Number of chunks to retrieve for context
            filter_expr: Optional filter for retrieval
            prompt_template: Optional custom PromptTemplate
            
        Returns:
            GeneratedResponse with answer and source citations
        """
        # Step 1: Retrieve relevant chunks asynchronously
        results = await self.retrieve_async(query, limit=limit, filter_expr=filter_expr)
        
        if not results:
            from ..generation import GeneratedResponse
            return GeneratedResponse(
                content="I couldn't find any relevant information in the documents to answer your question.",
                model=self.config.llm_model,
                sources=[],
            )
        
        # Step 2: Generate response asynchronously
        return await self.generator.generate_async(query, results, prompt_template)
    
    async def ask_stream_async(
        self,
        query: str,
        limit: int = 5,
        filter_expr: Optional[str] = None,
        prompt_template=None,
    ) -> AsyncIterator[str]:
        """
        Ask a question and stream the response asynchronously.
        
        Args:
            query: Question to answer
            limit: Number of chunks to retrieve for context
            filter_expr: Optional filter for retrieval
            prompt_template: Optional custom PromptTemplate
            
        Yields:
            Response chunks as they arrive
        """
        # Step 1: Retrieve relevant chunks
        results = await self.retrieve_async(query, limit=limit, filter_expr=filter_expr)
        
        if not results:
            yield "I couldn't find any relevant information in the documents to answer your question."
            return
        
        # Step 2: Stream the response
        async for chunk in self.generator.generate_stream_async(query, results, prompt_template):
            yield chunk
