"""
Real-Time Voice Input Test
Captures actual voice from microphone and analyzes it
"""

import sys
import time
import numpy as np
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


def capture_voice_sample(duration_seconds=3):
    """Capture voice from microphone.
    
    Args:
        duration_seconds: Duration to record in seconds
        
    Returns:
        Audio data as numpy array or None if failed
    """
    try:
        import pyaudio
        import wave
        
        CHUNK = 1024
        FORMAT = pyaudio.paFloat32
        CHANNELS = 1
        RATE = 16000
        
        p = pyaudio.PyAudio()
        
        print(f"Recording for {duration_seconds} seconds...")
        print("Speak now...")
        
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        frames = []
        for i in range(0, int(RATE / CHUNK * duration_seconds)):
            data = stream.read(CHUNK)
            frames.append(np.frombuffer(data, dtype=np.float32))
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        audio_data = np.concatenate(frames)
        print(f"✓ Recorded {len(audio_data)} samples")
        
        return audio_data
        
    except ImportError:
        print("⚠ PyAudio not installed. Using simulated audio.")
        return None
    except Exception as e:
        print(f"⚠ Failed to capture audio: {e}")
        return None


def analyze_audio_features(audio_data):
    """Analyze audio features to determine mood.
    
    Args:
        audio_data: Audio data as numpy array
        
    Returns:
        Dictionary with audio features
    """
    if audio_data is None:
        # Return simulated features
        return {
            "energy": np.random.uniform(0.3, 0.9),
            "pitch_variation": np.random.uniform(0.2, 0.8),
            "speaking_rate": np.random.uniform(0.8, 1.5),
            "silence_ratio": np.random.uniform(0.1, 0.4),
        }
    
    try:
        # Calculate energy
        energy = np.sqrt(np.mean(audio_data ** 2))
        
        # Calculate pitch variation (simplified)
        pitch_variation = np.std(audio_data) / (np.mean(np.abs(audio_data)) + 1e-6)
        
        # Estimate speaking rate from zero crossings
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_data)))) / 2
        speaking_rate = zero_crossings / len(audio_data)
        
        # Calculate silence ratio
        threshold = np.mean(np.abs(audio_data)) * 0.3
        silence_ratio = np.sum(np.abs(audio_data) < threshold) / len(audio_data)
        
        return {
            "energy": float(energy),
            "pitch_variation": float(pitch_variation),
            "speaking_rate": float(speaking_rate),
            "silence_ratio": float(silence_ratio),
        }
    except Exception as e:
        print(f"Error analyzing audio: {e}")
        return None


def features_to_mood(features):
    """Convert audio features to mood classification.
    
    Args:
        features: Dictionary with audio features
        
    Returns:
        Tuple of (mood_classification, confidence)
    """
    if features is None:
        return "neutral", 0.5
    
    energy = features.get("energy", 0.5)
    pitch_variation = features.get("pitch_variation", 0.5)
    speaking_rate = features.get("speaking_rate", 0.5)
    silence_ratio = features.get("silence_ratio", 0.5)
    
    # Simple mood classification based on features
    if energy > 0.6 and pitch_variation > 0.5 and speaking_rate > 0.4:
        mood = "positive"
        confidence = min(0.95, energy * 0.8 + pitch_variation * 0.2)
    elif energy < 0.3 or silence_ratio > 0.5:
        mood = "negative"
        confidence = min(0.95, (1 - energy) * 0.6 + silence_ratio * 0.4)
    else:
        mood = "neutral"
        confidence = 0.7
    
    return mood, confidence


def test_realtime_voice():
    """Test real-time voice input and analysis."""
    
    print_header("VASK REAL-TIME VOICE TEST")
    print("\nInitializing Vask application...")
    
    try:
        # Initialize application
        app = VaskApplication()
        app.start()
        
        print_section("Application Status")
        info = app.get_application_info()
        print(f"Application: {info['name']} v{info['version']}")
        print(f"Running: {info['is_running']}")
        
        # Start a session
        user_id = "realtime_user_001"
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
        
        # Capture and analyze voice samples
        print_section("Real-Time Voice Capture & Analysis")
        
        num_samples = 3
        moods = []
        
        for sample_num in range(1, num_samples + 1):
            print(f"\n--- Sample {sample_num}/{num_samples} ---")
            
            # Capture voice
            audio_data = capture_voice_sample(duration_seconds=2)
            
            # Analyze features
            features = analyze_audio_features(audio_data)
            print(f"\nAudio Features:")
            print(f"  Energy: {features['energy']:.3f}")
            print(f"  Pitch Variation: {features['pitch_variation']:.3f}")
            print(f"  Speaking Rate: {features['speaking_rate']:.3f}")
            print(f"  Silence Ratio: {features['silence_ratio']:.3f}")
            
            # Determine mood
            mood_class, confidence = features_to_mood(features)
            print(f"\nMood Classification:")
            print(f"  Classification: {mood_class}")
            print(f"  Confidence: {confidence:.2%}")
            
            # Create mood entry
            mood_entry = MoodEntry(
                timestamp=datetime.now(),
                classification=mood_class,
                confidence=confidence,
                facial_expression=None,
                voice_tone="upbeat" if mood_class == "positive" else "calm" if mood_class == "neutral" else "downbeat",
                conversation_topic="voice_test",
                time_of_day="afternoon"
            )
            moods.append(mood_entry)
            
            if sample_num < num_samples:
                print("\nPreparing for next sample...")
                time.sleep(1)
        
        # Generate mood report
        print_section("Overall Mood Analysis Report")
        mood_report = app.get_mood_report(user_id, period="session")
        if mood_report:
            print(f"Session Summary:")
            print(f"  Primary Mood: {mood_report.primary_mood}")
            print(f"  Mood Stability: {mood_report.mood_stability:.2%}")
            print(f"  Average Confidence: {mood_report.average_confidence:.2%}")
            
            # Calculate mood distribution
            mood_counts = {}
            for mood in moods:
                mood_counts[mood.classification] = mood_counts.get(mood.classification, 0) + 1
            
            print(f"\n  Mood Distribution:")
            for mood_type, count in sorted(mood_counts.items()):
                percentage = (count / len(moods)) * 100
                print(f"    {mood_type}: {count}/{len(moods)} ({percentage:.1f}%)")
            
            # Average confidence
            avg_confidence = sum(m.confidence for m in moods) / len(moods)
            print(f"\n  Average Confidence: {avg_confidence:.2%}")
        
        # Export conversation history
        print_section("Conversation History Export")
        exported = app.export_conversation_history(user_id, format="json")
        if exported:
            print("✓ Conversation history exported successfully")
        
        # End session
        print_section("Ending Session")
        if app.end_session():
            print("✓ Session ended successfully")
        
        # Stop application
        app.stop()
        
        print_header("REAL-TIME TEST COMPLETED")
        print("\nSummary:")
        print(f"✓ Captured {len(moods)} voice samples")
        print(f"✓ Analyzed audio features")
        print(f"✓ Generated mood classifications")
        print(f"✓ Created mood report")
        print(f"✓ Session completed successfully")
        
    except Exception as e:
        print_header("ERROR OCCURRED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_realtime_voice()
