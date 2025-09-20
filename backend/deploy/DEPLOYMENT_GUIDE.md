# MCU-Copilot 后端服务部署指南

## 📋 概述

本指南提供 MCU-Copilot 后端服务在云服务器上的完整部署步骤，支持阿里云ECS和AWS EC2。

## 🎯 部署目标服务器

### 阿里云ECS新加坡
- **服务器IP**: `8.219.74.61`
- **地理位置**: 新加坡（ap-southeast-1）
- **优势**: 无需代理访问Gemini API，低延迟，网络稳定
- **配置**: 2核4GB内存，40GB系统盘
- **系统**: Ubuntu 20.04 LTS
- **GitHub仓库**: https://github.com/IronManZ/mcu-copilot

## 🚀 快速部署（推荐）

### 方法一：Docker部署

```bash
# 1. 连接到新加坡服务器
ssh root@8.219.74.61

# 2. 下载并运行环境准备脚本
curl -fsSL https://raw.githubusercontent.com/IronManZ/mcu-copilot/main/backend/deploy/scripts/setup.sh -o setup.sh
chmod +x setup.sh
sudo ./setup.sh

# 3. 克隆MCU-Copilot代码库
cd /opt/mcu-copilot
git clone https://github.com/IronManZ/mcu-copilot.git .

# 4. 配置环境变量
cp backend/.env.example backend/.env
vi backend/.env  # 配置您的Qianwen和Gemini API keys

# 5. 启动服务
cd backend/deploy/docker
docker-compose up -d

# 6. 检查服务状态
docker-compose ps
curl http://localhost:8000/health
```

### 方法二：本地部署

```bash
# 1-3步同上

# 4. 运行本地部署脚本
chmod +x backend/deploy/scripts/local-deploy.sh
sudo backend/deploy/scripts/local-deploy.sh

# 5. 检查服务
systemctl status mcu-copilot
curl http://localhost:8000/health
```

## 📝 详细步骤

### 步骤1: 服务器准备

#### 阿里云ECS设置
1. **购买ECS实例**
   - 地域：根据目标用户选择
   - 实例规格：ecs.s6-c1m2.medium (2核4GB)
   - 镜像：Ubuntu 20.04 64位
   - 系统盘：40GB ESSD云盘
   - 网络：默认VPC，分配公网IP

2. **安全组配置**
   ```bash
   # 允许的端口
   22   (SSH)
   80   (HTTP)
   443  (HTTPS)
   8000 (API服务，可选)
   ```

3. **连接服务器**
   ```bash
   ssh root@8.219.74.61
   ```

#### AWS EC2设置
1. **启动EC2实例**
   - AMI：Ubuntu Server 20.04 LTS
   - 实例类型：t3.medium
   - VPC：默认VPC
   - 安全组：允许22, 80, 443端口
   - 密钥对：创建新密钥对

2. **连接服务器**
   ```bash
   ssh -i your-key.pem ubuntu@your-server-ip
   sudo su  # 切换到root
   ```

### 步骤2: 系统环境准备

运行自动化安装脚本：

```bash
curl -fsSL https://raw.githubusercontent.com/IronManZ/mcu-copilot/main/backend/deploy/scripts/setup.sh -o setup.sh
chmod +x setup.sh
./setup.sh
```

或手动安装：

```bash
# 更新系统
apt update && apt upgrade -y
apt install -y curl wget git unzip nginx certbot python3-certbot-nginx

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 创建应用用户
useradd -m -s /bin/bash mcucopilot
usermod -aG docker mcucopilot
mkdir -p /opt/mcu-copilot
chown mcucopilot:mcucopilot /opt/mcu-copilot
```

### 步骤3: 部署应用

```bash
# 切换到应用目录
cd /opt/mcu-copilot

# 克隆MCU-Copilot代码库
git clone https://github.com/IronManZ/mcu-copilot.git .

# 配置环境变量
cp backend/.env.example backend/.env

# 编辑配置文件
vi backend/.env
```

#### 关键环境变量配置

```bash
# .env 文件内容
QIANWEN_APIKEY=your-qianwen-api-key
GEMINI_APIKEY=your-gemini-api-key

# JWT认证
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-32-chars-long
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# 种子用户Token
API_TOKEN=mcu-copilot-prod-token-2025

# 生产环境配置
DEBUG=false
HOST=0.0.0.0
PORT=8000

# CORS配置（新加坡服务器）
ALLOWED_ORIGINS=http://8.219.74.61:8000,https://8.219.74.61:8000
```

### 步骤4: 启动服务

#### Docker方式：
```bash
cd backend/deploy/docker
docker-compose up -d

# 检查状态
docker-compose ps
docker-compose logs -f
```

#### 本地方式：
```bash
chmod +x backend/deploy/scripts/local-deploy.sh
./backend/deploy/scripts/local-deploy.sh

# 检查状态
systemctl status mcu-copilot
journalctl -u mcu-copilot -f
```

### 步骤5: 配置Nginx反向代理

```bash
# 创建Nginx配置
vi /etc/nginx/sites-available/mcu-copilot
```

配置内容：
```nginx
server {
    listen 80;
    server_name 8.219.74.61;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

```bash
# 启用站点
ln -s /etc/nginx/sites-available/mcu-copilot /etc/nginx/sites-enabled/
nginx -t  # 测试配置
systemctl reload nginx
```

### 步骤6: 配置SSL证书（可选但推荐）

```bash
# 使用Let's Encrypt免费证书
certbot --nginx -d your-domain.com

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

## 🧪 测试部署

### 基础健康检查
```bash
# 服务健康检查
curl http://localhost:8000/health

# 通过公网IP访问
curl http://8.219.74.61/health
```

### 认证测试
```bash
# 测试固定Token认证
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "控制LED闪烁"}' \
     http://8.219.74.61:8000/compile

# 生成JWT Token
curl -X POST -H "Content-Type: application/json" \
     -d '{"user_id": "test_user", "purpose": "api_test"}' \
     http://8.219.74.61:8000/auth/token

# 使用JWT Token测试
curl -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
     http://8.219.74.61:8000/auth/me
```

## 👥 种子用户使用指南

### 获取访问权限
1. **固定Token方式**（推荐用于种子测试）
   - Token: `[由项目管理员私下提供]`
   - 在所有API请求中添加Header: `Authorization: Bearer YOUR_TOKEN_HERE`
   - 📧 **获取Token**: 请联系项目管理员获取您专用的访问token

2. **动态JWT Token方式**
   - 首先调用 `/auth/token` 获取临时token
   - 使用临时token访问API

### API调用示例

```bash
# 1. 健康检查
curl http://8.219.74.61:8000/health

# 2. 编译ZH5001汇编代码
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "requirement": "控制P03引脚LED闪烁，500ms开500ms关"
     }' \
     http://8.219.74.61:8000/compile?use_gemini=true

# 3. 检查认证状态
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://8.219.74.61:8000/auth/me

# 4. ZH5001编译器信息
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://8.219.74.61:8000/zh5001/info
```

## 🔧 运维管理

### 日志查看
```bash
# Docker方式
docker-compose logs -f mcu-copilot-backend

# Systemd方式
journalctl -u mcu-copilot -f

# 应用日志
tail -f /opt/mcu-copilot/logs/service_$(date +%Y%m%d).log
```

### 服务管理
```bash
# Docker方式
docker-compose stop    # 停止
docker-compose start   # 启动
docker-compose restart # 重启
docker-compose pull    # 更新镜像

# Systemd方式
systemctl stop mcu-copilot     # 停止
systemctl start mcu-copilot    # 启动
systemctl restart mcu-copilot  # 重启
systemctl reload mcu-copilot   # 重载配置
```

### 更新部署
```bash
cd /opt/mcu-copilot

# 更新代码
git pull origin main

# Docker方式更新
cd deploy/docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Systemd方式更新
systemctl restart mcu-copilot
```

### 监控和备份
```bash
# 监控脚本示例
#!/bin/bash
# /opt/mcu-copilot/scripts/monitor.sh

while true; do
    if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "$(date): Service is down, restarting..."
        systemctl restart mcu-copilot
    fi
    sleep 60
done

# 设置定时任务
echo "*/5 * * * * /opt/mcu-copilot/scripts/monitor.sh" | crontab -

# 日志备份
echo "0 2 * * * tar -czf /opt/backups/logs-$(date +%Y%m%d).tar.gz /opt/mcu-copilot/logs" | crontab -
```

## 🛡️ 安全建议

1. **防火墙配置**
   ```bash
   ufw enable
   ufw allow ssh
   ufw allow 'Nginx Full'
   # 如果直接暴露API端口
   ufw allow 8000
   ```

2. **定期更新**
   - 定期更新系统包和Docker镜像
   - 监控安全补丁

3. **访问控制**
   - 使用强密码和密钥认证
   - 定期轮换API tokens
   - 考虑IP白名单

4. **备份策略**
   - 定期备份配置文件和日志
   - 数据库备份（如果使用）

## 🐛 故障排查

### 常见问题

1. **服务无法启动**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :8000

   # 检查环境变量
   cat .env

   # 检查依赖
   pip list | grep fastapi
   ```

2. **API调用失败**
   ```bash
   # 检查认证token
   curl -H "Authorization: Bearer your-token" \
        https://your-domain.com/auth/check

   # 检查API key配置
   grep -i api .env
   ```

3. **Gemini API无法访问**
   ```bash
   # 测试网络连通性
   curl https://generativelanguage.googleapis.com

   # 检查代理设置
   env | grep -i proxy
   ```

## 📞 支持和联系

如果遇到部署问题，请提供：
1. 服务器系统信息：`cat /etc/os-release`
2. 错误日志：相关的错误信息
3. 配置信息：`.env`文件内容（隐藏敏感信息）
4. 网络环境：服务器地理位置和网络情况

---

## 🎉 部署完成检查清单

- [ ] 服务器环境准备完成
- [ ] Docker/Python环境安装成功
- [ ] 代码库克隆完成
- [ ] 环境变量配置正确
- [ ] 服务启动成功
- [ ] 健康检查通过
- [ ] Nginx代理配置（可选）
- [ ] SSL证书配置（可选）
- [ ] API认证测试成功
- [ ] 监控和日志配置
- [ ] 防火墙和安全配置

完成以上检查清单后，您的MCU-Copilot后端服务就可以为种子用户提供稳定的API服务了！