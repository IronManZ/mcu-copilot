"""
Prompt Manager for centralized prompt handling
"""

from typing import Dict, List, Optional, Type
from .base import PromptBuilder, PromptVersion, PromptTemplate, PromptError

class PromptManager:
    """Manages prompt builders and templates"""

    def __init__(self):
        self._builders: Dict[str, PromptBuilder] = {}
        self._templates: Dict[str, PromptTemplate] = {}

    def register_builder(self, name: str, builder: PromptBuilder):
        """Register a prompt builder"""
        self._builders[name] = builder

    def get_builder(self, name: str) -> PromptBuilder:
        """Get a prompt builder by name"""
        if name not in self._builders:
            raise PromptError(f"Builder '{name}' not found")
        return self._builders[name]

    def register_template(self, template: PromptTemplate):
        """Register a prompt template"""
        self._templates[template.name] = template

    def get_template(self, name: str) -> PromptTemplate:
        """Get a prompt template by name"""
        if name not in self._templates:
            raise PromptError(f"Template '{name}' not found")
        return self._templates[name]

    def list_builders(self) -> List[str]:
        """List all registered builder names"""
        return list(self._builders.keys())

    def list_templates(self) -> List[str]:
        """List all registered template names"""
        return list(self._templates.keys())

    def build_prompt_for_provider(
        self,
        builder_name: str,
        provider_type: str,
        requirement: str,
        version: PromptVersion = PromptVersion.V4_STRUCTURED,
        **kwargs
    ) -> tuple[str, str]:
        """
        Build optimized prompts for a specific provider

        Returns:
            tuple: (system_prompt, user_prompt)
        """
        builder = self.get_builder(builder_name)

        # Get provider-optimized version if available
        if provider_type == "qwen_coder" and PromptVersion.V3_CODER in builder.get_supported_versions():
            version = PromptVersion.V3_CODER
        elif provider_type == "gemini" and PromptVersion.V2_OPTIMIZED in builder.get_supported_versions():
            version = PromptVersion.V2_OPTIMIZED

        system_prompt = builder.build_system_prompt(version)
        user_prompt = builder.build_user_prompt(requirement, **kwargs)

        return system_prompt, user_prompt

    def build_error_correction_prompt(
        self,
        builder_name: str,
        errors: List[str],
        previous_code: str,
        attempt_number: int
    ) -> str:
        """Build error correction prompt"""
        builder = self.get_builder(builder_name)
        return builder.build_error_correction_prompt(errors, previous_code, attempt_number)

# Global prompt manager instance
prompt_manager = PromptManager()