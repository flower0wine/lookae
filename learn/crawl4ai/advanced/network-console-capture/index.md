# 网络与控制台捕获（Network & Console Capture）

抓取失败或内容缺失时，捕获网络请求与浏览器控制台日志有助于定位问题。

## 示例：开启网络/控制台日志（示意）

```python
# file: network_console_capture_basic.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com"

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(
            url=URL,
            # debug={"capture_network": True, "capture_console": True}
        )
        # 假设结果对象中附带日志/或另行导出到文件
        # print(res.debug_logs[:10])
        print(res.status, len(res.markdown or ""))

if __name__ == "__main__":
    asyncio.run(main())
```

## 建议

- 结合 `crawler-result` 的 `error` 与 `timings` 交叉排查。
- 对有反爬的站点，配合 `undetected-browser` 与 `proxy-security`。
