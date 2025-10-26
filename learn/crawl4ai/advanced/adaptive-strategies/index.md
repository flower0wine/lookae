# 自适应策略（Adaptive Strategies）

高级自适应策略用于决定何时停止点击/滚动/抓取，降低开销并避免死循环。

## 常见策略

- 基于内容增量（相似度/新元素计数）
- 基于时间预算或最大步数
- 基于结构信号（分页器消失、按钮禁用）

## 示例：结合滚动 + 新元素计数（伪示意）

```python
# file: adaptive_strategies_scroll_new_items.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com/scroll"
MAX_STEPS = 15

async def main():
    async with AsyncWebCrawler() as crawler:
        prev_len = 0
        for step in range(MAX_STEPS):
            res = await crawler.arun(url=URL)
            md = res.markdown or ""
            cur_len = len(md)
            print("step", step, "md_len=", cur_len)
            if cur_len <= prev_len:
                print("Stop due to no growth")
                break
            prev_len = cur_len
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
```

提示：真实实现中可在单次 arun 期间注入滚动/点击，再根据页面结构或网络静默判断是否继续（与 `page-interaction` 联动）。
