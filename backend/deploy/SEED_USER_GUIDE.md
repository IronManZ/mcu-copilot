# MCU-Copilot 种子用户使用指南

## 🎯 快速开始

恭喜您成为MCU-Copilot的种子用户！本指南将帮助您快速上手使用API服务。

### 🔑 认证信息
- **API地址**: `http://8.219.74.61:80`
- **服务器位置**: 阿里云新加坡
- **认证Token**: `[由项目管理员私下提供]`
- **认证方式**: Bearer Token
- **GitHub仓库**: https://github.com/IronManZ/mcu-copilot

> ⚠️ **安全提醒**: 认证token是私密信息，不会在公开文档中显示。如需获取访问token，请联系项目管理员。

### 📋 使用步骤

1. **健康检查** - 确认服务运行正常
2. **认证测试** - 验证您的访问权限
3. **编译测试** - 生成您的第一个ZH5001汇编程序
4. **深入使用** - 探索更多功能

## 🚀 快速测试

### 1. 健康检查（无需认证）
```bash
curl http://8.219.74.61:80/health
```
**预期响应**:
```json
{"status": "ok"}
```

### 2. 认证测试
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://8.219.74.61:80/auth/me
```
**预期响应**:
```json
{
  "authenticated": true,
  "user_info": {
    "user_type": "seed_user",
    "token_type": "api_token",
    "authenticated": true
  },
  "message": "Authentication successful"
}
```

### 3. 编译测试
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "控制P03引脚LED闪烁，500ms开500ms关"}' \
     "http://8.219.74.61:80/compile?use_gemini=true"
```

## 📚 API 端点详解

### 认证端点

#### `GET /auth/me` - 获取用户信息
验证当前认证状态并返回用户信息。

**Headers**:
```
Authorization: Bearer YOUR_TOKEN_HERE
```

#### `POST /auth/token` - 生成JWT令牌
为特定用户生成动态JWT令牌（可选功能）。

**请求体**:
```json
{
  "user_id": "your_user_id",
  "purpose": "api_access"
}
```

### 编译端点

#### `POST /compile` - 完整编译流程
将自然语言需求转换为ZH5001汇编代码并编译为机器码。

**参数**:
- `use_gemini=true`: 使用Gemini模型（推荐）
- `use_gemini=false`: 使用通义千问模型

**请求体**:
```json
{
  "requirement": "您的功能需求描述"
}
```

**响应格式**:
```json
{
  "thought": "AI的思考过程",
  "assembly": "生成的汇编代码",
  "machine_code": ["机器码数组"],
  "filtered_assembly": "过滤后的汇编代码",
  "compile_error": null
}
```

#### `POST /nlp-to-assembly` - 自然语言转汇编
仅执行自然语言到汇编代码的转换，不进行编译。

#### `POST /assemble` - 汇编代码编译
将汇编代码编译为机器码。

**请求体**:
```json
{
  "assembly": "您的汇编代码"
}
```

### ZH5001编译器端点

#### `GET /zh5001/info` - 编译器信息
获取ZH5001编译器的详细信息和支持的指令集。

#### `POST /zh5001/validate` - 汇编验证
验证汇编代码的语法正确性。

**请求体**:
```json
{
  "assembly_code": "您的汇编代码"
}
```

#### `POST /zh5001/compile` - 直接编译
直接使用ZH5001编译器编译汇编代码。

## 🎮 实战示例

### 示例1: LED闪烁控制
```bash
curl -X POST \
     -H "Authorization: Bearer MCU_PILOT_3865d905aae1ccf8d09d07a7ee25e4cf" \
     -H "Content-Type: application/json" \
     -d '{
       "requirement": "控制P03引脚LED闪烁：500ms开，500ms关"
     }' \
     "http://8.219.74.61:80/compile?use_gemini=true"
```

### 示例2: 按键检测
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "requirement": "读取P01引脚按键状态，按下时P02引脚输出高电平"
     }' \
     "http://8.219.74.61:80/compile?use_gemini=true"
```

### 示例3: ADC模拟量读取
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "requirement": "读取ADC通道0模拟量，当值大于512时点亮P10 LED"
     }' \
     "http://8.219.74.61:80/compile?use_gemini=true"
```

### 示例4: 数码管显示
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "requirement": "数码管显示0-99循环计数，每秒递增1"
     }' \
     "http://8.219.74.61:80/compile?use_gemini=true"
```

## 🔧 功能特性

### 支持的需求类型
1. **GPIO控制**: LED控制、引脚输出
2. **输入检测**: 按键读取、开关状态
3. **模拟量处理**: ADC读取、阈值判断
4. **显示控制**: 数码管、LED阵列
5. **时序控制**: 延时、定时器、PWM
6. **通信功能**: 串口、I2C、SPI

### ZH5001微控制器特性
- **CPU架构**: 16位精简指令集
- **寄存器**: R0(累加器), R1(通用寄存器)
- **IO端口**: P00-P13 (14个IO引脚)
- **特殊寄存器**: IOSET0(49), IOSET1(50), IO(51), SYSREG(48)
- **指令集**: 支持30+条指令，包括算术、逻辑、跳转、移位等

### 代码生成质量
- **智能分析**: AI深度理解需求并生成优化代码
- **语法检查**: 自动验证汇编语法正确性
- **本地编译**: 集成完整ZH5001编译器
- **错误修正**: 多轮迭代自动修正编译错误
- **代码优化**: 生成高效、可读的汇编代码

## 📊 使用统计和限制

### 当前限制
- **请求频率**: 建议每分钟不超过30次请求
- **请求大小**: 每次需求描述建议不超过1000字符
- **并发连接**: 支持多用户并发访问
- **响应时间**: 通常5-30秒完成代码生成和编译

### 使用建议
1. **清晰描述**: 需求描述越清晰，生成的代码质量越高
2. **分步实现**: 复杂功能建议分步骤实现
3. **测试验证**: 生成的代码建议先仿真测试再实际使用
4. **反馈改进**: 遇到问题请及时反馈，帮助我们改进

## 🐛 常见问题

### Q1: API调用返回401错误
**A**: 检查Authorization头是否正确设置，确保使用正确的Bearer token格式：`Authorization: Bearer YOUR_TOKEN_HERE`

### Q2: 编译失败怎么办
**A**: 系统会自动重试修正，如果仍失败请检查需求描述是否清晰明确。

### Q3: 响应时间较长
**A**: AI代码生成需要时间，请耐心等待。复杂需求可能需要30秒以上。

### Q4: 生成的代码不符合预期
**A**: 请提供更详细的需求描述，包括具体的引脚定义、时序要求等。

## 📞 技术支持

### 问题反馈
如果遇到问题，请提供以下信息：
1. **错误信息**: 完整的错误响应
2. **请求内容**: 您发送的需求描述
3. **期望结果**: 您期望的功能效果
4. **使用场景**: 具体的应用场景

### 联系方式
- **邮箱**: support@mcu-copilot.com
- **问题反馈**: 通过issue tracker提交
- **技术交流**: 加入技术交流群

## 🎉 开始您的MCU开发之旅

现在您已经掌握了MCU-Copilot的基本使用方法，可以开始：

1. **尝试基础功能**: 从简单的LED控制开始
2. **探索复杂应用**: 逐步尝试更复杂的功能需求
3. **分享经验**: 与其他开发者分享使用心得
4. **提供反馈**: 帮助我们不断改进产品

祝您使用愉快！🚀