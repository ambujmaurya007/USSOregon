"""
Ollama LLM Provider
Supports local LLM inference via Ollama API.
"""

import requests
import time
from typing import Dict, Any, Optional
from ai.llm_router.base_provider import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    """Provider for local LLM inference via Ollama."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ollama provider.
        
        Config should contain:
        {
            "api_url": "http://localhost:11434",
            "model": "qwen:7b",
            "timeout": 300
        }
        """
        super().__init__(config)
        self.api_url = config.get("api_url", "http://localhost:11434")
        self.model = config.get("model", "qwen:7b")
        self.timeout = config.get("timeout", 300)
        self._check_url = f"{self.api_url}/api/tags"
    
    def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate response using Ollama."""
        start_time = time.time()
        
        try:
            url = f"{self.api_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False,
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            data = response.json()
            latency_ms = (time.time() - start_time) * 1000
            
            return LLMResponse(
                text=data.get("response", "").strip(),
                model=self.model,
                tokens_used=data.get("total_tokens"),
                latency_ms=latency_ms,
                metadata={"raw": data},
            )
        
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(self._check_url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
