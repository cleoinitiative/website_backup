#!/usr/bin/env python3
"""
GCFGlobal.org Scraper for Senior Tech Help Corpus

Scrapes technology tutorials from GCFGlobal's free educational resources.
Content is used for educational RAG chatbot purposes.
"""

import asyncio
import aiohttp
import aiofiles
import os
import re
import ssl
import time
import certifi
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import html2text
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential

# Create SSL context with certifi certificates
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

# Base configuration
BASE_URL = "https://edu.gcfglobal.org"
OUTPUT_DIR = Path(__file__).parent.parent / "corpus" / "gcfglobal"

# Tutorial courses to scrape - these are senior-relevant tech topics
# Each course has multiple lessons we'll extract
TUTORIAL_COURSES = [
    # Computer basics
    "/en/computerbasics/",
    "/en/basic-computer-skills/",
    "/en/mousetutorial/",
    "/en/typing/",
    "/en/techsavvy/",
    
    # Windows
    "/en/windowsbasics/",
    "/en/windows10/",
    
    # macOS
    "/en/macosbasics/",
    
    # Internet basics
    "/en/internetbasics/",
    "/en/chrome/",
    "/en/firefox/",
    "/en/safari/",
    "/en/internet-tips/",
    "/en/search-better-2018/",
    
    # Email
    "/en/email101/",
    "/en/gmail/",
    "/en/beyondemail/",
    
    # Online Safety
    "/en/internetsafety/",
    
    # Video calling
    "/en/zoom-basics/",
    
    # Smartphones & tablets
    "/en/iphonebasics/",
    "/en/androidbasics/",
    
    # Google apps
    "/en/googledocuments/",
    "/en/googlespreadsheets/",
    "/en/googleslides/",
    "/en/googledrive/",
    "/en/googlephotos/",
    
    # Social media
    "/en/facebook101/",
    "/en/twitter/",
    "/en/instagram/",
    "/en/youtube/",
    "/en/pinterest/",
]

# Rate limiting
REQUEST_DELAY = 1.0  # seconds between requests
MAX_CONCURRENT = 3


class GCFGlobalScraper:
    """Scraper for GCFGlobal educational content."""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # HTML to Markdown converter
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = True
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # No wrapping
        
        # Track scraped URLs to avoid duplicates
        self.scraped_urls = set()
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch a page with retry logic."""
        async with self.semaphore:
            try:
                await asyncio.sleep(REQUEST_DELAY)
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"  ⚠️  Status {response.status} for {url}")
                        return None
            except Exception as e:
                print(f"  ❌ Error fetching {url}: {e}")
                raise
    
    def extract_lesson_links(self, html: str, base_url: str) -> list[str]:
        """Extract lesson links from a tutorial course page."""
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        # Find lesson links - they typically follow pattern /en/course-name/lesson-name/1/
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(BASE_URL, href)
            
            # Match lesson URLs: /en/something/something/number/
            if re.search(r'/en/[^/]+/[^/]+/\d+/?$', full_url):
                if full_url not in self.scraped_urls:
                    links.append(full_url)
        
        return list(set(links))
    
    def extract_content(self, html: str, url: str) -> Optional[dict]:
        """Extract tutorial content from a page."""
        soup = BeautifulSoup(html, 'lxml')
        
        # GCFGlobal lesson pages have content in specific structure
        # The main lesson content is typically after the header section
        
        # Extract title - look for the lesson title (h2 after h1)
        title = None
        h2 = soup.find('h2')
        h1 = soup.find('h1')
        
        if h2:
            title = h2.get_text().strip()
            # Remove the dash prefix if present
            title = re.sub(r'^-\s*', '', title)
        elif h1:
            title = h1.get_text().strip()
        
        # Also try the page title
        if not title:
            title_elem = soup.find('title')
            if title_elem:
                title = title_elem.get_text().strip()
                title = re.sub(r'\s*\|\s*GCFGlobal.*$', '', title)
                title = re.sub(r':\s*', ' - ', title)
        
        if not title:
            return None
        
        # GCFGlobal puts lesson content in the main area after the header
        # Look for h3, h4 (section headers) and paragraphs
        content_parts = []
        
        # Find all content elements in order
        for elem in soup.find_all(['h3', 'h4', 'p', 'ul', 'ol']):
            # Skip if it's in header, footer, nav
            if elem.find_parent(['header', 'footer', 'nav', 'aside']):
                continue
            # Skip if it's a footer/copyright element
            if 'footer' in str(elem.get('class', [])) or 'copyright' in str(elem.get('class', [])):
                continue
            
            text = elem.get_text().strip()
            
            # Skip empty or very short elements
            if len(text) < 10:
                continue
            
            # Skip navigation/UI text
            if text.lower() in ['continue', 'next lesson', 'back to tutorial', 'topics', 'english']:
                continue
            
            if elem.name in ['h3', 'h4']:
                content_parts.append(f"\n## {text}\n")
            elif elem.name == 'p':
                content_parts.append(text)
            elif elem.name in ['ul', 'ol']:
                for li in elem.find_all('li', recursive=False):
                    li_text = li.get_text().strip()
                    # Remove "bullet" prefix that GCFGlobal adds
                    li_text = re.sub(r'^bullet\s*', '', li_text)
                    if li_text:
                        content_parts.append(f"- {li_text}")
        
        if not content_parts:
            return None
        
        content = '\n\n'.join(content_parts)
        content = self.clean_markdown(content)
        
        if len(content) < 300:  # Skip very short pages
            return None
        
        return {
            'title': title,
            'content': content,
            'url': url,
        }
    
    def clean_markdown(self, text: str) -> str:
        """Clean up extracted markdown."""
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove GCFGlobal branding/navigation artifacts
        text = re.sub(r'^\s*GCFGlobal.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*Skip to main content.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*Previous:.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*Next:.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*Continue.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\[Continue\].*$', '', text, flags=re.MULTILINE)
        
        # Clean up links that point to gcfglobal
        text = re.sub(r'\[([^\]]+)\]\(https?://edu\.gcfglobal\.org[^)]*\)', r'\1', text)
        
        # Remove empty list items
        text = re.sub(r'^\s*\*\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*-\s*$', '', text, flags=re.MULTILINE)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def save_content(self, data: dict, category: str) -> str:
        """Save content to a markdown file."""
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', data['title'])
        safe_title = re.sub(r'\s+', '-', safe_title).lower()[:50]
        
        # Create category subdirectory
        category_dir = self.output_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{safe_title}.md"
        filepath = category_dir / filename
        
        # Handle duplicates
        counter = 1
        while filepath.exists():
            filename = f"{safe_title}-{counter}.md"
            filepath = category_dir / filename
            counter += 1
        
        # Write the file
        content = f"# {data['title']}\n\n"
        content += f"> Source: {data['url']}\n\n"
        content += data['content']
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    async def scrape_course(self, session: aiohttp.ClientSession, course_url: str) -> int:
        """Scrape all lessons from a tutorial course."""
        full_url = urljoin(BASE_URL, course_url)
        course_name = course_url.strip('/').split('/')[-1]
        
        print(f"\n📚 Scraping course: {course_name}")
        
        # Fetch course overview page
        html = await self.fetch_page(session, full_url)
        if not html:
            return 0
        
        # Try to extract the first lesson and course overview
        data = self.extract_content(html, full_url)
        scraped_count = 0
        
        if data:
            self.save_content(data, course_name)
            scraped_count += 1
        
        # Get all lesson links
        links = self.extract_lesson_links(html, full_url)
        print(f"   Found {len(links)} lesson links")
        
        # Scrape each lesson
        for link in tqdm(links, desc=f"   {course_name}", leave=False):
            if link in self.scraped_urls:
                continue
            
            self.scraped_urls.add(link)
            
            try:
                html = await self.fetch_page(session, link)
                if not html:
                    continue
                
                data = self.extract_content(html, link)
                if data:
                    self.save_content(data, course_name)
                    scraped_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error processing {link}: {e}")
        
        print(f"   ✅ Saved {scraped_count} lessons from {course_name}")
        return scraped_count
    
    async def scrape_all(self) -> dict:
        """Scrape all categories."""
        print("🚀 Starting GCFGlobal scraper...")
        print(f"   Output directory: {self.output_dir}")
        
        start_time = time.time()
        total_count = 0
        
        # Create aiohttp session with headers
        headers = {
            'User-Agent': 'CLEO-TechHelp-Bot/1.0 (Educational non-profit; contact@cleoinitiative.org)',
            'Accept': 'text/html,application/xhtml+xml',
        }
        
        # Create connector with proper SSL context
        connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
        
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            for course in TUTORIAL_COURSES:
                count = await self.scrape_course(session, course)
                total_count += count
        
        elapsed = time.time() - start_time
        
        print(f"\n✨ Scraping complete!")
        print(f"   Total tutorials saved: {total_count}")
        print(f"   Time elapsed: {elapsed:.1f}s")
        
        return {
            'total_tutorials': total_count,
            'elapsed_seconds': elapsed,
            'output_dir': str(self.output_dir),
        }


async def main():
    """Run the scraper."""
    scraper = GCFGlobalScraper()
    stats = await scraper.scrape_all()
    return stats


if __name__ == "__main__":
    asyncio.run(main())
