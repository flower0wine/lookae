import asyncio
from pathlib import Path

from lookae_spider.crawler import crawl_page

async def main():
    # Auto-run two categories with polite settings
    for category, start_page, end_page in [("aechajian", 110, 173)]:
        for page in range(start_page, end_page + 1):
            outputs = await crawl_page(
                page=page,
                limit=None,
                force=False,
                category=category,
                concurrency=4,
                delay_seconds=0.8,
            )
            print(f"Saved {len(outputs)} markdown files for category={category}, page={page}")
            await asyncio.sleep(0.8)  # small gap between listing pages

if __name__ == "__main__":
    asyncio.run(main())
