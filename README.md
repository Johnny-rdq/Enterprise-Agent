# AI 智能体协作平台

基于 **LangGraph + FastAPI** 的多智能体协作系统，四位 AI Agent 接力完成从需求分析到代码生成的全流程任务。前端采用 React + Tailwind CSS，支持 SSE 流式对话、多会话管理、Markdown 渲染。

## 核心特性

- **智能路由** — 关键词 + LLM 双层判断，编码/开发任务进入多 Agent 管线，闲聊/问答走快速对话通道
- **四 Agent 协作管线** — 规划者 → 研究员 → 编码者 → 审核者，接力完成复杂编码任务
- **全类型代码生成** — 自动识别目标语言，支持 Python / HTML+CSS+JS / Shell / Markdown / SQL / JSON / YAML / Java / Go / Rust / C++ / C
- **pygame 游戏开发** — 游戏类任务优先使用 pygame，自动补装缺失包，GUI 程序无阻塞启动
- **安全沙箱执行** — Python 代码隔离运行，缺失包自动安装到项目 venv，非 Python 代码跳过执行直接保存
- **自动保存 & 打开** — 按语言自动选扩展名，落盘到 `completed_code/` 后自动用默认程序打开
- **重试机制** — 审核不通过自动打回编码者修改，最多重试 2 次
- **SSE 流式传输** — 实时推送节点状态（规划/搜索/编码/执行/审查）和 LLM 生成的 token
- **多会话管理** — 基于 thread_id 的会话隔离，聊天历史持久化到 SQLite
- **禁用缓存** — 全局 Cache-Control 头，确保每次拿到最新页面
- **Docker 部署** — 一键构建镜像，开箱即用

## 架构说明

```
用户请求
    │
    ▼
┌─────────────┐    闲聊/问答   ┌──────────────┐
│  路由判断    │──────────────▶│  对话通道      │────── 结束
│  (Router)   │               │ (chat_rag)    │
└─────────────┘               └──────────────┘
    │ 编码任务
    ▼
┌─────────────┐     ┌────────────────┐     ┌─────────────┐
│  规划者      │────▶│  研究员        │────▶│  编码者      │
│  (Planner)  │     │  (Researcher)  │     │  (Coder)    │
└─────────────┘     └────────────────┘     └─────────────┘
                                                   │
                                                   ▼
                                            ┌─────────────┐
                                            │  执行器      │
                                            │  (沙箱)     │
                                            └─────────────┘
                                                   │
                                                   ▼
                   ┌─────────────┐     ┌─────────────┐
                   │   保存代码    │◀────│  审核者      │
                   │ (SaveCode)  │ 通过 │ (Reviewer)  │
                   └─────────────┘     └─────────────┘
                          ▲                    │
                          │    不通过（重试）    │
                          └────────────────────┘
```

## Agent 角色说明

| Agent | 角色 | 职责 |
|-------|------|------|
| **Router（路由器）** | 流量分发 | LLM 判断任务类型，编码任务入管线，闲聊走对话通道 |
| **Planner（规划者）** | 项目经理 | 分析任务需求，拆解为 3-5 步执行计划 |
| **Researcher（研究员）** | 情报整理 | 将计划精简为编码者可直接使用的技术要点 |
| **Coder（编码者）** | 软件工程师 | 自动识别目标语言，生成完整可运行代码，支持全类型输出 |
| **Executor（执行器）** | 沙箱 | 隔离执行 Python 代码，自动补装缺失包到 venv，GUI 非阻塞启动 |
| **Reviewer（审核者）** | QA 工程师 | 检查执行结果，PASS 则保存，失败则分析根因打回重试 |
| **SaveCode（保存器）** | 归档 | 自动识别语言选扩展名，落盘到 `completed_code/` 并打开 |

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端框架** | FastAPI + Uvicorn |
| **工作流引擎** | LangGraph（StateGraph） |
| **LLM 调用** | LangChain + OpenAI 兼容接口 |
| **前端框架** | React 18 + Vite 6 |
| **样式** | Tailwind CSS（暗色主题） |
| **Markdown** | marked + DOMPurify |
| **数据持久化** | SQLite（聊天历史） |
| **流式传输** | SSE（Server-Sent Events） |
| **代码执行** | subprocess 沙箱 + 自动补包到 venv + GUI 非阻塞 |
| **容器化** | Docker |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+（仅前端开发时需要）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Johnny-rdq/Enterprise-Agent.git
cd Enterprise-Agent

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装游戏开发包（可选）
pip install pygame

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API_KEY 和 BASE_URL

# 6. 构建前端（可选，前端已预构建在 frontend/dist/）
cd frontend && npm install && npm run build && cd ..

# 7. 启动服务
python server_app.py
```

在浏览器中打开 **http://localhost:7860** 即可使用。

## Docker 部署

```bash
# 构建镜像
docker build -t enterprise-agent .

# 运行容器
docker run -p 7860:7860 --env-file .env enterprise-agent
```

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `API_KEY` | LLM API 密钥 | — |
| `BASE_URL` | API 接口地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `MODEL_NAME` | 大模型名称 | `qwen-max` |
| `AUTH_TOKEN` | 前端访问令牌 | `demo_token` |

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 前端页面 |
| `POST` | `/agentrun` | 提交任务，SSE 流式返回结果 |
| `GET` | `/get_chat_history` | 按 thread_id 查询历史消息 |

### POST /agentrun 请求体

```json
{
  "task": "用 Python 写一个冒泡排序",
  "token": "demo_token",
  "thread_id": "session_001"
}
```

### SSE 事件类型

| type | 说明 |
|------|------|
| `intent` | 路线提示（进入编码管线） |
| `thinking` | 当前节点状态（分析需求/搜索资料/编写代码/运行代码/检查结果） |
| `token` | LLM 流式生成的文本 |
| `result` | 执行输出或保存确认 |

## 项目结构

```
├── agents/                  # AI Agent 模块
│   ├── planner_agent.py     #   规划者 — 拆解任务计划
│   ├── researcher_agent.py  #   研究员 — 精简上下文
│   ├── coder_agent.py       #   编码者 — 全类型代码生成
│   └── reviewer_agent.py    #   审核者 — 审查执行结果
├── graph/                   # LangGraph 工作流编排
│   └── workflow.py          #   状态图 + Router + 对话/执行/保存节点
├── tools/                   # 工具集
│   └── execute_tool.py      #   安全沙箱 + 自动补包到 venv + GUI 支持
├── core/                    # 配置模块
│   └── config.py            #   环境变量读取
├── frontend/                # React 前端
│   ├── src/
│   │   ├── App.jsx          #   根组件 — SSE 流式接收
│   │   ├── components/
│   │   │   ├── ChatArea.jsx     # 聊天主区域
│   │   │   ├── ChatMessage.jsx  # 消息气泡（Markdown 渲染）
│   │   │   ├── MessageInput.jsx # 输入框 + 停止按钮
│   │   │   └── Sidebar.jsx      # 侧边栏 — 会话列表
│   │   ├── hooks/
│   │   │   └── useSessions.js   # 会话状态管理
│   │   ├── index.css        #   Tailwind + 全局样式
│   │   └── main.jsx         #   入口
│   └── dist/                #   预构建产物
├── data/                    # 运行时数据（SQLite）
├── completed_code/          # AI 生成的代码存档
├── server_app.py            # FastAPI 应用入口 + SSE 端点
├── temp_execution.py        # 临时执行脚本
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 支持的语言类型

| 类型 | 触发关键词 | 输出格式 | 执行方式 |
|------|-----------|---------|---------|
| HTML/CSS/JS | html、网页、前端、css、js | .html / .js / .css | 浏览器打开 |
| Python | python、py、脚本、api、数据分析 | .py | 沙箱执行 |
| 游戏（pygame） | 游戏、贪吃蛇、飞机大战、打砖块… | .py | GUI 非阻塞启动 |
| Shell | shell、bash、命令行、批处理 | .sh | 仅保存 |
| Markdown | markdown、readme、文档 | .md | 仅保存 |
| SQL | sql、数据库、建表、查询 | .sql | 仅保存 |
| JSON/YAML | json、yaml、配置、config | .json / .yml | 仅保存 |
| Java / Go / Rust / C++ | 通过代码特征自动识别 | .java / .go 等 | 仅保存 |
| CSS 绘图 | 爱心、心形、星星、图形… | .html | 浏览器打开 |

## 开源协议

MIT
