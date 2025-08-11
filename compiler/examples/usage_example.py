#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZH5001编译器使用示例
演示如何使用编译器编译汇编代码
"""

from zh5001_compiler import ZH5001Compiler
import json

def example_led_blink():
    """LED闪烁程序示例"""
    code = """
DATA
    delay_count    0
    led_state      1
    port_addr      2
ENDDATA

CODE
main:
    ; 初始化LED状态
    LDINS 0x01      ; LED初始状态
    ST led_state
    
    ; 设置端口地址
    LDINS 51        ; 假设LED连接到端口51 (IO寄存器)
    ST port_addr

blink_loop:
    ; 输出LED状态到端口
    LD led_state
    ST port_addr    ; 写入端口寄存器
    
    ; 延时循环
    LDINS 1000      ; 延时计数值
    ST delay_count

delay_loop:
    LD delay_count
    DEC
    ST delay_count
    JZ toggle_led   ; 延时结束，切换LED
    JUMP delay_loop ; 继续延时

toggle_led:
    ; 切换LED状态
    LD led_state
    NOT             ; 取反
    AND 0x01        ; 只保留最低位
    ST led_state
    
    JUMP blink_loop ; 继续闪烁

ENDCODE
"""
    
    print("=== LED闪烁程序示例 ===")
    print("源代码:")
    print(code)
    
    compiler = ZH5001Compiler()
    
    if compiler.parse_text(code):
        print("✓ 解析成功")
        
        if compiler.precompile():
            print("✓ 预编译成功")
            
            if compiler.compile():
                print("✓ 编译成功")
                
                result = compiler.generate_output()
                print(f"\n编译结果:")
                print(f"- 变量: {len(result['variables'])} 个")
                print(f"- 标号: {len(result['labels'])} 个") 
                print(f"- 机器码: {len(result['machine_code'])} 条")
                
                # 显示变量表
                print(f"\n变量表:")
                for name, addr in result['variables'].items():
                    print(f"  {name}: 地址 {addr}")
                
                # 显示标号表
                print(f"\n标号表:")
                for name, pc in result['labels'].items():
                    print(f"  {name}: PC {pc}")
                
                # 显示前10条机器码
                print(f"\n机器码 (前10条):")
                for i, item in enumerate(result['machine_code'][:10]):
                    print(f"  PC{item['pc']:3d}: {item['binary']} (0x{item['hex']})")
                
                # 生成HEX文件内容
                hex_content = '\n'.join(result['hex_output'])
                print(f"\nHEX文件内容:")
                print(hex_content[:200] + "..." if len(hex_content) > 200 else hex_content)
                
                return result
            else:
                print("✗ 编译失败")
        else:
            print("✗ 预编译失败")
    else:
        print("✗ 解析失败")
    
    # 显示错误信息
    if compiler.errors:
        print("\n错误信息:")
        for error in compiler.errors:
            print(f"  {error}")
    
    return None

def example_math_operations():
    """数学运算示例"""
    code = """
DATA
    operand1    0
    operand2    1  
    sum         2
    product     3
    quotient    4
    remainder   5
ENDDATA

CODE
    ; 设置操作数
    LDINS 15
    ST operand1
    
    LDINS 4
    ST operand2
    
    ; 加法运算
    LD operand1
    ADD operand2
    ST sum
    
    ; 乘法运算
    LD operand1
    MUL operand2    ; 结果在R1:R0中
    ST product      ; 存储低位
    R1R0            ; R0 = R1 (高位)
    ; 这里可以存储高位到另一个变量
    
    ; 除法运算 (使用循环实现)
    CLR             ; 清零商
    ST quotient
    LD operand1     ; 被除数
    ST remainder    ; 余数

divide_loop:
    LD remainder
    SUB operand2    ; 减去除数
    JCY divide_done ; 如果产生借位说明除法完成
    
    ST remainder    ; 更新余数
    LD quotient     ; 商加1
    INC
    ST quotient
    
    JUMP divide_loop

divide_done:
    ; 除法完成，结果在quotient和remainder中
    NOP

ENDCODE
"""
    
    print("\n=== 数学运算示例 ===")
    print("计算 15 + 4, 15 * 4, 15 / 4")
    
    compiler = ZH5001Compiler()
    
    if compiler.parse_text(code) and compiler.precompile() and compiler.compile():
        result = compiler.generate_output()
        print("✓ 编译成功")
        
        print(f"\n生成了 {len(result['machine_code'])} 条机器码")
        print("主要操作的机器码:")
        
        # 查找关键指令
        for i, inst in enumerate(result['precompiled']):
            if inst['mnemonic'] in ['ADD', 'MUL', 'SUB'] and inst['operand']:
                print(f"  {inst['mnemonic']} {inst['operand']}: {result['machine_code'][i]['hex']}")
        
        return result
    else:
        print("✗ 编译失败")
        for error in compiler.errors:
            print(f"  {error}")
        return None

def example_pwm_control():
    """PWM控制示例 (使用ZH5001的定时器功能)"""
    code = """
DATA
    duty_cycle      0   ; 占空比值
    timer_period    1   ; 定时器周期
    current_count   2   ; 当前计数值
    pwm_output      3   ; PWM输出状态
ENDDATA

CODE
setup:
    ; 设置PWM参数
    LDINS 100       ; 定时器周期
    ST timer_period
    
    LDINS 30        ; 30% 占空比
    ST duty_cycle
    
    CLR             ; 初始化计数器
    ST current_count

pwm_loop:
    ; 计数器递增
    LD current_count
    INC
    ST current_count
    
    ; 检查是否达到周期
    LD current_count
    SUB timer_period
    JZ reset_counter
    
    ; 比较计数值和占空比
    LD current_count
    SUB duty_cycle
    JCY pwm_high    ; 如果计数值 < 占空比，输出高电平
    
    ; 输出低电平
    CLR
    ST pwm_output
    JUMP pwm_continue

pwm_high:
    ; 输出高电平
    SET1
    ST pwm_output

pwm_continue:
    ; 这里可以将pwm_output写入到实际的IO端口
    ; 例如: LD pwm_output
    ;      ST IO_PORT_REGISTER
    
    JUMP pwm_loop

reset_counter:
    ; 重置计数器
    CLR
    ST current_count
    JUMP pwm_loop

ENDCODE
"""
    
    print("\n=== PWM控制示例 ===")
    print("生成30%占空比的PWM信号")
    
    compiler = ZH5001Compiler()
    
    if compiler.parse_text(code) and compiler.precompile() and compiler.compile():
        result = compiler.generate_output()
        print("✓ 编译成功")
        
        print(f"\n标号分布:")
        for name, pc in result['labels'].items():
            print(f"  {name}: PC {pc}")
        
        print(f"\n关键跳转指令:")
        for i, inst in enumerate(result['precompiled']):
            if inst['mnemonic'] in ['JZ', 'JCY', 'JUMP']:
                machine_code = result['machine_code'][i]['hex'] if i < len(result['machine_code']) else "N/A"
                print(f"  PC{i:2d}: {inst['mnemonic']:4s} {inst['operand']:12s} -> {machine_code}")
        
        return result
    else:
        print("✗ 编译失败")
        for error in compiler.errors:
            print(f"  {error}")
        return None

def example_interrupt_handler():
    """中断处理程序示例"""
    code = """
DATA
    int_flag        48  ; 中断标志 (使用特殊功能寄存器地址)
    saved_r0        10  ; 保存R0的值
    saved_r1        11  ; 保存R1的值
    counter         12  ; 中断计数器
ENDDATA

CODE
main:
    ; 主程序初始化
    CLR
    ST counter
    
    ; 主循环
main_loop:
    ; 检查中断标志
    LD int_flag
    JZ main_loop    ; 如果没有中断，继续主循环
    
    ; 处理中断
    JUMP int_handler

int_handler:
    ; 保存寄存器
    ST saved_r0     ; 保存R0
    R1R0            ; R0 = R1
    ST saved_r1     ; 保存R1
    
    ; 中断处理逻辑
    LD counter
    INC
    ST counter
    
    ; 清除中断标志
    CLR
    ST int_flag
    
    ; 恢复寄存器
    LD saved_r1     ; 恢复R1
    R0R1            ; R1 = R0
    LD saved_r0     ; 恢复R0
    
    ; 返回主程序
    JUMP main_loop

ENDCODE
"""
    
    print("\n=== 中断处理示例 ===")
    print("简单的中断处理程序")
    
    compiler = ZH5001Compiler()
    
    if compiler.parse_text(code) and compiler.precompile() and compiler.compile():
        result = compiler.generate_output()
        print("✓ 编译成功")
        
        print(f"\n使用了特殊功能寄存器:")
        for name, addr in result['variables'].items():
            if addr >= 48:
                print(f"  {name}: 地址 {addr} (特殊功能寄存器)")
        
        return result
    else:
        print("✗ 编译失败")
        for error in compiler.errors:
            print(f"  {error}")
        return None

def save_example_files():
    """保存示例文件"""
    examples = {
        'led_blink.asm': """DATA
    delay_count    0
    led_state      1
    port_addr      2
ENDDATA

CODE
main:
    LDINS 0x01
    ST led_state
    LDINS 51
    ST port_addr

blink_loop:
    LD led_state
    ST port_addr
    LDINS 1000
    ST delay_count

delay_loop:
    LD delay_count
    DEC
    ST delay_count
    JZ toggle_led
    JUMP delay_loop

toggle_led:
    LD led_state
    NOT
    ST led_state
    JUMP blink_loop
ENDCODE""",

        'fibonacci.asm': """DATA
    num1        0
    num2        1
    result      2
    counter     3
ENDDATA

CODE
main:
    LDINS 8         ; 计算第8个斐波那契数
    ST counter
    LDINS 0
    ST num1
    LDINS 1
    ST num2

fib_loop:
    LD counter
    JZ done
    LD num1
    ADD num2
    ST result
    LD num2
    ST num1
    LD result
    ST num2
    LD counter
    DEC
    ST counter
    JUMP fib_loop

done:
    LD num2
    ST result
    NOP
ENDCODE""",

        'timer_demo.asm': """DATA
    timer_count     0
    timer_preset    1
    output_pin      2
ENDDATA

CODE
init:
    LDINS 1000      ; 定时器预设值
    ST timer_preset
    LD timer_preset
    ST timer_count

timer_loop:
    LD timer_count
    DEC
    ST timer_count
    JZ timer_expired
    
    ; 这里可以做其他工作
    NOP
    JUMP timer_loop

timer_expired:
    ; 定时器到期，切换输出
    LD output_pin
    NOT
    ST output_pin
    
    ; 重新加载定时器
    LD timer_preset
    ST timer_count
    JUMP timer_loop
ENDCODE"""
    }
    
    print("\n=== 保存示例文件 ===")
    for filename, content in examples.items():
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 已保存: {filename}")
        except Exception as e:
            print(f"✗ 保存失败 {filename}: {str(e)}")

def main():
    """主函数"""
    print("ZH5001 单片机编译器使用示例")
    print("=" * 50)
    
    # 运行各种示例
    results = []
    
    result1 = example_led_blink()
    if result1:
        results.append(("LED闪烁", result1))
    
    result2 = example_math_operations()
    if result2:
        results.append(("数学运算", result2))
    
    result3 = example_pwm_control()
    if result3:
        results.append(("PWM控制", result3))
    
    result4 = example_interrupt_handler()
    if result4:
        results.append(("中断处理", result4))
    
    # 保存示例文件
    save_example_files()
    
    # 生成汇总报告
    print(f"\n=== 汇总报告 ===")
    print(f"成功编译的示例: {len(results)} 个")
    
    total_instructions = 0
    total_variables = 0
    total_labels = 0
    
    for name, result in results:
        instructions = len(result['machine_code'])
        variables = len(result['variables'])
        labels = len(result['labels'])
        
        total_instructions += instructions
        total_variables += variables
        total_labels += labels
        
        print(f"\n{name}:")
        print(f"  指令数: {instructions}")
        print(f"  变量数: {variables}")
        print(f"  标号数: {labels}")
    
    print(f"\n总计:")
    print(f"  总指令数: {total_instructions}")
    print(f"  总变量数: {total_variables}")
    print(f"  总标号数: {total_labels}")
    
    # 保存汇总结果
    summary = {
        'examples': len(results),
        'total_instructions': total_instructions,
        'total_variables': total_variables,
        'total_labels': total_labels,
        'results': [{'name': name, 'data': result} for name, result in results]
    }
    
    try:
        with open('examples_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print("\n✓ 汇总结果已保存到 examples_summary.json")
    except Exception as e:
        print(f"\n✗ 保存汇总结果失败: {str(e)}")

if __name__ == '__main__':
    main()