"""
Configuration Management System

This package provides centralized configuration management for LLM providers,
prompts, and system settings.
"""

from .base import ConfigManager, LLMConfig, SystemConfig
from .defaults import get_default_config, get_development_config, get_production_config

# Create global config manager instance
config_manager = ConfigManager()

__all__ = [
    'ConfigManager',
    'LLMConfig',
    'SystemConfig',
    'config_manager',
    'get_default_config',
    'get_development_config',
    'get_production_config'
]