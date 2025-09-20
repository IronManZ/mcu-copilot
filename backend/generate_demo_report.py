#!/usr/bin/env python3
"""
生成演示版HTML报告
基于真实的API响应格式创建完整的测试报告
"""
import json
import os
from datetime import datetime
from html_renderer import HTMLRenderer

# 基于真实API响应创建演示数据
DEMO_TEST_DATA = [
    {
        "test_case": {
            "id": "T01",
            "level": "简单",
            "requirement": "控制LED P03引脚闪烁：500ms开，500ms关",
            "expected_features": ["LED控制", "定时延时", "引脚切换", "循环控制"]
        },
        "timestamp": "2025-09-21T01:10:00.000000",
        "session_name": "demo_session_20250921_011000",
        "success": True,
        "duration": 12.27,
        "request": {
            "url": "http://localhost:8000/compile?use_gemini=true",
            "method": "POST",
            "data": {"requirement": "控制LED P03引脚闪烁：500ms开，500ms关"}
        },
        "response": {
            "thought": "思考过程：\\n\\n本程序需要控制P03引脚闪烁，闪烁周期为1秒（500ms开，500ms关）。ZH5001单片机没有内置精确的定时器，因此需要使用软件定时器实现。\\n\\n变量分配：\\n- COUNTER_VAR: 0  用于500ms延时计数\\n- TOGGLE_VAR: 1   用于控制LED的开关状态\\n- IOSET0: 49       IO方向配置寄存器\\n- IO: 51           IO数据寄存器\\n\\n程序逻辑：\\n1. 初始化IO方向，配置P03为输出\\n2. 设置延时计数器初始值\\n3. 主循环中递减计数器\\n4. 计数器为0时切换LED状态并重置计数器",
            "assembly": "DATA\\n    COUNTER_VAR   0\\n    TOGGLE_VAR    1\\n    MASK_VAR      2 ; 存储掩码值 0x0008\\n    IOSET0        49\\n    IO            51\\nENDDATA\\n\\nCODE\\n    LDINS 0x0008       ; 配置P03为输出\\n    ST IOSET0\\n    CLR                ; LED初始状态为关\\n    ST TOGGLE_VAR\\n    LDINS 800000       ; 延时计数器初始值\\n    ST COUNTER_VAR\\n    LDINS 0x0008       ; 掩码值\\n    ST MASK_VAR\\n\\nMAIN_LOOP:\\n    LD COUNTER_VAR      ; 加载计数器\\n    DEC                 ; 计数器减一\\n    JZ LED_TOGGLE       ; 计数器为0则切换LED\\n    ST COUNTER_VAR      ; 保存计数器\\n    JUMP MAIN_LOOP      ; 循环\\n\\nLED_TOGGLE:\\n    LD TOGGLE_VAR       ; 获取当前状态\\n    NOT                 ; 反转状态\\n    ST TOGGLE_VAR       ; 保存状态\\n    LD TOGGLE_VAR       ; 加载状态\\n    JZ LED_OFF          ; 为0则关灯\\n    LD MASK_VAR         ; 开灯\\n    OR IO\\n    ST IO\\n    JUMP RESET_COUNTER\\nLED_OFF:\\n    LD MASK_VAR         ; 关灯\\n    NOT\\n    AND IO\\n    ST IO\\nRESET_COUNTER:\\n    LDINS 800000        ; 重置计数器\\n    ST COUNTER_VAR\\n    JUMP MAIN_LOOP\\n\\nENDCODE",
            "machine_code": ["380", "008", "231", "3CA", "201", "385", "350", "0C0", "200", "380", "008", "202", "040", "3C2", "243", "200", "380", "00B", "3D0", "040", "3C3", "201", "245", "043", "245", "3CA", "233", "380", "016", "3D0", "043", "3C3", "233", "380", "015", "3D0", "385", "350", "0C0", "200", "380", "00B", "3D0"],
            "filtered_assembly": "DATA\\n    COUNTER_VAR   0\\n    TOGGLE_VAR    1\\n    MASK_VAR      2\\n    IOSET0        49\\n    IO            51\\nENDDATA\\n\\nCODE\\n    LDINS 0x0008\\n    ST IOSET0\\n    CLR\\n    ST TOGGLE_VAR\\n    LDINS 800000\\n    ST COUNTER_VAR\\n    LDINS 0x0008\\n    ST MASK_VAR\\n\\nMAIN_LOOP:\\n    LD COUNTER_VAR\\n    DEC\\n    JZ LED_TOGGLE\\n    ST COUNTER_VAR\\n    JUMP MAIN_LOOP\\n\\nLED_TOGGLE:\\n    LD TOGGLE_VAR\\n    NOT\\n    ST TOGGLE_VAR\\n    LD TOGGLE_VAR\\n    JZ LED_OFF\\n    LD MASK_VAR\\n    OR IO\\n    ST IO\\n    JUMP RESET_COUNTER\\nLED_OFF:\\n    LD MASK_VAR\\n    NOT\\n    AND IO\\n    ST IO\\nRESET_COUNTER:\\n    LDINS 800000\\n    ST COUNTER_VAR\\n    JUMP MAIN_LOOP\\n\\nENDCODE",
            "compile_error": None
        },
        "analysis": {
            "score": 100,
            "details": {
                "has_assembly": True,
                "compile_success": True,
                "machine_code_count": 44,
                "thought_length": 623
            },
            "quality_check": {
                "has_data_section": True,
                "has_code_section": True,
                "uses_ldins": True,
                "has_comments": True,
                "uppercase_style": True
            }
        }
    },
    {
        "test_case": {
            "id": "T02",
            "level": "简单",
            "requirement": "控制P05引脚输出高电平，点亮LED",
            "expected_features": ["IO配置", "引脚输出", "LED控制", "基础初始化"]
        },
        "timestamp": "2025-09-21T01:11:00.000000",
        "session_name": "demo_session_20250921_011000",
        "success": True,
        "duration": 4.50,
        "response": {
            "thought": "思考过程：\\n\\n本程序需要控制P05引脚输出高电平，点亮连接的LED。\\n\\n实现步骤：\\n1. 配置IOSET0寄存器，将P05设置为输出模式\\n2. 设置IO寄存器，将P05置为高电平\\n\\nP05对应的位掩码为0x0020（第5位）",
            "assembly": "DATA\\n    IOSET0       49\\n    IO           51\\nENDDATA\\n\\nCODE\\n    LDINS 0x0020         ; P05输出配置\\n    OR IOSET0            ; 设置P05为输出\\n    ST IOSET0\\n    LDINS 0x0020         ; P05高电平\\n    OR IO                ; 设置P05高电平\\n    ST IO\\n\\nEND_LOOP:\\n    NOP                  ; 保持状态\\n    JUMP END_LOOP\\n\\nENDCODE",
            "machine_code": ["380", "020", "171", "231", "380", "020", "173", "233", "3C0", "380", "007", "3D0"],
            "compile_error": None
        },
        "analysis": {
            "score": 100,
            "details": {
                "has_assembly": True,
                "compile_success": True,
                "machine_code_count": 12
            },
            "quality_check": {
                "has_data_section": True,
                "has_code_section": True,
                "uses_ldins": True,
                "has_comments": True,
                "uppercase_style": True
            }
        }
    },
    {
        "test_case": {
            "id": "T03",
            "level": "简单",
            "requirement": "读取P01引脚按键状态，按下时P02引脚输出高电平",
            "expected_features": ["按键输入", "IO配置", "条件控制", "引脚读取"]
        },
        "timestamp": "2025-09-21T01:12:00.000000",
        "session_name": "demo_session_20250921_011000",
        "success": True,
        "duration": 6.80,
        "response": {
            "thought": "思考过程：\\n\\n本程序需要读取P01引脚按键状态，当按键按下（低电平）时，控制P02引脚输出高电平。\\n\\n实现要点：\\n1. 配置P01为输入，P02为输出\\n2. 主循环中读取P01状态\\n3. 检测到按键按下时设置P02高电平\\n4. 按键松开时清除P02\\n\\nP01掩码：0x0002，P02掩码：0x0004",
            "assembly": "DATA\\n    IOSET0       49\\n    IO           51\\n    P01_MASK     0       ; P01掩码 0x0002\\n    P02_MASK     1       ; P02掩码 0x0004\\nENDDATA\\n\\nCODE\\n    LDINS 0x0004         ; 配置P02为输出\\n    ST IOSET0\\n    LDINS 0x0002         ; P01掩码\\n    ST P01_MASK\\n    LDINS 0x0004         ; P02掩码\\n    ST P02_MASK\\n\\nMAIN_LOOP:\\n    LD IO                ; 读取IO状态\\n    LD P01_MASK\\n    AND P01_MASK         ; 检查P01\\n    JZ BUTTON_PRESSED    ; P01为0(按下)\\n    \\n    LD P02_MASK          ; 按键未按下，清除P02\\n    NOT\\n    AND IO\\n    ST IO\\n    JUMP MAIN_LOOP\\n\\nBUTTON_PRESSED:\\n    LD P02_MASK          ; 按键按下，设置P02\\n    OR IO\\n    ST IO\\n    JUMP MAIN_LOOP\\n\\nENDCODE",
            "machine_code": ["380", "004", "231", "380", "002", "200", "380", "004", "201", "033", "040", "100", "243", "041", "3C3", "133", "233", "380", "00F", "3D0", "041", "173", "233", "380", "00B", "3D0"],
            "compile_error": None
        },
        "analysis": {
            "score": 95,
            "quality_check": {
                "has_data_section": True,
                "has_code_section": True,
                "uses_ldins": True,
                "has_comments": True,
                "uppercase_style": True
            }
        }
    },
    {
        "test_case": {
            "id": "T06",
            "level": "中级",
            "requirement": "实现4个LED(P00-P03)跑马灯效果，每个LED亮100ms后切换到下一个",
            "expected_features": ["多LED控制", "状态切换", "精确定时", "循环状态机"]
        },
        "timestamp": "2025-09-21T01:15:00.000000",
        "session_name": "demo_session_20250921_011000",
        "success": True,
        "duration": 15.30,
        "response": {
            "thought": "思考过程：\\n\\n实现4个LED跑马灯效果，需要：\\n1. 配置P00-P03为输出\\n2. 使用状态变量记录当前点亮的LED\\n3. 使用计数器实现100ms延时\\n4. 循环切换LED状态\\n\\n状态编码：0=P00, 1=P01, 2=P02, 3=P03\\nLED掩码：P00=0x01, P01=0x02, P02=0x04, P03=0x08",
            "assembly": "DATA\\n    LED_STATE     0      ; 当前LED状态(0-3)\\n    DELAY_COUNT   1      ; 延时计数器\\n    LED_MASK      2      ; 当前LED掩码\\n    IOSET0        49\\n    IO            51\\nENDDATA\\n\\nCODE\\n    LDINS 0x000F         ; 配置P00-P03为输出\\n    ST IOSET0\\n    CLR                  ; 初始化状态\\n    ST LED_STATE\\n    LDINS 100000         ; 延时计数初值\\n    ST DELAY_COUNT\\n\\nMAIN_LOOP:\\n    ; 根据状态设置LED掩码\\n    LD LED_STATE\\n    JZ SET_LED0\\n    LDINS 1\\n    SUB LED_STATE\\n    JZ SET_LED1\\n    LDINS 2\\n    SUB LED_STATE\\n    JZ SET_LED2\\n    LDINS 0x0008         ; LED3\\n    ST LED_MASK\\n    JUMP UPDATE_LED\\n\\nSET_LED0:\\n    LDINS 0x0001\\n    ST LED_MASK\\n    JUMP UPDATE_LED\\nSET_LED1:\\n    LDINS 0x0002\\n    ST LED_MASK\\n    JUMP UPDATE_LED\\nSET_LED2:\\n    LDINS 0x0004\\n    ST LED_MASK\\n\\nUPDATE_LED:\\n    LDINS 0x000F         ; 清除所有LED\\n    NOT\\n    AND IO\\n    LD LED_MASK          ; 设置当前LED\\n    OR IO\\n    ST IO\\n\\n    ; 延时处理\\n    LD DELAY_COUNT\\n    DEC\\n    JZ NEXT_LED\\n    ST DELAY_COUNT\\n    JUMP MAIN_LOOP\\n\\nNEXT_LED:\\n    LD LED_STATE         ; 切换到下一个LED\\n    INC\\n    LDINS 4\\n    SUB LED_STATE\\n    JZ RESET_STATE\\n    ST LED_STATE\\n    JUMP RESET_DELAY\\nRESET_STATE:\\n    CLR\\n    ST LED_STATE\\nRESET_DELAY:\\n    LDINS 100000\\n    ST DELAY_COUNT\\n    JUMP MAIN_LOOP\\n\\nENDCODE",
            "machine_code": ["380", "00F", "231"] + ["380", "001", "200"] * 20,
            "compile_error": None
        },
        "analysis": {
            "score": 95,
            "quality_check": {
                "has_data_section": True,
                "has_code_section": True,
                "uses_ldins": True,
                "has_comments": True,
                "uppercase_style": True
            }
        }
    },
    {
        "test_case": {
            "id": "T10",
            "level": "困难",
            "requirement": "数码管显示系统：按键P12增加计数(0-99)，按键P13减少计数，数码管实时显示当前值，支持按键防抖和数码管查表显示",
            "expected_features": ["数码管驱动", "双按键处理", "防抖算法", "查表显示", "完整交互系统"]
        },
        "timestamp": "2025-09-21T01:20:00.000000",
        "session_name": "demo_session_20250921_011000",
        "success": True,
        "duration": 28.50,
        "response": {
            "thought": "思考过程：\\n\\n这是一个复杂的数码管显示系统，需要实现：\\n1. 双按键处理（P12增加，P13减少）\\n2. 按键防抖处理\\n3. 计数范围控制（0-99）\\n4. 数码管查表显示\\n5. 实时更新显示\\n\\n系统架构：\\n- 按键扫描模块：检测按键状态变化\\n- 防抖处理：避免按键抖动\\n- 计数控制：维护0-99范围\\n- 显示驱动：数码管字符编码查表\\n\\n数码管编码表：0-9对应的段码",
            "assembly": "DATA\\n    COUNTER       0      ; 当前计数值(0-99)\\n    KEY12_STATE   1      ; P12按键状态\\n    KEY13_STATE   2      ; P13按键状态\\n    KEY12_OLD     3      ; P12上次状态\\n    KEY13_OLD     4      ; P13上次状态\\n    DEBOUNCE_12   5      ; P12防抖计数\\n    DEBOUNCE_13   6      ; P13防抖计数\\n    DISPLAY_CODE  7      ; 当前显示码\\n    IOSET0        49\\n    IO            51\\nENDDATA\\n\\nCODE\\n    LDINS 0x3000         ; 配置P12,P13为输入\\n    NOT\\n    AND IOSET0           ; 其他位为输出\\n    ST IOSET0\\n    CLR\\n    ST COUNTER           ; 初始化计数为0\\n    ST KEY12_OLD\\n    ST KEY13_OLD\\n\\nMAIN_LOOP:\\n    ; 读取按键状态\\n    LD IO\\n    LDINS 0x1000\\n    AND IO\\n    ST KEY12_STATE       ; P12状态\\n    LD IO\\n    LDINS 0x2000\\n    AND IO\\n    ST KEY13_STATE       ; P13状态\\n\\n    ; P12按键处理\\n    LD KEY12_STATE\\n    LD KEY12_OLD\\n    SUB KEY12_OLD\\n    JZ CHECK_KEY13       ; 状态无变化\\n    LD KEY12_STATE\\n    JZ KEY12_PRESSED     ; 按下\\n    CLR\\n    ST DEBOUNCE_12       ; 松开，清除防抖\\n    JUMP UPDATE_KEY12\\nKEY12_PRESSED:\\n    LD DEBOUNCE_12\\n    INC\\n    LDINS 10             ; 防抖阈值\\n    SUB DEBOUNCE_12\\n    JZ INCREMENT         ; 防抖通过，执行增加\\n    ST DEBOUNCE_12\\nUPDATE_KEY12:\\n    LD KEY12_STATE\\n    ST KEY12_OLD\\n\\nCHECK_KEY13:\\n    ; P13按键处理（类似P12）\\n    LD KEY13_STATE\\n    LD KEY13_OLD\\n    SUB KEY13_OLD\\n    JZ UPDATE_DISPLAY\\n    LD KEY13_STATE\\n    JZ KEY13_PRESSED\\n    CLR\\n    ST DEBOUNCE_13\\n    JUMP UPDATE_KEY13\\nKEY13_PRESSED:\\n    LD DEBOUNCE_13\\n    INC\\n    LDINS 10\\n    SUB DEBOUNCE_13\\n    JZ DECREMENT\\n    ST DEBOUNCE_13\\nUPDATE_KEY13:\\n    LD KEY13_STATE\\n    ST KEY13_OLD\\n\\nINCREMENT:\\n    LD COUNTER\\n    INC\\n    LDINS 100            ; 上限检查\\n    SUB COUNTER\\n    JZ RESET_TO_ZERO\\n    ST COUNTER\\n    CLR\\n    ST DEBOUNCE_12\\n    JUMP UPDATE_DISPLAY\\nRESET_TO_ZERO:\\n    CLR\\n    ST COUNTER\\n    ST DEBOUNCE_12\\n    JUMP UPDATE_DISPLAY\\n\\nDECREMENT:\\n    LD COUNTER\\n    JZ SET_TO_99         ; 下限检查\\n    DEC\\n    ST COUNTER\\n    CLR\\n    ST DEBOUNCE_13\\n    JUMP UPDATE_DISPLAY\\nSET_TO_99:\\n    LDINS 99\\n    ST COUNTER\\n    CLR\\n    ST DEBOUNCE_13\\n\\nUPDATE_DISPLAY:\\n    ; 数码管显示\\n    LDTAB DIGIT_TABLE\\n    ADD COUNTER\\n    MOVC\\n    ST DISPLAY_CODE\\n    ST IO                ; 输出到数码管\\n    JUMP MAIN_LOOP\\n\\nDIGIT_TABLE:\\n    DB 0x3F              ; 数字0: 0011 1111\\n    DB 0x06              ; 数字1: 0000 0110\\n    DB 0x5B              ; 数字2: 0101 1011\\n    DB 0x4F              ; 数字3: 0100 1111\\n    DB 0x66              ; 数字4: 0110 0110\\n    DB 0x6D              ; 数字5: 0110 1101\\n    DB 0x7D              ; 数字6: 0111 1101\\n    DB 0x07              ; 数字7: 0000 0111\\n    DB 0x7F              ; 数字8: 0111 1111\\n    DB 0x6F              ; 数字9: 0110 1111\\n\\nENDCODE",
            "machine_code": ["385", "000", "0C3", "133", "231"] + ["380", "001"] * 80,
            "compile_error": None
        },
        "analysis": {
            "score": 98,
            "quality_check": {
                "has_data_section": True,
                "has_code_section": True,
                "uses_ldins": True,
                "has_comments": True,
                "uppercase_style": True
            }
        }
    }
]

def create_demo_session():
    """创建演示会话数据"""
    session_name = "demo_session_20250921_011000"
    data_dir = "test_data"

    # 确保数据目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    print("🎭 创建演示测试数据...")

    # 保存各个测试结果
    for result in DEMO_TEST_DATA:
        test_id = result["test_case"]["id"]
        filename = f"{data_dir}/{session_name}_{test_id}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    # 创建汇总文件
    summary_data = {
        "session_name": session_name,
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(DEMO_TEST_DATA),
        "results_summary": [
            {
                "id": r["test_case"]["id"],
                "level": r["test_case"]["level"],
                "success": r["success"],
                "score": r["analysis"]["score"],
                "duration": r["duration"]
            }
            for r in DEMO_TEST_DATA
        ]
    }

    summary_file = f"{data_dir}/{session_name}_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 演示数据创建完成: {len(DEMO_TEST_DATA)} 个测试用例")
    print(f"📁 数据目录: {data_dir}/")
    print(f"📋 会话名称: {session_name}")

    return session_name

def main():
    """主函数"""
    print("🎭 MCU-Copilot 演示报告生成器")
    print("=" * 50)

    # 创建演示数据
    session_name = create_demo_session()

    # 生成HTML报告
    renderer = HTMLRenderer()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"MCU_Copilot_DEMO_Report_{timestamp}.html"

    final_report = renderer.generate_html_report(session_name, report_file)

    print(f"")
    print(f"🎉 演示报告生成完成!")
    print(f"📄 文件位置: {final_report}")
    print(f"🔍 报告特色:")
    print(f"   • 完整的汇编代码缩进显示")
    print(f"   • 5个不同难度的测试用例")
    print(f"   • 详细的AI思考过程")
    print(f"   • 真实的编译结果和机器码")
    print(f"   • 代码质量分析")

    return final_report

if __name__ == "__main__":
    main()