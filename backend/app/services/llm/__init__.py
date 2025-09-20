"""
LLM Service Package

This package provides a unified interface for different LLM providers
used in the MCU-Copilot project.
"""

from .base import LLMProvider, LLMResponse, LLMError, LLMProviderType
from .factory import LLMProviderFactory
from .qwen_provider import QwenProvider
from .qwen_coder_provider import Qwen3CoderProvider
from .gemini_provider import GeminiProvider

# Register providers with the factory
LLMProviderFactory.register_provider(LLMProviderType.QWEN, QwenProvider)
LLMProviderFactory.register_provider(LLMProviderType.QWEN_CODER, Qwen3CoderProvider)
LLMProviderFactory.register_provider(LLMProviderType.GEMINI, GeminiProvider)

__all__ = [
    'LLMProvider',
    'LLMResponse',
    'LLMError',
    'LLMProviderType',
    'LLMProviderFactory',
    'QwenProvider',
    'Qwen3CoderProvider',
    'GeminiProvider'
]