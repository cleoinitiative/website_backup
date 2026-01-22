#!/usr/bin/env python3
"""
TechBoomers Scraper for Senior Tech Help Corpus

Scrapes beginner-friendly technology tutorials from TechBoomers,
a site specifically designed for older adults learning technology.
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
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import html2text
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential

# Create SSL context with certifi certificates
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

# Base configuration
BASE_URL = "https://techboomers.com"
OUTPUT_DIR = Path(__file__).parent.parent / "corpus" / "techboomers"

# Category pages to scrape
CATEGORIES = [
    "/courses/",  # Main courses page
    "/c/internet-basics/",
    "/c/computer-basics/",
    "/c/smartphone-basics/",
    "/c/social-media/",
    "/c/email/",
    "/c/video-chat/",
    "/c/online-safety/",
    "/c/streaming/",
    "/c/smart-home/",
]

# Rate limiting
REQUEST_DELAY = 1.5
MAX_CONCURRENT = 2


class TechBoomersScraper:
    """Scraper for TechBoomers tutorials."""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = True
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
                    return None
            except Exception as e:
                print(f"  ❌ Error fetching {url}: {e}")
                raise
    
    def extract_lesson_links(self, html: str, base_url: str) -> list[str]:
        """Extract lesson/tutorial links from a category page."""
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        # Find course and lesson links
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            
            # Look for lesson pages
            if '/l/' in full_url or '/lesson/' in full_url:
                if full_url not in self.scraped_urls:
                    links.append(full_url)
            # Also get course overview pages
            elif '/c/' in full_url and full_url != base_url:
                if full_url not in self.scraped_urls:
                    links.append(full_url)
        
        return list(set(links))
    
    def extract_content(self, html: str, url: str) -> Optional[dict]:
        """Extract tutorial content from a page."""
        soup = BeautifulSoup(html, 'lxml')
        
        # Find title
        title_elem = soup.find('h1')
        if not title_elem:
            return None
        
        title = title_elem.get_text().strip()
        
        # Find main content
        content_div = (
            soup.find('div', class_='lesson-content') or
            soup.find('article') or
            soup.find('div', class_='content') or
            soup.find('main')
        )
        
        if not content_div:
            return None
        
        # Remove unwanted elements
        for elem in content_div.find_all(['script', 'style', 'nav', 'aside', 'footer']):
            elem.decompose()
        for elem in content_div.find_all(class_=re.compile(r'share|social|sidebar|ad|promo')):
            elem.decompose()
        
        # Convert to markdown
        markdown = self.h2t.handle(str(content_div))
        markdown = self.clean_markdown(markdown)
        
        if len(markdown) < 200:
            return None
        
        return {
            'title': title,
            'content': markdown,
            'url': url,
        }
    
    def clean_markdown(self, text: str) -> str:
        """Clean up extracted markdown."""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'TechBoomers', '', text)
        text = re.sub(r'\[.*?\]\(javascript:.*?\)', '', text)
        text = re.sub(r'^\s*Share.*$', '', text, flags=re.MULTILINE)
        return text.strip()
    
    def save_content(self, data: dict, category: str = "general") -> str:
        """Save content to markdown file."""
        safe_title = re.sub(r'[^\w\s-]', '', data['title'])
        safe_title = re.sub(r'\s+', '-', safe_title).lower()[:60]
        
        category_dir = self.output_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = category_dir / f"{safe_title}.md"
        
        counter = 1
        while filepath.exists():
            filepath = category_dir / f"{safe_title}-{counter}.md"
            counter += 1
        
        content = f"# {data['title']}\n\n"
        content += f"> Source: TechBoomers\n\n"
        content += data['content']
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    async def scrape_category(self, session: aiohttp.ClientSession, category_url: str) -> int:
        """Scrape all lessons from a category."""
        full_url = urljoin(BASE_URL, category_url)
        category_name = category_url.strip('/').split('/')[-1] or "courses"
        
        print(f"\n📂 Scraping: {category_name}")
        
        html = await self.fetch_page(session, full_url)
        if not html:
            return 0
        
        links = self.extract_lesson_links(html, full_url)
        print(f"   Found {len(links)} lessons")
        
        scraped_count = 0
        
        for link in links:
            if link in self.scraped_urls:
                continue
            
            self.scraped_urls.add(link)
            
            try:
                html = await self.fetch_page(session, link)
                if not html:
                    continue
                
                # Check for sub-lessons
                sub_links = self.extract_lesson_links(html, link)
                for sub_link in sub_links:
                    if sub_link not in self.scraped_urls:
                        self.scraped_urls.add(sub_link)
                        sub_html = await self.fetch_page(session, sub_link)
                        if sub_html:
                            data = self.extract_content(sub_html, sub_link)
                            if data:
                                self.save_content(data, category_name)
                                scraped_count += 1
                
                data = self.extract_content(html, link)
                if data:
                    self.save_content(data, category_name)
                    scraped_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"   ✅ Saved {scraped_count} lessons")
        return scraped_count
    
    async def scrape_all(self) -> dict:
        """Scrape all categories."""
        print("🚀 Starting TechBoomers scraper...")
        print(f"   Output directory: {self.output_dir}")
        
        start_time = time.time()
        total_count = 0
        
        headers = {
            'User-Agent': 'CLEO-TechHelp-Bot/1.0 (Educational non-profit)',
            'Accept': 'text/html',
        }
        
        connector = aiohttp.TCPConnector(ssl=SSL_CONTEXT)
        
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            for category in CATEGORIES:
                count = await self.scrape_category(session, category)
                total_count += count
        
        elapsed = time.time() - start_time
        
        print(f"\n✨ TechBoomers scraping complete!")
        print(f"   Total lessons saved: {total_count}")
        print(f"   Time elapsed: {elapsed:.1f}s")
        
        return {
            'total_lessons': total_count,
            'elapsed_seconds': elapsed,
        }


async def main():
    scraper = TechBoomersScraper()
    return await scraper.scrape_all()


if __name__ == "__main__":
    asyncio.run(main())
