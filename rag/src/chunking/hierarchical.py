"""Hierarchical (parent-child) chunking for context-aware retrieval."""

from dataclasses import dataclass, field
from typing import Optional
import hashlib

from .chunker import TextChunker, ChunkingConfig, Chunk


@dataclass
class HierarchicalChunkConfig:
    """Configuration for hierarchical chunking."""
    
    # Parent chunk settings (larger, for context)
    parent_chunk_size: int = 2048
    parent_chunk_overlap: int = 200
    
    # Child chunk settings (smaller, for precise matching)
    child_chunk_size: int = 256
    child_chunk_overlap: int = 50
    
    # Minimum sizes
    min_parent_size: int = 512
    min_child_size: int = 64
    
    def __post_init__(self):
        """Validate and adjust overlaps to be valid."""
        # Ensure overlaps are less than chunk sizes
        if self.parent_chunk_overlap >= self.parent_chunk_size:
            self.parent_chunk_overlap = self.parent_chunk_size // 10
        if self.child_chunk_overlap >= self.child_chunk_size:
            self.child_chunk_overlap = self.child_chunk_size // 10
        # Ensure min sizes are valid
        if self.min_parent_size >= self.parent_chunk_size:
            self.min_parent_size = self.parent_chunk_size // 4
        if self.min_child_size >= self.child_chunk_size:
            self.min_child_size = self.child_chunk_size // 4


@dataclass
class HierarchicalChunk:
    """A chunk with parent-child relationship."""
    
    # Child chunk (for retrieval)
    text: str
    chunk_id: str
    chunk_index: int
    start_char: int
    end_char: int
    token_count: int
    source_path: str
    
    # Parent reference
    parent_id: str
    parent_text: str
    parent_start_char: int
    parent_end_char: int
    parent_token_count: int
    
    # Position within parent
    child_index_in_parent: int
    
    metadata: dict = field(default_factory=dict)


class HierarchicalChunker:
    """
    Two-level hierarchical chunker for parent-child retrieval.
    
    Strategy:
    1. Split document into large "parent" chunks (for context)
    2. Split each parent into smaller "child" chunks (for precise matching)
    3. At retrieval time, match on children but return parent context
    
    Benefits:
    - Children provide precise semantic matching
    - Parents provide sufficient context for LLM generation
    - Reduces the "lost in the middle" problem
    """
    
    def __init__(self, config: Optional[HierarchicalChunkConfig] = None):
        self.config = config or HierarchicalChunkConfig()
        
        # Create parent and child chunkers
        self._parent_chunker = TextChunker(ChunkingConfig(
            chunk_size=self.config.parent_chunk_size,
            chunk_overlap=self.config.parent_chunk_overlap,
            min_chunk_size=self.config.min_parent_size,
        ))
        
        self._child_chunker = TextChunker(ChunkingConfig(
            chunk_size=self.config.child_chunk_size,
            chunk_overlap=self.config.child_chunk_overlap,
            min_chunk_size=self.config.min_child_size,
        ))
    
    def chunk_text(
        self,
        text: str,
        source_path: str = "",
    ) -> tuple[list[Chunk], list[HierarchicalChunk]]:
        """
        Create hierarchical chunks from text.
        
        Args:
            text: Text to chunk
            source_path: Source file path
            
        Returns:
            Tuple of (parent_chunks, child_chunks_with_parent_refs)
        """
        if not text.strip():
            return [], []
        
        # Step 1: Create parent chunks
        parent_chunks = self._parent_chunker.chunk_text(text, source_path)
        
        # Step 2: Create child chunks within each parent
        all_hierarchical_chunks = []
        
        for parent in parent_chunks:
            parent_id = self._generate_parent_id(parent)
            
            # Chunk the parent text
            children = self._child_chunker.chunk_text(parent.text, source_path)
            
            for child_idx, child in enumerate(children):
                # Calculate absolute positions
                abs_start = parent.start_char + child.start_char
                abs_end = parent.start_char + child.end_char
                
                hierarchical = HierarchicalChunk(
                    # Child info
                    text=child.text,
                    chunk_id=child.chunk_id,
                    chunk_index=len(all_hierarchical_chunks),
                    start_char=abs_start,
                    end_char=abs_end,
                    token_count=child.token_count,
                    source_path=source_path,
                    
                    # Parent info
                    parent_id=parent_id,
                    parent_text=parent.text,
                    parent_start_char=parent.start_char,
                    parent_end_char=parent.end_char,
                    parent_token_count=parent.token_count,
                    
                    # Position
                    child_index_in_parent=child_idx,
                )
                all_hierarchical_chunks.append(hierarchical)
        
        return parent_chunks, all_hierarchical_chunks
    
    def chunk_document(self, document) -> tuple[list[Chunk], list[HierarchicalChunk]]:
        """
        Create hierarchical chunks from a ParsedDocument.
        
        Args:
            document: ParsedDocument instance
            
        Returns:
            Tuple of (parent_chunks, hierarchical_child_chunks)
        """
        return self.chunk_text(document.content, document.source_path)
    
    def _generate_parent_id(self, chunk: Chunk) -> str:
        """Generate a unique ID for a parent chunk."""
        content = f"parent:{chunk.source_path}:{chunk.start_char}:{chunk.text[:100]}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


def expand_to_parent(
    child_chunks: list,
    hierarchical_store: dict[str, HierarchicalChunk],
) -> list[str]:
    """
    Given retrieved child chunks, expand to their parent context.
    
    Args:
        child_chunks: Retrieved child chunk IDs or objects
        hierarchical_store: Mapping of chunk_id to HierarchicalChunk
        
    Returns:
        List of unique parent texts (deduplicated)
    """
    seen_parents = set()
    parent_texts = []
    
    for child in child_chunks:
        chunk_id = child if isinstance(child, str) else child.chunk_id
        
        if chunk_id in hierarchical_store:
            hier_chunk = hierarchical_store[chunk_id]
            if hier_chunk.parent_id not in seen_parents:
                seen_parents.add(hier_chunk.parent_id)
                parent_texts.append(hier_chunk.parent_text)
    
    return parent_texts


