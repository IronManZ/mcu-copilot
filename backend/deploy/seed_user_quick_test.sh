#!/bin/bash

# MCU-Copilot 种子用户快速测试脚本
# 简化版本，用于快速验证API功能

echo "🧪 MCU-Copilot 快速API测试"
echo "========================"

# 配置参数
BASE_URL="http://8.219.74.61:80"
API_TOKEN="${1:-YOUR_TOKEN_HERE}"

# 检查token
if [ "$API_TOKEN" = "YOUR_TOKEN_HERE" ]; then
    echo "⚠️  请提供API Token作为参数"
    echo "使用方法: $0 YOUR_ACTUAL_TOKEN"
    echo "例如: $0 MCU_PILOT_abc123def456"
    exit 1
fi

echo "📋 测试配置: $BASE_URL"
echo "🔑 Token: ${API_TOKEN:0:12}..."
echo ""

# 1. 健康检查
echo "🔍 1. 健康检查"
health_response=$(curl -s "$BASE_URL/health")
if [[ $health_response == *"ok"* ]]; then
    echo "   ✅ 服务正常"
else
    echo "   ❌ 服务异常"
    exit 1
fi

# 2. 认证测试
echo "🔍 2. 认证测试"
auth_response=$(curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL/auth/me")
if [[ $auth_response == *"authenticated"* ]]; then
    echo "   ✅ 认证成功"
else
    echo "   ❌ 认证失败"
    exit 1
fi

# 3. LED闪烁编译测试
echo "🔍 3. LED闪烁编译测试"
compile_response=$(curl -s -X POST \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"requirement": "控制P03引脚LED闪烁"}' \
    "$BASE_URL/compile?use_gemini=true")

if [[ $compile_response == *"assembly"* ]]; then
    echo "   ✅ 编译成功"
    echo "   📄 生成了汇编代码和机器码"
else
    echo "   ❌ 编译失败"
    echo "   📄 错误信息: $(echo "$compile_response" | head -c 100)..."
fi

echo ""
echo "🎉 快速测试完成！"
echo ""
echo "📋 完整API使用指南请查看: SEED_USER_GUIDE.md"
echo "🔗 更多测试功能请使用: seed_user_test.sh"
