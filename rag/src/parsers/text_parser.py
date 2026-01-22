"""Plain text document parser."""

from pathlib import Path
from datetime import datetime
import os

from .base import DocumentParser, ParsedDocument


class TextParser(DocumentParser):
    """Parser for plain text documents."""
    
    SUPPORTED_EXTENSIONS = [".txt", ".md", ".markdown", ".rst", ".text"]
    
    def __init__(self, encoding: str = "utf-8"):
        """
        Initialize text parser.
        
        Args:
            encoding: Default encoding for reading files
        """
        self.encoding = encoding
    
    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse a plain text file.
        
        Handles:
        - Multiple encodings (with fallback)
        - File metadata from filesystem
        """
        file_path = Path(file_path)
        self._validate_file(file_path)
        
        # Try reading with specified encoding, fall back to alternatives
        content = self._read_with_fallback(file_path)
        
        # Get file system metadata
        stat = file_path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime)
        
        # Try to extract title from first line (for markdown, etc.)
        title = self._extract_title(content, file_path)
        
        metadata = {
            "encoding": self.encoding,
            "file_size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }
        
        return ParsedDocument(
            content=content,
            source_path=str(file_path.absolute()),
            file_type=file_path.suffix.lstrip(".") or "txt",
            title=title,
            created_at=created_at,
            metadata=metadata,
        )
    
    def _read_with_fallback(self, file_path: Path) -> str:
        """Try multiple encodings to read the file."""
        encodings = [self.encoding, "utf-8", "latin-1", "cp1252"]
        
        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        
        # Last resort: read with errors replaced
        return file_path.read_text(encoding="utf-8", errors="replace")
    
    def _extract_title(self, content: str, file_path: Path) -> str:
        """Extract title from content or filename."""
        lines = content.strip().split("\n")
        
        if not lines:
            return file_path.stem
        
        first_line = lines[0].strip()
        
        # Markdown header
        if first_line.startswith("# "):
            return first_line[2:].strip()
        
        # RST-style header (line of = or - under title)
        if len(lines) > 1:
            second_line = lines[1].strip()
            if second_line and all(c in "=-" for c in second_line):
                return first_line
        
        # Fall back to filename
        return file_path.stem

