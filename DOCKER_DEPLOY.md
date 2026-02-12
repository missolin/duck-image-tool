# 🐳 Docker 部署指南

## 本地 Docker 部署

### 1. 启动 Docker Desktop
确保 Docker Desktop 正在运行

### 2. 构建镜像
```bash
cd /Users/n/Desktop/小黄鸭
docker build -t duck-image-tool .
```

### 3. 运行容器
```bash
# 方式 A: 使用 docker run
docker run -d -p 8888:8888 --name duck-tool duck-image-tool

# 方式 B: 使用 docker-compose（推荐）
docker-compose up -d
```

### 4. 访问应用
打开浏览器访问: http://localhost:8888

### 5. 查看日志
```bash
docker logs -f duck-tool
# 或
docker-compose logs -f
```

### 6. 停止服务
```bash
docker stop duck-tool
# 或
docker-compose down
```

---

## 部署到云平台（免费）

### 🚂 Railway（最推荐）
**优点**: 自动检测 Dockerfile，免费额度充足

1. 访问 https://railway.app
2. 用 GitHub 登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择 `missolin/duck-image-tool` 仓库
5. Railway 自动检测 Dockerfile 并部署
6. 点击 "Generate Domain" 获取链接

**免费额度**: 每月 $5（约 500 小时）

---

### 🎨 Render（也很好）
**优点**: 永久免费，但会休眠

1. 访问 https://render.com
2. 点击 "New +" → "Web Service"
3. 连接 GitHub 仓库 `missolin/duck-image-tool`
4. 配置:
   - Name: `duck-image-tool`
   - Environment: `Docker`
   - Instance Type: `Free`
5. 点击 "Create Web Service"
6. 等待部署完成（约 5 分钟）

**注意**: 免费版 15 分钟无访问会休眠，下次访问需要等待启动

---

### ✈️ Fly.io（技术流）
**优点**: 全球 CDN，速度快

```bash
# 1. 安装 flyctl
brew install flyctl

# 2. 登录
flyctl auth login

# 3. 初始化项目
flyctl launch
# 选择:
# - App name: duck-image-tool
# - Region: Hong Kong (hkg) 或 Tokyo (nrt)
# - 不要创建 Postgres
# - 不要立即部署

# 4. 修改 fly.toml（已自动生成）
# 确保 internal_port = 8888

# 5. 部署
flyctl deploy

# 6. 打开应用
flyctl open
```

**免费额度**: 3 个应用，每月 160 小时

---

### 🌊 DigitalOcean App Platform
**优点**: 稳定可靠

1. 访问 https://cloud.digitalocean.com/apps
2. 点击 "Create App"
3. 选择 GitHub 仓库
4. 配置:
   - Type: Web Service
   - Dockerfile Path: `Dockerfile`
   - HTTP Port: 8888
5. 选择 Basic 计划（$5/月，有 $200 免费额度）

---

## 推荐部署方案对比

| 平台 | 免费额度 | 休眠 | 速度 | 推荐度 |
|------|---------|------|------|--------|
| Railway | $5/月 | ❌ | ⭐⭐⭐⭐⭐ | 🏆 最推荐 |
| Render | 永久免费 | ✅ 15分钟 | ⭐⭐⭐⭐ | 👍 推荐 |
| Fly.io | 160小时/月 | ❌ | ⭐⭐⭐⭐⭐ | 👍 推荐 |
| DigitalOcean | $200 额度 | ❌ | ⭐⭐⭐⭐⭐ | 💰 付费后最佳 |

---

## 快速部署命令

### Railway（最简单）
```bash
# 1. 确保代码已推送到 GitHub
git add .
git commit -m "Ready for deployment"
git push

# 2. 访问 Railway 网站部署
open https://railway.app
```

### Render
```bash
# 直接在网站操作，无需命令行
open https://render.com
```

### Fly.io
```bash
flyctl launch --now
```

---

## 故障排查

### Docker 构建失败
```bash
# 清理缓存重新构建
docker system prune -a
docker build --no-cache -t duck-image-tool .
```

### 端口被占用
```bash
# 查看占用端口的进程
lsof -i :8888

# 杀死进程
kill -9 <PID>
```

### FFmpeg 未安装
Docker 镜像已包含 FFmpeg，无需额外安装

---

## 下一步

选择一个平台部署后，你会得到一个公网链接，例如：
- Railway: `https://duck-image-tool.up.railway.app`
- Render: `https://duck-image-tool.onrender.com`
- Fly.io: `https://duck-image-tool.fly.dev`

可以直接分享给其他人使用！
