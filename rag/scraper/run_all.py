#!/usr/bin/env python3
"""
Master scraper script for CLEO Tech Help Corpus.

Runs all scrapers to build a comprehensive knowledge base for helping
seniors with technology questions.

Usage:
    python run_all.py           # Run all scrapers
    python run_all.py gcf       # Run only GCFGlobal scraper
    python run_all.py wikihow   # Run only WikiHow scraper
    python run_all.py techboomers # Run only TechBoomers scraper
"""

import asyncio
import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


async def run_gcfglobal():
    """Run the GCFGlobal scraper."""
    from scraper.gcfglobal import GCFGlobalScraper
    scraper = GCFGlobalScraper()
    return await scraper.scrape_all()


async def run_wikihow():
    """Run the WikiHow scraper."""
    from scraper.wikihow import WikiHowScraper
    scraper = WikiHowScraper()
    return await scraper.scrape_all()


async def run_techboomers():
    """Run the TechBoomers scraper."""
    from scraper.techboomers import TechBoomersScraper
    scraper = TechBoomersScraper()
    return await scraper.scrape_all()


async def run_all():
    """Run all scrapers sequentially."""
    print("=" * 60)
    print("🤖 CLEO Tech Help Corpus Builder")
    print("=" * 60)
    print()
    
    start_time = time.time()
    results = {}
    
    # Run each scraper
    scrapers = [
        ("GCFGlobal", run_gcfglobal),
        ("WikiHow", run_wikihow),
        ("TechBoomers", run_techboomers),
    ]
    
    for name, scraper_func in scrapers:
        print(f"\n{'='*60}")
        print(f"Running {name} scraper...")
        print("=" * 60)
        
        try:
            result = await scraper_func()
            results[name] = result
        except Exception as e:
            print(f"❌ {name} scraper failed: {e}")
            results[name] = {"error": str(e)}
    
    # Summary
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("📊 SCRAPING SUMMARY")
    print("=" * 60)
    
    total_docs = 0
    for name, result in results.items():
        if "error" in result:
            print(f"  {name}: ❌ Failed - {result['error']}")
        else:
            count = result.get('total_tutorials') or result.get('total_articles') or result.get('total_lessons', 0)
            total_docs += count
            print(f"  {name}: ✅ {count} documents")
    
    print(f"\n  Total documents: {total_docs}")
    print(f"  Total time: {total_time:.1f}s")
    print()
    
    # Remind to run ingestion
    print("=" * 60)
    print("📝 NEXT STEPS")
    print("=" * 60)
    print()
    print("  Run the ingestion script to index the new content:")
    print("  $ cd rag && python ingest.py")
    print()
    
    return results


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        scraper_name = sys.argv[1].lower()
        
        if scraper_name == "gcf" or scraper_name == "gcfglobal":
            asyncio.run(run_gcfglobal())
        elif scraper_name == "wikihow":
            asyncio.run(run_wikihow())
        elif scraper_name == "techboomers":
            asyncio.run(run_techboomers())
        else:
            print(f"Unknown scraper: {scraper_name}")
            print("Available: gcf, wikihow, techboomers")
            sys.exit(1)
    else:
        asyncio.run(run_all())


if __name__ == "__main__":
    main()
