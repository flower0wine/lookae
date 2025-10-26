# 安装与环境准备（Installation）

本节介绍如何安装 Crawl4AI，并给出最小可运行示例以验证环境。

## 环境要求

- Python 3.10+
- 建议使用虚拟环境（venv/conda/poetry 等）
- 具备网络访问能力（用于安装依赖与抓取网页）

## 安装 Crawl4AI

```bash
pip install -U crawl4ai
# 如需预发布版本（包含最新特性），可使用：
# pip install -U --pre crawl4ai
```

若需要浏览器无头环境，Crawl4AI 会在首次运行时自动下载 Playwright 依赖。你也可以提前安装：

```bash
python -m playwright install
```

## 最小可运行示例

以下示例测试单页抓取能力，输出标题与正文片段。

```python
# file: demo_installation_smoke_test.py
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        print("Status:", result.status)
        print("Title:", result.metadata.get("title"))
        print("Text snippet:", (result.markdown or "").split("\n")[:5])

if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python demo_installation_smoke_test.py
```

若成功看到页面标题与部分 Markdown 内容，说明安装就绪。

## 常见问题（FAQ）

- Windows 上如遇到编码问题，建议在终端设置 UTF-8 或使用 `PYTHONIOENCODING=utf-8`。
- 公司网络限制下可配置代理（见高级章节 `proxy-security`）。
- 若浏览器依赖下载失败，请重试 `python -m playwright install` 或切换国内源。
