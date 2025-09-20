# MCU-Copilot API使用示例集合

## 📋 基础信息
- **API地址**: `http://8.219.74.61:80` (Nginx代理端口)
- **认证方式**: `Authorization: Bearer YOUR_TOKEN_HERE`
- **内容类型**: `Content-Type: application/json`

## 🚀 快速开始示例

### 健康检查（无需认证）
```bash
curl http://8.219.74.61:80/health
```

### 认证验证
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://8.219.74.61:80/auth/me
```

## 💡 LED控制示例

### 基础LED控制
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "点亮P03引脚LED"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### LED闪烁控制
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "控制P03引脚LED闪烁，每500ms切换一次状态"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### 多LED流水灯
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "P00-P03引脚流水灯效果，每个LED亮200ms"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

## 🔘 按键输入示例

### 按键检测
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "读取P01引脚按键，按下时点亮P02 LED"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### 按键切换
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "P01按键每次按下切换P03 LED的亮灭状态"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

## 📊 ADC模拟量示例

### ADC阈值检测
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "读取ADC通道0，当值大于512时点亮P10 LED"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### ADC多级指示
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "ADC值0-255点亮P00，256-511点亮P01，512-767点亮P02，768以上点亮P03"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

## 🔢 数码管显示示例

### 固定数字显示
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "数码管显示数字8"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### 数码管计数
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "数码管显示0-9循环计数，每秒递增1"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### 双位数码管
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "双位数码管显示00-99计数，每500ms递增"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

## ⏱️ 定时器示例

### 基础延时
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "程序启动1秒后点亮P03 LED"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### 定时切换
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "每3秒在P00-P03之间循环点亮一个LED"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

## 🔄 PWM示例

### PWM调光
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "P03引脚输出50%占空比PWM信号控制LED亮度"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### PWM呼吸灯
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "P03 LED呼吸灯效果，亮度从0%到100%再到0%循环变化"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

## 🔧 系统功能示例

### 看门狗
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "启用看门狗功能，定期喂狗防止系统复位"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### 中断处理
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "P01引脚外部中断，中断时切换P03 LED状态"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

## 📡 通信示例

### 串口输出
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "串口每秒输出Hello World"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### 数据采集上传
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "每10秒读取ADC值并通过串口发送"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

## 🎛️ 复合功能示例

### 智能夜灯
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "ADC检测光照强度，暗时自动点亮P03 LED，亮时关闭"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### 温度监控
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "ADC读取温度传感器，温度过高时P00红灯闪烁报警，正常时P01绿灯长亮"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### 简单状态机
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "P01按键切换三种模式：模式1全灯亮，模式2流水灯，模式3全灯闪烁"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

## 🧪 高级测试

### 性能测试
```bash
# 并发测试 - 发送多个简单请求
for i in {1..5}; do
  curl -X POST \
       -H "Authorization: Bearer YOUR_TOKEN_HERE" \
       -H "Content-Type: application/json" \
       -d '{"requirement": "点亮P0'$i' LED"}' \
       http://8.219.74.61:80/compile?use_gemini=true &
done
wait
```

### 复杂需求测试
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "设计一个交通灯系统：P00红灯30秒，P01黄灯5秒，P02绿灯25秒，循环运行。按P03按键可以切换到紧急模式：所有灯闪烁"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

## 📝 使用技巧

### 1. 清晰的需求描述
- ✅ 好：`控制P03引脚LED每500ms闪烁一次`
- ❌ 差：`让灯闪一下`

### 2. 指定具体引脚
- ✅ 好：`P01引脚按键检测，P03引脚LED输出`
- ❌ 差：`按键控制LED`

### 3. 明确时间参数
- ✅ 好：`延时1秒，PWM频率1kHz`
- ❌ 差：`延时一下，高频PWM`

### 4. 分步骤描述复杂功能
```bash
# 复杂功能可以分步实现
curl ... -d '{"requirement": "第一步：设置P00-P03为输出模式"}'
curl ... -d '{"requirement": "第二步：实现4位二进制计数显示"}'
```

## 🐛 错误处理示例

### 语法错误测试
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "这是一个无法实现的需求：控制不存在的P99引脚"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

### 无效认证测试
```bash
curl -X POST \
     -H "Authorization: Bearer invalid-token" \
     -H "Content-Type: application/json" \
     -d '{"requirement": "测试无效token"}' \
     http://8.219.74.61:80/compile?use_gemini=true
```

---

💡 **提示**:
- 复制这些示例时，请将 `YOUR_TOKEN_HERE` 替换为您的实际API token
- 复杂需求可能需要30秒以上的处理时间，请耐心等待
- 如果编译失败，系统会自动尝试修正，通常会在几次尝试后成功