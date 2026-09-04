"""
Speech-to-Text (STT) module
Provides interface for converting audio to text.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class STTResult:
    """Result from speech-to-text conversion."""
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class STTEngine(ABC):
    """Abstract base class for Speech-to-Text engines."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize STT engine with configuration."""
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def transcribe(self, audio_path: str) -> STTResult:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
        
        Returns:
            STTResult with transcribed text
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if STT engine is available."""
        pass
    
    def get_name(self) -> str:
        """Get engine name."""
        return self.name


class WhisperSTTEngine(STTEngine):
    """OpenAI Whisper-based Speech-to-Text."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Whisper STT engine.
        
        Config should contain:
        {
            "model": "base",  # tiny, base, small, medium, large
            "language": "en",
            "device": "cpu"  # cpu or cuda
        }
        """
        super().__init__(config)
        self.model_name = config.get("model", "base")
        self.language = config.get("language", "en")
        self.device = config.get("device", "cpu")
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Whisper model."""
        try:
            import whisper
            self.model = whisper.load_model(self.model_name, device=self.device)
        except ImportError:
            raise RuntimeError("whisper not installed. Install with: pip install openai-whisper")
    
    def transcribe(self, audio_path: str) -> STTResult:
        """Transcribe audio using Whisper."""
        try:
            result = self.model.transcribe(audio_path, language=self.language)
            return STTResult(
                text=result.get("text", "").strip(),
                language=self.language,
                metadata=result,
            )
        except Exception as e:
            raise RuntimeError(f"Whisper transcription failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Whisper is available."""
        return self.model is not None
