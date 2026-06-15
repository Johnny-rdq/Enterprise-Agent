"""
================================================================================
[LLM] Planner Agent — AI 项目经理
================================================================================

职责：Router 已经判定这是编码/搜索任务，Planner 负责拆解为分步执行计划。
不再输出"无需编码"——那个判断 Router 已经做了。
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


# 计划节点 — Router 已判定需要编码，直接拆解为分步计划
def plan_node(state: dict):
    task = state.get("task", "")  # 用户原始输入
    history_info = state.get("context_output", "")  # 历史上下文

    prompt = f"""
你是一个资深的 AI 项目经理。用户任务已经过 Router 判定，确认需要执行以下之一：
- 编写代码 / 开发程序
- 搜索实时信息 / 最新动态

【用户任务】：
{task}

【历史上下文】：
{history_info if history_info else "无"}

请输出简洁的分步执行计划（3-5 步），包括：
- 需要调研哪些技术点
- 代码需要哪些功能模块
- 特殊注意事项

如果是搜索实时信息的任务，输出搜索计划而非编码计划。
禁止输出"无需编码"这类判断——Router 已经做过了。
"""

    response = llm.invoke(prompt)  # 同步调用 LLM
    return {"plan": response.content}
