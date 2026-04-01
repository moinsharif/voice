"""
Voice Debug Test
Records voice, plays it back, and transcribes it
"""

import sys
import os
import time
import numpy as np
from datetime import datetime
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
    """Record audio from microphone.
    
    Args:
        duration_seconds: Duration to record
        
    Returns:
        Tuple of (audio_data, sample_rate) or (None, None) if failed
    """
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
        print("⚠ PyAudio not installed")
        return None, None
    except Exception as e:
        print(f"⚠ Failed to record: {e}")
        return None, None


def play_audio(audio_data, sample_rate):
    """Play audio back.
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate
    """
    try:
        import pyaudio
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        
        p = pyaudio.PyAudio()
        
        print(f"\n🔊 Playing back your voice...")
        
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=sample_rate,
            output=True,
            frames_per_buffer=CHUNK
        )
        
        # Play audio
        audio_bytes = audio_data.tobytes()
        for i in range(0, len(audio_bytes), CHUNK * 2):
            chunk = audio_bytes[i:i + CHUNK * 2]
            stream.write(chunk)
            # Show progress
            progress = int((i / len(audio_bytes)) * 20)
            print(f"   [{progress:20s}] Playing...", end='\r')
        
        print()  # New line
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        print("✓ Playback complete")
        
    except ImportError:
        print("⚠ PyAudio not installed for playback")
    except Exception as e:
        print(f"⚠ Failed to play audio: {e}")


def save_audio_file(audio_data, sample_rate, filename="debug_audio.wav"):
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
        
        print(f"\n🔄 Transcribing audio...")
        
        model = whisper.load_model("base")
        result = model.transcribe(audio_file, language="en")
        
        text = result["text"].strip()
        
        print(f"✓ Transcription complete")
        
        return text, result
        
    except ImportError:
        print("⚠ Whisper not installed")
        return None, None
    except Exception as e:
        print(f"⚠ Failed to transcribe: {e}")
        return None, None


def analyze_audio_waveform(audio_data, sample_rate):
    """Analyze audio waveform.
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate
        
    Returns:
        Dictionary with analysis
    """
    try:
        # Convert to float for analysis
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        # Calculate statistics
        rms_energy = np.sqrt(np.mean(audio_float ** 2))
        peak_amplitude = np.max(np.abs(audio_float))
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_float)))) / 2
        
        # Estimate frequency content (simplified)
        fft = np.abs(np.fft.fft(audio_float))
        freqs = np.fft.fftfreq(len(audio_float), 1/sample_rate)
        
        # Find dominant frequency
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = fft[:len(fft)//2]
        dominant_freq = positive_freqs[np.argmax(positive_fft)]
        
        return {
            "duration_seconds": len(audio_data) / sample_rate,
            "rms_energy": float(rms_energy),
            "peak_amplitude": float(peak_amplitude),
            "zero_crossings": int(zero_crossings),
            "dominant_frequency": float(dominant_freq),
            "sample_count": len(audio_data),
            "sample_rate": sample_rate,
        }
        
    except Exception as e:
        print(f"⚠ Failed to analyze waveform: {e}")
        return None


def test_voice_debug():
    """Test voice recording, playback, and transcription."""
    
    print_header("VOICE DEBUG TEST")
    print("\nThis test will:")
    print("  1. Record your voice")
    print("  2. Play it back (so you can hear it)")
    print("  3. Analyze the waveform")
    print("  4. Transcribe what you said")
    print("  5. Show detailed analysis")
    
    try:
        # Record audio
        print_section("Step 1: Recording Your Voice")
        audio_data, sample_rate = record_audio(duration_seconds=5)
        
        if audio_data is None:
            print("Cannot proceed without audio recording")
            return
        
        # Play back
        print_section("Step 2: Playing Back Your Voice")
        play_audio(audio_data, sample_rate)
        
        # Analyze waveform
        print_section("Step 3: Analyzing Waveform")
        analysis = analyze_audio_waveform(audio_data, sample_rate)
        
        if analysis:
            print(f"\nAudio Statistics:")
            print(f"  Duration: {analysis['duration_seconds']:.2f} seconds")
            print(f"  Sample Count: {analysis['sample_count']:,}")
            print(f"  Sample Rate: {analysis['sample_rate']} Hz")
            print(f"  RMS Energy: {analysis['rms_energy']:.4f}")
            print(f"  Peak Amplitude: {analysis['peak_amplitude']:.4f}")
            print(f"  Zero Crossings: {analysis['zero_crossings']:,}")
            print(f"  Dominant Frequency: {analysis['dominant_frequency']:.2f} Hz")
        
        # Save audio file
        print_section("Step 4: Saving Audio File")
        audio_file = save_audio_file(audio_data, sample_rate)
        if not audio_file:
            print("Cannot proceed without saving audio")
            return
        
        # Transcribe
        print_section("Step 5: Transcribing Audio")
        text, result = transcribe_audio(audio_file)
        
        if not text:
            print("Cannot proceed without transcription")
            return
        
        print(f"\n📝 Transcription Result:")
        print(f"   \"{text}\"")
        
        # Show detailed transcription info
        print_section("Step 6: Detailed Analysis")
        
        print(f"\nTranscription Details:")
        print(f"  Text: \"{text}\"")
        print(f"  Length: {len(text)} characters")
        print(f"  Words: {len(text.split())}")
        
        if result:
            print(f"\nWhisper Model Info:")
            if "language" in result:
                print(f"  Detected Language: {result['language']}")
            if "duration" in result:
                print(f"  Audio Duration: {result['duration']:.2f}s")
        
        # Keyword detection
        print_section("Step 7: Keyword Detection")
        
        text_lower = text.lower()
        keywords = {
            "hello": "hello" in text_lower,
            "hi": "hi" in text_lower,
            "bye": "bye" in text_lower or "goodbye" in text_lower,
            "thanks": "thank" in text_lower,
            "yes": "yes" in text_lower,
            "no": "no" in text_lower,
            "help": "help" in text_lower,
        }
        
        print(f"\nKeyword Detection:")
        for keyword, found in keywords.items():
            status = "✓ FOUND" if found else "✗ NOT FOUND"
            print(f"  {keyword:10s}: {status}")
        
        # Cleanup
        print_section("Cleanup")
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"✓ Cleaned up {audio_file}")
        
        print_header("DEBUG TEST COMPLETED")
        print("\nSummary:")
        print(f"  ✓ Recorded voice for {analysis['duration_seconds']:.2f}s")
        print(f"  ✓ Played back your voice")
        print(f"  ✓ Analyzed waveform")
        print(f"  ✓ Transcribed: \"{text}\"")
        print(f"  ✓ Detected keywords")
        
    except Exception as e:
        print_header("ERROR OCCURRED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_voice_debug()
