"""
对话管理器 - 处理大模型的多轮对话和上下文记忆
"""
from typing import List, Dict, Any, Optional
import logging
from .structured_code_manager import StructuredCodeManager


class ConversationManager:
    """管理大模型的对话上下文"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[Dict[str, str]] = []
        self.logger = logging.getLogger(__name__)

    def start_conversation(self, system_prompt: str, user_requirement: str) -> List[Dict[str, str]]:
        """
        开始新对话

        Args:
            system_prompt: 系统提示词
            user_requirement: 用户需求

        Returns:
            消息列表
        """
        self.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_requirement}
        ]

        self.logger.debug(f"[{self.session_id}] 开始新对话，消息数: {len(self.messages)}")
        return self.messages.copy()

    def add_assistant_response(self, response: str) -> None:
        """
        添加助手响应

        Args:
            response: 助手响应内容
        """
        self.messages.append({"role": "assistant", "content": response})
        self.logger.debug(f"[{self.session_id}] 添加助手响应，总消息数: {len(self.messages)}")

    def add_error_feedback(self,
                          compile_errors: List[str],
                          compile_warnings: List[str] = None,
                          attempt_num: int = 1,
                          generated_code: str = None) -> List[Dict[str, str]]:
        """
        添加编译错误反馈

        Args:
            compile_errors: 编译错误列表
            compile_warnings: 编译警告列表
            attempt_num: 尝试次数
            generated_code: 生成的代码（用于结构化分析）

        Returns:
            更新后的消息列表
        """
        if generated_code:
            error_message = self._build_structured_error_feedback(
                compile_errors, compile_warnings, attempt_num, generated_code
            )
        else:
            error_message = self._build_error_feedback_message(
                compile_errors, compile_warnings, attempt_num
            )

        self.messages.append({"role": "user", "content": error_message})

        self.logger.debug(f"[{self.session_id}] 添加错误反馈，总消息数: {len(self.messages)}")
        return self.messages.copy()

    def _build_structured_error_feedback(self,
                                       compile_errors: List[str],
                                       compile_warnings: List[str] = None,
                                       attempt_num: int = 1,
                                       generated_code: str = "") -> str:
        """构建结构化错误反馈消息"""

        # 使用结构化代码管理器解析代码
        code_manager = StructuredCodeManager()
        code_manager.parse_assembly_code(generated_code)

        message_parts = [
            f"第{attempt_num}次编译失败，请仔细分析以下**结构化错误报告**：",
            ""
        ]

        if compile_errors:
            message_parts.append("🔴 **详细错误分析**:")
            for i, error in enumerate(compile_errors, 1):
                # 尝试从错误信息中提取行号
                line_num = self._extract_line_number(error)
                if line_num:
                    # 使用结构化管理器生成详细上下文
                    detailed_context = code_manager.format_error_context(line_num, error)
                    message_parts.append(f"\n**错误 {i}:**")
                    message_parts.append(detailed_context)
                else:
                    message_parts.append(f"{i}. {error}")
            message_parts.append("")

        if compile_warnings:
            message_parts.append("🟡 **编译警告**:")
            for i, warning in enumerate(compile_warnings, 1):
                message_parts.append(f"{i}. {warning}")
            message_parts.append("")

        # 添加修复指导
        message_parts.extend([
            "📋 **精确修复要求**:",
            "1. 查看上方的**结构化错误分析**，了解每个错误的确切位置和原因",
            "2. **只修复报告的具体错误**，不要重写整个程序",
            "3. 保持相同的功能需求和程序逻辑",
            "4. 确保所有变量在DATA段中正确定义",
            "5. 使用正确的ZH5001指令集语法",
            "",
            "请基于上述**精确的错误定位信息**输出修正后的完整汇编代码："
        ])

        return "\n".join(message_parts)

    def _extract_line_number(self, error_message: str) -> Optional[int]:
        """从错误信息中提取行号"""
        import re

        # 匹配 "第X行" 模式
        match = re.search(r'第(\d+)行', error_message)
        if match:
            return int(match.group(1))

        # 匹配 "Line X" 模式
        match = re.search(r'[Ll]ine\s+(\d+)', error_message)
        if match:
            return int(match.group(1))

        return None

    def _build_error_feedback_message(self,
                                    compile_errors: List[str],
                                    compile_warnings: List[str] = None,
                                    attempt_num: int = 1) -> str:
        """构建错误反馈消息"""

        message_parts = [
            f"第{attempt_num}次编译失败，请基于上一次生成的代码修复以下问题：",
            ""
        ]

        if compile_errors:
            message_parts.append("🔴 编译错误:")
            for i, error in enumerate(compile_errors, 1):
                message_parts.append(f"{i}. {error}")
            message_parts.append("")

        if compile_warnings:
            message_parts.append("🟡 编译警告:")
            for i, warning in enumerate(compile_warnings, 1):
                message_parts.append(f"{i}. {warning}")
            message_parts.append("")

        # 添加修复指导
        message_parts.extend([
            "📋 修复要求:",
            "1. 保持相同的功能需求",
            "2. 只修复报告的错误，不要重写整个程序",
            "3. 确保所有变量在DATA段中定义",
            "4. 跳转距离保持在±32范围内",
            "5. 使用正确的ZH5001指令集语法",
            "",
            "请输出修正后的完整汇编代码（包括思考过程）："
        ])

        return "\n".join(message_parts)

    def get_conversation_summary(self) -> str:
        """获取对话摘要"""
        total_chars = sum(len(msg["content"]) for msg in self.messages)
        return (f"对话轮次: {len(self.messages)}, "
                f"总字符数: {total_chars}, "
                f"系统消息: {sum(1 for msg in self.messages if msg['role'] == 'system')}, "
                f"用户消息: {sum(1 for msg in self.messages if msg['role'] == 'user')}, "
                f"助手消息: {sum(1 for msg in self.messages if msg['role'] == 'assistant')}")

    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """获取用于API调用的消息列表"""
        return self.messages.copy()

    def should_truncate_context(self, max_tokens: int = 8000) -> bool:
        """
        检查是否需要截断上下文

        Args:
            max_tokens: 最大token数（粗略估算：1 token ≈ 1.5 字符）

        Returns:
            是否需要截断
        """
        total_chars = sum(len(msg["content"]) for msg in self.messages)
        estimated_tokens = total_chars / 1.5

        return estimated_tokens > max_tokens

    def truncate_context(self, keep_recent: int = 4) -> None:
        """
        截断上下文，保留最近的消息

        Args:
            keep_recent: 保留最近的消息数量（不包括系统消息）
        """
        if not self.messages:
            return

        # 始终保留系统消息
        system_messages = [msg for msg in self.messages if msg["role"] == "system"]
        other_messages = [msg for msg in self.messages if msg["role"] != "system"]

        # 保留最近的消息
        if len(other_messages) > keep_recent:
            kept_messages = other_messages[-keep_recent:]
            self.messages = system_messages + kept_messages

            self.logger.info(f"[{self.session_id}] 截断对话上下文，保留 {len(self.messages)} 条消息")


class GeminiConversationManager(ConversationManager):
    """Gemini模型的对话管理器"""

    def get_messages_for_gemini(self) -> str:
        """
        获取用于Gemini API的单个提示词字符串

        Gemini使用单个字符串而不是消息列表
        """
        if not self.messages:
            return ""

        # 将对话转换为单个字符串
        conversation_parts = []

        for msg in self.messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                conversation_parts.append(f"# 系统指示\n{content}")
            elif role == "user":
                conversation_parts.append(f"# 用户\n{content}")
            elif role == "assistant":
                conversation_parts.append(f"# 助手\n{content}")

        return "\n\n".join(conversation_parts)


class QwenConversationManager(ConversationManager):
    """Qwen模型的对话管理器"""

    def get_messages_for_qwen(self) -> List[Dict[str, str]]:
        """获取用于Qwen API的消息列表格式"""
        return self.get_messages_for_api()