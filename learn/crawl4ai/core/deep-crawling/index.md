# 深度抓取（Deep Crawling）

本节聚焦多页内容的连续抓取与结果合并。先给出无需页面交互的“URL 模式分页”范式（可直接运行），再给出面向动态网站的思路，后续将与 `page-interaction`/`virtual-scroll` 章节联动。

## 场景 1：URL 模式分页（可直接运行）

很多站点的分页是纯 URL 规则（如 `?page=1,2,3...`）。这时我们无需点击“下一页”，而是直接构造分页 URL 列表并并发抓取。

```python
# file: deep_crawling_url_pattern.py
import asyncio
from typing import List
from crawl4ai import AsyncWebCrawler

BASE = "https://example.com/articles?page={page}"

async def fetch_pages(pages: List[int]):
    async with AsyncWebCrawler() as crawler:
        sem = asyncio.Semaphore(5)  # 控制并发，避免被限流

        async def fetch_one(p: int):
            url = BASE.format(page=p)
            async with sem:
                result = await crawler.arun(url)
                if result.status != "success":
                    print(f"Page {p} failed: {result.status}")
                    return None
                # 仅提取主体 Markdown，真实项目可做更细粒度解析
                return {"page": p, "markdown": result.markdown or ""}

        tasks = [asyncio.create_task(fetch_one(p)) for p in pages]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

async def main():
    pages = list(range(1, 6))  # 抓取前 5 页
    data = await fetch_pages(pages)

    # 合并保存
    combined = []
    for item in sorted(data, key=lambda x: x["page"]):
        combined.append(f"\n\n# Page {item['page']}\n\n")
        combined.append(item["markdown"])  # 已是结构化文本，适合 LLM

    out = "".join(combined)
    with open("deep_crawling_output.md", "w", encoding="utf-8") as f:
        f.write(out)
    print("Saved -> deep_crawling_output.md (", len(out), "chars)")

if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python deep_crawling_url_pattern.py
```

要点：

- 同一 `AsyncWebCrawler` 上下文下并发多个 `arun`，配合 `Semaphore` 做速率控制。
- 输出统一合并为一个 Markdown 文件，便于后续清洗/索引/向量化。

## 场景 2：发现型深度抓取（从页面抽取链接再抓取）

当无法预知分页 URL，但页面中存在“下一页”或“更多”链接（且为可点击的 a 标签），可以：

1. 先抓取起始页，解析 `links`（或从 `markdown`/`content` 中解析），
2. 过滤出目标链接（同域、特定路径规则等），
3. 将新链接放入队列，逐步抓取，直到满足停止条件（深度限制、数量限制、去重）。

示例（基于结果中的超链接，简单过滤同域链接）：

```python
# file: deep_crawling_discovery.py
import asyncio
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler

START_URL = "https://example.com/blog/"
MAX_PAGES = 10

async def main():
    seen = set()
    queue = [START_URL]
    results = []

    async with AsyncWebCrawler() as crawler:
        while queue and len(seen) < MAX_PAGES:
            url = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)

            res = await crawler.arun(url)
            if res.status != "success":
                print("skip due to error:", url)
                continue

            # 保存主体内容
            results.append({"url": url, "md": res.markdown or ""})

            # 从 metadata/markdown/links 中抽取可用链接（此处演示使用 metadata 可能提供的 base 信息并回落到 urljoin）
            base = res.metadata.get("base_url") if res.metadata else None
            base = base or url

            # 这里假设 res.links 存在并包含 href（不同版本可能字段名不同，可根据实际 API 调整）
            for link in (res.links or []):
                href = link.get("href") if isinstance(link, dict) else None
                if not href:
                    continue
                new_url = urljoin(base, href)
                # 只抓取同域链接作为示例
                if urlparse(new_url).netloc == urlparse(START_URL).netloc:
                    if new_url not in seen and new_url not in queue:
                        queue.append(new_url)

    # 按抓取顺序输出
    combined = []
    for item in results:
        combined.append(f"\n\n# {item['url']}\n\n")
        combined.append(item["md"])

    out = "".join(combined)
    with open("deep_crawling_discovery_output.md", "w", encoding="utf-8") as f:
        f.write(out)
    print("Saved -> deep_crawling_discovery_output.md (", len(out), "chars)")

if __name__ == "__main__":
    asyncio.run(main())
```

注意：真实站点可能需要更智能的停靠条件（如智能停止策略、最大层级/最大 URL 数、URL 规范化与去重等），并结合 `adaptive-crawling` 进一步优化。

## 动态分页（需要页面交互）

若“下一页”由 JS 触发并动态更新（无明显 URL 变化），需要“页面交互/滚动”等能力，请参考：

- `core/page-interaction`
- `advanced/virtual-scroll`

我们将在 `page-interaction` 章节提供点击、输入、等待元素出现等模式的代码示例。
