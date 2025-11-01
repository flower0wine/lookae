# main.py
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatLiteLLM  # 关键：官方集成

# ================== 加载环境变量 ==================
load_dotenv()

# ================== LLM：DeepSeek（官方支持）==================
llm = ChatLiteLLM(
    model="deepseek/deepseek-chat",   # 必须是 deepseek/xxx 格式
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
    max_tokens=1024,
    streaming=False,                  # 改为 True 启用流式
)

# ================== 嵌入 + 向量库 ==================
embeddings = HuggingFaceEmbeddings(model_name="./models/bge-small-zh-v1.5")
loader = PyPDFLoader("test.pdf")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(docs)

vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# ================== Prompt ==================
prompt = ChatPromptTemplate.from_template(
    "请根据以下上下文回答问题，只使用上下文中的信息：\n\n"
    "上下文：{context}\n\n"
    "问题：{question}\n"
    "回答："
)

# ================== 格式化文档 ==================
format_docs = lambda docs: "\n\n".join(doc.page_content for doc in docs)

# ================== RAG 链（LCEL）==================
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
)

# ================== 提问 ==================
answer = rag_chain.invoke("文档当中有什么？")
print(answer.content)  # v1.0+ 返回 AIMessage，内容在 .content