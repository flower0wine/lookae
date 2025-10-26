# PDF 解析（PDF Parsing）

当页面或下载的文件为 PDF，需要解析文本结构后再进入下游。

## 示例：下载后解析 PDF（结合 pdfminer.six）

```python
# file: pdf_parsing_basic.py
import asyncio
import os
import aiohttp
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler
from pdfminer.high_level import extract_text

URL = "https://example.com/paper"
OUT_PDF = "paper.pdf"
OUT_TXT = "paper.txt"

async def main():
    async with AsyncWebCrawler() as crawler:
        r = await crawler.arun(URL)
        base = r.metadata.get("base_url") if r.metadata else URL
        # 简化处理：假设页面上首个 .pdf 链接就是目标
        pdf_url = None
        for a in (r.links or []):
            href = a.get("href") if isinstance(a, dict) else None
            if href and href.lower().endswith(".pdf"):
                pdf_url = urljoin(base, href)
                break
        if not pdf_url:
            print("no pdf link found")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as resp:
                resp.raise_for_status()
                with open(OUT_PDF, "wb") as f:
                    f.write(await resp.read())
        text = extract_text(OUT_PDF)
        with open(OUT_TXT, "w", encoding="utf-8") as f:
            f.write(text)
        print("Saved ->", OUT_PDF, OUT_TXT)

if __name__ == "__main__":
    asyncio.run(main())
```

依赖：

```bash
pip install pdfminer.six
```

## 建议

- 学术 PDF 可考虑 `pymupdf`（fitz）以获取版面信息。
- 对扫描型 PDF，需 OCR（如 `pytesseract`）。
