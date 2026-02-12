# 使用 Python 3.9 基础镜像
FROM python:3.9-slim

# 安装 FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY web_backend/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY web_backend/ ./web_backend/
COPY SS_tools-main\ 2/ ./SS_tools-main\ 2/

# 暴露端口
EXPOSE 8888

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8888

# 启动命令
CMD ["python", "web_backend/app.py"]
