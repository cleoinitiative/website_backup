"""Factory functions for document parsing."""

from pathlib import Path
from typing import Optional

from .base import DocumentParser, ParsedDocument
from .pdf_parser import PDFParser
from .html_parser import HTMLParser
from .text_parser import TextParser


# Registry of parsers
PARSERS: list[type[DocumentParser]] = [
    PDFParser,
    HTMLParser,
    TextParser,
]


def get_parser(file_path: Path | str) -> Optional[DocumentParser]:
    """
    Get the appropriate parser for a file.
    
    Args:
        file_path: Path to the file to parse
        
    Returns:
        Parser instance or None if no parser supports the file type
    """
    file_path = Path(file_path)
    
    for parser_class in PARSERS:
        if parser_class.can_parse(file_path):
            return parser_class()
    
    return None


def parse_file(file_path: Path | str) -> ParsedDocument:
    """
    Parse a file using the appropriate parser.
    
    Args:
        file_path: Path to the file to parse
        
    Returns:
        ParsedDocument with extracted content
        
    Raises:
        ValueError: If no parser supports the file type
    """
    file_path = Path(file_path)
    parser = get_parser(file_path)
    
    if parser is None:
        supported = []
        for p in PARSERS:
            supported.extend(p.SUPPORTED_EXTENSIONS)
        raise ValueError(
            f"Unsupported file type: {file_path.suffix}. "
            f"Supported extensions: {supported}"
        )
    
    return parser.parse(file_path)


def get_supported_extensions() -> list[str]:
    """Get list of all supported file extensions."""
    extensions = []
    for parser_class in PARSERS:
        extensions.extend(parser_class.SUPPORTED_EXTENSIONS)
    return extensions

