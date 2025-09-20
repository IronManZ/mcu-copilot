#!/usr/bin/env python3
"""
基于真实API调用结果重新生成修复格式的HTML报告
"""
import requests
import json
import time
from datetime import datetime
from automated_test_suite import MCUTestRunner, TEST_CASES

def regenerate_with_real_data_sample():
    """使用真实数据的前3个测试用例生成报告"""
    print("🔧 重新生成HTML报告（使用真实数据样本）...")
    print("=" * 60)

    runner = MCUTestRunner()

    # 运行前3个测试用例作为示例（避免长时间等待）
    sample_cases = TEST_CASES[:3]

    print(f"📊 运行 {len(sample_cases)} 个示例测试用例:")
    for i, test_case in enumerate(sample_cases, 1):
        print(f"[{i}/{len(sample_cases)}] {test_case['id']}: {test_case['requirement'][:50]}...")

    # 运行测试
    for test_case in sample_cases:
        result = runner.run_single_test(test_case)
        runner.results.append(result)
        time.sleep(1)

    # 生成修复格式的HTML报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"MCU_Copilot_REAL_FIXED_Report_{timestamp}.html"

    report_file = runner.generate_html_report(output_file)

    print(f"\n✅ 重新生成完成！")
    print(f"📄 修复格式的HTML报告: {report_file}")
    print(f"🔍 格式改进:")
    print(f"   • 汇编代码正确缩进（4空格转&nbsp;）")
    print(f"   • 变量定义缩进保持")
    print(f"   • 标号顶格显示")
    print(f"   • 注释对齐良好")

    return report_file

def show_formatting_comparison():
    """显示修复前后的格式对比"""
    print("\n" + "="*60)
    print("🔍 格式修复对比")
    print("="*60)

    print("\n❌ 修复前（缩进丢失）:")
    print("""
DATA
COUNTER_VAR 0
TOGGLE_VAR 1
IOSET0 49
ENDDATA

CODE
LDINS 0x0008
ST IOSET0
MAIN_LOOP:
LD COUNTER_VAR
DEC
ENDCODE
    """)

    print("\n✅ 修复后（缩进保持）:")
    print("""
DATA
    COUNTER_VAR   0
    TOGGLE_VAR    1
    IOSET0        49
ENDDATA

CODE
    LDINS 0x0008       ; 配置P03为输出
    ST IOSET0
MAIN_LOOP:
    LD COUNTER_VAR     ; 加载计数器
    DEC                ; 计数器减一
ENDCODE
    """)

if __name__ == "__main__":
    # 显示格式对比
    show_formatting_comparison()

    # 询问是否运行真实测试
    response = input("\n是否运行3个真实测试用例验证格式修复？(y/n): ").strip().lower()

    if response == 'y':
        regenerate_with_real_data_sample()
    else:
        print("✅ 格式修复逻辑已就绪，可随时使用 automated_test_suite.py 生成正确格式的报告！")