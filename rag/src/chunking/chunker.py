"""Text chunking with configurable strategies."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import hashlib

import tiktoken

if TYPE_CHECKING:
    from ..parsers.base import ParsedDocument


@dataclass
class ChunkingConfig:
    """Configuration for text chunking."""
    
    chunk_size: int = 512  # Target chunk size in tokens
    chunk_overlap: int = 50  # Overlap between chunks in tokens
    min_chunk_size: int = 100  # Minimum chunk size (skip smaller)
    
    # Separators for recursive splitting (ordered by preference)
    separators: list[str] = field(default_factory=lambda: [
        "\n\n",  # Paragraphs
        "\n",    # Lines
        ". ",    # Sentences
        "? ",    # Questions
        "! ",    # Exclamations
        "; ",    # Clauses
        ", ",    # Phrases
        " ",     # Words
    ])
    
    def __post_init__(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")


@dataclass
class Chunk:
    """A single text chunk with metadata."""
    
    text: str
    chunk_index: int
    start_char: int
    end_char: int
    source_path: str
    chunk_id: str = field(default="")
    token_count: int = 0
    
    def __post_init__(self):
        if not self.chunk_id:
            # Generate deterministic chunk ID from content + position
            content = f"{self.source_path}:{self.start_char}:{self.text[:100]}"
            self.chunk_id = hashlib.md5(content.encode()).hexdigest()[:16]


class TextChunker:
    """
    Recursive character text splitter with token-aware chunking.
    
    Strategy:
    1. Try to split on preferred separators (paragraphs first)
    2. If chunk is still too large, try next separator
    3. Maintain overlap between chunks for context continuity
    """
    
    config: ChunkingConfig
    tokenizer: tiktoken.Encoding
    
    def __init__(self, config: ChunkingConfig | None = None):
        self.config = config or ChunkingConfig()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))
    
    def chunk_text(self, text: str, source_path: str = "") -> list[Chunk]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            source_path: Source file path for metadata
            
        Returns:
            List of Chunk objects
        """
        if not text.strip():
            return []
        
        # Split recursively
        splits = self._recursive_split(text, self.config.separators)
        
        # Merge splits into chunks with overlap
        chunks = self._merge_splits(splits, source_path)
        
        return chunks
    
    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split text using separators in order of preference."""
        if not separators:
            # No more separators, just return the text
            return [text] if text.strip() else []
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        # Split on current separator
        if separator in text:
            splits = text.split(separator)
        else:
            # Separator not found, try next
            return self._recursive_split(text, remaining_separators)
        
        result: list[str] = []
        for split in splits:
            if not split.strip():
                continue
            
            # Check if split is small enough
            if self.count_tokens(split) <= self.config.chunk_size:
                result.append(split)
            else:
                # Too large, split further
                result.extend(self._recursive_split(split, remaining_separators))
        
        return result
    
    def _merge_splits(self, splits: list[str], source_path: str) -> list[Chunk]:
        """Merge small splits into chunks, maintaining overlap."""
        if not splits:
            return []
        
        chunks: list[Chunk] = []
        current_texts: list[str] = []
        current_tokens = 0
        current_start = 0
        char_position = 0
        
        for split in splits:
            split_tokens = self.count_tokens(split)
            
            # Check if adding this split would exceed chunk size
            if current_tokens + split_tokens > self.config.chunk_size and current_texts:
                # Create chunk from accumulated texts
                chunk_text = " ".join(current_texts)
                
                if self.count_tokens(chunk_text) >= self.config.min_chunk_size:
                    chunks.append(Chunk(
                        text=chunk_text,
                        chunk_index=len(chunks),
                        start_char=current_start,
                        end_char=char_position,
                        source_path=source_path,
                        token_count=self.count_tokens(chunk_text),
                    ))
                
                # Calculate overlap - keep last N tokens worth of text
                overlap_texts: list[str] = []
                overlap_tokens = 0
                for t in reversed(current_texts):
                    t_tokens = self.count_tokens(t)
                    if overlap_tokens + t_tokens <= self.config.chunk_overlap:
                        overlap_texts.insert(0, t)
                        overlap_tokens += t_tokens
                    else:
                        break
                
                current_texts = overlap_texts
                current_tokens = overlap_tokens
                current_start = char_position - len(" ".join(overlap_texts))
            
            current_texts.append(split)
            current_tokens += split_tokens
            char_position += len(split) + 1  # +1 for separator
        
        # Don't forget the last chunk
        if current_texts:
            chunk_text = " ".join(current_texts)
            if self.count_tokens(chunk_text) >= self.config.min_chunk_size:
                chunks.append(Chunk(
                    text=chunk_text,
                    chunk_index=len(chunks),
                    start_char=current_start,
                    end_char=char_position,
                    source_path=source_path,
                    token_count=self.count_tokens(chunk_text),
                ))
        
        return chunks
    
    def chunk_document(self, document: "ParsedDocument") -> list[Chunk]:
        """
        Chunk a ParsedDocument.
        
        Args:
            document: ParsedDocument instance
            
        Returns:
            List of Chunk objects with source metadata
        """
        return self.chunk_text(document.content, document.source_path)
