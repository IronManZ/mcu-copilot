import os
import re
import json
import logging
import uuid
from datetime import datetime
from dashscope import Generation
from dotenv import load_dotenv

# 尝试导入Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# 引入本地ZH5001编译服务进行本地编译校验
from app.services.compiler.zh5001_service import ZH5001CompilerService

# 引入模板引擎和对话管理器
from app.services.template_engine import render_zh5001_prompt
from app.services.conversation_manager import GeminiConversationManager

# 配置日志
def setup_service_logging():
    """设置服务端日志 - 生产环境仅使用控制台日志"""
    # 生产环境禁用文件日志以避免权限问题
    logging.basicConfig(
        level=logging.INFO,  # 生产环境使用INFO级别
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # 仅使用控制台日志
        ]
    )

    return logging.getLogger(__name__)

# 初始化日志
logger = setup_service_logging()

def log_service_request(session_id: str, requirement: str, use_gemini: bool):
    """记录服务请求"""
    logger.info(f"[{session_id}] 新的编译请求")
    logger.info(f"[{session_id}] 需求: {requirement}")
    logger.info(f"[{session_id}] 使用模型: {'Gemini' if use_gemini else 'Qwen'}")

def log_service_response(session_id: str, thought: str, assembly: str, success: bool):
    """记录服务响应"""
    logger.info(f"[{session_id}] 服务响应生成完成")
    logger.info(f"[{session_id}] 思考过程长度: {len(thought)} 字符")
    logger.info(f"[{session_id}] 汇编代码长度: {len(assembly)} 字符")
    logger.info(f"[{session_id}] 生成成功: {success}")
    
    if thought:
        if len(thought) <= 500:
            logger.info(f"[{session_id}] 思考过程: {thought}")
        else:
            logger.info(f"[{session_id}] 思考过程: {thought[:500]}...")
            logger.debug(f"[{session_id}] 完整思考过程: {thought}")

    if assembly:
        if len(assembly) <= 1000:
            logger.info(f"[{session_id}] 汇编代码: {assembly}")
        else:
            logger.info(f"[{session_id}] 汇编代码: {assembly[:1000]}...")
            logger.debug(f"[{session_id}] 完整汇编代码: {assembly}")

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def nl_to_assembly(requirement: str, use_gemini: bool = False, session_id: str = None) -> tuple[str, str]:
    """自然语言转汇编代码，支持选择使用通义千问或Gemini模型"""
    
    # 生成session_id如果没有提供
    if session_id is None:
        session_id = str(uuid.uuid4())[:8]
    
    # 记录请求
    log_service_request(session_id, requirement, use_gemini)
    
    try:
        if use_gemini and GEMINI_AVAILABLE:
            thought, assembly = nl_to_assembly_gemini(requirement, session_id)
        else:
            thought, assembly = nl_to_assembly_qwen(requirement, session_id)
        
        # 记录响应
        success = bool(thought and assembly)
        log_service_response(session_id, thought, assembly, success)
        
        return thought, assembly
    
    except Exception as e:
        logger.error(f"[{session_id}] 处理请求时发生异常: {e}")
        raise

def nl_to_assembly_gemini(requirement: str, session_id: str) -> tuple[str, str]:
    """使用Gemini模型生成ZH5001汇编代码"""
    
    # 记录Gemini处理开始
    logger.info(f"[{session_id}] 开始使用Gemini模型处理")
    
    # 尝试不使用代理，如果失败再使用代理
    # 清除代理设置，先尝试直连
    os.environ.pop('HTTP_PROXY', None)
    os.environ.pop('HTTPS_PROXY', None)
    logger.info(f"[{session_id}] 尝试直连Google API（无代理）")
    
    # 配置Gemini API - 从环境变量读取密钥
    api_key = os.environ.get("GEMINI_APIKEY")
    if not api_key:
        logger.error(f"[{session_id}] GEMINI_APIKEY未配置")
        raise Exception("请在 .env 或环境变量中配置 GEMINI_APIKEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 使用新的统一模板系统
    template_path = os.path.join(os.path.dirname(__file__), 'prompts', 'zh5001_gemini_complete_template.md')
    if not os.path.exists(template_path):
        raise Exception(f"模板文件不存在: {template_path}")

    # 初始化对话管理器
    conversation = GeminiConversationManager(session_id)

    # 渲染初始系统提示词
    system_prompt = render_zh5001_prompt(template_path, requirement)

    # 开始对话
    user_message = f"请根据需求生成ZH5001汇编代码：{requirement}"
    conversation.start_conversation(system_prompt, user_message)

    # 生成 → 本地编译校验 → 如失败则反馈错误让模型修正，最多重试5次
    compiler_service = ZH5001CompilerService()
    thought: str = ""
    assembly: str = ""
    all_thoughts = []  # 记录所有尝试的思考过程

    for attempt in range(5):
        try:
            logger.info(f"[{session_id}] 第{attempt + 1}次尝试使用Gemini生成代码...（可能需要30-60秒）")
            logger.info(f"[{session_id}] 第{attempt + 1}次尝试调用Gemini API")

            # 获取当前对话的完整提示词
            full_prompt = conversation.get_messages_for_gemini()

            # 记录请求详情（debug级别显示完整提示词）
            logger.debug(f"[{session_id}] 第{attempt + 1}次尝试 - Gemini完整请求内容:")
            logger.debug(f"[{session_id}] 对话摘要: {conversation.get_conversation_summary()}")
            logger.debug(f"[{session_id}] 提示词长度: {len(full_prompt)} 字符")
            logger.debug(f"[{session_id}] 完整对话内容:")
            logger.debug("-" * 80)
            logger.debug(full_prompt)
            logger.debug("-" * 80)

            # 调用Gemini API（设置更长的超时时间）
            response = model.generate_content(full_prompt)
            
            if not response.text:
                raise Exception("Gemini API返回空响应")
            
            full_response = response.text

            # 记录Gemini模型完整响应
            logger.info(f"[{session_id}] 第{attempt + 1}次Gemini响应长度: {len(full_response)} 字符")
            logger.info(f"[{session_id}] 第{attempt + 1}次Gemini完整响应:")
            logger.info(full_response)

            # 将响应添加到对话历史
            conversation.add_assistant_response(full_response)

            current_thought, current_assembly = parse_gemini_response(full_response)

            # 记录当前尝试的思考过程
            if current_thought:
                all_thoughts.append(f"第{attempt + 1}次尝试：{current_thought}")

            # 更新最终结果
            thought = current_thought
            assembly = current_assembly
            
            # 本地尝试编译
            logger.info(f"[{session_id}] 第{attempt + 1}次尝试 - 开始本地编译验证")
            compile_result = compiler_service.compile_assembly(assembly)

            # 记录编译器完整输出结果
            logger.info(f"[{session_id}] 第{attempt + 1}次编译结果:")
            logger.info(f"[{session_id}] 编译成功: {compile_result.get('success', False)}")

            if compile_result.get('success'):
                logger.info(f"[{session_id}] ✅ 编译成功！生成机器码长度: {len(compile_result.get('machine_code', []))} 条指令")
                if compile_result.get('warnings'):
                    logger.info(f"[{session_id}] 编译警告 ({len(compile_result['warnings'])}个):")
                    for i, warning in enumerate(compile_result['warnings'], 1):
                        logger.info(f"[{session_id}] 警告{i}: {warning}")

                # 成功编译，返回完整的思考过程
                if len(all_thoughts) > 1:
                    thought = "\n\n".join(all_thoughts)
                logger.info(f"[{session_id}] 🎉 代码生成和编译验证成功！")
                return thought, assembly
            
            # 失败则将错误反馈给模型，继续迭代
            current_errors = compile_result.get('errors', [])
            current_warnings = compile_result.get('warnings', [])

            # 详细记录编译失败信息
            logger.info(f"[{session_id}] ❌ 编译失败！")
            if current_errors:
                logger.info(f"[{session_id}] 编译错误 ({len(current_errors)}个):")
                for i, error in enumerate(current_errors, 1):
                    logger.info(f"[{session_id}] 错误{i}: {error}")

            if current_warnings:
                logger.info(f"[{session_id}] 编译警告 ({len(current_warnings)}个):")
                for i, warning in enumerate(current_warnings, 1):
                    logger.info(f"[{session_id}] 警告{i}: {warning}")

            # 记录完整的编译器输出（如果有的话）
            if 'full_output' in compile_result:
                logger.debug(f"[{session_id}] 编译器完整输出:")
                logger.debug(compile_result['full_output'])

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
            
            # 使用对话管理器添加结构化错误反馈
            conversation.add_error_feedback(
                compile_errors=current_errors,
                compile_warnings=current_warnings,
                attempt_num=attempt + 1,
                generated_code=assembly  # 传递生成的代码用于结构化分析
            )

            # 检查是否需要截断上下文（避免token过多）
            if conversation.should_truncate_context():
                conversation.truncate_context()
                logger.info(f"[{session_id}] 截断对话上下文以控制token数量")
            
        except Exception as e:
            logger.error(f"[{session_id}] Gemini API调用异常: {e}")
            if attempt == 0:
                raise Exception(f"Gemini API调用失败: {e}")
            # 如果是重试失败，继续下一次尝试
    
    # 5次修正仍失败，则返回最后一次结果（携带错误信息由上层处理）
    # 但返回完整的思考过程
    if len(all_thoughts) > 1:
        thought = "\n\n".join(all_thoughts)
    return thought, assembly

def nl_to_assembly_qwen(requirement: str, session_id: str) -> tuple[str, str]:
    """使用通义千问模型生成ZH5001汇编代码（原有实现）"""
    
    # 记录Qwen处理开始
    logger.info(f"[{session_id}] 开始使用Qwen模型处理")
    
    api_key = os.environ.get("QIANWEN_APIKEY")
    if not api_key:
        logger.error(f"[{session_id}] QIANWEN_APIKEY未配置")
        raise Exception("请在 .env 或环境变量中配置 QIANWEN_APIKEY")
    
    # 加载系统提示词：fpga-simulator/zh5001_prompt.md
    # 在Docker容器中，项目根目录是/app
    if os.path.exists('/app'):
        project_root = '/app'
    else:
        # 开发环境：计算项目根目录（本文件位于 backend/app/services/）
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

    system_prompt_path = os.path.join(project_root, 'fpga-simulator', 'zh5001_prompt.md')
    if not os.path.exists(system_prompt_path):
        raise Exception(f"系统提示词文件不存在: {system_prompt_path}")
    with open(system_prompt_path, 'r', encoding='utf-8') as f:
        system_prompt_core = f.read()
    
    # 附加严格生成规范，确保输出可被本地编译器通过
    system_addendum = (
        "\n\n【严格输出规范 - 务必遵守】\n"
        "- 生成 ZH5001 汇编，必须包含 DATA 段和 CODE 段（使用大写标识）。\n"
        "- DATA 段内显式定义所有用到的变量/寄存器别名，地址范围 0-47 为用户区，48-63 为特殊寄存器。\n"
        "- 如需访问特殊寄存器，请在 DATA 段定义：IOSET0 49、IOSET1 50、IO 51、SYSREG 48 等。\n"
        "- 只使用本编译器支持的指令助记符（LD, ST, ADD, SUB, AND, OR, MUL, CLAMP, JZ, JOV, JCY, JUMP, \n"
        "  SFT0RZ, SFT0RS, SFT0RR1, SFT0LZ, SFT1RZ, SFT1RS, SFT1RR1, SFT1LZ, LDINS, \n"
        "  NOP, INC, DEC, NOT, LDPC, NOTFLAG, R0R1, R1R0, SIN, COS, CLR, SET1, CLRFLAG, SETZ, SETCY, SETOV, \n"
        "  SQRT, NEG, EXR0R1, SIXSTEP, JNZ3, MOVC）。\n"
        "- 变量寻址必须通过 DATA 中的变量名（间接以地址）。不要在指令中直接写 0x???? 作为变量操作数。\n"
        "- 立即数只允许用于 LDINS。\n"
        "- 短跳转使用 JZ/JCY/JOV，长跳转用 JUMP（模型自行衡量，优先短跳转）。\n"
        "- 使用 4 个空格缩进指令；标号顶格 + 冒号。允许少量注释，但不要影响编译。\n"
        "- 输出务必为可编译格式。\n"
    )
    system_prompt = system_prompt_core + system_addendum

    # 用户提示：明确要求输出JSON格式
    user_prompt = (
        f"需求：{requirement}\n\n"
        "请严格按照系统提示词中规定的JSON格式输出，不要添加任何其他内容。\n"
        "确保返回有效的JSON格式，包含以下字段：\n"
        "- description: 功能描述\n"
        "- thought_process: 设计思路\n"
        "- assembly_code: 完整的汇编代码\n"
        "- key_points: 关键说明列表\n"
        "- testing_guide: 测试指导列表\n\n"
        "注意：汇编代码中的换行符请使用\\n表示。"
    )

    # 生成 → 本地编译校验 → 如失败则反馈错误让模型修正，最多重试5次
    compiler_service = ZH5001CompilerService()
    thought: str = ""
    assembly: str = ""
    previous_errors = []  # 记录之前的错误，避免重复
    all_thoughts = []  # 记录所有尝试的思考过程

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    for attempt in range(5):
        logger.info(f"[{session_id}] 第{attempt + 1}次尝试调用Qwen API")
        
        # 记录请求详情（debug级别显示完整消息）
        logger.debug(f"[{session_id}] 第{attempt + 1}次尝试 - Qwen完整请求消息:")
        logger.debug(f"[{session_id}] 系统提示词长度: {len(system_prompt)} 字符")
        logger.debug(f"[{session_id}] 用户消息长度: {len(user_prompt)} 字符")
        logger.debug(f"[{session_id}] 完整消息内容:")
        logger.debug("-" * 80)
        for i, msg in enumerate(messages, 1):
            logger.debug(f"[{session_id}] 消息{i} ({msg['role']}):")
            logger.debug(msg['content'])
            logger.debug("-" * 40)
        logger.debug("-" * 80)

        response = Generation.call(
            model="qwen-turbo",
            api_key=api_key,
            messages=messages
        )

        if 'output' not in response or 'text' not in response['output']:
            raise Exception(f"大模型API返回异常: {response}")

        full_response = response['output']['text']
        
        # 记录模型完整响应
        logger.info(f"[{session_id}] 第{attempt + 1}次模型响应长度: {len(full_response)} 字符")
        logger.info(f"[{session_id}] 第{attempt + 1}次模型完整响应:")
        logger.info(f"[{session_id}]\n{full_response}")
        
        current_thought, current_assembly = parse_response(session_id, full_response)
        
        # 记录当前尝试的思考过程
        if current_thought:
            all_thoughts.append(f"第{attempt + 1}次尝试：{current_thought}")
        
        # 更新最终结果
        thought = current_thought
        assembly = current_assembly

        # 本地尝试编译
        logger.info(f"[{session_id}] 第{attempt + 1}次尝试 - 开始本地编译验证")
        compile_result = compiler_service.compile_assembly(assembly)

        # 记录编译器完整输出结果
        logger.info(f"[{session_id}] 第{attempt + 1}次编译结果:")
        logger.info(f"[{session_id}] 编译成功: {compile_result.get('success', False)}")

        if compile_result.get('success'):
            logger.info(f"[{session_id}] ✅ 编译成功！生成机器码长度: {len(compile_result.get('machine_code', []))} 条指令")
            if compile_result.get('warnings'):
                logger.info(f"[{session_id}] 编译警告 ({len(compile_result['warnings'])}个):")
                for i, warning in enumerate(compile_result['warnings'], 1):
                    logger.info(f"[{session_id}] 警告{i}: {warning}")

            # 成功编译，返回完整的思考过程
            if len(all_thoughts) > 1:
                thought = "\n\n".join(all_thoughts)
            logger.info(f"[{session_id}] 🎉 代码生成和编译验证成功！")
            return thought, assembly

        # 失败则将错误反馈给模型，继续迭代
        current_errors = compile_result.get('errors', [])
        current_warnings = compile_result.get('warnings', [])

        # 详细记录编译失败信息
        logger.info(f"[{session_id}] ❌ 编译失败！")
        if current_errors:
            logger.info(f"[{session_id}] 编译错误 ({len(current_errors)}个):")
            for i, error in enumerate(current_errors, 1):
                logger.info(f"[{session_id}] 错误{i}: {error}")

        if current_warnings:
            logger.info(f"[{session_id}] 编译警告 ({len(current_warnings)}个):")
            for i, warning in enumerate(current_warnings, 1):
                logger.info(f"[{session_id}] 警告{i}: {warning}")

        # 记录完整的编译器输出（如果有的话）
        if 'full_output' in compile_result:
            logger.debug(f"[{session_id}] 编译器完整输出:")
            logger.debug(compile_result['full_output'])
        
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
            correction_guidance += "- JZ/JCY/JOV跳转距离必须在±32范围内，超出时使用JUMP\n"
        if any("未定义的变量" in error for error in current_errors):
            correction_guidance += "- 所有变量必须在DATA段中定义\n"
        if any("未识别的指令" in error for error in current_errors):
            correction_guidance += "- 只使用支持的指令助记符\n"
        if any("立即数" in error for error in current_errors):
            correction_guidance += "- 立即数只能用于LDINS指令\n"
        
        # 如果是重试，添加之前的问题对比
        if attempt > 0:
            error_context += f"\n之前尝试的问题：\n"
            for i, prev_error in enumerate(previous_errors, 1):
                error_context += f"尝试{i}: {prev_error}\n"
        
        # 更新错误历史
        previous_errors = current_errors.copy()
        
        fix_prompt = (
            f"{error_context}\n"
            f"{correction_guidance}\n"
            "请基于上述错误信息修正代码，确保：\n"
            "1. 所有变量在DATA段中定义\n"
            "2. 跳转距离在允许范围内\n"
            "3. 使用正确的指令格式\n"
            "4. 避免之前尝试中的错误\n\n"
            "请按相同格式输出修正后的完整汇编代码与思考过程。"
        )
        
        # 记录错误反馈消息
        logger.info(f"[{session_id}] 第{attempt + 1}次错误反馈消息:")
        logger.info(fix_prompt)
        
        messages.append({"role": "assistant", "content": full_response})
        messages.append({"role": "user", "content": fix_prompt})

    # 5次修正仍失败，则返回最后一次结果（携带错误信息由上层处理）
    # 但返回完整的思考过程
    if len(all_thoughts) > 1:
        thought = "\n\n".join(all_thoughts)
    return thought, assembly

def parse_response(session_id: str, response: str) -> tuple[str, str]:
    """解析大模型响应，优先处理JSON格式，回退到文本格式"""
    
    # logger.info(f"response: {response}")
    # 首先尝试解析JSON格式
    try:
        # 查找JSON代码块
        # 尝试直接解析整个响应为JSON
        json_str = response.strip()
        logger.info(f"🔍 尝试解析整个响应为JSON，长度: {len(json_str)}")
        
        # 解析JSON
        data = json.loads(json_str)
        logger.info(f"✅ JSON解析成功，类型: {type(data)}")
        
        if isinstance(data, dict):
            logger.info(f"📋 JSON字段: {list(data.keys())}")
            
            # 从JSON中提取思考过程和汇编代码
            thought_parts = []
            
            # 添加描述
            description = data.get('description', '')
            if description:
                thought_parts.append(description)
                logger.info(f"📝 描述长度: {len(description)}")
            
            # 添加思考过程
            thought_process = data.get('thought_process', '')
            if thought_process:
                thought_parts.append(thought_process)
                logger.info(f"🧠 思考过程长度: {len(thought_process)}")
            
            # 合并思考过程
            thought = '\n\n'.join(thought_parts) if thought_parts else ''
            logger.info(f"📄 合并后思考过程长度: {len(thought)}")
            
            # 获取汇编代码
            assembly = data.get('assembly_code', '')
            logger.info(f"汇编代码长度: {len(assembly)}")
            logger.info(f"[{session_id}] 汇编代码: \n{assembly}")
            
            # 如果汇编代码包含\n，需要转换为实际的换行符
            if assembly and '\\n' in assembly:
                assembly = assembly.replace('\\n', '\n')
                logger.info(f"🔄 转换换行符后汇编代码长度: {len(assembly)}")
                logger.info(f"[{session_id}] 转换换行符后汇编代码:\n {assembly}")
            
            # 打印完整的汇编代码
            if assembly:
                logger.info(f"📋 完整汇编代码:")
                logger.info("=" * 50)
                logger.info(assembly)
                logger.info("=" * 50)
                
            return thought, assembly
    
    except (json.JSONDecodeError, AttributeError) as e:
        # JSON解析失败，记录错误并回退到原有的文本解析方式
        logger.error(f"❌ JSON解析失败: {e}")
        pass
    
    # 回退：使用原有的文本解析方式
    # 优先用markdown代码块提取（支持```asm/```assembly/```）
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
    
    # 打印完整的汇编代码（文本格式）
    if assembly:
        logger.info(f"📋 完整汇编代码（文本格式）:")
        logger.info("=" * 50)
        logger.info(assembly)
        logger.info("=" * 50)
    
    return thought, assembly 

def parse_gemini_response(response: str) -> tuple[str, str]:
    """解析Gemini响应，分离思考过程和汇编代码"""

    # 首先尝试从包含DATA/CODE结构的片段中提取汇编代码
    data_code_match = re.search(r'(DATA[\s\S]*?ENDDATA[\s\S]*?CODE[\s\S]*?ENDCODE)', response, re.IGNORECASE)
    if data_code_match:
        assembly = data_code_match.group(1).strip()
        # 提取思考过程：取"## 功能说明"到"## 完整代码"之间的内容
        thought_match = re.search(r'## 功能说明\s*(.*?)(?=## 完整代码)', response, re.DOTALL)
        if thought_match:
            thought = thought_match.group(1).strip()
        else:
            # 如果没找到指定格式，取DATA/CODE之前的内容
            thought = response[:data_code_match.start()].strip()
    else:
        # 尝试用markdown代码块提取
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
                # 最后回退：整段作为思考过程，无汇编
                thought = response.strip()
                assembly = ''

    # 清理汇编代码：去除围栏标记与无关前缀
    if assembly:
        cleaned_lines = []
        for line in assembly.split('\n'):
            line = line.strip('\r')
            # 跳过代码块标记和注释中的"汇编代码："
            if line.strip().startswith('```') or line.strip() == '汇编代码：':
                continue
            cleaned_lines.append(line)
        assembly = '\n'.join(cleaned_lines).strip()

    return thought, assembly 