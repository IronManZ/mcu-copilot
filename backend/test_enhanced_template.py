#!/usr/bin/env python3
"""
测试增强后的提示词模板
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.template_engine import TemplateEngine

def test_enhanced_template():
    """测试增强后的提示词模板"""
    print("🧪 测试增强后的提示词模板...")

    # 读取新模板
    template_path = "app/services/prompts/zh5001_gemini_complete_template.md"
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    print(f"📄 模板文件大小: {len(template_content)} 字符")

    # 测试模板渲染
    variables = {
        "USER_REQUIREMENT": "控制LED P03引脚闪烁：500ms开，500ms关",
        "COMPILER_ERRORS": "第2行: 无效的地址值"
    }

    rendered = TemplateEngine.render(template_content, variables)

    print(f"📊 渲染后文本大小: {len(rendered)} 字符")

    # 验证关键改进
    improvements = [
        ("包含完整ASM代码", "TOGGLE_RAM   0" in rendered and "TABLE700:" in rendered),
        ("包含机器码示例", "388  ; LDINS 0x2000" in rendered),
        ("包含Verilog示例", "c_m[0] = {LDINS_IMMTH,6'd8}" in rendered),
        ("强调变量无冒号", "变量名后绝对没有冒号" in rendered),
        ("编译器原理说明", "占用2个程序字" in rendered),
        ("用户需求正确替换", variables["USER_REQUIREMENT"] in rendered),
        ("错误反馈正确显示", variables["COMPILER_ERRORS"] in rendered)
    ]

    print("\n✅ 模板增强验证:")
    all_passed = True
    for desc, passed in improvements:
        status = "✅" if passed else "❌"
        print(f"  {status} {desc}: {passed}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 增强模板验证通过！")
        print("📈 关键改进:")
        print("  • 包含了完整的386行真实程序代码")
        print("  • 显示机器码和Verilog编译结果")
        print("  • 强化了编译器工作原理理解")
        print("  • 纠正了变量定义格式错误")
        print("  • 提供了完整的编码规范指导")

        # 显示模板前200字符预览
        print(f"\n📝 模板开头预览:")
        print("=" * 50)
        print(rendered[:300] + "...")
        print("=" * 50)

        return True
    else:
        print("\n⚠️  模板增强验证失败")
        return False

if __name__ == "__main__":
    test_enhanced_template()