# 🦆 鸭鸭图 - 媒体内容保护工具

一个基于隐写术的图片/视频编码解码工具，支持视频合并和帧截取功能。

## ✨ 功能特性

- 📸 **图片编码**: 将图片/视频隐藏到鸭子图中
- 🔓 **图片解码**: 从鸭子图中提取原始内容
- 🎬 **视频合并**: 支持多个视频按顺序合并
- 📹 **时间轴预览**: 类似剪映的时间轴播放功能
- 🖼️ **帧截取**: 从视频中截取任意帧并保存
- 🔐 **密码保护**: 可选的密码加密功能

## 🚀 快速开始

### 方式 1: Docker（推荐）

```bash
# 构建并启动
docker-compose up -d

# 访问
open http://localhost:8888
```

### 方式 2: 本地运行

```bash
# 使用启动脚本
./start_server.sh

# 或手动启动
cd web_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 📦 部署到云平台

### Railway（推荐）
1. Fork 这个仓库
2. 访问 https://railway.app
3. 选择 "Deploy from GitHub repo"
4. 选择你的仓库
5. 等待部署完成
6. 生成域名即可访问

### Render
1. 访问 https://render.com
2. 创建新的 Web Service
3. 连接 GitHub 仓库
4. 选择 Docker 部署
5. 等待部署完成

### Fly.io
```bash
# 安装 flyctl
brew install flyctl

# 登录
flyctl auth login

# 部署
flyctl launch
flyctl deploy
```

## 🛠️ 技术栈

- **后端**: Flask + Python 3.9
- **前端**: 原生 HTML/CSS/JavaScript
- **视频处理**: FFmpeg
- **图像处理**: Pillow + NumPy

## 📝 使用说明

### 编码
1. 上传图片或视频
2. 可选设置标题和密码
3. 选择压缩级别
4. 生成鸭子图并下载

### 解码
1. 上传鸭子图（PNG格式）
2. 如果有密码则输入
3. 提取原始文件并下载

### 视频合并
1. 上传或解码视频到视频库
2. 从左侧列表添加视频到时间轴
3. 拖拽调整视频顺序
4. 预览播放效果
5. 截取需要的帧（可选）
6. 合并并导出

## 🔧 环境要求

- Python 3.9+
- FFmpeg
- 100MB+ 可用内存

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
