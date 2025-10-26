# 会话管理（Session Management）

针对需要保持身份或共享状态的抓取，使用会话管理（共享 Cookie、缓存、上下文）。

## 示例：复用会话抓取多个页面（示意）

```python
# file: session_management_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URLS = [
    "https://example.com/account",
    "https://example.com/account/messages",
]

async def main():
    # 思路：在同一 AsyncWebCrawler 上下文中顺序抓取，复用浏览器上下文
    async with AsyncWebCrawler() as crawler:
        for u in URLS:
            r = await crawler.arun(u)
            print(u, r.status, r.metadata.get("title"))

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 登录表单可与 `hooks-auth` 结合，在 on_page_ready 阶段输入账号并提交。
- 区分不同身份的缓存/会话，避免数据串扰。
