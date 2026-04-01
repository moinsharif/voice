"""
Simple Voice Test - Record and Playback
"""

import sys
import os
import time
import numpy as np
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


def record_audio(duration_seconds=5):
    """Record audio from microphone."""
    try:
        import pyaudio
        
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
        print(f"✓ Recorded {len(audio_data)} samples")
        
        return audio_data, RATE
        
    except Exception as e:
        print(f"✗ Error: {e}")
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
        
        print(f"✓ Saved to {filename}")
        return filename
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def play_wav(filename):
    """Play WAV file using system player."""
    try:
        import subprocess
        import platform
        
        print(f"\n🔊 Playing {filename}...")
        
        system = platform.system()
        
        if system == "Windows":
            # Use Windows Media Player
            os.startfile(filename)
            print("✓ Playing in Windows Media Player")
            time.sleep(2)
        elif system == "Darwin":
            # Use macOS afplay
            subprocess.run(["afplay", filename])
            print("✓ Playback complete")
        else:
            # Use Linux player
            subprocess.run(["aplay", filename])
            print("✓ Playback complete")
            
    except Exception as e:
        print(f"✗ Playback error: {e}")
        print(f"   File saved at: {os.path.abspath(filename)}")
        print(f"   You can manually play it with any audio player")


def transcribe_audio(audio_file):
    """Transcribe audio using Whisper."""
    try:
        import whisper
        
        print(f"\n🔄 Transcribing...")
        
        model = whisper.load_model("base")
        result = model.transcribe(audio_file, language="en")
        
        text = result["text"].strip()
        print(f"✓ Transcription complete")
        
        return text
        
    except ImportError:
        print("⚠ Whisper not installed")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_simple():
    """Simple voice test."""
    
    print_header("SIMPLE VOICE TEST")
    print("\nThis will:")
    print("  1. Record your voice (5 seconds)")
    print("  2. Save it as WAV file")
    print("  3. Play it back")
    print("  4. Transcribe it")
    
    try:
        # Record
        print_section("Recording")
        audio_data, sample_rate = record_audio(duration_seconds=5)
        
        if audio_data is None:
            return
        
        # Save
        print_section("Saving")
        filename = "my_voice.wav"
        if not save_wav(audio_data, sample_rate, filename):
            return
        
        # Play
        print_section("Playback")
        play_wav(filename)
        
        # Transcribe
        print_section("Transcription")
        text = transcribe_audio(filename)
        
        if text:
            print(f"\n📝 You said:")
            print(f"   \"{text}\"")
            
            # Keyword check
            print_section("Analysis")
            text_lower = text.lower()
            
            if "hello" in text_lower:
                print("✓ Detected: HELLO")
            if "hi" in text_lower:
                print("✓ Detected: HI")
            if "bye" in text_lower or "goodbye" in text_lower:
                print("✓ Detected: BYE/GOODBYE")
            if "thanks" in text_lower or "thank you" in text_lower:
                print("✓ Detected: THANKS")
            
            print(f"\nWord count: {len(text.split())}")
            print(f"Character count: {len(text)}")
        
        # Cleanup
        print_section("Cleanup")
        if os.path.exists(filename):
            os.remove(filename)
            print(f"✓ Deleted {filename}")
        
        print_header("DONE")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_simple()
