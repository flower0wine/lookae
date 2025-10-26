# Hooks 与鉴权（Hooks & Auth）

Hooks 允许在抓取生命周期的关键时刻执行自定义逻辑（注入脚本、打点、登录表单、Cookie 设置等）。请严格遵守安全最佳实践。

## 示例：登录前设置 Cookie 与脚本注入（示意）

```python
# file: hooks_auth_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com/private"

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(
            url=URL,
            # hooks={
            #   "on_execution_started": [
            #       {"type": "set_cookie", "name": "session", "value": "...", "domain": ".example.com"}
            #   ],
            #   "on_page_ready": [
            #       {"type": "inject_js", "code": "document.body.setAttribute('data-c4a', '1');"}
            #   ]
            # }
        )
        print(res.status, res.metadata.get("title"))

if __name__ == "__main__":
    asyncio.run(main())
```

## 安全提示

- 不要在不可信网站执行复杂脚本。
- Cookie/Token 等敏感信息请使用环境变量或安全注入，避免明文写入仓库。
