import os
import re
from dashscope import Generation
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def nl_to_assembly(requirement: str) -> tuple[str, str]:
    api_key = os.environ.get("QIANWEN_APIKEY")
    if not api_key:
        raise Exception("请在 .env 或环境变量中配置 QIANWEN_APIKEY")
    
    # 直接定位到 backend/assembler/mcu_assembler.py
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    assembler_path = os.path.join(backend_dir, 'assembler', 'mcu_assembler.py')
    with open(assembler_path, 'r', encoding='utf-8') as f:
        assembler_code = f.read()
    
    prompt = (
        "你是一个16位MCU汇编代码专家。"
        "下面是本MCU的汇编器Python实现源码，请严格参考其指令集、语法和格式生成汇编代码：\n"
        "----- 汇编器源码开始 -----\n"
        f"{assembler_code}\n"
        "----- 汇编器源码结束 -----\n"
        f"需求：{requirement}\n\n"
        "请严格按照以下格式输出，不要添加任何其他内容：\n\n"
        "思考过程：\n"
        "[在这里写你的分析思路，包括寄存器分配、算法设计等]\n\n"
        "汇编代码：\n"
        "```assembly\n"
        "[在这里写纯汇编代码，每行一条指令，不要包含注释、标签或其他内容]\n"
        "```\n\n"
        "注意：\n"
        "1. 只使用支持的指令：MOV, ADD, SUB, CMP, LDR, STR, B, AND, ORR, EOR, LSL, LSR\n"
        "2. 不要使用ORG、NOP等不支持的指令\n"
        "3. 不要使用标签（如LOOP:）\n"
        "4. 汇编代码部分必须是纯指令，不要包含思考过程\n"
    )
    
    response = Generation.call(
        model="qwen-turbo",
        api_key=api_key,
        messages=[{"role": "user", "content": prompt}]
    )
    
    if 'output' in response and 'text' in response['output']:
        full_response = response['output']['text']
        
        # 分离思考过程和汇编代码
        thought, assembly = parse_response(full_response)
        return thought, assembly
    else:
        raise Exception(f"大模型API返回异常: {response}")

def parse_response(response: str) -> tuple[str, str]:
    """解析大模型响应，分离思考过程和汇编代码"""
    # 首先尝试用markdown代码块提取汇编代码
    code_block_match = re.search(r'```(?:assembly)?\s*\n(.*?)\n```', response, re.DOTALL)
    
    if code_block_match:
        assembly = code_block_match.group(1).strip()
        # 思考过程是代码块之前的内容，去掉"思考过程："等标记
        thought_part = response[:code_block_match.start()].strip()
        # 清理思考过程，去掉格式标记
        thought = re.sub(r'^思考过程：?\s*', '', thought_part, flags=re.MULTILINE)
        thought = thought.strip()
    else:
        # 如果没有代码块，尝试用关键词分割
        # 寻找"汇编代码："或类似标记
        assembly_marker = re.search(r'汇编代码：?\s*', response, re.IGNORECASE)
        if assembly_marker:
            assembly_start = assembly_marker.end()
            assembly = response[assembly_start:].strip()
            thought = response[:assembly_marker.start()].strip()
            # 清理思考过程
            thought = re.sub(r'^思考过程：?\s*', '', thought, flags=re.MULTILINE)
            thought = thought.strip()
        else:
            # 最后的fallback：按指令关键词分割
            lines = response.split('\n')
            assembly_lines = []
            thought_lines = []
            in_assembly = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 检查是否是汇编指令
                if re.match(r'^(MOV|ADD|SUB|CMP|LDR|STR|B|AND|ORR|EOR|LSL|LSR)\s+', line, re.IGNORECASE):
                    in_assembly = True
                    assembly_lines.append(line)
                elif in_assembly and line and not line.startswith(';') and not line.startswith('-'):
                    # 如果已经在汇编部分，且不是注释或列表项，继续添加
                    assembly_lines.append(line)
                else:
                    thought_lines.append(line)
            
            thought = '\n'.join(thought_lines).strip()
            assembly = '\n'.join(assembly_lines).strip()
    
    # 最后清理：确保汇编代码只包含指令
    if assembly:
        # 过滤掉非指令行
        assembly_lines = []
        for line in assembly.split('\n'):
            line = line.strip()
            if line and not line.startswith(';') and not line.startswith('-') and not line.startswith('```'):
                # 检查是否包含指令关键词
                if any(keyword in line.upper() for keyword in ['MOV', 'ADD', 'SUB', 'CMP', 'LDR', 'STR', 'B', 'AND', 'ORR', 'EOR', 'LSL', 'LSR']):
                    assembly_lines.append(line)
        assembly = '\n'.join(assembly_lines)
    
    return thought, assembly 