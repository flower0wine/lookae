# 代理与安全（Proxy & Security）

在企业网络或目标站点有访问限制时，常需要代理、UA 调整、限速与安全设置。

## 示例：为浏览器配置代理与 UA（示意）

```python
# file: proxy_security_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com"

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(
            url=URL,
            # browser={
            #   "proxy": {"server": "http://127.0.0.1:7890"},
            #   "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
            # },
            # crawler={
            #   "rate_limit": {"rps": 1}
            # }
        )
        print(res.status, len(res.markdown or ""))

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 保护凭据：使用环境变量/密钥管理服务，不要硬编码。
- 谨慎对待登录/表单/Hook：避免在不可信站点执行潜在危险脚本（参考 `hooks-auth` 的安全提示）。
