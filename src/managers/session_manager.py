"""Session Manager for conversation lifecycle."""

from typing import Optional
from datetime import datetime
from enum import Enum
import uuid

from src.models.data_models import Session, Exchange, SessionMetadata, Mood
from src.managers.context_manager import ContextManager
from src.engines.speech_recognition_engine import SpeechRecognitionEngine
from src.engines.ai_model_wrapper import AIModelWrapper, ConversationContext
from src.engines.text_to_speech_engine import TextToSpeechEngine
from src.analysis.mood_analysis import MoodAnalysisEngine
from src.utils.logger import Logger


class SessionState(Enum):
    """Session states."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    PAUSED = "paused"
    ENDED = "ended"


class SessionManager:
    """Manages conversation lifecycle and coordinates components."""

    def __init__(self, context_manager: ContextManager):
        """Initialize session manager.
        
        Args:
            context_manager: ContextManager instance
        """
        self.context_manager = context_manager
        self.logger = Logger("SessionManager")
        
        # Components
        self.speech_engine: Optional[SpeechRecognitionEngine] = None
        self.ai_model: Optional[AIModelWrapper] = None
        self.tts_engine: Optional[TextToSpeechEngine] = None
        self.mood_engine: Optional[MoodAnalysisEngine] = None
        
        # Session state
        self.current_session: Optional[Session] = None
        self.current_state = SessionState.IDLE
        self.exchange_count = 0

    def initialize_components(self, speech_engine: SpeechRecognitionEngine,
                            ai_model: AIModelWrapper,
                            tts_engine: TextToSpeechEngine,
                            mood_engine: MoodAnalysisEngine) -> None:
        """Initialize processing components.
        
        Args:
            speech_engine: Speech recognition engine
            ai_model: AI model wrapper
            tts_engine: Text-to-speech engine
            mood_engine: Mood analysis engine
        """
        self.speech_engine = speech_engine
        self.ai_model = ai_model
        self.tts_engine = tts_engine
        self.mood_engine = mood_engine
        self.logger.info("Components initialized")

    def start_session(self, user_id: str) -> Optional[Session]:
        """Start new conversation session.
        
        Args:
            user_id: User ID
            
        Returns:
            New Session object or None on error
        """
        try:
            session_id = str(uuid.uuid4())
            self.current_session = self.context_manager.start_session(user_id, session_id)
            self.current_state = SessionState.IDLE
            self.exchange_count = 0

            self.logger.info(f"Started session {session_id} for user {user_id}")
            return self.current_session

        except Exception as e:
            self.logger.error(f"Failed to start session: {e}")
            return None

    def end_session(self) -> Optional[Session]:
        """End current session.
        
        Returns:
            Completed Session object or None
        """
        try:
            if not self.current_session:
                return None

            # Create metadata
            duration = (datetime.now() - self.current_session.created_at).total_seconds()
            metadata = SessionMetadata(
                duration_seconds=int(duration),
                exchange_count=self.exchange_count,
                completion_status="completed"
            )
            self.current_session.metadata = metadata

            # End session in context manager
            session = self.context_manager.end_session()
            self.current_state = SessionState.ENDED

            self.logger.info(f"Ended session {self.current_session.session_id}")
            return session

        except Exception as e:
            self.logger.error(f"Failed to end session: {e}")
            return None

    def pause_session(self) -> bool:
        """Pause current session.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.current_state == SessionState.IDLE:
                self.current_state = SessionState.PAUSED
                self.logger.info("Session paused")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Failed to pause session: {e}")
            return False

    def resume_session(self) -> bool:
        """Resume paused session.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.current_state == SessionState.PAUSED:
                self.current_state = SessionState.IDLE
                self.logger.info("Session resumed")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Failed to resume session: {e}")
            return False

    def process_user_input(self, audio_data: bytes) -> Optional[str]:
        """Process user input through full pipeline.
        
        Args:
            audio_data: Audio data from user
            
        Returns:
            AI response text or None on error
        """
        try:
            if not self.current_session or not all([
                self.speech_engine, self.ai_model, self.tts_engine, self.mood_engine
            ]):
                return None

            # 1. Speech Recognition
            self.current_state = SessionState.LISTENING
            transcription = self.speech_engine.transcribe(audio_data)

            if transcription.error or not transcription.text:
                self.logger.warning(f"Speech recognition failed: {transcription.error}")
                return None

            user_message = transcription.text
            self.logger.info(f"Transcribed: {user_message}")

            # 2. Mood Analysis
            mood = self.mood_engine.analyze_mood(audio_data)

            # 3. AI Response Generation
            self.current_state = SessionState.PROCESSING
            context = ConversationContext()
            context.exchanges = self.context_manager.get_recent_exchanges()
            context.user_profile = self.context_manager.get_user_profile()
            context.mood_state = mood.classification if mood else "neutral"

            ai_response = self.ai_model.generate_response(context, user_message)

            # 4. Create exchange
            exchange = Exchange(
                timestamp=datetime.now(),
                user_message=user_message,
                ai_response=ai_response,
                mood_detected=mood
            )
            self.context_manager.add_exchange(exchange)
            self.current_session.exchanges.append(exchange)
            self.exchange_count += 1

            # 5. Text-to-Speech
            self.current_state = SessionState.SPEAKING
            audio_output = self.tts_engine.synthesize(ai_response)
            if audio_output:
                self.tts_engine.play_audio(audio_output)

            self.current_state = SessionState.IDLE
            self.logger.info(f"Processed exchange {self.exchange_count}")
            return ai_response

        except Exception as e:
            self.logger.error(f"Failed to process user input: {e}")
            self.current_state = SessionState.IDLE
            return None

    def get_session_state(self) -> dict:
        """Get current session state.
        
        Returns:
            Dictionary with session state information
        """
        return {
            "session_id": self.current_session.session_id if self.current_session else None,
            "user_id": self.current_session.user_id if self.current_session else None,
            "state": self.current_state.value,
            "exchange_count": self.exchange_count,
            "created_at": self.current_session.created_at.isoformat() if self.current_session else None,
        }

    def replay_session(self, session_id: str) -> bool:
        """Replay a previous session.
        
        Args:
            session_id: ID of session to replay
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.context_manager.persistence_layer:
                return False

            session = self.context_manager.persistence_layer.load_conversation(session_id)
            if not session:
                return False

            self.logger.info(f"Replaying session {session_id}")
            # In production, would replay audio and display transcript
            return True

        except Exception as e:
            self.logger.error(f"Failed to replay session: {e}")
            return False

    def get_model_info(self) -> dict:
        """Get information about session manager.
        
        Returns:
            Dictionary with manager information
        """
        return {
            "current_state": self.current_state.value,
            "exchange_count": self.exchange_count,
            "has_session": self.current_session is not None,
            "components_initialized": all([
                self.speech_engine, self.ai_model, self.tts_engine, self.mood_engine
            ])
        }
