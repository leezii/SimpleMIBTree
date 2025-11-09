#!/bin/bash

# Docker部署脚本
echo "开始Docker部署..."

# 构建并启动服务
docker-compose up -d --build

# 查看服务状态
echo "服务状态："
docker-compose ps

# 查看日志
echo "查看日志："
docker-compose logs -f
