# 缓存模式（Cache Modes）

缓存可显著减少重复抓取的开销，提升稳定性与速度。

## 目标

- 了解缓存的作用范围（HTML、渲染结果、Markdown 等）
- 控制缓存键策略与过期

## 示例：开启缓存并复用

```python
# file: cache_modes_basic.py
import asyncio
import time
from crawl4ai import AsyncWebCrawler

URL = "https://example.com"

async def fetch_once():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(
            url=URL,
            # cache={"enable": True, "ttl": 3600}  # TTL 1 小时，具体参数以 API 为准
        )
        return res

async def main():
    t1 = time.time()
    r1 = await fetch_once()
    t2 = time.time()
    print("first fetch:", r1.status, "cost:", round(t2 - t1, 2), "s")

    r2 = await fetch_once()
    t3 = time.time()
    print("second fetch:", r2.status, "cost:", round(t3 - t2, 2), "s (should be faster if cached)")

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 结合 `content-selection` 与 `markdown-generation`，缓存“已清洗”的结果更省资源。
- 注意对需要登录/会话的页面，缓存策略需区分身份（参考 `session-management`）。
