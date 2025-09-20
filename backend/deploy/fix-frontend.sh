#!/bin/bash

# MCU-Copilot 前端问题修复脚本

echo "🔧 修复前端部署问题"
echo "=================="

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请以root权限运行此脚本: sudo $0"
    exit 1
fi

PROJECT_DIR="/opt/mcu-copilot"
NGINX_CONF_DIR="/etc/nginx/sites-available"
NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"

echo "📋 项目目录: $PROJECT_DIR"

# 检查前端文件
echo "🔍 检查前端文件..."
if [ ! -f "$PROJECT_DIR/frontend/dist/index.html" ]; then
    echo "❌ 前端文件不存在，需要重新复制"
    if [ -d "$PROJECT_DIR/mcu-code-whisperer/dist" ]; then
        echo "📦 复制前端文件..."
        cp -r $PROJECT_DIR/mcu-code-whisperer/dist/* $PROJECT_DIR/frontend/dist/
        chown -R www-data:www-data $PROJECT_DIR/frontend/dist
        chmod -R 755 $PROJECT_DIR/frontend/dist
        echo "✅ 前端文件复制完成"
    else
        echo "❌ 构建产物不存在"
        exit 1
    fi
fi

# 更新Nginx配置
echo "🔧 更新Nginx配置..."
cp $PROJECT_DIR/backend/deploy/nginx-frontend.conf $NGINX_CONF_DIR/mcu-copilot

# 测试配置
echo "🧪 测试Nginx配置..."
if nginx -t; then
    echo "✅ Nginx配置测试通过"
else
    echo "❌ Nginx配置测试失败"
    exit 1
fi

# 重新加载Nginx
echo "🔄 重新加载Nginx..."
systemctl reload nginx

echo "✅ 修复完成！"
echo ""
echo "🧪 测试命令:"
echo "curl -I http://8.219.74.61/"
echo "curl http://8.219.74.61/health"