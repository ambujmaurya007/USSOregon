"""Google Gemini provider using the Gemini generateContent REST API."""

import os
import time
from typing import Any, Dict, Optional

import requests

from ai.llm_router.base_provider import LLMProvider, LLMResponse


class GeminiProvider(LLMProvider):
    """Optional cloud provider for requests needing additional capability."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = config.get("model", "gemini-2.5-flash")
        self.api_key = os.getenv(config.get("api_key_env", "GEMINI_API_KEY"), "")
        self.timeout = config.get("timeout", 60)
        self.api_url = config.get(
            "api_url",
            "https://generativelanguage.googleapis.com/v1beta/models",
        )

    def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a response through Gemini."""
        if not self.api_key:
            raise RuntimeError("Gemini is not configured: set GEMINI_API_KEY")

        start_time = time.time()
        url = f"{self.api_url}/{self.model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }

        try:
            response = requests.post(
                url,
                params={"key": self.api_key},
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            text = ""
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                text = "".join(part.get("text", "") for part in parts).strip()
            if not text:
                raise RuntimeError("Gemini returned an empty response")

            return LLMResponse(
                text=text,
                model=self.model,
                latency_ms=(time.time() - start_time) * 1000,
                metadata={"provider": "gemini", "raw": data},
            )
        except RuntimeError:
            raise
        except Exception as error:
            raise RuntimeError(f"Gemini generation failed: {error}") from error

    def is_available(self) -> bool:
        """Return whether Gemini has an API key configured."""
        return bool(self.api_key)
