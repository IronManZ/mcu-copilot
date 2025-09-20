"""
Base classes for retry logic and error handling
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class RetryStrategy(Enum):
    """Different retry strategies"""
    SIMPLE = "simple"  # Simple retry with same prompt
    PROGRESSIVE = "progressive"  # Gradually more detailed prompts
    ERROR_AWARE = "error_aware"  # Adjust prompt based on error type
    SMART_ADAPTIVE = "smart_adaptive"  # Learn from patterns and adapt

@dataclass
class CompilationError:
    """Represents a compilation error with metadata"""
    message: str
    line_number: Optional[int] = None
    error_type: str = "unknown"
    severity: str = "error"  # error, warning, info
    suggestion: Optional[str] = None

@dataclass
class RetryResult:
    """Result of a retry attempt"""
    success: bool
    attempt_number: int
    thought_process: str
    generated_code: str
    compilation_errors: List[CompilationError]
    metadata: Dict[str, Any]
    total_attempts: int
    strategy_used: RetryStrategy

class RetryManager(ABC):
    """Abstract base class for retry managers"""

    def __init__(self, max_attempts: int = 5, strategy: RetryStrategy = RetryStrategy.SMART_ADAPTIVE):
        self.max_attempts = max_attempts
        self.strategy = strategy

    @abstractmethod
    def execute_with_retry(
        self,
        generator_func: Callable,
        validator_func: Callable,
        requirement: str,
        session_id: str,
        **kwargs
    ) -> RetryResult:
        """
        Execute a generation function with intelligent retry logic

        Args:
            generator_func: Function that generates code
            validator_func: Function that validates/compiles code
            requirement: Original requirement string
            session_id: Unique session identifier
            **kwargs: Additional arguments

        Returns:
            RetryResult: Final result after all attempts
        """
        pass

    @abstractmethod
    def should_retry(self, attempt: int, errors: List[CompilationError]) -> bool:
        """Determine if another retry attempt should be made"""
        pass

    @abstractmethod
    def adapt_strategy(self, errors: List[CompilationError], attempt: int) -> Dict[str, Any]:
        """Adapt the generation strategy based on previous errors"""
        pass