# MCU-Copilot 新加坡服务器快速部署

## 🎯 服务器信息
- **IP地址**: `8.219.74.61`
- **位置**: 阿里云新加坡节点
- **仓库**: https://github.com/IronManZ/mcu-copilot

## 🚀 一键部署

### 方法1: 自动化脚本（推荐）
```bash
# 1. 下载并运行一键部署脚本
curl -fsSL https://raw.githubusercontent.com/IronManZ/mcu-copilot/main/backend/deploy/singapore_deploy.sh -o singapore_deploy.sh
chmod +x singapore_deploy.sh
./singapore_deploy.sh
```

### 方法2: 手动部署
```bash
# 1. 连接服务器
ssh root@8.219.74.61

# 2. 快速环境准备
curl -fsSL https://raw.githubusercontent.com/IronManZ/mcu-copilot/main/backend/deploy/scripts/setup.sh -o setup.sh
chmod +x setup.sh && ./setup.sh

# 3. 克隆代码
cd /opt/mcu-copilot
git clone https://github.com/IronManZ/mcu-copilot.git .

# 4. 配置环境变量
cp backend/.env.example backend/.env
vi backend/.env  # 配置您的API密钥

# 5. Docker启动
cd backend/deploy/docker
docker-compose up -d --build

# 6. 验证部署
curl http://localhost:8000/health
```

## 🔑 必要配置

在 `backend/.env` 文件中配置以下密钥：

```env
# LLM API Keys（必须配置）
QIANWEN_APIKEY=sk-your-qianwen-api-key-here
GEMINI_APIKEY=AIza-your-gemini-api-key-here

# JWT Authentication
JWT_SECRET_KEY=mcu-copilot-singapore-secret-2025
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# API Authentication (种子用户使用)
API_TOKEN=your-secure-seed-user-token-here

# Server Configuration
DEBUG=false
HOST=0.0.0.0
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=http://8.219.74.61:8000,https://8.219.74.61:8000
```

## 🧪 部署验证

### 基础健康检查
```bash
curl http://8.219.74.61:8000/health
# 期望响应: {"status": "ok"}
```

### 认证测试
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://8.219.74.61:8000/auth/me
```

### 编译功能测试
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "控制P03引脚LED闪烁"}' \
     http://8.219.74.61:8000/compile?use_gemini=true
```

### 完整测试套件
```bash
# 下载并运行测试脚本
curl -fsSL https://raw.githubusercontent.com/IronManZ/mcu-copilot/main/backend/deploy/seed_user_test.sh -o test.sh
chmod +x test.sh
./test.sh http://8.219.74.61:8000
```

## 📊 服务管理

### 查看服务状态
```bash
ssh root@8.219.74.61
cd /opt/mcu-copilot/backend/deploy/docker
docker-compose ps
```

### 查看日志
```bash
docker-compose logs -f
```

### 重启服务
```bash
docker-compose restart
```

### 更新代码
```bash
cd /opt/mcu-copilot
git pull origin main
cd backend/deploy/docker
docker-compose down
docker-compose up -d --build
```

## 🛠️ 故障排查

### 常见问题

1. **服务无法启动**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :8000

   # 检查Docker状态
   docker-compose ps
   docker-compose logs
   ```

2. **API调用401错误**
   - 确认token: `mcu-copilot-2025-seed-token`
   - 检查Header格式: `Authorization: Bearer mcu-copilot-2025-seed-token`

3. **编译失败**
   - 检查API密钥配置
   - 查看服务日志: `docker-compose logs -f`

4. **网络连接问题**
   ```bash
   # 检查防火墙设置
   ufw status

   # 检查端口监听
   ss -tulpn | grep :8000
   ```

## 🎉 种子用户信息

部署完成后，可以将以下信息提供给种子用户：

- **API地址**: `http://8.219.74.61:8000`
- **认证Token**: `mcu-copilot-2025-seed-token`
- **使用指南**: [SEED_USER_GUIDE.md](./SEED_USER_GUIDE.md)
- **GitHub仓库**: https://github.com/IronManZ/mcu-copilot

### 种子用户快速测试命令
```bash
# 健康检查
curl http://8.219.74.61:8000/health

# 编译测试
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "控制LED闪烁"}' \
     http://8.219.74.61:8000/compile?use_gemini=true
```

---

🇸🇬 **新加坡服务器已就绪，开始您的MCU开发之旅！** 🚀