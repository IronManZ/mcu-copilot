"""
Error Analysis and Pattern Recognition
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum
from .base import CompilationError

class ErrorPattern(Enum):
    """Common error patterns in ZH5001 compilation"""
    UNDEFINED_VARIABLE = "undefined_variable"
    INVALID_INSTRUCTION = "invalid_instruction"
    JUMP_DISTANCE = "jump_distance"
    IMMEDIATE_VALUE_MISUSE = "immediate_value_misuse"
    SYNTAX_ERROR = "syntax_error"
    MISSING_DATA_SECTION = "missing_data_section"
    MISSING_CODE_SECTION = "missing_code_section"
    INVALID_ADDRESS = "invalid_address"
    LABEL_ERROR = "label_error"

@dataclass
class ErrorSuggestion:
    """Suggestion for fixing a specific error pattern"""
    pattern: ErrorPattern
    description: str
    fix_template: str
    example: str

class ErrorAnalyzer:
    """Analyzes compilation errors and provides targeted suggestions"""

    def __init__(self):
        self._error_patterns = self._initialize_patterns()
        self._error_history: Dict[str, List[ErrorPattern]] = {}

    def _initialize_patterns(self) -> Dict[ErrorPattern, ErrorSuggestion]:
        """Initialize error pattern definitions"""
        return {
            ErrorPattern.UNDEFINED_VARIABLE: ErrorSuggestion(
                pattern=ErrorPattern.UNDEFINED_VARIABLE,
                description="Variable used but not defined in DATA section",
                fix_template="Add 'variable_name address' to DATA section",
                example="DATA\n    temp_var    0\nENDDATA"
            ),
            ErrorPattern.INVALID_INSTRUCTION: ErrorSuggestion(
                pattern=ErrorPattern.INVALID_INSTRUCTION,
                description="Instruction not supported by ZH5001",
                fix_template="Replace with supported instruction",
                example="Use LD instead of MOV, JZ instead of BEQ"
            ),
            ErrorPattern.JUMP_DISTANCE: ErrorSuggestion(
                pattern=ErrorPattern.JUMP_DISTANCE,
                description="JZ/JOV/JCY jump distance exceeds ±32 limit",
                fix_template="Use JUMP for long distances or reorganize code",
                example="Replace 'JZ distant_label' with 'JUMP distant_label'"
            ),
            ErrorPattern.IMMEDIATE_VALUE_MISUSE: ErrorSuggestion(
                pattern=ErrorPattern.IMMEDIATE_VALUE_MISUSE,
                description="Immediate value used with instruction that doesn't support it",
                fix_template="Store immediate in variable or use LDINS",
                example="LDINS 123\nST temp_var\nADD temp_var"
            ),
            ErrorPattern.SYNTAX_ERROR: ErrorSuggestion(
                pattern=ErrorPattern.SYNTAX_ERROR,
                description="General syntax error in assembly code",
                fix_template="Check instruction format and operands",
                example="Ensure proper spacing and valid operand types"
            ),
            ErrorPattern.MISSING_DATA_SECTION: ErrorSuggestion(
                pattern=ErrorPattern.MISSING_DATA_SECTION,
                description="DATA section missing or malformed",
                fix_template="Add properly formatted DATA section",
                example="DATA\n    variable_name    address\nENDDATA"
            ),
            ErrorPattern.MISSING_CODE_SECTION: ErrorSuggestion(
                pattern=ErrorPattern.MISSING_CODE_SECTION,
                description="CODE section missing or malformed",
                fix_template="Add properly formatted CODE section",
                example="CODE\nlabel:\n    instruction operand\nENDCODE"
            ),
            ErrorPattern.INVALID_ADDRESS: ErrorSuggestion(
                pattern=ErrorPattern.INVALID_ADDRESS,
                description="Variable address out of valid range (0-63)",
                fix_template="Use address in range 0-47 for user variables",
                example="Use addresses 0-47 for user data"
            ),
            ErrorPattern.LABEL_ERROR: ErrorSuggestion(
                pattern=ErrorPattern.LABEL_ERROR,
                description="Label definition or reference error",
                fix_template="Ensure labels are defined with colon and properly referenced",
                example="main:\n    LDINS 1"
            )
        }

    def analyze_errors(self, errors: List[str], session_id: Optional[str] = None) -> List[CompilationError]:
        """Analyze raw error messages and categorize them"""
        analyzed_errors = []
        detected_patterns = set()

        for error_msg in errors:
            compilation_error = self._classify_error(error_msg)
            analyzed_errors.append(compilation_error)

            # Track pattern for this session
            if compilation_error.error_type != "unknown":
                try:
                    pattern = ErrorPattern(compilation_error.error_type)
                    detected_patterns.add(pattern)
                except ValueError:
                    pass

        # Update error history
        if session_id:
            if session_id not in self._error_history:
                self._error_history[session_id] = []
            self._error_history[session_id].extend(list(detected_patterns))

        return analyzed_errors

    def _classify_error(self, error_msg: str) -> CompilationError:
        """Classify a single error message"""
        error_lower = error_msg.lower()

        # Check for undefined variables
        if any(keyword in error_lower for keyword in ['undefined', '未定义', 'not defined']):
            return CompilationError(
                message=error_msg,
                error_type=ErrorPattern.UNDEFINED_VARIABLE.value,
                suggestion=self._error_patterns[ErrorPattern.UNDEFINED_VARIABLE].fix_template
            )

        # Check for invalid instructions
        if any(keyword in error_lower for keyword in ['invalid instruction', 'unknown instruction', '未识别的指令']):
            return CompilationError(
                message=error_msg,
                error_type=ErrorPattern.INVALID_INSTRUCTION.value,
                suggestion=self._error_patterns[ErrorPattern.INVALID_INSTRUCTION].fix_template
            )

        # Check for jump distance errors
        if any(keyword in error_lower for keyword in ['jump distance', 'jump range', '跳转距离']):
            return CompilationError(
                message=error_msg,
                error_type=ErrorPattern.JUMP_DISTANCE.value,
                suggestion=self._error_patterns[ErrorPattern.JUMP_DISTANCE].fix_template
            )

        # Check for immediate value errors
        if any(keyword in error_lower for keyword in ['immediate', '立即数', 'constant']):
            return CompilationError(
                message=error_msg,
                error_type=ErrorPattern.IMMEDIATE_VALUE_MISUSE.value,
                suggestion=self._error_patterns[ErrorPattern.IMMEDIATE_VALUE_MISUSE].fix_template
            )

        # Check for missing sections
        if any(keyword in error_lower for keyword in ['missing data', 'no data section']):
            return CompilationError(
                message=error_msg,
                error_type=ErrorPattern.MISSING_DATA_SECTION.value,
                suggestion=self._error_patterns[ErrorPattern.MISSING_DATA_SECTION].fix_template
            )

        if any(keyword in error_lower for keyword in ['missing code', 'no code section']):
            return CompilationError(
                message=error_msg,
                error_type=ErrorPattern.MISSING_CODE_SECTION.value,
                suggestion=self._error_patterns[ErrorPattern.MISSING_CODE_SECTION].fix_template
            )

        # Check for address range errors
        if any(keyword in error_lower for keyword in ['address', 'range', '地址']):
            return CompilationError(
                message=error_msg,
                error_type=ErrorPattern.INVALID_ADDRESS.value,
                suggestion=self._error_patterns[ErrorPattern.INVALID_ADDRESS].fix_template
            )

        # Check for label errors
        if any(keyword in error_lower for keyword in ['label', '标号', 'undefined label']):
            return CompilationError(
                message=error_msg,
                error_type=ErrorPattern.LABEL_ERROR.value,
                suggestion=self._error_patterns[ErrorPattern.LABEL_ERROR].fix_template
            )

        # Default to syntax error
        return CompilationError(
            message=error_msg,
            error_type=ErrorPattern.SYNTAX_ERROR.value,
            suggestion=self._error_patterns[ErrorPattern.SYNTAX_ERROR].fix_template
        )

    def get_error_patterns_for_session(self, session_id: str) -> List[ErrorPattern]:
        """Get historical error patterns for a session"""
        return self._error_history.get(session_id, [])

    def get_targeted_suggestions(self, patterns: List[ErrorPattern]) -> List[str]:
        """Get targeted suggestions for specific error patterns"""
        suggestions = []
        for pattern in patterns:
            if pattern in self._error_patterns:
                suggestion_obj = self._error_patterns[pattern]
                suggestions.append(f"{suggestion_obj.description}: {suggestion_obj.fix_template}")
        return suggestions

    def should_switch_model(self, session_id: str) -> bool:
        """Determine if we should switch to a different model based on error history"""
        if session_id not in self._error_history:
            return False

        patterns = self._error_history[session_id]

        # If we see the same error pattern repeatedly, suggest model switch
        pattern_counts = {}
        for pattern in patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        # Switch model if any pattern appears 3+ times
        return any(count >= 3 for count in pattern_counts.values())