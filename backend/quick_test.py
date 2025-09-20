#!/usr/bin/env python3
"""
MCU-Copilot 快速测试脚本
用于快速验证单个测试用例或少量测试
"""
import requests
import json
import time
from datetime import datetime

def quick_test(requirement: str, test_id: str = "QT", use_gemini: bool = True):
    """快速测试单个需求"""
    print(f"🧪 快速测试 {test_id}: {requirement}")
    print("-" * 60)

    start_time = time.time()

    try:
        # 调用API
        response = requests.post(
            f"http://localhost:8000/compile?use_gemini={str(use_gemini).lower()}",
            json={"requirement": requirement},
            headers={"Content-Type": "application/json"},
            timeout=120
        )

        duration = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            print(f"✅ 响应成功 - 耗时: {duration:.1f}s")
            print(f"🧠 思考过程长度: {len(result.get('thought', ''))} 字符")
            print(f"📄 汇编代码长度: {len(result.get('assembly', ''))} 字符")

            if result.get('machine_code'):
                print(f"🔧 编译成功 - 机器码: {len(result['machine_code'])} 条指令")
            elif result.get('compile_error'):
                print(f"❌ 编译失败: {result['compile_error']}")
            else:
                print("⚠️  未知编译状态")

            print("\n🧠 AI思考过程:")
            print("-" * 40)
            thought = result.get('thought', '无思考过程')
            # 处理换行符显示
            thought_display = thought.replace('\\n', '\n')
            print(thought_display[:500] + "..." if len(thought_display) > 500 else thought_display)

            print("\n📄 生成的汇编代码:")
            print("-" * 40)
            assembly = result.get('assembly', '无汇编代码')
            # 处理换行符显示
            assembly_display = assembly.replace('\\n', '\n')
            print(assembly_display)

            return True

        else:
            print(f"❌ API调用失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def run_sample_tests():
    """运行几个示例测试"""
    print("🤖 MCU-Copilot 快速测试")
    print("=" * 60)

    sample_tests = [
        "控制LED P03引脚闪烁：500ms开，500ms关",
        "读取P01引脚按键状态，按下时P02引脚输出高电平",
        "实现4个LED(P00-P03)跑马灯效果，每个LED亮100ms后切换到下一个"
    ]

    success_count = 0

    for i, test in enumerate(sample_tests, 1):
        print(f"\n[测试 {i}/{len(sample_tests)}]")
        if quick_test(test, f"ST{i:02d}"):
            success_count += 1

        if i < len(sample_tests):
            time.sleep(1)  # 测试间隔

    print("\n" + "=" * 60)
    print(f"📊 快速测试完成: {success_count}/{len(sample_tests)} 成功")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # 命令行参数测试
        requirement = " ".join(sys.argv[1:])
        quick_test(requirement)
    else:
        # 运行示例测试
        run_sample_tests()