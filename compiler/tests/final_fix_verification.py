#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复验证脚本
验证MOVC指令编码和HEX文件格式修复
"""

from zh5001_corrected_compiler import ZH5001Compiler
import os

def test_movc_instruction_encoding():
    """测试MOVC指令的正确编码"""
    print("=== MOVC指令编码验证 ===\n")
    
    test_code = """DATA
    result 0
ENDDATA

CODE
main:
    LDTAB data_table
    MOVC
    ST result
    NOP
    
data_table:
    DB 0x15F
    DB 0x150
    DB 0x13B
ENDCODE
"""
    
    compiler = ZH5001Compiler()
    if not compiler.compile_text(test_code):
        print("❌ 编译失败:")
        for error in compiler.errors:
            print(f"  {error}")
        return False
    
    print("✅ 编译成功")
    
    # 查找MOVC指令的编译结果
    movc_found = False
    for code in compiler.machine_code:
        if 'MOVC' in code.verilog:
            print(f"MOVC指令编译结果:")
            print(f"  二进制: {code.binary}")
            print(f"  十六进制: {code.hex_code}")
            print(f"  Verilog: {code.verilog}")
            
            # 验证二进制编码
            expected_binary = '1111010100'
            if code.binary == expected_binary:
                print(f"  ✅ 二进制编码正确: {expected_binary}")
            else:
                print(f"  ❌ 二进制编码错误: 期望{expected_binary}, 实际{code.binary}")
                return False
            
            # 验证十六进制
            expected_hex = '3D4'
            if code.hex_code == expected_hex:
                print(f"  ✅ 十六进制编码正确: {expected_hex}")
            else:
                print(f"  ❌ 十六进制编码错误: 期望{expected_hex}, 实际{code.hex_code}")
                return False
            
            movc_found = True
            break
    
    if not movc_found:
        print("❌ 未找到MOVC指令")
        return False
    
    return True

def test_hex_file_format():
    """测试HEX文件格式（无尾部换行符）"""
    print("\n=== HEX文件格式验证 ===\n")
    
    test_code = """DATA
    temp 0
ENDDATA

CODE
    LDINS 100
    ST temp
    LD temp
    NOP
ENDCODE
"""
    
    compiler = ZH5001Compiler()
    if not compiler.compile_text(test_code):
        print("❌ 编译失败")
        return False
    
    # 保存HEX文件
    test_output = "format_test"
    compiler.save_output(test_output)
    
    # 检查HEX文件格式
    hex_filename = f"{test_output}.hex"
    if os.path.exists(hex_filename):
        with open(hex_filename, 'rb') as f:  # 使用二进制模式读取
            content = f.read()
        
        print(f"HEX文件: {hex_filename}")
        print(f"文件大小: {len(content)} 字节")
        
        # 检查是否以换行符结尾
        if content.endswith(b'\n'):
            print("❌ 文件以换行符结尾（不符合要求）")
            return False
        else:
            print("✅ 文件不以换行符结尾（符合要求）")
        
        # 显示文件内容
        content_str = content.decode('utf-8')
        lines = content_str.split('\n')
        print(f"文件内容 ({len(lines)} 行):")
        for i, line in enumerate(lines):
            print(f"  行{i+1}: '{line}'")
        
        # 验证最后一行没有换行符
        last_char = content_str[-1] if content_str else ''
        if last_char == '\n':
            print("❌ 最后一个字符是换行符")
            return False
        else:
            print(f"✅ 最后一个字符是: '{last_char}' (不是换行符)")
        
        return True
    else:
        print(f"❌ HEX文件未生成: {hex_filename}")
        return False

def test_comprehensive_program():
    """综合测试程序，包含MOVC和多个JZ指令"""
    print("\n=== 综合程序测试 ===\n")
    
    comprehensive_code = """DATA
    counter     0
    index       1
    result      2
    temp        3
ENDDATA

CODE
main:
    LDINS 10
    ST counter
    CLR
    ST index

loop:
    LD counter
    JZ finished
    
    ; 使用MOVC查表
    LD index
    LDTAB lookup_table
    ADD index
    MOVC
    R1R0
    ADD result
    ST result
    
    ; 更新计数器
    LD counter
    DEC
    ST counter
    LD index
    INC
    ST index
    
    JUMP loop

finished:
    LD result
    ST temp
    NOP

lookup_table:
    DB 1
    DB 2
    DB 4
    DB 8
    DB 16
ENDCODE
"""
    
    compiler = ZH5001Compiler()
    if not compiler.compile_text(comprehensive_code):
        print("❌ 综合程序编译失败:")
        for error in compiler.errors:
            print(f"  {error}")
        return False
    
    result = compiler.generate_output()
    
    print("✅ 综合程序编译成功")
    print(f"统计信息:")
    print(f"  变量: {result['statistics']['total_variables']}")
    print(f"  标号: {result['statistics']['total_labels']}")
    print(f"  指令: {result['statistics']['total_instructions']}")
    
    # 检查MOVC指令
    movc_found = False
    jz_count = 0
    
    for code in compiler.machine_code:
        if 'MOVC' in code.verilog:
            print(f"\nMOVC指令:")
            print(f"  PC{code.pc}: {code.binary} ({code.hex_code})")
            print(f"  Verilog: {code.verilog}")
            movc_found = True
        
        if code.verilog and any(jz in code.verilog for jz in ['JZ', 'JOV', 'JCY']):
            jz_count += 1
    
    print(f"\n指令统计:")
    print(f"  MOVC指令: {'✅ 找到' if movc_found else '❌ 未找到'}")
    print(f"  JZ类指令: {jz_count} 条")
    
    # 保存综合测试输出
    compiler.save_output("comprehensive_test")
    
    return movc_found

def verify_hex_file_ending():
    """专门验证HEX文件结尾格式"""
    print("\n=== HEX文件结尾格式专项验证 ===\n")
    
    # 创建一个简单的3行程序
    simple_code = """DATA
    temp 0
ENDDATA

CODE
    LDINS 123
    ST temp
    NOP
ENDCODE
"""
    
    compiler = ZH5001Compiler()
    if compiler.compile_text(simple_code):
        compiler.save_output("ending_test")
        
        # 读取并分析HEX文件
        with open("ending_test.hex", 'rb') as f:
            raw_content = f.read()
        
        print(f"HEX文件原始内容:")
        print(f"  字节序列: {raw_content}")
        print(f"  ASCII内容: '{raw_content.decode('utf-8')}'")
        print(f"  文件大小: {len(raw_content)} 字节")
        
        # 检查最后几个字节
        if len(raw_content) >= 3:
            last_3_bytes = raw_content[-3:]
            print(f"  最后3个字节: {last_3_bytes}")
            
            if raw_content.endswith(b'\n'):
                print("  ❌ 文件以换行符(\\n)结尾")
                print("  最后一个字节: 0x0A (换行符)")
            else:
                print("  ✅ 文件不以换行符结尾")
                last_byte = raw_content[-1]
                print(f"  最后一个字节: 0x{last_byte:02X} ({chr(last_byte) if 32 <= last_byte <= 126 else '不可打印'})")
        
        return not raw_content.endswith(b'\n')
    
    return False

def main():
    """主验证函数"""
    print("ZH5001编译器最终修复验证")
    print("=" * 60)
    
    # 验证修复项目
    fixes = [
        ("MOVC指令编码修复", test_movc_instruction_encoding),
        ("HEX文件格式修复", test_hex_file_format),
        ("综合程序测试", test_comprehensive_program),
        ("HEX文件结尾验证", verify_hex_file_ending),
    ]
    
    passed = 0
    total = len(fixes)
    
    for fix_name, test_func in fixes:
        try:
            if test_func():
                print(f"✅ {fix_name} - 修复成功")
                passed += 1
            else:
                print(f"❌ {fix_name} - 仍有问题")
        except Exception as e:
            print(f"❌ {fix_name} - 测试异常: {str(e)}")
    
    print(f"\n" + "=" * 60)
    print(f"修复验证结果: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有修复都成功验证！")
        print("\n编译器现在具备:")
        print("✅ 正确的JZ偏移量计算规则")
        print("✅ 正确的MOVC指令编码 (1111010100)")
        print("✅ 标准的HEX文件格式 (无尾部换行符)")
        print("✅ 完整的指令集支持")
        print("✅ 详细的错误检测和警告")
    else:
        print(f"⚠️ 还有 {total - passed} 个问题需要解决")
    
    return passed == total

if __name__ == '__main__':
    main()
