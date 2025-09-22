"""
Prompt Management System

This package provides modular, versioned prompts for different LLM providers
and use cases in the MCU-Copilot project.
"""

from .base import PromptTemplate, PromptVersion, PromptError
from .manager import PromptManager, prompt_manager

__all__ = [
    'PromptTemplate',
    'PromptVersion',
    'PromptError',
    'PromptManager',
    'prompt_manager'
]