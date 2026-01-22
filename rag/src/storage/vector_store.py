"""LanceDB vector store implementation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any
import os
import hashlib
import logging

import lancedb
from lancedb.pydantic import LanceModel, Vector
import pyarrow as pa

logger = logging.getLogger(__name__)


@dataclass
class VectorStoreConfig:
    """Configuration for LanceDB vector store."""
    
    # Database location
    db_path: str = "./rag_db"
    table_name: str = "documents"
    
    # Vector settings
    embedding_dim: int = 384  # Default for all-MiniLM-L6-v2
    
    # Index settings (for larger datasets)
    create_index: bool = False
    index_type: str = "IVF_PQ"  # IVF_PQ, IVF_FLAT, etc.
    num_partitions: int = 256  # For IVF
    num_sub_vectors: int = 96  # For PQ
    
    # Search settings
    metric: str = "cosine"  # cosine, L2, dot


@dataclass
class SearchResult:
    """A single search result."""
    
    text: str
    chunk_id: str
    source_path: str
    score: float
    chunk_index: int = 0
    token_count: int = 0
    metadata: dict = field(default_factory=dict)


class VectorStore:
    """
    LanceDB vector store for RAG pipeline.
    
    Features:
    - Embedded database (no server required)
    - Disk-native (handles larger-than-memory datasets)
    - Automatic schema inference
    - Vector similarity search with filtering
    """
    
    def __init__(self, config: Optional[VectorStoreConfig] = None):
        self.config = config or VectorStoreConfig()
        self._db = None
        self._table = None
    
    @property
    def db(self):
        """Lazy-initialize database connection."""
        if self._db is None:
            db_path = Path(self.config.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self._db = lancedb.connect(str(db_path))
        return self._db
    
    @property
    def table(self):
        """Get or create the documents table."""
        if self._table is None:
            if self.config.table_name in self.db.list_tables().tables:
                self._table = self.db.open_table(self.config.table_name)
            else:
                self._table = None
        return self._table
    
    def create_table(self, embedded_chunks: list) -> None:
        """
        Create table and insert initial data.
        
        Args:
            embedded_chunks: List of EmbeddedChunk objects
        """
        if not embedded_chunks:
            raise ValueError("Cannot create table with empty data")
        
        # Convert to records
        records = self._chunks_to_records(embedded_chunks)
        
        # Create table (overwrites if exists)
        self._table = self.db.create_table(
            self.config.table_name,
            records,
            mode="overwrite",
        )
        
        # Create index for large datasets
        if self.config.create_index:
            self._create_index()
    
    def add(self, embedded_chunks: list) -> int:
        """
        Add chunks to existing table.
        
        Args:
            embedded_chunks: List of EmbeddedChunk objects
            
        Returns:
            Number of chunks added
        """
        if not embedded_chunks:
            return 0
        
        if self.table is None:
            self.create_table(embedded_chunks)
            return len(embedded_chunks)
        
        records = self._chunks_to_records(embedded_chunks)
        self.table.add(records)
        
        return len(embedded_chunks)
    
    def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        filter_expr: Optional[str] = None,
    ) -> list[SearchResult]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query vector
            limit: Number of results to return
            filter_expr: Optional SQL-like filter (e.g., "source_path LIKE '%report%'")
            
        Returns:
            List of SearchResult objects
        """
        if self.table is None:
            return []
        
        # Build search query - exclude marker records (chunk_index = -1)
        search = self.table.search(query_embedding).limit(limit)
        
        # Combine user filter with marker exclusion
        marker_filter = "chunk_index >= 0"
        if filter_expr:
            combined_filter = f"({filter_expr}) AND {marker_filter}"
        else:
            combined_filter = marker_filter
        search = search.where(combined_filter)
        
        # Execute search
        results = search.to_pandas()
        
        # Convert to SearchResult objects
        search_results = []
        for _, row in results.iterrows():
            search_results.append(SearchResult(
                text=row["text"],
                chunk_id=row["chunk_id"],
                source_path=row["source_path"],
                score=float(row.get("_distance", 0)),
                chunk_index=int(row.get("chunk_index", 0)),
                token_count=int(row.get("token_count", 0)),
            ))
        
        return search_results
    
    def hybrid_search(
        self,
        query_embedding: list[float],
        query_text: str,
        limit: int = 10,
        vector_weight: float = 0.7,
    ) -> list[SearchResult]:
        """
        Hybrid search combining vector similarity and full-text search.
        
        Args:
            query_embedding: Query vector for semantic search
            query_text: Query text for full-text search
            limit: Number of results to return
            vector_weight: Weight for vector search (0-1, remainder goes to FTS)
            
        Returns:
            List of SearchResult objects
        """
        if self.table is None:
            return []
        
        try:
            # LanceDB hybrid search (requires FTS index)
            # Exclude marker records (chunk_index = -1)
            results = (
                self.table.search(query_embedding, query_type="hybrid")
                .text(query_text)
                .where("chunk_index >= 0")
                .limit(limit)
                .to_pandas()
            )
        except Exception:
            # Fall back to vector-only search if FTS not available
            return self.search(query_embedding, limit)
        
        # Convert to SearchResult objects
        search_results = []
        for _, row in results.iterrows():
            search_results.append(SearchResult(
                text=row["text"],
                chunk_id=row["chunk_id"],
                source_path=row["source_path"],
                score=float(row.get("_distance", 0)),
                chunk_index=int(row.get("chunk_index", 0)),
                token_count=int(row.get("token_count", 0)),
            ))
        
        return search_results
    
    def delete(self, filter_expr: str) -> int:
        """
        Delete chunks matching filter expression.
        
        Args:
            filter_expr: SQL-like filter (e.g., "source_path = '/path/to/file.pdf'")
            
        Returns:
            Number of rows deleted (approximate)
        """
        if self.table is None:
            return 0
        
        # Get count before deletion
        count_before = self.count()
        
        # Delete matching rows
        self.table.delete(filter_expr)
        
        # Return approximate count
        return count_before - self.count()
    
    def count(self) -> int:
        """Get total number of chunks in the store."""
        if self.table is None:
            return 0
        return self.table.count_rows()
    
    def list_sources(self) -> list[str]:
        """Get list of unique source paths."""
        if self.table is None:
            return []
        
        df = self.table.to_pandas()
        return df["source_path"].unique().tolist()
    
    def _chunks_to_records(self, embedded_chunks: list, file_hash: Optional[str] = None) -> list[dict]:
        """Convert EmbeddedChunk objects to LanceDB records."""
        records = []
        for chunk in embedded_chunks:
            record = {
                "text": chunk.text,
                "embedding": chunk.embedding,
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "source_path": chunk.source_path,
                "token_count": chunk.token_count,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
            }
            # Add file_hash if provided (for incremental updates)
            if file_hash:
                record["file_hash"] = file_hash
            records.append(record)
        return records
    
    def get_file_hash(self, source_path: str) -> Optional[str]:
        """Get the stored hash for a file, if it exists."""
        if self.table is None:
            return None
        
        try:
            # Use LanceDB filter to get file hash efficiently
            escaped_path = source_path.replace("'", "''")
            df = (
                self.table.search()
                .where(f"source_path = '{escaped_path}'")
                .select(["file_hash"])
                .limit(1)
                .to_pandas()
            )
            if len(df) > 0 and "file_hash" in df.columns:
                hash_val = df.iloc[0]["file_hash"]
                if hash_val is not None and str(hash_val) != "nan":
                    return str(hash_val)
        except Exception:
            pass
        return None
    
    def delete_by_source(self, source_path: str) -> int:
        """Delete all chunks from a specific source file."""
        if self.table is None:
            return 0
        
        try:
            count_before = self.count()
            # Escape single quotes in path
            escaped_path = source_path.replace("'", "''")
            self.table.delete(f"source_path = '{escaped_path}'")
            deleted = count_before - self.count()
            if deleted > 0:
                logger.debug(f"Deleted {deleted} chunks from {source_path}")
            return deleted
        except Exception as e:
            logger.warning(f"Failed to delete chunks for {source_path}: {e}")
            return 0
    
    def add_with_hash(self, embedded_chunks: list, source_path: str, file_hash: str) -> int:
        """
        Add chunks with file hash, replacing existing chunks from same source.
        
        Args:
            embedded_chunks: List of EmbeddedChunk objects
            source_path: Path to the source file
            file_hash: Hash of the source file content
            
        Returns:
            Number of chunks added
        """
        # Delete existing chunks from this source
        self.delete_by_source(source_path)
        
        # If no chunks, store a marker record to track the file hash
        if not embedded_chunks:
            marker_record = {
                "text": "",
                "embedding": [0.0] * self.config.embedding_dim,
                "chunk_id": f"_marker_{file_hash[:16]}",
                "chunk_index": -1,  # Marker for empty file
                "source_path": source_path,
                "token_count": 0,
                "start_char": 0,
                "end_char": 0,
                "file_hash": file_hash,
            }
            if self.table is None:
                self._table = self.db.create_table(
                    self.config.table_name,
                    [marker_record],
                    mode="overwrite",
                )
            else:
                self.table.add([marker_record])
            return 0
        
        if self.table is None:
            # Create new table with hash field
            records = self._chunks_to_records(embedded_chunks, file_hash)
            self._table = self.db.create_table(
                self.config.table_name,
                records,
                mode="overwrite",
            )
            return len(embedded_chunks)
        
        # Add new chunks
        records = self._chunks_to_records(embedded_chunks, file_hash)
        self.table.add(records)
        
        return len(embedded_chunks)
    
    def _create_index(self) -> None:
        """Create vector index for faster search on large datasets."""
        if self.table is None:
            return
        
        self.table.create_index(
            metric=self.config.metric,
            num_partitions=self.config.num_partitions,
            num_sub_vectors=self.config.num_sub_vectors,
            index_type=self.config.index_type,
        )
    
    def create_fts_index(self) -> None:
        """Create full-text search index for hybrid search."""
        if self.table is None:
            return
        
        self.table.create_fts_index("text")
    
    def drop_table(self) -> None:
        """Drop the documents table."""
        if self.config.table_name in self.db.list_tables().tables:
            self.db.drop_table(self.config.table_name)
            self._table = None

