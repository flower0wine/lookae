import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import List
import hashlib
import asyncio
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


class FileVectorStoreManager:
    """
    全自动文件级向量库管理器
    - 支持中文文件名（通过哈希索引）
    - 启动时自动构建所有未索引 PDF
    - 支持增量更新（新增/删除 PDF）
    - 内部维护 processed.json 与 index_map.json
    """

    def __init__(self, pdf_dir: str, index_dir: str, embeddings):
        self.pdf_dir = Path(pdf_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)
        self.embeddings = embeddings
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.cache = {}
        self.processed_file = Path("processed.json")
        self.index_map_file = Path("index_map.json")

        # 载入文件名映射
        self.index_map = self._load_index_map()

        # 自动同步索引
        self._sync_all_indexes()

    # ========= 工具函数 =========
    def _hash_filename(self, filename: str) -> str:
        """将文件名哈希化，确保安全文件名"""
        return hashlib.sha1(filename.encode("utf-8")).hexdigest()

    def _load_index_map(self) -> dict:
        if self.index_map_file.exists():
            with open(self.index_map_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_index_map(self):
        with open(self.index_map_file, "w", encoding="utf-8") as f:
            json.dump(self.index_map, f, ensure_ascii=False, indent=2)

    def _load_processed(self) -> set:
        if self.processed_file.exists():
            with open(self.processed_file, "r", encoding="utf-8") as f:
                return set(json.load(f).get("files", []))
        return set()

    def _save_processed(self, processed: set):
        with open(self.processed_file, "w", encoding="utf-8") as f:
            json.dump({"files": list(processed)}, f, ensure_ascii=False, indent=2)

    def _index_path(self, filename: str) -> Path:
        """根据原文件名找到实际索引路径"""
        hashed = self.index_map.get(filename)
        if not hashed:
            hashed = self._hash_filename(filename)
            self.index_map[filename] = hashed
            self._save_index_map()
        return self.index_dir / f"{hashed}.faiss"

    def _is_indexed(self, filename: str) -> bool:
        return self._index_path(filename).exists()

    def load_pdf(self, file_path: Path) -> List[Document]:
        loader = PyPDFLoader(str(file_path))
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_file"] = file_path.name
        return docs

    # ========= 核心构建 =========
    def _build_index(self, pdf_path: Path):
        docs = self.load_pdf(pdf_path)
        chunks = self.text_splitter.split_documents(docs)
        vs = FAISS.from_documents(chunks, self.embeddings)
        index_path = self._index_path(pdf_path.name)
        vs.save_local(str(index_path.parent), index_name=index_path.stem)
        print(f"索引构建完成: {pdf_path.name} → {index_path.name}")

    def _sync_all_indexes(self):
        print("正在初始化向量库管理器...")
        current_pdfs = {p.name for p in self.pdf_dir.glob("*.pdf")}
        processed = self._load_processed()
        indexed = {p.stem for p in self.index_dir.glob("*.faiss")}

        # 删除不存在的 PDF
        for f in list(processed):
            if f not in current_pdfs:
                self.delete_index(f)
                processed.discard(f)

        # 构建未索引文件
        to_build = current_pdfs - processed
        if to_build:
            print(f"发现 {len(to_build)} 个新文件，构建索引...")
            for pdf_name in to_build:
                pdf_path = self.pdf_dir / pdf_name
                try:
                    self._build_index(pdf_path)
                    processed.add(pdf_name)
                except Exception as e:
                    print(f"  失败: {pdf_name} → {e}")
            self._save_processed(processed)
        else:
            print("所有 PDF 已索引。")

        print(f"初始化完成！共 {len(current_pdfs)} 个文件，{len(processed)} 个已索引。")

    def get_index(self, filename: str) -> FAISS:
        if filename in self.cache:
            return self.cache[filename]

        pdf_path = self.pdf_dir / filename
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 不存在: {filename}")

        index_path = self._index_path(filename)
        vs = FAISS.load_local(
            folder_path=str(index_path.parent),
            embeddings=self.embeddings,
            index_name=index_path.stem,
            allow_dangerous_deserialization=True
        )
        self.cache[filename] = vs
        return vs

    def search(self, filename: str, query: str, k: int = 5) -> List[Document]:
        vs = self.get_index(filename)
        return vs.similarity_search(query, k=k)

    def delete_index(self, filename: str):
        path = self._index_path(filename)
        if path.exists():
            path.unlink()
            self.cache.pop(filename, None)
            processed = self._load_processed()
            processed.discard(filename)
            self._save_processed(processed)
            print(f"索引已删除: {filename}")
        # 删除映射
        if filename in self.index_map:
            del self.index_map[filename]
            self._save_index_map()

    def list_indexed_files(self) -> List[str]:
        return list(self._load_processed())

    def resync(self):
        print("正在重新同步索引...")
        self._sync_all_indexes()



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
    语义搜索 PDF 内容
    
    Args:
        query: 要搜索的问题或关键词
        filenames: 文件名列表，可选。只搜索指定文件当中的内容
                   如果为 None，自动从所有文件中找最相关的
    Returns:
        格式化后的检索结果，含有内容来源
    """
    def is_safe_filename(f: str):
        return Path(f).name == f and not f.startswith('.')

    if filenames:
        target_files = [f for f in filenames if is_safe_filename(f) and (PDF_DIR / f).exists()]
        if not target_files:
            return json.dumps({"error": "指定文件不存在或路径非法", "requested": filenames}, ensure_ascii=False)
    else:
        # 2. 自动路由：基于相似度分数
        candidate_scores = []
        for pdf_file in PDF_DIR.glob("*.pdf"):
            if not manager._is_indexed(pdf_file.name):
                continue  # 跳过未索引
            try:
                vs = manager.get_index(pdf_file.name)
                docs = vs.similarity_search_with_score(query, k=1)
                if docs:
                    _, score = docs[0]
                    candidate_scores.append((pdf_file.name, score))
            except Exception as e:
                continue
        if not candidate_scores:
            return json.dumps({"error": "无可用索引文件"}, ensure_ascii=False)
        target_files = [name for name, _ in sorted(candidate_scores, key=lambda x: x[1])[:3]]

    # 3. 搜索并返回结构化 JSON
    results = []
    for filename in target_files:
        try:
            vs = manager.get_index(filename)
            docs = vs.similarity_search_with_score(query, k=top_k_per_file)
            file_results = []
            for doc, score in docs:
                page = doc.metadata.get("page", 0) + 1
                text = doc.page_content.strip().replace("\n", " ")[:800]
                file_results.append({
                    "page": page,
                    "content": text,
                    "score": float(score)
                })
            results.append({"filename": filename, "matches": file_results})
        except Exception as e:
            results.append({"filename": filename, "error": str(e)})

    return json.dumps({"results": results}, ensure_ascii=False, indent=2)


@tool
def ask_user_for_file_clarification(
    question: str,
    candidate_files: List[str]
) -> str:
    """
    当多个文件当中存在类似的信息，而用户没有说明从哪个文件当中获取该信息时，这时请你使用此工具询问用户从哪些文件获取数据。用户可能并不知道有多个文件包含他需要的信息
    
    此工具会直接与用户交互，打印候选文件列表并等待用户输入选择的文件名。
    
    Args:
        question: 你想询问用户的问题
        candidate_files: 候选文件名列表（至少2个），这些文件有相似内容
    
    Returns:
        用户的回答，可能包含需要的某个文件，也可能包含多个文件，甚至可能没有任何文件
    """
    if len(candidate_files) < 2:
        return json.dumps({"error": "候选文件必须至少2个时才应该调用该工具"}, ensure_ascii=False)
    
    print(question)
    for i, fname in enumerate(candidate_files, 1):
        print(f"  {i}. {fname}")
    print("请输入您想选择的文件的编")
    
    while True:
        try:
            choice = int(input().strip())
            if choice == 0:
                return json.dumps({"selected": "none"}, ensure_ascii=False)
            if 1 <= choice <= len(candidate_files):
                selected = candidate_files[choice - 1]
                print(f"已选择: {selected}")
                return json.dumps({"selected": selected}, ensure_ascii=False)
            else:
                print("无效编号，请重试。")
        except ValueError:
            print("请输入数字编号。")


agent = create_agent(
    model=llm,
    tools=[search_in_pdfs, ask_user_for_file_clarification],
    system_prompt="""
    你是一个助手，回答用户的问题。可以调用工具来解决问题，你需要熟悉每个工具的应用场景。

    特别严格判断：当用户需要的内容存在多个项目当中时请你使用ask_user_for_file_clarification询问用户，请求获取更多信息
    """
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

async def chat():
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
        for token, metadata in agent.stream(  
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="messages",
        ):
            print(f"node: {metadata['langgraph_node']}")
            print(f"content: {token.content_blocks}")
            print("\n")

if __name__ == "__main__":
    asyncio.run(chat())