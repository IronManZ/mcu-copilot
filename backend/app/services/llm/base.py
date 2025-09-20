"""
Base classes for LLM providers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class LLMProviderType(Enum):
    """Enumeration of supported LLM provider types"""
    QWEN = "qwen"
    QWEN_CODER = "qwen_coder"
    GEMINI = "gemini"

@dataclass
class LLMResponse:
    """Standardized response from LLM providers"""
    content: str
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    token_usage: Optional[Dict[str, int]] = None

class LLMError(Exception):
    """Custom exception for LLM-related errors"""
    def __init__(self, message: str, provider_type: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.provider_type = provider_type
        self.original_error = original_error

class LLMProvider(ABC):
    """Abstract base class for all LLM providers"""

    def __init__(self, provider_type: LLMProviderType, model_name: str, api_key: Optional[str] = None):
        self.provider_type = provider_type
        self.model_name = model_name
        self.api_key = api_key

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            system_prompt: Optional system prompt to prepend
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse: Standardized response object
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the provider configuration"""
        pass

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider"""
        # Handle both enum and string provider types
        provider_type_str = self.provider_type.value if hasattr(self.provider_type, 'value') else str(self.provider_type)
        return {
            "type": provider_type_str,
            "model": self.model_name,
            "available": self.is_available(),
            "config_valid": self.validate_config()
        }

    def _create_error_response(self, error_message: str, original_error: Optional[Exception] = None) -> LLMResponse:
        """Helper method to create error responses"""
        # Handle both enum and string provider types
        provider_type_str = self.provider_type.value if hasattr(self.provider_type, 'value') else str(self.provider_type)
        return LLMResponse(
            content="",
            success=False,
            error_message=error_message,
            metadata={
                "provider_type": provider_type_str,
                "model_name": self.model_name,
                "original_error": str(original_error) if original_error else None
            }
        )