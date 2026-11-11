"""Microphone capture for the local voice pipeline."""

from pathlib import Path
from typing import Any, Dict, Optional, Union
import wave


class MicrophoneRecorder:
    """Record mono PCM audio from a system microphone."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sample_rate = int(self.config.get("sample_rate", 16000))
        self.channels = int(self.config.get("channels", 1))
        self.dtype = self.config.get("dtype", "int16")
        self.device = self.config.get("device")
        self._sounddevice = None

    def _load_sounddevice(self):
        if self._sounddevice is None:
            try:
                import sounddevice
            except ImportError as error:
                raise RuntimeError(
                    "sounddevice is not installed. Install with: "
                    "pip install sounddevice"
                ) from error
            self._sounddevice = sounddevice
        return self._sounddevice

    def list_devices(self):
        """Return the available audio devices."""
        return self._load_sounddevice().query_devices()

    def is_available(self) -> bool:
        """Return whether a usable input device is available."""
        try:
            devices = self.list_devices()
            return any(device.get("max_input_channels", 0) > 0 for device in devices)
        except Exception:
            return False

    def record(self, duration_seconds: float, output_path: Union[str, Path]) -> str:
        """Record for a fixed duration and save a PCM WAV file."""
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be greater than zero")

        sounddevice = self._load_sounddevice()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            recording = sounddevice.rec(
                int(duration_seconds * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                device=self.device,
            )
            sounddevice.wait()
        except Exception as error:
            raise RuntimeError(f"Microphone recording failed: {error}") from error

        try:
            with wave.open(str(output_file), "wb") as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(recording.tobytes())
        except Exception as error:
            raise RuntimeError(f"Could not save microphone recording: {error}") from error

        return str(output_file)
