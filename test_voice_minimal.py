"""
Minimal Voice Test - No external audio libraries
Just uses Whisper for transcription
"""

import sys
import os
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


def test_whisper_only():
    """Test Whisper transcription only."""
    
    print_header("WHISPER TRANSCRIPTION TEST")
    print("\nThis test will:")
    print("  1. Check if Whisper is installed")
    print("  2. List available audio files")
    print("  3. Transcribe any WAV file you provide")
    
    try:
        # Check Whisper
        print_section("Checking Whisper Installation")
        try:
            import whisper
            print("✓ Whisper is installed")
        except ImportError:
            print("✗ Whisper not installed")
            print("   Install with: pip install openai-whisper")
            return
        
        # List audio files
        print_section("Available Audio Files")
        
        # Create audio_samples directory if it doesn't exist
        audio_dir = Path("audio_samples")
        audio_dir.mkdir(exist_ok=True)
        
        audio_files = list(audio_dir.glob("*.wav")) + list(audio_dir.glob("*.mp3"))
        
        if audio_files:
            print(f"Found {len(audio_files)} audio files in 'audio_samples' folder:")
            for i, f in enumerate(audio_files, 1):
                size = os.path.getsize(f) / 1024 / 1024
                print(f"  {i}. {f.name} ({size:.2f} MB)")
        else:
            print("No audio files found in 'audio_samples' folder")
            print(f"\nAudio folder location:")
            print(f"  {audio_dir.absolute()}")
            print("\nTo test:")
            print("  1. Record audio using Windows Sound Recorder")
            print("  2. Save as WAV file in the 'audio_samples' folder")
            print("  3. Run this script again")
            return
        
        # Transcribe
        print_section("Transcription")
        
        if audio_files:
            audio_file = audio_files[0]
            print(f"\nTranscribing: {audio_file.name}")
            
            model = whisper.load_model("base")
            result = model.transcribe(str(audio_file), language="en")
            
            text = result["text"].strip()
            
            print(f"\n📝 Transcription Result:")
            print(f"   \"{text}\"")
            
            # Analysis
            print_section("Analysis")
            
            text_lower = text.lower()
            
            print(f"\nText Statistics:")
            print(f"  Characters: {len(text)}")
            print(f"  Words: {len(text.split())}")
            
            print(f"\nKeyword Detection:")
            keywords = ["hello", "hi", "bye", "goodbye", "thanks", "yes", "no", "help"]
            for keyword in keywords:
                if keyword in text_lower:
                    print(f"  ✓ {keyword}")
            
            if result.get("language"):
                print(f"\nDetected Language: {result['language']}")
            
            print_header("TRANSCRIPTION COMPLETE")
            
    except Exception as e:
        print_header("ERROR")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def manual_record_instructions():
    """Show instructions for manual recording."""
    
    print_header("MANUAL RECORDING INSTRUCTIONS")
    
    print("\nSince PyAudio is blocked, use Windows built-in recorder:")
    print("\n1. Open Sound Recorder:")
    print("   - Press Windows + R")
    print("   - Type: soundrecorder")
    print("   - Press Enter")
    print("\n2. Click 'Start Recording'")
    print("\n3. Speak your message (e.g., 'hello')")
    print("\n4. Click 'Stop Recording'")
    print("\n5. Save as WAV file in this directory")
    print("\n6. Run this script again to transcribe")
    
    print("\nOr use any other audio recorder:")
    print("  - Audacity (free)")
    print("  - OBS Studio (free)")
    print("  - Any online recorder")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  VOICE TEST - MINIMAL VERSION")
    print("="*70)
    
    print("\nOptions:")
    print("  1. Test Whisper transcription (if you have audio files)")
    print("  2. Get recording instructions")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_whisper_only()
    elif choice == "2":
        manual_record_instructions()
    else:
        print("Invalid choice")
