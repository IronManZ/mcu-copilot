#!/bin/bash

# MCU-Copilot 新加坡服务器一键部署脚本
# 阿里云ECS新加坡节点 (8.219.74.61) 专用部署脚本

set -e

echo "🇸🇬 MCU-Copilot 新加坡服务器部署脚本"
echo "======================================"
echo "📍 目标服务器: 8.219.74.61 (阿里云新加坡)"
echo "📦 GitHub仓库: https://github.com/IronManZ/mcu-copilot"
echo ""

# 确认部署
read -p "是否继续部署到新加坡服务器？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 1
fi

# 检查SSH连接
echo "🔗 检查服务器连接..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes root@8.219.74.61 exit &>/dev/null; then
    echo "❌ 无法连接到服务器 8.219.74.61"
    echo "请确保："
    echo "  1. SSH密钥已配置"
    echo "  2. 安全组允许SSH连接"
    echo "  3. 服务器运行正常"
    exit 1
fi
echo "✅ 服务器连接正常"

# 远程执行部署命令
echo ""
echo "🚀 开始远程部署..."
ssh root@8.219.74.61 'bash -s' << 'EOF'
echo "📦 步骤1: 环境准备"
# 更新系统
apt update && apt upgrade -y
apt install -y curl wget git unzip

# 安装Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 安装Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    rm get-docker.sh
else
    echo "✅ Docker已安装"
fi

# 安装Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "🔧 安装Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose已安装"
fi

# 创建应用用户和目录
if ! id "mcucopilot" &>/dev/null; then
    useradd -m -s /bin/bash mcucopilot
    usermod -aG docker mcucopilot
fi
mkdir -p /opt/mcu-copilot
chown mcucopilot:mcucopilot /opt/mcu-copilot

echo "📦 步骤2: 代码部署"
cd /opt/mcu-copilot

# 克隆或更新代码
if [ -d ".git" ]; then
    echo "🔄 更新现有代码..."
    git fetch origin
    git reset --hard origin/main
else
    echo "📥 克隆新代码..."
    git clone https://github.com/IronManZ/mcu-copilot.git .
fi

echo "📦 步骤3: 环境配置"
# 复制环境配置文件
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "⚠️  请配置backend/.env文件中的API密钥:"
    echo "   - QIANWEN_APIKEY=your-qianwen-api-key"
    echo "   - GEMINI_APIKEY=your-gemini-api-key"
    echo ""
    echo "🔧 使用以下命令编辑配置文件:"
    echo "   vi /opt/mcu-copilot/backend/.env"
    echo ""
    read -p "配置完成后按回车继续..." -r
fi

echo "📦 步骤4: 启动服务"
cd backend/deploy/docker

# 检查配置文件
if ! grep -q "sk-" ../../../backend/.env || ! grep -q "AIza" ../../../backend/.env; then
    echo "⚠️  检测到API密钥可能未配置，请确认.env文件:"
    cat ../../../backend/.env | grep -E "(QIANWEN|GEMINI)_APIKEY"
    echo ""
    read -p "确认配置无误后按回车继续..." -r
fi

# 构建并启动容器
echo "🐳 启动Docker服务..."
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

echo "🧪 健康检查..."
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ 服务启动成功！"
else
    echo "❌ 服务可能未正常启动，检查日志:"
    docker-compose logs --tail=20
fi

echo ""
echo "🎉 部署完成！"
echo "=================================="
echo "📍 服务地址: http://8.219.74.61:8000"
echo "🔑 API Token: mcu-copilot-2025-seed-token"
echo "📚 GitHub: https://github.com/IronManZ/mcu-copilot"
echo ""
echo "🧪 测试命令:"
echo "curl http://8.219.74.61:8000/health"
echo ""
echo "🔧 管理命令:"
echo "  查看日志: docker-compose logs -f"
echo "  重启服务: docker-compose restart"
echo "  停止服务: docker-compose down"
EOF

# 本地测试连接
echo ""
echo "🧪 本地测试服务连接..."
sleep 5

if curl -s http://8.219.74.61:8000/health >/dev/null; then
    echo "✅ 远程服务连接成功！"

    # 运行完整API测试
    echo ""
    echo "🔬 运行API功能测试..."
    if [ -f "./seed_user_test.sh" ]; then
        chmod +x ./seed_user_test.sh
        ./seed_user_test.sh http://8.219.74.61:8000
    else
        echo "⚠️  测试脚本未找到，手动测试API："
        echo "curl -H 'Authorization: Bearer mcu-copilot-2025-seed-token' http://8.219.74.61:8000/auth/me"
    fi
else
    echo "❌ 无法连接到远程服务，可能的问题："
    echo "  1. 防火墙未开放8000端口"
    echo "  2. 服务启动失败"
    echo "  3. 网络连接问题"
    echo ""
    echo "🔧 排查命令："
    echo "ssh root@8.219.74.61 'cd /opt/mcu-copilot/backend/deploy/docker && docker-compose logs'"
fi

echo ""
echo "🎊 新加坡服务器部署完成！"
echo "=============================="
echo "📋 部署总结:"
echo "  🌐 服务地址: http://8.219.74.61:8000"
echo "  🔑 认证Token: mcu-copilot-2025-seed-token"
echo "  📊 健康检查: curl http://8.219.74.61:8000/health"
echo "  📚 用户指南: backend/deploy/SEED_USER_GUIDE.md"
echo "  📖 部署文档: backend/deploy/DEPLOYMENT_GUIDE.md"
echo ""
echo "🚀 现在您可以将API信息分享给种子用户开始测试！"