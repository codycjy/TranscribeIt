# 轻量级 Debian 版本的 Dockerfile
FROM python:3.10-slim-bullseye

# 设置工作目录
WORKDIR /app

# 避免交互式配置
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip3 install --no-cache-dir --upgrade pip

RUN pip3 install --no-cache-dir streamlit torch openai-whisper
# 安装Python依赖
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt


# 复制应用代码
COPY . .

# 创建下载目录
RUN mkdir -p downloads

# 暴露Streamlit默认端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "main.py"]
