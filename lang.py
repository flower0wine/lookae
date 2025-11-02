import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatLiteLLM
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain.agents import create_agent


# ================== 配置 ==================
load_dotenv()

PDF_DIR = Path("pdfs")                    # ← 所有 PDF 放这里
INDEX_DIR = Path("faiss_index")           # 向量库保存目录
PROCESSED_FILE = Path("processed.json")   # 记录已处理文件
EMBEDDING_MODEL = "./models/bge-small-zh-v1.5"

# ================== LLM ==================
llm = ChatLiteLLM(
    model="deepseek/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
    max_tokens=1024,
    streaming=False,
)

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# ================== 加载已处理记录 ==================
def load_processed() -> set:
    if PROCESSED_FILE.exists():
        with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get("files", []))
    return set()

def save_processed(processed: set):
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump({"files": list(processed)}, f, ensure_ascii=False, indent=2)

def load_pdf(file_path: Path) -> List[Document]:
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    # 添加文件名到 metadata
    for doc in docs:
        doc.metadata["source_file"] = file_path.name
    return docs


class FileVectorStoreManager:
    """
    自动管理「一个 PDF = 一个 FAISS 索引」
    完全透明，无需手动干预
    """
    def __init__(self, pdf_dir: str, index_dir: str, embeddings):
        self.pdf_dir = Path(pdf_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)
        self.embeddings = embeddings
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.cache = {}  # filename -> FAISS (内存缓存)

    def _index_path(self, filename: str) -> str:
        return self.index_dir / f"{Path(filename).stem}.faiss"

    def _is_indexed(self, filename: str) -> bool:
        return self._index_path(filename).exists()

    def _build_index(self, pdf_path: Path):
        """为单个 PDF 构建索引"""
        docs = load_pdf(pdf_path)
        chunks = self.text_splitter.split_documents(docs)
        vs = FAISS.from_documents(chunks, self.embeddings)
        vs.save_local(str(self.index_dir), index_name=pdf_path.name)
        print(f"索引构建完成: {pdf_path.name}")

    def get_or_create_index(self, filename: str) -> FAISS:
        """自动加载或创建索引（核心！）"""
        if filename in self.cache:
            return self.cache[filename]

        pdf_path = self.pdf_dir / filename
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 不存在: {filename}")

        # 如果索引不存在 → 自动构建
        if not self._is_indexed(filename):
            print(f"未找到索引，自动构建: {filename}")
            self._build_index(pdf_path)

        # 加载索引
        vs = FAISS.load_local(
            folder_path=str(self.index_dir),
            embeddings=self.embeddings,
            index_name=filename,
            allow_dangerous_deserialization=True
        )
        self.cache[filename] = vs
        return vs

    def search(self, filename: str, query: str, k: int = 5) -> List[Document]:
        """自动检索"""
        vs = self.get_or_create_index(filename)
        return vs.similarity_search(query, k=k)

    def delete_index(self, filename: str):
        """删除索引"""
        path = self._index_path(filename)
        if path.exists():
            path.unlink()
            self.cache.pop(filename, None)
            print(f"索引已删除: {filename}")

    def list_indexed_files(self) -> List[str]:
        """列出已索引文件"""
        return [p.stem + ".pdf" for p in self.index_dir.glob("*.faiss")]

manager = FileVectorStoreManager(
    pdf_dir="pdfs",
    index_dir="faiss_index",
    embeddings=embeddings
)

@tool
def search_in_pdfs(
    query: str,
    filenames: List[str] = None,
    top_k_per_file: int = 3
) -> str:
    """
    智能搜索 PDF 内容（文件级隔离）
    
    Args:
        query: 要搜索的问题或关键词
        filenames: 可选，指定搜索的文件名列表
                   如果为 None，自动从所有文件中找最相关的
        top_k_per_file: 每个文件返回的片段数
    
    Returns:
        格式化后的检索结果，带来源
    """
    if filenames:
        target_files = [f for f in filenames if (PDF_DIR / f).exists()]
        if not target_files:
            return f"指定文件不存在：{filenames}"
    else:
        # 自动选择：用所有文件的第一页做轻量路由
        candidate_scores = []
        for pdf_file in PDF_DIR.glob("*.pdf"):
            try:
                vs = manager.get_or_create_index(pdf_file.name)
                docs = vs.similarity_search(query, k=1)
                if docs:
                    candidate_scores.append((pdf_file.name, docs[0]))
            except:
                continue
        # 按相关性排序
        target_files = [name for name, _ in sorted(candidate_scores, key=lambda x: len(x[1].page_content), reverse=True)[:3]]

    if not target_files:
        return "未找到相关 PDF 文件或内容。"

    results = []
    for filename in target_files:
        try:
            docs = manager.search(filename, query, k=top_k_per_file)
            if not docs:
                continue
            results.append(f"\n### 【{filename}】")
            for doc in docs:
                page = doc.metadata.get("page", 0) + 1
                text = doc.page_content.strip().replace("\n", " ")[:800]
                results.append(f"[第{page}页] {text}")
        except Exception as e:
            results.append(f"\n### 【{filename}】\n[错误] {e}")

    return "\n".join(results) if results else "未检索到相关内容。"


agent = create_agent(
    model=llm,
    tools=[search_in_pdfs],
    system_prompt="你是一个助手，回答用户的问题。可以调用工具来解决问题"
)

def debug_retrieval(question: str, filename: str = "test.pdf"):
    print(f"\n{'='*60}")
    print(f"调试检索: 文件={filename} | 问题={question}")
    print(f"{'-'*60}")
    try:
        docs = manager.search(filename, question, k=6)
        if not docs:
            print("警告：未检索到任何内容！")
            return
        for i, doc in enumerate(docs):
            page = doc.metadata.get("page", 0) + 1
            print(f"\n[{i+1}] [第{page}页]")
            print(f"    {doc.page_content[:400]}...")
    except Exception as e:
        print(f"错误: {e}")
    print(f"{'='*60}\n")

def chat():
    print("\n=== 文件级 RAG 系统已就绪 ===")
    print(f"PDF 目录: {len(list(PDF_DIR.glob('*.pdf')))} 个文件")
    print(f"已索引: {len(manager.list_indexed_files())} 个")
    print("输入 'exit' 退出\n")

    while True:
        question = input("\n你的问题: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        print("检索中...")
        # debug_retrieval(question)  # 调试指定文件
        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        print(f"\n回答:\n{result}\n")

if __name__ == "__main__":
    chat()