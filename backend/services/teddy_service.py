"""
Main backend service for Teddy AI
Orchestrates voice pipeline, LLM, memory, and personality.
"""

import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

from ai.providers.ollama_provider import OllamaProvider
from memory.long_term.memory_backend import SQLiteMemoryBackend, ShortTermMemory
from personality.personality_engine import PersonalityEngine
from voice.stt.stt_engine import WhisperSTTEngine
from voice.tts.tts_engine import PiperTTSEngine


class RequestType(Enum):
    """Types of requests that might be routed differently."""
    STORY = "story"
    CONVERSATION = "conversation"
    EDUCATIONAL = "educational"
    COMPLEX = "complex"


class TeddyAIService:
    """Main service orchestrating all Teddy AI components."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Teddy AI service.
        
        Args:
            config: Configuration dictionary (loaded from YAML)
        """
        self.config = config
        self.logger = self._setup_logging()
        
        self.llm_provider: Optional[Any] = None
        self.stt_engine: Optional[Any] = None
        self.tts_engine: Optional[Any] = None
        self.memory_backend: Optional[Any] = None
        self.short_term_memory: Optional[Any] = None
        self.personality_engine: Optional[Any] = None
        
        self.logger.info("Teddy AI Service initializing...")
        self._initialize_components()
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging."""
        logger = logging.getLogger("TeddyAI")
        level = self.config.get("logging", {}).get("level", "INFO")
        logger.setLevel(level)
        
        # Console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            self.config.get("logging", {}).get(
                "format",
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _initialize_components(self):
        """Initialize all components based on config."""
        self.logger.info("Initializing components...")
        
        # Initialize memory
        try:
            memory_config = self.config.get("memory", {})
            db_path = memory_config.get("sqlite", {}).get("db_path", "./data/teddy.db")
            self.memory_backend = SQLiteMemoryBackend(db_path)
            self.short_term_memory = ShortTermMemory()
            self._restore_conversation()
            self.logger.info("✓ Memory system initialized")
        except Exception as e:
            self.logger.error(f"✗ Memory initialization failed: {e}")
        
        # Initialize personality
        try:
            personality_config = self.config.get("personality", {})
            self.personality_engine = PersonalityEngine(
                personality_config.get("config_path")
            )
            self.logger.info("✓ Personality engine initialized")
        except Exception as e:
            self.logger.error(f"✗ Personality initialization failed: {e}")
        
        # Initialize LLM provider
        try:
            llm_config = self.config.get("llm", {})
            provider_name = llm_config.get("primary_provider", "ollama")
            provider_config = llm_config.get("providers", {}).get(provider_name, {})
            if provider_name != "ollama":
                raise ValueError(f"Unsupported provider: {provider_name}")
            self.llm_provider = OllamaProvider(provider_config)
            self.logger.info(f"✓ LLM provider initialized: {self.llm_provider.get_name()}")
        except Exception as e:
            self.logger.error(f"✗ LLM initialization failed: {e}")
        
        # Initialize STT
        try:
            stt_config = self.config.get("voice", {}).get("stt", {})
            if stt_config.get("engine") == "whisper":
                self.stt_engine = WhisperSTTEngine(stt_config.get("config", {}))
                self.logger.info(f"✓ STT engine ready: {self.stt_engine.get_name()}")
        except Exception as e:
            self.logger.warning(f"⚠ STT unavailable: {e}")
        
        # Initialize TTS
        try:
            tts_config = self.config.get("voice", {}).get("tts", {})
            if tts_config.get("engine") == "piper":
                self.tts_engine = PiperTTSEngine(tts_config.get("config", {}))
                self.logger.info(f"✓ TTS engine ready: {self.tts_engine.get_name()}")
        except Exception as e:
            self.logger.warning(f"⚠ TTS unavailable: {e}")
        
        self.logger.info("Component initialization complete")
    
    def process_voice_interaction(
        self,
        audio_path: str,
        child_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a complete voice interaction:
        Audio → STT → LLM → TTS → Audio
        
        Args:
            audio_path: Path to input audio file
            child_profile: Optional child profile for personalization
        
        Returns:
            Dictionary with results
        """
        self.logger.info("Processing voice interaction...")
        
        result = {
            "status": "processing",
            "steps": {}
        }
        
        try:
            if not self.stt_engine:
                raise RuntimeError("Speech-to-text is not available; install and configure Whisper")

            # Step 1: Speech-to-Text
            self.logger.info("Step 1: Converting speech to text...")
            stt_result = self.stt_engine.transcribe(audio_path)
            result["steps"]["stt"] = {
                "text": stt_result.text,
                "confidence": stt_result.confidence,
            }

            if child_profile:
                self.update_child_profile(child_profile)

            # Step 2: Generate LLM response through the shared brain
            self.logger.info("Step 2: Generating AI response...")
            response_text = self.ask(stt_result.text)
            result["steps"]["llm"] = {"response": response_text}
            
            # Step 3: Text-to-Speech
            self.logger.info("Step 3: Converting response to speech...")
            if not self.tts_engine:
                raise RuntimeError("Text-to-speech is not available; install and configure Piper")
            output_audio_path = Path("./data/response.wav")
            tts_result = self.tts_engine.synthesize(response_text, str(output_audio_path))
            result["steps"]["tts"] = {
                "audio_path": tts_result.audio_path,
                "duration_ms": tts_result.duration_ms,
            }
            
            result["status"] = "success"
        
        except Exception as e:
            self.logger.error(f"Voice interaction failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result

    def ask(self, user_message: str) -> str:
        """Generate a personalized response using conversation and saved memory."""
        if not user_message.strip():
            raise ValueError("user_message must not be empty")
        if not self.llm_provider or not self.personality_engine or not self.short_term_memory:
            raise RuntimeError("Teddy service is not fully initialized")

        self._remember_preferences(user_message)
        memories = (
            self.memory_backend.retrieve(limit=5)
            if self.memory_backend
            else []
        )
        memories = [memory for memory in memories if memory.category != "conversation"]
        memory_texts = [memory.content for memory in memories]
        child_profile = self.config.get("child", {})
        system_prompt = self.personality_engine.construct_system_prompt(
            child_profile=child_profile,
            memories=memory_texts,
            language=child_profile.get("language", "en"),
        )
        conversation = self.short_term_memory.get_context()
        prompt_parts = [system_prompt]
        if conversation:
            prompt_parts.extend(["Conversation so far:", conversation])
        prompt_parts.extend([
            f"{child_profile.get('name', 'Neo')}: {user_message.strip()}",
            f"{self.personality_engine.personality.name}:",
        ])

        response = self.llm_provider.generate("\n".join(prompt_parts))
        child_name = child_profile.get("name", "Neo")
        companion_name = self.personality_engine.personality.name
        self._record_turn(child_name, user_message.strip())
        self._record_turn(companion_name, response.text)
        return response.text

    def _restore_conversation(self):
        """Restore the latest persisted conversation turns into short-term memory."""
        if not self.memory_backend or not self.short_term_memory:
            return
        turns = self.memory_backend.retrieve(
            category="conversation",
            limit=self.short_term_memory.max_turns * 2,
        )
        for turn in reversed(turns):
            role = (turn.metadata or {}).get("role", "conversation")
            self.short_term_memory.add(role, turn.content)

    def _record_turn(self, role: str, message: str):
        """Add a turn to in-session and persistent conversation memory."""
        self.short_term_memory.add(role, message)
        if self.memory_backend:
            self.memory_backend.store(
                "conversation",
                message,
                {"role": role},
            )

    def _remember_preferences(self, user_message: str):
        """Persist simple preference statements before generating a response."""
        if not self.memory_backend:
            return

        patterns = [
            (r"(?:i like|i love|my favorite animal is)\s+([^.!?]+)", "favorite_animals"),
            (r"(?:my favorite color is)\s+([^.!?]+)", "favorite_colors"),
        ]
        for pattern, category in patterns:
            match = re.search(pattern, user_message, flags=re.IGNORECASE)
            if not match:
                continue

            preference = match.group(1).strip()
            content = f"{self.config.get('child', {}).get('name', 'Neo')} likes {preference}"
            existing = self.memory_backend.retrieve(category=category, limit=100)
            if not any(memory.content.casefold() == content.casefold() for memory in existing):
                self.store_memory(category, content, {"source": "conversation"})
    
    def update_child_profile(self, profile: Dict[str, Any]):
        """Update child profile for personalization."""
        self.config["child"].update(profile)
        self.logger.info(f"Child profile updated: {profile}")
    
    def store_memory(self, category: str, content: str, metadata: Optional[Dict] = None):
        """Store a memory about the child."""
        if not self.memory_backend:
            raise RuntimeError("Memory backend is not initialized")
        memory_id = self.memory_backend.store(category, content, metadata)
        self.logger.info(f"Memory stored: {memory_id}")
        return memory_id
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "service": "TeddyAI",
            "status": "running",
            "components": {
                "memory": self.memory_backend is not None,
                "personality": self.personality_engine is not None,
                "llm": self.llm_provider is not None and self.llm_provider.is_available(),
                "stt": self.stt_engine is not None and self.stt_engine.is_available(),
                "tts": self.tts_engine is not None and self.tts_engine.is_available(),
            }
        }


# Example usage
if __name__ == "__main__":
    import yaml
    
    # Load config
    with open("config/teddy.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize service
    teddy = TeddyAIService(config)
    
    # Check status
    print(teddy.get_status())
