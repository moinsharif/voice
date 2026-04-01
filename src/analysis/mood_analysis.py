"""Mood Analysis Engine."""

from typing import Optional, List, Dict
from datetime import datetime
import numpy as np
from src.models.data_models import Mood, MoodSummary, Face, Expression
from src.utils.logger import Logger


class MoodAnalysisEngine:
    """Analyzes user emotional state from voice and facial expressions."""

    def __init__(self):
        """Initialize mood analysis engine."""
        self.logger = Logger("MoodAnalysisEngine")
        self.mood_history: List[Mood] = []

    def analyze_mood(self, audio_data: Optional[bytes] = None, 
                    face: Optional[Face] = None,
                    expression: Optional[Expression] = None) -> Mood:
        """Analyze mood from audio and/or facial expression.
        
        Args:
            audio_data: Audio data for voice tone analysis
            face: Detected face
            expression: Facial expression
            
        Returns:
            Mood classification
        """
        try:
            # Analyze voice tone
            voice_mood = self._analyze_voice_tone(audio_data) if audio_data else None
            
            # Analyze facial expression
            facial_mood = self._analyze_facial_expression(expression) if expression else None

            # Combine analyses
            mood = self._combine_mood_signals(voice_mood, facial_mood)

            # Add to history
            self.mood_history.append(mood)

            self.logger.info(f"Mood analyzed: {mood.classification}")
            return mood

        except Exception as e:
            self.logger.error(f"Mood analysis failed: {e}")
            # Default to neutral on error
            return Mood(
                timestamp=datetime.now(),
                classification="neutral",
                confidence=0.0
            )

    def _analyze_voice_tone(self, audio_data: bytes) -> Optional[Mood]:
        """Analyze voice tone from audio.
        
        Args:
            audio_data: Audio data
            
        Returns:
            Mood from voice analysis or None
        """
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)

            # Extract features
            energy = np.mean(np.abs(audio_array))
            zero_crossing_rate = np.mean(np.abs(np.diff(np.sign(audio_array))))

            # Simple classification based on features
            if energy > 0.3:
                classification = "positive"
            elif energy < 0.1:
                classification = "negative"
            else:
                classification = "neutral"

            confidence = min(energy, 1.0)

            return Mood(
                timestamp=datetime.now(),
                classification=classification,
                confidence=confidence,
                voice_tone=classification
            )

        except Exception as e:
            self.logger.warning(f"Voice tone analysis failed: {e}")
            return None

    def _analyze_facial_expression(self, expression: Expression) -> Optional[Mood]:
        """Analyze mood from facial expression.
        
        Args:
            expression: Facial expression
            
        Returns:
            Mood from facial analysis or None
        """
        try:
            # Map expression to mood
            expression_to_mood = {
                "happy": "positive",
                "sad": "negative",
                "angry": "negative",
                "surprised": "positive",
                "neutral": "neutral",
            }

            classification = expression_to_mood.get(expression.expression_type, "neutral")

            return Mood(
                timestamp=datetime.now(),
                classification=classification,
                confidence=expression.confidence,
                facial_expression=expression.expression_type
            )

        except Exception as e:
            self.logger.warning(f"Facial expression analysis failed: {e}")
            return None

    def _combine_mood_signals(self, voice_mood: Optional[Mood], 
                             facial_mood: Optional[Mood]) -> Mood:
        """Combine voice and facial mood signals.
        
        Args:
            voice_mood: Mood from voice analysis
            facial_mood: Mood from facial analysis
            
        Returns:
            Combined mood classification
        """
        if voice_mood and facial_mood:
            # Both signals available
            if voice_mood.classification == facial_mood.classification:
                # Signals agree
                combined_confidence = (voice_mood.confidence + facial_mood.confidence) / 2
                return Mood(
                    timestamp=datetime.now(),
                    classification=voice_mood.classification,
                    confidence=combined_confidence,
                    voice_tone=voice_mood.voice_tone,
                    facial_expression=facial_mood.facial_expression
                )
            else:
                # Signals conflict - classify as mixed
                return Mood(
                    timestamp=datetime.now(),
                    classification="mixed",
                    confidence=0.5,
                    voice_tone=voice_mood.voice_tone,
                    facial_expression=facial_mood.facial_expression
                )
        elif voice_mood:
            return voice_mood
        elif facial_mood:
            return facial_mood
        else:
            # No signals - default to neutral
            return Mood(
                timestamp=datetime.now(),
                classification="neutral",
                confidence=0.0
            )

    def get_mood_history(self, user_id: str = "", period: str = "session") -> List[Mood]:
        """Get mood history for period.
        
        Args:
            user_id: User ID (for future database queries)
            period: Time period ("session", "day", "week", "month")
            
        Returns:
            List of moods in period
        """
        # For now, return session history
        return self.mood_history

    def generate_mood_report(self, user_id: str = "", period: str = "session") -> MoodSummary:
        """Generate mood report for period.
        
        Args:
            user_id: User ID
            period: Time period
            
        Returns:
            Mood summary report
        """
        try:
            moods = self.get_mood_history(user_id, period)

            if not moods:
                return MoodSummary(
                    session_id="",
                    primary_mood="neutral",
                    mood_transitions=[],
                    average_confidence=0.0,
                    mood_stability=1.0
                )

            # Calculate statistics
            mood_counts = {}
            total_confidence = 0.0

            for mood in moods:
                mood_counts[mood.classification] = mood_counts.get(mood.classification, 0) + 1
                total_confidence += mood.confidence

            # Primary mood is most frequent
            primary_mood = max(mood_counts, key=mood_counts.get)
            average_confidence = total_confidence / len(moods) if moods else 0.0

            # Calculate mood stability (how consistent moods are)
            mood_stability = self._calculate_mood_stability(moods)

            return MoodSummary(
                session_id="",
                primary_mood=primary_mood,
                mood_transitions=moods,
                average_confidence=average_confidence,
                mood_stability=mood_stability
            )

        except Exception as e:
            self.logger.error(f"Mood report generation failed: {e}")
            return MoodSummary(
                session_id="",
                primary_mood="neutral",
                mood_transitions=[],
                average_confidence=0.0,
                mood_stability=0.0
            )

    def _calculate_mood_stability(self, moods: List[Mood]) -> float:
        """Calculate mood stability (consistency).
        
        Args:
            moods: List of moods
            
        Returns:
            Stability score (0.0-1.0, higher = more stable)
        """
        if len(moods) < 2:
            return 1.0

        # Count transitions between different moods
        transitions = 0
        for i in range(1, len(moods)):
            if moods[i].classification != moods[i-1].classification:
                transitions += 1

        # Stability = 1 - (transitions / total_transitions_possible)
        max_transitions = len(moods) - 1
        stability = 1.0 - (transitions / max_transitions) if max_transitions > 0 else 1.0

        return max(0.0, min(1.0, stability))

    def correlate_mood_with_topics(self, user_id: str = "") -> Dict[str, float]:
        """Correlate mood with conversation topics.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary mapping topics to mood correlation scores
        """
        # Mock implementation - would analyze actual conversations
        return {
            "work": 0.3,
            "family": 0.7,
            "hobbies": 0.8,
            "health": 0.5,
        }

    def clear_history(self) -> None:
        """Clear mood history."""
        self.mood_history.clear()
        self.logger.info("Mood history cleared")

    def get_model_info(self) -> dict:
        """Get information about mood analysis engine.
        
        Returns:
            Dictionary with engine information
        """
        return {
            "mood_history_size": len(self.mood_history),
            "current_mood": self.mood_history[-1].classification if self.mood_history else "unknown"
        }
