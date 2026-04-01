"""Integration tests for component wiring and data flow pipeline."""

import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from src.main import VaskApplication
from src.managers.session_manager import SessionManager, SessionState
from src.managers.context_manager import ContextManager
from src.persistence.persistence_layer import PersistenceLayer
from src.models.data_models import Session, Exchange, Mood, UserProfile, TranscriptionResult
from src.engines.speech_recognition_engine import SpeechRecognitionEngine
from src.engines.ai_model_wrapper import AIModelWrapper, ConversationContext
from src.engines.text_to_speech_engine import TextToSpeechEngine
from src.analysis.mood_analysis import MoodAnalysisEngine
from src.analysis.face_detection import FaceDetectionModule


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def temp_config():
    """Create temporary config file for testing."""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    os.close(fd)
    
    config_content = """version: "1.0.0"
offline_mode: true
language: "en"
voice_id: "en_US-lessac-medium"
speaking_rate: 1.0
listening_sensitivity: 0.8
mood_sensitivity: 0.7
response_tone: "empathetic"
enable_camera: false
enable_audio_output: false
enable_learning: true
max_context_exchanges: 10
response_timeout_seconds: 2
encryption_enabled: true
auto_delete_after_days: null
whisper_model_path: "models/whisper-base"
llama_model_path: "models/llama-2-7b"
piper_model_path: "models/piper"
"""
    
    with open(path, 'w') as f:
        f.write(config_content)
    
    yield path
    if os.path.exists(path):
        os.remove(path)


class TestComponentWiring:
    """Tests for component wiring and initialization."""

    def test_vask_application_initialization(self, temp_config, temp_db):
        """Test VaskApplication initializes all components."""
        with patch('src.main.PersistenceLayer') as mock_persistence:
            with patch('src.verification.offline_operation_verifier.os.path.exists', return_value=True):
                mock_persistence.return_value = PersistenceLayer(db_path=temp_db)
                
                app = VaskApplication(config_path=temp_config)
                
                # Verify all components are initialized
                assert app.persistence_layer is not None
                assert app.context_manager is not None
                assert app.session_manager is not None
                assert app.learning_system is not None
                assert app.speech_engine is not None
                assert app.ai_model is not None
                assert app.tts_engine is not None
                assert app.face_detector is not None
                assert app.mood_engine is not None

    def test_session_manager_wiring(self, temp_db):
        """Test SessionManager is properly wired with all processing components."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        # Create mock engines
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Wire components
        session_manager.initialize_components(
            speech_engine=speech_engine,
            ai_model=ai_model,
            tts_engine=tts_engine,
            mood_engine=mood_engine
        )
        
        # Verify wiring
        assert session_manager.speech_engine is speech_engine
        assert session_manager.ai_model is ai_model
        assert session_manager.tts_engine is tts_engine
        assert session_manager.mood_engine is mood_engine

    def test_component_wiring_verification(self, temp_config, temp_db):
        """Test component wiring verification catches missing components."""
        with patch('src.main.PersistenceLayer') as mock_persistence:
            with patch('src.verification.offline_operation_verifier.os.path.exists', return_value=True):
                mock_persistence.return_value = PersistenceLayer(db_path=temp_db)
                
                app = VaskApplication(config_path=temp_config)
                
                # Verify wiring verification passed
                # If it didn't, an exception would have been raised during init
                assert app.session_manager.speech_engine is not None
                assert app.session_manager.ai_model is not None
                assert app.session_manager.tts_engine is not None
                assert app.session_manager.mood_engine is not None

    def test_context_manager_wiring(self, temp_db):
        """Test ContextManager is properly wired with persistence layer."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        
        assert context.persistence_layer is persistence
        assert context.max_context_exchanges == 10

    def test_learning_system_wiring(self, temp_db):
        """Test LearningSystem is wired with ContextManager."""
        from src.managers.learning_system import LearningSystem
        
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        learning_system = LearningSystem()
        
        learning_system.set_context_manager(context)
        
        assert learning_system.context_manager is context


class TestDataFlowPipeline:
    """Tests for complete data flow pipeline."""

    def test_complete_pipeline_flow(self, temp_db):
        """Test complete data flow: input → recognition → context → AI → mood → output."""
        # Setup
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        # Create mock engines
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Hello, how are you?",
            error=None,
            confidence=0.95,
            language="en",
            duration_seconds=2.5
        )
        
        mood = Mock()
        mood.classification = "positive"
        mood_engine.analyze_mood.return_value = mood
        
        ai_model.generate_response.return_value = "I'm doing well, thank you!"
        
        tts_engine.synthesize.return_value = b"audio_data"
        tts_engine.play_audio.return_value = None
        
        # Wire components
        session_manager.initialize_components(
            speech_engine=speech_engine,
            ai_model=ai_model,
            tts_engine=tts_engine,
            mood_engine=mood_engine
        )
        
        # Start session
        session = session_manager.start_session("user-1")
        assert session is not None
        
        # Process input through pipeline
        audio_data = b"mock_audio_data"
        response = session_manager.process_user_input(audio_data)
        
        # Verify pipeline executed
        assert response == "I'm doing well, thank you!"
        assert session_manager.exchange_count == 1
        
        # Verify each stage was called
        speech_engine.transcribe.assert_called_once_with(audio_data)
        mood_engine.analyze_mood.assert_called_once_with(audio_data)
        ai_model.generate_response.assert_called_once()
        tts_engine.synthesize.assert_called_once_with("I'm doing well, thank you!")
        tts_engine.play_audio.assert_called_once()

    def test_pipeline_stage_1_speech_recognition(self, temp_db):
        """Test Stage 1: Speech Recognition in pipeline."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Test message",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        ai_model.generate_response.return_value = "Response"
        tts_engine.synthesize.return_value = b"audio"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        response = session_manager.process_user_input(b"audio")
        
        # Verify speech recognition was called
        assert speech_engine.transcribe.called
        assert response is not None

    def test_pipeline_stage_2_mood_analysis(self, temp_db):
        """Test Stage 2: Mood Analysis in pipeline."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="I'm happy!",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        
        mood = Mock()
        mood.classification = "positive"
        mood_engine.analyze_mood.return_value = mood
        
        ai_model.generate_response.return_value = "That's great!"
        tts_engine.synthesize.return_value = b"audio"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        response = session_manager.process_user_input(b"audio")
        
        # Verify mood analysis was called
        assert mood_engine.analyze_mood.called
        
        # Verify mood was passed to AI model
        call_args = ai_model.generate_response.call_args
        context_arg = call_args[0][0]
        assert context_arg.mood_state == "positive"

    def test_pipeline_stage_3_context_preparation(self, temp_db):
        """Test Stage 3: Context Preparation in pipeline."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Hello",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        ai_model.generate_response.return_value = "Hi there!"
        tts_engine.synthesize.return_value = b"audio"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        # Load user profile
        context.load_user_profile("user-1")
        
        session_manager.start_session("user-1")
        response = session_manager.process_user_input(b"audio")
        
        # Verify context was prepared
        call_args = ai_model.generate_response.call_args
        context_arg = call_args[0][0]
        assert context_arg.user_profile is not None
        assert context_arg.exchanges is not None

    def test_pipeline_stage_4_ai_response_generation(self, temp_db):
        """Test Stage 4: AI Response Generation in pipeline."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="What's the weather?",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        ai_model.generate_response.return_value = "I don't have weather data."
        tts_engine.synthesize.return_value = b"audio"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        response = session_manager.process_user_input(b"audio")
        
        # Verify AI response was generated
        assert ai_model.generate_response.called
        assert response == "I don't have weather data."

    def test_pipeline_stage_5_context_update(self, temp_db):
        """Test Stage 5: Context Update in pipeline."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Hello",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        ai_model.generate_response.return_value = "Hi!"
        tts_engine.synthesize.return_value = b"audio"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        
        # Verify context is empty before
        assert len(context.current_exchanges) == 0
        
        response = session_manager.process_user_input(b"audio")
        
        # Verify context was updated
        assert len(context.current_exchanges) == 1
        assert context.current_exchanges[0].user_message == "Hello"
        assert context.current_exchanges[0].ai_response == "Hi!"

    def test_pipeline_stage_6_text_to_speech(self, temp_db):
        """Test Stage 6: Text-to-Speech in pipeline."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Say hello",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        ai_model.generate_response.return_value = "Hello!"
        tts_engine.synthesize.return_value = b"audio_data"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        response = session_manager.process_user_input(b"audio")
        
        # Verify TTS was called
        assert tts_engine.synthesize.called
        assert tts_engine.play_audio.called
        tts_engine.synthesize.assert_called_with("Hello!")


class TestErrorHandlingAndRecovery:
    """Tests for error handling and recovery in pipeline."""

    def test_speech_recognition_failure_recovery(self, temp_db):
        """Test pipeline recovers from speech recognition failure."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure speech recognition to fail
        speech_engine.transcribe.return_value = TranscriptionResult(
            text=None,
            error="Audio too quiet",
            confidence=0.0,
            language="en",
            duration_seconds=2.0
        )
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        response = session_manager.process_user_input(b"audio")
        
        # Verify pipeline returned None and didn't crash
        assert response is None
        assert session_manager.current_state == SessionState.IDLE

    def test_mood_analysis_failure_recovery(self, temp_db):
        """Test pipeline recovers from mood analysis failure."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Hello",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        
        # Mood analysis fails
        mood_engine.analyze_mood.side_effect = Exception("Mood analysis error")
        
        ai_model.generate_response.return_value = "Hi!"
        tts_engine.synthesize.return_value = b"audio"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        response = session_manager.process_user_input(b"audio")
        
        # Verify pipeline continued with neutral mood
        assert response == "Hi!"
        call_args = ai_model.generate_response.call_args
        context_arg = call_args[0][0]
        assert context_arg.mood_state == "neutral"

    def test_ai_model_failure_recovery(self, temp_db):
        """Test pipeline recovers from AI model failure."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Hello",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        
        # AI model fails
        ai_model.generate_response.side_effect = Exception("Model error")
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        response = session_manager.process_user_input(b"audio")
        
        # Verify pipeline returned None and didn't crash
        assert response is None
        assert session_manager.current_state == SessionState.IDLE

    def test_tts_failure_recovery(self, temp_db):
        """Test pipeline recovers from TTS failure."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Hello",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        ai_model.generate_response.return_value = "Hi!"
        
        # TTS fails
        tts_engine.synthesize.side_effect = Exception("TTS error")
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        response = session_manager.process_user_input(b"audio")
        
        # Verify pipeline continued despite TTS failure
        assert response == "Hi!"
        assert session_manager.current_state == SessionState.IDLE

    def test_missing_components_error(self, temp_db):
        """Test error when components are not initialized."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        # Don't initialize components
        session_manager.start_session("user-1")
        response = session_manager.process_user_input(b"audio")
        
        # Verify error handling
        assert response is None

    def test_no_active_session_error(self, temp_db):
        """Test error when no active session."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        # Try to process without starting session
        response = session_manager.process_user_input(b"audio")
        
        # Verify error handling
        assert response is None


class TestComponentCommunication:
    """Tests for component communication and event handling."""

    def test_session_manager_coordinates_components(self, temp_db):
        """Test SessionManager properly coordinates all components."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Test",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        ai_model.generate_response.return_value = "Response"
        tts_engine.synthesize.return_value = b"audio"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        session_manager.process_user_input(b"audio")
        
        # Verify all components were called in correct order
        assert speech_engine.transcribe.call_count == 1
        assert mood_engine.analyze_mood.call_count == 1
        assert ai_model.generate_response.call_count == 1
        assert tts_engine.synthesize.call_count == 1

    def test_context_manager_receives_exchanges(self, temp_db):
        """Test ContextManager receives exchanges from SessionManager."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Hello",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        ai_model.generate_response.return_value = "Hi!"
        tts_engine.synthesize.return_value = b"audio"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        session_manager.process_user_input(b"audio")
        
        # Verify context received exchange
        assert len(context.current_exchanges) == 1
        exchange = context.current_exchanges[0]
        assert exchange.user_message == "Hello"
        assert exchange.ai_response == "Hi!"

    def test_session_state_transitions(self, temp_db):
        """Test proper session state transitions during pipeline."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Test",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        ai_model.generate_response.return_value = "Response"
        tts_engine.synthesize.return_value = b"audio"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        # Start session
        session_manager.start_session("user-1")
        assert session_manager.current_state == SessionState.IDLE
        
        # Process input - state should transition through pipeline
        session_manager.process_user_input(b"audio")
        
        # After processing, should return to IDLE
        assert session_manager.current_state == SessionState.IDLE

    def test_multiple_exchanges_in_session(self, temp_db):
        """Test multiple exchanges are properly handled in a session."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        session_manager = SessionManager(context)
        
        speech_engine = Mock(spec=SpeechRecognitionEngine)
        ai_model = Mock(spec=AIModelWrapper)
        tts_engine = Mock(spec=TextToSpeechEngine)
        mood_engine = Mock(spec=MoodAnalysisEngine)
        
        # Configure mocks
        speech_engine.transcribe.return_value = TranscriptionResult(
            text="Hello",
            error=None,
            confidence=0.9,
            language="en",
            duration_seconds=2.0
        )
        mood_engine.analyze_mood.return_value = Mock(classification="neutral")
        ai_model.generate_response.return_value = "Hi!"
        tts_engine.synthesize.return_value = b"audio"
        
        session_manager.initialize_components(
            speech_engine, ai_model, tts_engine, mood_engine
        )
        
        session_manager.start_session("user-1")
        
        # Process multiple exchanges
        for i in range(3):
            response = session_manager.process_user_input(b"audio")
            assert response == "Hi!"
            assert session_manager.exchange_count == i + 1
        
        # Verify all exchanges are in context
        assert len(context.current_exchanges) == 3
        assert len(session_manager.current_session.exchanges) == 3
