"""
Prompt Management System

This package provides modular, versioned prompts for different LLM providers
and use cases in the MCU-Copilot project.
"""

from .base import PromptTemplate, PromptVersion, PromptError
from .manager import PromptManager, prompt_manager
from .zh5001_prompts import ZH5001PromptBuilder

# Register the ZH5001 prompt builder
zh5001_builder = ZH5001PromptBuilder()
prompt_manager.register_builder("zh5001", zh5001_builder)

__all__ = [
    'PromptTemplate',
    'PromptVersion',
    'PromptError',
    'PromptManager',
    'prompt_manager',
    'ZH5001PromptBuilder'
]