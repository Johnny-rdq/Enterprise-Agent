# 1. Python 3.11 基础镜像
FROM python:3.11-slim

# 2. 设置工作目录
WORKDIR /code

# 3. 安装系统依赖（pygame 需要 SDL）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# 4. 安装 Python 依赖
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

# 5. 预装常用游戏开发包
RUN pip install --no-cache-dir pygame

# 6. 复制项目代码
COPY . /code

# 7. 暴露端口
EXPOSE 7860

# 8. 启动服务
CMD ["uvicorn", "server_app:app", "--host", "0.0.0.0", "--port", "7860"]
