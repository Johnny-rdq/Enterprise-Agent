import os

def generate_love_html():
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ 跳动的爱心网页 ✨</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #ff9a9e, #fad0c4, #a1c4fd, #c2e9fb);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            font-family: 'Segoe UI', system-ui, sans-serif;
            color: #fff;
            text-align: center;
        }

        .header {
            margin-bottom: 2rem;
            text-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }

        h1 {
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(to right, #ff416c, #ff4b2b);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            letter-spacing: 2px;
        }

        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            line-height: 1.6;
        }

        /* 爱心核心动画容器 */
        .hearts-container {
            position: relative;
            width: 100%;
            height: 40vh;
            margin: 2rem 0;
        }

        .heart {
            position: absolute;
            font-size: 2rem;
            animation: float 4s ease-in-out infinite;
            text-shadow: 0 0 12px rgba(255, 255, 255, 0.7);
            user-select: none;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0) scale(1); opacity: 0.9; }
            50% { transform: translateY(-20px) scale(1.15); opacity: 1; }
        }

        /* 底部交互提示 */
        .footer {
            margin-top: 2rem;
            padding: 1rem 2rem;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 30px;
            backdrop-filter: blur(8px);
            font-size: 0.95rem;
            opacity: 0.85;
        }

        /* 响应式适配 */
        @media (max-width: 768px) {
            h1 { font-size: 2.2rem; }
            .subtitle { font-size: 1rem; }
            .heart { font-size: 1.5rem; }
        }

        @media (max-width: 480px) {
            h1 { font-size: 1.8rem; }
            .subtitle { font-size: 0.9rem; }
            .heart { font-size: 1.2rem; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>❤️ 爱在指尖跳动 ❤️</h1>
        <p class="subtitle">纯 HTML + CSS 实现｜无需 JavaScript｜轻量·优雅·可直接运行</p>
    </div>

    <div class="hearts-container" id="heartsContainer"></div>

    <div class="footer">
        ✦ 可用任意 HTML 编辑器打开（VS Code / HBuilder / Notepad++ 等）<br>
        ✦ 修改颜色/动画/文字？只需编辑 CSS 或 HTML 即可！
    </div>

    <script>
        // 动态生成 12 颗飘浮爱心（纯前端，无外部依赖）
        const container = document.getElementById('heartsContainer');
        const hearts = ['❤️', '💕', '💖', '💗', '💓', '💞', '💝', '💘', '💌', '💋', '🌹', '✨'];
        
        for (let i = 0; i < 12; i++) {
            const heart = document.createElement('div');
            heart.className = 'heart';
            heart.innerHTML = hearts[i % hearts.length];
            heart.style.left = `${Math.random() * 100}%`;
            heart.style.animationDelay = `${Math.random() * 4}s`;
            heart.style.animationDuration = `${3 + Math.random() * 3}s`;
            container.appendChild(heart);
        }
    </script>
</body>
</html>'''
    return html_content

def main():
    filename = "love_heart.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(generate_love_html())
    print(f"✅ 已生成：{os.path.abspath(filename)}")

if __name__ == "__main__":
    main()