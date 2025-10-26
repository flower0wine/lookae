# 抓取调度器（Crawl Dispatcher）

当抓取任务复杂（不同站点、不同策略、优先级队列）时，可设计调度器来分发任务、回收结果并按策略动态调整。

## 示例：最小调度器雏形（按域名分配并发）

```python
# file: crawl_dispatcher_basic.py
import asyncio
from collections import defaultdict, deque
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler

URLS = [
    "https://example.com/a",
    "https://example.com/b",
    "https://another.com/x",
    "https://another.com/y",
]
PER_DOMAIN_CONCURRENCY = 2

class Dispatcher:
    def __init__(self, per_domain_concurrency=2):
        self.queues = defaultdict(deque)
        self.domain_sems = defaultdict(lambda: asyncio.Semaphore(per_domain_concurrency))

    def add(self, url):
        d = urlparse(url).netloc
        self.queues[d].append(url)

    async def run(self):
        async with AsyncWebCrawler() as crawler:
            tasks = []
            for domain, q in self.queues.items():
                tasks.append(asyncio.create_task(self.worker(domain, q, crawler)))
            await asyncio.gather(*tasks)

    async def worker(self, domain, q, crawler):
        sem = self.domain_sems[domain]
        while q:
            url = q.popleft()
            async with sem:
                r = await crawler.arun(url)
                print(domain, url, r.status, len(r.markdown or ""))

async def main():
    d = Dispatcher(per_domain_concurrency=PER_DOMAIN_CONCURRENCY)
    for u in URLS:
        d.add(u)
    await d.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## 提示

- 可加入优先级队列、重试队列与结果持久化。
- 更复杂的需求（任务依赖、分布式）可引入消息队列或任务系统。
