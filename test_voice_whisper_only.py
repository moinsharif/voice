"""
Voice Test using Whisper directly
Records audio and transcribes using Whisper
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text):
    """Print formatted section."""
    print(f"\n>>> {text}")
    print("-" * 70)


def record_with_pyaudio(duration_seconds=5):
    """Record audio using PyAudio."""
    try:
        import pyaudio
        import numpy as np
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        p = pyaudio.PyAudio()
        
        print(f"\n🎤 Recording for {duration_seconds} seconds...")
        print("   Speak now!")
        
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
            progress = int((i / (RATE / CHUNK * duration_seconds)) * 20)
            print(f"   [{progress:20s}] {i * CHUNK / RATE:.1f}s", end='\r')
        
        print()
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        print(f"✓ Recorded {len(audio_data)} samples at {RATE}Hz")
        
        return audio_data, RATE
        
    except Exception as e:
        print(f"✗ Recording error: {e}")
        return None, None


def save_wav(audio_data, sample_rate, filename):
    """Save audio as WAV file."""
    try:
        import wave
        
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        file_size = os.path.getsize(filename)
        print(f"✓ Saved to {filename} ({file_size} bytes)")
        return filename
        
    except Exception as e:
        print(f"✗ Save error: {e}")
        return None


def transcribe_with_whisper(audio_file):
    """Transcribe using Whisper."""
    try:
        import whisper
        
        print(f"\n🔄 Loading Whisper model...")
        model = whisper.load_model("base")
        
        print(f"🔄 Transcribing audio...")
        result = model.transcribe(audio_file, language="en")
        
        text = result["text"].strip()
        
        print(f"✓ Transcription complete")
        
        return text, result
        
    except ImportError:
        print("✗ Whisper not installed")
        print("   Install with: pip install openai-whisper")
        return None, None
    except Exception as e:
        print(f"✗ Transcription error: {e}")
        return None, None


def analyze_text(text):
    """Analyze transcribed text."""
    if not text:
        return None
    
    analysis = {
        "text": text,
        "length": len(text),
        "words": len(text.split()),
        "sentences": len(text.split('.')),
    }
    
    # Keyword detection
    text_lower = text.lower()
    keywords = {
        "hello": "hello" in text_lower,
        "hi": "hi" in text_lower,
        "bye": "bye" in text_lower or "goodbye" in text_lower,
        "thanks": "thank" in text_lower or "thank you" in text_lower,
        "yes": "yes" in text_lower,
        "no": "no" in text_lower,
        "help": "help" in text_lower,
        "please": "please" in text_lower,
    }
    
    analysis["keywords"] = keywords
    
    return analysis


def test_whisper():
    """Test voice recording and Whisper transcription."""
    
    print_header("VOICE TRANSCRIPTION TEST")
    print("\nThis will:")
    print("  1. Record your voice (5 seconds)")
    print("  2. Save as WAV file")
    print("  3. Transcribe using Whisper")
    print("  4. Analyze the text")
    
    try:
        # Record
        print_section("Step 1: Recording")
        audio_data, sample_rate = record_with_pyaudio(duration_seconds=5)
        
        if audio_data is None:
            print("Cannot proceed without recording")
            return
        
        # Save
        print_section("Step 2: Saving")
        filename = "voice_recording.wav"
        if not save_wav(audio_data, sample_rate, filename):
            print("Cannot proceed without saving")
            return
        
        # Transcribe
        print_section("Step 3: Transcription")
        text, result = transcribe_with_whisper(filename)
        
        if not text:
            print("Cannot proceed without transcription")
            return
        
        # Display result
        print_section("Step 4: Results")
        print(f"\n📝 You said:")
        print(f"   \"{text}\"")
        
        # Analyze
        print_section("Step 5: Analysis")
        analysis = analyze_text(text)
        
        if analysis:
            print(f"\nText Statistics:")
            print(f"  Length: {analysis['length']} characters")
            print(f"  Words: {analysis['words']}")
            print(f"  Sentences: {analysis['sentences']}")
            
            print(f"\nKeyword Detection:")
            for keyword, found in analysis['keywords'].items():
                status = "✓ FOUND" if found else "✗ NOT FOUND"
                print(f"  {keyword:10s}: {status}")
        
        # Show Whisper details
        if result:
            print_section("Whisper Details")
            if "language" in result:
                print(f"Language: {result['language']}")
            if "duration" in result:
                print(f"Duration: {result['duration']:.2f}s")
        
        # Cleanup
        print_section("Cleanup")
        if os.path.exists(filename):
            os.remove(filename)
            print(f"✓ Deleted {filename}")
        
        print_header("TEST COMPLETED")
        print("\n✓ Successfully recorded and transcribed your voice!")
        
    except Exception as e:
        print_header("ERROR")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_whisper()
