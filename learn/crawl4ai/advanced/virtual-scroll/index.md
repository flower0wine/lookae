# 虚拟滚动（Virtual Scroll）

当页面采用懒加载，需要多次滚动才能加载更多内容。

## 示例：多次滚动并等待

```python
# file: virtual_scroll_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com/scroll"

SCROLL_TIMES = 10
SCROLL_DELAY_MS = 800
SCROLL_STEP = 1200

SCROLL_JS = f"""
let y=0;
for (let i=0; i<{SCROLL_TIMES}; i++) {{
  y += {SCROLL_STEP};
  window.scrollTo(0, y);
  await new Promise(r => setTimeout(r, {SCROLL_DELAY_MS}));
}}
"""

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(
            url=URL,
            # inject_js=[SCROLL_JS]  // 示意参数，具体以 API 为准
        )
        print("status:", res.status)
        print("md chars:", len(res.markdown or ""))

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 滚动前可等待初始列表渲染完成（wait_selector）。
- 结合 `adaptive-crawling`：检测新内容增量，若无新增则提前停止滚动。
