# 页面交互（Page Interaction）

本节演示抓取前/抓取中对页面进行交互，例如点击、输入、等待元素出现与滚动。不同版本的 Crawl4AI 在交互 API 上可能略有差异，本节采用保守范式，并在注释中提示可替代策略。

## 典型需求

- 点击“下一页/更多”按钮加载更多内容
- 在搜索框输入关键字并提交
- 滚动页面以触发懒加载
- 等待某个元素出现后再抽取

## 模式 1：抓取前注入交互脚本

对于简单的一次性交互，可在导航后注入 JavaScript，或使用内置的交互钩子（如有）。

```python
# file: page_interaction_click_once.py
import asyncio
from crawl4ai import AsyncWebCrawler

TARGET = "https://example.com/infinite"

async def main():
    async with AsyncWebCrawler() as crawler:
        # 思路：先加载，再执行一次点击（此处用 JS 选择器示例）。
        # 具体 API 可能提供 "hooks" 或 "js" 参数用来在页面上下文执行脚本。
        # 伪参数示例：hooks={"on_page_ready": [...]} 或 inject_js=["..."]
        result = await crawler.arun(
            url=TARGET,
            # inject_js=["document.querySelector('#loadMore')?.click();"],
            # 或者在 on_page_ready 钩子中执行点击
        )
        print("status:", result.status)
        print("title:", result.metadata.get("title"))
        print((result.markdown or "")[:500])

if __name__ == "__main__":
    asyncio.run(main())
```

上面的写法展示了“加载后点击一次”的范式。具体参数名需参考当前版本的 `Browser/Crawler Config` 与 `Hooks` 文档。

## 模式 2：多步交互（点击多次 + 等待）

当需要连续点击“下一页”，常见做法是：

1. 循环执行点击；
2. 每次点击后等待网络静止、或等待某个选择器出现；
3. 达到最大次数或未出现新内容则停止。

下面给出一种保守的多步框架（伪参数，演示控制结构）：

```python
# file: page_interaction_multi_clicks.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com/list"
MAX_CLICKS = 5

async def main():
    async with AsyncWebCrawler() as crawler:
        # 伪参数：pre_actions/post_actions 仅作为示意，实际以当前版本 API 为准
        result = await crawler.arun(
            url=URL,
            # pre_actions=[{"type": "wait_selector", "selector": ".items"}],
            # post_actions=[
            #     {"type": "repeat", "times": MAX_CLICKS, "steps": [
            #         {"type": "click", "selector": "button.next"},
            #         {"type": "wait_network_idle", "timeout": 5000},
            #     ]}
            # ]
        )
        print("status:", result.status)
        print("items length (md chars):", len(result.markdown or ""))

if __name__ == "__main__":
    asyncio.run(main())
```

## 模式 3：滚动加载（虚拟滚动见 advanced/virtual-scroll）

某些站点仅通过滚动加载更多内容。可在抓取前/中执行多次 `window.scrollTo` 并等待内容追加。

```python
# file: page_interaction_scroll.py
import asyncio
from crawl4ai import AsyncWebCrawler

URL = "https://example.com/scroll"

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=URL,
            # inject_js=[
            #     "let y=0; let i=0; const step=1000; const max=10;\n" \
            #     "async function s(){for(i=0;i<max;i++){y+=step;window.scrollTo(0,y);await new Promise(r=>setTimeout(r,800));}}; s();"
            # ]
        )
        print("status:", result.status)
        print("title:", result.metadata.get("title"))

if __name__ == "__main__":
    asyncio.run(main())
```

提示：长期维护建议把交互脚本外置为 C4A-Script 或 hooks，以便复用与审计。高阶内容见 `advanced/virtual-scroll` 与 `advanced/hooks-auth`。
