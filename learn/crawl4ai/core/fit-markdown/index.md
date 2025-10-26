# Fit Markdown（长文适配）

本节说明在面对长文或动态加载页面时，如何让 Markdown 更适合下游 LLM：控制长度、结构与可读性。

## 目标

- 限制输出长度或分块
- 保留结构化信息（标题/列表/表格）
- 可选生成摘要或目录

## 示例：限制 Markdown 长度与分段保存

```python
# file: fit_markdown_basic.py
import asyncio
from textwrap import shorten
from crawl4ai import AsyncWebCrawler

URL = "https://example.com/long"
MAX_CHARS = 20_000
CHUNK_SIZE = 4_000

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(URL)
        md = res.markdown or ""
        # 限长：避免下游提示词或窗口溢出
        trimmed = md if len(md) <= MAX_CHARS else md[:MAX_CHARS]

        # 分段：粗略按字符切分，生产中建议结合语义/标题做更优切分
        chunks = [trimmed[i:i+CHUNK_SIZE] for i in range(0, len(trimmed), CHUNK_SIZE)]

        for i, c in enumerate(chunks, 1):
            with open(f"fit_md_part_{i}.md", "w", encoding="utf-8") as f:
                f.write(c)
        print("Saved parts:", len(chunks))

        # 可选：生成一个简短摘要（此处仅示意截断，真实可用 LLM 生成）
        summary = shorten(md, width=800, placeholder="...")
        with open("fit_md_summary.md", "w", encoding="utf-8") as f:
            f.write(summary)
        print("Saved -> fit_md_summary.md")

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 与 `markdown-generation` 配合，先确保结构化质量再做长度控制。
- 可与 `extraction/chunking` 策略结合，按标题/语义/DOM 结构切分更优。
- 对需要滚动或点击加载更多的页面，先参考 `page-interaction` 与 `virtual-scroll` 获取完整内容。
