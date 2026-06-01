"""
================================================================================
RAG 工具 — 本地知识库检索（懒加载版）
================================================================================

启动时不加载模型（省 16 秒），第一次调用 search_knowledge_base 时才加载。
向量模型：shibing624/text2vec-base-chinese（轻量中文，CPU 运行）
"""

import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PERSIST_DIRECTORY = "./chroma_db"
DOC_PATH = "./docs/company_docs.txt"

# 全局变量，懒加载
_vector_db = None
_embeddings = None


def _get_embeddings():
    """懒加载 embedding 模型（首次调用才下载/加载，省启动时间）"""
    global _embeddings
    if _embeddings is None:
        print("[RAG] 首次使用，正在加载向量模型（约需 10~15 秒）...")
        _embeddings = HuggingFaceEmbeddings(
            model_name="shibing624/text2vec-base-chinese",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("[RAG] 向量模型加载完毕。")
    return _embeddings


def _get_vector_db():
    """懒加载向量数据库"""
    global _vector_db
    if _vector_db is None:
        embeddings = _get_embeddings()

        if os.path.exists(PERSIST_DIRECTORY):
            print("[RAG] 加载已有向量数据库...")
            _vector_db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
        else:
            print("[RAG] 未找到数据库，正在从文档构建...")
            if not os.path.exists(DOC_PATH):
                raise FileNotFoundError(f"文档文件不存在: {DOC_PATH}")

            loader = TextLoader(DOC_PATH, encoding="utf-8")
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
            chunks = text_splitter.split_documents(documents)
            _vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=PERSIST_DIRECTORY
            )
            print("[RAG] 知识库构建完成。")
    return _vector_db


def search_knowledge_base(query: str) -> str:
    """
    在本地知识库中搜索相关内容。
    首次调用会自动加载模型（需等待），后续调用秒回。
    """
    print(f"   -> [RAG Search] 搜索: {query}")
    db = _get_vector_db()
    docs = db.similarity_search(query, k=3)

    if not docs:
        return "本地知识库中未找到相关机密信息。"

    result_text = "\n\n".join([f"片段 {i + 1}:\n{doc.page_content}" for i, doc in enumerate(docs)])
    return result_text
