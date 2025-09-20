#!/bin/bash

# MCU-Copilot 上传缺失文件脚本
# 上传系统提示词等必需文件到服务器

echo "📤 上传缺失的系统文件到服务器"
echo "=========================="

SERVER="root@8.219.74.61"
PROJECT_DIR="/opt/mcu-copilot"

echo "🎯 目标服务器: $SERVER"
echo "📁 项目目录: $PROJECT_DIR"

# 检查本地文件
echo ""
echo "🔍 检查本地必需文件..."

LOCAL_FILES=(
    "fpga-simulator/zh5001_prompt.md"
    "fpga-simulator/zh5001_programming_assistant.md"
    "fpga-simulator/zh5001_programming_assistant_v3.md"
)

for file in "${LOCAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
        exit 1
    fi
done

echo ""
echo "📤 开始上传文件..."

# 确保服务器目录存在
echo "📁 创建服务器目录..."
ssh $SERVER "mkdir -p $PROJECT_DIR/fpga-simulator"

# 上传fpga-simulator整个目录
echo "📦 上传fpga-simulator目录..."
rsync -avz --progress fpga-simulator/ $SERVER:$PROJECT_DIR/fpga-simulator/

# 上传编译器目录（如果不存在）
if [ -d "compiler" ]; then
    echo "📦 上传编译器相关文件..."
    rsync -avz --progress compiler/ $SERVER:$PROJECT_DIR/compiler/
fi

echo ""
echo "🔧 在服务器上设置权限..."
ssh $SERVER << 'EOF'
cd /opt/mcu-copilot
chown -R root:root fpga-simulator/
chmod -R 644 fpga-simulator/*.md
chmod -R 755 fpga-simulator/

if [ -d "compiler" ]; then
    chown -R root:root compiler/
    chmod -R 644 compiler/*.py
    chmod +x compiler/*.py
fi

echo "✅ 权限设置完成"
EOF

echo ""
echo "🧪 验证文件上传..."
ssh $SERVER << 'EOF'
cd /opt/mcu-copilot
echo "📋 检查关键文件:"
if [ -f "fpga-simulator/zh5001_prompt.md" ]; then
    echo "✅ fpga-simulator/zh5001_prompt.md"
else
    echo "❌ fpga-simulator/zh5001_prompt.md 缺失"
fi

if [ -f "fpga-simulator/zh5001_programming_assistant.md" ]; then
    echo "✅ fpga-simulator/zh5001_programming_assistant.md"
else
    echo "❌ fpga-simulator/zh5001_programming_assistant.md 缺失"
fi

echo ""
echo "📁 fpga-simulator目录内容:"
ls -la fpga-simulator/ | head -10
EOF

echo ""
echo "🔄 重启后端服务以加载新文件..."
ssh $SERVER << 'EOF'
cd /opt/mcu-copilot/backend/deploy/docker
docker-compose restart
echo "✅ 后端服务重启完成"
EOF

echo ""
echo "🎉 文件上传完成！"
echo ""
echo "🧪 测试建议:"
echo "1. 访问前端: http://8.219.74.61"
echo "2. 尝试生成代码功能"
echo "3. 检查是否还有文件缺失错误"