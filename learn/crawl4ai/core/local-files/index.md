# 本地文件与原始 HTML（Local Files & Raw HTML）

除了 URL 抓取，有时我们需要处理本地 HTML 文件或直接传入原始 HTML 字符串。

## 示例：从本地 HTML 渲染并抽取 Markdown

```python
# file: local_files_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

HTML_PATH = "sample.html"

async def main():
    async with AsyncWebCrawler() as crawler:
        # 伪参数：raw_html / file_path 仅作为示意，具体请参考当前版本 API
        res = await crawler.arun(
            # file_path=HTML_PATH
            # raw_html=open(HTML_PATH, "r", encoding="utf-8").read()
        )
        md = res.markdown or ""
        with open("local_html_output.md", "w", encoding="utf-8") as f:
            f.write(md)
        print("Saved -> local_html_output.md")

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 本地 HTML 的编码/资源路径（CSS/JS/图片）与线上有差异，注意相对路径。
- 对于安全考虑，谨慎执行来自不可信来源的脚本。
