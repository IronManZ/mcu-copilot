"""
Factory class for creating LLM provider instances
"""

from typing import Dict, Optional
from .base import LLMProvider, LLMProviderType, LLMError

class LLMProviderFactory:
    """Factory for creating LLM provider instances"""

    _providers: Dict[LLMProviderType, type] = {}

    @classmethod
    def register_provider(cls, provider_type: LLMProviderType, provider_class: type):
        """Register a provider class with the factory"""
        cls._providers[provider_type] = provider_class

    @classmethod
    def create_provider(
        cls,
        provider_type: LLMProviderType,
        model_name: str,
        api_key: Optional[str] = None,
        **kwargs
    ) -> LLMProvider:
        """
        Create a provider instance

        Args:
            provider_type: Type of provider to create
            model_name: Name/ID of the model to use
            api_key: API key for the provider
            **kwargs: Additional provider-specific configuration

        Returns:
            LLMProvider: Instance of the requested provider

        Raises:
            LLMError: If provider type is not supported
        """
        if provider_type not in cls._providers:
            raise LLMError(
                f"Unsupported provider type: {provider_type.value}",
                provider_type.value
            )

        provider_class = cls._providers[provider_type]
        return provider_class(
            provider_type=provider_type,
            model_name=model_name,
            api_key=api_key,
            **kwargs
        )

    @classmethod
    def get_supported_providers(cls) -> list[LLMProviderType]:
        """Get list of supported provider types"""
        return list(cls._providers.keys())

    @classmethod
    def create_from_config(cls, config: Dict) -> LLMProvider:
        """
        Create a provider from a configuration dictionary

        Args:
            config: Configuration dictionary containing:
                - type: Provider type string
                - model: Model name
                - api_key: API key (optional)
                - Additional provider-specific config

        Returns:
            LLMProvider: Configured provider instance
        """
        provider_type_str = config.get("type")
        if not provider_type_str:
            raise LLMError("Missing 'type' in provider configuration", "unknown")

        try:
            provider_type = LLMProviderType(provider_type_str)
        except ValueError:
            raise LLMError(f"Invalid provider type: {provider_type_str}", provider_type_str)

        model_name = config.get("model")
        if not model_name:
            raise LLMError("Missing 'model' in provider configuration", provider_type_str)

        api_key = config.get("api_key")

        # Extract additional configuration
        provider_config = {k: v for k, v in config.items()
                          if k not in ["type", "model", "api_key"]}

        return cls.create_provider(
            provider_type=provider_type,
            model_name=model_name,
            api_key=api_key,
            **provider_config
        )