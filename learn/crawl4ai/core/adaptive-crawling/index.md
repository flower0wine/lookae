# 自适应抓取（Adaptive Crawling）

Crawl4AI 支持“智能知道何时停止”的抓取：根据内容增量、页面结构或自定义策略来终止深度抓取，避免无效翻页。

## 思路

- 通过“新内容增量”判断是否继续（如最新一次抓取的 Markdown 与上一次高度相似则停止）
- 控制最大点击次数/最大 URL 数
- 结合黑白名单与去重策略

## 示例：基于内容增量的停止策略（伪示意）

```python
# file: adaptive_crawling_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com/infinite"
MAX_STEPS = 10
SIMILARITY_THRESHOLD = 0.95

def jaccard(a: str, b: str) -> float:
    sa, sb = set(a.split()), set(b.split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

async def main():
    async with AsyncWebCrawler() as crawler:
        prev_md = ""
        for i in range(MAX_STEPS):
            res = await crawler.arun(url=URL)
            md = res.markdown or ""
            sim = jaccard(prev_md, md)
            print(f"step {i}: sim={sim:.3f}")
            if sim > SIMILARITY_THRESHOLD:
                print("Stop due to high similarity.")
                break
            prev_md = md
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
```

说明：真实实现可把交互（点击/滚动）和内容对比结合在一个循环中，或使用框架内置的自适应策略（见 advanced/adaptive-strategies）。
