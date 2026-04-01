"""Tests for persistence layer."""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
from src.persistence.persistence_layer import PersistenceLayer
from src.models.data_models import Session, UserProfile, Exchange, MoodEntry


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


class TestPersistenceLayer:
    """Tests for PersistenceLayer."""

    def test_initialization(self, temp_db):
        """Test persistence layer initialization."""
        persistence = PersistenceLayer(db_path=temp_db)
        assert persistence.db_path == temp_db

    def test_save_and_load_conversation(self, temp_db):
        """Test saving and loading conversation."""
        persistence = PersistenceLayer(db_path=temp_db)
        
        exchange = Exchange(
            timestamp=datetime.now(),
            user_message="Hello",
            ai_response="Hi!"
        )
        
        session = Session(
            session_id="test-session-1",
            user_id="user-1",
            created_at=datetime.now(),
            exchanges=[exchange]
        )
        
        persistence.save_conversation(session)
        loaded_session = persistence.load_conversation("test-session-1")
        
        assert loaded_session is not None
        assert loaded_session.session_id == "test-session-1"
        assert len(loaded_session.exchanges) == 1

    def test_save_and_load_user_profile(self, temp_db):
        """Test saving and loading user profile."""
        persistence = PersistenceLayer(db_path=temp_db)
        
        profile = UserProfile(
            user_id="user-1",
            created_at=datetime.now(),
            last_interaction=datetime.now(),
            communication_style="casual"
        )
        
        persistence.save_user_profile(profile)
        loaded_profile = persistence.load_user_profile("user-1")
        
        assert loaded_profile is not None
        assert loaded_profile.user_id == "user-1"
        assert loaded_profile.communication_style == "casual"

    def test_search_conversations(self, temp_db):
        """Test searching conversations."""
        persistence = PersistenceLayer(db_path=temp_db)
        
        # Create and save multiple sessions
        for i in range(3):
            exchange = Exchange(
                timestamp=datetime.now(),
                user_message=f"Message {i}",
                ai_response=f"Response {i}"
            )
            session = Session(
                session_id=f"session-{i}",
                user_id="user-1",
                created_at=datetime.now(),
                exchanges=[exchange]
            )
            persistence.save_conversation(session)
        
        # Search
        results = persistence.search_conversations("user-1")
        assert len(results) == 3

    def test_delete_conversation(self, temp_db):
        """Test deleting conversation."""
        persistence = PersistenceLayer(db_path=temp_db)
        
        session = Session(
            session_id="test-session-1",
            user_id="user-1",
            created_at=datetime.now()
        )
        
        persistence.save_conversation(session)
        assert persistence.load_conversation("test-session-1") is not None
        
        persistence.delete_conversation("test-session-1")
        assert persistence.load_conversation("test-session-1") is None

    def test_export_conversations_json(self, temp_db):
        """Test exporting conversations as JSON."""
        persistence = PersistenceLayer(db_path=temp_db)
        
        exchange = Exchange(
            timestamp=datetime.now(),
            user_message="Hello",
            ai_response="Hi!"
        )
        session = Session(
            session_id="test-session-1",
            user_id="user-1",
            created_at=datetime.now(),
            exchanges=[exchange]
        )
        
        persistence.save_conversation(session)
        exported = persistence.export_conversations("user-1", format="json")
        
        assert exported is not None
        assert "user-1" in exported
        assert "sessions" in exported

    def test_configuration_storage(self, temp_db):
        """Test configuration storage."""
        persistence = PersistenceLayer(db_path=temp_db)
        
        persistence.save_configuration("language", "en")
        value = persistence.load_configuration("language")
        
        assert value == "en"

    def test_backup_and_restore(self, temp_db):
        """Test backup and restore functionality."""
        persistence = PersistenceLayer(db_path=temp_db)
        
        # Save some data
        session = Session(
            session_id="test-session-1",
            user_id="user-1",
            created_at=datetime.now()
        )
        persistence.save_conversation(session)
        
        # Create backup
        backup_id = persistence.create_backup()
        assert backup_id is not None
        
        # Delete original
        persistence.delete_conversation("test-session-1")
        assert persistence.load_conversation("test-session-1") is None
        
        # Restore
        success = persistence.restore_backup(backup_id)
        assert success
        assert persistence.load_conversation("test-session-1") is not None


# Property-based tests using Hypothesis

def mood_entry_strategy():
    """Strategy for generating valid MoodEntry objects."""
    return st.builds(
        MoodEntry,
        timestamp=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime.now()
        ),
        classification=st.sampled_from(["positive", "neutral", "negative", "mixed"]),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        facial_expression=st.one_of(
            st.none(),
            st.sampled_from(["happy", "sad", "angry", "surprised", "neutral"])
        ),
        voice_tone=st.one_of(
            st.none(),
            st.sampled_from(["upbeat", "downbeat", "neutral", "excited", "calm"])
        ),
        conversation_topic=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
        time_of_day=st.one_of(
            st.none(),
            st.sampled_from(["morning", "afternoon", "evening", "night"])
        )
    )


def user_profile_strategy():
    """Strategy for generating valid UserProfile objects."""
    now = datetime.now()
    return st.builds(
        UserProfile,
        user_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
        created_at=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=now
        ),
        last_interaction=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=now
        ),
        communication_style=st.sampled_from(["formal", "casual", "technical"]),
        preferred_topics=st.lists(
            st.text(min_size=1, max_size=30, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
            max_size=10
        ),
        response_preferences=st.dictionaries(
            keys=st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
            values=st.floats(min_value=0.0, max_value=1.0),
            max_size=5
        ),
        mood_history=st.lists(mood_entry_strategy(), max_size=20),
        average_mood=st.sampled_from(["positive", "neutral", "negative", "mixed"]),
        mood_trends=st.dictionaries(
            keys=st.sampled_from(["positive", "neutral", "negative", "mixed"]),
            values=st.floats(min_value=0.0, max_value=1.0),
            max_size=4
        ),
        learned_preferences=st.dictionaries(
            keys=st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
            values=st.one_of(
                st.text(max_size=50),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.booleans()
            ),
            max_size=5
        ),
        interaction_count=st.integers(min_value=0, max_value=10000),
        last_learning_update=st.one_of(
            st.none(),
            st.datetimes(
                min_value=datetime(2020, 1, 1),
                max_value=now
            )
        ),
        language=st.sampled_from(["en", "es", "fr", "de", "ja", "zh"]),
        voice_id=st.text(min_size=1, max_size=30, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
        speaking_rate=st.floats(min_value=0.5, max_value=2.0),
        listening_sensitivity=st.floats(min_value=0.0, max_value=1.0),
        mood_sensitivity=st.floats(min_value=0.0, max_value=1.0)
    )


class TestUserProfilePersistenceProperty:
    """Property-based tests for User Profile persistence."""

    @given(user_profile_strategy())
    @settings(deadline=None)
    def test_user_profile_persistence_roundtrip(self, profile):
        """
        **Validates: Requirement 18.3**
        
        Property 3: User Profile Round-Trip Consistency
        
        FOR ALL valid UserProfile objects, saving then loading SHALL produce an equivalent object.
        
        This test verifies:
        - All fields are preserved exactly
        - Nested objects (mood_history list of MoodEntry) are correctly reconstructed
        - Datetime objects maintain precision
        - Dictionary fields (response_preferences, mood_trends, learned_preferences) are preserved
        - Optional fields are handled correctly
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            persistence = PersistenceLayer(db_path=db_path)
            
            # Save the profile
            persistence.save_user_profile(profile)
            
            # Load it back
            loaded_profile = persistence.load_user_profile(profile.user_id)
            
            # Verify the loaded profile is not None
            assert loaded_profile is not None, "Loaded profile should not be None"
            
            # Verify all fields are preserved exactly
            assert loaded_profile.user_id == profile.user_id, "user_id should be preserved"
            assert loaded_profile.communication_style == profile.communication_style, "communication_style should be preserved"
            assert loaded_profile.language == profile.language, "language should be preserved"
            assert loaded_profile.voice_id == profile.voice_id, "voice_id should be preserved"
            assert loaded_profile.speaking_rate == profile.speaking_rate, "speaking_rate should be preserved"
            assert loaded_profile.listening_sensitivity == profile.listening_sensitivity, "listening_sensitivity should be preserved"
            assert loaded_profile.mood_sensitivity == profile.mood_sensitivity, "mood_sensitivity should be preserved"
            assert loaded_profile.average_mood == profile.average_mood, "average_mood should be preserved"
            assert loaded_profile.interaction_count == profile.interaction_count, "interaction_count should be preserved"
            
            # Verify datetime objects maintain precision (to microsecond level)
            assert abs((loaded_profile.created_at - profile.created_at).total_seconds()) < 0.001, "created_at should be preserved with precision"
            assert abs((loaded_profile.last_interaction - profile.last_interaction).total_seconds()) < 0.001, "last_interaction should be preserved with precision"
            
            # Verify optional datetime field
            if profile.last_learning_update is not None:
                assert loaded_profile.last_learning_update is not None, "last_learning_update should not be None if original was not None"
                assert abs((loaded_profile.last_learning_update - profile.last_learning_update).total_seconds()) < 0.001, "last_learning_update should be preserved with precision"
            else:
                assert loaded_profile.last_learning_update is None, "last_learning_update should be None if original was None"
            
            # Verify list fields are preserved
            assert len(loaded_profile.preferred_topics) == len(profile.preferred_topics), "preferred_topics length should be preserved"
            assert loaded_profile.preferred_topics == profile.preferred_topics, "preferred_topics should be preserved exactly"
            
            # Verify dictionary fields are preserved
            assert loaded_profile.response_preferences == profile.response_preferences, "response_preferences should be preserved exactly"
            assert loaded_profile.mood_trends == profile.mood_trends, "mood_trends should be preserved exactly"
            assert loaded_profile.learned_preferences == profile.learned_preferences, "learned_preferences should be preserved exactly"
            
            # Verify nested MoodEntry objects are correctly reconstructed
            assert len(loaded_profile.mood_history) == len(profile.mood_history), "mood_history length should be preserved"
            for i, (loaded_mood, original_mood) in enumerate(zip(loaded_profile.mood_history, profile.mood_history)):
                assert loaded_mood.classification == original_mood.classification, f"mood_history[{i}].classification should be preserved"
                assert abs(loaded_mood.confidence - original_mood.confidence) < 0.0001, f"mood_history[{i}].confidence should be preserved"
                assert abs((loaded_mood.timestamp - original_mood.timestamp).total_seconds()) < 0.001, f"mood_history[{i}].timestamp should be preserved with precision"
                assert loaded_mood.facial_expression == original_mood.facial_expression, f"mood_history[{i}].facial_expression should be preserved"
                assert loaded_mood.voice_tone == original_mood.voice_tone, f"mood_history[{i}].voice_tone should be preserved"
                assert loaded_mood.conversation_topic == original_mood.conversation_topic, f"mood_history[{i}].conversation_topic should be preserved"
                assert loaded_mood.time_of_day == original_mood.time_of_day, f"mood_history[{i}].time_of_day should be preserved"
