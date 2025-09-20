"""
Qwen LLM Provider implementation
"""

import os
from typing import Dict, List, Optional, Any
from dashscope import Generation
from .base import LLMProvider, LLMProviderType, LLMResponse, LLMError

class QwenProvider(LLMProvider):
    """Provider for Alibaba's Qwen models via Dashscope API"""

    SUPPORTED_MODELS = [
        "qwen-turbo",
        "qwen-plus",
        "qwen-max",
        "qwen-max-longcontext",
        "qwen1.5-72b-chat",
        "qwen1.5-32b-chat",
        "qwen1.5-14b-chat",
        "qwen1.5-7b-chat"
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
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Qwen model"""

        if not self.is_available():
            return self._create_error_response("Qwen provider not available - missing API key")

        try:
            # Prepare messages - add system prompt if provided
            api_messages = []
            if system_prompt:
                api_messages.append({"role": "system", "content": system_prompt})
            api_messages.extend(messages)

            # Prepare parameters
            params = {
                "model": self.model_name,
                "api_key": self.api_key,
                "messages": api_messages
            }

            # Add optional parameters
            if temperature != 0.7:
                params["temperature"] = temperature
            if max_tokens:
                params["max_tokens"] = max_tokens

            # Add any additional kwargs
            params.update(kwargs)

            # Make API call
            response = Generation.call(**params)

            # Check for API errors
            if 'output' not in response or 'text' not in response['output']:
                error_msg = response.get('message', 'Unknown API error')
                return self._create_error_response(f"Qwen API error: {error_msg}")

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
                    "provider": "qwen",
                    "request_id": response.get('request_id')
                },
                token_usage=token_usage
            )

        except Exception as e:
            return self._create_error_response(f"Qwen API call failed: {str(e)}", e)

    def is_available(self) -> bool:
        """Check if Qwen provider is available"""
        return bool(self.api_key and self.model_name in self.SUPPORTED_MODELS)

    def validate_config(self) -> bool:
        """Validate Qwen provider configuration"""
        if not self.api_key:
            return False
        if self.model_name not in self.SUPPORTED_MODELS:
            return False
        return True

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Qwen provider information"""
        info = super().get_provider_info()
        info.update({
            "supported_models": self.SUPPORTED_MODELS,
            "api_key_configured": bool(self.api_key),
            "model_supported": self.model_name in self.SUPPORTED_MODELS
        })
        return info