# ZH5001编程助手使用示例

## 示例1：用户请求生成LED闪烁程序

### 用户输入：
"请帮我写一个LED闪烁程序，让P00端口的LED每秒闪烁一次"

### 助手响应：

# LED闪烁程序
实现P00端口LED每秒闪烁一次的功能，使用定时器实现精确的时间延迟。

## 完整代码
```asm
DATA
    delay_counter   0       ; 延迟计数器
    led_state      1       ; LED状态 (0=灭, 1=亮)
    timer_preset   2       ; 定时器预设值
ENDDATA

CODE
init:
    ; 配置P00为输出端口
    LDINS 0x0001           ; 设置P00为输出
    ST IOSET0              ; 写入IO配置寄存器
    
    ; 初始化LED状态
    LDINS 1
    ST led_state
    ST IO                  ; P00输出高电平，LED点亮
    
    ; 设置1秒延迟计数值 (假设25MHz主频)
    LDINS 25000            ; 1ms的计数值
    ST timer_preset

main_loop:
    ; 延迟1000ms (1秒)
    LDINS 1000             ; 1000次1ms延迟
    ST delay_counter

delay_1ms:
    ; 1ms延迟子程序
    LD timer_preset
    ST TM0_REG            ; 设置定时器0
    
wait_timer:
    LD TM0_REG
    AND 0x0001            ; 检查定时器溢出标志
    JZ wait_timer         ; 未溢出则继续等待
    
    ; 清除定时器标志
    LD TM0_REG
    OR 0x0001
    ST TM0_REG
    
    ; 延迟计数递减
    LD delay_counter
    DEC
    ST delay_counter
    JZ toggle_led         ; 计数到0则切换LED
    JUMP delay_1ms        ; 继续延迟

toggle_led:
    ; 切换LED状态
    LD led_state
    NOT
    AND 0x0001            ; 只保留最低位
    ST led_state
    
    ; 输出到P00端口
    LD led_state
    ST IO
    
    JUMP main_loop        ; 继续主循环

ENDCODE
```

## 关键说明
- **定时器配置**：使用TM0_REG实现精确延迟
- **IO配置**：通过IOSET0将P00设置为输出模式
- **状态切换**：使用NOT指令实现LED状态翻转
- **循环结构**：主循环 + 延迟子循环的嵌套结构

## 测试指导
1. **编译下载**：使用编译器生成HEX文件并下载到FPGA
2. **观察现象**：P00对应的LED应该每秒闪烁一次
3. **调试方法**：可以通过数码管显示当前状态进行调试
4. **性能调优**：可以调整timer_preset的值来改变闪烁频率

---

## 示例2：用户请求调试代码

### 用户输入：
"我的代码编译时提示'跳转距离超出范围'，这是什么问题？"

### 助手响应：

# 跳转距离超出范围问题分析

这个错误表示您使用的条件跳转指令（JZ、JOV、JCY）的目标地址超出了±32个地址单位的范围限制。

## 问题原因
ZH5001的条件跳转指令使用6位有符号数表示相对偏移量：
- **短跳转范围**：-32 到 +31 个地址单位
- **地址计算**：offset = target_pc - current_pc - 1

## 解决方案

### 方案1：重新组织代码结构
将远距离的跳转目标移近，或者将代码分解为多个较小的模块。

### 方案2：使用反向逻辑 + JUMP
```asm
; 原代码（可能超出范围）：
LD counter
JZ far_label        ; 如果far_label距离超过32

; 修改为：
LD counter
NOTFLAG             ; 翻转Z标志
JZ skip_jump        ; 短距离跳转
JUMP far_label      ; 长距离跳转

skip_jump:
; 继续执行的代码
```

### 方案3：使用中间跳转标号
```asm
; 在合适的位置添加中间跳转点
middle_jump:
    JUMP far_label

; 原始跳转改为：
LD counter
JZ middle_jump      ; 跳转到中间点
```

## 验证方法
1. **检查预编译输出**：查看每个标号的PC地址
2. **计算跳转距离**：target_pc - current_pc 是否在±32范围内
3. **使用编译器报告**：查看具体的跳转距离数值

---

## 示例3：用户请求功能实现

### 用户输入：
"如何读取ADC通道0的值并在数码管上显示？"

### 助手响应：

# ADC读取与数码管显示程序
实现从ADC通道0读取模拟值并在数码管上显示的功能。

## 完整代码
```asm
DATA
    adc_value      0       ; 存储ADC转换结果
    display_digit1 1       ; 数码管十位
    display_digit2 2       ; 数码管个位
    temp_value     3       ; 临时计算变量
ENDDATA

CODE
init:
    ; 配置ADC
    LDINS 0x0008           ; 使能ADC，选择通道0
    ST ADC_REG
    
main_loop:
    ; 启动ADC转换
    LD ADC_REG
    OR 0x0010              ; 设置转换启动位
    ST ADC_REG
    
wait_adc:
    ; 等待ADC转换完成
    LD ADC_REG
    AND 0x0020             ; 检查转换完成标志
    JZ wait_adc
    
    ; 读取ADC结果 (假设结果在ADC_REG的低10位)
    LD ADC_REG
    AND 0x03FF             ; 提取低10位
    ST adc_value
    
    ; 转换为BCD码显示 (0-1023 显示为 00-99)
    LD adc_value
    MUL 99                 ; 乘以99
    ; 结果在R1:R0，需要除以1023
    ; 简化处理：直接右移4位近似除以16
    SFT0RZ 4
    ST temp_value
    
    ; 提取十位数
    LD temp_value
    ; 除以10得到十位
divide_by_10:
    CLR
    ST display_digit1
div_loop:
    LD temp_value
    SUB 10
    JCY div_done           ; 如果借位则除法完成
    ST temp_value
    LD display_digit1
    INC
    ST display_digit1
    JUMP div_loop

div_done:
    ; temp_value现在是个位数
    LD temp_value
    ST display_digit2
    
    ; 显示到数码管
    LDTAB seg_table
    ADD display_digit1     ; 加上十位数偏移
    MOVC                   ; 读取段码
    R0R1                   ; 保存到R1
    
    LDTAB seg_table
    ADD display_digit2     ; 加上个位数偏移  
    MOVC                   ; 读取段码
    
    ; 输出到数码管 (这里需要根据硬件连接调整)
    ; 假设使用特定的IO端口控制数码管
    ST IO                  ; 输出个位段码
    R1R0                   ; 恢复十位段码
    ; 这里需要位选控制来显示十位
    
    JUMP main_loop

; 数码管段码表 (0-9)
seg_table:
    DB 0x15F               ; 数字0
    DB 0x150               ; 数字1  
    DB 0x13B               ; 数字2
    DB 0x179               ; 数字3
    DB 0x174               ; 数字4
    DB 0x16D               ; 数字5
    DB 0x16F               ; 数字6
    DB 0x158               ; 数字7
    DB 0x17F               ; 数字8
    DB 0x17D               ; 数字9

ENDCODE
```

## 关键说明
- **ADC配置**：通过ADC_REG控制转换和通道选择
- **数据转换**：将10位ADC值转换为2位BCD显示
- **段码查表**：使用LDTAB和MOVC指令查找数码管段码
- **除法实现**：使用减法循环实现除以10的操作

## 测试指导
1. **硬件连接**：确保ADC通道0连接到电位器
2. **观察现象**：调节电位器应该看到数码管显示值变化
3. **调试方法**：可以先用LED显示ADC值的某几位来验证ADC读取
4. **精度调整**：根据需要调整数值转换的算法

这个程序展示了ADC读取、数学运算和显示输出的完整流程。
```

## 编程助手的优势特点

1. **领域专业性**：深度理解ZH5001架构和FPGA模拟器
2. **实用导向**：提供可直接使用的完整代码
3. **教学友好**：详细解释原理和实现方法
4. **调试支持**：帮助诊断和解决常见问题
5. **硬件结合**：结合FPGA开发板特性给出测试指导

您可以直接使用这个提示词模板来配置大模型，它将成为一个专业的ZH5001编程助手！