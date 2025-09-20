"""
Qwen3 Coder LLM Provider implementation
"""

import os
from typing import Dict, List, Optional, Any
from dashscope import Generation
from .base import LLMProvider, LLMProviderType, LLMResponse, LLMError

class Qwen3CoderProvider(LLMProvider):
    """Provider for Qwen3 Coder models optimized for code generation"""

    SUPPORTED_MODELS = [
        "qwen-coder-turbo",
        "qwen-coder-plus",
        "qwen-coder-32b",
        "qwen-coder-7b",
        "qwen-coder-1.5b",
        "qwen2.5-coder-32b-instruct",
        "qwen2.5-coder-14b-instruct",
        "qwen2.5-coder-7b-instruct",
        "qwen2.5-coder-3b-instruct",
        "qwen2.5-coder-1.5b-instruct"
    ]

    def __init__(self, provider_type: LLMProviderType, model_name: str, api_key: Optional[str] = None, **kwargs):
        super().__init__(provider_type, model_name, api_key)

        # Get API key from environment if not provided
        if not self.api_key:
            self.api_key = os.getenv("QIANWEN_APIKEY") or os.getenv("DASHSCOPE_API_KEY")

        # Store additional parameters
        self.additional_params = kwargs

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,  # Lower temperature for code generation
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Qwen Coder model"""

        if not self.is_available():
            return self._create_error_response("Qwen Coder provider not available - missing API key")

        try:
            # Prepare messages - add system prompt if provided
            api_messages = []
            if system_prompt:
                api_messages.append({"role": "system", "content": system_prompt})
            api_messages.extend(messages)

            # Prepare parameters with coding-optimized defaults
            params = {
                "model": self.model_name,
                "api_key": self.api_key,
                "messages": api_messages,
                "temperature": temperature,  # Lower temperature for more deterministic code
                "top_p": kwargs.get("top_p", 0.95),  # Slightly lower for focused responses
                "repetition_penalty": kwargs.get("repetition_penalty", 1.05)  # Reduce repetition
            }

            # Add optional parameters
            if max_tokens:
                params["max_tokens"] = max_tokens

            # Add any additional kwargs (excluding ones we've already handled)
            additional_kwargs = {k: v for k, v in kwargs.items()
                               if k not in ["top_p", "repetition_penalty"]}
            params.update(additional_kwargs)

            # Make API call
            response = Generation.call(**params)

            # Check for API errors
            if 'output' not in response or 'text' not in response['output']:
                error_msg = response.get('message', 'Unknown API error')
                return self._create_error_response(f"Qwen Coder API error: {error_msg}")

            # Extract response content
            content = response['output']['text']

            # Extract token usage if available
            token_usage = None
            if 'usage' in response:
                usage = response['usage']
                token_usage = {
                    "prompt_tokens": usage.get('input_tokens', 0),
                    "completion_tokens": usage.get('output_tokens', 0),
                    "total_tokens": usage.get('total_tokens', 0)
                }

            return LLMResponse(
                content=content,
                success=True,
                metadata={
                    "model": self.model_name,
                    "provider": "qwen_coder",
                    "request_id": response.get('request_id'),
                    "optimized_for": "code_generation"
                },
                token_usage=token_usage
            )

        except Exception as e:
            return self._create_error_response(f"Qwen Coder API call failed: {str(e)}", e)

    def is_available(self) -> bool:
        """Check if Qwen Coder provider is available"""
        return bool(self.api_key and self.model_name in self.SUPPORTED_MODELS)

    def validate_config(self) -> bool:
        """Validate Qwen Coder provider configuration"""
        if not self.api_key:
            return False
        if self.model_name not in self.SUPPORTED_MODELS:
            return False
        return True

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Qwen Coder provider information"""
        info = super().get_provider_info()
        info.update({
            "supported_models": self.SUPPORTED_MODELS,
            "api_key_configured": bool(self.api_key),
            "model_supported": self.model_name in self.SUPPORTED_MODELS,
            "specialization": "code_generation",
            "optimizations": [
                "Lower temperature for deterministic output",
                "Reduced top_p for focused responses",
                "Repetition penalty to avoid code duplication"
            ]
        })
        return info