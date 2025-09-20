#!/bin/bash

# MCU-Copilot 本地部署脚本（无Docker）
# 使用Python虚拟环境和systemd服务

set -e

echo "🔧 MCU-Copilot 本地部署脚本"
echo "============================="

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请以root权限运行此脚本: sudo $0"
    exit 1
fi

APP_DIR="/opt/mcu-copilot"
USER="mcucopilot"

# 检查应用目录是否存在
if [ ! -d "$APP_DIR" ]; then
    echo "❌ 应用目录不存在: $APP_DIR"
    echo "请先运行 setup.sh 脚本"
    exit 1
fi

echo "📦 安装Python依赖..."
# 切换到应用用户并创建虚拟环境
su - $USER -c "cd $APP_DIR && python3.11 -m venv venv"
su - $USER -c "cd $APP_DIR && venv/bin/pip install --upgrade pip"
su - $USER -c "cd $APP_DIR && venv/bin/pip install -r requirements.txt"

echo "📝 检查配置文件..."
if [ ! -f "$APP_DIR/.env" ]; then
    echo "⚠️ .env文件不存在，从模板复制..."
    su - $USER -c "cd $APP_DIR && cp .env.example .env"
    echo "🔧 请编辑 $APP_DIR/.env 文件配置API keys"
    echo "vi $APP_DIR/.env"
    read -p "配置完成后按回车继续..."
fi

echo "📋 创建logs目录..."
su - $USER -c "mkdir -p $APP_DIR/logs"

echo "🔧 配置systemd服务..."
# 复制systemd服务文件
cp $APP_DIR/deploy/systemd/mcu-copilot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable mcu-copilot

echo "🚀 启动服务..."
systemctl start mcu-copilot

echo "📊 检查服务状态..."
sleep 3
systemctl status mcu-copilot --no-pager

echo ""
echo "✅ 部署完成！"
echo ""
echo "📋 服务管理命令："
echo "  启动: systemctl start mcu-copilot"
echo "  停止: systemctl stop mcu-copilot"
echo "  重启: systemctl restart mcu-copilot"
echo "  状态: systemctl status mcu-copilot"
echo "  日志: journalctl -u mcu-copilot -f"
echo ""
echo "🌐 服务地址: http://$(hostname -I | awk '{print $1}'):8000"
echo "🔍 健康检查: curl http://localhost:8000/health"