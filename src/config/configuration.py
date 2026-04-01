"""Configuration dataclass and schema for Vask."""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class Configuration:
    """Configuration dataclass with all required fields for Vask."""

    # System settings
    version: str = "1.0.0"
    offline_mode: bool = True

    # Audio settings
    language: str = "en"
    voice_id: str = "en_US-hfc_female-medium"
    speaking_rate: float = 1.0  # 0.5-2.0
    listening_sensitivity: float = 0.8  # 0.0-1.0

    # Feature settings
    enable_camera: bool = True
    enable_audio_output: bool = True
    enable_learning: bool = True

    # Performance settings
    max_context_exchanges: int = 10
    response_timeout_seconds: int = 2

    # Privacy settings
    encryption_enabled: bool = True
    auto_delete_after_days: Optional[int] = None

    # Model paths
    whisper_model_path: str = "models/whisper-base"
    llama_model_path: str = "models/llama-2-7b-q4"
    piper_model_path: str = "models/piper-voices"

    # Mood sensitivity
    mood_sensitivity: float = 0.8  # 0.0-1.0

    # Response tone
    response_tone: str = "empathetic"  # empathetic, technical, casual, formal

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Configuration":
        """Create configuration from dictionary."""
        return cls(**data)
