#!/bin/bash

# MCU-Copilot 易读模式测试脚本

echo "🧪 测试API易读模式功能"
echo "====================="

API_BASE="http://8.219.74.61:80"
TOKEN="MCU_PILOT_3865d905aae1ccf8d09d07a7ee25e4cf"

echo "🎯 测试目标: $API_BASE"
echo "🔑 使用Token: ${TOKEN:0:12}..."
echo ""

# 测试1: 默认模式（含转义字符）
echo "📋 测试1: 默认模式返回"
echo "========================"
default_response=$(curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"requirement": "点亮P03 LED"}' \
    "$API_BASE/compile?use_gemini=false")

if echo "$default_response" | grep -q "assembly"; then
    echo "✅ 默认模式API调用成功"
    echo "📄 汇编代码字段 (默认格式):"
    echo "$default_response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'assembly' in data:
    print('包含 \\\\n 转义字符:')
    print(repr(data['assembly'][:100] + '...'))
"
else
    echo "❌ 默认模式API调用失败"
    echo "$default_response" | head -c 200
fi

echo ""
echo ""

# 测试2: 易读模式
echo "📋 测试2: 易读模式返回"
echo "====================="
pretty_response=$(curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"requirement": "点亮P03 LED"}' \
    "$API_BASE/compile?use_gemini=false&pretty=true")

if echo "$pretty_response" | grep -q "assembly_formatted"; then
    echo "✅ 易读模式API调用成功"
    echo "📄 新增格式化字段检查:"
    echo "$pretty_response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
fields = ['assembly_formatted', 'filtered_assembly_formatted', 'thought_formatted']
for field in fields:
    if field in data and data[field]:
        print(f'✅ {field}: 存在')
    else:
        print(f'❌ {field}: 缺失或为空')

if 'assembly_formatted' in data:
    print('\\n📝 格式化汇编代码预览:')
    print(data['assembly_formatted'][:200])
"
else
    echo "❌ 易读模式API调用失败"
    echo "$pretty_response" | head -c 200
fi

echo ""
echo ""

# 测试3: 比较输出差异
echo "📋 测试3: 输出格式对比"
echo "====================="

# 保存两个响应到临时文件
echo "$default_response" > /tmp/default_response.json
echo "$pretty_response" > /tmp/pretty_response.json

python3 << 'EOF'
import json

# 读取两个响应
try:
    with open('/tmp/default_response.json') as f:
        default = json.load(f)
    with open('/tmp/pretty_response.json') as f:
        pretty = json.load(f)

    print("🔍 字段对比:")
    print(f"默认模式字段数量: {len(default)}")
    print(f"易读模式字段数量: {len(pretty)}")

    if 'assembly' in default and 'assembly_formatted' in pretty:
        default_assembly = default['assembly']
        pretty_assembly = pretty['assembly_formatted']

        print(f"\n📏 汇编代码长度对比:")
        print(f"默认格式: {len(default_assembly)} 字符")
        print(f"易读格式: {len(pretty_assembly)} 字符")

        # 检查转义字符
        default_newlines = default_assembly.count('\\n')
        pretty_newlines = pretty_assembly.count('\n')

        print(f"\n🔤 换行符对比:")
        print(f"默认格式 \\n 转义字符: {default_newlines}")
        print(f"易读格式真实换行符: {pretty_newlines}")

        if pretty_newlines > 0 and default_newlines > 0:
            print("✅ 转义字符转换成功!")
        else:
            print("⚠️  转义字符转换可能有问题")

except Exception as e:
    print(f"❌ 分析失败: {e}")
EOF

# 清理临时文件
rm -f /tmp/default_response.json /tmp/pretty_response.json

echo ""
echo "🎉 易读模式测试完成!"
echo ""
echo "💡 使用建议:"
echo "- 在终端中使用API时，添加 &pretty=true 参数"
echo "- 前端界面可以显示 assembly_formatted 字段"
echo "- 格式化字段更适合代码复制和使用"