#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZH5001编译器服务
将ZH5001编译器集成到后端API中
"""

import sys
import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from zh5001_corrected_compiler import ZH5001Compiler

class ZH5001CompilerService:
    """ZH5001编译器服务类"""
    
    def __init__(self):
        self.compiler = ZH5001Compiler()
    
    def compile_assembly(self, assembly_code: str) -> Dict:
        """
        编译汇编代码
        
        Args:
            assembly_code: 汇编代码字符串
            
        Returns:
            Dict: 包含编译结果的字典
        """
        try:
            # 重置编译器状态，避免重复定义错误
            self.compiler = ZH5001Compiler()
            
            # 编译汇编代码
            success = self.compiler.compile_text(assembly_code)
            
            if success:
                # 生成编译结果
                result = self.compiler.generate_output()
                
                # 格式化输出
                formatted_result = {
                    'success': True,
                    'errors': [],
                    'warnings': result.get('warnings', []),
                    'variables': result.get('variables', {}),
                    'labels': result.get('labels', {}),
                    'machine_code': result.get('machine_code', []),
                    'statistics': result.get('statistics', {}),
                    'hex_code': self._generate_hex_output(),
                    'verilog_code': self._generate_verilog_output()
                }
                
                return formatted_result
            else:
                return {
                    'success': False,
                    'errors': self.compiler.errors,
                    'warnings': self.compiler.warnings,
                    'variables': {},
                    'labels': {},
                    'machine_code': [],
                    'statistics': {},
                    'hex_code': '',
                    'verilog_code': ''
                }
                
        except Exception as e:
            return {
                'success': False,
                'errors': [f"编译过程中发生错误: {str(e)}"],
                'warnings': [],
                'variables': {},
                'labels': {},
                'machine_code': [],
                'statistics': {},
                'hex_code': '',
                'verilog_code': ''
            }
    
    def _generate_hex_output(self) -> str:
        """生成HEX格式输出"""
        hex_lines = []
        for code in self.compiler.machine_code:
            hex_lines.append(code.hex_code)
        
        # 最后一行不添加换行符
        return '\n'.join(hex_lines)
    
    def _generate_verilog_output(self) -> str:
        """生成Verilog格式输出"""
        verilog_lines = ["// ZH5001 程序存储器初始化", "initial begin"]
        
        for code in self.compiler.machine_code:
            verilog_lines.append(f"    {code.verilog}")
        
        verilog_lines.append("end")
        return '\n'.join(verilog_lines)
    
    def validate_assembly(self, assembly_code: str) -> Dict:
        """
        验证汇编代码语法
        
        Args:
            assembly_code: 汇编代码字符串
            
        Returns:
            Dict: 验证结果
        """
        try:
            # 重置编译器状态，避免重复定义错误
            self.compiler = ZH5001Compiler()
            
            # 只进行语法解析，不生成机器码
            success = self.compiler.compile_text(assembly_code)
            
            return {
                'valid': success,
                'errors': self.compiler.errors,
                'warnings': self.compiler.warnings,
                'variables': {name: var.address for name, var in self.compiler.variables.items()},
                'labels': {name: label.pc for name, label in self.compiler.labels.items()}
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"验证过程中发生错误: {str(e)}"],
                'warnings': [],
                'variables': {},
                'labels': {}
            }
    
    def get_instruction_set(self) -> Dict:
        """
        获取ZH5001指令集信息
        
        Returns:
            Dict: 指令集信息
        """
        return {
            'instructions': {
                'basic_arithmetic': ['LD', 'ADD', 'SUB', 'AND', 'OR', 'MUL', 'CLAMP', 'ST'],
                'jump_instructions': ['JZ', 'JOV', 'JCY', 'JUMP'],
                'shift_instructions': ['SFT0RZ', 'SFT0RS', 'SFT0RR1', 'SFT0LZ', 'SFT1RZ', 'SFT1RS', 'SFT1RR1', 'SFT1LZ'],
                'immediate_instructions': ['LDINS'],
                'no_operand_instructions': ['NOP', 'INC', 'DEC', 'NOT', 'LDPC', 'NOTFLAG', 'R0R1', 'R1R0', 'SIN', 'COS', 'CLR', 'SET1', 'CLRFLAG', 'SETZ', 'SETCY', 'SETOV', 'SQRT', 'NEG', 'EXR0R1', 'SIXSTEP', 'JNZ3', 'MOVC'],
                'pseudo_instructions': ['DB', 'DS', 'ORG']
            },
            'addressing_modes': {
                'immediate': '立即数寻址',
                'direct': '直接寻址（变量地址）',
                'relative': '相对寻址（跳转指令）',
                'absolute': '绝对寻址（JUMP指令）'
            },
            'memory_organization': {
                'program_memory': '1024 x 10位',
                'data_memory': '64 x 10位（0-47用户区，48-63系统区）',
                'stack': '无硬件栈，使用软件实现'
            }
        }
    
    def get_compiler_info(self) -> Dict:
        """
        获取编译器信息
        
        Returns:
            Dict: 编译器信息
        """
        return {
            'name': 'ZH5001编译器（修正版）',
            'version': '1.0-final',
            'features': [
                '完整的ZH5001指令集支持',
                '正确的JZ指令偏移量计算',
                '复合指令预编译（LDINS、JUMP、LDTAB）',
                'DB数据定义和伪指令支持',
                '多种输出格式（HEX、JSON、Verilog）',
                '详细的错误检测和警告系统'
            ],
            'supported_formats': ['HEX', 'JSON', 'Verilog'],
            'max_program_size': 1024,
            'max_data_memory': 64
        }

# 创建全局服务实例
zh5001_service = ZH5001CompilerService()
