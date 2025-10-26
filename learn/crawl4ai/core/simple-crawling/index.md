# 单页基础抓取（Simple Crawling）

本节深入单页抓取的核心用法，包括基础参数、结果结构与常见注意事项。

## 基础用法

```python
# file: simple_crawling_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com",
        )
        print("status:", result.status)
        print("title:", result.metadata.get("title"))
        print("md top:", (result.markdown or "").split("\n")[:10])

if __name__ == "__main__":
    asyncio.run(main())
```

## 常用参数概览

`AsyncWebCrawler` 在构造与 `arun()` 时可接收多类配置，常见包括：

- 浏览器/渲染相关：无头模式、视窗大小、超时、脚本注入等（详见 `core/config`）。
- 内容质量：是否启用 Markdown 生成、标题提取、噪声过滤（详见 `markdown-generation`、`fit-markdown`）。
- 选择器过滤：仅输出指定区域或排除区域（详见 `content-selection`）。
- 缓存策略：提高重复抓取性能（详见 `cache-modes`）。

提示：不同版本的参数名和默认值可能调整，请以 `API Reference -> parameters` 为准。

## 结果结构（CrawlResult）

典型可用字段：

- `status`: 抓取状态（如 `success`/`error`）。
- `url`: 实际访问的 URL（可能不同于输入，因跳转）。
- `metadata`: 包含页面标题、语言等信息。
- `markdown`: 结构化 Markdown 文本（适合 LLM）。
- `content`: 原始/清洗后文本（视配置而定）。
- `links`, `images`, `media`: 链接与媒体资源（如启用链接/媒体提取）。

## 错误处理与重试

```python
# file: simple_crawling_retry.py
import asyncio
from crawl4ai import AsyncWebCrawler

async def safe_fetch(url: str):
    async with AsyncWebCrawler() as crawler:
        try:
            result = await crawler.arun(url)
            if result.status != "success":
                raise RuntimeError(f"fetch failed: {result.status}")
            return result
        except Exception as e:
            print("error:", e)
            return None

async def main():
    res = await safe_fetch("https://example.com")
    if res:
        print("title:", res.metadata.get("title"))

if __name__ == "__main__":
    asyncio.run(main())
```

## 后续阅读

- 交互、滚动、分页：`deep-crawling`、`page-interaction`、`virtual-scroll`。
- 智能停止策略：`adaptive-crawling` 与高级 `adaptive-strategies`。
- 并发与大规模抓取：`multi-url-crawling`、`crawl-dispatcher`。
