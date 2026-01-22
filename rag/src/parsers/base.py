"""Base classes for document parsing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import datetime


@dataclass
class ParsedDocument:
    """Represents a parsed document with extracted text and metadata."""
    
    content: str
    source_path: str
    file_type: str
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    page_count: Optional[int] = None
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        # Normalize whitespace
        self.content = " ".join(self.content.split())
    
    @property
    def is_empty(self) -> bool:
        return len(self.content.strip()) == 0
    
    @property
    def char_count(self) -> int:
        return len(self.content)
    
    @property
    def word_count(self) -> int:
        return len(self.content.split())


class DocumentParser(ABC):
    """Abstract base class for document parsers."""
    
    SUPPORTED_EXTENSIONS: list[str] = []
    
    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDocument:
        """Parse a document and return extracted content with metadata."""
        pass
    
    @classmethod
    def can_parse(cls, file_path: Path) -> bool:
        """Check if this parser can handle the given file."""
        return file_path.suffix.lower() in cls.SUPPORTED_EXTENSIONS
    
    def _validate_file(self, file_path: Path) -> None:
        """Validate that the file exists and is readable."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        if not self.can_parse(file_path):
            raise ValueError(
                f"Unsupported file type: {file_path.suffix}. "
                f"Supported: {self.SUPPORTED_EXTENSIONS}"
            )

