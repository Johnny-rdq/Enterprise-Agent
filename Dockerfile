# 1. Python 3.11 基础镜像
FROM python:3.11-slim

# 2. 设置工作目录
WORKDIR /code

# 3. 换用清华 Debian 镜像源（加速 apt）
RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources

# 4. 安装系统依赖（pygame 需要 SDL），带重试防止镜像偶发失败
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# 5. 安装 Python 依赖（清华 PyPI 镜像）
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn -r /code/requirements.txt

# 6. 复制项目代码
COPY . /code

# 7. 暴露端口
EXPOSE 7860

# 8. 启动服务
CMD ["uvicorn", "server_app:app", "--host", "0.0.0.0", "--port", "7860"]
