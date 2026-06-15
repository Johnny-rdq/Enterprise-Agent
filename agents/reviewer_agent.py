"""
================================================================================
[LLM] Reviewer Agent — AI 代码审查员
================================================================================

职责：检查代码执行结果，决定通过还是打回。
- 执行成功 → 返回 "PASS"，管线进入 SaveCode
- 执行失败 → 分析错误原因，打回 Coder 重写（最多 2 次）
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


# 审查节点 — 检查执行结果，快速通道 PASS / 失败则分析根因
def review_node(state: dict):
    print("\n[Reviewer] 正在检查代码执行结果...")

    exec_result = state.get("execution_result", "")  # 执行输出

    # 快速通道：执行成功直接 PASS
    if "[OK] 运行成功" in exec_result or "[OK] GUI" in exec_result or "GUI 程序已启动" in exec_result:
        print("      -> 代码执行成功，PASS！")
        return {"feedback": "PASS"}

    # 失败：LLM 分析根因并给出修复方向
    prompt = f"""你是一个严格的代码审查员。

代码运行结果/错误信息：
{exec_result}

用户的原始需求：{state.get("task", "")}

请分析失败的根本原因，给出修复方向。只输出诊断和建议，不要输出代码。
"""

    response = llm.invoke(prompt)
    return {"feedback": response.content}
