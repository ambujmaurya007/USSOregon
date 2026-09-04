"""
LLM Provider abstract base class and interface definitions.
All LLM providers must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    text: str
    model: str
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize provider with configuration."""
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate response from prompt.
        
        Args:
            prompt: Input prompt text
            context: Optional context dictionary
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
        
        Returns:
            LLMResponse with generated text
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and configured."""
        pass
    
    def get_name(self) -> str:
        """Get provider name."""
        return self.name
    
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration."""
        return self.config.copy()


# Provider-specific implementations will be in separate files
