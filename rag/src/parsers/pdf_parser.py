"""PDF document parser using PyMuPDF."""

from pathlib import Path
from datetime import datetime
from typing import Optional

import fitz  # PyMuPDF

from .base import DocumentParser, ParsedDocument


class PDFParser(DocumentParser):
    """Parser for PDF documents using PyMuPDF (fitz)."""
    
    SUPPORTED_EXTENSIONS = [".pdf"]
    
    def __init__(self, extract_images: bool = False):
        """
        Initialize PDF parser.
        
        Args:
            extract_images: Whether to extract and OCR images (not implemented yet)
        """
        self.extract_images = extract_images
    
    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse a PDF file and extract text content.
        
        Uses PyMuPDF's text extraction which handles:
        - Multi-column layouts
        - Tables (as text)
        - Embedded fonts
        - Reading order reconstruction
        """
        file_path = Path(file_path)
        self._validate_file(file_path)
        
        text_blocks = []
        metadata = {}
        
        with fitz.open(file_path) as doc:
            # Extract document metadata
            pdf_metadata = doc.metadata
            title = pdf_metadata.get("title") or None
            author = pdf_metadata.get("author") or None
            created_at = self._parse_pdf_date(pdf_metadata.get("creationDate"))
            
            metadata["producer"] = pdf_metadata.get("producer")
            metadata["subject"] = pdf_metadata.get("subject")
            metadata["keywords"] = pdf_metadata.get("keywords")
            
            # Extract text from each page
            for page_num, page in enumerate(doc):
                # Use "text" extraction for clean text
                # Alternative: "dict" for structured extraction with positions
                page_text = page.get_text("text")
                
                if page_text.strip():
                    text_blocks.append(page_text)
                
                # Track page-level metadata
                metadata[f"page_{page_num + 1}_chars"] = len(page_text)
            
            page_count = len(doc)
        
        # Join pages with double newline for clear separation
        content = "\n\n".join(text_blocks)
        
        return ParsedDocument(
            content=content,
            source_path=str(file_path.absolute()),
            file_type="pdf",
            title=title,
            author=author,
            created_at=created_at,
            page_count=page_count,
            metadata={k: v for k, v in metadata.items() if v},  # Remove None values
        )
    
    def _parse_pdf_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse PDF date format (D:YYYYMMDDHHmmSS) to datetime."""
        if not date_str:
            return None
        
        try:
            # Remove 'D:' prefix if present
            if date_str.startswith("D:"):
                date_str = date_str[2:]
            
            # Parse basic format (may have timezone suffix)
            date_str = date_str[:14]  # YYYYMMDDHHmmSS
            return datetime.strptime(date_str, "%Y%m%d%H%M%S")
        except (ValueError, IndexError):
            return None

