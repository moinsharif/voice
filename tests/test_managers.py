"""Tests for managers."""

import pytest
import tempfile
import os
from datetime import datetime
from src.managers.context_manager import ContextManager
from src.managers.session_manager import SessionManager, SessionState
from src.managers.learning_system import LearningSystem, LearningInsights
from src.persistence.persistence_layer import PersistenceLayer
from src.models.data_models import (
    UserProfile, Session, Exchange, Mood
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


class TestContextManager:
    """Tests for ContextManager."""

    def test_initialization(self, temp_db):
        """Test context manager initialization."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        assert context.current_user_id is None

    def test_load_user_profile(self, temp_db):
        """Test loading user profile."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        
        profile = context.load_user_profile("user-1")
        assert profile is not None
        assert profile.user_id == "user-1"

    def test_save_user_profile(self, temp_db):
        """Test saving user profile."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        
        context.load_user_profile("user-1")
        success = context.save_user_profile()
        assert success

    def test_add_exchange(self, temp_db):
        """Test adding exchanges to context."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        
        exchange = Exchange(
            timestamp=datetime.now(),
            user_message="Hello",
            ai_response="Hi!"
        )
        
        context.add_exchange(exchange)
        assert len(context.current_exchanges) == 1

    def test_context_string(self, temp_db):
        """Test getting context string."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        
        context.load_user_profile("user-1")
        exchange = Exchange(
            timestamp=datetime.now(),
            user_message="Hello",
            ai_response="Hi!"
        )
        context.add_exchange(exchange)
        
        context_str = context.get_context_string()
        assert "Hello" in context_str
        assert "Hi!" in context_str

    def test_start_session(self, temp_db):
        """Test starting a session."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        
        session = context.start_session("user-1", "session-1")
        assert session is not None
        assert session.user_id == "user-1"

    def test_end_session(self, temp_db):
        """Test ending a session."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        
        context.start_session("user-1", "session-1")
        session = context.end_session()
        assert session is not None
        assert session.ended_at is not None


class TestSessionManager:
    """Tests for SessionManager."""

    def test_initialization(self, temp_db):
        """Test session manager initialization."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        manager = SessionManager(context)
        
        assert manager.current_state == SessionState.IDLE

    def test_start_session(self, temp_db):
        """Test starting a session."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        manager = SessionManager(context)
        
        session = manager.start_session("user-1")
        assert session is not None
        assert manager.current_state == SessionState.IDLE

    def test_end_session(self, temp_db):
        """Test ending a session."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        manager = SessionManager(context)
        
        manager.start_session("user-1")
        session = manager.end_session()
        assert session is not None
        assert manager.current_state == SessionState.ENDED

    def test_pause_resume_session(self, temp_db):
        """Test pausing and resuming session."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        manager = SessionManager(context)
        
        manager.start_session("user-1")
        
        success = manager.pause_session()
        assert success
        assert manager.current_state == SessionState.PAUSED
        
        success = manager.resume_session()
        assert success
        assert manager.current_state == SessionState.IDLE

    def test_get_session_state(self, temp_db):
        """Test getting session state."""
        persistence = PersistenceLayer(db_path=temp_db)
        context = ContextManager(persistence_layer=persistence)
        manager = SessionManager(context)
        
        manager.start_session("user-1")
        state = manager.get_session_state()
        
        assert state["state"] == "idle"
        assert state["exchange_count"] == 0


class TestLearningSystem:
    """Tests for LearningSystem."""

    def test_initialization(self):
        """Test learning system initialization."""
        system = LearningSystem()
        assert system is not None

    def test_analyze_day(self):
        """Test analyzing a day of interactions."""
        system = LearningSystem()
        
        exchange = Exchange(
            timestamp=datetime.now(),
            user_message="I love working on projects",
            ai_response="That's great!"
        )
        
        session = Session(
            session_id="session-1",
            user_id="user-1",
            created_at=datetime.now(),
            exchanges=[exchange]
        )
        
        insights = system.analyze_day("user-1", [session])
        assert isinstance(insights, LearningInsights)

    def test_identify_patterns(self):
        """Test identifying patterns."""
        system = LearningSystem()
        
        exchanges = [
            Exchange(
                timestamp=datetime.now(),
                user_message="I love working on projects",
                ai_response="That's great!"
            ),
            Exchange(
                timestamp=datetime.now(),
                user_message="I enjoy coding",
                ai_response="Nice!"
            ),
        ]
        
        patterns = system.identify_patterns(exchanges)
        assert len(patterns) > 0

    def test_update_user_profile(self):
        """Test updating user profile with insights."""
        system = LearningSystem()
        
        profile = UserProfile(
            user_id="user-1",
            created_at=datetime.now(),
            last_interaction=datetime.now()
        )
        
        insights = LearningInsights()
        insights.communication_style = "casual"
        insights.topic_preferences = {"work": 0.6, "hobbies": 0.4}
        
        system.update_user_profile(profile, insights)
        
        assert profile.communication_style == "casual"
        assert "work" in profile.preferred_topics

    def test_apply_learnings(self):
        """Test applying learnings."""
        system = LearningSystem()
        
        profile = UserProfile(
            user_id="user-1",
            created_at=datetime.now(),
            last_interaction=datetime.now(),
            communication_style="formal",
            preferred_topics=["work"]
        )
        
        learnings = system.apply_learnings(profile)
        
        assert learnings["communication_style"] == "formal"
        assert "work" in learnings["preferred_topics"]

    def test_analyze_topic_preferences(self):
        """Test analyzing topic preferences."""
        system = LearningSystem()
        
        exchanges = [
            Exchange(
                timestamp=datetime.now(),
                user_message="I love my job",
                ai_response="That's great!"
            ),
            Exchange(
                timestamp=datetime.now(),
                user_message="I enjoy family time",
                ai_response="Nice!"
            ),
        ]
        
        topics = system._analyze_topic_preferences(exchanges)
        assert "work" in topics or "family" in topics

    def test_analyze_communication_style(self):
        """Test analyzing communication style."""
        system = LearningSystem()
        
        exchanges = [
            Exchange(
                timestamp=datetime.now(),
                user_message="Hi",
                ai_response="Hello"
            ),
        ]
        
        style = system._analyze_communication_style(exchanges)
        assert style in ["formal", "casual", "technical"]
