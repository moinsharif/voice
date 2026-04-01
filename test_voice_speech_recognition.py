"""
Voice Speech Recognition Test
Captures voice and transcribes what you said using Whisper
"""

import sys
import os
import time
import numpy as np
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import VaskApplication


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text):
    """Print formatted section."""
    print(f"\n>>> {text}")
    print("-" * 70)


def record_audio(duration_seconds=5):
    """Record audio from microphone.
    
    Args:
        duration_seconds: Duration to record
        
    Returns:
        Tuple of (audio_data, sample_rate) or (None, None) if failed
    """
    try:
        import pyaudio
        import wave
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        p = pyaudio.PyAudio()
        
        print(f"\n🎤 Recording for {duration_seconds} seconds...")
        print("   Speak now! (e.g., say 'hello')")
        
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
            frames.append(data)
            # Show progress
            progress = int((i / (RATE / CHUNK * duration_seconds)) * 20)
            print(f"   [{progress:20s}] {i * CHUNK / RATE:.1f}s", end='\r')
        
        print()  # New line
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Convert to numpy array
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        
        print(f"✓ Recorded {len(audio_data)} samples at {RATE}Hz")
        
        return audio_data, RATE
        
    except ImportError:
        print("⚠ PyAudio not installed. Cannot record audio.")
        return None, None
    except Exception as e:
        print(f"⚠ Failed to record audio: {e}")
        return None, None


def save_audio_file(audio_data, sample_rate, filename="temp_audio.wav"):
    """Save audio to WAV file.
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate
        filename: Output filename
        
    Returns:
        Path to saved file or None
    """
    try:
        import wave
        
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        print(f"✓ Audio saved to {filename}")
        return filename
        
    except Exception as e:
        print(f"⚠ Failed to save audio: {e}")
        return None


def transcribe_audio(audio_file):
    """Transcribe audio using Whisper.
    
    Args:
        audio_file: Path to audio file
        
    Returns:
        Transcribed text or None
    """
    try:
        import whisper
        
        print(f"\n🔄 Transcribing audio using Whisper...")
        print("   (This may take a moment on first run)")
        
        model = whisper.load_model("base")
        result = model.transcribe(audio_file, language="en")
        
        text = result["text"].strip()
        confidence = result.get("confidence", 0)
        
        print(f"✓ Transcription complete")
        
        return text, result
        
    except ImportError:
        print("⚠ Whisper not installed. Install with: pip install openai-whisper")
        return None, None
    except Exception as e:
        print(f"⚠ Failed to transcribe: {e}")
        return None, None


def analyze_transcription(text):
    """Analyze the transcribed text.
    
    Args:
        text: Transcribed text
        
    Returns:
        Dictionary with analysis
    """
    if not text:
        return None
    
    analysis = {
        "text": text,
        "length": len(text),
        "word_count": len(text.split()),
        "lowercase": text.lower(),
        "contains_hello": "hello" in text.lower(),
        "contains_hi": "hi" in text.lower(),
        "contains_bye": "bye" in text.lower(),
        "contains_thanks": "thank" in text.lower(),
    }
    
    return analysis


def test_speech_recognition():
    """Test speech recognition with real voice input."""
    
    print_header("VASK SPEECH RECOGNITION TEST")
    print("\nThis test will:")
    print("  1. Record your voice from microphone")
    print("  2. Transcribe what you said using Whisper")
    print("  3. Analyze the transcription")
    print("  4. Generate a response")
    
    try:
        # Initialize application
        print_section("Initializing Vask Application")
        app = VaskApplication()
        app.start()
        print("✓ Application initialized")
        
        # Start session
        user_id = "speech_test_user"
        print_section(f"Starting Session")
        if app.start_session(user_id):
            print(f"✓ Session started for {user_id}")
        else:
            print("✗ Failed to start session")
            return
        
        # Record audio
        print_section("Voice Recording")
        audio_data, sample_rate = record_audio(duration_seconds=5)
        
        if audio_data is None:
            print("Cannot proceed without audio recording")
            return
        
        # Save audio file
        audio_file = save_audio_file(audio_data, sample_rate)
        if not audio_file:
            print("Cannot proceed without saving audio")
            return
        
        # Transcribe
        print_section("Speech Transcription")
        text, result = transcribe_audio(audio_file)
        
        if not text:
            print("Cannot proceed without transcription")
            return
        
        print(f"\n📝 What you said:")
        print(f"   \"{text}\"")
        
        # Analyze
        print_section("Transcription Analysis")
        analysis = analyze_transcription(text)
        
        if analysis:
            print(f"Text Length: {analysis['length']} characters")
            print(f"Word Count: {analysis['word_count']} words")
            print(f"\nKeyword Detection:")
            print(f"  Contains 'hello': {analysis['contains_hello']}")
            print(f"  Contains 'hi': {analysis['contains_hi']}")
            print(f"  Contains 'bye': {analysis['contains_bye']}")
            print(f"  Contains 'thanks': {analysis['contains_thanks']}")
        
        # Generate response
        print_section("AI Response Generation")
        
        # Simple response logic
        text_lower = text.lower()
        
        if "hello" in text_lower or "hi" in text_lower:
            response = "Hello! Nice to meet you. How can I help you today?"
            print(f"🤖 AI: {response}")
        elif "bye" in text_lower or "goodbye" in text_lower:
            response = "Goodbye! Have a great day!"
            print(f"🤖 AI: {response}")
        elif "thanks" in text_lower or "thank you" in text_lower:
            response = "You're welcome! Happy to help."
            print(f"🤖 AI: {response}")
        else:
            response = f"You said: '{text}'. That's interesting! Tell me more."
            print(f"🤖 AI: {response}")
        
        # Text-to-speech (optional)
        print_section("Text-to-Speech Output")
        if app.tts_engine:
            try:
                print("🔊 Converting response to speech...")
                audio_bytes = app.tts_engine.synthesize(response)
                if audio_bytes:
                    print("✓ Speech synthesis complete")
                    print("   (Audio would be played here)")
                else:
                    print("⚠ Speech synthesis failed")
            except Exception as e:
                print(f"⚠ TTS error: {e}")
        
        # End session
        print_section("Session Summary")
        if app.end_session():
            print("✓ Session ended successfully")
        
        app.stop()
        
        # Cleanup
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"✓ Cleaned up temporary audio file")
        
        print_header("TEST COMPLETED SUCCESSFULLY")
        print("\nWhat happened:")
        print(f"  1. ✓ Recorded your voice")
        print(f"  2. ✓ Transcribed: \"{text}\"")
        print(f"  3. ✓ Analyzed the text")
        print(f"  4. ✓ Generated response: \"{response}\"")
        
    except Exception as e:
        print_header("ERROR OCCURRED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_speech_recognition()
