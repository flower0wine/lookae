# 浏览器、爬虫与 LLM 配置（Browser, Crawler & LLM Config）

理解配置项有助于稳定抓取、加速与质量控制。不同版本的 Crawl4AI 在参数命名上可能有差异，请以 API Reference 为准。

## 常见配置面向点

- 浏览器：无头/有头、视窗、超时、代理、UA、隐身、忽略证书错误等
- 渲染：是否执行 JS、脚本注入、等待网络空闲、截图/调试
- Crawler：并发/速率限制、重试、缓存、会话管理
- LLM：如启用 LLM 辅助抽取时的模型/温度/提示（如有）

## 示例：自定义浏览器与超时

```python
# file: config_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com"

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(
            url=URL,
            # browser={
            #   "headless": True,
            #   "viewport": {"width": 1200, "height": 900},
            #   "timeout": 20000,
            #   "user_agent": "Mozilla/5.0 ..."
            # },
            # crawler={
            #   "retries": 2,
            #   "rate_limit": {"rps": 2}
            # }
        )
        print(res.status, res.metadata.get("title"))

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 超时设置与站点复杂度匹配，避免不必要等待。
- 将可变参数（代理、UA、并发）外置到配置文件，便于不同环境切换。
- 与 `proxy-security`、`undetected-browser`、`session-management` 联动提高成功率。
