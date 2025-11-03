# LookAE AI

![logo](./logo.png)

这是一个从 LookAE 获取 AE 插件和脚本数据之后搭建的语义搜索插件的项目，在这个项目当中你可以输入你想要做什么效果，它就会推荐给你合适的插件或脚本，这个插件或脚本具有什么功能。

```
项目结构
├── lookae_spider 从 LookAE 获取 AE 插件和脚本数据
├── vector 实现嵌入向量并语义搜索相关的内容
├── data 插件数据
├── main.py 爬取数据
├── build_vector_index.py 构建向量索引
├── semantic_search.py 语义搜索
└── README.md
```

HuggingFace 模型下载缓慢使用官方 CLI，[hf cli](https://huggingface.co/docs/huggingface_hub/en/guides/cli)
