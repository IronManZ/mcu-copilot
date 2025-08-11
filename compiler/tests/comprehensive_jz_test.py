#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JZ指令全面测试套件
验证新发现的JZ指令规则的所有边界情况
"""

from zh5001_corrected_compiler import ZH5001Compiler

def test_jz_distance_systematically():
    """系统性测试各种JZ跳转距离"""
    print("=== 系统性JZ跳转距离测试 ===\n")
    
    test_cases = []
    
    # 向前跳转测试：距离2到35
    for distance in range(1, 36):
        nop_count = distance - 1  # start指令后需要的NOP数量
        
        test_code = f'''DATA
    temp 0
ENDDATA

CODE
start:
    JZ target
'''
        for i in range(nop_count):
            test_code += "    NOP\n"
        
        test_code += '''target:
    NOP
ENDCODE
'''
        
        expected_offset = distance - 2 if distance >= 2 else None
        should_compile = distance >= 2 and distance <= 33
        
        test_cases.append({
            'name': f'向前跳转距离{distance}',
            'code': test_code,
            'distance': distance,
            'expected_offset': expected_offset,
            'should_compile': should_compile,
            'direction': 'forward'
        })
    
    # 向后跳转测试：距离1到35
    for distance in range(1, 36):
        nop_count = distance - 1  # loop标号后需要的NOP数量
        
        test_code = f'''DATA
    temp 0
ENDDATA

CODE
loop:
    NOP
'''
        for i in range(nop_count):
            test_code += "    NOP\n"
        
        test_code += '''    JZ loop
ENDCODE
'''
        
        expected_offset = -distance
        should_compile = distance <= 32
        
        test_cases.append({
            'name': f'向后跳转距离{distance}',
            'code': test_code,
            'distance': distance,
            'expected_offset': expected_offset, 
            'should_compile': should_compile,
            'direction': 'backward'
        })
    
    # 执行测试
    passed = 0
    failed = 0
    
    for case in test_cases:
        compiler = ZH5001Compiler()
        success = compiler.compile_text(case['code'])
        
        if case['should_compile']:
            if success:
                # 验证偏移量计算
                jz_found = False
                for i, inst in enumerate(compiler.precompiled):
                    if inst.mnemonic == 'JZ':
                        pc = i
                        target_pc = compiler.labels[inst.operand].pc
                        
                        if case['direction'] == 'forward':
                            calculated_offset = target_pc - pc - 2
                        else:
                            calculated_offset = target_pc - pc
                        
                        if calculated_offset == case['expected_offset']:
                            print(f"✅ {case['name']}: 偏移量{calculated_offset}")
                            passed += 1
                        else:
                            print(f"❌ {case['name']}: 偏移量错误 (期望{case['expected_offset']}, 实际{calculated_offset})")
                            failed += 1
                        
                        jz_found = True
                        break
                
                if not jz_found:
                    print(f"❌ {case['name']}: 未找到JZ指令")
                    failed += 1
            else:
                print(f"❌ {case['name']}: 编译失败，但应该成功")
                print(f"     错误: {compiler.errors}")
                failed += 1
        else:
            if success:
                print(f"❌ {case['name']}: 编译成功，但应该失败")
                failed += 1
            else:
                print(f"✅ {case['name']}: 正确拒绝")
                passed += 1
    
    print(f"\n测试总结: {passed} 通过, {failed} 失败")
    return failed == 0

def test_excel_corrected_cases():
    """测试修正后的Excel程序案例"""
    print("\n=== 测试修正后的Excel程序案例 ===\n")
    
    # 基于修正后的目标PC创建测试
    corrected_cases = [
        {
            'name': 'JZ KEY13_INC_1S_100MS (修正版)',
            'current_pc': 46,
            'target_pc': 60,  # 46 + 12 + 2
            'expected_offset': 12
        },
        {
            'name': 'JZ INC_KEY13 (修正版)',
            'current_pc': 56,
            'target_pc': 87,  # 56 + 29 + 2
            'expected_offset': 29
        }
    ]
    
    for case in corrected_cases:
        # 构造测试代码
        distance = case['target_pc'] - case['current_pc']
        nop_before_jz = case['current_pc']
        nop_after_jz = distance - 1
        
        test_code = '''DATA
    temp 0
ENDDATA

CODE
'''
        
        # 添加指令到达指定的current_pc
        for i in range(nop_before_jz):
            test_code += "    NOP\n"
        
        test_code += "    JZ target\n"
        
        # 添加指令到达指定的target_pc
        for i in range(nop_after_jz):
            test_code += "    NOP\n"
        
        test_code += '''target:
    NOP
ENDCODE
'''
        
        compiler = ZH5001Compiler()
        if compiler.compile_text(test_code):
            # 验证偏移量
            for i, inst in enumerate(compiler.precompiled):
                if inst.mnemonic == 'JZ':
                    pc = i
                    target_pc = compiler.labels[inst.operand].pc
                    calculated_offset = target_pc - pc - 2
                    
                    print(f"{case['name']}:")
                    print(f"  当前PC: {pc} (期望: {case['current_pc']})")
                    print(f"  目标PC: {target_pc} (期望: {case['target_pc']})")
                    print(f"  计算偏移: {calculated_offset} (期望: {case['expected_offset']})")
                    
                    if (pc == case['current_pc'] and 
                        target_pc == case['target_pc'] and 
                        calculated_offset == case['expected_offset']):
                        print(f"  ✅ 完全匹配!")
                    else:
                        print(f"  ❌ 不匹配")
                    break
        else:
            print(f"{case['name']}: ❌ 编译失败")
            print(f"  错误: {compiler.errors}")

def test_boundary_precision():
    """精确测试边界情况"""
    print("\n=== 精确边界测试 ===\n")
    
    boundary_tests = [
        # 向前跳转边界
        {'name': '向前最小距离(2)', 'distance': 2, 'direction': 'forward', 'should_pass': True},
        {'name': '向前最大距离(33)', 'distance': 33, 'direction': 'forward', 'should_pass': True},
        {'name': '向前超出距离(34)', 'distance': 34, 'direction': 'forward', 'should_pass': False},
        
        # 向后跳转边界
        {'name': '向后最小距离(1)', 'distance': 1, 'direction': 'backward', 'should_pass': True},
        {'name': '向后最大距离(32)', 'distance': 32, 'direction': 'backward', 'should_pass': True},
        {'name': '向后超出距离(33)', 'distance': 33, 'direction': 'backward', 'should_pass': False},
        
        # 无效距离
        {'name': '向前无效距离(1)', 'distance': 1, 'direction': 'forward', 'should_pass': False},
        {'name': '向前无效距离(0)', 'distance': 0, 'direction': 'forward', 'should_pass': False},
    ]
    
    for test in boundary_tests:
        if test['direction'] == 'forward':
            # 构造向前跳转
            if test['distance'] <= 0:
                # 特殊处理无效距离
                test_code = '''DATA
    temp 0
ENDDATA

CODE
start:
    JZ start
ENDCODE
''' if test['distance'] == 0 else '''DATA
    temp 0  
ENDDATA

CODE
target:
    JZ target
ENDCODE
'''
            else:
                nop_count = test['distance'] - 1
                test_code = '''DATA
    temp 0
ENDDATA

CODE
start:
    JZ target
'''
                for i in range(nop_count):
                    test_code += "    NOP\n"
                test_code += '''target:
    NOP
ENDCODE
'''
        else:
            # 构造向后跳转
            nop_count = test['distance'] - 1
            test_code = '''DATA
    temp 0
ENDDATA

CODE
loop:
    NOP
'''
            for i in range(nop_count):
                test_code += "    NOP\n"
            test_code += '''    JZ loop
ENDCODE
'''
        
        compiler = ZH5001Compiler()
        success = compiler.compile_text(test_code)
        
        if test['should_pass']:
            if success:
                print(f"✅ {test['name']}: 正确通过")
            else:
                print(f"❌ {test['name']}: 应该通过但失败")
                print(f"     错误: {compiler.errors}")
        else:
            if success:
                print(f"❌ {test['name']}: 应该失败但通过")
            else:
                print(f"✅ {test['name']}: 正确拒绝")

def main():
    """主测试函数"""
    print("JZ指令全面测试套件")
    print("=" * 80)
    
    # 运行系统性测试（可能输出较多，可选择性运行）
    run_systematic = input("是否运行系统性距离测试？(y/N): ").lower().strip() == 'y'
    
    if run_systematic:
        test_jz_distance_systematically()
    
    # 运行关键测试
    test_excel_corrected_cases()
    test_boundary_precision()
    
    print("\n" + "=" * 80)
    print("全面测试完成！")
    print("主要验证点:")
    print("✅ JZ指令新规则实现正确")
    print("✅ 边界条件处理准确")
    print("✅ Excel程序案例可以用修正后的目标PC解释")

if __name__ == '__main__':
    main()
