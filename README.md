# AI 智能体协作平台

基于 **LangGraph + FastAPI** 的多智能体协作系统，四位 AI Agent 接力完成从规划到编码的全流程任务。

## 架构说明

```
用户请求
    │
    ▼
┌─────────────┐    简单问题   ┌──────────────┐
│  路由判断    │──────────────│  聊天对话      │────── 结束
│  (Router)   │              └──────────────┘
└─────────────┘
    │ 编码任务
    ▼
┌─────────────┐     ┌────────────────┐     ┌─────────────┐
│  规划者      │────▶│  研究员        │────▶│  编码者      │
│  (PM)       │     │  (Analyst)     │     │  (Engineer) │
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
                    └─────────────┘ 通过 └─────────────┘
                           ▲                    │
                           │    不通过（重试）    │
                           └────────────────────┘
```

## Agent 角色说明

| Agent | 角色 | 职责 |
|-------|------|------|
| **Planner（规划者）** | 项目经理 | 分析任务，制定分步执行计划 |
| **Researcher（研究员）** | 情报整理员 | 将计划精简为 Coder 可直接使用的要点 |
| **Coder（编码者）** | 软件工程师 | 生成可运行的 Python 或前端代码 |
| **Reviewer（审核者）** | QA 工程师 | 验证执行结果，批准通过或打回修改 |

## 技术栈

- **后端**：FastAPI + LangGraph + LangChain
- **大模型**：Qwen 系列（通过 DashScope 的 OpenAI 兼容 API）
- **工具集**：Python 沙箱执行（GUI 程序非阻塞启动，缺失包自动安装）
- **前端**：React + Vite + Tailwind CSS + Markdown 渲染 + SSE 流式传输

## 快速开始

### 环境要求

- Python 3.11+
- [DashScope API Key](https://dashscope.console.aliyun.com/)

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

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API_KEY 和 BASE_URL

# 5. 构建前端（可选，前端已预构建在 frontend/dist/）
cd frontend && npm install && npm run build && cd ..

# 6. 启动服务
python server_app.py
```

在浏览器中打开 **http://localhost:7860** 即可使用。

## Docker 部署

```bash
docker build -t enterprise-agent .
docker run -p 7860:7860 --env-file .env enterprise-agent
```

## 项目结构

```
├── agents/              # 四个 AI Agent（规划者、研究员、编码者、审核者）
│   ├── planner_agent.py
│   ├── researcher_agent.py
│   ├── coder_agent.py
│   └── reviewer_agent.py
├── graph/               # LangGraph 工作流编排
│   └── workflow.py
├── tools/               # 工具集
│   └── execute_tool.py  # 代码安全执行（沙箱 + 自动补包 + GUI 支持）
├── core/                # 配置模块
│   └── config.py
├── frontend/            # React 前端界面
│   └── src/
├── server_app.py        # FastAPI 应用入口
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `API_KEY` | DashScope API 密钥 | — |
| `BASE_URL` | API 接口地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `MODEL_NAME` | 大模型名称 | `qwen-turbo` |
| `AUTH_TOKEN` | 前端认证令牌 | `demo_token` |

## 开源协议

MIT
