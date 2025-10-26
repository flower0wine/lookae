# 懒加载（Lazy Loading）

处理图片/列表等懒加载（滚动或可视区触发）场景。

## 思路

- 结合滚动与等待（见 virtual-scroll）
- 替换占位属性（如 data-src -> src）后再抽取

## 示例：滚动 + 修复图片懒加载属性

```python
# file: lazy_loading_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com/gallery"

FIX_LAZY_JS = """
for (const img of document.querySelectorAll('img')) {
  const ds = img.getAttribute('data-src') || img.getAttribute('data-original') || img.getAttribute('data-lazy');
  if (ds && !img.getAttribute('src')) img.setAttribute('src', ds);
}
"""

SCROLL_JS = """
let y=0; for (let i=0;i<10;i++){ y+=1200; window.scrollTo(0,y); await new Promise(r=>setTimeout(r,700)); }
"""

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(
            url=URL,
            # inject_js=[SCROLL_JS, FIX_LAZY_JS]  # 示意参数
        )
        print("status:", res.status, "md:", len(res.markdown or ""))

if __name__ == "__main__":
    asyncio.run(main())
```

## 提示

- 对列表懒加载同样可在滚动后等待选择器变化（新增节点数）。
- 图片下载参见 `file-downloading` 与 `link-media`。
