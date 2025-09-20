#!/bin/bash

# 修复Python 3.11 pip安装问题的快速脚本

echo "🔧 修复Python 3.11 pip安装问题"
echo "================================"

# 安装Python 3.11的distutils和其他依赖
echo "📦 安装Python 3.11依赖包..."
apt-get install -y python3.11-distutils python3.11-dev

# 手动安装pip for Python 3.11
if ! command -v pip3.11 &> /dev/null; then
    echo "📦 手动安装pip for Python 3.11..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3.11 get-pip.py
    rm get-pip.py
    echo "✅ pip3.11安装完成"
else
    echo "ℹ️ pip3.11已安装"
fi

# 验证安装
echo ""
echo "🧪 验证Python 3.11和pip安装:"
python3.11 --version
pip3.11 --version

echo ""
echo "✅ Python 3.11环境修复完成！"
echo "现在可以继续进行Docker部署了。"