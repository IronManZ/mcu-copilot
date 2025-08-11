#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZH5001编译器测试套件
验证修正后的编译器是否能正确处理各种情况
"""

import sys
import os
from typing import List, Dict, Tuple

# 导入编译器（假设在同目录下）
try:
    from zh5001_corrected_compiler import ZH5001Compiler
except ImportError:
    print("错误: 无法导入ZH5001Compiler，请确保编译器文件在同目录下")
    sys.exit(1)

class CompilerTestSuite:
    """编译器测试套件"""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
    
    def run_test(self, test_name: str, test_func) -> bool:
        """运行单个测试"""
        print(f"\n=== {test_name} ===")
        try:
            result = test_func()
            if result:
                print(f"✓ {test_name} 通过")
                self.passed_tests += 1
            else:
                print(f"✗ {test_name} 失败")
                self.failed_tests += 1
            
            self.test_results.append((test_name, result))
            return result
        except Exception as e:
            print(f"✗ {test_name} 异常: {str(e)}")
            self.failed_tests += 1
            self.test_results.append((test_name, False))
            return False
    
    def test_jz_offset_calculation(self) -> bool:
        """测试JZ指令偏移量计算的正确性"""
        test_code = """DATA
    temp    0
ENDDATA

CODE
LOOP1:
    LD temp
    JZ LOOP1
    JZ forward
    NOP
forward:
    NOP
ENDCODE
"""
        
        compiler = ZH5001Compiler()
        if not compiler.compile_text(test_code):
            print("编译失败:", compiler.errors)
            return False
        
        # 验证JZ指令的偏移量
        expected_offsets = {
            'LOOP1': -1,    # 0 - 1 = -1
            'forward': 2    # 4 - 2 = +2
        }
        
        jz_count = 0
        for i, inst in enumerate(compiler.precompiled):
            if inst.mnemonic == 'JZ':
                pc = i
                target_pc = compiler.labels[inst.operand].pc
                calculated_offset = target_pc - pc
                expected_offset = expected_offsets.get(inst.operand)
                
                print(f"JZ {inst.operand}: PC{pc}→PC{target_pc}, 偏移={calculated_offset}")
                
                if expected_offset is not None:
                    if calculated_offset == expected_offset:
                        print(f"  ✓ 偏移量正确: {calculated_offset}")
                    else:
                        print(f"  ✗ 偏移量错误: 期望{expected_offset}, 实际{calculated_offset}")
                        return False
                
                jz_count += 1
        
        return jz_count == 2  # 应该有2条JZ指令
    
    def test_verilog_output_format(self) -> bool:
        """测试Verilog输出格式的正确性"""
        test_code = """DATA
    counter 0
ENDDATA

CODE
start:
    JZ loop         ; 正偏移量
    NOP
loop:
    JZ start        ; 负偏移量
ENDCODE
"""
        
        compiler = ZH5001Compiler()
        if not compiler.compile_text(test_code):
            return False
        
        # 检查Verilog输出格式
        verilog_outputs = []
        for code in compiler.machine_code:
            if 'JZ' in code.verilog:
                verilog_outputs.append(code.verilog)
                print(f"Verilog: {code.verilog}")
        
        # 应该有一个正偏移和一个负偏移的JZ指令
        has_positive = any('6\'d' in v and '-' not in v for v in verilog_outputs)
        has_negative = any('-6\'sd' in v for v in verilog_outputs)
        
        return has_positive and has_negative
    
    def test_excel_program_simulation(self) -> bool:
        """模拟Excel程序中的实际情况"""
        test_code = """DATA
    TOGGLE_RAM   0
    IO_PLUS_RAM  1
    COUNTER_RAM  3
    IO           51
ENDDATA

CODE
    LDINS 0x03FF
    ST IO
    CLR
    ST TOGGLE_RAM

LOOP1:
    LDINS 0x0001
    AND IO
    JZ LOOP1

KEY13:
    LDINS 0x2000
    AND IO
    JZ KEY13_INC_1S_100MS
    JUMP NOTHING0

KEY13_INC_1S_100MS:
    NOP
    JUMP NOTHING0

NOTHING0:
    NOP
    JUMP LOOP1
ENDCODE
"""
        
        compiler = ZH5001Compiler()
        if not compiler.compile_text(test_code):
            print("编译失败:", compiler.errors)
            return False
        
        # 分析结果
        result = compiler.generate_output()
        print(f"标号地址:")
        for name, pc in result['labels'].items():
            print(f"  {name}: PC {pc}")
        
        # 检查关键的JZ指令
        jz_found = False
        for i, inst in enumerate(compiler.precompiled):
            if inst.mnemonic == 'JZ' and inst.operand == 'LOOP1':
                pc = i
                target_pc = compiler.labels['LOOP1'].pc
                offset = target_pc - pc
                print(f"JZ LOOP1: PC{pc}→PC{target_pc}, 偏移={offset}")
                
                # 这个偏移量应该是负数（向后跳转）
                if offset < 0:
                    jz_found = True
                    print("  ✓ 向后跳转偏移量正确")
                else:
                    print(f"  ✗ 向后跳转偏移量错误: {offset}")
                    return False
                break
        
        return jz_found
    
    def test_edge_cases(self) -> bool:
        """测试边界情况"""
        # 测试接近±32边界的跳转，但保持在合法范围内
        test_code = """DATA
    temp 0
ENDDATA

CODE
start:
    NOP
"""
        
        # 生成25个NOP指令来测试但不超出边界
        for i in range(25):
            test_code += "    NOP\n"
        
        test_code += """    JZ start
    NOP
ENDCODE
"""
        
        compiler = ZH5001Compiler()
        if not compiler.compile_text(test_code):
            print("编译失败:", compiler.errors)
            return False
        
        # 检查JZ指令的偏移量
        for i, inst in enumerate(compiler.precompiled):
            if inst.mnemonic == 'JZ' and inst.operand == 'start':
                pc = i
                target_pc = compiler.labels['start'].pc
                offset = target_pc - pc
                print(f"边界测试 JZ start: PC{pc}→PC{target_pc}, 偏移={offset}")
                
                # 偏移量应该在合法范围内
                if -32 <= offset <= 31:
                    print(f"  ✓ 偏移量在合法范围内: {offset}")
                    
                    # 检查是否有警告（接近边界）
                    if compiler.warnings:
                        print("编译器警告:")
                        for warning in compiler.warnings:
                            print(f"  {warning}")
                    
                    return True
                else:
                    print(f"  ✗ 偏移量超出范围: {offset}")
                    return False
        
        return False
    
    def test_db_instruction(self) -> bool:
        """测试DB指令"""
        test_code = """DATA
    temp 0
ENDDATA

CODE
main:
    LDTAB data_table
    MOVC
    ST temp

data_table:
    DB 0x15F
    DB 351      ; 十进制
    DB 0x100    ; 256
ENDCODE
"""
        
        compiler = ZH5001Compiler()
        if not compiler.compile_text(test_code):
            print("编译失败:", compiler.errors)
            return False
        
        # 检查DB指令的编译结果
        db_count = 0
        for code in compiler.machine_code:
            if code.verilog and '10\'d' in code.verilog and 'c_m[' in code.verilog:
                print(f"DB数据: {code.verilog}")
                db_count += 1
        
        return db_count >= 3  # 应该有3个DB数据
    
    def test_movc_instruction(self) -> bool:
        """测试MOVC指令"""
        test_code = """DATA
    result 0
ENDDATA

CODE
    LDTAB table
    MOVC
    ST result
    
table:
    DB 100
ENDCODE
"""
        
        compiler = ZH5001Compiler()
        if not compiler.compile_text(test_code):
            print("编译失败:", compiler.errors)
            return False
        
        # 检查MOVC指令是否被正确编译
        movc_found = False
        for code in compiler.machine_code:
            if code.verilog and 'MOVC' in code.verilog:
                print(f"MOVC指令: {code.verilog}")
                movc_found = True
                break
        
        return movc_found
    
    def test_complex_program(self) -> bool:
        """测试复杂程序"""
        # 一个包含多种指令类型的复杂程序
        test_code = """DATA
    counter     0
    result      1
    temp        2
    threshold   3
ENDDATA

CODE
main:
    LDINS 10
    ST counter
    CLR
    ST result

loop:
    LD counter
    JZ finished
    
    ; 条件检查
    LD counter
    SUB threshold
    JZ special_case
    
    ; 正常处理
    LD result
    ADD counter
    ST result
    JUMP continue

special_case:
    LD result
    MUL counter
    ST result

continue:
    LD counter
    DEC
    ST counter
    JUMP loop

finished:
    LD result
    ST temp
    NOP

; 数据表
lookup_table:
    DB 0
    DB 1
    DB 4
    DB 9
    DB 16
ENDCODE
"""
        
        compiler = ZH5001Compiler()
        if not compiler.compile_text(test_code):
            print("编译失败:", compiler.errors)
            return False
        
        result = compiler.generate_output()
        
        # 检查统计信息
        stats = result['statistics']
        print(f"复杂程序统计:")
        print(f"  变量: {stats['total_variables']}")
        print(f"  标号: {stats['total_labels']}")
        print(f"  指令: {stats['total_instructions']}")
        
        # 应该有足够的复杂性
        return (stats['total_variables'] >= 4 and 
                stats['total_labels'] >= 5 and 
                stats['total_instructions'] >= 15)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("ZH5001编译器测试套件")
        print("=" * 50)
        
        test_methods = [
            ("JZ偏移量计算测试", self.test_jz_offset_calculation),
            ("Verilog输出格式测试", self.test_verilog_output_format),
            ("Excel程序模拟测试", self.test_excel_program_simulation),
            ("边界情况测试", self.test_edge_cases),
            ("DB指令测试", self.test_db_instruction),
            ("MOVC指令测试", self.test_movc_instruction),
            ("复杂程序测试", self.test_complex_program),
        ]
        
        for test_name, test_func in test_methods:
            self.run_test(test_name, test_func)
        
        # 输出总结
        print(f"\n" + "=" * 50)
        print(f"测试总结:")
        print(f"  通过: {self.passed_tests}")
        print(f"  失败: {self.failed_tests}")
        print(f"  总计: {self.passed_tests + self.failed_tests}")
        print(f"  成功率: {self.passed_tests/(self.passed_tests + self.failed_tests)*100:.1f}%")
        
        if self.failed_tests == 0:
            print(f"\n🎉 所有测试通过！编译器工作正常。")
        else:
            print(f"\n⚠️  有 {self.failed_tests} 个测试失败，需要检查。")
        
        return self.failed_tests == 0


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("ZH5001编译器测试套件")
        print("用法: python compiler_test_suite.py")
        print("运行所有测试来验证编译器的正确性")
        return
    
    test_suite = CompilerTestSuite()
    success = test_suite.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
