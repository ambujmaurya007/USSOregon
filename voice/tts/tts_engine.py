"""
Text-to-Speech (TTS) module
Provides interface for converting text to audio.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TTSResult:
    """Result from text-to-speech conversion."""
    audio_path: str
    duration_ms: Optional[float] = None
    model: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TTSEngine(ABC):
    """Abstract base class for Text-to-Speech engines."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize TTS engine with configuration."""
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def synthesize(self, text: str, output_path: str) -> TTSResult:
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to synthesize
            output_path: Path where audio file will be saved
        
        Returns:
            TTSResult with path to generated audio
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if TTS engine is available."""
        pass
    
    def get_name(self) -> str:
        """Get engine name."""
        return self.name


class PiperTTSEngine(TTSEngine):
    """Piper-based Text-to-Speech engine."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Piper TTS engine.
        
        Config should contain:
        {
            "voice": "en_US-jenny_low",
            "model_path": "./models/en_US-lessac-medium.onnx",
            "speaker": 0,
            "length_scale": 1.0,
            "noise_scale": 0.667
        }
        """
        super().__init__(config)
        self.voice = config.get("voice", "en_US-jenny_low")
        self.model_path = config.get("model_path")
        self.speaker = config.get("speaker", 0)
        self.length_scale = config.get("length_scale", 1.0)
        self.noise_scale = config.get("noise_scale", 0.667)
        self.piper = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Piper TTS."""
        try:
            from piper import PiperVoice

            if not self.model_path:
                raise RuntimeError("Piper model_path is not configured")

            self.piper = PiperVoice.load(self.model_path)
        except ImportError:
            raise RuntimeError("piper not installed. Install with: pip install piper-tts")
    
    def synthesize(self, text: str, output_path: str) -> TTSResult:
        """Synthesize text to speech using Piper."""
        try:
            if not self.piper:
                raise RuntimeError("Piper voice is not initialized")

            import wave
            from pathlib import Path
            from piper.config import SynthesisConfig

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            synthesis_config = SynthesisConfig(
                speaker_id=self.speaker,
                length_scale=self.length_scale,
                noise_scale=self.noise_scale,
            )
            with wave.open(str(output_file), "wb") as wav_file:
                self.piper.synthesize_wav(text, wav_file, syn_config=synthesis_config)

            with wave.open(str(output_file), "rb") as wav_file:
                duration_ms = wav_file.getnframes() / wav_file.getframerate() * 1000
            
            return TTSResult(
                audio_path=output_path,
                duration_ms=duration_ms,
                model=self.voice,
            )
        except Exception as e:
            raise RuntimeError(f"Piper synthesis failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Piper TTS is available."""
        return self.piper is not None
