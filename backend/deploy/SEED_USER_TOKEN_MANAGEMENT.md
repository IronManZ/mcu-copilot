# MCU-Copilot 种子用户Token管理指南

## 🔒 安全原则

为了保护API服务的安全性，我们采用以下安全措施：

1. **Token不在公开文档中显示** - 所有公开文档使用占位符
2. **私密分发机制** - Token仅通过安全渠道分发给授权用户
3. **定期轮换** - 根据需要定期更换token
4. **使用监控** - 跟踪token使用情况

## 👨‍💼 管理员操作指南

### 生成安全Token
```bash
# 方法1: 使用openssl生成随机token
TOKEN="MCU_PILOT_$(openssl rand -hex 16)"
echo "Generated token: $TOKEN"

# 方法2: 使用uuidgen
TOKEN="MCU_PILOT_$(uuidgen | tr -d '-')"
echo "Generated token: $TOKEN"

# 方法3: 使用Python生成
python3 -c "import secrets; print('MCU_PILOT_' + secrets.token_hex(16))"
```

### 更新服务器Token
```bash
# 1. 连接到新加坡服务器
ssh root@8.219.74.61

# 2. 更新.env文件
cd /opt/mcu-copilot
vi backend/.env

# 3. 更新API_TOKEN行
# API_TOKEN=your-new-secure-token-here

# 4. 重启服务
cd backend/deploy/docker
docker-compose restart

# 5. 验证新token
curl -H "Authorization: Bearer your-new-secure-token-here" \
     http://localhost:8000/auth/me
```

## 👥 种子用户管理

### Token分发流程

1. **申请阶段**
   - 用户通过安全渠道申请访问权限
   - 验证用户身份和使用目的
   - 记录用户信息和联系方式

2. **Token生成**
   - 为每个用户生成唯一的token（如果需要个人化）
   - 或者使用统一的种子用户token
   - 记录token分发记录

3. **安全分发**
   - 通过加密邮件发送
   - 或者通过安全的即时通讯工具
   - 避免在公开平台或不安全渠道发送

4. **使用指导**
   - 发送详细的API使用指南
   - 提供技术支持联系方式
   - 强调token安全保管

### Token信息模板

发送给种子用户的信息模板：

```
主题：MCU-Copilot API访问权限

亲爱的 [用户名]，

感谢您参与MCU-Copilot的种子用户测试！

🔑 您的API访问信息：
- API地址: http://8.219.74.61:8000
- 认证Token: [SECURE_TOKEN_HERE]
- 服务器位置: 阿里云新加坡

📖 使用指南：
1. 详细文档请参考：https://github.com/IronManZ/mcu-copilot/blob/main/backend/deploy/SEED_USER_GUIDE.md
2. 在所有API请求中添加Header: Authorization: Bearer [您的TOKEN]
3. 技术支持邮箱: [support@your-domain.com]

🚨 安全提醒：
- 请妥善保管您的token，不要分享给他人
- 不要在公开场所展示包含token的代码
- 如果token泄露，请立即联系我们更换

🧪 快速测试：
curl -H "Authorization: Bearer [您的TOKEN]" http://8.219.74.61:8000/health

祝测试愉快！
MCU-Copilot团队
```

## 📊 Token使用监控

### 日志监控脚本

```bash
# 创建token使用监控脚本
cat > /opt/mcu-copilot/scripts/token_monitor.sh << 'EOF'
#!/bin/bash

LOG_FILE="/opt/mcu-copilot/logs/token_usage_$(date +%Y%m%d).log"
ALERT_EMAIL="admin@your-domain.com"

# 监控异常使用
check_token_usage() {
    # 检查API调用频率
    current_hour=$(date +%H)
    request_count=$(grep "$(date +%Y-%m-%d)" /opt/mcu-copilot/logs/*.log | grep "Authorization" | wc -l)

    if [ $request_count -gt 1000 ]; then
        echo "$(date): High API usage detected: $request_count requests" >> $LOG_FILE
        # 可以添加邮件告警
    fi

    # 检查无效token尝试
    invalid_attempts=$(grep "401" /opt/mcu-copilot/logs/*.log | grep "$(date +%Y-%m-%d)" | wc -l)
    if [ $invalid_attempts -gt 50 ]; then
        echo "$(date): High invalid token attempts: $invalid_attempts" >> $LOG_FILE
    fi
}

check_token_usage
EOF

chmod +x /opt/mcu-copilot/scripts/token_monitor.sh

# 添加到定时任务
echo "0 * * * * /opt/mcu-copilot/scripts/token_monitor.sh" | crontab -
```

## 🔄 Token轮换计划

### 定期轮换流程

1. **轮换周期**: 建议每3-6个月轮换一次
2. **通知用户**: 提前7天通知所有用户
3. **并行期**: 新旧token并行有效7天
4. **完全切换**: 禁用旧token，仅使用新token

### 轮换脚本模板

```bash
#!/bin/bash
# Token轮换脚本

NEW_TOKEN="MCU_PILOT_$(openssl rand -hex 16)"
OLD_TOKEN_FILE="/tmp/old_token.txt"

echo "Starting token rotation..."
echo "New token: $NEW_TOKEN"

# 保存当前token
grep "API_TOKEN=" /opt/mcu-copilot/backend/.env > $OLD_TOKEN_FILE

# 更新配置文件
sed -i "s/API_TOKEN=.*/API_TOKEN=$NEW_TOKEN/" /opt/mcu-copilot/backend/.env

# 重启服务
cd /opt/mcu-copilot/backend/deploy/docker
docker-compose restart

echo "Token rotation completed!"
echo "Please notify all seed users of the new token: $NEW_TOKEN"
```

## 📞 紧急响应

### Token泄露处理

如果发现token泄露：

1. **立即轮换** - 生成新token并更新服务器
2. **通知用户** - 通过安全渠道通知所有用户
3. **监控访问** - 检查是否有异常访问行为
4. **评估影响** - 确定泄露范围和潜在影响
5. **改进措施** - 优化安全流程防止再次发生

### 联系方式

- **紧急联系**: [emergency@your-domain.com]
- **技术支持**: [tech-support@your-domain.com]
- **GitHub Issues**: https://github.com/IronManZ/mcu-copilot/issues

---

🔒 **安全是我们的首要任务，感谢您的配合！**