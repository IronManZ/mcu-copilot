#!/bin/bash

# MCU-Copilot 安全Token生成器
# 为种子用户生成安全的API访问token

echo "🔐 MCU-Copilot Token生成器"
echo "========================"

# 生成安全随机token
generate_token() {
    local method="$1"
    case $method in
        1)
            # 使用openssl (推荐)
            echo "MCU_PILOT_$(openssl rand -hex 16)"
            ;;
        2)
            # 使用uuidgen
            echo "MCU_PILOT_$(uuidgen | tr -d '-' | tr '[:upper:]' '[:lower:]')"
            ;;
        3)
            # 使用urandom
            echo "MCU_PILOT_$(head -c 32 /dev/urandom | base64 | tr -d '=/+' | head -c 32)"
            ;;
        *)
            # 默认方法
            echo "MCU_PILOT_$(openssl rand -hex 16)"
            ;;
    esac
}

echo "选择Token生成方法:"
echo "1. OpenSSL (推荐)"
echo "2. UUID"
echo "3. URandom"
echo ""

read -p "请选择方法 (1-3，默认为1): " choice
choice=${choice:-1}

echo ""
echo "正在生成安全Token..."
TOKEN=$(generate_token $choice)

echo ""
echo "✅ Token生成成功!"
echo "🔑 您的API Token:"
echo ""
echo "    $TOKEN"
echo ""
echo "📋 使用说明:"
echo "1. 将此token配置到服务器的.env文件中"
echo "2. 通过安全渠道将token分发给种子用户"
echo "3. 用户在API请求中使用: Authorization: Bearer $TOKEN"
echo ""
echo "⚠️  安全提醒:"
echo "- 请妥善保管此token"
echo "- 不要在公开场所展示"
echo "- 建议定期更换"
echo ""

# 可选：直接更新服务器配置
read -p "是否立即更新新加坡服务器配置? (y/n): " update_server

if [[ $update_server =~ ^[Yy]$ ]]; then
    echo ""
    echo "🌐 正在更新新加坡服务器配置..."

    # 检查SSH连接
    if ssh -o ConnectTimeout=10 -o BatchMode=yes root@8.219.74.61 exit &>/dev/null 2>&1; then
        # 更新服务器配置
        ssh root@8.219.74.61 << EOF
cd /opt/mcu-copilot
# 备份当前配置
cp backend/.env backend/.env.backup.\$(date +%Y%m%d_%H%M%S)
# 更新token
sed -i 's/^API_TOKEN=.*/API_TOKEN=$TOKEN/' backend/.env
# 重启服务
cd backend/deploy/docker
docker-compose restart
echo "Token已更新并重启服务"
EOF

        echo "✅ 服务器配置更新成功!"
        echo "🧪 测试新token:"
        echo "curl -H 'Authorization: Bearer $TOKEN' http://8.219.74.61:8000/auth/me"

    else
        echo "❌ 无法连接到服务器，请手动更新配置"
        echo ""
        echo "手动更新步骤:"
        echo "1. ssh root@8.219.74.61"
        echo "2. cd /opt/mcu-copilot"
        echo "3. vi backend/.env"
        echo "4. 更新行: API_TOKEN=$TOKEN"
        echo "5. cd backend/deploy/docker && docker-compose restart"
    fi
else
    echo ""
    echo "📝 手动配置命令:"
    echo "ssh root@8.219.74.61"
    echo "cd /opt/mcu-copilot && vi backend/.env"
    echo "更新行: API_TOKEN=$TOKEN"
    echo "cd backend/deploy/docker && docker-compose restart"
fi

echo ""
echo "🎊 Token生成完成！请安全地分发给种子用户。"