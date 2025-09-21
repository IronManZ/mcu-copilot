#!/bin/bash

# MCU-Copilot 服务器端部署脚本
# 此脚本会被GitHub Actions在服务器上执行

set -e  # 出错时立即退出

echo "=== MCU-Copilot Server Deployment Script ==="

# 配置变量
PROJECT_DIR="/root/mcu-copilot"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/mcu-code-whisperer"
NGINX_DIR="/var/www/mcu-copilot"

# 函数：输出带时间戳的日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 函数：检查命令是否成功
check_command() {
    if [ $? -eq 0 ]; then
        log "✅ $1 succeeded"
    else
        log "❌ $1 failed"
        exit 1
    fi
}

# 1. 更新代码
log "Updating code from repository..."
cd $PROJECT_DIR
git pull origin main
check_command "Git pull"

git submodule update --init --recursive
check_command "Submodule update"

# 2. 部署后端
log "Deploying backend..."
cd $BACKEND_DIR

# 停止现有服务
docker-compose -f docker-compose.prod.yml down
log "Stopped existing backend service"

# 重新构建并启动服务
docker-compose -f docker-compose.prod.yml build
check_command "Backend Docker build"

docker-compose -f docker-compose.prod.yml up -d
check_command "Backend service start"

# 等待服务启动
log "Waiting for backend to be ready..."
sleep 20

# 健康检查
for i in {1..12}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log "✅ Backend health check passed"
        break
    fi
    if [ $i -eq 12 ]; then
        log "❌ Backend health check failed after 12 attempts"
        exit 1
    fi
    log "Backend not ready yet, waiting... ($i/12)"
    sleep 5
done

# 3. 部署前端
log "Deploying frontend..."
cd $FRONTEND_DIR

# 安装依赖
npm ci
check_command "Frontend npm install"

# 构建前端
npm run build
check_command "Frontend build"

# 部署到nginx目录
log "Copying frontend files to nginx directory..."
mkdir -p $NGINX_DIR
rm -rf $NGINX_DIR/*
cp -r dist/* $NGINX_DIR/
check_command "Frontend file copy"

# 重新加载nginx配置
log "Reloading nginx..."
systemctl reload nginx
check_command "Nginx reload"

# 4. 最终验证
log "Running final verification..."

# 测试前端
if curl -f http://localhost/ >/dev/null 2>&1; then
    log "✅ Frontend is accessible"
else
    log "❌ Frontend verification failed"
    exit 1
fi

# 测试API直接访问
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    log "✅ Backend API is accessible"
else
    log "❌ Backend API verification failed"
    exit 1
fi

# 测试API通过nginx代理
if curl -f http://localhost/api/health >/dev/null 2>&1; then
    log "✅ API proxy is working"
else
    log "❌ API proxy verification failed"
    exit 1
fi

log "=== Deployment completed successfully! ==="

# 输出服务状态
log "Service status:"
docker-compose -f $BACKEND_DIR/docker-compose.prod.yml ps
systemctl status nginx --no-pager

log "Deployment script finished."