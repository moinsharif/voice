"""Tests for data models."""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st
from src.models.data_models import (
    UserProfile, Session, Exchange, Mood, MoodSummary, SessionMetadata,
    MoodEntry, TranscriptionResult, Face, Expression
)


class TestMood:
    """Tests for Mood model."""

    def test_mood_creation(self):
        """Test creating a mood."""
        mood = Mood(
            timestamp=datetime.now(),
            classification="positive",
            confidence=0.8
        )
        assert mood.classification == "positive"
        assert mood.confidence == 0.8

    def test_mood_serialization(self):
        """Test mood serialization and deserialization."""
        mood = Mood(
            timestamp=datetime.now(),
            classification="neutral",
            confidence=0.5,
            voice_tone="calm"
        )
        
        mood_dict = mood.to_dict()
        mood_restored = Mood.from_dict(mood_dict)
        
        assert mood_restored.classification == mood.classification
        assert mood_restored.confidence == mood.confidence
        assert mood_restored.voice_tone == mood.voice_tone


class TestExchange:
    """Tests for Exchange model."""

    def test_exchange_creation(self):
        """Test creating an exchange."""
        exchange = Exchange(
            timestamp=datetime.now(),
            user_message="Hello",
            ai_response="Hi there!",
            response_feedback=0.9
        )
        assert exchange.user_message == "Hello"
        assert exchange.ai_response == "Hi there!"
        assert exchange.response_feedback == 0.9

    def test_exchange_serialization(self):
        """Test exchange serialization and deserialization."""
        mood = Mood(
            timestamp=datetime.now(),
            classification="positive",
            confidence=0.8
        )
        exchange = Exchange(
            timestamp=datetime.now(),
            user_message="How are you?",
            ai_response="I'm doing well!",
            mood_detected=mood
        )
        
        exchange_dict = exchange.to_dict()
        exchange_restored = Exchange.from_dict(exchange_dict)
        
        assert exchange_restored.user_message == exchange.user_message
        assert exchange_restored.ai_response == exchange.ai_response
        assert exchange_restored.mood_detected is not None


class TestSession:
    """Tests for Session model."""

    def test_session_creation(self):
        """Test creating a session."""
        session = Session(
            session_id="test-session-1",
            user_id="user-1",
            created_at=datetime.now()
        )
        assert session.session_id == "test-session-1"
        assert session.user_id == "user-1"

    def test_session_json_roundtrip(self):
        """Test session JSON serialization roundtrip."""
        exchange = Exchange(
            timestamp=datetime.now(),
            user_message="Hello",
            ai_response="Hi!"
        )
        
        session = Session(
            session_id="test-session-1",
            user_id="user-1",
            created_at=datetime.now(),
            exchanges=[exchange],
            transcript="Hello\nHi!"
        )
        
        json_str = session.to_json()
        session_restored = Session.from_json(json_str)
        
        assert session_restored.session_id == session.session_id
        assert session_restored.user_id == session.user_id
        assert len(session_restored.exchanges) == 1
        assert session_restored.exchanges[0].user_message == "Hello"


class TestUserProfile:
    """Tests for UserProfile model."""

    def test_profile_creation(self):
        """Test creating a user profile."""
        profile = UserProfile(
            user_id="user-1",
            created_at=datetime.now(),
            last_interaction=datetime.now(),
            communication_style="casual"
        )
        assert profile.user_id == "user-1"
        assert profile.communication_style == "casual"

    def test_profile_json_roundtrip(self):
        """Test profile JSON serialization roundtrip."""
        profile = UserProfile(
            user_id="user-1",
            created_at=datetime.now(),
            last_interaction=datetime.now(),
            preferred_topics=["work", "hobbies"],
            interaction_count=10
        )
        
        json_str = profile.to_json()
        profile_restored = UserProfile.from_json(json_str)
        
        assert profile_restored.user_id == profile.user_id
        assert profile_restored.preferred_topics == profile.preferred_topics
        assert profile_restored.interaction_count == profile.interaction_count


class TestMoodSummary:
    """Tests for MoodSummary model."""

    def test_mood_summary_creation(self):
        """Test creating a mood summary."""
        summary = MoodSummary(
            session_id="session-1",
            primary_mood="positive",
            average_confidence=0.8,
            mood_stability=0.9
        )
        assert summary.session_id == "session-1"
        assert summary.primary_mood == "positive"

    def test_mood_summary_serialization(self):
        """Test mood summary serialization."""
        mood = Mood(
            timestamp=datetime.now(),
            classification="positive",
            confidence=0.8
        )
        summary = MoodSummary(
            session_id="session-1",
            primary_mood="positive",
            mood_transitions=[mood],
            average_confidence=0.8
        )
        
        summary_dict = summary.to_dict()
        summary_restored = MoodSummary.from_dict(summary_dict)
        
        assert summary_restored.session_id == summary.session_id
        assert len(summary_restored.mood_transitions) == 1


class TestTranscriptionResult:
    """Tests for TranscriptionResult model."""

    def test_transcription_creation(self):
        """Test creating a transcription result."""
        result = TranscriptionResult(
            text="Hello world",
            confidence=0.95,
            language="en",
            duration_seconds=2.5
        )
        assert result.text == "Hello world"
        assert result.confidence == 0.95


class TestFace:
    """Tests for Face model."""

    def test_face_creation(self):
        """Test creating a face."""
        face = Face(
            face_id=0,
            landmarks=[(10, 20), (30, 40)],
            bounding_box=(0, 0, 100, 100),
            confidence=0.95
        )
        assert face.face_id == 0
        assert len(face.landmarks) == 2


class TestExpression:
    """Tests for Expression model."""

    def test_expression_creation(self):
        """Test creating an expression."""
        expr = Expression(
            expression_type="happy",
            confidence=0.9,
            intensity=0.8
        )
        assert expr.expression_type == "happy"
        assert expr.confidence == 0.9


# Property-Based Testing Strategies

def datetime_strategy():
    """Generate valid datetime objects."""
    return st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31),
        timezones=st.none()
    )


def mood_strategy():
    """Generate valid Mood objects."""
    return st.builds(
        Mood,
        timestamp=datetime_strategy(),
        classification=st.sampled_from(["positive", "neutral", "negative", "mixed"]),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        facial_expression=st.one_of(st.none(), st.sampled_from(["happy", "sad", "angry", "surprised", "neutral"])),
        voice_tone=st.one_of(st.none(), st.sampled_from(["calm", "excited", "sad", "neutral"])),
        conversation_topic=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
        time_of_day=st.one_of(st.none(), st.sampled_from(["morning", "afternoon", "evening", "night"]))
    )


def exchange_strategy():
    """Generate valid Exchange objects."""
    return st.builds(
        Exchange,
        timestamp=datetime_strategy(),
        user_message=st.text(min_size=1, max_size=200),
        ai_response=st.text(min_size=1, max_size=500),
        mood_detected=st.one_of(st.none(), mood_strategy()),
        response_feedback=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0))
    )


def mood_summary_strategy():
    """Generate valid MoodSummary objects."""
    return st.builds(
        MoodSummary,
        session_id=st.text(min_size=1, max_size=50),
        primary_mood=st.sampled_from(["positive", "neutral", "negative", "mixed"]),
        mood_transitions=st.lists(mood_strategy(), max_size=10),
        average_confidence=st.floats(min_value=0.0, max_value=1.0),
        mood_stability=st.floats(min_value=0.0, max_value=1.0)
    )


def session_metadata_strategy():
    """Generate valid SessionMetadata objects."""
    return st.builds(
        SessionMetadata,
        duration_seconds=st.integers(min_value=1, max_value=3600),
        exchange_count=st.integers(min_value=0, max_value=100),
        topics_discussed=st.lists(st.text(min_size=1, max_size=50), max_size=10),
        user_initiated=st.booleans(),
        completion_status=st.sampled_from(["completed", "interrupted", "error"]),
        error_messages=st.lists(st.text(min_size=0, max_size=100), max_size=5)
    )


def session_strategy():
    """Generate valid Session objects with all nested structures."""
    return st.builds(
        Session,
        session_id=st.text(min_size=1, max_size=50),
        user_id=st.text(min_size=1, max_size=50),
        created_at=datetime_strategy(),
        exchanges=st.lists(exchange_strategy(), max_size=20),
        mood_summary=st.one_of(st.none(), mood_summary_strategy()),
        metadata=st.one_of(st.none(), session_metadata_strategy()),
        audio_data=st.one_of(st.none(), st.binary(min_size=0, max_size=1000)),
        transcript=st.text(max_size=500),
        ended_at=st.one_of(st.none(), datetime_strategy())
    )


class TestSessionSerialization:
    """Property-based tests for Session serialization."""

    @given(session_strategy())
    def test_session_serialization_roundtrip(self, session: Session):
        """
        **Validates: Requirement 17.3**
        
        FOR ALL valid Session objects, serializing then deserializing 
        SHALL produce an equivalent object.
        
        This property test verifies:
        - All fields are preserved exactly
        - Nested objects (Exchange, Mood, MoodSummary, SessionMetadata) are correctly reconstructed
        - Datetime objects maintain precision
        - Binary audio_data is correctly encoded/decoded
        - Optional fields are handled correctly
        """
        # Serialize to JSON
        json_str = session.to_json()
        
        # Deserialize back from JSON
        restored_session = Session.from_json(json_str)
        
        # Assert all fields are preserved
        assert restored_session.session_id == session.session_id
        assert restored_session.user_id == session.user_id
        assert restored_session.created_at == session.created_at
        assert restored_session.ended_at == session.ended_at
        assert restored_session.transcript == session.transcript
        
        # Assert exchanges are preserved
        assert len(restored_session.exchanges) == len(session.exchanges)
        for original_ex, restored_ex in zip(session.exchanges, restored_session.exchanges):
            assert restored_ex.timestamp == original_ex.timestamp
            assert restored_ex.user_message == original_ex.user_message
            assert restored_ex.ai_response == original_ex.ai_response
            assert restored_ex.response_feedback == original_ex.response_feedback
            
            # Assert nested mood is preserved
            if original_ex.mood_detected:
                assert restored_ex.mood_detected is not None
                assert restored_ex.mood_detected.timestamp == original_ex.mood_detected.timestamp
                assert restored_ex.mood_detected.classification == original_ex.mood_detected.classification
                assert restored_ex.mood_detected.confidence == original_ex.mood_detected.confidence
                assert restored_ex.mood_detected.facial_expression == original_ex.mood_detected.facial_expression
                assert restored_ex.mood_detected.voice_tone == original_ex.mood_detected.voice_tone
                assert restored_ex.mood_detected.conversation_topic == original_ex.mood_detected.conversation_topic
                assert restored_ex.mood_detected.time_of_day == original_ex.mood_detected.time_of_day
            else:
                assert restored_ex.mood_detected is None
        
        # Assert mood_summary is preserved
        if session.mood_summary:
            assert restored_session.mood_summary is not None
            assert restored_session.mood_summary.session_id == session.mood_summary.session_id
            assert restored_session.mood_summary.primary_mood == session.mood_summary.primary_mood
            assert restored_session.mood_summary.average_confidence == session.mood_summary.average_confidence
            assert restored_session.mood_summary.mood_stability == session.mood_summary.mood_stability
            assert len(restored_session.mood_summary.mood_transitions) == len(session.mood_summary.mood_transitions)
            
            for original_mood, restored_mood in zip(
                session.mood_summary.mood_transitions,
                restored_session.mood_summary.mood_transitions
            ):
                assert restored_mood.timestamp == original_mood.timestamp
                assert restored_mood.classification == original_mood.classification
                assert restored_mood.confidence == original_mood.confidence
        else:
            assert restored_session.mood_summary is None
        
        # Assert metadata is preserved
        if session.metadata:
            assert restored_session.metadata is not None
            assert restored_session.metadata.duration_seconds == session.metadata.duration_seconds
            assert restored_session.metadata.exchange_count == session.metadata.exchange_count
            assert restored_session.metadata.topics_discussed == session.metadata.topics_discussed
            assert restored_session.metadata.user_initiated == session.metadata.user_initiated
            assert restored_session.metadata.completion_status == session.metadata.completion_status
            assert restored_session.metadata.error_messages == session.metadata.error_messages
        else:
            assert restored_session.metadata is None
        
        # Assert binary audio_data is correctly encoded/decoded
        assert restored_session.audio_data == session.audio_data
