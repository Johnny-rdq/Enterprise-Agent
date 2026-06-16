"""
================================================================================
[LLM] Coder Agent — AI 程序员
================================================================================

职责：根据计划（plan）和管线上下文（context_output）编写代码。
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


# 编码节点 — 根据任务类型自动检测输出语言，支持全类型
def code_node(state: dict):
    task = state.get("task", "")
    plan = state.get("plan", "")
    context_output = state.get("context_output", "无附加资料")

    task_lower = task.lower()

    # 后端 语言类型检测（按优先级）
    _web_kw = ["html", "网页", "页面", "前端", "css", "javascript", "js"]
    _py_kw = ["python", "py", "爬虫", "后端", "api", "数据分析"]
    _game_kw = ["游戏", "贪吃蛇", "俄罗斯方块", "扫雷", "打砖块", "小游戏", "game", "snake", "tetris", "飞机大战", "flappy", "2048", "消消乐", "连连看"]
    _css_draw_kw = ["爱心", "心形", "形状", "画", "图形", "几何", "星星", "月亮", "花", "钻石"]
    _shell_kw = ["shell", "bash", "sh脚本", "命令行", "批处理", "bat脚本"]
    _md_kw = ["markdown", "md文档", "readme", "文档"]
    _sql_kw = ["sql", "数据库", "建表", "查询"]
    _json_kw = ["json", "yaml", "yml", "配置文件", "config"]

    is_html = any(kw in task_lower for kw in _web_kw)
    is_python = any(kw in task_lower for kw in _py_kw)
    is_game = any(kw in task_lower for kw in _game_kw)
    is_css_draw = any(kw in task_lower for kw in _css_draw_kw)
    is_shell = any(kw in task_lower for kw in _shell_kw)
    is_md = any(kw in task_lower for kw in _md_kw)
    is_sql = any(kw in task_lower for kw in _sql_kw)
    is_json = any(kw in task_lower for kw in _json_kw)

    # 后端 根据检测结果设置语言提示和格式规则
    if is_html and not is_python:
        _draw_hint = """
CSS 绘图技巧：
- 爱心标准做法：一个旋转45度的正方形 + 两个伪元素(::before, ::after)做圆形，用绝对定位放在正方形上方两侧
- 关键代码：.heart { width:200px; height:200px; background:red; transform:rotate(45deg); position:relative; margin:100px auto; }
  .heart::before, .heart::after { content:''; width:200px; height:200px; border-radius:50%; background:red; position:absolute; }
  .heart::before { left:-100px; } .heart::after { top:-100px; }
- 元素尺寸要大（200px以上），颜色要鲜艳，背景用深色渐变突出主体
- 可加 @keyframes 缩放动画让爱心"跳动"
""" if is_css_draw else ""
        lang_hint = f"""直接输出完整的 HTML/CSS/JS 源码。
视觉要求：
- 页面美观、现代风格，使用渐变背景或好看的配色
- 主体元素要大、居中、醒目
- 不要有大段文字说明，纯视觉呈现
- 可以加动画效果让页面更生动
{_draw_hint}"""
        format_rule = '只输出纯代码，严禁任何解释说明文字。以 <!DOCTYPE html> 或 <html> 开头。严禁用 ``` 包裹。'
        lang_name = "HTML/CSS/JS"
    elif is_shell:
        lang_hint = "输出完整的 Shell 脚本。"
        format_rule = "只输出纯代码，不要解释。以 #!/bin/bash 或 #!/bin/sh 开头。严禁用 ``` 包裹。"
        lang_name = "Shell"
    elif is_md:
        lang_hint = "输出完整的 Markdown 文档。"
        format_rule = "只输出纯文档内容，不要解释。以 # 标题 开头。严禁用 ``` 包裹。"
        lang_name = "Markdown"
    elif is_sql:
        lang_hint = "输出完整的 SQL 语句。"
        format_rule = "只输出纯 SQL，不要解释。以 CREATE/INSERT/SELECT/ALTER 等关键字开头。严禁用 ``` 包裹。"
        lang_name = "SQL"
    elif is_json:
        lang_hint = "输出完整的 JSON/YAML 配置文件。"
        format_rule = "只输出纯配置内容，不要解释。以 { 或 [ 开头（JSON），或以字段名开头（YAML）。严禁用 ``` 包裹。"
        lang_name = "JSON/YAML"
    else:
        # Python / 游戏 / 通用脚本
        lang_hint = "输出完整的、可直接运行的 Python 代码。"
        if is_game:
            lang_hint += """\n游戏开发规则：
- 可以使用 pygame 或 turtle，优先 pygame（已安装可用）
- 游戏窗口 600x600 起，背景深色
- 完整的游戏循环、得分显示、游戏结束判断
- 注意资源清理和异常处理
- 用 pip install 安装缺失的包时，系统会自动补装"""
        format_rule = "只输出纯代码，不要解释，严禁用 ```python 或 ``` 包裹。"
        lang_name = "Python"

    print(f"\n[Coder] 正在编写代码... (语言: {lang_name})")

    prompt = f"""你是一个顶级程序员。

用户需求：{task}
架构师计划：{plan}
上下文资料：{context_output}

{lang_hint}

要求：
1. {format_rule}
2. 代码完整、能直接运行。
3. 最终回复严禁先说话再给代码，第一个字符必须是代码本身的第一个字符。
"""

    response = llm.invoke(prompt)
    return {"code": response.content}
