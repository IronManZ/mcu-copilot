"""
Gemini LLM Provider implementation
"""

import os
from typing import Dict, List, Optional, Any
from .base import LLMProvider, LLMProviderType, LLMResponse, LLMError

# Optional Gemini import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

class GeminiProvider(LLMProvider):
    """Provider for Google's Gemini models"""

    SUPPORTED_MODELS = [
        # Latest 2025 models (recommended)
        "gemini-2.5-flash",      # Newest multimodal model, improved capabilities
        "gemini-2.5-pro",        # Most powerful thinking model for complex reasoning
        "gemini-2.5-flash-lite", # Fastest and most cost-efficient
        "gemini-2.0-flash",      # Previous generation

        # Legacy models (still supported)
        "gemini-pro",
        "gemini-pro-vision",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.0-pro"
    ]

    def __init__(self, provider_type: LLMProviderType, model_name: str, api_key: Optional[str] = None, **kwargs):
        super().__init__(provider_type, model_name, api_key)

        # Get API key from environment if not provided
        if not self.api_key:
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        # Extract proxy from kwargs or environment
        self.proxy = kwargs.get("proxy") or os.getenv("GEMINI_PROXY")
        self._model = None

        # Store additional parameters
        self.additional_params = kwargs

        # Configure Gemini if available
        if GEMINI_AVAILABLE and self.api_key:
            self._configure_gemini()

    def _configure_gemini(self):
        """Configure Gemini API client"""
        try:
            # Set proxy if configured
            if self.proxy:
                os.environ['HTTP_PROXY'] = self.proxy
                os.environ['HTTPS_PROXY'] = self.proxy

            # Configure API
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)

        except Exception as e:
            self._model = None
            raise LLMError(f"Failed to configure Gemini: {str(e)}", "gemini", e)

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Gemini model"""

        if not self.is_available():
            return self._create_error_response("Gemini provider not available")

        if not GEMINI_AVAILABLE:
            return self._create_error_response("Gemini SDK not installed. Install: pip install google-generativeai")

        try:
            # Prepare the full prompt
            full_prompt = ""

            # Add system prompt if provided
            if system_prompt:
                full_prompt += f"{system_prompt}\n\n"

            # Add conversation history
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                if role == "user":
                    full_prompt += f"Human: {content}\n"
                elif role == "assistant":
                    full_prompt += f"Assistant: {content}\n"

            # Configure generation parameters
            generation_config = {
                "temperature": temperature,
                "candidate_count": 1,
            }

            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Add any additional generation config from kwargs
            generation_config.update(kwargs.get("generation_config", {}))

            # Configure safety settings to be less restrictive for code generation
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]

            # Make API call
            response = self._model.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            # Check for response and handle safety filtering
            if not response.text:
                error_msg = "Gemini returned empty response"
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason'):
                        if candidate.finish_reason == 2:  # SAFETY
                            error_msg = "Response blocked by safety filters"
                        elif candidate.finish_reason == 3:  # RECITATION
                            error_msg = "Response blocked due to recitation"
                        elif candidate.finish_reason == 4:  # OTHER
                            error_msg = "Response blocked for other reasons"
                return self._create_error_response(error_msg)

            # Extract token usage if available
            token_usage = None
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                token_usage = {
                    "prompt_tokens": getattr(usage, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage, 'total_token_count', 0)
                }

            return LLMResponse(
                content=response.text,
                success=True,
                metadata={
                    "model": self.model_name,
                    "provider": "gemini",
                    "proxy_used": bool(self.proxy),
                    "generation_config": generation_config
                },
                token_usage=token_usage
            )

        except Exception as e:
            return self._create_error_response(f"Gemini API call failed: {str(e)}", e)

    def is_available(self) -> bool:
        """Check if Gemini provider is available"""
        return (GEMINI_AVAILABLE and
                bool(self.api_key) and
                self.model_name in self.SUPPORTED_MODELS and
                self._model is not None)

    def validate_config(self) -> bool:
        """Validate Gemini provider configuration"""
        if not GEMINI_AVAILABLE:
            return False
        if not self.api_key:
            return False
        if self.model_name not in self.SUPPORTED_MODELS:
            return False
        return True

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Gemini provider information"""
        info = super().get_provider_info()
        info.update({
            "supported_models": self.SUPPORTED_MODELS,
            "api_key_configured": bool(self.api_key),
            "model_supported": self.model_name in self.SUPPORTED_MODELS,
            "sdk_available": GEMINI_AVAILABLE,
            "proxy_configured": bool(self.proxy),
            "model_initialized": self._model is not None
        })
        return info