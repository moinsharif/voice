#!/usr/bin/env python3
"""
Download Piper voice model - Simple version
"""

import os
from pathlib import Path

def download_voice():
    """Download Piper voice model."""
    try:
        print("Downloading Piper voice model...")
        print("This will download ~100MB...\n")
        
        # Create models directory
        models_dir = Path("models/piper")
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Download voice
        from piper import download_voices
        
        print("Downloading en_US-lessac-medium...")
        download_voices(
            voice="en_US-lessac-medium",
            output_dir=str(models_dir),
            speaker=None,
            download_dir=str(models_dir)
        )
        
        print("✓ Voice downloaded successfully!")
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nTry this instead:")
        print("pip install pyttsx3")
        return False

if __name__ == "__main__":
    download_voice()
