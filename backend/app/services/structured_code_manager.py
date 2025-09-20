"""
结构化代码管理器
解决编译器错误与大模型理解之间的行号不匹配问题
"""
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class CodeLine:
    """代码行结构"""
    line_number: int        # 全局行号（1开始）
    section: str           # DATA/CODE
    section_line: int      # 段内行号
    content_type: str      # variable/instruction/label/empty
    raw_content: str       # 原始内容
    parsed_content: Dict[str, Any]  # 解析后的结构化内容


class StructuredCodeManager:
    """结构化代码管理器"""

    def __init__(self):
        self.lines: List[CodeLine] = []
        self.variables: Dict[str, Dict] = {}
        self.instructions: List[Dict] = []

    def parse_assembly_code(self, assembly_text: str) -> List[CodeLine]:
        """解析汇编代码为结构化格式"""
        lines = assembly_text.strip().split('\n')
        parsed_lines = []
        current_section = None
        section_line_counter = 0

        for global_line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # 检查段标识符
            if stripped == 'DATA':
                current_section = 'DATA'
                section_line_counter = 0
            elif stripped == 'ENDDATA':
                current_section = None
            elif stripped == 'CODE':
                current_section = 'CODE'
                section_line_counter = 0
            elif stripped == 'ENDCODE':
                current_section = None
            else:
                section_line_counter += 1

            # 解析行内容
            parsed_content = self._parse_line_content(line, current_section)

            code_line = CodeLine(
                line_number=global_line_num,
                section=current_section or 'OTHER',
                section_line=section_line_counter,
                content_type=parsed_content['type'],
                raw_content=line,
                parsed_content=parsed_content
            )

            parsed_lines.append(code_line)

        self.lines = parsed_lines
        return parsed_lines

    def _parse_line_content(self, line: str, section: str) -> Dict[str, Any]:
        """解析单行内容"""
        stripped = line.strip()

        if not stripped or stripped.startswith(';'):
            return {'type': 'empty', 'comment': stripped}

        if section == 'DATA':
            # 解析变量定义: variable_name: DS000 1
            if ':' in stripped:
                parts = stripped.split(':')
                if len(parts) >= 2:
                    var_name = parts[0].strip()
                    rest = parts[1].strip().split()
                    return {
                        'type': 'variable',
                        'name': var_name,
                        'definition': rest[0] if rest else '',
                        'value': rest[1] if len(rest) > 1 else '',
                        'raw_def': parts[1].strip()
                    }

        elif section == 'CODE':
            # 解析指令
            if ':' in stripped and not stripped.startswith(' '):
                # 标号行
                label = stripped.replace(':', '').strip()
                return {
                    'type': 'label',
                    'name': label
                }
            elif stripped.startswith('    ') or line.startswith('    '):
                # 指令行（4空格缩进）
                instruction = stripped.strip().split()
                mnemonic = instruction[0] if instruction else ''
                operand = ' '.join(instruction[1:]) if len(instruction) > 1 else ''
                return {
                    'type': 'instruction',
                    'mnemonic': mnemonic,
                    'operand': operand
                }

        return {'type': 'unknown', 'content': stripped}

    def generate_structured_representation(self) -> str:
        """生成结构化表示（JSON格式）"""
        structured = {
            'format_version': '1.0',
            'total_lines': len(self.lines),
            'lines': []
        }

        for line in self.lines:
            line_data = {
                'line_number': line.line_number,
                'section': line.section,
                'section_line': line.section_line,
                'content_type': line.content_type,
                'raw_content': line.raw_content,
                'parsed': line.parsed_content
            }
            structured['lines'].append(line_data)

        return json.dumps(structured, indent=2, ensure_ascii=False)

    def get_line_by_number(self, line_num: int) -> Optional[CodeLine]:
        """根据行号获取代码行"""
        for line in self.lines:
            if line.line_number == line_num:
                return line
        return None

    def format_error_context(self, line_num: int, error_msg: str) -> str:
        """格式化错误上下文信息"""
        line = self.get_line_by_number(line_num)
        if not line:
            return f"行 {line_num}: {error_msg} (未找到对应行)"

        context = [
            f"🔴 编译错误详情:",
            f"全局行号: {line.line_number}",
            f"代码段: {line.section}",
            f"段内行号: {line.section_line}",
            f"内容类型: {line.content_type}",
            f"原始内容: `{line.raw_content.strip()}`",
            ""
        ]

        # 添加解析后的结构化信息
        if line.content_type == 'variable':
            parsed = line.parsed_content
            context.extend([
                f"变量名: {parsed.get('name', 'N/A')}",
                f"定义类型: {parsed.get('definition', 'N/A')}",
                f"值: {parsed.get('value', 'N/A')}",
                f"原始定义: {parsed.get('raw_def', 'N/A')}",
            ])
        elif line.content_type == 'instruction':
            parsed = line.parsed_content
            context.extend([
                f"指令: {parsed.get('mnemonic', 'N/A')}",
                f"操作数: {parsed.get('operand', 'N/A')}",
            ])

        context.extend([
            "",
            f"错误信息: {error_msg}",
            "",
            f"📋 上下文（第{max(1, line_num-2)}到{min(len(self.lines), line_num+2)}行）:"
        ])

        # 显示上下文行
        for i in range(max(0, line_num-3), min(len(self.lines), line_num+2)):
            current_line = self.lines[i]
            prefix = ">>> " if current_line.line_number == line_num else "    "
            context.append(f"{prefix}{current_line.line_number:2}: {current_line.raw_content}")

        return "\n".join(context)


def test_structured_code_manager():
    """测试结构化代码管理器"""
    test_code = """DATA
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

    manager = StructuredCodeManager()
    parsed = manager.parse_assembly_code(test_code)

    print("=== 结构化解析结果 ===")
    for line in parsed[:8]:  # 只显示前8行
        print(f"行{line.line_number}: {line.section}段 {line.content_type} - {line.raw_content.strip()}")

    print("\n=== 错误上下文示例 ===")
    error_context = manager.format_error_context(2, "无效的地址值")
    print(error_context)

    print("\n=== JSON格式示例 ===")
    json_repr = manager.generate_structured_representation()
    print(json_repr[:500] + "...")  # 只显示前500字符


if __name__ == "__main__":
    test_structured_code_manager()