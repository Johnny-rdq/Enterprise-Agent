"""
================================================================================
RAG 工具 — 本地知识库检索（阿里云 DashScope Embedding API 版）
================================================================================

DP 优化：所有重型 import 都延迟到首次使用时才加载，启动快 10 秒。
首次 RAG 调用仍需 4~8 秒构建向量库（API 调用），之后秒回。
"""

import os
import shutil
import time

PERSIST_DIRECTORY = "./chroma_db"
DOC_PATH = "./docs/company_docs.txt"
VERSION_FILE = os.path.join(PERSIST_DIRECTORY, ".embedding_version")
CURRENT_VERSION = "v2"

_vector_db = None


def _get_embeddings():
    """DP: 延迟导入重型库，只在首次调用 RAG 时才加载"""
    from langchain_core.embeddings import Embeddings
    from dashscope import TextEmbedding
    from core.config import settings

    class DashScopeEmbeddings(Embeddings):
        """LangChain 兼容的 DashScope Embedding 包装类"""

        def embed_documents(self, texts):
            resp = TextEmbedding.call(
                model="text-embedding-v2",
                input=texts,
                api_key=settings.API_KEY,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Embedding API 调用失败: {resp.message}")
            return [item["embedding"] for item in resp.output["embeddings"]]

        def embed_query(self, text):
            resp = TextEmbedding.call(
                model="text-embedding-v2",
                input=[text],
                api_key=settings.API_KEY,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Embedding API 调用失败: {resp.message}")
            return resp.output["embeddings"][0]["embedding"]

    return DashScopeEmbeddings()


def _get_vector_db():
    """DP: 懒加载向量数据库 — 首次调用才初始化，后续直接读缓存"""
    global _vector_db

    if _vector_db is not None:
        return _vector_db

    # DP: 只有在真正需要时才导入这些重库
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_chroma import Chroma

    embeddings = _get_embeddings()

    need_rebuild = not (os.path.exists(PERSIST_DIRECTORY) and os.path.exists(VERSION_FILE))
    if not need_rebuild:
        with open(VERSION_FILE, "r") as f:
            need_rebuild = f.read().strip() != CURRENT_VERSION

    if need_rebuild:
        if os.path.exists(PERSIST_DIRECTORY):
            shutil.rmtree(PERSIST_DIRECTORY)

        print("[RAG] 正在通过 DashScope API 构建向量数据库...")
        t0 = time.time()
        if not os.path.exists(DOC_PATH):
            raise FileNotFoundError(f"文档文件不存在: {DOC_PATH}")

        loader = TextLoader(DOC_PATH, encoding="utf-8")
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        chunks = text_splitter.split_documents(documents)
        print(f"[RAG] 文档切分为 {len(chunks)} 段，调用 Embedding API 生成向量...")

        _vector_db = Chroma.from_documents(
            documents=chunks, embedding=embeddings, persist_directory=PERSIST_DIRECTORY,
        )
        os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
        with open(VERSION_FILE, "w") as f:
            f.write(CURRENT_VERSION)
        print(f"[RAG] 向量数据库构建完成（耗时 {time.time()-t0:.1f}秒）")
    else:
        t0 = time.time()
        print("[RAG] 加载已有向量数据库（秒级）...")
        _vector_db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
        print(f"[RAG] 向量数据库就绪（耗时 {time.time()-t0:.1f}秒）")

    return _vector_db


# DP: 公司文档相关的关键词 — 命中这些才触发 RAG，闲聊不触发
_RAG_KEYWORDS = [
    "迟到", "惩罚", "罚款", "福利", "CEO", "老板", "水豚", "密码", "机房",
    "考勤", "打卡", "年假", "火星日", "补贴", "生发水", "食堂", "深渊",
    "极客", "公司", "内部", "机密", "规定", "制度", "门禁", "工资",
    "奖金", "bug修复", "炸酱面", "拖鞋", "猛犸象",
]


def _is_company_question(query: str) -> bool:
    """DP: 快速判断是否可能是公司文档相关的问题，避免闲聊也触发 RAG"""
    return any(kw in query for kw in _RAG_KEYWORDS)


def search_knowledge_base(query: str) -> str:
    """在本地知识库中搜索。首次调用构建向量库，后续秒回。"""
    # DP: 快速预判 — 跟公司文档无关的问题直接跳过，不浪费 API 调用
    if not _is_company_question(query):
        print(f"   -> [RAG Search] 跳过（非公司文档问题）: {query}")
        return "本地知识库中未找到相关机密信息。"

    print(f"   -> [RAG Search] 搜索: {query}")
    db = _get_vector_db()
    t0 = time.time()
    docs = db.similarity_search(query, k=3)
    print(f"   -> [RAG Search] 向量检索耗时: {time.time()-t0:.1f}秒")

    if not docs:
        return "本地知识库中未找到相关机密信息。"

    return "\n\n".join([f"片段 {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])
