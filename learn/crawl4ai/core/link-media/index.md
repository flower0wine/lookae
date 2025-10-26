# 链接与媒体（Link & Media）

开启链接与媒体提取，便于后续下载或溯源。

## 示例：提取链接与图片

```python
# file: link_media_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com"

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(
            url=URL,
            # extract={"links": True, "images": True}  # 示意参数
        )
        links = res.links or []
        images = res.images or []
        print("links:", len(links), "images:", len(images))
        # 简要输出前几个
        for a in links[:5]:
            href = a.get("href") if isinstance(a, dict) else str(a)
            print("-", href)

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 结合 `file-downloading` 在高级章节实现后续下载。
- 对外链可做白名单或同域限制，避免无关采集。
