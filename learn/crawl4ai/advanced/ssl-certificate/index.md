# SSL 证书（SSL Certificate）

处理自签名证书或证书错误的站点访问问题。

## 示例：忽略证书错误（仅用于受控环境，谨慎使用）

```python
# file: ssl_certificate_ignore_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://self-signed.badssl.com/"

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(
            url=URL,
            # browser={"ignore_https_errors": True}
        )
        print(res.status, res.metadata.get("title"))

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 仅在内网或测试环境临时放宽证书校验；生产环境建议正确安装 CA 或信任链。
