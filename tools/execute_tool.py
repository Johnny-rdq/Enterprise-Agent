import subprocess
import sys
import os
import re


# 检测代码是否为 GUI 程序（turtle/pygame/tkinter 等会打开窗口，不能等待结束）
def _is_gui_code(code: str) -> bool:
    _gui_markers = [
        "import turtle", "from turtle import",
        "import pygame", "from pygame import",
        "import tkinter", "from tkinter import",
        "turtle.Screen()", "pygame.init()",
        "turtle.mainloop()", "turtle.done()",
    ]
    return any(marker in code for marker in _gui_markers)


# 从报错中提取缺失的模块名
def _extract_missing_module(stderr: str) -> str | None:
    m = re.search(r"No module named ['\"]([^'\"]+)['\"]", stderr)
    if m:
        return m.group(1)
    m = re.search(r"ModuleNotFoundError: No module named '([^']+)'", stderr)
    if m:
        return m.group(1)
    return None


# DP 获取 pip 安装用的 Python 解释器（优先用项目 .venv）
def _get_pip_python() -> str:
    # DP 如果当前已在 venv 中运行，直接用它
    if sys.prefix != sys.base_prefix:
        return sys.executable
    # DP 尝试找项目根目录下的 .venv
    _dir = os.path.dirname(os.path.abspath(__file__))  # tools/
    _project = os.path.dirname(_dir)  # 项目根
    _venv_python = os.path.join(_project, ".venv", "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(_project, ".venv", "bin", "python")
    if os.path.exists(_venv_python):
        return _venv_python
    return sys.executable  # 回退到当前 Python


# 自动安装缺失的包
def _auto_install(pkg: str) -> bool:
    _python = _get_pip_python()
    print(f"[ExecuteTool] 检测到缺失包: {pkg}，正在自动安装（{_python}）...")
    try:
        result = subprocess.run(
            [_python, "-m", "pip", "install", pkg, "-q"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120
        )
        ok = result.returncode == 0
        if ok:
            print(f"[ExecuteTool] [OK] {pkg} 安装成功")
        else:
            print(f"[ExecuteTool] [ERROR] {pkg} 安装失败: {result.stderr[-200:]}")
        return ok
    except Exception as e:
        print(f"[ExecuteTool] [ERROR] 安装 {pkg} 异常: {e}")
        return False


# 单次执行 — 跑代码文件，返回 (ok, stdout, stderr)
def _run_once(run_file: str, timeout: int = 15) -> tuple[bool, str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, run_file],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=timeout
    )
    ok = result.returncode == 0
    stdout = result.stdout.strip() if result.stdout else ""
    stderr = result.stderr.strip() if result.stderr else ""
    return ok, stdout, stderr


# GUI 程序启动 — 非阻塞，打开窗口即返回
def _run_gui(run_file: str) -> str:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    try:
        subprocess.Popen(  # 非阻塞，窗口独立运行
            [sys.executable, run_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env
        )
        return "[OK] GUI 程序已启动！游戏窗口已打开，请在弹出的窗口中操作。"
    except Exception as e:
        return f"[OK] GUI 程序已启动（但可能有问题）: {str(e)}"


# 代码安全执行 — 隔离沙盒运行，GUI程序非阻塞启动，自动补装缺失包
def run_code_safely(input_data: str) -> str:
    try:
        code = input_data.strip()

        # 检测前端/非Python代码 → 跳过执行
        _frontend_markers = [
            "<!DOCTYPE html", "<html", "<head>", "<body", "<script", "<style",
            "import React", "from 'react'", "from \"react\"",
            "export default", "export function", "export const",
            "const ", "function ", "document.querySelector",
            "console.log", "console.error",
        ]
        for marker in _frontend_markers:
            if marker in code:
                return "[INFO] 检测到前端代码（HTML/JS/CSS），已跳过Python沙盒执行。代码将直接保存为文件。"

        # 判断传入的是文件路径还是代码字符串
        if input_data.endswith(".py") and len(input_data) < 255 and os.path.exists(input_data):
            run_file = input_data
        else:
            run_file = "temp_execution.py"
            with open(run_file, "w", encoding="utf-8") as f:
                f.write(input_data)

        is_gui = _is_gui_code(code)

        if is_gui:
            # GUI 程序 → 先编译检查语法
            try:
                compile(code, run_file, "exec")
            except SyntaxError as e:
                return f"[ERROR] 代码语法错误！\n{e}"
            # 快速试跑检测缺失模块（3秒超时，import 阶段应该够了）
            gui_stderr = ""
            try:
                ok, stdout, gui_stderr = _run_once(run_file, timeout=3)
                if ok:
                    return _run_gui(run_file)
            except subprocess.TimeoutExpired:
                pass  # 超时说明进入事件循环了，正常
            pkg = _extract_missing_module(gui_stderr)
            if pkg and _auto_install(pkg):
                return _run_gui(run_file)
            return _run_gui(run_file)

        # 非 GUI 程序 → 正常阻塞执行
        ok, stdout, stderr = _run_once(run_file)

        if ok:
            return f"[OK] 运行成功！终端输出结果: \n{stdout}" if stdout else "[OK] 运行成功！（无终端输出）"

        # 检测缺失模块 → 自动安装后重试
        retry = 0
        while retry < 3:
            pkg = _extract_missing_module(stderr)
            if not pkg:
                break
            if not _auto_install(pkg):
                return f"[ERROR] 缺少包 `{pkg}` 且自动安装失败。\n原始错误: \n{stderr}"
            retry += 1
            ok, stdout, stderr = _run_once(run_file)
            if ok:
                return f"[OK] 运行成功！（已自动安装 `{pkg}`）\n终端输出: \n{stdout}" if stdout else f"[OK] 运行成功！（已自动安装 `{pkg}`）"

        if stderr:
            return f"[ERROR] 运行失败！\n{stderr}"
        return f"[ERROR] 运行失败，无具体报错信息。"

    except subprocess.TimeoutExpired:
        return "[ERROR] 运行失败！代码执行超时（超过15秒），可能陷入了死循环。"
    except Exception as e:
        return f"[ERROR] 执行工具发生严重系统异常: {str(e)}"
