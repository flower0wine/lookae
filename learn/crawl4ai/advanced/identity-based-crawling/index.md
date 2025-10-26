# 身份化抓取（Identity Based Crawling）

在多租户或多账号场景，需要以不同身份抓取并隔离会话、缓存与代理设置。

## 示例：以多身份抓取不同页面（示意）

```python
# file: identity_based_crawling_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

IDENTITIES = [
    {"name": "user_a", "cookies": {"session": "..."}, "proxy": None},
    {"name": "user_b", "cookies": {"session": "..."}, "proxy": "http://127.0.0.1:7890"},
]
URL = "https://example.com/account"

async def crawl_with_identity(identity):
    name = identity["name"]
    cookies = identity.get("cookies")
    proxy = identity.get("proxy")
    async with AsyncWebCrawler() as crawler:
        r = await crawler.arun(
            url=URL,
            # browser={"proxy": {"server": proxy}} if proxy else None,
            # hooks={"on_execution_started": [
            #    {"type": "set_cookie", "name": "session", "value": cookies.get("session"), "domain": ".example.com"}
            # ]}
        )
        print(name, r.status, r.metadata.get("title"))

async def main():
    await asyncio.gather(*(crawl_with_identity(i) for i in IDENTITIES))

if __name__ == "__main__":
    asyncio.run(main())
```

## 提示

- 区分每个身份的缓存与下载目录，避免串扰。
- 配合 `session-management`、`hooks-auth` 与 `proxy-security` 形成完整方案。
