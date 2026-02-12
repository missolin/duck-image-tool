# 鸭鸭图 Web 服务部署指南

基于原项目核心逻辑实现的 Web 版本，支持在线编码和解码。

## 快速开始

### 1. 安装依赖

```bash
cd web_backend
pip install -r requirements.txt
```

### 2. 本地运行

```bash
python app.py
```

访问 http://localhost:5000

### 3. 生产环境部署

#### 使用 Gunicorn（推荐）

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

参数说明：
- `-w 4`: 4 个工作进程
- `-b 0.0.0.0:5000`: 监听所有网卡的 5000 端口
- `--timeout 300`: 超时时间 300 秒（处理大文件）

#### 使用 Docker

```bash
docker build -t duck-web .
docker run -p 5000:5000 duck-web
```

### 4. Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name duck.yourdomain.com;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }
}
```

## API 文档

### 编码接口

**POST** `/api/encode`

参数（multipart/form-data）：
- `file`: 文件（图片或视频）
- `password`: 密码（可选）
- `title`: 标题（可选）
- `compress`: 压缩级别 2/6/8

返回：PNG 图片文件

### 解码接口

**POST** `/api/decode`

参数（multipart/form-data）：
- `file`: 鸭子图文件
- `password`: 密码（可选）

返回：原始文件

### 健康检查

**GET** `/api/health`

返回：`{"status": "ok", "version": "1.2"}`

## 注意事项

1. 确保服务器有足够的内存处理大文件
2. 建议配置 Nginx 限制上传大小
3. 生产环境建议使用 HTTPS
4. 可以配置 Redis 做缓存优化

## 性能优化建议

1. 使用 CDN 加速静态资源
2. 启用 Gzip 压缩
3. 配置文件缓存策略
4. 使用负载均衡处理高并发

## 安全建议

1. 限制上传文件大小和类型
2. 添加请求频率限制（Rate Limiting）
3. 使用 HTTPS 加密传输
4. 定期清理临时文件
