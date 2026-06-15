"""
================================================================================
🧠 AI 智能体协作平台 — FastAPI 服务端
================================================================================
"""

import sys
import io
import json
import asyncio
import sqlite3
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, OSError):
        pass

from graph.workflow import app_graph

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "history_messages.sqlite3")

with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ui_chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_TOKEN = os.getenv("AUTH_TOKEN", "demo_token")

class AgentRequest(BaseModel):
    task: str = "Write a simple Python script."
    token: str = ""
    thread_id: str = "default_thread"


@app.get("/")
async def serve_frontend():
    dist_index = "frontend/dist/index.html"
    if os.path.exists(dist_index):
        return FileResponse(dist_index)
    vite_index = "frontend/index.html"
    if os.path.exists(vite_index):
        return FileResponse(vite_index)
    return {"message": "前端文件未找到，请运行 cd frontend && npm run dev"}


# Agent 运行核心 — SSE 流式推送，消息分 type=intent/thinking/token/result
@app.post("/agentrun")
async def run_agent(req: AgentRequest):
    if req.token != AUTH_TOKEN:
        raise HTTPException(401, detail="Invalid token.")

    # 用户消息落库
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        conn.execute(
            "INSERT INTO ui_chat_history (thread_id, role, content) VALUES (?, ?, ?)",
            (req.thread_id, "user", req.task)
        )

    async def event_stream(current_task: str, current_thread_id: str):
        inputs = {"task": current_task}
        config = {
            "recursion_limit": 25,
            "configurable": {"thread_id": current_thread_id}
        }

        final_answer = ""       # 内部累积（调试用）
        display_content = ""    # 存入数据库给用户看的干净内容
        intent_shown = False
        current_node_blocked = False  # 中间节点屏蔽 token 流
        is_chat_rag = False     # 标记是否走对话通道

        try:
            async for event in app_graph.astream_events(inputs, config=config, version="v2"):
                kind = event["event"]
                node_name = event.get("metadata", {}).get("langgraph_node", "")

                # 跟踪节点切换
                if kind == "on_chain_start" and node_name and event.get("name") == node_name:
                    current_node_blocked = node_name in (
                        "plan_node", "research_node", "code_node", "review_node"
                    )
                    if node_name == "chat_rag_node":
                        is_chat_rag = True

                # A. 流式 token — 对话通道才推送 + 存 display，中间节点屏蔽
                if kind == "on_chat_model_stream":
                    chunk_obj = event["data"].get("chunk")
                    if not chunk_obj:
                        continue
                    ct = chunk_obj.content if hasattr(chunk_obj, "content") else str(chunk_obj)
                    if not ct:
                        continue
                    if current_node_blocked:
                        final_answer += ct  # 中间节点内部累积不推送
                        continue
                    final_answer += ct
                    display_content += ct  # 对话 token 是用户可见内容
                    yield f"data: {json.dumps({'type': 'token', 'content': ct}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.002)

                # B. 节点启动 — 推简短状态提示（不存库）
                elif kind == "on_chain_start" and node_name and event.get("name") == node_name:
                    node_tips = {
                        "plan_node": "正在分析需求，制定计划...",
                        "research_node": "正在搜索相关资料...",
                        "code_node": "正在编写代码...",
                        "execute_node": "正在运行代码...",
                        "review_node": "正在检查结果...",
                        "save_code_node": "正在保存代码...",
                        "chat_rag_node": "正在处理...",
                    }
                    tip = node_tips.get(node_name)
                    if tip:
                        if node_name == "plan_node":
                            if not intent_shown:
                                full_tip = "已进入多Agent编码管线（规划 -> 调研 -> 编码 -> 审查）"
                                intent_shown = True
                                yield f"data: {json.dumps({'type': 'intent', 'content': full_tip}, ensure_ascii=False)}\n\n"
                        else:
                            yield f"data: {json.dumps({'type': 'thinking', 'content': tip}, ensure_ascii=False)}\n\n"

                # C. 节点结束 — 推送最终结果，同时存入 display_content
                elif kind == "on_chain_end" and node_name and event.get("name") == node_name:
                    output = event["data"].get("output")
                    if not isinstance(output, dict) or node_name == "chat_rag_node":
                        continue
                    if node_name in ("plan_node", "research_node", "code_node", "review_node"):
                        continue

                    field_map = {
                        "execute_node": ("execution_result", "result"),
                        "save_code_node": ("context_output", "result"),
                    }
                    if node_name in field_map:
                        field, msg_type = field_map[node_name]
                        captured = output.get(field, "")
                        if captured:
                            final_answer += f"\n{captured}\n"
                            display_content += captured + "\n"  # 结果内容存入干净版本
                            yield f"data: {json.dumps({'type': msg_type, 'content': captured}, ensure_ascii=False)}\n\n"

        except Exception as e:
            err_msg = f"❌ 执行中断: {str(e)}"
            display_content += err_msg
            yield f"data: {json.dumps({'type': 'result', 'content': err_msg}, ensure_ascii=False)}\n\n"

        # 回复落库 — 只存干净的用户可见内容
        content_to_save = display_content.strip() or final_answer.strip()
        if content_to_save:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                conn.execute(
                    "INSERT INTO ui_chat_history (thread_id, role, content) VALUES (?, ?, ?)",
                    (current_thread_id, "assistant", content_to_save)
                )

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(req.task, req.thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# 聊天历史查询 — 按 thread_id 拉取某个会话的全部消息
@app.get("/get_chat_history")
async def get_chat_history(thread_id: str):
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        cursor = conn.execute(
            "SELECT role, content FROM ui_chat_history WHERE thread_id = ? ORDER BY id ASC",
            (thread_id,)
        )
        rows = cursor.fetchall()
    return {"history": [{"role": r, "content": c} for r, c in rows]}


DIST_ASSETS = "frontend/dist/assets"
if os.path.exists(DIST_ASSETS):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
