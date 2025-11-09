#!/bin/bash

# Systemd部署脚本
echo "开始Systemd部署..."

# 设置变量
APP_PATH="/path/to/SimpleMIBTree"
SERVICE_NAME="flask-web"

# 检查路径
if [ ! -d "$APP_PATH" ]; then
    echo "错误：应用路径不存在：$APP_PATH"
    echo "请修改脚本中的APP_PATH变量"
    exit 1
fi

# 复制服务文件
echo "复制systemd服务文件..."
sudo cp deployment/systemd/flask-web.service /etc/systemd/system/
sudo cp deployment/systemd/gunicorn.conf.py $APP_PATH/

# 设置权限
echo "设置文件权限..."
sudo chown -R www-data:www-data $APP_PATH
sudo chmod +x deployment/systemd/deploy.sh

# 重新加载systemd
echo "重新加载systemd..."
sudo systemctl daemon-reload

# 启用并启动服务
echo "启动Flask服务..."
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# 检查服务状态
echo "检查服务状态："
sudo systemctl status $SERVICE_NAME

echo "Systemd部署完成！"
echo "查看日志：sudo journalctl -u $SERVICE_NAME -f"
