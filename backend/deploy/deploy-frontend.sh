#!/bin/bash

# MCU-Copilot 前端部署脚本
# 在服务器上运行，部署前端到Nginx

set -e  # 遇到错误立即退出

echo "🚀 MCU-Copilot 前端部署脚本"
echo "=========================="

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请以root权限运行此脚本: sudo $0"
    exit 1
fi

# 项目目录
PROJECT_DIR="/opt/mcu-copilot"
FRONTEND_DIR="$PROJECT_DIR/frontend"
NGINX_CONF_DIR="/etc/nginx/sites-available"
NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"

echo "📋 项目目录: $PROJECT_DIR"
echo "📋 前端目录: $FRONTEND_DIR"

# 创建前端目录
echo "📁 创建前端目录..."
mkdir -p $FRONTEND_DIR

# 检查构建产物是否存在
if [ ! -d "$PROJECT_DIR/mcu-code-whisperer/dist" ]; then
    echo "❌ 前端构建产物不存在，请先在本地运行 npm run build"
    echo "💡 提示: 将构建产物上传到 $PROJECT_DIR/mcu-code-whisperer/dist"
    exit 1
fi

# 复制构建产物
echo "📦 复制前端构建产物..."
cp -r $PROJECT_DIR/mcu-code-whisperer/dist/* $FRONTEND_DIR/

# 设置文件权限
echo "🔐 设置文件权限..."
chown -R www-data:www-data $FRONTEND_DIR
chmod -R 755 $FRONTEND_DIR

# 配置Nginx
echo "🔧 配置Nginx..."

# 备份原有配置
if [ -f "$NGINX_ENABLED_DIR/default" ]; then
    mv $NGINX_ENABLED_DIR/default $NGINX_ENABLED_DIR/default.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ 备份原有Nginx配置"
fi

# 复制新的Nginx配置
cp $PROJECT_DIR/backend/deploy/nginx-frontend.conf $NGINX_CONF_DIR/mcu-copilot
ln -sf $NGINX_CONF_DIR/mcu-copilot $NGINX_ENABLED_DIR/mcu-copilot

# 测试Nginx配置
echo "🧪 测试Nginx配置..."
if nginx -t; then
    echo "✅ Nginx配置测试通过"
else
    echo "❌ Nginx配置测试失败"
    exit 1
fi

# 重启Nginx
echo "🔄 重启Nginx服务..."
systemctl restart nginx
systemctl enable nginx

# 检查Nginx状态
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx服务运行正常"
else
    echo "❌ Nginx服务启动失败"
    systemctl status nginx
    exit 1
fi

# 检查端口占用
echo "🔍 检查端口占用..."
if netstat -tlnp | grep :80 > /dev/null; then
    echo "✅ 端口80已被Nginx占用"
else
    echo "❌ 端口80未被占用，可能配置有问题"
fi

echo ""
echo "🎉 前端部署完成！"
echo ""
echo "📋 访问信息:"
echo "   前端地址: http://8.219.74.61"
echo "   API地址: http://8.219.74.61/api"
echo "   健康检查: http://8.219.74.61/health"
echo ""
echo "🧪 测试命令:"
echo "   curl http://8.219.74.61/health"
echo "   curl http://8.219.74.61/api/zh5001/info"
echo ""
echo "📄 日志位置:"
echo "   访问日志: /var/log/nginx/mcu-copilot.access.log"
echo "   错误日志: /var/log/nginx/mcu-copilot.error.log"