# URL 种子（URL Seeding）

当需要批量抓取时，可以从文件、数据库或代码中提供 URL 种子列表，并结合并发、重试与缓存。

## 示例：从文件读取 URL 并并发抓取

```python
# file: url_seeding_from_file.py
import asyncio
from crawl4ai import AsyncWebCrawler

INPUT = "seeds.txt"  # 每行一个 URL

async def fetch_all(urls):
    async with AsyncWebCrawler() as crawler:
        sem = asyncio.Semaphore(5)
        async def fetch_one(u):
            async with sem:
                r = await crawler.arun(u)
                return {"url": u, "status": r.status, "md": r.markdown or ""}
        tasks = [asyncio.create_task(fetch_one(u)) for u in urls]
        return await asyncio.gather(*tasks)

async def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    results = await fetch_all(urls)
    # 简单落盘
    for i, r in enumerate(results, 1):
        name = f"seed_{i}.md"
        with open(name, "w", encoding="utf-8") as f:
            f.write(r["md"])
        print("Saved ->", name, r["url"], r["status"])

if __name__ == "__main__":
    asyncio.run(main())
```

提示：生产中可结合去重、失败重试、速率限制与缓存（见 `cache-modes`、`multi-url-crawling`）。
