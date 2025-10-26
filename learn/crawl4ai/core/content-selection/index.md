# 内容选择（Content Selection）

通过选择器包含或排除页面区域，提高输出质量、降低噪声。

## 目标

- 仅保留主体区域（如文章正文）
- 排除导航/广告/评论等噪声

## 示例：包含与排除选择器

```python
# file: content_selection_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com/article"

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=URL,
            # 说明：不同版本参数名可能不同，以下为示意
            # selectors={
            #   "include": ["article .content", ".post"],
            #   "exclude": ["nav", ".ads", ".footer", ".comments"]
            # }
        )
        md = result.markdown or ""
        with open("selected_content.md", "w", encoding="utf-8") as f:
            f.write(md)
        print("Saved -> selected_content.md (", len(md), "chars)")

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 优先基于明确的正文容器选择器（如 `.article-body`, `main`）。
- 排除区补充“粘性元素/弹窗/推荐流”等常见干扰。
- 配合 `markdown-generation` 的标题抽取与链接保留可获得更高质量输出。
