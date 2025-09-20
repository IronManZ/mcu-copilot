# ZH5001 FPGA模拟器完整技术规范

## 1. 系统架构概述

### 1.1 模拟器本质
ZH5001 FPGA模拟器是一个基于FPGA硬件实现的完整单片机仿真系统，它在FPGA内部用硬件描述语言(Verilog/VHDL)重建了ZH5001单片机的所有功能模块，实现了指令级精确的硬件仿真。

### 1.2 核心价值
- **硬件级仿真**：不是软件模拟，而是真实的硬件重现
- **实时性能**：具备与真实ZH5001相同的时序特性
- **完整兼容**：100%兼容ZH5001的指令集和硬件特性
- **调试便利**：提供丰富的可视化调试接口

## 2. 硬件架构详解

### 2.1 FPGA核心模块 (U21)
```
FPGA内部实现模块：
├── ZH5001_CPU_Core          # CPU核心逻辑
│   ├── Instruction_Decoder  # 指令解码器
│   ├── ALU                 # 算术逻辑单元
│   ├── Register_File       # 寄存器组(R0,R1,PC,FLAG)
│   └── Control_Unit        # 控制单元
├── Program_Memory          # 程序存储器 1K×10bit
├── Data_Memory             # 数据存储器 48×16bit
├── IO_Controller           # IO端口控制器
├── Timer_Module            # 定时器模块
├── ADC_Controller          # ADC控制器
└── Special_Function_Regs   # 特殊功能寄存器
```

### 2.2 外部接口系统

#### 2.2.1 IO端口映射 (P00-P13, 14个端口)
每个IO端口的完整信号链：

```
ZH5001虚拟IO → FPGA引脚 → 电平转换 → 外部接口

具体映射：
ZH5001.P00 → FPGA-P00 → U1(缓冲器) → 外部P00
ZH5001.P01 → FPGA-P01 → U2(缓冲器) → 外部P01
...
ZH5001.P13 → FPGA-P13 → U14(缓冲器) → 外部P13
```

#### 2.2.2 三态控制机制
```
每个IO端口控制信号：
- FPGA-P[n]-I: 内部数据输出到外部
- FPGA-P[n]EN: 输出使能控制
- P[n]: 外部双向数据线

控制逻辑：
当FPGA-P[n]EN = 0: 端口为高阻态(输入模式)
当FPGA-P[n]EN = 1: 端口输出FPGA-P[n]-I的值
```

### 2.3 模拟信号处理系统

#### 2.3.1 ADC模拟器架构
```
外部模拟信号 → 多路复用器 → 信号调理 → ADC转换 → FPGA数字信号

详细信号流：
8路电位器 → DG408(8选1) → MCP6022(运放) → ADC → FPGA处理
     ↑              ↑              ↑           ↑
  ADCCHANNAL0-7  ADCADRA0-2选择   信号调理    ADC2FPGA
```

#### 2.3.2 ADC地址解码
```
ADCADRA2 ADCADRA1 ADCADRA0 → 选择通道
   0        0        0     → ADCCHANNAL0
   0        0        1     → ADCCHANNAL1
   0        1        0     → ADCCHANNAL2
   0        1        1     → ADCCHANNAL3
   1        0        0     → ADCCHANNAL4
   1        0        1     → ADCCHANNAL5
   1        1        0     → ADCCHANNAL6
   1        1        1     → ADCCHANNAL7
```

### 2.4 用户交互系统

#### 2.4.1 输入系统 (按键SW1-SW14)
```
物理按键 → 防抖电路 → FPGA输入

每个按键电路：
按键开关 → 上拉电阻(10k) → 防抖电容(100nF) → FPGA输入引脚

逻辑状态：
按键未按下: 高电平(+5V)
按键按下: 低电平(GND)
```

#### 2.4.2 输出显示系统
```
FPGA输出 → 限流电阻 → LED指示灯
FPGA输出 → NMOS驱动 → 7段数码管

LED控制：
FPGA输出高电平 → LED点亮
FPGA输出低电平 → LED熄灭

数码管控制：
段码输出: LED0-A ~ LED7-DP (8位段码)
位选输出: LED8-N1, LED9-N1 (2位选择)
```

## 3. ZH5001单片机在FPGA中的实现

### 3.1 内存映射在FPGA中的实现
```
ZH5001内存空间 → FPGA内部RAM映射：

用户数据RAM (地址0-47):
- 实现为48个16位RAM单元
- 每个地址对应一个16位寄存器
- 支持随机读写访问

特殊功能寄存器 (地址48-63):
地址48: SYSREG    → FPGA内部系统寄存器
地址49: IOSET0    → IO端口配置寄存器0
地址50: IOSET1    → IO端口配置寄存器1
地址51: IO        → IO端口数据寄存器
地址52: TM0_REG   → 定时器0寄存器
地址53: TM1_REG   → 定时器1寄存器
地址54: TM2_REG   → 定时器2寄存器
地址55: TMCT      → 定时器控制寄存器
地址56: TMCT2     → 定时器控制寄存器2
地址57: ADC_REG   → ADC控制寄存器
地址58: PFC_PDC   → 功率因数控制寄存器
地址59: COM_REG   → 通信寄存器
地址60: TX_DAT    → 发送数据寄存器
地址61: RX_DAT    → 接收数据寄存器

程序存储器 (1K×10位):
- 实现为1024个10位ROM/RAM
- 存储编译后的机器码
- 支持程序下载和执行
```

### 3.2 指令执行流水线
```
FPGA中的指令执行周期：

周期1: 取指令 (Instruction Fetch)
- PC → 程序存储器地址
- 读取10位指令码

周期2: 指令解码 (Instruction Decode)  
- 解码10位指令
- 确定操作类型和操作数

周期3: 执行 (Execute)
- ALU运算或数据传输
- 更新寄存器和标志位

周期4: 写回 (Write Back)
- 结果写入目标寄存器
- PC更新指向下一条指令
```

## 4. 外设功能实现

### 4.1 IO端口控制器
```verilog
// FPGA内部IO控制器伪代码
module IO_Controller (
    input clk,
    input [5:0] address,        // 地址总线
    input [15:0] data_in,       // 数据输入
    output [15:0] data_out,     // 数据输出
    input write_enable,         // 写使能
    output [13:0] port_out,     // 14个IO端口输出
    input [13:0] port_in,       // 14个IO端口输入
    output [13:0] port_enable   // 14个IO端口使能
);

// 当访问地址51(IO寄存器)时的行为
always @(posedge clk) begin
    if (write_enable && address == 6'd51) begin
        port_out <= data_in[13:0];    // 写入数据到端口
        port_enable <= ioset0_reg;    // 根据配置决定方向
    end
end
```

### 4.2 ADC控制器
```verilog
// ADC控制器伪代码
module ADC_Controller (
    input clk,
    input [5:0] address,
    input [15:0] data_in,
    output [15:0] data_out,
    input write_enable,
    output [2:0] adc_address,   // ADC通道选择
    output adc_enable,          // ADC使能
    input [9:0] adc_data        // ADC转换结果
);

// 当访问地址57(ADC_REG)时的行为
always @(posedge clk) begin
    if (write_enable && address == 6'd57) begin
        adc_address <= data_in[2:0];  // 设置ADC通道
        adc_enable <= data_in[3];     // 启动ADC转换
    end
end
```

## 5. 程序下载和执行流程

### 5.1 程序下载过程
```
PC端编译器 → USB串口 → CH340E → FPGA → 程序存储器

步骤详解：
1. PC端汇编编译器生成机器码
2. 通过USB发送HEX文件到FPGA
3. FPGA接收并解析HEX格式
4. 将机器码写入程序存储器
5. 重置CPU开始执行程序
```

### 5.2 实时调试机制
```
FPGA内部调试信号 → IO端口 → 外部LED显示

调试信息包括：
- 当前PC值 → 通过数码管显示
- 寄存器状态 → 通过LED指示
- IO端口状态 → 通过LED实时显示
- 标志位状态 → 通过特定LED显示
```

## 6. 系统时序特性

### 6.1 时钟系统
```
外部晶振 → FPGA PLL → 内部时钟分配

时钟分配：
- 主时钟: 25MHz (模拟ZH5001主频)
- ADC时钟: 1MHz (ADC采样时钟)
- 串口时钟: 波特率相关时钟
- 显示刷新时钟: 1kHz (数码管扫描)
```

### 6.2 时序约束
```
指令执行时序(与真实ZH5001完全一致)：
- 单周期指令: 1个时钟周期 (40ns @ 25MHz)
- LDINS指令: 2个时钟周期 (80ns @ 25MHz)  
- JUMP指令: 3个时钟周期 (120ns @ 25MHz)
```

## 7. 调试和测试接口

### 7.1 实时监控能力
```
可监控的信号：
- CPU内部寄存器 (R0, R1, PC, FLAG)
- 内存内容 (数据RAM 0-47)
- IO端口状态 (P00-P13)
- 特殊功能寄存器状态
- 指令执行历史
```

### 7.2 交互控制能力  
```
可控制的操作：
- 单步执行 (Step by Step)
- 断点设置 (Breakpoint)
- 内存修改 (Memory Edit)
- 寄存器修改 (Register Edit)
- 复位操作 (Reset)
```

## 8. 与ZH5001真实芯片的对比

### 8.1 完全兼容的特性
- ✅ 指令集100%兼容
- ✅ 内存映射完全一致
- ✅ 时序特性精确匹配
- ✅ IO端口行为一致
- ✅ 中断和定时器功能

### 8.2 模拟器增强特性
- 🔥 实时调试能力
- 🔥 状态可视化显示
- 🔥 单步执行和断点
- 🔥 内存实时监控
- 🔥 USB程序下载

### 8.3 物理限制
- ⚠️ 无真实模拟信号(通过电位器模拟)
- ⚠️ IO驱动能力有限(受FPGA限制)
- ⚠️ 功耗特性不同(FPGA vs 真实芯片)

## 9. 开发者使用指南

### 9.1 典型开发流程
```
1. 编写ZH5001汇编代码
2. 使用编译器生成HEX文件
3. 通过USB下载到FPGA模拟器
4. 运行程序并观察LED/数码管输出
5. 使用按键模拟外部输入
6. 通过串口监控内部状态
7. 调试和优化代码
```

### 9.2 硬件操作说明
```
开发板使用：
- 上电: 连接USB Type-C
- 程序下载: 通过USB串口
- 输入测试: 按下SW1-SW14按键
- 输出观察: 观察LED1-LED15状态
- 模拟输入: 调节8个电位器
- 数码管显示: 观察2位数码管
```

## 10. 技术规格总结

| 特性 | ZH5001真实芯片 | FPGA模拟器 |
|------|---------------|------------|
| 指令集 | 40条RISC指令 | 完全兼容 |
| 程序存储 | 1K×10bit OTP | 1K×10bit RAM |
| 数据存储 | 48×16bit SRAM | 48×16bit RAM |
| IO端口 | 14个 | 14个(增强调试) |
| 主频 | 最高25MHz | 25MHz |
| 封装 | 实际芯片封装 | FPGA开发板 |
| 调试能力 | 有限 | 全面增强 |
| 开发便利性 | 需要编程器 | USB直接下载 |

这个FPGA模拟器本质上是一个"增强版的ZH5001单片机"，它不仅具备了原芯片的所有功能，还增加了强大的调试和开发辅助功能，是学习、开发和验证ZH5001程序的理想平台。