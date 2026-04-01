"""Tests for analysis modules."""

import pytest
import numpy as np
from datetime import datetime
from src.analysis.mood_analysis import MoodAnalysisEngine
from src.models.data_models import Expression, Mood


class TestMoodAnalysisEngine:
    """Tests for MoodAnalysisEngine."""

    def test_initialization(self):
        """Test mood engine initialization."""
        engine = MoodAnalysisEngine()
        assert len(engine.mood_history) == 0

    def test_analyze_mood_default(self):
        """Test mood analysis with no input."""
        engine = MoodAnalysisEngine()
        
        mood = engine.analyze_mood()
        assert mood is not None
        assert mood.classification == "neutral"

    def test_analyze_mood_with_voice(self):
        """Test mood analysis with voice data."""
        engine = MoodAnalysisEngine()
        
        # Create dummy audio data
        audio_data = np.random.randn(16000).astype(np.float32).tobytes()
        
        mood = engine.analyze_mood(audio_data=audio_data)
        assert mood is not None
        assert mood.classification in ["positive", "neutral", "negative"]

    def test_analyze_mood_with_expression(self):
        """Test mood analysis with facial expression."""
        engine = MoodAnalysisEngine()
        
        expression = Expression(
            expression_type="happy",
            confidence=0.9,
            intensity=0.8
        )
        
        mood = engine.analyze_mood(expression=expression)
        assert mood is not None
        assert mood.classification == "positive"

    def test_mood_history(self):
        """Test mood history tracking."""
        engine = MoodAnalysisEngine()
        
        for i in range(5):
            mood = engine.analyze_mood()
            assert len(engine.mood_history) == i + 1

    def test_generate_mood_report(self):
        """Test mood report generation."""
        engine = MoodAnalysisEngine()
        
        # Add some moods
        for _ in range(3):
            engine.analyze_mood()
        
        report = engine.generate_mood_report()
        assert report is not None
        assert report.primary_mood == "neutral"
        assert len(report.mood_transitions) == 3

    def test_mood_stability_calculation(self):
        """Test mood stability calculation."""
        engine = MoodAnalysisEngine()
        
        # Create consistent moods
        moods = [
            Mood(datetime.now(), "positive", 0.8),
            Mood(datetime.now(), "positive", 0.8),
            Mood(datetime.now(), "positive", 0.8),
        ]
        
        stability = engine._calculate_mood_stability(moods)
        assert stability == 1.0  # All same mood = stable

    def test_mood_stability_with_transitions(self):
        """Test mood stability with transitions."""
        engine = MoodAnalysisEngine()
        
        # Create alternating moods
        moods = [
            Mood(datetime.now(), "positive", 0.8),
            Mood(datetime.now(), "negative", 0.8),
            Mood(datetime.now(), "positive", 0.8),
        ]
        
        stability = engine._calculate_mood_stability(moods)
        assert stability < 1.0  # Transitions = less stable

    def test_correlate_mood_with_topics(self):
        """Test mood-topic correlation."""
        engine = MoodAnalysisEngine()
        
        correlations = engine.correlate_mood_with_topics()
        assert isinstance(correlations, dict)
        assert len(correlations) > 0

    def test_clear_history(self):
        """Test clearing mood history."""
        engine = MoodAnalysisEngine()
        
        engine.analyze_mood()
        assert len(engine.mood_history) > 0
        
        engine.clear_history()
        assert len(engine.mood_history) == 0

    def test_combine_mood_signals_agreement(self):
        """Test combining agreeing mood signals."""
        engine = MoodAnalysisEngine()
        
        voice_mood = Mood(datetime.now(), "positive", 0.8, voice_tone="upbeat")
        facial_mood = Mood(datetime.now(), "positive", 0.9, facial_expression="happy")
        
        combined = engine._combine_mood_signals(voice_mood, facial_mood)
        assert combined.classification == "positive"

    def test_combine_mood_signals_conflict(self):
        """Test combining conflicting mood signals."""
        engine = MoodAnalysisEngine()
        
        voice_mood = Mood(datetime.now(), "positive", 0.8, voice_tone="upbeat")
        facial_mood = Mood(datetime.now(), "negative", 0.9, facial_expression="sad")
        
        combined = engine._combine_mood_signals(voice_mood, facial_mood)
        assert combined.classification == "mixed"
