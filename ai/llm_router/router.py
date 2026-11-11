"""Configurable provider selection and optional cloud fallback."""

import logging
from typing import Any, Dict, Optional

from ai.llm_router.base_provider import LLMProvider, LLMResponse
from ai.providers.gemini_provider import GeminiProvider
from ai.providers.ollama_provider import OllamaProvider


class AIProviderRouter(LLMProvider):
    """Route Emma requests to Ollama by default, with optional Gemini use."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger("TeddyAI.Router")
        providers_config = config.get("providers", {})
        self.providers = {}

        ollama_config = providers_config.get("ollama", {})
        if ollama_config.get("enabled", True):
            self.providers["ollama"] = OllamaProvider(ollama_config)

        gemini_config = providers_config.get("gemini", {})
        if gemini_config.get("enabled", False):
            self.providers["gemini"] = GeminiProvider(gemini_config)

        routing = config.get("routing", {})
        self.default_provider = routing.get(
            "default", config.get("primary_provider", "ollama")
        )
        self.allow_cloud_fallback = routing.get("allow_cloud_fallback", False)
        self.cloud_fallback_on_error = routing.get("cloud_fallback_on_error", False)

    def _select_provider(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        context = context or {}
        if context.get("is_private"):
            return "ollama"
        if context.get("requires_multimodal") or context.get("requires_complex_reasoning"):
            if "gemini" in self.providers and self.providers["gemini"].is_available():
                return "gemini"
        return self.default_provider

    def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> LLMResponse:
        provider_name = self._select_provider(prompt, context)
        provider = self.providers.get(provider_name)
        if not provider:
            raise RuntimeError(f"Configured provider is unavailable: {provider_name}")

        try:
            response = provider.generate(prompt, context, max_tokens, temperature)
            response.metadata = response.metadata or {}
            response.metadata.update({"selected_provider": provider_name, "fallback_used": False})
            return response
        except Exception as error:
            if not self.allow_cloud_fallback or not self.cloud_fallback_on_error:
                raise
            fallback = self.providers.get("gemini")
            if provider_name == "gemini" or not fallback or not fallback.is_available():
                raise
            self.logger.warning("Provider %s failed; using Gemini fallback: %s", provider_name, error)
            response = fallback.generate(prompt, context, max_tokens, temperature)
            response.metadata = response.metadata or {}
            response.metadata.update({"selected_provider": "gemini", "fallback_used": True})
            return response

    def is_available(self) -> bool:
        """Return whether the configured default provider is available."""
        provider = self.providers.get(self.default_provider)
        return bool(provider and provider.is_available())

    def get_name(self) -> str:
        return "AIProviderRouter"
