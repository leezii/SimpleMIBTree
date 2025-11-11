# Flask Network Tools Production Environment Deployment Guide

## 🚀 Deployment Overview

### 1. Traditional Server Deployment
### 2. Docker Container Deployment
### 3. Cloud Platform Deployment (Heroku, AWS, etc.)
### 4. Nginx + Gunicorn Deployment

---

## 📋 Pre-deployment Preparation

### Environment Requirements
- Python 3.8+
- Operating System: Linux/Ubuntu/CentOS
- Memory: At least 512MB
- Storage: At least 1GB

### Code Preparation
```bash
# Clone code
git clone git@github.com:leezii/SimpleMIBTree.git
cd SimpleMIBTree

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Compile translation files (important!)
pybabel compile -d locales
```

---

## 🐳 Method 1: Docker Deployment (Recommended)

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production

# Startup command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.app:app"]
```

### 2. Create docker-compose.yml
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

### 3. Deployment Commands
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🖥️ Method 2: Nginx + Gunicorn Deployment

### 1. Install Gunicorn
```bash
pip install gunicorn
```

### 2. Create Gunicorn Configuration File
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

### 3. Create Systemd Service
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

### 4. Configure Nginx
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
        
        # File upload size limit
        client_max_body_size 50M;
    }

    # Static files (if any)
    location /static {
        alias /path/to/SimpleMIBTree/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5. Start Services
```bash
# Enable and start Flask service
sudo systemctl enable flask-web
sudo systemctl start flask-web

# Configure Nginx
sudo ln -s /etc/nginx/sites-available/flask-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ☁️ Method 3: Cloud Platform Deployment

### Heroku Deployment
1. Install Heroku CLI
2. Create Procfile:
```
web: gunicorn --bind 0.0.0.0:$PORT src.app:app
```
3. Deployment commands:
```bash
heroku create your-app-name
git push heroku main
```

### AWS Elastic Beanstalk
1. Install EB CLI
2. Initialize application:
```bash
eb init
eb create production
```

---

## 🔧 Production Environment Configuration

### 1. Environment Variable Configuration
```bash
# Create .env file
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=52428800  # 50MB

# Internationalization configuration
BABEL_DEFAULT_LOCALE=zh  # Default language: zh or en
BABEL_TRANSLATION_DIRECTORIES=/app/locales
```

### 2. Security Configuration
```python
# src/config.py
import os

class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
```

### 3. Logging Configuration
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

## 📊 Monitoring and Maintenance

### 1. Health Check
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
```

### 2. Performance Monitoring
```bash
# Install monitoring tools
pip install psutil

# Add monitoring endpoint in application
@app.route('/metrics')
def metrics():
    import psutil
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }
```

### 3. Backup Strategy
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz uploads/ logs/
```

---

## 🚨 Troubleshooting

### Common Issues
1. **502 Bad Gateway**: Check if Gunicorn is running
2. **File upload failure**: Check permissions and disk space
3. **Insufficient memory**: Adjust worker count
4. **Port conflict**: Check port usage

### Log Viewing
```bash
# Systemd service logs
sudo journalctl -u flask-web -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log

# Application logs
tail -f logs/flask-web.log
```

---

## 📈 Performance Optimization

### 1. Cache Configuration
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/data')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_data():
    return expensive_operation()
```

### 2. Compression Configuration
```python
from flask_compress import Compress

Compress(app)
```

### 3. CDN Configuration
```nginx
# Configure CDN in Nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header X-CDN-Cache "HIT";
}
```

---

## 🔒 Security Best Practices

1. **HTTPS Configuration**: Use Let's Encrypt free SSL certificates
2. **Firewall Configuration**: Only open necessary ports
3. **Regular Updates**: Keep system and dependency packages updated
4. **Access Control**: Limit management function access
5. **Data Backup**: Regularly backup important data

---

## 📞 Deployment Checklist

- [ ] Code pushed to production branch
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Database initialized (if needed)
- [ ] Static files handled
- [ ] SSL certificates configured
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Performance testing completed
- [ ] Security checks passed
- [ ] **Translation files compiled** (`pybabel compile -d locales`)
- [ ] **Internationalization configuration verified** (test Chinese/English switching)
- [ ] **Language file permissions set** (ensure application can read locales/ directory)

---

**Choose the deployment method that suits your needs and follow the steps to successfully deploy the Flask application!** 🚀
