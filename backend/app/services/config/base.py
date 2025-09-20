"""
Base configuration classes and manager
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json

class ModelPriority(Enum):
    """Model priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider_type: str
    model_name: str
    api_key: Optional[str] = None
    priority: ModelPriority = ModelPriority.MEDIUM
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout_seconds: int = 60
    max_retries: int = 3
    enabled: bool = True
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemConfig:
    """System-wide configuration"""
    log_level: str = "INFO"
    log_directory: str = "logs"
    max_retry_attempts: int = 5
    default_retry_strategy: str = "smart_adaptive"
    enable_analytics: bool = True
    enable_performance_monitoring: bool = True
    prompt_version: str = "v4_structured"
    compilation_timeout_seconds: int = 30

class ConfigManager:
    """Manages system and LLM configurations"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.getenv("MCU_COPILOT_CONFIG", "mcu_copilot_config.json")
        self._llm_configs: Dict[str, LLMConfig] = {}
        self._system_config = SystemConfig()
        self._load_config()

    def _load_config(self):
        """Load configuration from file and environment"""
        # Load from file if it exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self._parse_config_data(config_data)
            except Exception as e:
                print(f"Warning: Failed to load config file {self.config_file}: {e}")

        # Override with environment variables
        self._load_from_environment()

    def _parse_config_data(self, config_data: Dict[str, Any]):
        """Parse configuration data from file"""
        # Parse system config
        system_data = config_data.get("system", {})
        self._system_config = SystemConfig(
            log_level=system_data.get("log_level", self._system_config.log_level),
            log_directory=system_data.get("log_directory", self._system_config.log_directory),
            max_retry_attempts=system_data.get("max_retry_attempts", self._system_config.max_retry_attempts),
            default_retry_strategy=system_data.get("default_retry_strategy", self._system_config.default_retry_strategy),
            enable_analytics=system_data.get("enable_analytics", self._system_config.enable_analytics),
            enable_performance_monitoring=system_data.get("enable_performance_monitoring", self._system_config.enable_performance_monitoring),
            prompt_version=system_data.get("prompt_version", self._system_config.prompt_version),
            compilation_timeout_seconds=system_data.get("compilation_timeout_seconds", self._system_config.compilation_timeout_seconds)
        )

        # Parse LLM configs
        llm_configs = config_data.get("llm_providers", {})
        for provider_key, provider_data in llm_configs.items():
            try:
                priority = ModelPriority(provider_data.get("priority", "medium"))
                config = LLMConfig(
                    provider_type=provider_data["provider_type"],
                    model_name=provider_data["model_name"],
                    api_key=provider_data.get("api_key"),
                    priority=priority,
                    temperature=provider_data.get("temperature", 0.7),
                    max_tokens=provider_data.get("max_tokens"),
                    timeout_seconds=provider_data.get("timeout_seconds", 60),
                    max_retries=provider_data.get("max_retries", 3),
                    enabled=provider_data.get("enabled", True),
                    additional_params=provider_data.get("additional_params", {})
                )
                self._llm_configs[provider_key] = config
            except KeyError as e:
                print(f"Warning: Invalid LLM config for {provider_key}: missing {e}")
            except ValueError as e:
                print(f"Warning: Invalid priority value for {provider_key}: {e}")

    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # System config from environment
        if os.getenv("LOG_LEVEL"):
            self._system_config.log_level = os.getenv("LOG_LEVEL")

        if os.getenv("MAX_RETRY_ATTEMPTS"):
            try:
                self._system_config.max_retry_attempts = int(os.getenv("MAX_RETRY_ATTEMPTS"))
            except ValueError:
                pass

        # LLM API keys from environment
        qwen_api_key = os.getenv("QIANWEN_APIKEY") or os.getenv("DASHSCOPE_API_KEY")
        gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        # Apply to all relevant providers
        for provider_key, config in self._llm_configs.items():
            if config.provider_type in ["qwen", "qwen_coder"] and qwen_api_key:
                config.api_key = qwen_api_key
            elif config.provider_type == "gemini" and gemini_api_key:
                config.api_key = gemini_api_key

    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        return self._system_config

    def get_llm_config(self, provider_key: str) -> Optional[LLMConfig]:
        """Get LLM configuration by provider key"""
        return self._llm_configs.get(provider_key)

    def get_all_llm_configs(self) -> Dict[str, LLMConfig]:
        """Get all LLM configurations"""
        return self._llm_configs.copy()

    def get_enabled_llm_configs(self) -> Dict[str, LLMConfig]:
        """Get only enabled LLM configurations"""
        return {key: config for key, config in self._llm_configs.items() if config.enabled}

    def get_providers_by_priority(self, priority: ModelPriority) -> List[str]:
        """Get provider keys by priority level"""
        return [
            key for key, config in self._llm_configs.items()
            if config.priority == priority and config.enabled
        ]

    def get_best_available_provider(self) -> Optional[str]:
        """Get the best available provider based on priority and availability"""
        # Try high priority first
        high_priority = self.get_providers_by_priority(ModelPriority.HIGH)
        for provider_key in high_priority:
            config = self._llm_configs[provider_key]
            if config.api_key:  # Has API key configured
                return provider_key

        # Try medium priority
        medium_priority = self.get_providers_by_priority(ModelPriority.MEDIUM)
        for provider_key in medium_priority:
            config = self._llm_configs[provider_key]
            if config.api_key:
                return provider_key

        # Try low priority
        low_priority = self.get_providers_by_priority(ModelPriority.LOW)
        for provider_key in low_priority:
            config = self._llm_configs[provider_key]
            if config.api_key:
                return provider_key

        return None

    def add_llm_config(self, provider_key: str, config: LLMConfig):
        """Add or update LLM configuration"""
        self._llm_configs[provider_key] = config

    def remove_llm_config(self, provider_key: str):
        """Remove LLM configuration"""
        if provider_key in self._llm_configs:
            del self._llm_configs[provider_key]

    def save_config(self, file_path: Optional[str] = None):
        """Save current configuration to file"""
        save_path = file_path or self.config_file

        config_data = {
            "system": {
                "log_level": self._system_config.log_level,
                "log_directory": self._system_config.log_directory,
                "max_retry_attempts": self._system_config.max_retry_attempts,
                "default_retry_strategy": self._system_config.default_retry_strategy,
                "enable_analytics": self._system_config.enable_analytics,
                "enable_performance_monitoring": self._system_config.enable_performance_monitoring,
                "prompt_version": self._system_config.prompt_version,
                "compilation_timeout_seconds": self._system_config.compilation_timeout_seconds
            },
            "llm_providers": {}
        }

        for provider_key, config in self._llm_configs.items():
            config_data["llm_providers"][provider_key] = {
                "provider_type": config.provider_type,
                "model_name": config.model_name,
                "api_key": config.api_key,
                "priority": config.priority.value,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "timeout_seconds": config.timeout_seconds,
                "max_retries": config.max_retries,
                "enabled": config.enabled,
                "additional_params": config.additional_params
            }

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to save config to {save_path}: {e}")

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return status"""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "provider_status": {}
        }

        # Check if any providers are configured
        if not self._llm_configs:
            validation_result["errors"].append("No LLM providers configured")
            validation_result["valid"] = False

        # Check each provider
        enabled_providers = 0
        for provider_key, config in self._llm_configs.items():
            provider_status = {
                "enabled": config.enabled,
                "has_api_key": bool(config.api_key),
                "valid_config": True,
                "issues": []
            }

            if config.enabled:
                enabled_providers += 1

                if not config.api_key:
                    provider_status["issues"].append("Missing API key")
                    validation_result["warnings"].append(f"{provider_key}: No API key configured")

                if config.temperature < 0 or config.temperature > 2:
                    provider_status["issues"].append("Invalid temperature range")
                    provider_status["valid_config"] = False

                if config.max_retries < 0:
                    provider_status["issues"].append("Invalid max_retries value")
                    provider_status["valid_config"] = False

            validation_result["provider_status"][provider_key] = provider_status

        if enabled_providers == 0:
            validation_result["errors"].append("No enabled providers found")
            validation_result["valid"] = False

        # Validate system config
        if self._system_config.max_retry_attempts < 1:
            validation_result["errors"].append("max_retry_attempts must be at least 1")
            validation_result["valid"] = False

        if validation_result["errors"]:
            validation_result["valid"] = False

        return validation_result