"""
Voice Transcription - No FFmpeg Required
Uses scipy to load WAV files directly
"""

import sys
import os
from pathlib import Path
import numpy as np

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


def load_wav_file(filename):
    """Load WAV file using scipy."""
    try:
        from scipy.io import wavfile
        
        sample_rate, audio_data = wavfile.read(filename)
        
        # Convert to float32 and normalize
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        elif audio_data.dtype == np.int32:
            audio_data = audio_data.astype(np.float32) / 2147483648.0
        
        # If stereo, convert to mono
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        print(f"✓ Loaded {filename}")
        print(f"  Sample rate: {sample_rate} Hz")
        print(f"  Duration: {len(audio_data) / sample_rate:.2f} seconds")
        print(f"  Samples: {len(audio_data):,}")
        
        return audio_data, sample_rate
        
    except ImportError:
        print("✗ scipy not installed")
        print("   Install with: pip install scipy")
        return None, None
    except Exception as e:
        print(f"✗ Error loading audio: {e}")
        return None, None


def transcribe_with_whisper(audio_data, sample_rate):
    """Transcribe audio using Whisper."""
    try:
        import whisper
        
        print(f"\n🔄 Loading Whisper model...")
        model = whisper.load_model("base")
        
        print(f"🔄 Transcribing audio...")
        
        # Resample to 16000 Hz if needed
        if sample_rate != 16000:
            print(f"   Resampling from {sample_rate} Hz to 16000 Hz...")
            from scipy import signal
            num_samples = int(len(audio_data) * 16000 / sample_rate)
            audio_data = signal.resample(audio_data, num_samples)
            sample_rate = 16000
        
        # Transcribe
        result = model.transcribe(audio_data, language="en")
        
        text = result["text"].strip()
        
        print(f"✓ Transcription complete")
        
        return text, result
        
    except ImportError:
        print("✗ Whisper not installed")
        print("   Install with: pip install openai-whisper")
        return None, None
    except Exception as e:
        print(f"✗ Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def analyze_text(text):
    """Analyze transcribed text."""
    if not text:
        return None
    
    analysis = {
        "text": text,
        "length": len(text),
        "words": len(text.split()),
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


def test_transcription():
    """Test voice transcription."""
    
    print_header("VOICE TRANSCRIPTION TEST (No FFmpeg)")
    print("\nThis test will:")
    print("  1. Find audio files in 'audio_samples' folder")
    print("  2. Load WAV file using scipy")
    print("  3. Transcribe using Whisper")
    print("  4. Analyze the text")
    
    try:
        # Check scipy
        print_section("Checking Dependencies")
        try:
            from scipy.io import wavfile
            print("✓ scipy is installed")
        except ImportError:
            print("✗ scipy not installed")
            print("   Install with: pip install scipy")
            return
        
        try:
            import whisper
            print("✓ Whisper is installed")
        except ImportError:
            print("✗ Whisper not installed")
            print("   Install with: pip install openai-whisper")
            return
        
        # Find audio files
        print_section("Finding Audio Files")
        
        audio_dir = Path("audio_samples")
        audio_dir.mkdir(exist_ok=True)
        
        audio_files = list(audio_dir.glob("*.wav")) + list(audio_dir.glob("*.mp3"))
        
        if not audio_files:
            print("No audio files found in 'audio_samples' folder")
            print(f"\nAudio folder: {audio_dir.absolute()}")
            return
        
        print(f"Found {len(audio_files)} audio file(s):")
        for i, f in enumerate(audio_files, 1):
            size = os.path.getsize(f) / 1024
            print(f"  {i}. {f.name} ({size:.1f} KB)")
        
        # Process first audio file
        audio_file = audio_files[0]
        
        print_section("Loading Audio")
        audio_data, sample_rate = load_wav_file(str(audio_file))
        
        if audio_data is None:
            return
        
        # Transcribe
        print_section("Transcription")
        text, result = transcribe_with_whisper(audio_data, sample_rate)
        
        if not text:
            return
        
        # Display result
        print(f"\n📝 You said:")
        print(f"   \"{text}\"")
        
        # Analyze
        print_section("Analysis")
        analysis = analyze_text(text)
        
        if analysis:
            print(f"\nText Statistics:")
            print(f"  Characters: {analysis['length']}")
            print(f"  Words: {analysis['words']}")
            
            print(f"\nKeyword Detection:")
            found_keywords = [k for k, v in analysis['keywords'].items() if v]
            if found_keywords:
                for keyword in found_keywords:
                    print(f"  ✓ {keyword}")
            else:
                print("  (No keywords detected)")
        
        # Show Whisper details
        if result:
            print_section("Whisper Details")
            if "language" in result:
                print(f"Language: {result['language']}")
            if "duration" in result:
                print(f"Duration: {result['duration']:.2f}s")
        
        print_header("TRANSCRIPTION COMPLETE")
        print("\n✓ Successfully transcribed your voice!")
        
    except Exception as e:
        print_header("ERROR")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_transcription()
