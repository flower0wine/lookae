# 快速上手（Quick Start）

本节通过一个可运行脚本，演示如何用 Crawl4AI 抓取单页，并对结果进行基础处理。

## 要点速览

- 使用 `AsyncWebCrawler` 执行抓取。
- 通过 `arun(url)` 获取 `CrawlResult`。
- 读取 `markdown`、`content`、`metadata` 等字段。

## 示例：抓取并保存 Markdown

```python
# file: quickstart_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    url = "https://news.ycombinator.com/"
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        # 输出关键信息
        print("Fetched:", url)
        print("Status:", result.status)
        print("Title:", result.metadata.get("title"))

        # 保存 Markdown
        md = result.markdown or ""
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(md)
        print("Saved -> output.md (", len(md), "chars)")

if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python quickstart_basic.py
```

你将得到一个 `output.md`，其中包含页面抽取后的 Markdown 内容，可用于 LLM 上下文或后续处理。

## 常见扩展

- 想过滤页面内容：参考核心章节 `content-selection`。
- 想提高质量：参考 `markdown-generation` 与 `fit-markdown`。
- 想并发抓取多链接：参考高级章节 `multi-url-crawling`。
