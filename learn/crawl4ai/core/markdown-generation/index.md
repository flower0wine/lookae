# Markdown 生成（Markdown Generation）

本节介绍如何生成高质量的 Markdown 内容，便于直接作为 LLM 上下文或知识库素材。

## 目标

- 开启/控制 Markdown 生成
- 了解常见质量参数与取舍
- 保存结果用于后续处理

## 示例：启用高质量 Markdown 生成

```python
# file: markdown_generation_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com"

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=URL,
            # 提示：不同版本参数命名可能不同，以下仅为示意，请结合 API Reference
            # markdown_options={
            #     "enable": True,
            #     "extract_headings": True,
            #     "preserve_links": True,
            #     "merge_adjacent_text": True,
            # }
        )
        md = result.markdown or ""
        print("status:", result.status)
        print("md length:", len(md))
        with open("markdown_output.md", "w", encoding="utf-8") as f:
            f.write(md)
        print("Saved -> markdown_output.md")

if __name__ == "__main__":
    asyncio.run(main())
```

## 质量建议

- 合理的标题提取与层级保留，有利于后续分块与检索。
- 保留关键链接（如目录、引用来源），便于追溯。
- 对于重复/导航噪声，可结合 `content-selection` 过滤。

## 与下游的配合

- 与 `fit-markdown` 联动优化长文输出（分页/折叠/摘要）。
- 与 `chunking`（见 Extraction 章节）配合切分，便于向量化与检索。
