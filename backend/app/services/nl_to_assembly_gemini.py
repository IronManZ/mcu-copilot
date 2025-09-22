import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# 引入本地ZH5001编译服务进行本地编译校验
from app.services.compiler.zh5001_service import ZH5001CompilerService

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def nl_to_assembly_gemini(requirement: str) -> tuple[str, str]:
    """使用Gemini模型生成ZH5001汇编代码"""
    
    # 配置Gemini API
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise Exception("请在 .env 或环境变量中配置 GOOGLE_API_KEY")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    # 加载系统提示词
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    system_prompt_path = os.path.join(project_root, 'fpga-simulator', 'zh5001_programming_assistant.md')
    if not os.path.exists(system_prompt_path):
        raise Exception(f"系统提示词文件不存在: {system_prompt_path}")
    
    with open(system_prompt_path, 'r', encoding='utf-8') as f:
        system_prompt_core = f.read()
    
    # 构建完整的提示词
    full_prompt = f"""
{system_prompt_core}

## 当前任务
请根据以下需求生成ZH5001汇编代码：

**需求描述：** {requirement}

## 严格输出要求
1. **必须使用正确的ZH5001指令集**，不要使用不存在的指令
2. **变量地址分配**：用户区0-47，特殊寄存器48-63
3. **跳转距离限制**：JZ/JOV/JCY跳转必须在±32范围内
4. **指令语法**：SUB指令需要操作数，格式为 `SUB 变量名`
5. **程序结构**：必须包含DATA段和CODE段
6. **输出格式**：严格按照以下格式输出

## 输出格式
```
思考过程：
[详细分析你的设计思路、变量分配、跳转设计等]

汇编代码：
```asm
DATA
    ; 在此定义变量
ENDDATA

CODE
start:
    ; 在此编写指令
ENDCODE
```
```

请确保生成的代码能够通过ZH5001编译器编译，避免使用不存在的指令和错误的语法。
"""
    
    # 生成 → 本地编译校验 → 如失败则反馈错误让模型修正，最多重试5次
    compiler_service = ZH5001CompilerService()
    thought: str = ""
    assembly: str = ""
    previous_errors = []  # 记录之前的错误，避免重复
    all_thoughts = []  # 记录所有尝试的思考过程

    for attempt in range(5):
        try:
            print(f"第{attempt + 1}次尝试使用Gemini生成代码...")
            
            # 调用Gemini API
            response = model.generate_content(full_prompt)
            
            if not response.text:
                raise Exception("Gemini API返回空响应")
            
            full_response = response.text
            current_thought, current_assembly = parse_gemini_response(full_response)
            
            # 记录当前尝试的思考过程
            if current_thought:
                all_thoughts.append(f"第{attempt + 1}次尝试：{current_thought}")
            
            # 更新最终结果
            thought = current_thought
            assembly = current_assembly
            
            # 本地尝试编译
            compile_result = compiler_service.compile_assembly(assembly)
            if compile_result.get('success'):
                # 成功编译，返回完整的思考过程
                if len(all_thoughts) > 1:
                    thought = "\n\n".join(all_thoughts)
                return thought, assembly
            
            # 失败则将错误反馈给模型，继续迭代
            current_errors = compile_result.get('errors', [])
            current_warnings = compile_result.get('warnings', [])
            
            # 构建详细的错误反馈
            error_context = f"第{attempt + 1}次编译尝试失败：\n"
            if current_errors:
                error_context += f"编译错误 ({len(current_errors)}个)：\n"
                for i, error in enumerate(current_errors, 1):
                    error_context += f"{i}. {error}\n"
            
            if current_warnings:
                error_context += f"\n编译警告 ({len(current_warnings)}个)：\n"
                for i, warning in enumerate(current_warnings, 1):
                    error_context += f"{i}. {warning}\n"
            
            # 添加修正建议
            correction_guidance = "\n修正建议：\n"
            if any("跳转距离" in error for error in current_errors):
                correction_guidance += "- JZ/JOV/JCY跳转距离必须在±32范围内，超出时使用JUMP\n"
            if any("未定义的变量" in error for error in current_errors):
                correction_guidance += "- 所有变量必须在DATA段中定义\n"
            if any("未识别的指令" in error for error in current_errors):
                correction_guidance += "- 只使用ZH5001支持的指令助记符\n"
            if any("立即数" in error for error in current_errors):
                correction_guidance += "- 立即数只能用于LDINS指令\n"
            if any("SUB" in error for error in current_errors):
                correction_guidance += "- SUB指令格式：SUB 变量名，确保操作数正确\n"
            
            # 如果是重试，添加之前的问题对比
            if attempt > 0:
                error_context += f"\n之前尝试的问题：\n"
                for i, prev_error in enumerate(previous_errors, 1):
                    error_context += f"尝试{i}: {prev_error}\n"
            
            # 更新错误历史
            previous_errors = current_errors.copy()
            
            # 构建修正提示词
            fix_prompt = f"""
{error_context}
{correction_guidance}

请基于上述错误信息修正代码，确保：
1. 所有变量在DATA段中定义
2. 跳转距离在允许范围内
3. 使用正确的指令格式和语法
4. 避免之前尝试中的错误
5. 严格按照ZH5001指令集规范

请按相同格式输出修正后的完整汇编代码与思考过程。
"""
            
            # 更新提示词，包含错误信息
            full_prompt = f"""
{system_prompt_core}

## 当前任务
请根据以下需求生成ZH5001汇编代码：

**需求描述：** {requirement}

## 编译错误反馈
{fix_prompt}

## 严格输出要求
1. **必须使用正确的ZH5001指令集**，不要使用不存在的指令
2. **变量地址分配**：用户区0-47，特殊寄存器48-63
3. **跳转距离限制**：JZ/JOV/JCY跳转必须在±32范围内
4. **指令语法**：SUB指令需要操作数，格式为 `SUB 变量名`
5. **程序结构**：必须包含DATA段和CODE段
6. **输出格式**：严格按照以下格式输出

## 输出格式
```
思考过程：
[详细分析你的设计思路、变量分配、跳转设计等]

汇编代码：
```asm
DATA
    ; 在此定义变量
ENDDATA

CODE
start:
    ; 在此编写指令
ENDCODE
```
```

请确保生成的代码能够通过ZH5001编译器编译，避免使用不存在的指令和错误的语法。
"""
            
        except Exception as e:
            print(f"Gemini API调用异常: {e}")
            if attempt == 0:
                raise Exception(f"Gemini API调用失败: {e}")
            # 如果是重试失败，继续下一次尝试
    
    # 5次修正仍失败，则返回最后一次结果（携带错误信息由上层处理）
    # 但返回完整的思考过程
    if len(all_thoughts) > 1:
        thought = "\n\n".join(all_thoughts)
    return thought, assembly

def parse_gemini_response(response: str) -> tuple[str, str]:
    """解析Gemini响应，分离思考过程和汇编代码"""
    # 优先用markdown代码块提取
    code_block_match = re.search(r'```(?:asm|assembly)?\s*\n(.*?)\n```', response, re.DOTALL | re.IGNORECASE)
    
    if code_block_match:
        assembly = code_block_match.group(1).strip()
        # 思考过程取代码块之前内容
        thought_part = response[:code_block_match.start()].strip()
        thought = re.sub(r'^思考过程：?\s*', '', thought_part, flags=re.MULTILINE)
        thought = thought.strip()
    else:
        # 尝试按"汇编代码："标记提取
        assembly_marker = re.search(r'汇编代码：?\s*', response)
        if assembly_marker:
            assembly_start = assembly_marker.end()
            assembly = response[assembly_start:].strip()
            thought = response[:assembly_marker.start()].strip()
            thought = re.sub(r'^思考过程：?\s*', '', thought, flags=re.MULTILINE).strip()
        else:
            # 回退：从包含DATA/CODE结构的片段中提取
            data_code_match = re.search(r'(DATA[\s\S]*?ENDDATA[\s\S]*?CODE[\s\S]*?ENDCODE)', response, re.IGNORECASE)
            if data_code_match:
                assembly = data_code_match.group(1).strip()
                thought = response.replace(assembly, '').strip()
            else:
                # 最后回退：整段作为思考过程，无汇编
                thought = response.strip()
                assembly = ''
    
    # 清理汇编代码：去除围栏标记与无关前缀
    if assembly:
        cleaned_lines = []
        for line in assembly.split('\n'):
            line = line.strip('\r')
            if line.strip().startswith('```'):
                continue
            cleaned_lines.append(line)
        assembly = '\n'.join(cleaned_lines).strip()
    
    return thought, assembly
