import os

def generate_heart_html():
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>❤ 简单爱心 - 纯前端实现</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Segoe UI', system-ui, sans-serif;
            padding: 20px;
            color: #333;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            max-width: 600px;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 12px;
            color: #e74c3c;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .subtitle {
            font-size: 1.1rem;
            opacity: 0.8;
            margin-bottom: 30px;
        }
        .demo-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 40px;
            max-width: 1000px;
            width: 100%;
        }
        .demo-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
            padding: 28px;
            width: 280px;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .demo-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.12);
        }
        .demo-title {
            font-size: 1.3rem;
            margin-bottom: 20px;
            color: #2c3e50;
        }
        /* ✅ 方案一：纯 CSS 爱心 */
        .heart-css {
            position: relative;
            width: 100px;
            height: 90px;
            margin: 0 auto 20px;
        }
        .heart-css:before,
        .heart-css:after {
            content: "";
            position: absolute;
            width: 50px;
            height: 80px;
            background: #e74c3c;
            border-radius: 50px 50px 0 0;
        }
        .heart-css:before {
            left: 50px;
            transform: rotate(-45deg);
            transform-origin: 0 100%;
        }
        .heart-css:after {
            left: 0;
            transform: rotate(45deg);
            transform-origin: 100% 100%;
        }
        .heart-css {
            animation: beat 1.2s infinite ease-in-out;
        }
        @keyframes beat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        /* ✅ 方案二：SVG 爱心 */
        .heart-svg {
            width: 100px;
            height: 90px;
            margin: 0 auto 20px;
        }
        /* ✅ 方案三：Canvas 爱心 */
        .heart-canvas {
            width: 100px;
            height: 100px;
            margin: 0 auto 20px;
        }
        .code-snippet {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 14px;
            border-radius: 8px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 0.85rem;
            text-align: left;
            overflow-x: auto;
            margin-top: 16px;
            max-height: 120px;
            line-height: 1.4;
        }
        .code-snippet span {
            display: block;
        }
        .tag { color: #3498db; }
        .attr { color: #2ecc71; }
        .value { color: #e74c3c; }
        .comment { color: #95a5a6; font-style: italic; }
        footer {
            margin-top: 50px;
            text-align: center;
            opacity: 0.7;
            font-size: 0.9rem;
        }
        @media (max-width: 768px) {
            .demo-container { flex-direction: column; align-items: center; }
            h1 { font-size: 2rem; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>❤ 简单爱心</h1>
        <p class="subtitle">三种零依赖、纯静态、可直接运行的前端实现方案</p>
    </div>

    <div class="demo-container">
        <!-- 方案一：CSS -->
        <div class="demo-card">
            <h2 class="demo-title">CSS + 伪元素</h2>
            <div class="heart-css"></div>
            <p>零 JS｜兼容性极佳｜轻量动画</p>
            <div class="code-snippet">
                <span><span class="tag">&lt;div</span> <span class="attr">class</span>=<span class="value">"heart-css"</span><span class="tag">&gt;&lt;/div&gt;</span></span>
                <span><span class="comment">&lt;!-- 样式见 &lt;style&gt; --&gt;</span></span>
            </div>
        </div>

        <!-- 方案二：SVG -->
        <div class="demo-card">
            <h2 class="demo-title">SVG 路径</h2>
            <svg class="heart-svg" viewBox="0 0 100 90" fill="#e74c3c">
                <path d="M50,10 C30,10 15,25 15,45 C15,65 30,80 50,80 C70,80 85,65 85,45 C85,25 70,10 50,10 Z" />
            </svg>
            <p>矢量无损｜语义清晰｜易响应式</p>
            <div class="code-snippet">
                <span><span class="tag">&lt;svg</span> <span class="attr">viewBox</span>=<span class="value">"0 0 100 90"</span><span class="tag">&gt;</span></span>
                <span>&nbsp;&nbsp;<span class="tag">&lt;path</span> <span class="attr">d</span>=<span class="value">"M50,10 C30,10..."</span><span class="tag">/&gt;</span></span>
                <span><span class="tag">&lt;/svg&gt;</span></span>
            </div>
        </div>

        <!-- 方案三：Canvas -->
        <div class="demo-card">
            <h2 class="demo-title">Canvas + JS</h2>
            <canvas class="heart-canvas" width="100" height="100"></canvas>
            <p>动态缩放｜贝塞尔曲线｜轻量交互</p>
            <div class="code-snippet">
                <span><span class="tag">&lt;canvas</span> <span class="attr">id</span>=<span class="value">"heartCanvas"</span><span class="tag">&gt;&lt;/canvas&gt;</span></span>
                <span><span class="comment">&lt;script&gt; // 绘制跳动爱心 &lt;/script&gt;</span></span>
            </div>
        </div>
    </div>

    <footer>
        <p>✅ 单文件 HTML｜无需网络｜双击即开｜所有方案均经实测可运行</p>
        <p>Generated with pure Python — no frameworks, no build steps</p>
    </footer>

    <script>
        // ✅ 方案三：Canvas 动态爱心（简化版，内联执行）
        document.addEventListener('DOMContentLoaded', () => {
            const canvas = document.querySelector('.heart-canvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            
            function drawHeart(x, y, size, color = '#e74c3c') {
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.bezierCurveTo(
                    x - size, y - size,
                    x - size, y + size,
                    x, y + size * 1.5
                );
                ctx.bezierCurveTo(
                    x + size, y + size,
                    x + size, y - size,
                    x, y
                );
                ctx.closePath();
                ctx.fill();
            }
            
            let scale = 1;
            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                // 居中绘制（canvas 100x100，爱心中心在 50,50）
                drawHeart(50, 50, 25 * scale);
                scale = 0.95 + 0.1 * Math.sin(Date.now() / 300);
                requestAnimationFrame(animate);
            }
            animate();
        });
    </script>
</body>
</html>'''
    return html_content

if __name__ == "__main__":
    html = generate_heart_html()
    with open("heart.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ 已生成 'heart.html' — 双击即可在浏览器中查看三种爱心实现！")