"""Context Manager for conversation state and user profile."""

from typing import Optional, List
from datetime import datetime
from src.models.data_models import UserProfile, Exchange, Session
from src.persistence.persistence_layer import PersistenceLayer
from src.utils.logger import Logger


class ContextManager:
    """Manages conversation context and user profile."""

    def __init__(self, persistence_layer: Optional[PersistenceLayer] = None, 
                 max_context_exchanges: int = 10):
        """Initialize context manager.
        
        Args:
            persistence_layer: Persistence layer for data storage
            max_context_exchanges: Maximum exchanges to keep in context
        """
        self.persistence_layer = persistence_layer
        self.max_context_exchanges = max_context_exchanges
        self.logger = Logger("ContextManager")
        
        self.current_user_id: Optional[str] = None
        self.current_user_profile: Optional[UserProfile] = None
        self.current_exchanges: List[Exchange] = []
        self.current_session: Optional[Session] = None

    def load_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load user profile.
        
        Args:
            user_id: User ID
            
        Returns:
            UserProfile or None if not found
        """
        try:
            self.current_user_id = user_id

            if self.persistence_layer:
                profile = self.persistence_layer.load_user_profile(user_id)
                if profile:
                    self.current_user_profile = profile
                    self.logger.info(f"Loaded user profile for {user_id}")
                    return profile

            # Create new profile if not found
            profile = UserProfile(
                user_id=user_id,
                created_at=datetime.now(),
                last_interaction=datetime.now()
            )
            self.current_user_profile = profile
            self.logger.info(f"Created new user profile for {user_id}")
            return profile

        except Exception as e:
            self.logger.error(f"Failed to load user profile: {e}")
            return None

    def save_user_profile(self) -> bool:
        """Save current user profile.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_user_profile or not self.persistence_layer:
                return False

            self.current_user_profile.last_interaction = datetime.now()
            self.persistence_layer.save_user_profile(self.current_user_profile)
            self.logger.info(f"Saved user profile for {self.current_user_profile.user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save user profile: {e}")
            return False

    def add_exchange(self, exchange: Exchange) -> None:
        """Add exchange to context.
        
        Args:
            exchange: Exchange to add
        """
        self.current_exchanges.append(exchange)

        # Keep only last N exchanges
        if len(self.current_exchanges) > self.max_context_exchanges:
            self.current_exchanges = self.current_exchanges[-self.max_context_exchanges:]

        self.logger.info(f"Added exchange, context size: {len(self.current_exchanges)}")

    def get_context_string(self) -> str:
        """Get formatted context string for AI model.
        
        Returns:
            Formatted context string
        """
        context_lines = []

        # Add user profile info
        if self.current_user_profile:
            context_lines.append(f"User: {self.current_user_profile.user_id}")
            if self.current_user_profile.communication_style:
                context_lines.append(f"Style: {self.current_user_profile.communication_style}")

        # Add recent exchanges
        context_lines.append("\nRecent conversation:")
        for exchange in self.current_exchanges[-5:]:
            context_lines.append(f"User: {exchange.user_message}")
            context_lines.append(f"Assistant: {exchange.ai_response}")

        return "\n".join(context_lines)

    def get_recent_exchanges(self, count: int = 5) -> List[Exchange]:
        """Get recent exchanges.
        
        Args:
            count: Number of recent exchanges to return
            
        Returns:
            List of recent exchanges
        """
        return self.current_exchanges[-count:]

    def clear_context(self) -> None:
        """Clear current context."""
        self.current_exchanges.clear()
        self.logger.info("Context cleared")

    def start_session(self, user_id: str, session_id: str) -> Session:
        """Start new session.
        
        Args:
            user_id: User ID
            session_id: Session ID
            
        Returns:
            New Session object
        """
        self.load_user_profile(user_id)
        self.clear_context()

        self.current_session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now()
        )

        self.logger.info(f"Started session {session_id} for user {user_id}")
        return self.current_session

    def end_session(self) -> Optional[Session]:
        """End current session.
        
        Returns:
            Completed Session object or None
        """
        try:
            if not self.current_session:
                return None

            self.current_session.ended_at = datetime.now()
            self.current_session.exchanges = self.current_exchanges

            if self.persistence_layer:
                self.persistence_layer.save_conversation(self.current_session)

            self.logger.info(f"Ended session {self.current_session.session_id}")
            return self.current_session

        except Exception as e:
            self.logger.error(f"Failed to end session: {e}")
            return None

    def load_conversation_history(self, user_id: str, limit: int = 10) -> List[Session]:
        """Load conversation history for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations to load
            
        Returns:
            List of Session objects
        """
        try:
            if not self.persistence_layer:
                return []

            sessions = self.persistence_layer.search_conversations(user_id)
            return sessions[-limit:]

        except Exception as e:
            self.logger.error(f"Failed to load conversation history: {e}")
            return []

    def get_user_profile(self) -> Optional[UserProfile]:
        """Get current user profile.
        
        Returns:
            Current UserProfile or None
        """
        return self.current_user_profile

    def update_user_preferences(self, preferences: dict) -> bool:
        """Update user preferences.
        
        Args:
            preferences: Dictionary of preferences to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_user_profile:
                return False

            for key, value in preferences.items():
                if hasattr(self.current_user_profile, key):
                    setattr(self.current_user_profile, key, value)

            return self.save_user_profile()

        except Exception as e:
            self.logger.error(f"Failed to update user preferences: {e}")
            return False

    def get_model_info(self) -> dict:
        """Get information about context manager.
        
        Returns:
            Dictionary with manager information
        """
        return {
            "current_user_id": self.current_user_id,
            "context_size": len(self.current_exchanges),
            "max_context_exchanges": self.max_context_exchanges,
            "has_session": self.current_session is not None
        }
