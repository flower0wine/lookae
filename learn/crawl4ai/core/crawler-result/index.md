# 抓取结果结构（Crawler Result）

理解结果结构有助于进行后续抽取、索引与排错。

## 典型字段

- `status`: 执行状态（`success`/`error`）。
- `url`: 实际访问的 URL。
- `metadata`: 标题、语言、base_url 等元信息。
- `markdown`: 结构化 Markdown 文本。
- `content`: 文本内容（清洗程度视配置）。
- `links`, `images`, `media`: 页面中的链接与媒体资源（若启用）。
- `timings`: 可选的计时信息（DNS/连接/渲染等）。
- `error`: 错误信息（当 status!=success 时）。

## 示例：检查结果并落盘

```python
# file: crawler_result_inspect.py
import asyncio
import json
from crawl4ai import AsyncWebCrawler

URL = "https://example.com"

async def main():
    async with AsyncWebCrawler() as crawler:
        r = await crawler.arun(URL)
        if r.status != "success":
            print("ERROR:", r.error)
            return
        # 简要查看字段
        print("title:", r.metadata.get("title"))
        print("md chars:", len(r.markdown or ""))
        # 保存 JSON（不包含大字段时更轻量）
        out = {
            "url": r.url,
            "status": r.status,
            "metadata": r.metadata,
            "md_len": len(r.markdown or ""),
            "links_count": len(r.links or []),
        }
        with open("crawl_result_meta.json", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print("Saved -> crawl_result_meta.json")

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 将结果按“原始/清洗/结构化”多层次保存，便于回溯。
- 出错时优先查看 `error` 与 `timings`，配合 `network-console-capture` 进行诊断（见 advanced）。
