# 🚀 Railway 部署指南

## 部署步骤

### 1. 准备 Git 仓库
```bash
cd /Users/n/Desktop/小黄鸭
git init
git add .
git commit -m "Initial commit"
```

### 2. 推送到 GitHub（可选但推荐）
```bash
# 在 GitHub 创建新仓库后
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

### 3. 部署到 Railway

#### 方式 A：通过 GitHub（推荐）
1. 访问 https://railway.app
2. 点击 "Start a New Project"
3. 选择 "Deploy from GitHub repo"
4. 授权并选择你的仓库
5. Railway 会自动检测配置并部署
6. 等待部署完成（约 2-3 分钟）
7. 点击 "Generate Domain" 获取公网链接

#### 方式 B：通过 Railway CLI
```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 或使用 Homebrew
brew install railway

# 登录
railway login

# 初始化项目
railway init

# 部署
railway up

# 生成域名
railway domain
```

### 4. 配置环境变量（可选）
在 Railway 项目设置中添加：
- `PYTHON_VERSION`: 3.9
- `PORT`: 自动设置，无需手动配置

### 5. 查看日志
```bash
railway logs
```

## 部署后
- ✅ 自动获得 HTTPS 链接：`https://你的项目名.up.railway.app`
- ✅ 自动重启和健康检查
- ✅ 支持视频编解码（FFmpeg 已安装）
- ✅ 每月 $5 免费额度（约 500 小时）

## 更新部署
```bash
git add .
git commit -m "Update"
git push

# Railway 会自动重新部署
```

## 注意事项
1. 免费版有使用限制，超出后需要付费
2. 上传文件大小限制（建议 < 100MB）
3. 视频合并可能需要较长时间，注意超时设置

## 故障排查
- 查看日志：`railway logs`
- 重启服务：`railway restart`
- 查看状态：`railway status`
