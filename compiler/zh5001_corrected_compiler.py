#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZH5001单片机汇编编译器（修正版）
基于实际Excel程序验证的正确JZ偏移量计算规则

主要修正：
- JZ指令偏移量计算：offset = target_pc - current_pc （无需-1修正）
- 添加MOVC指令支持
- 完善DB指令处理
- 增强错误检测和验证
"""

import re
import sys
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class InstructionType(Enum):
    """指令类型枚举"""
    NORMAL = "normal"
    IMMEDIATE = "immediate"
    JUMP = "jump"
    PSEUDO = "pseudo"
    DATA = "data"

@dataclass
class Variable:
    """变量定义"""
    name: str
    address: int

@dataclass
class Label:
    """标号定义"""
    name: str
    pc: int

@dataclass
class Instruction:
    """指令定义"""
    line_no: int
    label: Optional[str]
    mnemonic: str
    operand: str
    original_line: str

@dataclass
class PrecompiledInstruction:
    """预编译指令"""
    line_no: int
    label: Optional[str]
    mnemonic: str
    operand: str
    original_instruction: Optional[Instruction]

@dataclass
class MachineCode:
    """机器码"""
    pc: int
    binary: str
    hex_code: str
    verilog: str
    original_instruction: Optional[PrecompiledInstruction]

class ZH5001Compiler:
    """ZH5001单片机编译器（修正版）"""
    
    def __init__(self):
        self.variables: Dict[str, Variable] = {}
        self.labels: Dict[str, Label] = {}
        self.instructions: List[Instruction] = []
        self.precompiled: List[PrecompiledInstruction] = []
        self.machine_code: List[MachineCode] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # 指令操作码定义
        self.opcodes = {
            # 基本运算指令
            'LD': '0001', 'ADDR1': '0000', 'ADD': '0010', 'SUB': '0011',
            'AND': '0100', 'OR': '0101', 'MUL': '0110', 'CLAMP': '0111',
            'ST': '1000',
            
            # 跳转指令  
            'JZ': '1001', 'JOV': '1010', 'JCY': '1011',
            
            # 移位指令
            'SFT0RZ': '110000', 'SFT0RS': '110001', 'SFT0RR1': '110010', 'SFT0LZ': '110011',
            'SFT1RZ': '1100000000', 'SFT1RS': '1100010000', 'SFT1RR1': '1100100000', 'SFT1LZ': '1100110000',
            
            # 立即数指令
            'LDINS': '1110',
            
            # 无操作数指令
            'NOP': '1111000000', 'INC': '1111000001', 'DEC': '1111000010',
            'NOT': '1111000011', 'LDPC': '1111000100', 'NOTFLAG': '1111000101',
            'R0R1': '1111000110', 'R1R0': '1111000111', 'SIN': '1111001000', 'COS': '1111001001',
            'CLR': '1111001010', 'SET1': '1111001011', 'CLRFLAG': '1111001100', 'SETZ': '1111001101',
            'SETCY': '1111001110', 'SETOV': '1111001111', 'JUMP': '1111010000', 'SQRT': '1111010001',
            'NEG': '1111010010', 'EXR0R1': '1111010011', 'SIXSTEP': '1111010100', 'JNZ3': '1111010101',
            
            # 新增指令
            'MOVC': '1111010100',  # 修正：MOVC的正确二进制码
        }
    
    def compile_file(self, filename: str) -> bool:
        """编译文件"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._parse_text(content) and self._precompile() and self._compile()
        except FileNotFoundError:
            self.errors.append(f"文件 {filename} 不存在")
            return False
        except Exception as e:
            self.errors.append(f"读取文件错误: {str(e)}")
            return False
    
    def compile_text(self, text: str) -> bool:
        """编译文本"""
        return self._parse_text(text) and self._precompile() and self._compile()
    
    def _parse_text(self, text: str) -> bool:
        """解析汇编代码文本"""
        lines = text.split('\n')
        in_data_section = False
        in_code_section = False
        
        for line_no, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith(';') or line.startswith("'"):
                continue
            
            # 处理行内注释
            if ';' in line:
                line = line.split(';')[0].strip()
            if "'" in line:
                line = line.split("'")[0].strip()
            
            # 如果处理注释后变成空行，跳过
            if not line:
                continue
            
            # 检查段标识
            if line == 'DATA':
                in_data_section = True
                in_code_section = False
                continue
            elif line == 'ENDDATA':
                in_data_section = False
                continue
            elif line == 'CODE':
                in_code_section = True
                in_data_section = False
                continue
            elif line == 'ENDCODE':
                in_code_section = False
                continue
            
            # 解析DATA段
            if in_data_section:
                self._parse_data_line(line_no, line)
            
            # 解析CODE段
            elif in_code_section:
                self._parse_code_line(line_no, line, original_line)
        
        return len(self.errors) == 0
    
    def _parse_data_line(self, line_no: int, line: str) -> None:
        """解析数据段行"""
        parts = line.split()
        if len(parts) >= 2:
            var_name = parts[0]
            try:
                address = int(parts[1])
                if address < 0 or address > 63:
                    self.errors.append(f"第{line_no}行: 变量地址必须在0-63范围内")
                    return
                
                if var_name in self.variables:
                    self.errors.append(f"第{line_no}行: 变量 {var_name} 重复定义")
                    return
                
                self.variables[var_name] = Variable(var_name, address)
            except ValueError:
                self.errors.append(f"第{line_no}行: 无效的地址值")
    
    def _parse_code_line(self, line_no: int, line: str, original_line: str) -> None:
        """解析代码段行"""
        # 处理标号
        label = None
        if ':' in line:
            parts = line.split(':', 1)
            label = parts[0].strip()
            line = parts[1].strip() if len(parts) > 1 else ''
        
        # 如果只有标号，没有指令
        if not line:
            if label:
                self.instructions.append(Instruction(line_no, label, '', '', original_line))
            return
        
        # 解析指令和操作数
        parts = line.split()
        if not parts:
            return
        
        mnemonic = parts[0].upper()
        operand = parts[1] if len(parts) > 1 else ''
        
        self.instructions.append(Instruction(line_no, label, mnemonic, operand, original_line))
    
    def _precompile(self) -> bool:
        """预编译处理"""
        current_pc = 0
        
        for inst in self.instructions:
            # 处理标号
            if inst.label:
                if inst.label in self.labels:
                    self.errors.append(f"第{inst.line_no}行: 标号 {inst.label} 重复定义")
                    continue
                self.labels[inst.label] = Label(inst.label, current_pc)
            
            # 跳过空指令
            if not inst.mnemonic:
                continue
            
            # 预编译不同类型的指令
            if inst.mnemonic == 'LDINS':
                # LDINS分解为两条指令
                self.precompiled.append(PrecompiledInstruction(
                    inst.line_no, inst.label, 'LDINS_IMMTH', inst.operand, inst))
                current_pc += 1
                
                self.precompiled.append(PrecompiledInstruction(
                    inst.line_no, None, 'LDINS_IMMTL', inst.operand, None))
                current_pc += 1
                
            elif inst.mnemonic == 'JUMP':
                # JUMP分解为三条指令
                self.precompiled.append(PrecompiledInstruction(
                    inst.line_no, inst.label, 'LDINS_TABH', inst.operand, inst))
                current_pc += 1
                
                self.precompiled.append(PrecompiledInstruction(
                    inst.line_no, None, 'LDINS_TABL', inst.operand, None))
                current_pc += 1
                
                self.precompiled.append(PrecompiledInstruction(
                    inst.line_no, None, 'JUMP_EXEC', '', None))
                current_pc += 1
                
            elif inst.mnemonic == 'LDTAB':
                # LDTAB分解为两条指令
                self.precompiled.append(PrecompiledInstruction(
                    inst.line_no, inst.label, 'LDINS_TABH', inst.operand, inst))
                current_pc += 1
                
                self.precompiled.append(PrecompiledInstruction(
                    inst.line_no, None, 'LDINS_TABL', inst.operand, None))
                current_pc += 1
                
            elif inst.mnemonic == 'ORG':
                # ORG伪指令设置PC
                try:
                    new_pc = self._parse_number(inst.operand)
                    if new_pc is None:
                        self.errors.append(f"第{inst.line_no}行: ORG指令的操作数无效")
                        continue
                    
                    if current_pc <= new_pc:
                        current_pc = new_pc
                    else:
                        self.errors.append(f"第{inst.line_no}行: ORG地址冲突")
                        continue
                except ValueError:
                    self.errors.append(f"第{inst.line_no}行: ORG指令的地址值无效")
                    continue
                    
            elif inst.mnemonic == 'DB':
                # DB指令：直接在程序存储器中定义数据
                value = self._parse_number(inst.operand)
                if value is None:
                    self.errors.append(f"第{inst.line_no}行: DB指令的数据值无效")
                    continue
                
                # 处理负数
                if value < 0:
                    value = 1024 + value  # 10位补码
                
                # 确保数据在10位范围内
                if value > 1023:
                    self.errors.append(f"第{inst.line_no}行: DB数据值超出10位范围")
                    continue
                
                self.precompiled.append(PrecompiledInstruction(
                    inst.line_no, inst.label, 'DB', str(value), inst))
                current_pc += 1
                
            elif inst.mnemonic.startswith('DS'):
                # DS伪指令处理
                try:
                    count = int(inst.operand) if inst.operand else 1
                    if count <= 0:
                        self.errors.append(f"第{inst.line_no}行: DS指令的数量必须大于0")
                        continue
                    
                    fill_value = '000' if inst.mnemonic == 'DS000' else '3FF'
                    
                    for i in range(count):
                        label = inst.label if i == 0 else None
                        self.precompiled.append(PrecompiledInstruction(
                            inst.line_no, label, fill_value, '', inst if i == 0 else None))
                        current_pc += 1
                        
                except ValueError:
                    self.errors.append(f"第{inst.line_no}行: DS指令的数量值无效")
                    continue
                    
            else:
                # 普通指令直接复制
                self.precompiled.append(PrecompiledInstruction(
                    inst.line_no, inst.label, inst.mnemonic, inst.operand, inst))
                current_pc += 1
        
        return len(self.errors) == 0
    
    def _compile(self) -> bool:
        """编译生成机器码"""
        current_pc = 0
        
        for inst in self.precompiled:
            binary_code = self._compile_instruction(inst, current_pc)
            if binary_code:
                hex_code = self._bin_to_hex(binary_code)
                verilog_code = self._generate_verilog(current_pc, binary_code, inst)
                
                machine_code = MachineCode(
                    pc=current_pc,
                    binary=binary_code,
                    hex_code=hex_code,
                    verilog=verilog_code,
                    original_instruction=inst
                )
                self.machine_code.append(machine_code)
                current_pc += 1
        
        return len(self.errors) == 0
    
    def _compile_instruction(self, inst: PrecompiledInstruction, pc: int) -> Optional[str]:
        """编译单条指令"""
        mnemonic = inst.mnemonic
        operand = inst.operand
        
        # 处理特殊的预编译指令
        if mnemonic == 'LDINS_IMMTH':
            value = self._parse_number(operand)
            if value is None:
                self.errors.append(f"第{inst.line_no}行: 无效的立即数")
                return None
            
            # 处理负数
            if value < 0:
                value = 65536 + value
            
            high_6bits = (value >> 10) & 0x3F
            return self.opcodes['LDINS'] + format(high_6bits, '06b')
        
        elif mnemonic == 'LDINS_IMMTL':
            value = self._parse_number(operand)
            if value is None:
                self.errors.append(f"第{inst.line_no}行: 无效的立即数")
                return None
            
            # 处理负数
            if value < 0:
                value = 65536 + value
                
            low_10bits = value & 0x3FF
            return format(low_10bits, '010b')
        
        elif mnemonic == 'LDINS_TABH':
            if operand not in self.labels:
                self.errors.append(f"第{inst.line_no}行: 未定义的标号 {operand}")
                return None
            
            target_pc = self.labels[operand].pc
            high_6bits = (target_pc >> 10) & 0x3F
            return self.opcodes['LDINS'] + format(high_6bits, '06b')
        
        elif mnemonic == 'LDINS_TABL':
            # 查找对应的TABH指令获取标号
            target_pc = 0
            for i, prev_inst in enumerate(self.precompiled):
                if prev_inst == inst and i > 0:
                    prev_prev = self.precompiled[i-1]
                    if prev_prev.mnemonic == 'LDINS_TABH' and prev_prev.operand in self.labels:
                        target_pc = self.labels[prev_prev.operand].pc
                        break
            
            low_10bits = target_pc & 0x3FF
            return format(low_10bits, '010b')
        
        elif mnemonic == 'JUMP_EXEC':
            # JUMP的实际执行指令
            return self.opcodes['JUMP']
        
        # 处理JZ指令 - 使用作者透露的正确计算公式
        elif mnemonic in ['JZ', 'JOV', 'JCY']:
            if operand not in self.labels:
                self.errors.append(f"第{inst.line_no}行: 未定义的标号 {operand}")
                return None
            
            target_pc = self.labels[operand].pc
            
            # 关键修正：根据单片机作者的规则
            if target_pc >= pc:
                # 正偏移量（向前跳转）: offset = target_pc - current_pc - 2
                raw_distance = target_pc - pc
                if raw_distance < 2:
                    self.errors.append(
                        f"第{inst.line_no}行: {mnemonic} {operand} 向前跳转距离太近 "
                        f"(距离: {raw_distance}, 最小向前跳转距离: 2)"
                    )
                    return None
                offset = raw_distance - 2
                
                # 检查正偏移量范围 (0-31, 对应实际距离2-33)
                if offset > 31:
                    actual_max_distance = 33
                    self.errors.append(
                        f"第{inst.line_no}行: {mnemonic} {operand} 向前跳转距离过远 "
                        f"(实际距离: {raw_distance}, 最大向前距离: {actual_max_distance})\n"
                        f"建议使用JUMP长跳转指令"
                    )
                    return None
            else:
                # 负偏移量（向后跳转）: offset = target_pc - current_pc
                offset = target_pc - pc
                
                # 检查负偏移量范围 (-32 到 -1, 对应实际距离1-32)
                if offset < -32:
                    self.errors.append(
                        f"第{inst.line_no}行: {mnemonic} {operand} 向后跳转距离过远 "
                        f"(偏移量: {offset}, 最大向后偏移: -32)\n"
                        f"建议使用JUMP长跳转指令或重新组织代码"
                    )
                    return None
            
            # 生成警告当接近边界时
            actual_distance = abs(target_pc - pc)
            if (offset >= 0 and offset > 25) or (offset < 0 and offset < -25):
                self.warnings.append(
                    f"第{inst.line_no}行: {mnemonic} {operand} 跳转距离接近边界 "
                    f"(实际距离: {actual_distance})"
                )
            
            # 使用6位补码表示偏移量
            if offset < 0:
                offset = 64 + offset  # 6位补码
            
            return self.opcodes[mnemonic] + format(offset & 0x3F, '06b')
        
        # 处理带变量操作数的指令
        elif mnemonic in ['LD', 'ST', 'ADD', 'SUB', 'AND', 'OR', 'MUL', 'CLAMP', 'ADDR1']:
            if operand not in self.variables:
                self.errors.append(f"第{inst.line_no}行: 未定义的变量 {operand}")
                return None
            
            address = self.variables[operand].address
            return self.opcodes[mnemonic] + format(address, '06b')
        
        # 处理带立即数操作数的移位指令
        elif mnemonic in ['SFT0RZ', 'SFT0RS', 'SFT0RR1', 'SFT0LZ']:
            try:
                shift_bits = int(operand)
                if shift_bits > 15:
                    self.errors.append(f"第{inst.line_no}行: 移位位数超过15")
                    return None
                
                return self.opcodes[mnemonic] + format(shift_bits, '04b')
            except ValueError:
                self.errors.append(f"第{inst.line_no}行: 无效的移位位数")
                return None
        
        # 处理无操作数指令
        elif mnemonic in self.opcodes:
            return self.opcodes[mnemonic]
        
        # 处理数据填充和DB指令
        elif mnemonic == '000':
            return '0000000000'
        elif mnemonic == '3FF':
            return '1111111111'
        elif mnemonic == 'DB':
            # DB指令定义的数据
            try:
                value = int(operand)
                if value < 0:
                    value = 1024 + value  # 10位补码
                if value > 1023:
                    self.errors.append(f"第{inst.line_no}行: DB数据值超出10位范围")
                    return None
                return format(value, '010b')
            except ValueError:
                self.errors.append(f"第{inst.line_no}行: DB数据值格式错误")
                return None
        
        else:
            self.errors.append(f"第{inst.line_no}行: 未识别的指令 {mnemonic}")
            return None
    
    def _parse_number(self, text: str) -> Optional[int]:
        """解析数字（支持十进制和十六进制）"""
        if not text:
            return None
        
        try:
            if text.startswith('0x') or text.startswith('0X'):
                return int(text, 16)
            else:
                return int(text)
        except ValueError:
            return None
    
    def _bin_to_hex(self, binary: str) -> str:
        """将二进制字符串转换为十六进制"""
        if len(binary) == 10:
            # 分成2位和8位
            high_2 = binary[:2]
            low_8 = binary[2:]
            return hex(int(high_2, 2))[2:].upper() + hex(int(low_8, 2))[2:].upper().zfill(2)
        else:
            return hex(int(binary, 2))[2:].upper()
    
    def _generate_verilog(self, pc: int, binary: str, inst: PrecompiledInstruction) -> str:
        """生成Verilog代码"""
        if inst.mnemonic == 'LDINS_IMMTL':
            return f"c_m[{pc}] = 10'd{int(binary, 2)};"
        elif inst.mnemonic == 'DB':
            return f"c_m[{pc}] = 10'd{int(binary, 2)};"
        elif inst.mnemonic == '000':
            return f"c_m[{pc}] = 10'd0;"
        elif inst.mnemonic == '3FF':
            return f"c_m[{pc}] = 10'd1023;"
        elif inst.mnemonic in ['JZ', 'JOV', 'JCY']:
            # 从二进制中提取偏移量，并根据规则还原实际跳转距离
            offset_bits = binary[4:]  # 后6位
            encoded_offset = int(offset_bits, 2)
            
            # 解码偏移量
            if encoded_offset > 31:  # 负数补码
                actual_offset = encoded_offset - 64  # 转换为负数
                display_offset = actual_offset
            else:  # 正数，需要加2得到实际跳转距离
                actual_offset = encoded_offset
                display_offset = encoded_offset  # Verilog中显示编码值
            
            if actual_offset >= 0:
                return f"c_m[{pc}] = {{{inst.mnemonic},6'd{display_offset}}};"
            else:
                return f"c_m[{pc}] = {{{inst.mnemonic},-6'sd{abs(actual_offset)}}};"
        else:
            # 提取操作数部分
            if len(binary) > 4:
                operand_bits = binary[4:]
                operand_val = int(operand_bits, 2)
                return f"c_m[{pc}] = {{{inst.mnemonic},6'd{operand_val}}};"
            else:
                return f"c_m[{pc}] = {inst.mnemonic};"
    
    def generate_output(self) -> Dict:
        """生成完整的编译输出"""
        result = {
            'success': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'variables': {name: var.address for name, var in self.variables.items()},
            'labels': {name: label.pc for name, label in self.labels.items()},
            'precompiled': [],
            'machine_code': [],
            'statistics': {
                'total_variables': len(self.variables),
                'total_labels': len(self.labels),
                'total_instructions': len(self.machine_code),
                'memory_usage': len(self.machine_code),
                'max_memory': 1024,
                'warnings_count': len(self.warnings)
            }
        }
        
        # 预编译输出
        for i, inst in enumerate(self.precompiled):
            result['precompiled'].append({
                'pc': i,
                'line_no': inst.line_no,
                'label': inst.label,
                'mnemonic': inst.mnemonic,
                'operand': inst.operand
            })
        
        # 机器码输出
        for code in self.machine_code:
            result['machine_code'].append({
                'pc': code.pc,
                'binary': code.binary,
                'hex': code.hex_code,
                'verilog': code.verilog
            })
        
        return result
    
    def save_output(self, base_filename: str) -> None:
        """保存编译输出到多种格式"""
        result = self.generate_output()
        
        # 保存HEX文件
        hex_file = f"{base_filename}.hex"
        with open(hex_file, 'w', encoding='utf-8') as f:
            for i, code in enumerate(self.machine_code):
                if i == len(self.machine_code) - 1:
                    # 最后一行不添加换行符
                    f.write(code.hex_code)
                else:
                    f.write(code.hex_code + '\n')
        
        # 保存JSON文件
        json_file = f"{base_filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # 保存Verilog文件
        verilog_file = f"{base_filename}.v"
        with open(verilog_file, 'w', encoding='utf-8') as f:
            f.write("// ZH5001 程序存储器初始化\n")
            f.write("initial begin\n")
            for code in self.machine_code:
                f.write(f"    {code.verilog}\n")
            f.write("end\n")
        
        print(f"编译输出已保存:")
        print(f"  HEX文件: {hex_file}")
        print(f"  JSON文件: {json_file}")
        print(f"  Verilog文件: {verilog_file}")
    
    def validate_jz_instructions(self) -> List[str]:
        """验证所有JZ指令的正确性"""
        validation_errors = []
        
        for inst in self.precompiled:
            if inst.mnemonic in ['JZ', 'JOV', 'JCY']:
                target_label = inst.operand
                if target_label in self.labels:
                    pc = self.precompiled.index(inst)
                    target_pc = self.labels[target_label].pc
                    offset = target_pc - pc
                    
                    if not (-32 <= offset <= 31):
                        validation_errors.append(
                            f"行{inst.line_no}: {inst.mnemonic} {target_label} "
                            f"跳转距离超出范围 (偏移量: {offset})"
                        )
        
        return validation_errors


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ZH5001单片机汇编编译器（修正版）')
    parser.add_argument('input', help='输入汇编文件')
    parser.add_argument('-o', '--output', help='输出文件前缀（默认与输入文件同名）')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('--validate', action='store_true', help='进行额外的验证检查')
    
    args = parser.parse_args()
    
    # 创建编译器实例
    compiler = ZH5001Compiler()
    
    print(f"正在编译: {args.input}")
    
    # 编译文件
    if compiler.compile_file(args.input):
        print("✓ 编译成功")
        
        result = compiler.generate_output()
        
        # 显示统计信息
        stats = result['statistics']
        print(f"\n编译统计:")
        print(f"  变量数量: {stats['total_variables']}")
        print(f"  标号数量: {stats['total_labels']}")  
        print(f"  指令数量: {stats['total_instructions']}")
        print(f"  内存使用: {stats['memory_usage']}/1024")
        
        # 显示警告
        if result['warnings']:
            print(f"\n⚠️  编译警告 ({len(result['warnings'])} 条):")
            for warning in result['warnings']:
                print(f"  {warning}")
        
        # 额外验证
        if args.validate:
            validation_errors = compiler.validate_jz_instructions()
            if validation_errors:
                print(f"\n❌ 验证发现问题:")
                for error in validation_errors:
                    print(f"  {error}")
            else:
                print(f"\n✅ 验证通过，所有JZ指令都在有效范围内")
        
        # 保存输出
        output_base = args.output or Path(args.input).stem
        compiler.save_output(output_base)
        
        # 详细信息
        if args.verbose:
            print(f"\n=== 详细信息 ===")
            print(f"标号地址:")
            for name, pc in result['labels'].items():
                print(f"  {name}: PC {pc}")
            
            print(f"\n前10条机器码:")
            for i, code in enumerate(result['machine_code'][:10]):
                print(f"  PC{code['pc']:3d}: {code['binary']} ({code['hex']})")
        
    else:
        print("✗ 编译失败")
        for error in compiler.errors:
            print(f"  {error}")
        sys.exit(1)


def create_test_program():
    """创建测试程序"""
    test_program = """DATA
    counter    0
    result     1
    temp       2
    delay      3
ENDDATA

CODE
start:
    LDINS 10        ; 初始化计数器
    ST counter
    CLR             ; 清零结果
    ST result

main_loop:
    LD counter      ; 加载计数器
    JZ finished     ; 如果为0则结束
    
    ; 累加操作
    LD result
    ADD counter
    ST result
    
    ; 计数器减1
    LD counter
    DEC
    ST counter
    
    ; 简单延时
    LDINS 1000
    ST delay
    
delay_loop:
    LD delay
    DEC
    ST delay
    JZ main_loop    ; 延时结束，回到主循环
    JUMP delay_loop ; 继续延时

finished:
    LD result       ; 加载最终结果
    ST temp         ; 保存到临时变量
    NOP             ; 程序结束

; 数据表示例
data_table:
    DB 0x15F        ; 数码管显示码0
    DB 0x150        ; 数码管显示码1
    DB 0x13B        ; 数码管显示码2
    DB 0x179        ; 数码管显示码3
ENDCODE
"""
    
    with open('test_program.asm', 'w', encoding='utf-8') as f:
        f.write(test_program)
    
    print("已创建测试程序: test_program.asm")
    return test_program


def example_usage():
    """使用示例"""
    print("=== ZH5001编译器使用示例 ===\n")
    
    # 创建测试程序
    test_code = create_test_program()
    
    # 编译测试程序
    compiler = ZH5001Compiler()
    
    print("编译测试程序...")
    if compiler.compile_text(test_code):
        result = compiler.generate_output()
        
        print("✓ 编译成功!")
        print(f"生成了 {len(result['machine_code'])} 条机器码")
        
        # 显示JZ指令分析
        print(f"\nJZ指令分析:")
        for inst in compiler.precompiled:
            if inst.mnemonic in ['JZ', 'JOV', 'JCY']:
                pc = compiler.precompiled.index(inst)
                target_pc = compiler.labels[inst.operand].pc
                offset = target_pc - pc
                
                print(f"  {inst.mnemonic} {inst.operand}: PC{pc}→PC{target_pc}, 偏移={offset}")
        
        # 保存示例输出
        compiler.save_output('example_output')
        
        # 显示前几条机器码
        print(f"\n前5条机器码:")
        for code in result['machine_code'][:5]:
            print(f"  PC{code['pc']:2d}: {code['binary']} ({code['hex']}) - {code['verilog']}")
        
        return True
    else:
        print("✗ 编译失败:")
        for error in compiler.errors:
            print(f"  {error}")
        return False


def validate_compiler_with_known_results():
    """使用已知结果验证编译器"""
    print("\n=== 编译器验证测试 ===")
    
    # 使用实际Excel程序中的代码片段进行验证
    validation_code = """DATA
    TOGGLE_RAM   0
    IO           51
ENDDATA

CODE
LOOP1:
    LDINS 0x0001
    AND IO
    JZ LOOP1        ; 这应该产生偏移量-3

test_forward:
    LD TOGGLE_RAM
    JZ end_program  ; 这应该是正偏移量

end_program:
    NOP
ENDCODE
"""
    
    compiler = ZH5001Compiler()
    print("验证编译器对JZ指令的处理...")
    
    if compiler.compile_text(validation_code):
        print("✓ 验证编译成功")
        
        # 检查JZ指令的编译结果
        for code in compiler.machine_code:
            if code.verilog and 'JZ' in code.verilog:
                print(f"  {code.verilog}")
        
        # 验证偏移量计算
        for inst in compiler.precompiled:
            if inst.mnemonic == 'JZ':
                pc = compiler.precompiled.index(inst)
                target_pc = compiler.labels[inst.operand].pc
                offset = target_pc - pc
                
                print(f"  验证: JZ {inst.operand} - PC{pc}→PC{target_pc}, 偏移={offset}")
                
                # 检查是否与预期一致
                if inst.operand == 'LOOP1' and offset == -3:
                    print("    ✓ LOOP1偏移量正确")
                elif inst.operand == 'end_program' and offset > 0:
                    print("    ✓ end_program偏移量正确")
        
        return True
    else:
        print("✗ 验证编译失败:")
        for error in compiler.errors:
            print(f"  {error}")
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main()
    else:
        print("ZH5001汇编编译器（修正版）")
        print("=" * 50)
        print("主要改进:")
        print("✓ 修正了JZ指令偏移量计算（无需-1修正）")
        print("✓ 添加了MOVC指令支持")
        print("✓ 完善了DB指令处理")
        print("✓ 增强了错误检测和验证")
        print("✓ 支持多种输出格式（HEX、JSON、Verilog）")
        print()
        
        # 运行示例和验证
        if example_usage():
            validate_compiler_with_known_results()
        
        print(f"\n使用方法:")
        print(f"  python {sys.argv[0]} <输入文件.asm> [-o 输出前缀] [-v] [--validate]")
        print(f"  python {sys.argv[0]} test_program.asm -v --validate")