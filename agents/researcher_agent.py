"""
================================================================================
Researcher Agent — AI 情报分析师（简化版）

职责：为 Coder 准备上下文资料。已砍联网搜索，直接用 LLM 整理计划。
"""

from langchain_openai import ChatOpenAI
from core.config import settings

llm = ChatOpenAI(
    model=settings.MODEL_NAME,
    api_key=settings.API_KEY,
    base_url=settings.BASE_URL,
    temperature=0.7,
    streaming=True
)


# 调研节点 — 直接用 LLM 整理计划作为 Coder 的上下文
def research_node(state: dict):
    task = state.get("task", "")
    plan = state.get("plan", "")

    print(f"[Researcher] 整理上下文资料...")

    # 简单任务直接传计划
    if len(task) < 100 and len(plan) < 500:
        return {"research_info": f"任务：{task}\n计划：{plan}"}

    # 复杂任务让 LLM 精简
    prompt = f"""你是技术资料整理员。请将以下计划精简为 Coder 能直接使用的要点（3-5条）。

任务：{task}
计划：{plan}

只输出要点列表，不要废话。"""
    msg = llm.invoke(prompt)
    return {"research_info": msg.content}
