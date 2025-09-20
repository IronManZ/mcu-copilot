# MCU-Copilot 前端部署指南

## 🎯 部署概述

将MCU-Copilot React前端应用部署到阿里云服务器，通过Nginx提供静态文件服务和API代理。

## 📋 部署架构

```
用户浏览器 → Nginx:80 → 前端静态文件 (React SPA)
                    ↓ /api/* 请求
                    → FastAPI后端:8000
```

## 🚀 部署步骤

### 第1步：准备构建产物

在开发机器上执行：
```bash
# 进入前端目录
cd /Users/shanzhou/projects/yingneng/mcu-copilot/mcu-code-whisperer

# 安装依赖
npm install

# 构建生产版本
npm run build

# 检查构建产物
ls -la dist/
```

### 第2步：上传文件到服务器

```bash
# 方法1：使用rsync上传构建产物
rsync -avz --progress dist/ root@8.219.74.61:/opt/mcu-copilot/mcu-code-whisperer/dist/

# 方法2：使用scp上传
scp -r dist/ root@8.219.74.61:/opt/mcu-copilot/mcu-code-whisperer/

# 上传部署脚本和配置
scp backend/deploy/deploy-frontend.sh root@8.219.74.61:/opt/mcu-copilot/backend/deploy/
scp backend/deploy/nginx-frontend.conf root@8.219.74.61:/opt/mcu-copilot/backend/deploy/
```

### 第3步：服务器执行部署

SSH连接到服务器并执行部署：
```bash
# 连接服务器
ssh root@8.219.74.61

# 进入项目目录
cd /opt/mcu-copilot

# 执行前端部署脚本
chmod +x backend/deploy/deploy-frontend.sh
sudo backend/deploy/deploy-frontend.sh
```

## 🔧 配置说明

### Nginx配置重点

**静态文件服务**:
- 前端文件位置: `/opt/mcu-copilot/frontend/dist`
- 支持SPA路由: `try_files $uri $uri/ /index.html`
- 静态资源缓存: CSS/JS文件缓存1年

**API代理**:
- `/api/*` → `http://localhost:8000/`
- 兼容性代理: `/health`, `/auth/`, `/compile`, `/zh5001/`
- CORS处理: 支持跨域请求

### 环境变量配置

前端使用以下环境变量：
- `VITE_API_BASE_URL=/api` (生产环境使用相对路径)
- `VITE_API_TOKEN=MCU_PILOT_3865d905aae1ccf8d09d07a7ee25e4cf` (API认证)

## 🧪 部署验证

### 基础功能测试

```bash
# 1. 健康检查
curl http://8.219.74.61/health

# 2. 前端页面访问
curl -I http://8.219.74.61/

# 3. API代理测试
curl http://8.219.74.61/api/zh5001/info

# 4. 编译功能测试
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer MCU_PILOT_3865d905aae1ccf8d09d07a7ee25e4cf" \
     -d '{"requirement": "点亮P03 LED"}' \
     http://8.219.74.61/api/compile?use_gemini=true
```

### 浏览器测试

1. 访问 `http://8.219.74.61` 查看前端界面
2. 测试自然语言编译功能
3. 测试直接汇编编译功能
4. 检查所有API调用是否正常

## 📊 监控和日志

### Nginx日志位置

```bash
# 访问日志
tail -f /var/log/nginx/mcu-copilot.access.log

# 错误日志
tail -f /var/log/nginx/mcu-copilot.error.log

# 实时监控
tail -f /var/log/nginx/mcu-copilot.access.log | grep -E "(POST|GET) /"
```

### 后端服务监控

```bash
# Docker容器状态
cd /opt/mcu-copilot/backend/deploy/docker
docker-compose ps
docker-compose logs --tail=50

# 端口占用检查
netstat -tlnp | grep -E "(80|8000)"
```

## 🐛 常见问题排查

### 前端无法访问

1. **检查Nginx状态**: `systemctl status nginx`
2. **检查端口占用**: `netstat -tlnp | grep :80`
3. **检查文件权限**: `ls -la /opt/mcu-copilot/frontend/`
4. **查看错误日志**: `tail /var/log/nginx/error.log`

### API调用失败

1. **检查后端服务**: `docker-compose ps`
2. **检查API代理**: `curl http://localhost:8000/health`
3. **检查CORS配置**: 查看浏览器开发者工具网络面板
4. **验证token**: 确认API token配置正确

### 性能问题

1. **启用Gzip压缩**: Nginx配置中添加gzip相关设置
2. **CDN加速**: 考虑使用阿里云CDN加速静态资源
3. **缓存优化**: 调整静态资源缓存策略

## 🔄 更新部署

### 更新前端代码

```bash
# 本地重新构建
npm run build

# 上传新的构建产物
rsync -avz --progress dist/ root@8.219.74.61:/opt/mcu-copilot/frontend/dist/

# 服务器上清除缓存（如果需要）
ssh root@8.219.74.61 "systemctl reload nginx"
```

### 更新API配置

```bash
# 修改环境变量
ssh root@8.219.74.61
cd /opt/mcu-copilot
vi backend/.env

# 重启后端服务
cd backend/deploy/docker
docker-compose restart
```

## 🎉 部署成功标志

当以下条件都满足时，说明前端部署成功：

1. ✅ 浏览器能访问 `http://8.219.74.61` 并看到前端界面
2. ✅ 前端能正常调用API并获得响应
3. ✅ 自然语言编译功能正常工作
4. ✅ 直接汇编编译功能正常工作
5. ✅ Nginx日志显示正常的请求记录

恭喜！您的MCU-Copilot现在拥有了完整的Web界面！ 🚀