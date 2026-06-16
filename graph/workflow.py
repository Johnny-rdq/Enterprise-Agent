"""
================================================================================
[LLM] AI 智能体协作平台 — LangGraph 工作流核心
   Router -> Planner -> Researcher -> Coder -> Executor -> Reviewer -> SaveCode
================================================================================
"""

import os
import re
import subprocess
import time
from datetime import datetime
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from core.config import settings
from agents.planner_agent import plan_node
from agents.researcher_agent import research_node
from agents.coder_agent import code_node
from agents.reviewer_agent import review_node
from tools.execute_tool import run_code_safely

class AgentState(TypedDict, total=False):
    task: str
    context_output: str  # 管线最终输出的内容（对话回复 / 保存确认 / 精简计划）
    plan: str
    code: str
    execution_result: str
    feedback: str
    retry_count: int

# LLM 实例 — streaming=True 确保流式输出
llm = ChatOpenAI(
    model=settings.MODEL_NAME,
    api_key=settings.API_KEY,
    base_url=settings.BASE_URL,
    temperature=0.7,
    streaming=True
)


# 路由裁判 — 关键词 + LLM 双层判断，chat 走快速通道，planner 走编码管线
def router_judge(state: AgentState) -> Literal["chat_rag", "planner"]:
    task = state["task"].strip()

    # 编码关键词 → 最优先判断（避免被问候检测误拦截）
    _code_kw = ["写代码", "编写", "写个", "写一个", "写一", "开发", "实现",
                "python", "html", "javascript", "react", "vue", "css", "爬虫",
                "网页", "游戏", "程序", "脚本", "api", "后端", "前端", "网站",
                "帮我写", "帮我做", "生成", "创建一个"]
    if any(kw in task.lower() for kw in _code_kw):
        print("[Router] >> 编码关键词 -> 多Agent管线")
        return "planner"

    # 纯问候短句快速拦截
    greeting_keywords = ["你好", "嗨", "hello", "hi", "哈哈", "谢谢", "再见", "拜拜", "早上好", "晚上好", "晚安"]
    if (len(task) <= 6 or
            (len(task) <= 15 and any(kw in task.lower() for kw in greeting_keywords))):
        print("[Router] >> 纯问候 -> 对话通道")
        return "chat_rag"

    # 搜索/信息类关键词 → chat_rag（纯 LLM 对话，不需要编码管线）
    _search_kw = ["搜索", "搜一下", "查一下", "查查", "帮我查", "帮我搜", "找一下",
                  "开始了吗", "最新", "新闻", "今天", "现在", "最近", "实时", "刚刚", "当前",
                  "什么时候", "在哪里", "开始了没", "结束了吗", "世界杯", "奥运会", "比赛"]
    if any(kw in task.lower() for kw in _search_kw):
        print("[Router] >> 搜索/信息关键词 -> 对话+搜索通道")
        return "chat_rag"

    # LLM 路由兜底
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个精准的路由分类器。分析用户输入，只返回一个词：

返回 chat_rag（对话+搜索通道）：
- 纯闲聊、问候、知识问答（"什么是AI"）
- 翻译、总结、建议咨询
- 纯文字创作：写诗、写信、写文章
- 搜索实时信息、新闻、最新动态
- 用户只想了解/查询/搜索信息，不需要生成代码

返回 planner（多Agent编码管线）：
- 要求写代码/编程/开发/实现某个程序
- 提到编程语言（Python/HTML/JS/React等）
- 要求创建项目、网站、游戏、爬虫

关键：只有用户明确要求"写代码""开发""实现程序"才返回 planner。
信息查询、搜索、问答一律返回 chat_rag。
只能返回一个词。"""),
        ("user", "{input}")
    ])

    t0 = time.time()
    chain = prompt | llm
    response = chain.invoke({"input": task})
    decision = response.content.strip().lower()

    print(f"[Router] [IN]  输入: {task[:60]}...")
    print(f"[Router] [LLM] LLM路由: {decision}（{time.time()-t0:.1f}s）")

    if "planner" in decision:
        print(f"[Router] -> 多Agent管线")
        return "planner"
    else:
        print(f"[Router] -> 对话通道")
        return "chat_rag"


# 对话节点 — 纯 LLM 对话
async def chat_rag_node(state: AgentState, config: RunnableConfig | None = None) -> dict:
    task = state["task"]
    print(f"[Chat] {task[:60]}...")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个友好专业的 AI 助手，请用中文简洁回答用户的问题。使用 Markdown 格式。"),
        ("user", "{input}")
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"input": task}, config=config)
    return {"context_output": response.content}


# 代码执行节点 — 剥离 markdown 包裹后隔离沙盒运行
def execute_node(state: AgentState) -> dict:
    code = state.get("code", "")
    if not code:
        return {"execution_result": "错误：没有可执行的代码。"}

    # 剥离 ```python ... ``` 包裹
    code = code.strip()
    if code.startswith("```"):
        lines = code.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = "\n".join(lines)

    result = run_code_safely(code)  # 隔离沙盒执行
    retry_count = state.get("retry_count", 0) + 1
    return {"execution_result": result, "retry_count": retry_count}


# 审查决策 — PASS 保存，失败打回重试（最多2次），前端代码跳过执行直接通过
def review_decision(state: AgentState) -> Literal["save_code", "code_node", "__end__"]:
    feedback = state.get("feedback", "")
    execution_result = state.get("execution_result", "")
    retry_count = state.get("retry_count", 0)

    # 前端代码跳过 Python 执行是正常的，不需要重试
    if "前端代码" in execution_result or "跳过Python沙盒" in execution_result:
        print("[Reviewer] [OK] 前端代码无需Python执行，直接保存")
        return "save_code"

    if "PASS" in feedback:
        print("[Reviewer] [OK] 审查通过，保存代码...")
        return "save_code"
    if retry_count >= 2:
        print("[Reviewer] [WARN] 已达最大重试次数，管线结束。")
        return "__end__"

    print(f"[Reviewer] [RETRY] 需要修改（第 {retry_count + 1}/2 次），打回 Coder。")
    return "code_node"


# 代码保存节点 — 落盘到 completed_code/，自动识别语言选扩展名，并打开编辑器
def save_code_node(state: AgentState) -> dict:
    code = state.get("code", "")
    task = state.get("task", "untitled")
    if not code:
        return {}

    # 剥离 markdown 包裹，同时提取语言标记
    code = code.strip()
    lang = ""
    if code.startswith("```"):
        lines = code.split("\n")
        if lines[0].startswith("```"):
            lang = lines[0][3:].strip().lower()  # 提取语言标记
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = "\n".join(lines)

    # 后端 根据语言标记或内容特征决定扩展名
    first_line = code.split('\n')[0].strip() if code else ''
    code_lower = code[:200].lower()
    is_python_code = first_line.startswith(('def ', 'import ', 'from ', 'class ', '#', '"""', '#!/usr/bin/env python'))

    if lang in ("html", "htm") or "<!doctype html" in code_lower or "<html" in code_lower:
        ext = ".html"
    elif lang in ("js", "javascript") or "document.queryselector" in code_lower:
        ext = ".js"
    elif lang in ("css",):
        ext = ".css"
    elif lang in ("tsx", "jsx", "ts", "react"):
        ext = ".tsx" if lang == "tsx" else ".jsx" if lang == "jsx" else ".ts"
    elif lang in ("sh", "bash", "shell") or first_line.startswith(('#!/bin/bash', '#!/bin/sh', '#!/usr/bin/env bash')):
        ext = ".sh"
    elif lang in ("sql",) or any(code_lower.startswith(kw) for kw in ('create table', 'insert into', 'select ', 'alter table', 'drop ')):
        ext = ".sql"
    elif lang in ("md", "markdown") or first_line.startswith('#'):
        ext = ".md"
    elif lang in ("json",) or first_line.startswith(('{', '[')):
        ext = ".json"
    elif lang in ("yaml", "yml") or ':' in first_line and not is_python_code:
        ext = ".yml"
    elif lang in ("java",):
        ext = ".java"
    elif lang in ("go", "golang"):
        ext = ".go"
    elif lang in ("rs", "rust"):
        ext = ".rs"
    elif lang in ("cpp", "c++", "cxx"):
        ext = ".cpp"
    elif lang in ("c",):
        ext = ".c"
    elif is_python_code:
        ext = ".py"
    else:
        ext = ".py"  # 默认 Python

    output_dir = os.path.join(os.getcwd(), "completed_code")
    os.makedirs(output_dir, exist_ok=True)

    # 安全文件名
    safe_name = re.sub(r'[^\w]', '_', task)[:20].strip('_')
    if not safe_name:
        safe_name = "script"
    timestamp = datetime.now().strftime("%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"{safe_name}_{timestamp}{ext}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    abs_path = os.path.abspath(filename)
    print(f"[SaveCode] [OK] 已保存: {abs_path}")

    # 自动打开 — HTML 用浏览器，Python 用编辑器
    try:
        if os.name == "nt":
            os.startfile(abs_path)  # Windows 自动用默认程序打开（.html→浏览器，.py→编辑器）
        elif hasattr(os, 'uname') and os.uname().sysname == "Darwin":
            subprocess.run(["open", abs_path])
        else:
            subprocess.run(["xdg-open", abs_path])
    except Exception as e:
        print(f"[SaveCode] [WARN] 自动打开失败: {e}")

    open_type = "浏览器" if ext == ".html" else "编辑器"
    return {"context_output": f"[OK] 代码已生成并保存：\n`{abs_path}`\n\n系统已自动用{open_type}打开！"}


# ==================== [BUILD] 组装工作流图 ====================
workflow = StateGraph(AgentState)

workflow.add_node("chat_rag_node", chat_rag_node)
workflow.add_node("plan_node", plan_node)
workflow.add_node("research_node", research_node)
workflow.add_node("code_node", code_node)
workflow.add_node("execute_node", execute_node)
workflow.add_node("review_node", review_node)
workflow.add_node("save_code_node", save_code_node)

# 入口：Router 分发
workflow.set_conditional_entry_point(
    router_judge,
    {"chat_rag": "chat_rag_node", "planner": "plan_node"}
)

# 对话通道：回答完就结束
workflow.add_edge("chat_rag_node", END)

# 编码管线：规划 → 调研 → 编码 → 执行 → 审查
workflow.add_edge("plan_node", "research_node")
workflow.add_edge("research_node", "code_node")  # 去掉 need_code_decision，调研完直接编码
workflow.add_edge("code_node", "execute_node")
workflow.add_edge("execute_node", "review_node")

# 审查分支：通过 → 保存，失败 → 重试/结束
workflow.add_conditional_edges(
    "review_node",
    review_decision,
    {"save_code": "save_code_node", "code_node": "code_node", "__end__": END}
)

workflow.add_edge("save_code_node", END)
app_graph = workflow.compile()
