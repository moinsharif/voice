"""Speech Recognition Engine using Whisper."""

import whisper
import numpy as np
from typing import Optional
from src.models.data_models import TranscriptionResult
from src.utils.logger import Logger
from src.utils.fallback_responses import FallbackResponses


class SpeechRecognitionEngine:
    """Converts audio input to text using Whisper."""

    def __init__(self, model_size: str = "base", language: str = "en"):
        """Initialize speech recognition engine.
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            language: Language code (e.g., "en", "es", "fr")
        """
        self.model_size = model_size
        self.language = language
        self.logger = Logger("SpeechRecognitionEngine")
        self.model = None
        self.is_listening = False
        self._load_model()

    def _load_model(self) -> None:
        """Load Whisper model."""
        try:
            self.logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            self.logger.info("Whisper model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            raise

    def start_listening(self) -> None:
        """Start listening for audio input."""
        self.is_listening = True
        self.logger.info("Started listening")

    def stop_listening(self) -> None:
        """Stop listening for audio input."""
        self.is_listening = False
        self.logger.info("Stopped listening")

    def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """Transcribe audio to text.
        
        Args:
            audio_data: Audio data in bytes
            
        Returns:
            TranscriptionResult with transcription and metadata
        """
        try:
            if not self.model:
                return TranscriptionResult(
                    text="",
                    confidence=0.0,
                    language=self.language,
                    duration_seconds=0.0,
                    error="Model not loaded"
                )

            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)

            # Transcribe
            result = self.model.transcribe(
                audio_array,
                language=self.language,
                fp16=False
            )

            text = result.get("text", "").strip()
            confidence = result.get("confidence", 0.0)
            detected_language = result.get("language", self.language)

            if not text:
                error_msg = FallbackResponses.get_response("speech_recognition_failed")
                return TranscriptionResult(
                    text="",
                    confidence=0.0,
                    language=detected_language,
                    duration_seconds=len(audio_data) / 16000,  # Approximate
                    error=error_msg
                )

            self.logger.info(f"Transcribed: {text[:100]}...")
            return TranscriptionResult(
                text=text,
                confidence=confidence,
                language=detected_language,
                duration_seconds=len(audio_data) / 16000
            )

        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            error_msg = FallbackResponses.get_response("speech_recognition_failed")
            return TranscriptionResult(
                text="",
                confidence=0.0,
                language=self.language,
                duration_seconds=0.0,
                error=error_msg
            )

    def set_language(self, language_code: str) -> None:
        """Set language for recognition.
        
        Args:
            language_code: Language code (e.g., "en", "es", "fr")
        """
        self.language = language_code
        self.logger.info(f"Language set to {language_code}")

    def apply_noise_filter(self, audio_data: bytes) -> bytes:
        """Apply noise filtering to audio.
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            Filtered audio data
        """
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)

            # Simple spectral subtraction for noise reduction
            # Calculate noise profile from first 0.5 seconds
            sample_rate = 16000
            noise_duration = int(0.5 * sample_rate)
            noise_profile = np.mean(np.abs(audio_array[:noise_duration]))

            # Apply noise gate
            threshold = noise_profile * 1.5
            filtered = np.where(np.abs(audio_array) > threshold, audio_array, 0)

            # Convert back to bytes
            return filtered.astype(np.float32).tobytes()

        except Exception as e:
            self.logger.warning(f"Noise filtering failed: {e}")
            return audio_data

    def get_model_info(self) -> dict:
        """Get information about loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_size": self.model_size,
            "language": self.language,
            "is_loaded": self.model is not None,
            "is_listening": self.is_listening
        }
