# 文件下载（File Downloading）

下载页面中的文件（PDF、图片、附件等），并结合白名单/同域策略确保安全与相关性。

## 示例：下载页面中的 PDF（示意）

```python
# file: file_downloading_basic.py
import asyncio
import os
from urllib.parse import urljoin, urlparse
import aiohttp
from crawl4ai import AsyncWebCrawler

URL = "https://example.com/resources"
OUT_DIR = "downloads"

async def download(session, url, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    async with session.get(url) as resp:
        resp.raise_for_status()
        with open(out_path, "wb") as f:
            while True:
                chunk = await resp.content.read(8192)
                if not chunk:
                    break
                f.write(chunk)

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(URL)
        base = res.metadata.get("base_url") if res.metadata else URL
        links = res.links or []
        pdfs = []
        for a in links:
            href = a.get("href") if isinstance(a, dict) else None
            if not href:
                continue
            full = urljoin(base, href)
            if full.lower().endswith(".pdf"):
                # 同域限制（可选）
                if urlparse(full).netloc != urlparse(URL).netloc:
                    continue
                pdfs.append(full)
        print("found pdfs:", len(pdfs))
        async with aiohttp.ClientSession() as session:
            for i, u in enumerate(pdfs, 1):
                out = os.path.join(OUT_DIR, f"file_{i}.pdf")
                try:
                    await download(session, u, out)
                    print("Saved ->", out)
                except Exception as e:
                    print("fail:", u, e)

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 结合 `link-media` 获取更多媒体类型；使用白名单（扩展名/域名）筛选。
- 对需要授权的下载，结合 `session-management` 和 `hooks-auth` 处理 Cookie 或表单登录。
