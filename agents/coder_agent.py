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


# 编码节点 — 根据任务类型自动选择输出语言（HTML/CSS/JS 或 Python）
def code_node(state: dict):
    task = state.get("task", "")
    plan = state.get("plan", "")
    context_output = state.get("context_output", "无附加资料")

    # 根据任务内容判断目标语言
    task_lower = task.lower()
    is_html = any(kw in task_lower for kw in ["html", "网页", "页面", "前端", "css", "javascript", "js"])
    is_python = any(kw in task_lower for kw in ["python", "py", "爬虫", "脚本", "后端", "api", "数据分析"])
    is_game = any(kw in task_lower for kw in ["游戏", "贪吃蛇", "俄罗斯方块", "扫雷", "打砖块", "小游戏", "game", "snake", "tetris"])

    if is_html and not is_python:
        # 检测是否需要 CSS 绘图（爱心、形状等）
        is_drawing = any(kw in task_lower for kw in ["爱心", "心形", "形状", "画", "图形", "几何", "星星", "月亮", "花", "钻石"])
        if is_drawing:
            drawing_hint = """
CSS 绘图技巧：
- 爱心标准做法：一个旋转45度的正方形 + 两个伪元素(::before, ::after)做圆形，用绝对定位放在正方形上方两侧
- 关键代码：.heart { width:200px; height:200px; background:red; transform:rotate(45deg); position:relative; margin:100px auto; }
  .heart::before, .heart::after { content:''; width:200px; height:200px; border-radius:50%; background:red; position:absolute; }
  .heart::before { left:-100px; } .heart::after { top:-100px; }
- 元素尺寸要大（200px以上），颜色要鲜艳，背景用深色渐变突出主体
- 可加 @keyframes 缩放动画让爱心"跳动"
"""
        else:
            drawing_hint = ""
        # HTML/前端项目：直接输出 HTML 源码
        lang_hint = f"""直接输出完整的 HTML/CSS/JS 源码，不要包在 Python 函数或字符串里。
视觉要求：
- 页面美观、现代风格，使用渐变背景或好看的配色
- 主体元素要大、居中、醒目
- 不要有大段文字说明，纯视觉呈现
- 可以加动画效果让页面更生动
{drawing_hint}"""
        format_rule = '只输出纯代码，严禁任何解释说明文字。以 <!DOCTYPE html> 或 <html> 开头。严禁用 ``` 包裹。'
    else:
        # Python 项目
        lang_hint = "输出完整的、可直接运行的 Python 代码。"
        if is_game:
            lang_hint += """\n游戏开发规则（重要！）：
- 必须使用 turtle 模块（Python 内置，无需安装任何包）
- 游戏窗口 600x600，背景黑色
- 使用 turtle.onkey() 绑定方向键控制
- 完整的游戏循环、得分显示、游戏结束判断
- turtle 贪吃蛇示例结构：
  1. 用 turtle.Turtle() 创建蛇头和食物
  2. 蛇身用列表存储坐标，每次移动更新
  3. screen.listen() + screen.onkey() 绑定 WASD/方向键
  4. 用 screen.ontimer() 做游戏循环（不要用 while True）
  5. 吃到食物加分，撞墙/撞自己结束
- 严禁 import pygame（pygame 无法安装），只用 turtle"""
        format_rule = "只输出纯代码，不要解释，严禁用 ```python 或 ``` 包裹。"

    print(f"\n[Coder] 正在编写代码... (语言: {'前端' if is_html and not is_python else 'Python'})")

    prompt = f"""你是一个顶级程序员。

用户需求：{task}
架构师计划：{plan}
上下文资料：{context_output}

{lang_hint}

要求：
1. {format_rule}
2. 代码完整、能直接运行。
3. 最终回复里，你的第一个字符必须是 '<'（HTML）或 '#'/'i'/'f'/'d'（Python），严禁先说话再给代码。
"""

    response = llm.invoke(prompt)  # 同步调用 LLM
    return {"code": response.content}
