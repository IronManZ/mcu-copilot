"""
Base classes for prompt management
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class PromptVersion(Enum):
    """Prompt version enumeration"""
    V1_ORIGINAL = "v1_original"
    V2_OPTIMIZED = "v2_optimized"
    V3_CODER = "v3_coder"  # Optimized for coding models
    V4_STRUCTURED = "v4_structured"  # Latest structured version

class PromptError(Exception):
    """Custom exception for prompt-related errors"""
    pass

@dataclass
class PromptTemplate:
    """Represents a prompt template with metadata"""
    name: str
    version: PromptVersion
    description: str
    content: str
    variables: List[str] = field(default_factory=list)
    target_provider: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs) -> str:
        """Render the prompt template with provided variables"""
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            raise PromptError(f"Missing required variable: {e}")

    def validate_variables(self, **kwargs) -> bool:
        """Validate that all required variables are provided"""
        missing = [var for var in self.variables if var not in kwargs]
        if missing:
            raise PromptError(f"Missing required variables: {missing}")
        return True

class PromptBuilder(ABC):
    """Abstract base class for prompt builders"""

    @abstractmethod
    def build_system_prompt(self, version: PromptVersion = PromptVersion.V4_STRUCTURED) -> str:
        """Build the system prompt"""
        pass

    @abstractmethod
    def build_user_prompt(self, requirement: str, **kwargs) -> str:
        """Build the user prompt for a specific requirement"""
        pass

    @abstractmethod
    def build_error_correction_prompt(self, errors: List[str], previous_code: str, attempt_number: int) -> str:
        """Build prompt for error correction iteration"""
        pass

    @abstractmethod
    def get_supported_versions(self) -> List[PromptVersion]:
        """Get list of supported prompt versions"""
        pass