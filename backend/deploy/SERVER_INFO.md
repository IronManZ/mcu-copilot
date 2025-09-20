# MCU-Copilot 服务器部署信息

## 🌏 生产服务器

### 新加坡节点 (主节点)
- **服务器IP**: `8.219.74.61`
- **服务商**: 阿里云ECS
- **地理位置**: 新加坡 (ap-southeast-1)
- **配置**: 2核4GB内存，40GB系统盘
- **系统**: Ubuntu 20.04 LTS
- **API地址**: `http://8.219.74.61:8000`

### 网络优势
- ✅ 无需代理访问Gemini API
- ✅ 低延迟连接到Google服务
- ✅ 稳定的国际网络环境
- ✅ 24/7运行保障

## 🔐 种子用户访问信息

### 认证配置
- **认证方式**: Bearer Token
- **种子用户Token**: `[由项目管理员私下分发]`
- **Token类型**: 固定Token (长期有效)
- **安全说明**: Token不在公开文档中显示，仅通过私密渠道分发

### API端点
```
基础URL: http://8.219.74.61:8000

主要端点:
GET  /health              - 健康检查 (无需认证)
GET  /auth/me            - 用户认证验证
POST /compile            - 完整编译流程 (自然语言→汇编→机器码)
POST /nlp-to-assembly    - 自然语言转汇编
POST /assemble           - 汇编代码编译
GET  /zh5001/info        - ZH5001编译器信息
POST /zh5001/compile     - ZH5001直接编译
POST /zh5001/validate    - 汇编代码验证
```

## 📊 服务状态监控

### 实时状态检查
```bash
# 服务健康检查
curl http://8.219.74.61:8000/health

# 认证状态检查
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://8.219.74.61:8000/auth/me

# 编译器信息
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://8.219.74.61:8000/zh5001/info
```

### 服务可用性
- **正常运行时间**: 99.9%目标
- **响应时间**: < 30秒 (代码生成)
- **并发支持**: 多用户同时访问
- **限流策略**: 建议每分钟不超过30次请求

## 🔧 技术架构

### 部署方式
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx (可选)
- **进程管理**: Docker容器自动重启
- **日志管理**: 容器日志 + 应用日志

### 核心组件
- **Web框架**: FastAPI (Python)
- **AI模型**:
  - 通义千问 (Qwen-Turbo)
  - Gemini 1.5-Flash
- **编译器**: ZH5001汇编编译器
- **认证**: JWT + 固定Token混合认证

## 📚 文档资源

### 部署文档
- [完整部署指南](./DEPLOYMENT_GUIDE.md) - 详细的服务器部署步骤
- [快速部署](./QUICK_DEPLOY.md) - 一键部署脚本和快速开始
- [种子用户指南](./SEED_USER_GUIDE.md) - API使用说明和示例

### 脚本工具
- `singapore_deploy.sh` - 新加坡服务器一键部署脚本
- `seed_user_test.sh` - API功能测试脚本
- `setup.sh` - 服务器环境准备脚本
- `local-deploy.sh` - 本地部署脚本

## 🎯 种子用户测试场景

### 基础功能测试
1. **LED控制**: 简单的引脚输出控制
2. **按键检测**: 数字输入读取和处理
3. **定时控制**: 延时和定时器应用
4. **模拟量处理**: ADC读取和阈值判断

### 中级功能测试
1. **跑马灯**: 多LED循环控制
2. **按键防抖**: 复杂的输入处理
3. **状态机**: 交通灯等多状态系统
4. **数码管显示**: 显示驱动和查表

### 高级功能测试
1. **通信协议**: 串口、I2C、SPI
2. **中断处理**: 外部中断和定时中断
3. **PWM控制**: 脉宽调制输出
4. **复合系统**: 多功能综合应用

## 📞 技术支持

### 问题反馈渠道
- **GitHub Issues**: https://github.com/IronManZ/mcu-copilot/issues
- **技术文档**: 项目Wiki和文档目录
- **代码仓库**: https://github.com/IronManZ/mcu-copilot

### 常见问题解答
1. **API调用失败**: 检查认证token和网络连接
2. **编译错误**: 查看返回的错误信息和建议
3. **响应超时**: 复杂需求可能需要更长时间
4. **功能限制**: 参考ZH5001指令集文档

---

🚀 **服务器已就绪，开始您的MCU智能开发体验！**