"""
Natural Language to Assembly Conversion - Version 2

Clean, modular implementation using the new LLM provider architecture,
smart retry logic, and structured logging.
"""

import uuid
import time
from typing import Tuple, Optional, Dict, Any

# Import new architecture components
from .llm import LLMProviderFactory, LLMProviderType, LLMError
from .prompts import prompt_manager, PromptVersion
from .retry import SmartRetryManager, RetryStrategy
from .analytics import StructuredLogger, MetricsCollector
from .config import config_manager
from .compiler.zh5001_service import ZH5001CompilerService

class NLToAssemblyService:
    """
    Natural Language to Assembly conversion service using new architecture
    """

    def __init__(self):
        self.config = config_manager.get_system_config()
        self.logger = StructuredLogger(self.config.log_directory)
        self.metrics = MetricsCollector()
        self.retry_manager = SmartRetryManager(
            max_attempts=self.config.max_retry_attempts,
            strategy=RetryStrategy(self.config.default_retry_strategy)
        )
        self.compiler_service = ZH5001CompilerService()

    def generate_assembly(
        self,
        requirement: str,
        provider_override: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        Convert natural language requirement to ZH5001 assembly code

        Args:
            requirement: Natural language description of the desired functionality
            provider_override: Optional provider key to use instead of auto-selection
            session_id: Optional session identifier for tracking
            **kwargs: Additional parameters

        Returns:
            Tuple[str, str]: (thought_process, assembly_code)

        Raises:
            LLMError: If generation fails after all retry attempts
        """
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]

        start_time = time.time()

        try:
            # Select provider
            provider_key = provider_override or config_manager.get_best_available_provider()
            if not provider_key:
                raise LLMError("No available LLM providers configured", "system")

            llm_config = config_manager.get_llm_config(provider_key)
            if not llm_config:
                raise LLMError(f"Configuration not found for provider: {provider_key}", provider_key)

            # Create provider instance
            provider = LLMProviderFactory.create_provider(
                provider_type=LLMProviderType(llm_config.provider_type),
                model_name=llm_config.model_name,
                api_key=llm_config.api_key,
                **llm_config.additional_params
            )

            # Start metrics collection
            self.metrics.start_session(session_id, llm_config.provider_type, llm_config.model_name, requirement)

            # Log session start
            self.logger.log_session_start(
                session_id=session_id,
                requirement=requirement,
                provider=llm_config.provider_type,
                model=llm_config.model_name
            )

            # Create generation and validation functions for retry manager
            def generate_code(prompt_text: str, session_id: str, is_correction: bool = False, **gen_kwargs) -> Tuple[str, str]:
                return self._generate_with_provider(
                    provider=provider,
                    prompt_text=prompt_text,
                    session_id=session_id,
                    llm_config=llm_config,
                    is_correction=is_correction,
                    **gen_kwargs
                )

            def validate_code(code: str) -> Dict[str, Any]:
                return self.compiler_service.compile_assembly(code)

            # Execute with smart retry
            retry_result = self.retry_manager.execute_with_retry(
                generator_func=generate_code,
                validator_func=validate_code,
                requirement=requirement,
                session_id=session_id,
                **kwargs
            )

            # Calculate total duration
            total_duration_ms = (time.time() - start_time) * 1000

            # Log session end
            self.logger.log_session_end(
                session_id=session_id,
                success=retry_result.success,
                total_attempts=retry_result.total_attempts,
                final_code_length=len(retry_result.generated_code),
                total_duration_ms=total_duration_ms,
                provider=llm_config.provider_type,
                model=llm_config.model_name
            )

            # Collect final metrics
            final_metrics = self.metrics.end_session(
                session_id=session_id,
                final_success=retry_result.success,
                final_code_length=len(retry_result.generated_code)
            )

            # Log performance metrics
            if self.config.enable_performance_monitoring:
                self.logger.log_performance_metrics(session_id, final_metrics.__dict__)

            if retry_result.success:
                return retry_result.thought_process, retry_result.generated_code
            else:
                # Even if unsuccessful, return the last attempt for debugging
                error_msg = f"Failed to generate working assembly code after {retry_result.total_attempts} attempts"
                if retry_result.compilation_errors:
                    error_details = "; ".join([error.message for error in retry_result.compilation_errors[:3]])
                    error_msg += f". Last errors: {error_details}"

                raise LLMError(error_msg, llm_config.provider_type)

        except Exception as e:
            # Log error
            self.logger.log_error(
                session_id=session_id,
                error_type=type(e).__name__,
                error_message=str(e),
                context={"requirement": requirement, "provider": provider_key if 'provider_key' in locals() else None}
            )

            # Re-raise as LLMError if not already
            if isinstance(e, LLMError):
                raise
            else:
                raise LLMError(f"Unexpected error in assembly generation: {str(e)}", "system", e)

    def _generate_with_provider(
        self,
        provider,
        prompt_text: str,
        session_id: str,
        llm_config,
        is_correction: bool = False,
        attempt_number: int = 1,
        **kwargs
    ) -> Tuple[str, str]:
        """Generate code using the specified provider"""

        # Build appropriate prompts based on provider type and version
        if is_correction:
            # For corrections, use the prompt_text directly as user prompt
            system_prompt = prompt_manager.get_builder("zh5001").build_system_prompt(
                PromptVersion(self.config.prompt_version)
            )
            user_prompt = prompt_text
        else:
            # For initial generation, build prompts using prompt manager
            system_prompt, user_prompt = prompt_manager.build_prompt_for_provider(
                builder_name="zh5001",
                provider_type=llm_config.provider_type,
                requirement=prompt_text,
                version=PromptVersion(self.config.prompt_version),
                **kwargs
            )

        # Prepare messages for the provider
        messages = [{"role": "user", "content": user_prompt}]

        # Log LLM request
        prompt_length = len(system_prompt) + len(user_prompt)
        self.logger.log_llm_request(
            session_id=session_id,
            provider=llm_config.provider_type,
            model=llm_config.model_name,
            prompt_length=prompt_length,
            attempt=attempt_number
        )

        # Record request timing
        request_start = time.time()

        # Filter out conflicting parameters from kwargs
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens', 'system_prompt']}

        # Use retry system temperature if provided, otherwise use config temperature
        final_temperature = kwargs.get('temperature', llm_config.temperature)

        # Make LLM API call
        response = provider.generate(
            messages=messages,
            system_prompt=system_prompt,
            temperature=final_temperature,
            max_tokens=llm_config.max_tokens,
            **filtered_kwargs
        )

        # Calculate duration
        duration_ms = (time.time() - request_start) * 1000

        # Log LLM response
        self.logger.log_llm_response(
            session_id=session_id,
            provider=llm_config.provider_type,
            model=llm_config.model_name,
            success=response.success,
            response_length=len(response.content) if response.success else None,
            duration_ms=duration_ms,
            token_usage=response.token_usage,
            error_message=response.error_message if not response.success else None
        )

        # Record metrics
        self.metrics.record_llm_call(
            session_id=session_id,
            attempt=attempt_number,
            duration_ms=duration_ms,
            success=response.success,
            prompt_tokens=response.token_usage.get("prompt_tokens", 0) if response.token_usage else 0,
            completion_tokens=response.token_usage.get("completion_tokens", 0) if response.token_usage else 0,
            error=response.error_message if not response.success else None
        )

        if not response.success:
            raise LLMError(
                f"LLM API call failed: {response.error_message}",
                llm_config.provider_type
            )

        # Parse the response to extract thought process and assembly code
        thought, assembly = self._parse_llm_response(response.content, llm_config.provider_type)

        if not assembly:
            raise LLMError(
                "No assembly code found in LLM response",
                llm_config.provider_type
            )

        return thought, assembly

    def _parse_llm_response(self, response_content: str, provider_type: str) -> Tuple[str, str]:
        """Parse LLM response to extract thought process and assembly code"""

        # Try JSON format first (preferred for structured responses)
        thought, assembly = self._try_parse_json_response(response_content)
        if thought and assembly:
            return thought, assembly

        # Fallback to text parsing
        return self._parse_text_response(response_content)

    def _try_parse_json_response(self, response: str) -> Tuple[Optional[str], Optional[str]]:
        """Try to parse response as JSON format"""
        try:
            import json
            import re

            # Find JSON in response - look for complete JSON objects
            json_match = re.search(r'\{[^{}]*"assembly_code"[^{}]*\}', response, re.DOTALL)
            if not json_match:
                # Try to find any JSON block
                json_match = re.search(r'```json\s*\n(.*?)\n```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if not json_match:
                        return None, None
                    json_str = json_match.group()
            else:
                json_str = json_match.group()

            data = json.loads(json_str)

            # Extract thought process
            thought_parts = []
            if data.get('description'):
                thought_parts.append(data['description'])
            if data.get('thought_process'):
                thought_parts.append(data['thought_process'])

            thought = '\n\n'.join(thought_parts) if thought_parts else ''

            # Extract assembly code
            assembly = data.get('assembly_code', '')

            # Convert \n to actual newlines if needed
            if assembly and '\\n' in assembly:
                assembly = assembly.replace('\\n', '\n')

            # Only return if we have assembly code
            if assembly:
                return thought, assembly
            else:
                return None, None

        except (json.JSONDecodeError, KeyError, AttributeError):
            return None, None

    def _parse_text_response(self, response: str) -> Tuple[str, str]:
        """Parse text response to extract thought and assembly"""
        import re

        # Try to find assembly code in code blocks
        code_block_match = re.search(r'```(?:asm|assembly)?\s*\n(.*?)\n```', response, re.DOTALL | re.IGNORECASE)

        if code_block_match:
            assembly = code_block_match.group(1).strip()
            # Everything before the code block is thought process
            thought_part = response[:code_block_match.start()].strip()
            thought = re.sub(r'^思考过程：?\s*', '', thought_part, flags=re.MULTILINE).strip()
        else:
            # Try to find DATA/CODE structure
            data_code_match = re.search(r'(DATA[\s\S]*?ENDDATA[\s\S]*?CODE[\s\S]*?ENDCODE)', response, re.IGNORECASE)
            if data_code_match:
                assembly = data_code_match.group(1).strip()
                thought = response.replace(assembly, '').strip()
            else:
                # Last resort: everything is thought, no assembly
                thought = response.strip()
                assembly = ''

        return thought, assembly

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all configured providers"""
        status = {}

        for provider_key, config in config_manager.get_all_llm_configs().items():
            try:
                provider = LLMProviderFactory.create_provider(
                    provider_type=LLMProviderType(config.provider_type),
                    model_name=config.model_name,
                    api_key=config.api_key,
                    **config.additional_params
                )

                status[provider_key] = {
                    "available": provider.is_available(),
                    "config_valid": provider.validate_config(),
                    "provider_info": provider.get_provider_info(),
                    "config": {
                        "model": config.model_name,
                        "priority": config.priority.value,
                        "enabled": config.enabled
                    }
                }
            except Exception as e:
                status[provider_key] = {
                    "available": False,
                    "error": str(e),
                    "config": {
                        "model": config.model_name,
                        "priority": config.priority.value,
                        "enabled": config.enabled
                    }
                }

        return status

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.metrics.get_global_statistics()

    def get_recommendations(self) -> Dict[str, Any]:
        """Get recommendations for improving performance"""
        return self.metrics.get_recommendations()

# Create global service instance
nl_to_assembly_service = NLToAssemblyService()