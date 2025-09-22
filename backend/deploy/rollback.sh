#!/bin/bash

# MCU-Copilot 自动回滚脚本
# 当测试失败或部署失败时，回滚到上一个稳定版本

set -e

echo "=== MCU-Copilot 自动回滚脚本 ==="

# 获取当前git状态
CURRENT_COMMIT=$(git rev-parse HEAD)
echo "当前提交: $CURRENT_COMMIT"

# 获取上一个提交
PREVIOUS_COMMIT=$(git rev-parse HEAD~1)
echo "回滚目标: $PREVIOUS_COMMIT"

# 记录回滚开始
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始回滚，从 $CURRENT_COMMIT 到 $PREVIOUS_COMMIT" >> deploy/rollback.log

# 停止当前服务
echo "停止当前服务..."
docker-compose -f docker-compose.prod.yml down || true

# 回滚代码
echo "回滚代码到上一个版本..."
git reset --hard $PREVIOUS_COMMIT

# 重新构建和启动服务
echo "重新构建服务..."
docker-compose -f docker-compose.prod.yml build

echo "启动服务..."
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "等待服务启动..."
sleep 20

# 验证回滚是否成功
echo "验证回滚结果..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 回滚成功！服务已恢复正常"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 回滚成功，服务已恢复" >> deploy/rollback.log
        exit 0
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "⏳ 等待服务启动... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 5
    fi
done

echo "❌ 回滚失败！服务仍然无法访问"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 回滚失败，需要手动干预" >> deploy/rollback.log
exit 1