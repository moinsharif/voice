"""
Vask - Voice-Based AI Companion
Main application entry point
"""

import sys
import logging
from typing import Optional
from pathlib import Path

from src.config.config_system import ConfigurationSystem
from src.persistence.persistence_layer import PersistenceLayer
from src.managers.context_manager import ContextManager
from src.managers.session_manager import SessionManager
from src.managers.learning_system import LearningSystem
from src.engines.speech_recognition_engine import SpeechRecognitionEngine
from src.engines.ai_model_wrapper import AIModelWrapper
from src.engines.text_to_speech_engine import TextToSpeechEngine
from src.analysis.face_detection import FaceDetectionModule
from src.analysis.mood_analysis import MoodAnalysisEngine
from src.utils.logger import Logger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VaskApplication:
    """Main Vask application class orchestrating all components."""

    def __init__(self, config_path: str = None, encryption_key: Optional[str] = None):
        """Initialize Vask application.
        
        Args:
            config_path: Path to configuration file
            encryption_key: Encryption key for data
        """
        self.config_path = config_path or "config/default_config.yaml"
        self.logger = Logger("VaskApplication")
        self.config_system = ConfigurationSystem()
        self.config = None
        
        # Initialize components
        self.persistence_layer: Optional[PersistenceLayer] = None
        self.context_manager: Optional[ContextManager] = None
        self.session_manager: Optional[SessionManager] = None
        self.learning_system: Optional[LearningSystem] = None
        
        self.speech_engine: Optional[SpeechRecognitionEngine] = None
        self.ai_model: Optional[AIModelWrapper] = None
        self.tts_engine: Optional[TextToSpeechEngine] = None
        self.face_detector: Optional[FaceDetectionModule] = None
        self.mood_engine: Optional[MoodAnalysisEngine] = None
        
        self.is_running = False
        self.encryption_key = encryption_key
        
        self._load_configuration()
        self._initialize_components()

    def _load_configuration(self) -> None:
        """Load configuration from file."""
        try:
            self.config = self.config_system.parse_config_file(self.config_path)
            self.logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise

    def _initialize_components(self) -> None:
        """Initialize all application components."""
        try:
            # Persistence layer
            self.persistence_layer = PersistenceLayer(
                db_path="vask_data.db",
                encryption_key=self.encryption_key
            )
            self.logger.info("Persistence layer initialized")

            # Context manager
            self.context_manager = ContextManager(
                persistence_layer=self.persistence_layer,
                max_context_exchanges=self.config.max_context_exchanges if self.config else 10
            )
            self.logger.info("Context manager initialized")

            # Session manager
            self.session_manager = SessionManager(self.context_manager)
            self.logger.info("Session manager initialized")

            # Learning system
            self.learning_system = LearningSystem()
            self.logger.info("Learning system initialized")

            # Speech recognition engine
            self.speech_engine = SpeechRecognitionEngine(
                model_size="base",
                language=self.config.language if self.config else "en"
            )
            self.logger.info("Speech recognition engine initialized")

            # AI model wrapper
            self.ai_model = AIModelWrapper()
            self.logger.info("AI model wrapper initialized")

            # Text-to-speech engine
            self.tts_engine = TextToSpeechEngine(
                voice_id=self.config.voice_id if self.config else "en_US-lessac-medium",
                enabled=self.config.enable_audio_output if self.config else True
            )
            self.logger.info("Text-to-speech engine initialized")

            # Face detection module
            self.face_detector = FaceDetectionModule(
                enable_camera=self.config.enable_camera if self.config else True
            )
            self.logger.info("Face detection module initialized")

            # Mood analysis engine
            self.mood_engine = MoodAnalysisEngine()
            self.logger.info("Mood analysis engine initialized")

            # Wire components to session manager
            self.session_manager.initialize_components(
                self.speech_engine,
                self.ai_model,
                self.tts_engine,
                self.mood_engine
            )
            self.logger.info("All components initialized and wired")

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise

    def start(self) -> None:
        """Start the application."""
        try:
            self.is_running = True
            self.logger.info("Vask application started")
            print("Vask application started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start application: {e}")
            raise

    def stop(self) -> None:
        """Stop the application gracefully."""
        try:
            self.is_running = False
            
            # Clean up resources
            if self.face_detector:
                self.face_detector.stop_camera()
            
            if self.speech_engine:
                self.speech_engine.stop_listening()
            
            self.logger.info("Vask application stopped")
            print("Vask application stopped")
        except Exception as e:
            self.logger.error(f"Failed to stop application: {e}")

    def process_voice_input(self, audio_data: bytes) -> Optional[str]:
        """Process voice input through full pipeline.
        
        Args:
            audio_data: Audio data in bytes
            
        Returns:
            Response text or None on error
        """
        try:
            if not self.is_running or not self.session_manager:
                return None

            return self.session_manager.process_user_input(audio_data)

        except Exception as e:
            self.logger.error(f"Failed to process voice input: {e}")
            return None

    def start_session(self, user_id: str) -> bool:
        """Start a new conversation session.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.session_manager:
                return False

            session = self.session_manager.start_session(user_id)
            return session is not None

        except Exception as e:
            self.logger.error(f"Failed to start session: {e}")
            return False

    def end_session(self) -> bool:
        """End current session.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.session_manager:
                return False

            session = self.session_manager.end_session()
            return session is not None

        except Exception as e:
            self.logger.error(f"Failed to end session: {e}")
            return False

    def get_user_profile(self, user_id: str):
        """Get user profile.
        
        Args:
            user_id: User ID
            
        Returns:
            UserProfile or None
        """
        try:
            if not self.context_manager:
                return None

            return self.context_manager.load_user_profile(user_id)

        except Exception as e:
            self.logger.error(f"Failed to get user profile: {e}")
            return None

    def get_mood_report(self, user_id: str, period: str = "session"):
        """Get mood report for user.
        
        Args:
            user_id: User ID
            period: Time period ("session", "day", "week", "month")
            
        Returns:
            MoodSummary or None
        """
        try:
            if not self.mood_engine:
                return None

            return self.mood_engine.generate_mood_report(user_id, period)

        except Exception as e:
            self.logger.error(f"Failed to get mood report: {e}")
            return None

    def export_conversation_history(self, user_id: str, format: str = "json") -> Optional[str]:
        """Export conversation history.
        
        Args:
            user_id: User ID
            format: Export format ("json" or "csv")
            
        Returns:
            Exported data as string or None on error
        """
        try:
            if not self.persistence_layer:
                return None

            return self.persistence_layer.export_conversations(user_id, format)

        except Exception as e:
            self.logger.error(f"Failed to export conversation history: {e}")
            return None

    def get_application_info(self) -> dict:
        """Get application information.
        
        Returns:
            Dictionary with application info
        """
        return {
            "name": "Vask",
            "version": "1.0.0",
            "is_running": self.is_running,
            "components": {
                "speech_engine": self.speech_engine is not None,
                "ai_model": self.ai_model is not None,
                "tts_engine": self.tts_engine is not None,
                "face_detector": self.face_detector is not None,
                "mood_engine": self.mood_engine is not None,
            }
        }


def main():
    """Main entry point for the application."""
    try:
        app = VaskApplication()
        app.start()
        # Application would run here
        app.stop()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
