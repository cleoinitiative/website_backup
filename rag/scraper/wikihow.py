#!/usr/bin/env python3
"""
WikiHow Technology Scraper for Senior Tech Help Corpus

Scrapes beginner-friendly technology how-to articles from WikiHow.
Focuses on articles relevant to seniors learning technology.
"""

import asyncio
import aiohttp
import os
import re
import ssl
import time
import certifi
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, quote

from bs4 import BeautifulSoup
import html2text
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential

# Create SSL context with certifi certificates
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

# Base configuration
BASE_URL = "https://www.wikihow.com"
OUTPUT_DIR = Path(__file__).parent.parent / "corpus" / "wikihow"

# Search queries for senior-relevant tech topics
SEARCH_QUERIES = [
    # Smartphones
    "use iPhone for beginners",
    "use Android phone",
    "make phone call smartphone",
    "send text message",
    "take photos smartphone",
    "download apps",
    "update phone",
    "charge phone properly",
    "increase font size phone",
    
    # Video calling
    "use FaceTime",
    "use Zoom",
    "video call",
    "use Google Meet",
    "use Skype",
    
    # Email
    "create email account",
    "send email",
    "attach file email",
    "check email",
    "use Gmail",
    "recognize spam email",
    
    # Social Media
    "use Facebook",
    "create Facebook account",
    "use Instagram",
    "use YouTube",
    "use WhatsApp",
    
    # Computers
    "use computer for beginners",
    "use Windows",
    "use Mac",
    "use laptop",
    "connect WiFi",
    "use mouse",
    "use keyboard",
    "save files computer",
    "print from computer",
    
    # Internet Safety
    "create strong password",
    "avoid internet scams",
    "recognize phishing",
    "online safety",
    "protect privacy online",
    "safe online shopping",
    
    # Tablets
    "use iPad",
    "use tablet",
    
    # General Tech
    "take screenshot",
    "copy and paste",
    "search internet",
    "use Google",
    "bookmark website",
]

# Rate limiting
REQUEST_DELAY = 2.0  # WikiHow needs more delay
MAX_CONCURRENT = 2
MAX_ARTICLES_PER_QUERY = 5


class WikiHowScraper:
    """Scraper for WikiHow technology articles."""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # HTML to Markdown converter
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = True  # WikiHow links are mostly internal
        self.h2t.ignore_images = True
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0
        
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
                        return None
            except Exception as e:
                print(f"  ❌ Error fetching {url}: {e}")
                raise
    
    def extract_article_links(self, html: str) -> list[str]:
        """Extract article links from search results."""
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        # Find article links in search results
        for a in soup.find_all('a', class_='result_link'):
            href = a.get('href', '')
            if href and '//' not in href:
                links.append(urljoin(BASE_URL, href))
        
        # Also try other patterns
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/') and not href.startswith('//'):
                full_url = urljoin(BASE_URL, href)
                # WikiHow article URLs don't have hyphens in the path
                if re.match(r'https://www\.wikihow\.com/[A-Z][a-z]+-', full_url):
                    links.append(full_url)
        
        return list(set(links))[:MAX_ARTICLES_PER_QUERY]
    
    def extract_content(self, html: str, url: str) -> Optional[dict]:
        """Extract article content."""
        soup = BeautifulSoup(html, 'lxml')
        
        # Get title
        title_elem = soup.find('h1', class_='title_lg') or soup.find('h1')
        if not title_elem:
            return None
        
        title = title_elem.get_text().strip()
        title = re.sub(r'^How to\s+', '', title, flags=re.IGNORECASE)
        
        # Find the main content (steps)
        content_parts = []
        
        # Get the intro/description
        intro = soup.find('div', class_='mf-section-0')
        if intro:
            intro_p = intro.find('p')
            if intro_p:
                content_parts.append(intro_p.get_text().strip())
        
        # Get method sections (WikiHow often has multiple methods)
        methods = soup.find_all('div', class_=re.compile(r'steps'))
        
        for method in methods:
            # Get method title if present
            method_title = method.find_previous('span', class_='mw-headline')
            if method_title:
                content_parts.append(f"\n## {method_title.get_text().strip()}\n")
            
            # Get steps
            steps = method.find_all('li', id=re.compile(r'step'))
            for i, step in enumerate(steps, 1):
                # Get step text
                step_text = step.find('div', class_='step')
                if step_text:
                    # Get the bold part (main instruction)
                    bold = step_text.find('b')
                    if bold:
                        main_instruction = bold.get_text().strip()
                        content_parts.append(f"\n**Step {i}: {main_instruction}**")
                        
                        # Get additional details
                        bold.decompose()
                        details = step_text.get_text().strip()
                        if details:
                            content_parts.append(details)
                    else:
                        text = step_text.get_text().strip()
                        if text:
                            content_parts.append(f"\n**Step {i}:** {text}")
        
        if not content_parts:
            return None
        
        content = "\n\n".join(content_parts)
        content = self.clean_content(content)
        
        if len(content) < 300:
            return None
        
        return {
            'title': f"How to {title}",
            'content': content,
            'url': url,
        }
    
    def clean_content(self, text: str) -> str:
        """Clean up extracted content."""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove WikiHow specific artifacts
        text = re.sub(r'\[Edit\]', '', text)
        text = re.sub(r'\[Image:.*?\]', '', text)
        text = re.sub(r'X\s*Research source', '', text)
        text = re.sub(r'Advertisement', '', text)
        
        return text.strip()
    
    def save_content(self, data: dict, category: str = "general") -> str:
        """Save content to markdown file."""
        safe_title = re.sub(r'[^\w\s-]', '', data['title'])
        safe_title = re.sub(r'\s+', '-', safe_title).lower()[:60]
        
        filepath = self.output_dir / f"{safe_title}.md"
        
        counter = 1
        while filepath.exists():
            filepath = self.output_dir / f"{safe_title}-{counter}.md"
            counter += 1
        
        content = f"# {data['title']}\n\n"
        content += f"> Source: WikiHow\n\n"
        content += data['content']
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    async def search_and_scrape(self, session: aiohttp.ClientSession, query: str) -> int:
        """Search WikiHow and scrape relevant articles."""
        search_url = f"{BASE_URL}/wikiHowTo?search={quote(query)}"
        
        html = await self.fetch_page(session, search_url)
        if not html:
            return 0
        
        links = self.extract_article_links(html)
        scraped_count = 0
        
        for link in links:
            if link in self.scraped_urls:
                continue
            
            self.scraped_urls.add(link)
            
            try:
                html = await self.fetch_page(session, link)
                if not html:
                    continue
                
                data = self.extract_content(html, link)
                if data:
                    self.save_content(data)
                    scraped_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return scraped_count
    
    async def scrape_all(self) -> dict:
        """Scrape articles for all queries."""
        print("🚀 Starting WikiHow scraper...")
        print(f"   Output directory: {self.output_dir}")
        print(f"   Queries to search: {len(SEARCH_QUERIES)}")
        
        start_time = time.time()
        total_count = 0
        
        headers = {
            'User-Agent': 'CLEO-TechHelp-Bot/1.0 (Educational non-profit)',
            'Accept': 'text/html,application/xhtml+xml',
        }
        
        connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
        
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            for query in tqdm(SEARCH_QUERIES, desc="   Searching"):
                count = await self.search_and_scrape(session, query)
                total_count += count
        
        elapsed = time.time() - start_time
        
        print(f"\n✨ WikiHow scraping complete!")
        print(f"   Total articles saved: {total_count}")
        print(f"   Time elapsed: {elapsed:.1f}s")
        
        return {
            'total_articles': total_count,
            'elapsed_seconds': elapsed,
        }


async def main():
    scraper = WikiHowScraper()
    return await scraper.scrape_all()


if __name__ == "__main__":
    asyncio.run(main())
