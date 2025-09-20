#!/usr/bin/env python3
"""
测试新的日志功能
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.nl_to_assembly import nl_to_assembly

def test_logging():
    """测试日志功能"""
    print("🧪 开始测试新的日志功能...")

    # 测试需求
    requirement = "控制LED P03引脚闪烁：500ms开，500ms关"

    try:
        # 使用Gemini模型测试
        print("📝 测试Gemini模型日志...")
        thought, assembly = nl_to_assembly(requirement, use_gemini=True, session_id="test-log-001")

        print(f"✅ 测试完成")
        print(f"📊 思考过程长度: {len(thought)} 字符")
        print(f"📊 汇编代码长度: {len(assembly)} 字符")

        if thought and assembly:
            print("🎉 生成成功！")
            print("思考过程前100字符:", thought[:100])
            print("汇编代码前100字符:", assembly[:100])
        else:
            print("⚠️  生成结果为空")

    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_logging()