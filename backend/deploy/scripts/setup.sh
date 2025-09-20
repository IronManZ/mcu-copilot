#!/bin/bash

# MCU-Copilot 后端服务部署脚本
# 支持阿里云ECS和AWS EC2

set -e  # 遇到错误立即退出

echo "🚀 MCU-Copilot 后端服务部署脚本"
echo "=================================="

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请以root权限运行此脚本: sudo $0"
    exit 1
fi

# 检测系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "❌ 无法检测系统类型"
    exit 1
fi

echo "📋 检测到系统: $OS $VER"

# 更新系统包
echo "📦 更新系统包..."
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    apt-get update
    apt-get upgrade -y
    apt-get install -y curl wget git unzip
elif [[ "$OS" == *"Amazon Linux"* ]] || [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
    yum update -y
    yum install -y curl wget git unzip
fi

# 安装Docker
echo "🐳 安装Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    rm get-docker.sh
    echo "✅ Docker安装完成"
else
    echo "ℹ️ Docker已安装"
fi

# 安装Docker Compose
echo "🔧 安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose安装完成"
else
    echo "ℹ️ Docker Compose已安装"
fi

# 安装Python 3.11（如果需要本地运行）
echo "🐍 安装Python 3.11..."
if [[ "$OS" == *"Ubuntu"* ]]; then
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get update
    apt-get install -y python3.11 python3.11-pip python3.11-venv
elif [[ "$OS" == *"Amazon Linux"* ]]; then
    yum install -y python3.11 python3.11-pip
fi

# 创建应用用户
echo "👤 创建应用用户..."
if ! id "mcucopilot" &>/dev/null; then
    useradd -m -s /bin/bash mcucopilot
    usermod -aG docker mcucopilot
    echo "✅ 用户mcucopilot创建完成"
else
    echo "ℹ️ 用户mcucopilot已存在"
fi

# 创建应用目录
echo "📁 创建应用目录..."
APP_DIR="/opt/mcu-copilot"
mkdir -p $APP_DIR
chown mcucopilot:mcucopilot $APP_DIR

echo "✅ 系统环境准备完成！"
echo ""
echo "📋 下一步操作指南："
echo "1. 将代码复制到 $APP_DIR 目录"
echo "2. 配置 .env 文件"
echo "3. 运行 docker-compose up -d"
echo ""
echo "🔧 快速部署命令："
echo "cd $APP_DIR && git clone <your-repo-url> ."
echo "cp .env.example .env"
echo "vi .env  # 编辑配置文件"
echo "cd deploy/docker && docker-compose up -d"