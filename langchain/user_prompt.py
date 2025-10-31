user_prompt = """
请你将下面的内容转换为 JSON 格式

# JSON格式要求
{struct}


如果有未在 JSON 格式要求当中设定的数据，请你将其放在 other 字段当中
{content}
"""

json_str = """
```json
{
    "title": "",
    "slug": "",
    "author": "",
    "post_date": "",
    "source_url": "",
    "category": "",
    "tags": [],
    "content": "这是文章内容",
    "image_urls": [],
    "video_urls": [],
    "supported_versions": "",
    "supported_os": "",
    "download_links": [
        {
            "name": "",
            "url": ""
        }
    ],
}
```

注意: 尽可能将 content 当中的信息提取出来，只让它具有介绍性信息，content 不要包含已经被提取出来的信息
"""

def get_use_prompt(content: str) -> str:
    return user_prompt.format(content=content, struct=json_str)