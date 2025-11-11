# Flask网络工具集生产环境部署指南

## 🚀 部署方式概览

### 1. 传统服务器部署
### 2. Docker容器化部署
### 3. 云平台部署（Heroku、AWS等）
### 4. Nginx + Gunicorn部署

---

## 📋 部署前准备

### 环境要求
- Python 3.8+
- 操作系统：Linux/Ubuntu/CentOS
- 内存：至少512MB
- 存储：至少1GB

### 代码准备
```bash
# 克隆代码
git clone git@github.com:leezii/SimpleMIBTree.git
cd SimpleMIBTree

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 编译翻译文件（重要！）
pybabel compile -d locales
```

---

## 🐳 方式一：Docker部署（推荐）

### 1. 创建Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.app:app"]
```

### 2. 创建docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
    environment:
      - FLASK_ENV=production
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
    restart: unless-stopped
```

### 3. 部署命令
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 🖥️ 方式二：Nginx + Gunicorn部署

### 1. 安装Gunicorn
```bash
pip install gunicorn
```

### 2. 创建Gunicorn配置文件
```python
# gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### 3. 创建Systemd服务
```ini
# /etc/systemd/system/flask-web.service
[Unit]
Description=Flask Web Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/SimpleMIBTree
Environment="PATH=/path/to/SimpleMIBTree/venv/bin"
ExecStart=/path/to/SimpleMIBTree/venv/bin/gunicorn -c gunicorn.conf.py src.app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. 配置Nginx
```nginx
# /etc/nginx/sites-available/flask-web
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 文件上传大小限制
        client_max_body_size 50M;
    }

    # 静态文件（如果有）
    location /static {
        alias /path/to/SimpleMIBTree/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5. 启动服务
```bash
# 启用并启动Flask服务
sudo systemctl enable flask-web
sudo systemctl start flask-web

# 配置Nginx
sudo ln -s /etc/nginx/sites-available/flask-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ☁️ 方式三：云平台部署

### Heroku部署
1. 安装Heroku CLI
2. 创建Procfile：
```
web: gunicorn --bind 0.0.0.0:$PORT src.app:app
```
3. 部署命令：
```bash
heroku create your-app-name
git push heroku main
```

### AWS Elastic Beanstalk
1. 安装EB CLI
2. 初始化应用：
```bash
eb init
eb create production
```

---

## 🔧 生产环境配置

### 1. 环境变量配置
```bash
# 创建.env文件
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=52428800  # 50MB

# 国际化配置
BABEL_DEFAULT_LOCALE=zh  # 默认语言：zh 或 en
BABEL_TRANSLATION_DIRECTORIES=/app/locales
```

### 2. 安全配置
```python
# src/config.py
import os

class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))
    
    # 安全头
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
```

### 3. 日志配置
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/flask-web.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

---

## 📊 监控和维护

### 1. 健康检查
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
```

### 2. 性能监控
```bash
# 安装监控工具
pip install psutil

# 在应用中添加监控端点
@app.route('/metrics')
def metrics():
    import psutil
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }
```

### 3. 备份策略
```bash
# 创建备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz uploads/ logs/
```

---

## 🚨 故障排除

### 常见问题
1. **502 Bad Gateway**: 检查Gunicorn是否运行
2. **文件上传失败**: 检查权限和磁盘空间
3. **内存不足**: 调整worker数量
4. **端口冲突**: 检查端口占用

### 日志查看
```bash
# Systemd服务日志
sudo journalctl -u flask-web -f

# Nginx日志
sudo tail -f /var/log/nginx/error.log

# 应用日志
tail -f logs/flask-web.log
```

---

## 📈 性能优化

### 1. 缓存配置
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/data')
@cache.cached(timeout=300)  # 缓存5分钟
def get_data():
    return expensive_operation()
```

### 2. 压缩配置
```python
from flask_compress import Compress

Compress(app)
```

### 3. CDN配置
```nginx
# 在Nginx中配置CDN
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header X-CDN-Cache "HIT";
}
```

---

## 🔒 安全最佳实践

1. **HTTPS配置**: 使用Let's Encrypt免费SSL证书
2. **防火墙配置**: 只开放必要端口
3. **定期更新**: 保持系统和依赖包更新
4. **访问控制**: 限制管理功能访问
5. **数据备份**: 定期备份重要数据

---

## 📞 部署检查清单

- [ ] 代码已推送到生产分支
- [ ] 依赖包已安装
- [ ] 环境变量已配置
- [ ] 数据库已初始化（如需要）
- [ ] 静态文件已处理
- [ ] SSL证书已配置
- [ ] 监控已设置
- [ ] 备份策略已实施
- [ ] 性能测试已完成
- [ ] 安全检查已通过
- [ ] **翻译文件已编译** (`pybabel compile -d locales`)
- [ ] **国际化配置已验证** (测试中英文切换)
- [ ] **语言文件权限已设置** (确保应用可读取 locales/ 目录)

---

**选择适合你需求的部署方式，按照步骤操作即可成功部署Flask应用！** 🚀
