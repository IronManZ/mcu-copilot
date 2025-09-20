"""
Smart Retry Manager with adaptive strategies
"""

from typing import Dict, List, Optional, Any, Callable
from .base import RetryManager, RetryStrategy, RetryResult, CompilationError
from .error_analyzer import ErrorAnalyzer, ErrorPattern

class SmartRetryManager(RetryManager):
    """Intelligent retry manager that adapts based on error patterns"""

    def __init__(self, max_attempts: int = 5, strategy: RetryStrategy = RetryStrategy.SMART_ADAPTIVE):
        super().__init__(max_attempts, strategy)
        self.error_analyzer = ErrorAnalyzer()
        self._attempt_metadata: List[Dict[str, Any]] = []

    def execute_with_retry(
        self,
        generator_func: Callable,
        validator_func: Callable,
        requirement: str,
        session_id: str,
        **kwargs
    ) -> RetryResult:
        """Execute generation with smart retry logic"""

        self._attempt_metadata = []
        all_thoughts = []
        last_code = ""
        last_thought = ""

        for attempt in range(1, self.max_attempts + 1):
            # Adapt strategy based on previous attempts
            if attempt > 1:
                strategy_params = self.adapt_strategy(
                    self._get_previous_errors(),
                    attempt
                )
                kwargs.update(strategy_params)

            try:
                # Generate code
                if attempt == 1:
                    # First attempt uses original requirement
                    thought, code = generator_func(requirement, session_id=session_id, **kwargs)
                else:
                    # Subsequent attempts use error correction
                    correction_prompt = self._build_correction_prompt(
                        self._get_previous_errors(),
                        last_code,
                        attempt
                    )
                    thought, code = generator_func(
                        correction_prompt,
                        session_id=session_id,
                        is_correction=True,
                        **kwargs
                    )

                # Store results
                last_thought = thought
                last_code = code
                all_thoughts.append(f"Attempt {attempt}: {thought}")

                # Validate/compile code
                compile_result = validator_func(code)

                # Record attempt metadata
                self._attempt_metadata.append({
                    "attempt": attempt,
                    "success": compile_result.get('success', False),
                    "errors": compile_result.get('errors', []),
                    "warnings": compile_result.get('warnings', []),
                    "code_length": len(code),
                    "thought_length": len(thought)
                })

                # Check for success
                if compile_result.get('success'):
                    return RetryResult(
                        success=True,
                        attempt_number=attempt,
                        thought_process="\n\n".join(all_thoughts),
                        generated_code=code,
                        compilation_errors=[],
                        metadata={
                            "total_attempts": attempt,
                            "strategy_used": self.strategy,
                            "session_id": session_id,
                            "attempt_details": self._attempt_metadata
                        },
                        total_attempts=attempt,
                        strategy_used=self.strategy
                    )

                # Analyze errors for next iteration
                errors = compile_result.get('errors', [])
                analyzed_errors = self.error_analyzer.analyze_errors(errors, session_id)

                # Check if we should continue retrying
                if not self.should_retry(attempt, analyzed_errors):
                    break

            except Exception as e:
                # Handle generation/validation errors
                self._attempt_metadata.append({
                    "attempt": attempt,
                    "success": False,
                    "errors": [str(e)],
                    "warnings": [],
                    "exception": True
                })

                if attempt == self.max_attempts:
                    break

        # All attempts failed
        final_errors = []
        if self._attempt_metadata:
            last_attempt = self._attempt_metadata[-1]
            error_messages = last_attempt.get('errors', [])
            final_errors = self.error_analyzer.analyze_errors(error_messages, session_id)

        return RetryResult(
            success=False,
            attempt_number=self.max_attempts,
            thought_process="\n\n".join(all_thoughts) if all_thoughts else "No thoughts generated",
            generated_code=last_code,
            compilation_errors=final_errors,
            metadata={
                "total_attempts": self.max_attempts,
                "strategy_used": self.strategy,
                "session_id": session_id,
                "attempt_details": self._attempt_metadata,
                "failure_reason": "Max attempts exceeded"
            },
            total_attempts=self.max_attempts,
            strategy_used=self.strategy
        )

    def should_retry(self, attempt: int, errors: List[CompilationError]) -> bool:
        """Determine if another retry attempt should be made"""
        if attempt >= self.max_attempts:
            return False

        # Don't retry if we've seen the same errors repeatedly
        if self._is_repeating_pattern(errors):
            return False

        # Don't retry for certain unrecoverable errors
        unrecoverable_patterns = {
            ErrorPattern.MISSING_DATA_SECTION,
            ErrorPattern.MISSING_CODE_SECTION
        }

        error_types = {error.error_type for error in errors}
        if any(pattern.value in error_types for pattern in unrecoverable_patterns):
            # Only retry once for structural errors
            return attempt == 1

        return True

    def adapt_strategy(self, errors: List[CompilationError], attempt: int) -> Dict[str, Any]:
        """Adapt the generation strategy based on previous errors"""
        strategy_params = {}

        if not errors:
            return strategy_params

        # Get error patterns
        error_patterns = [ErrorPattern(error.error_type) for error in errors
                         if error.error_type != "unknown"]

        # Adjust temperature based on error type
        if ErrorPattern.SYNTAX_ERROR in error_patterns or ErrorPattern.INVALID_INSTRUCTION in error_patterns:
            strategy_params['temperature'] = max(0.1, 0.7 - (attempt * 0.1))  # Lower temp for syntax issues

        # Add more specific guidance for repeated patterns
        if ErrorPattern.UNDEFINED_VARIABLE in error_patterns:
            strategy_params['emphasis'] = "variable_definition"
        elif ErrorPattern.JUMP_DISTANCE in error_patterns:
            strategy_params['emphasis'] = "jump_optimization"
        elif ErrorPattern.IMMEDIATE_VALUE_MISUSE in error_patterns:
            strategy_params['emphasis'] = "instruction_constraints"

        # Progressive prompting - add more constraints as attempts increase
        if attempt > 2:
            strategy_params['strict_mode'] = True
            strategy_params['include_examples'] = True

        # Consider model switching for persistent errors
        if attempt > 3:
            strategy_params['suggest_model_switch'] = True

        return strategy_params

    def _get_previous_errors(self) -> List[CompilationError]:
        """Get compilation errors from previous attempts"""
        all_errors = []
        for metadata in self._attempt_metadata:
            if not metadata.get('success', False):
                error_messages = metadata.get('errors', [])
                analyzed_errors = self.error_analyzer.analyze_errors(error_messages)
                all_errors.extend(analyzed_errors)
        return all_errors

    def _build_correction_prompt(
        self,
        errors: List[CompilationError],
        previous_code: str,
        attempt: int
    ) -> str:
        """Build a correction prompt based on errors"""
        error_messages = [error.message for error in errors]
        error_patterns = [ErrorPattern(error.error_type) for error in errors
                         if error.error_type != "unknown"]

        # Get targeted suggestions
        suggestions = self.error_analyzer.get_targeted_suggestions(error_patterns)

        correction_prompt = f"""**COMPILATION FAILED - Attempt {attempt}**

**Errors to Fix**:
{chr(10).join(f'• {msg}' for msg in error_messages)}

**Specific Fixes Needed**:
{chr(10).join(f'• {suggestion}' for suggestion in suggestions)}

**Previous Code**:
```assembly
{previous_code}
```

**Requirements**:
1. Fix ALL compilation errors listed above
2. Maintain the original functionality
3. Use only supported ZH5001 instructions
4. Ensure all variables are defined in DATA section
5. Check jump distances and use JUMP for long distances

Generate corrected code that will compile successfully."""

        return correction_prompt

    def _is_repeating_pattern(self, current_errors: List[CompilationError]) -> bool:
        """Check if we're seeing the same error pattern repeatedly"""
        if len(self._attempt_metadata) < 2:
            return False

        current_error_types = {error.error_type for error in current_errors}

        # Check last two attempts
        for metadata in self._attempt_metadata[-2:]:
            if metadata.get('success', False):
                continue

            previous_errors = metadata.get('errors', [])
            previous_analyzed = self.error_analyzer.analyze_errors(previous_errors)
            previous_types = {error.error_type for error in previous_analyzed}

            # If error types are identical, it's likely a repeating pattern
            if current_error_types == previous_types:
                return True

        return False

    def get_success_rate(self, session_id: Optional[str] = None) -> float:
        """Calculate success rate for current session or overall"""
        if not self._attempt_metadata:
            return 0.0

        successful = sum(1 for meta in self._attempt_metadata if meta.get('success', False))
        total = len(self._attempt_metadata)

        return successful / total if total > 0 else 0.0