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
from src.utils.performance_optimizer import PerformanceOptimizer
from src.verification.offline_operation_verifier import OfflineOperationVerifier

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
        self.offline_verifier: Optional[OfflineOperationVerifier] = None
        self.performance_optimizer: Optional[PerformanceOptimizer] = None
        
        self._load_configuration()
        self._verify_offline_operation()
        self._initialize_performance_optimizer()
        self._initialize_components()

    def _load_configuration(self) -> None:
        """Load configuration from file."""
        try:
            self.config = self.config_system.parse_config_file(self.config_path)
            self.logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise

    def _initialize_performance_optimizer(self) -> None:
        """Initialize performance optimization."""
        try:
            self.performance_optimizer = PerformanceOptimizer(db_path="vask_data.db")
            if self.performance_optimizer.initialize():
                self.logger.info("Performance optimizer initialized")
                
                # Register models for lazy loading
                self.performance_optimizer.register_model("whisper", "models/whisper-base.pt")
                self.performance_optimizer.register_model("llama", "models/llama-2-7b.gguf")
                self.performance_optimizer.register_model("piper", "models/piper-en_US.onnx")
            else:
                self.logger.warning("Failed to initialize performance optimizer")
        except Exception as e:
            self.logger.error(f"Failed to initialize performance optimizer: {e}")

    def _initialize_components(self) -> None:
        """Initialize all application components."""
        try:
            # 1. Persistence layer - foundation for all data storage
            self.persistence_layer = PersistenceLayer(
                db_path="vask_data.db",
                encryption_key=self.encryption_key
            )
            self.logger.info("Persistence layer initialized")

            # 2. Context manager - manages conversation state and user profiles
            self.context_manager = ContextManager(
                persistence_layer=self.persistence_layer,
                max_context_exchanges=self.config.max_context_exchanges if self.config else 10
            )
            self.logger.info("Context manager initialized")

            # 3. Session manager - orchestrates all components
            self.session_manager = SessionManager(self.context_manager)
            self.logger.info("Session manager initialized")

            # 4. Learning system - analyzes interactions and improves responses
            self.learning_system = LearningSystem()
            self.logger.info("Learning system initialized")

            # 5. Speech recognition engine - converts audio to text
            self.speech_engine = SpeechRecognitionEngine(
                model_size="base",
                language=self.config.language if self.config else "en"
            )
            self.logger.info("Speech recognition engine initialized")

            # 6. AI model wrapper - generates contextual responses
            self.ai_model = AIModelWrapper()
            self.logger.info("AI model wrapper initialized")

            # 7. Text-to-speech engine - converts responses to audio
            self.tts_engine = TextToSpeechEngine(
                voice_id=self.config.voice_id if self.config else "en_US-lessac-medium",
                enabled=self.config.enable_audio_output if self.config else True
            )
            self.logger.info("Text-to-speech engine initialized")

            # 8. Face detection module - detects and analyzes faces
            self.face_detector = FaceDetectionModule(
                enable_camera=self.config.enable_camera if self.config else True
            )
            self.logger.info("Face detection module initialized")

            # 9. Mood analysis engine - analyzes emotional state
            self.mood_engine = MoodAnalysisEngine()
            self.logger.info("Mood analysis engine initialized")

            # 10. Wire all processing components to session manager
            # This establishes the data flow pipeline
            self.session_manager.initialize_components(
                speech_engine=self.speech_engine,
                ai_model=self.ai_model,
                tts_engine=self.tts_engine,
                mood_engine=self.mood_engine
            )
            
            # 11. Wire context manager with learning system
            self.learning_system.set_context_manager(self.context_manager)
            
            self.logger.info("All components initialized and wired successfully")
            self._verify_component_wiring()

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise

    def _verify_component_wiring(self) -> None:
        """Verify all components are properly wired.
        
        Raises:
            RuntimeError: If any component is not properly initialized
        """
        required_components = {
            "persistence_layer": self.persistence_layer,
            "context_manager": self.context_manager,
            "session_manager": self.session_manager,
            "learning_system": self.learning_system,
            "speech_engine": self.speech_engine,
            "ai_model": self.ai_model,
            "tts_engine": self.tts_engine,
            "face_detector": self.face_detector,
            "mood_engine": self.mood_engine,
        }
        
        missing_components = [name for name, component in required_components.items() if component is None]
        
        if missing_components:
            raise RuntimeError(f"Missing components: {', '.join(missing_components)}")
        
        # Verify session manager has all processing components
        if not self.session_manager.speech_engine:
            raise RuntimeError("Session manager not wired with speech engine")
        if not self.session_manager.ai_model:
            raise RuntimeError("Session manager not wired with AI model")
        if not self.session_manager.tts_engine:
            raise RuntimeError("Session manager not wired with TTS engine")
        if not self.session_manager.mood_engine:
            raise RuntimeError("Session manager not wired with mood engine")
        
        self.logger.info("Component wiring verification passed")

    def _verify_offline_operation(self) -> None:
        """Verify offline operation requirements.
        
        Checks that all required models are available locally and that
        the system is configured for offline operation.
        
        Raises:
            RuntimeError: If offline operation requirements are not met
        """
        try:
            # Create verifier with current configuration
            config_dict = self.config.to_dict() if self.config else {}
            self.offline_verifier = OfflineOperationVerifier(config=config_dict)
            
            # Run verification
            all_passed, results = self.offline_verifier.verify_offline_operation()
            
            # Log results
            self.logger.info("Offline operation verification started")
            for result in results:
                if result.is_available:
                    self.logger.info(f"✓ {result.component_name} verified")
                else:
                    self.logger.error(f"✗ {result.component_name} not available")
                    if result.error_message:
                        self.logger.error(f"  Error: {result.error_message}")
            
            # If verification failed, raise error with instructions
            if not all_passed:
                error_messages = self.offline_verifier.get_error_messages()
                installation_instructions = self.offline_verifier.get_installation_instructions()
                
                error_report = "Offline operation verification failed:\n"
                error_report += "\n".join(error_messages)
                error_report += "\n\nTo fix these issues, follow the installation instructions:\n"
                error_report += installation_instructions
                
                self.logger.error(error_report)
                raise RuntimeError(error_report)
            
            self.logger.info("Offline operation verification passed")
            
        except Exception as e:
            self.logger.error(f"Offline operation verification failed: {e}")
            raise

    def verify_offline_operation(self) -> bool:
        """Verify offline operation is properly configured.
        
        Returns:
            True if all checks pass, False otherwise
        """
        try:
            if not self.offline_verifier:
                config_dict = self.config.to_dict() if self.config else {}
                self.offline_verifier = OfflineOperationVerifier(config=config_dict)
            
            all_passed, _ = self.offline_verifier.verify_offline_operation()
            return all_passed
        except Exception as e:
            self.logger.error(f"Failed to verify offline operation: {e}")
            return False

    def check_model_availability(self) -> dict:
        """Check availability of all required models.
        
        Returns:
            Dictionary mapping model names to availability status
        """
        try:
            if not self.offline_verifier:
                config_dict = self.config.to_dict() if self.config else {}
                self.offline_verifier = OfflineOperationVerifier(config=config_dict)
            
            return self.offline_verifier.check_model_availability()
        except Exception as e:
            self.logger.error(f"Failed to check model availability: {e}")
            return {}

    def check_no_external_calls(self) -> bool:
        """Verify no external API calls are configured.
        
        Returns:
            True if offline mode is properly configured, False otherwise
        """
        try:
            if not self.config:
                return False
            
            offline_mode = self.config.offline_mode if hasattr(self.config, 'offline_mode') else True
            return offline_mode
        except Exception as e:
            self.logger.error(f"Failed to check external calls configuration: {e}")
            return False

    def get_offline_verification_report(self) -> str:
        """Get detailed offline operation verification report.
        
        Returns:
            Formatted verification report
        """
        try:
            if not self.offline_verifier:
                config_dict = self.config.to_dict() if self.config else {}
                self.offline_verifier = OfflineOperationVerifier(config=config_dict)
                self.offline_verifier.verify_offline_operation()
            
            return self.offline_verifier.generate_verification_report()
        except Exception as e:
            self.logger.error(f"Failed to generate verification report: {e}")
            return f"Error generating report: {e}"

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

    def get_performance_metrics(self) -> dict:
        """Get current performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.performance_optimizer:
            return {}
        
        metrics = self.performance_optimizer.get_performance_metrics()
        if not metrics:
            return {}
        
        return {
            "timestamp": metrics.timestamp.isoformat(),
            "memory_mb": metrics.memory_profile.rss_mb if metrics.memory_profile else 0,
            "memory_percent": metrics.memory_profile.percent if metrics.memory_profile else 0,
            "cpu_percent": metrics.cpu_percent,
            "database_size_mb": metrics.database_size_mb,
            "active_sessions": metrics.active_sessions,
            "cached_responses": metrics.cached_responses,
        }

    def get_performance_report(self) -> dict:
        """Get comprehensive performance report.
        
        Returns:
            Dictionary with performance statistics
        """
        if not self.performance_optimizer:
            return {}
        
        return self.performance_optimizer.get_performance_report()

    def run_maintenance(self) -> bool:
        """Run maintenance tasks.
        
        Returns:
            True if successful
        """
        if not self.performance_optimizer:
            return False
        
        return self.performance_optimizer.run_maintenance()

    def load_model(self, model_name: str):
        """Load a model on demand.
        
        Args:
            model_name: Name of model to load
            
        Returns:
            Loaded model or None
        """
        if not self.performance_optimizer:
            return None
        
        return self.performance_optimizer.load_model(model_name)

    def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory.
        
        Args:
            model_name: Name of model to unload
            
        Returns:
            True if successful
        """
        if not self.performance_optimizer:
            return False
        
        return self.performance_optimizer.unload_model(model_name)


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
