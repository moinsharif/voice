"""Tests for engines."""

import pytest
import numpy as np
from datetime import datetime
from src.engines.speech_recognition_engine import SpeechRecognitionEngine
from src.engines.ai_model_wrapper import AIModelWrapper, ConversationContext
from src.engines.text_to_speech_engine import TextToSpeechEngine
from src.models.data_models import Exchange


class TestSpeechRecognitionEngine:
    """Tests for SpeechRecognitionEngine."""

    def test_initialization(self):
        """Test engine initialization."""
        engine = SpeechRecognitionEngine(model_size="tiny")
        assert engine.model_size == "tiny"
        assert engine.language == "en"

    def test_set_language(self):
        """Test setting language."""
        engine = SpeechRecognitionEngine()
        engine.set_language("es")
        assert engine.language == "es"

    def test_listening_state(self):
        """Test listening state management."""
        engine = SpeechRecognitionEngine()
        assert not engine.is_listening
        
        engine.start_listening()
        assert engine.is_listening
        
        engine.stop_listening()
        assert not engine.is_listening

    def test_noise_filter(self):
        """Test noise filtering."""
        engine = SpeechRecognitionEngine()
        
        # Create dummy audio data
        audio_data = np.random.randn(16000).astype(np.float32).tobytes()
        
        filtered = engine.apply_noise_filter(audio_data)
        assert filtered is not None
        assert len(filtered) > 0


class TestAIModelWrapper:
    """Tests for AIModelWrapper."""

    def test_initialization(self):
        """Test model wrapper initialization."""
        wrapper = AIModelWrapper()
        assert wrapper.response_tone == "friendly"

    def test_set_response_tone(self):
        """Test setting response tone."""
        wrapper = AIModelWrapper()
        
        wrapper.set_response_tone("formal")
        assert wrapper.response_tone == "formal"
        
        wrapper.set_response_tone("empathetic")
        assert wrapper.response_tone == "empathetic"

    def test_generate_response(self):
        """Test response generation."""
        wrapper = AIModelWrapper()
        context = ConversationContext()
        
        response = wrapper.generate_response(context, "Hello")
        assert response is not None
        assert len(response) > 0

    def test_response_caching(self):
        """Test response caching."""
        wrapper = AIModelWrapper()
        context = ConversationContext()
        
        response1 = wrapper.generate_response(context, "Hello")
        response2 = wrapper.generate_response(context, "Hello")
        
        # Should return same response from cache
        assert response1 == response2

    def test_conversation_context(self):
        """Test conversation context management."""
        context = ConversationContext(max_exchanges=5)
        
        for i in range(10):
            exchange = Exchange(
                timestamp=datetime.now(),
                user_message=f"Message {i}",
                ai_response=f"Response {i}"
            )
            context.add_exchange(exchange)
        
        # Should only keep last 5
        assert len(context.exchanges) == 5


class TestTextToSpeechEngine:
    """Tests for TextToSpeechEngine."""

    def test_initialization(self):
        """Test TTS engine initialization."""
        engine = TextToSpeechEngine()
        assert engine.enabled
        assert engine.speaking_rate == 1.0

    def test_set_voice(self):
        """Test setting voice."""
        engine = TextToSpeechEngine()
        
        success = engine.set_voice("en_US-ryan-medium")
        assert success
        assert engine.voice_id == "en_US-ryan-medium"

    def test_set_speaking_rate(self):
        """Test setting speaking rate."""
        engine = TextToSpeechEngine()
        
        engine.set_speaking_rate(1.5)
        assert engine.speaking_rate == 1.5
        
        # Invalid rate should not change
        engine.set_speaking_rate(3.0)
        assert engine.speaking_rate == 1.5

    def test_enable_disable(self):
        """Test enabling/disabling TTS."""
        engine = TextToSpeechEngine(enabled=True)
        assert engine.is_enabled()
        
        engine.set_enabled(False)
        assert not engine.is_enabled()

    def test_synthesize(self):
        """Test text synthesis."""
        engine = TextToSpeechEngine()
        
        audio = engine.synthesize("Hello world")
        assert audio is not None

    def test_available_voices(self):
        """Test getting available voices."""
        engine = TextToSpeechEngine()
        
        voices = engine.get_available_voices()
        assert len(voices) > 0
        assert "en_US-lessac-medium" in voices
