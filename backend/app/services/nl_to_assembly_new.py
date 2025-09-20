"""
Backward-compatible wrapper for the new NL to Assembly architecture

This module provides the same interface as the original nl_to_assembly.py
while using the improved architecture under the hood.
"""

import os
from typing import Tuple
from .nl_to_assembly_v2 import nl_to_assembly_service
from .config import config_manager, get_default_config
from .llm import LLMError

# Initialize default configuration if not already done
def _ensure_default_config():
    """Ensure default configuration is loaded"""
    if not config_manager.get_all_llm_configs():
        # Load default configurations
        default_config = get_default_config()
        config_manager._parse_config_data(default_config)

        # Load from environment
        config_manager._load_from_environment()

def nl_to_assembly(requirement: str, use_gemini: bool = False, session_id: str = None) -> Tuple[str, str]:
    """
    Backward-compatible function for natural language to assembly conversion

    Args:
        requirement: Natural language description
        use_gemini: If True, prefer Gemini provider (legacy parameter)
        session_id: Optional session identifier

    Returns:
        Tuple[str, str]: (thought_process, assembly_code)
    """
    _ensure_default_config()

    # Handle legacy use_gemini parameter
    provider_override = None
    if use_gemini:
        # Try to find a Gemini provider
        all_configs = config_manager.get_all_llm_configs()
        gemini_providers = [key for key, config in all_configs.items()
                          if config.provider_type == "gemini" and config.enabled]
        if gemini_providers:
            provider_override = gemini_providers[0]  # Use first available Gemini provider

    try:
        return nl_to_assembly_service.generate_assembly(
            requirement=requirement,
            provider_override=provider_override,
            session_id=session_id
        )
    except LLMError as e:
        # Convert to a more user-friendly error for backward compatibility
        raise Exception(f"Failed to generate assembly code: {e}")

def nl_to_assembly_qwen(requirement: str, session_id: str = None) -> Tuple[str, str]:
    """
    Qwen-specific generation function for backward compatibility
    """
    _ensure_default_config()

    # Find a Qwen provider
    all_configs = config_manager.get_all_llm_configs()
    qwen_providers = [key for key, config in all_configs.items()
                     if config.provider_type in ["qwen", "qwen_coder"] and config.enabled]

    provider_override = None
    if qwen_providers:
        # Prefer coder models, then regular qwen
        coder_providers = [key for key in qwen_providers if config_manager.get_llm_config(key).provider_type == "qwen_coder"]
        provider_override = coder_providers[0] if coder_providers else qwen_providers[0]

    try:
        return nl_to_assembly_service.generate_assembly(
            requirement=requirement,
            provider_override=provider_override,
            session_id=session_id
        )
    except LLMError as e:
        raise Exception(f"Qwen generation failed: {e}")

def nl_to_assembly_gemini(requirement: str, session_id: str = None) -> Tuple[str, str]:
    """
    Gemini-specific generation function for backward compatibility
    """
    _ensure_default_config()

    # Find a Gemini provider
    all_configs = config_manager.get_all_llm_configs()
    gemini_providers = [key for key, config in all_configs.items()
                       if config.provider_type == "gemini" and config.enabled]

    provider_override = None
    if gemini_providers:
        provider_override = gemini_providers[0]
    else:
        raise Exception("No Gemini providers configured or enabled")

    try:
        return nl_to_assembly_service.generate_assembly(
            requirement=requirement,
            provider_override=provider_override,
            session_id=session_id
        )
    except LLMError as e:
        raise Exception(f"Gemini generation failed: {e}")

# Additional utility functions for the new architecture
def get_provider_status():
    """Get status of all configured providers"""
    _ensure_default_config()
    return nl_to_assembly_service.get_provider_status()

def get_performance_stats():
    """Get performance statistics"""
    return nl_to_assembly_service.get_performance_stats()

def get_recommendations():
    """Get recommendations for improving performance"""
    return nl_to_assembly_service.get_recommendations()

def configure_provider(provider_key: str, **kwargs):
    """Configure a specific provider"""
    # This could be used for dynamic configuration
    # Implementation would depend on specific needs
    pass