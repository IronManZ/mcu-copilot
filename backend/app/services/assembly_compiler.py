import sys
import os
from typing import List

from assembler.mcu_assembler import MCU_Assembler

assembler = MCU_Assembler()

def assembly_to_machine_code(assembly: str) -> tuple[List[str], str]:
    # 支持的指令列表
    supported_instructions = [
        'ADD', 'SUB', 'MOV', 'CMP', 'LDR', 'STR', 'B', 'AND', 'ORR', 'EOR', 'LSL', 'LSR'
    ]
    
    # 去掉每行的分号及后面内容，并过滤掉标签行和无效指令
    lines = []
    for line in assembly.splitlines():
        code = line.split(';')[0].strip()
        # 跳过空行、标签（以冒号结尾）和无效指令
        if code and not code.endswith(':'):
            # 检查是否是支持的指令
            first_word = code.split()[0].upper() if code.split() else ""
            if first_word in supported_instructions or first_word.startswith('B'):  # 支持条件分支
                lines.append(code)
    
    filtered_assembly = '\n'.join(lines)
    machine_code = assembler.assemble(filtered_assembly)
    return machine_code, filtered_assembly