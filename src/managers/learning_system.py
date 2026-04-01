"""Learning System for daily interaction analysis."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
from src.models.data_models import Session, UserProfile, Exchange
from src.utils.logger import Logger


class LearningInsights:
    """Insights from daily learning analysis."""

    def __init__(self):
        """Initialize learning insights."""
        self.topic_preferences: Dict[str, float] = {}
        self.communication_style: Optional[str] = None
        self.response_preferences: Dict[str, float] = {}
        self.mood_patterns: Dict[str, float] = {}
        self.time_patterns: Dict[str, float] = {}


class Pattern:
    """Identified pattern in interactions."""

    def __init__(self, pattern_type: str, value: Any, confidence: float):
        """Initialize pattern.
        
        Args:
            pattern_type: Type of pattern
            value: Pattern value
            confidence: Confidence score (0.0-1.0)
        """
        self.pattern_type = pattern_type
        self.value = value
        self.confidence = confidence


class LearningSystem:
    """Analyzes daily interactions and improves response quality."""

    def __init__(self):
        """Initialize learning system."""
        self.logger = Logger("LearningSystem")
        self.context_manager = None

    def set_context_manager(self, context_manager) -> None:
        """Set context manager for learning system.
        
        Args:
            context_manager: ContextManager instance
        """
        self.context_manager = context_manager
        self.logger.info("Context manager set for learning system")

    def analyze_day(self, user_id: str, sessions: List[Session]) -> LearningInsights:
        """Analyze all interactions from a day.
        
        Args:
            user_id: User ID
            sessions: List of sessions from the day
            
        Returns:
            LearningInsights object
        """
        try:
            insights = LearningInsights()

            if not sessions:
                return insights

            # Extract all exchanges
            all_exchanges = []
            for session in sessions:
                all_exchanges.extend(session.exchanges)

            if not all_exchanges:
                return insights

            # Analyze patterns
            insights.topic_preferences = self._analyze_topic_preferences(all_exchanges)
            insights.communication_style = self._analyze_communication_style(all_exchanges)
            insights.response_preferences = self._analyze_response_preferences(all_exchanges)
            insights.mood_patterns = self._analyze_mood_patterns(sessions)
            insights.time_patterns = self._analyze_time_patterns(sessions)

            self.logger.info(f"Analyzed {len(all_exchanges)} exchanges for user {user_id}")
            return insights

        except Exception as e:
            self.logger.error(f"Failed to analyze day: {e}")
            return LearningInsights()

    def _analyze_topic_preferences(self, exchanges: List[Exchange]) -> Dict[str, float]:
        """Analyze topic preferences from exchanges.
        
        Args:
            exchanges: List of exchanges
            
        Returns:
            Dictionary mapping topics to preference scores
        """
        topics = {}

        # Simple keyword-based topic extraction
        topic_keywords = {
            "work": ["work", "job", "project", "meeting", "deadline"],
            "family": ["family", "parent", "sibling", "child", "relative"],
            "hobbies": ["hobby", "game", "music", "book", "movie"],
            "health": ["health", "exercise", "sleep", "diet", "fitness"],
            "technology": ["tech", "computer", "software", "code", "app"],
        }

        for exchange in exchanges:
            message = exchange.user_message.lower()
            for topic, keywords in topic_keywords.items():
                if any(keyword in message for keyword in keywords):
                    topics[topic] = topics.get(topic, 0) + 1

        # Normalize to scores
        if topics:
            total = sum(topics.values())
            return {topic: count / total for topic, count in topics.items()}

        return {}

    def _analyze_communication_style(self, exchanges: List[Exchange]) -> Optional[str]:
        """Analyze communication style.
        
        Args:
            exchanges: List of exchanges
            
        Returns:
            Communication style ("formal", "casual", "technical")
        """
        if not exchanges:
            return None

        # Analyze message characteristics
        avg_length = sum(len(e.user_message.split()) for e in exchanges) / len(exchanges)
        formal_words = sum(1 for e in exchanges if any(
            word in e.user_message.lower() for word in ["therefore", "however", "moreover"]
        ))

        if avg_length > 20 and formal_words > len(exchanges) * 0.1:
            return "formal"
        elif avg_length < 5:
            return "casual"
        else:
            return "casual"

    def _analyze_response_preferences(self, exchanges: List[Exchange]) -> Dict[str, float]:
        """Analyze response type preferences.
        
        Args:
            exchanges: List of exchanges
            
        Returns:
            Dictionary mapping response types to preference scores
        """
        preferences = {}

        for exchange in exchanges:
            if exchange.response_feedback:
                # Categorize response type
                response_type = self._categorize_response(exchange.ai_response)
                if response_type:
                    preferences[response_type] = preferences.get(response_type, 0) + exchange.response_feedback

        # Normalize
        if preferences:
            total = sum(preferences.values())
            return {rtype: score / total for rtype, score in preferences.items()}

        return {}

    def _categorize_response(self, response: str) -> Optional[str]:
        """Categorize response type.
        
        Args:
            response: Response text
            
        Returns:
            Response type or None
        """
        response_lower = response.lower()

        if any(word in response_lower for word in ["haha", "lol", "funny", "joke"]):
            return "humorous"
        elif any(word in response_lower for word in ["understand", "feel", "empathize", "sorry"]):
            return "empathetic"
        elif any(word in response_lower for word in ["technically", "specifically", "precisely"]):
            return "technical"
        else:
            return "informative"

    def _analyze_mood_patterns(self, sessions: List[Session]) -> Dict[str, float]:
        """Analyze mood patterns.
        
        Args:
            sessions: List of sessions
            
        Returns:
            Dictionary mapping moods to frequency
        """
        moods = []

        for session in sessions:
            if session.mood_summary:
                moods.append(session.mood_summary.primary_mood)

        if not moods:
            return {}

        mood_counts = Counter(moods)
        total = len(moods)

        return {mood: count / total for mood, count in mood_counts.items()}

    def _analyze_time_patterns(self, sessions: List[Session]) -> Dict[str, float]:
        """Analyze time-based patterns.
        
        Args:
            sessions: List of sessions
            
        Returns:
            Dictionary mapping time periods to activity frequency
        """
        time_periods = {}

        for session in sessions:
            hour = session.created_at.hour
            if hour < 6:
                period = "night"
            elif hour < 12:
                period = "morning"
            elif hour < 18:
                period = "afternoon"
            else:
                period = "evening"

            time_periods[period] = time_periods.get(period, 0) + 1

        if time_periods:
            total = sum(time_periods.values())
            return {period: count / total for period, count in time_periods.items()}

        return {}

    def identify_patterns(self, exchanges: List[Exchange]) -> List[Pattern]:
        """Identify patterns in interactions.
        
        Args:
            exchanges: List of exchanges
            
        Returns:
            List of identified patterns
        """
        patterns = []

        # Pattern 1: Frequent topics
        topics = self._analyze_topic_preferences(exchanges)
        for topic, score in topics.items():
            if score > 0.2:
                patterns.append(Pattern("frequent_topic", topic, score))

        # Pattern 2: Communication style
        style = self._analyze_communication_style(exchanges)
        if style:
            patterns.append(Pattern("communication_style", style, 0.8))

        # Pattern 3: Response preferences
        prefs = self._analyze_response_preferences(exchanges)
        for pref, score in prefs.items():
            if score > 0.3:
                patterns.append(Pattern("response_preference", pref, score))

        return patterns

    def update_user_profile(self, profile: UserProfile, insights: LearningInsights) -> None:
        """Update user profile with learned insights.
        
        Args:
            profile: UserProfile to update
            insights: LearningInsights from analysis
        """
        try:
            # Update topic preferences
            if insights.topic_preferences:
                profile.preferred_topics = list(insights.topic_preferences.keys())

            # Update communication style
            if insights.communication_style:
                profile.communication_style = insights.communication_style

            # Update response preferences
            if insights.response_preferences:
                profile.response_preferences.update(insights.response_preferences)

            # Update mood trends
            if insights.mood_patterns:
                profile.mood_trends.update(insights.mood_patterns)
                primary_mood = max(insights.mood_patterns, key=insights.mood_patterns.get)
                profile.average_mood = primary_mood

            # Update learning metadata
            profile.last_learning_update = datetime.now()

            self.logger.info(f"Updated user profile for {profile.user_id}")

        except Exception as e:
            self.logger.error(f"Failed to update user profile: {e}")

    def apply_learnings(self, profile: UserProfile) -> Dict[str, Any]:
        """Apply previous learnings to improve responses.
        
        Args:
            profile: UserProfile with learned preferences
            
        Returns:
            Dictionary with applied learnings
        """
        learnings = {
            "communication_style": profile.communication_style,
            "preferred_topics": profile.preferred_topics,
            "response_preferences": profile.response_preferences,
            "mood_state": profile.average_mood,
        }

        self.logger.info(f"Applied learnings for user {profile.user_id}")
        return learnings

    def get_model_info(self) -> dict:
        """Get information about learning system.
        
        Returns:
            Dictionary with system information
        """
        return {
            "system_type": "LearningSystem",
            "status": "active"
        }
