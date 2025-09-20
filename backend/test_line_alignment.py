#!/usr/bin/env python3
"""
测试行号对齐系统是否正确解决了编译器错误与大模型理解的偏差问题
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.conversation_manager import GeminiConversationManager
from app.services.structured_code_manager import StructuredCodeManager

def test_line_alignment():
    """测试行号对齐系统"""
    print("🧪 测试行号对齐系统...")

    # 模拟有问题的汇编代码（和之前log中看到的问题类似）
    problematic_assembly = """DATA
counter: DS000 1
ENDDATA

CODE
start:
    LDINS 0x0008
    ST 49
main_loop:
    LDINS 0x0008
    OR 51
ENDCODE"""

    # 模拟编译器错误：第2行 无效的地址值（这应该指向counter: DS000 1）
    compile_errors = ["第2行: 无效的地址值"]

    print("📝 问题场景:")
    print("代码:", problematic_assembly)
    print("编译错误:", compile_errors)
    print()

    # 测试结构化代码管理器
    print("🔍 测试结构化代码解析...")
    code_manager = StructuredCodeManager()
    parsed_lines = code_manager.parse_assembly_code(problematic_assembly)

    print("解析结果:")
    for line in parsed_lines:
        if line.content_type != 'empty':
            print(f"  行{line.line_number}: {line.section}段 {line.content_type} - '{line.raw_content.strip()}'")

    print()

    # 测试错误上下文格式化
    print("🎯 测试错误上下文生成...")
    error_context = code_manager.format_error_context(2, "无效的地址值")
    print("生成的错误上下文:")
    print("=" * 50)
    print(error_context)
    print("=" * 50)
    print()

    # 测试对话管理器的结构化反馈
    print("💬 测试对话管理器结构化反馈...")
    conversation = GeminiConversationManager("test-alignment-001")

    # 开始对话
    conversation.start_conversation(
        "你是ZH5001汇编专家",
        "请生成LED控制代码"
    )

    # 添加助手响应（模拟生成的有问题代码）
    conversation.add_assistant_response(problematic_assembly)

    # 添加结构化错误反馈
    messages = conversation.add_error_feedback(
        compile_errors=compile_errors,
        attempt_num=1,
        generated_code=problematic_assembly
    )

    print("对话管理器生成的结构化反馈:")
    last_message = messages[-1]['content']
    print("=" * 60)
    print(last_message)
    print("=" * 60)
    print()

    # 验证关键信息是否正确
    print("✅ 验证结果:")
    success_checks = [
        ("包含全局行号信息", "全局行号: 2" in last_message),
        ("正确识别DATA段", "代码段: DATA" in last_message),
        ("正确识别变量类型", "内容类型: variable" in last_message),
        ("显示正确的原始内容", "counter: DS000 1" in last_message),
        ("提供上下文行", ">>> " in last_message),
    ]

    for check_name, passed in success_checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}: {passed}")

    all_passed = all(passed for _, passed in success_checks)
    if all_passed:
        print("\n🎉 行号对齐系统工作正常！LLM现在能够准确理解编译器错误的具体位置。")
    else:
        print("\n⚠️  行号对齐系统可能存在问题，需要进一步调试。")

    return all_passed

if __name__ == "__main__":
    test_line_alignment()