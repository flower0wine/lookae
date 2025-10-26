import asyncio
import re
from pathlib import Path
from typing import List, Optional, Dict, Any

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm import tqdm
from rich import print as rprint

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

from .ai_md import AIParser
from .config import build_listing_url, output_dir_for, DEFAULT_CONCURRENCY, DEFAULT_DELAY_SECONDS
from .extractors import parse_listing, extract_article_md_and_tags, Item


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=15),
       retry=retry_if_exception_type(Exception))
async def fetch_markdown(crawler: AsyncWebCrawler, url: str, run_cfg: Optional[CrawlerRunConfig] = None) -> Dict[str, Any]:
    result = await crawler.arun(url=url, config=run_cfg or CrawlerRunConfig())
    if not result or not (result.markdown or result.html):
        raise RuntimeError(f"Empty result for {url}")
    return {
        "markdown": result.markdown or "",
        "html": result.html or "",
        "links": getattr(result, "links", []),
    }

async def crawl_page(
    page: int = 2,
    limit: Optional[int] = None,
    force: bool = False,
    ai: Optional[AIParser] = None,
    category: str = "aescripts",
    concurrency: int = DEFAULT_CONCURRENCY,
    delay_seconds: float = DEFAULT_DELAY_SECONDS,
) -> List[Path]:
    """
    Crawl a listing page and each item details, render to Markdown files.

    - page: listing page number (the user asked for /page/2/)
    - limit: optional cap on number of items
    - force: if False, skip existing item files
    - ai: optional AIParser for smart Markdown normalization
    """
    ai = ai or AIParser()

    url = build_listing_url(category=category, page=page)
    rprint(f"[bold cyan]Crawling listing:[/] {url}")

    outputs: List[Path] = []
    out_dir = output_dir_for(category)

    # Configure browser and run parameters for stability and cert issues
    browser = BrowserConfig(
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36",
        ignore_https_errors=True,
        java_script_enabled=True,
    )
    run_cfg = CrawlerRunConfig()

    async with AsyncWebCrawler(config=browser) as crawler:
        listing = await crawler.arun(url=url, config=run_cfg)
        if not listing or not (listing.html or listing.markdown):
            raise RuntimeError(f"Failed to load listing page: {url}")
        html = listing.html or ""
        items = parse_listing(html)
        if limit:
            items = items[:limit]

        if not items:
            rprint("[yellow]No items found on listing. Check selectors or page status.[/]")
            return outputs

        rprint(f"Found {len(items)} items. Fetching details...")

        sem = asyncio.Semaphore(max(1, concurrency))

        async def process_item(it: Item):
            out_file = out_dir / f"{re.sub(r"[\\/:*?\"<>|]", "", it.title)}.md"
            if out_file.exists() and not force:
                return out_file

            async with sem:
                details = await fetch_markdown(crawler, it.url, run_cfg)
                await asyncio.sleep(delay_seconds)
            compact_md, tags = extract_article_md_and_tags(details.get("html") or "")
            if not compact_md:
                compact_md = (details.get("markdown") or "").strip()
            md = ai.to_markdown({
                "title": it.title,
                "url": it.url,
                "thumb": it.thumb,
                "summary": it.summary,
                "markdown": compact_md,
                "html": details.get("html") or "",
                "category": category,
                "tags": tags,
            })
            out_file.write_text(md, encoding="utf-8")
            return out_file

        for fut in tqdm(asyncio.as_completed([process_item(it) for it in items]), total=len(items), desc="Items"):
            try:
                path = await fut
                if path:
                    outputs.append(path)
            except Exception as e:
                rprint(f"[red]Failed item:[/] {e}")

    return outputs


def crawl_aescripts_page(page: int = 2, limit: Optional[int] = None, force: bool = False) -> List[Path]:
    return asyncio.run(crawl_page(page=page, limit=limit, force=force, category="aescripts"))
