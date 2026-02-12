#!/bin/bash

# 鸭鸭图 Web 服务启动脚本
# 用法: ./start_server.sh

set -e

echo "🦆 鸭鸭图 Web 服务启动脚本"
echo "================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3，请先安装 Python 3"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"

# 检查并关闭占用端口的进程
PORT=8888
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 $PORT 已被占用，正在关闭..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
    echo "✅ 端口已释放"
fi

# 进入后端目录
cd web_backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
if [ ! -f "venv/.installed" ]; then
    echo "📥 安装依赖包..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.installed
else
    echo "✅ 依赖已安装"
fi

# 启动服务
echo ""
echo "🚀 启动 Flask 服务..."
echo "================================"
echo "📍 本地访问: http://localhost:$PORT"
echo "📍 局域网访问: http://$(ipconfig getifaddr en0 2>/dev/null || hostname):$PORT"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================"
echo ""

# 启动 Flask
python3 app.py
