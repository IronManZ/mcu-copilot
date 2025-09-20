"""
Default configuration values
"""

from .base import LLMConfig, SystemConfig, ModelPriority

def get_default_config() -> dict:
    """Get default configuration dictionary"""
    return {
        "system": {
            "log_level": "INFO",
            "log_directory": "logs",
            "max_retry_attempts": 5,
            "default_retry_strategy": "smart_adaptive",
            "enable_analytics": True,
            "enable_performance_monitoring": True,
            "prompt_version": "v4_structured",
            "compilation_timeout_seconds": 30
        },
        "llm_providers": {
            "qwen_coder_turbo": {
                "provider_type": "qwen_coder",
                "model_name": "qwen-coder-turbo",
                "priority": "low",
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout_seconds": 60,
                "max_retries": 3,
                "enabled": False,
                "additional_params": {
                    "top_p": 0.95,
                    "repetition_penalty": 1.05
                }
            },
            "qwen_coder_32b": {
                "provider_type": "qwen_coder",
                "model_name": "qwen2.5-coder-32b-instruct",
                "priority": "high",
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout_seconds": 90,
                "max_retries": 3,
                "enabled": True,
                "additional_params": {
                    "top_p": 0.95,
                    "repetition_penalty": 1.05
                }
            },
            "qwen_turbo": {
                "provider_type": "qwen",
                "model_name": "qwen-turbo",
                "priority": "medium",
                "temperature": 0.3,
                "max_tokens": 4000,
                "timeout_seconds": 60,
                "max_retries": 3,
                "enabled": True,
                "additional_params": {}
            },
            "qwen_plus": {
                "provider_type": "qwen",
                "model_name": "qwen-plus",
                "priority": "medium",
                "temperature": 0.3,
                "max_tokens": 4000,
                "timeout_seconds": 60,
                "max_retries": 3,
                "enabled": False,
                "additional_params": {}
            },
            "gemini_pro": {
                "provider_type": "gemini",
                "model_name": "gemini-pro",
                "priority": "low",
                "temperature": 0.7,
                "max_tokens": 4000,
                "timeout_seconds": 120,
                "max_retries": 3,
                "enabled": True,
                "additional_params": {
                    "proxy": "http://127.0.0.1:10800"
                }
            },
            "gemini_15_flash": {
                "provider_type": "gemini",
                "model_name": "gemini-1.5-flash",
                "priority": "high",
                "temperature": 0.3,
                "max_tokens": 4000,
                "timeout_seconds": 90,
                "max_retries": 3,
                "enabled": True,
                "additional_params": {}
            },
            "gemini_flash": {
                "provider_type": "gemini",
                "model_name": "gemini-1.5-flash",
                "priority": "medium",
                "temperature": 0.3,
                "max_tokens": 4000,
                "timeout_seconds": 60,
                "max_retries": 3,
                "enabled": False,
                "additional_params": {
                    "proxy": "http://127.0.0.1:10800"
                }
            }
        }
    }

def get_default_llm_configs() -> dict[str, LLMConfig]:
    """Get default LLM configurations as objects"""
    defaults = get_default_config()
    configs = {}

    for provider_key, provider_data in defaults["llm_providers"].items():
        try:
            priority = ModelPriority(provider_data["priority"])
            config = LLMConfig(
                provider_type=provider_data["provider_type"],
                model_name=provider_data["model_name"],
                priority=priority,
                temperature=provider_data["temperature"],
                max_tokens=provider_data.get("max_tokens"),
                timeout_seconds=provider_data.get("timeout_seconds", 60),
                max_retries=provider_data.get("max_retries", 3),
                enabled=provider_data.get("enabled", True),
                additional_params=provider_data.get("additional_params", {})
            )
            configs[provider_key] = config
        except (KeyError, ValueError) as e:
            print(f"Warning: Invalid default config for {provider_key}: {e}")

    return configs

def get_development_config() -> dict:
    """Get configuration optimized for development"""
    config = get_default_config()

    # Enable verbose logging and monitoring for development
    config["system"]["log_level"] = "DEBUG"
    config["system"]["enable_analytics"] = True
    config["system"]["enable_performance_monitoring"] = True

    # Reduce timeouts for faster development cycles
    for provider_key, provider_config in config["llm_providers"].items():
        provider_config["timeout_seconds"] = min(provider_config.get("timeout_seconds", 60), 30)
        provider_config["max_retries"] = 2  # Fewer retries in development

    # Enable high-performance models for development
    config["llm_providers"]["qwen_coder_32b"]["enabled"] = True
    config["llm_providers"]["gemini_flash"]["enabled"] = True

    return config

def get_production_config() -> dict:
    """Get configuration optimized for production"""
    config = get_default_config()

    # Production logging
    config["system"]["log_level"] = "INFO"
    config["system"]["enable_analytics"] = True
    config["system"]["enable_performance_monitoring"] = True

    # Increase retry attempts for production reliability
    config["system"]["max_retry_attempts"] = 5

    for provider_key, provider_config in config["llm_providers"].items():
        provider_config["max_retries"] = 3

    # Prefer stable models in production
    config["llm_providers"]["qwen_coder_turbo"]["priority"] = "high"
    config["llm_providers"]["qwen_turbo"]["priority"] = "medium"
    config["llm_providers"]["gemini_pro"]["enabled"] = False  # Disable if proxy unreliable

    return config