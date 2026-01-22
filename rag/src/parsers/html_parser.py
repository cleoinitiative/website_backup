"""HTML document parser using BeautifulSoup."""

from pathlib import Path
from typing import Optional
import re

from bs4 import BeautifulSoup, Comment

from .base import DocumentParser, ParsedDocument


class HTMLParser(DocumentParser):
    """Parser for HTML documents using BeautifulSoup."""
    
    SUPPORTED_EXTENSIONS = [".html", ".htm", ".xhtml"]
    
    # Tags to remove entirely (content and all)
    REMOVE_TAGS = [
        "script", "style", "noscript", "iframe", "svg", 
        "canvas", "video", "audio", "map", "object", "embed"
    ]
    
    # Tags that typically contain navigation/boilerplate
    BOILERPLATE_TAGS = ["nav", "header", "footer", "aside"]
    
    def __init__(
        self, 
        remove_boilerplate: bool = True,
        extract_links: bool = False
    ):
        """
        Initialize HTML parser.
        
        Args:
            remove_boilerplate: Remove nav, header, footer, aside elements
            extract_links: Include link URLs in extracted text
        """
        self.remove_boilerplate = remove_boilerplate
        self.extract_links = extract_links
    
    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse an HTML file and extract clean text content.
        
        Handles:
        - Malformed HTML (BeautifulSoup is fault-tolerant)
        - Script/style removal
        - Boilerplate removal (nav, header, footer)
        - Whitespace normalization
        """
        file_path = Path(file_path)
        self._validate_file(file_path)
        
        # Read file content
        content = file_path.read_text(encoding="utf-8", errors="replace")
        
        # Parse with lxml for speed (falls back to html.parser)
        try:
            soup = BeautifulSoup(content, "lxml")
        except Exception:
            soup = BeautifulSoup(content, "html.parser")
        
        # Extract metadata before cleaning
        title = self._extract_title(soup)
        author = self._extract_author(soup)
        metadata = self._extract_metadata(soup)
        
        # Remove unwanted elements
        self._clean_soup(soup)
        
        # Extract text
        text = self._extract_text(soup)
        
        return ParsedDocument(
            content=text,
            source_path=str(file_path.absolute()),
            file_type="html",
            title=title,
            author=author,
            metadata=metadata,
        )
    
    def _clean_soup(self, soup: BeautifulSoup) -> None:
        """Remove unwanted elements from the soup (modifies in place)."""
        # Remove comments
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()
        
        # Remove script, style, etc.
        for tag in self.REMOVE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove boilerplate if configured
        if self.remove_boilerplate:
            for tag in self.BOILERPLATE_TAGS:
                for element in soup.find_all(tag):
                    element.decompose()
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text from soup."""
        # Get text with space separator
        text = soup.get_text(separator=" ", strip=True)
        
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract document title."""
        # Try <title> tag first
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        
        # Try <h1> as fallback
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text(strip=True)
        
        # Try og:title meta tag
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract document author."""
        # Try meta author tag
        author_meta = soup.find("meta", attrs={"name": "author"})
        if author_meta and author_meta.get("content"):
            return author_meta["content"]
        
        # Try article:author
        article_author = soup.find("meta", property="article:author")
        if article_author and article_author.get("content"):
            return article_author["content"]
        
        return None
    
    def _extract_metadata(self, soup: BeautifulSoup) -> dict:
        """Extract additional metadata from HTML."""
        metadata = {}
        
        # Description
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            metadata["description"] = desc["content"]
        
        # Keywords
        keywords = soup.find("meta", attrs={"name": "keywords"})
        if keywords and keywords.get("content"):
            metadata["keywords"] = keywords["content"]
        
        # Language
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            metadata["language"] = html_tag["lang"]
        
        return metadata

