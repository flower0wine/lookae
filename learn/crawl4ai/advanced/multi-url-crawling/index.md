# 多 URL 并发抓取（Advanced Multi-URL Crawling）

当抓取规模上升，需要稳健的并发、速率限制与内存控制。

## 示例：信号量 + 批次控制 + 简单限速

```python
# file: multi_url_crawling_basic.py
import asyncio
import time
from crawl4ai import AsyncWebCrawler

URLS = [f"https://example.com/page/{i}" for i in range(1, 51)]
MAX_CONCURRENCY = 10
DELAY_BETWEEN_BATCH = 1.0
BATCH_SIZE = 20

async def fetch_batch(urls):
    async with AsyncWebCrawler() as crawler:
        sem = asyncio.Semaphore(MAX_CONCURRENCY)
        async def fetch_one(u):
            async with sem:
                r = await crawler.arun(u)
                return {"url": u, "status": r.status, "md_len": len(r.markdown or "")}
        tasks = [asyncio.create_task(fetch_one(u)) for u in urls]
        return await asyncio.gather(*tasks)

async def main():
    results = []
    for i in range(0, len(URLS), BATCH_SIZE):
        batch = URLS[i:i+BATCH_SIZE]
        t0 = time.time()
        res = await fetch_batch(batch)
        t1 = time.time()
        results.extend(res)
        print(f"Batch {i//BATCH_SIZE+1}: {len(batch)} urls, cost={t1-t0:.2f}s")
        await asyncio.sleep(DELAY_BETWEEN_BATCH)
    print("total:", len(results))

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 将失败的 URL 重新入队重试，按错误类型做指数退避。
- 结合 `cache-modes` 与 `session-management` 减少重复开销与登录压力。
