#!/bin/bash

# Heroku部署脚本
echo "开始Heroku部署..."

# 检查Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "错误：请先安装Heroku CLI"
    exit 1
fi

# 登录Heroku（如果需要）
heroku login

# 创建应用（如果不存在）
APP_NAME="flask-network-tools"
if ! heroku apps:info $APP_NAME &> /dev/null; then
    echo "创建Heroku应用：$APP_NAME"
    heroku create $APP_NAME
fi

# 推送代码
echo "推送代码到Heroku..."
git push heroku main

# 打开应用
echo "打开应用..."
heroku open $APP_NAME
