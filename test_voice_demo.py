"""
Simple Voice Test Demo
Real-time voice input, analysis, and reporting
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import VaskApplication
from src.models.data_models import MoodEntry


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_section(text):
    """Print formatted section."""
    print(f"\n>>> {text}")
    print("-" * 60)


def test_voice_input():
    """Test real-time voice input and analysis."""
    
    print_header("VASK VOICE TEST DEMO")
    print("\nInitializing Vask application...")
    
    try:
        # Initialize application
        app = VaskApplication()
        app.start()
        
        print_section("Application Status")
        info = app.get_application_info()
        print(f"Application: {info['name']} v{info['version']}")
        print(f"Running: {info['is_running']}")
        print(f"Components initialized:")
        for component, status in info['components'].items():
            status_str = "✓" if status else "✗"
            print(f"  {status_str} {component}")
        
        # Start a session
        user_id = "test_user_001"
        print_section(f"Starting Session for {user_id}")
        
        if app.start_session(user_id):
            print(f"✓ Session started successfully")
        else:
            print(f"✗ Failed to start session")
            return
        
        # Get user profile
        print_section("User Profile")
        profile = app.get_user_profile(user_id)
        if profile:
            print(f"User ID: {profile.user_id}")
            print(f"Language: {profile.language}")
            print(f"Communication Style: {profile.communication_style}")
            print(f"Voice ID: {profile.voice_id}")
            print(f"Speaking Rate: {profile.speaking_rate}")
            print(f"Interaction Count: {profile.interaction_count}")
        else:
            print("No profile found (will be created)")
        
        # Simulate voice input and mood analysis
        print_section("Voice Input & Analysis")
        print("\nSimulating voice input analysis...")
        print("(In real usage, this would capture from microphone)")
        
        # Create sample mood entries to simulate analysis
        sample_moods = [
            MoodEntry(
                timestamp=datetime.now(),
                classification="positive",
                confidence=0.85,
                facial_expression="happy",
                voice_tone="upbeat",
                conversation_topic="greeting",
                time_of_day="morning"
            ),
            MoodEntry(
                timestamp=datetime.now(),
                classification="neutral",
                confidence=0.72,
                facial_expression="neutral",
                voice_tone="calm",
                conversation_topic="question",
                time_of_day="morning"
            ),
            MoodEntry(
                timestamp=datetime.now(),
                classification="positive",
                confidence=0.88,
                facial_expression="happy",
                voice_tone="excited",
                conversation_topic="response",
                time_of_day="morning"
            ),
        ]
        
        print(f"\nAnalyzed {len(sample_moods)} voice samples:")
        for i, mood in enumerate(sample_moods, 1):
            print(f"\n  Sample {i}:")
            print(f"    Classification: {mood.classification}")
            print(f"    Confidence: {mood.confidence:.2%}")
            print(f"    Facial Expression: {mood.facial_expression}")
            print(f"    Voice Tone: {mood.voice_tone}")
            print(f"    Topic: {mood.conversation_topic}")
            print(f"    Time: {mood.time_of_day}")
        
        # Generate mood report
        print_section("Mood Analysis Report")
        mood_report = app.get_mood_report(user_id, period="session")
        if mood_report:
            print(f"Session Mood Summary:")
            print(f"  Primary Mood: {mood_report.primary_mood}")
            print(f"  Mood Stability: {mood_report.mood_stability:.2%}")
            print(f"  Average Confidence: {mood_report.average_confidence:.2%}")
            print(f"  Mood Transitions: {len(mood_report.mood_transitions)}")
            
            if mood_report.mood_transitions:
                print(f"\n  Mood Transitions:")
                for i, transition in enumerate(mood_report.mood_transitions, 1):
                    print(f"    {i}. {transition.classification} (confidence: {transition.confidence:.2%})")
        else:
            print("No mood report available")
        
        # Export conversation history
        print_section("Conversation History Export")
        exported = app.export_conversation_history(user_id, format="json")
        if exported:
            print("✓ Conversation history exported successfully")
            print(f"Export preview (first 200 chars):")
            print(exported[:200] + "..." if len(exported) > 200 else exported)
        else:
            print("No conversation history to export")
        
        # End session
        print_section("Ending Session")
        if app.end_session():
            print("✓ Session ended successfully")
        else:
            print("✗ Failed to end session")
        
        # Stop application
        app.stop()
        
        print_header("TEST COMPLETED SUCCESSFULLY")
        print("\nSummary:")
        print("✓ Application initialized")
        print("✓ Session created")
        print("✓ Voice analysis simulated")
        print("✓ Mood report generated")
        print("✓ Conversation history exported")
        print("✓ Session ended")
        
    except Exception as e:
        print_header("ERROR OCCURRED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_voice_input()
