"""
================================================================================
🧠 Reviewer Agent — AI 代码审查员
================================================================================

职责：检查代码执行结果，决定通过还是打回。
- 执行成功 → 返回 "PASS"，管线进入 SaveCode
- 执行失败 → 分析错误原因，打回 Coder 重写（最多 2 次）

DP 改动：提示词从英文改为中文
"""

from langchain_openai import ChatOpenAI
from core.config import settings

import os

llm = ChatOpenAI(
    model="qwen-turbo",
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.7  # 如果你原来有 temperature 等参数，可以保留
)


def review_node(state: dict):
    """
    被 LangGraph 工作流调用的入口函数。
    输入：state["execution_result"]、state["task"]
    输出：{"feedback": "PASS"} 或 {"feedback": "错误分析..."}
    """
    print("\n[Reviewer] 正在检查代码执行结果...")

    exec_result = state.get("execution_result", "")

    # DP: 快速通道 — 执行成功直接 PASS
    if "✅ 运行成功" in exec_result or "success" in exec_result.lower():
        print("      -> 代码执行成功，PASS！")
        return {"feedback": "PASS"}

    # DP: 失败 → 分析根因，给出修复建议（中文）
    prompt = f"""你是一个严格的代码审查员。

代码运行结果/错误信息：
{exec_result}

用户的原始需求：{state.get("task", "")}

请分析失败的根本原因，给出修复方向。只输出诊断和建议，不要输出代码。
"""

    response = llm.invoke(prompt)
    return {"feedback": response.content}
