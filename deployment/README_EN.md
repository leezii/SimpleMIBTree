# 部署配置文件说明

本目录包含了Flask网络工具集的各种部署方式配置文件和脚本。

## 📁 目录结构

```
deployment/
├── docker/          # Docker容器化部署
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── deploy.sh
├── nginx/           # Nginx反向代理配置
│   └── flask-web
├── heroku/          # Heroku云平台部署
│   ├── Procfile
│   └── deploy.sh
├── systemd/         # Systemd服务部署
│   ├── flask-web.service
│   ├── gunicorn.conf.py
│   └── deploy.sh
└── README.md        # 本文件
```

## 🚀 快速部署指南

### 1. Docker部署（推荐）
```bash
cd deployment/docker
chmod +x deploy.sh
./deploy.sh
```

### 2. Heroku部署
```bash
cd deployment/heroku
chmod +x deploy.sh
./deploy.sh
```

### 3. Systemd部署
```bash
cd deployment/systemd
chmod +x deploy.sh
# 修改deploy.sh中的APP_PATH变量
./deploy.sh
```

### 4. 手动Nginx配置
```bash
sudo cp deployment/nginx/flask-web /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/flask-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📋 部署前检查清单

- [ ] 已安装Python 3.8+
- [ ] 已安装Docker（Docker部署）
- [ ] 已安装Nginx（反向代理部署）
- [ ] 已配置域名和SSL证书
- [ ] 已设置防火墙规则
- [ ] 已配置监控和日志

## 🔧 配置说明

### 环境变量
根据部署方式，可能需要设置以下环境变量：
- `FLASK_ENV=production`
- `SECRET_KEY=your-secret-key`
- `UPLOAD_FOLDER=/app/uploads`
- `MAX_CONTENT_LENGTH=52428800`
- `BABEL_DEFAULT_LOCALE=zh`  # 默认语言：zh 或 en
- `BABEL_TRANSLATION_DIRECTORIES=/app/locales`

### 端口配置
- Flask应用：5000
- Nginx代理：80/443
- Docker映射：5000:5000

### 权限设置
- 上传目录：www-data:www-data
- 日志目录：www-data:www-data
- 配置文件：644权限

## 🚨 注意事项

1. **路径配置**：所有脚本中的路径都需要根据实际部署位置修改
2. **权限管理**：确保应用有正确的文件读写权限
3. **安全配置**：生产环境必须配置HTTPS和防火墙
4. **监控设置**：建议配置日志轮转和监控告警
5. **备份策略**：定期备份上传的文件和配置
6. **国际化配置**：部署前必须运行 `pybabel compile -d locales` 编译翻译文件
7. **语言文件权限**：确保应用有权限读取 `locales/` 目录及其子目录

## 📞 故障排除

### 常见问题
1. **端口冲突**：检查5000端口是否被占用
2. **权限错误**：检查文件和目录权限
3. **服务启动失败**：查看systemd或docker日志
4. **Nginx 502错误**：检查后端服务是否运行

### 日志查看
```bash
# Docker日志
docker-compose logs -f

# Systemd日志
sudo journalctl -u flask-web -f

# Nginx日志
sudo tail -f /var/log/nginx/error.log
```

选择适合你环境的部署方式，按照对应目录下的说明进行操作！
