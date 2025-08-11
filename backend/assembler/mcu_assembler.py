import re

class MCU_Assembler:
    """
    一个用于将自定义16位MCU汇编代码转换为机器码的汇编器。
    """
    def __init__(self):
        # 指令操作码和功能码定义 (基于对Sheet1和Sheet3的分析)
        # 格式: '助记符': [操作码(4位), 指令类型]
        self.opcodes = {
            'ADD': ['0100', 'data_proc'],
            'SUB': ['0010', 'data_proc'],
            'MOV': ['1101', 'data_proc'],
            'CMP': ['1010', 'data_proc'],
            'LDR': ['0101', 'mem_access'],
            'STR': ['0101', 'mem_access'], # LDR/STR 在这个设计中可能共享部分opcode
            'B':   ['1010', 'branch'],
            'AND': ['0000', 'data_proc'],
            'ORR': ['1100', 'data_proc'],
            'EOR': ['0001', 'data_proc'],
            'LSL': ['1101', 'shift'], # 逻辑左移, MOV的一个变种
            'LSR': ['1101', 'shift'], # 逻辑右移, MOV的一个变种
        }
        # 条件码定义
        self.cond_codes = {
            'EQ': '0000', 'NE': '0001', 'CS': '0010', 'CC': '0011',
            'MI': '0100', 'PL': '0101', 'VS': '0110', 'VC': '0111',
            'HI': '1000', 'LS': '1001', 'GE': '1010', 'LT': '1011',
            'GT': '1100', 'LE': '1101', 'AL': '1110',
        }

    def _parse_register(self, r_str):
        """将寄存器名 'rX' 转换为4位二进制"""
        num = int(r_str.lower().replace('r', ''))
        return format(num, '04b')

    def _parse_immediate(self, imm_str):
        """将立即数 '#X' 转换为8位二进制"""
        # 去除注释和多余空白
        imm_str = imm_str.split(';')[0].strip()
        num = int(imm_str.replace('#', ''))
        return format(num, '08b')

    def assemble_line(self, line):
        """汇编单行代码"""
        line = line.strip().upper()
        parts = re.split(r'[, ]+', line, 1)
        mnemonic = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        
        # 提取条件码，默认为 'AL' (无条件执行)
        cond = 'AL'
        for c in self.cond_codes:
            if mnemonic.endswith(c):
                cond = c
                mnemonic = mnemonic[:-len(c)]
                break

        if mnemonic not in self.opcodes:
            raise ValueError(f"Unknown instruction: {mnemonic}")

        op_info = self.opcodes[mnemonic]
        opcode = op_info[0]
        inst_type = op_info[1]
        
        cond_bin = self.cond_codes[cond]
        
        machine_code_bin = ""

        # 根据指令类型处理参数
        if inst_type == 'data_proc':
            # 格式: OP Cond Rd, Rn, #imm8  (简化模型)
            # 机器码: Cond(4) OP(4) Rn(4) Rd(4) imm8(8) -> 这里简化为16位
            # 根据Sheet3的逻辑，格式更像是: Cond(4) OP(4) Rd(4) imm(4)
            # 让我们采用一个更符合16位的简化结构：Cond(4) OP(4) Rd(4) imm(4)
            # 或者 Cond(4) OP(4) Rn(4) Rd(4)
            # 示例: MOV r0, #1 -> 机器码: 1110 1101 0000 0001
            args = [a.strip() for a in args_str.split(',')]
            rd = self._parse_register(args[0])
            if '#' in args[1]: # 立即数
                imm = self._parse_immediate(args[1])[-4:] # 取低4位作为示例
                # 假设Rn在这种情况下为0000
                rn = '0000'
                machine_code_bin = f"{cond_bin}{opcode}{rn}{rd}" # 这是一个假设，需要根据MCU设计文档精确调整
            else: # 寄存器
                rn = self._parse_register(args[1])
                machine_code_bin = f"{cond_bin}{opcode}{rn}{rd}"

        elif inst_type == 'branch':
            # 格式: B label
            # 机器码: Cond(4) OP(4) offset(8)
            # offset需要根据标签地址计算，这里暂时简化
            offset = format(int(args_str), '08b') # 假设直接给出了偏移量
            machine_code_bin = f"{cond_bin}{opcode}{offset}"

        # 其他指令类型...
        
        else:
             # 为简化，我们先用一个固定的0填充
            machine_code_bin = f"{cond_bin}{opcode}{'0'*8}"


        # 将16位二进制转换为4位十六进制
        hex_code = format(int(machine_code_bin, 2), '04X')
        return hex_code, machine_code_bin

    def assemble(self, code):
        """汇编多行代码"""
        machine_code = []
        lines = code.strip().split('\n')
        for line in lines:
            if not line or line.startswith(';'): # 跳过空行和注释
                continue
            hex_code, _ = self.assemble_line(line)
            machine_code.append(hex_code)
        return machine_code

# --- 使用示例 ---
assembler = MCU_Assembler()

# 这是一个控制LED灯闪烁的示例汇编代码
# 假设r0是计数器, I/O地址 0x10 是LED控制寄存器
assembly_code = """
; Simple LED Blink Program
MOV r0, #10      ;  r0 = 10 (loop counter)
LOOP:
  MOV r1, #1       ;  r1 = 1 (value to turn LED on)
  STR r1, [r2]     ;  假设 r2 存储了LED的地址, 将1写入
  SUB r0, r0, #1   ;  r0 = r0 - 1
  MOV r1, #0       ;  r1 = 0 (value to turn LED off)
  STR r1, [r2]
  CMP r0, #0       ;  compare r0 with 0
  BNE LOOP         ;  if r0 is not zero, jump to LOOP
"""

# 注意：上面的汇编器实现是一个简化的模型，
# 真实的LDR/STR和分支指令需要更复杂的地址计算，
# 但它展示了基本思路。
# 我们先用一个更简单的指令来测试
simple_assembly = "MOVAL r1, #5"
hex_result, bin_result = assembler.assemble_line(simple_assembly)

print(f"汇编代码: '{simple_assembly}'")
print(f"二进制机器码: {bin_result}")
print(f"十六进制机器码: {hex_result}")