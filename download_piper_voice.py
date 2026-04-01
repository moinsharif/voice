#!/usr/bin/env python3
"""
Download Piper TTS voice model
"""

import os
import sys
from pathlib import Path

def download_piper_voice():
    """Download Piper voice model."""
    try:
        print("Downloading Piper voice model...")
        print("This may take a few minutes (~100MB)...\n")
        
        # Create models directory
        models_dir = Path("models/piper")
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Download using piper
        import piper_tts
        from piper_tts import PiperTTS
        
        # Initialize piper (this downloads the model)
        print("Initializing Piper TTS...")
        tts = PiperTTS(
            model="en_US-lessac-medium",
            data_dir=str(models_dir)
        )
        
        print("✓ Voice model downloaded successfully!")
        print(f"✓ Location: {models_dir}")
        
        # Test it
        print("\nTesting voice synthesis...")
        output_file = models_dir / "test.wav"
        tts.synthesize("Hello, this is a test.", str(output_file))
        
        if output_file.exists():
            print(f"✓ Test successful! Audio saved to: {output_file}")
            print("\nYou can now use Piper TTS with Vask!")
        else:
            print("✗ Test failed")
            return False
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure piper-tts is installed: pip install piper-tts")
        print("2. Check internet connection")
        print("3. Try again")
        return False

if __name__ == "__main__":
    success = download_piper_voice()
    sys.exit(0 if success else 1)
