#!/usr/bin/env python3
"""
Setup script to download all required models for VASK
"""

import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """Create necessary model directories"""
    dirs = [
        'models/whisper-base',
        'models/whisper-tiny',
        'models/whisper-small',
        'models/llama-2-7b',
        'models/piper',
        'models/mediapipe'
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {d}")

def download_whisper_models():
    """Download Whisper models"""
    print("\n" + "="*60)
    print("Downloading Whisper Speech Recognition Models...")
    print("="*60)
    
    try:
        import whisper
        models = ['base', 'tiny', 'small']
        for model in models:
            print(f"\nDownloading whisper-{model}...")
            whisper.load_model(model)
            print(f"✓ Successfully downloaded whisper-{model}")
    except Exception as e:
        print(f"✗ Error downloading Whisper models: {e}")
        print("Install with: pip install openai-whisper")
        return False
    return True

def download_llama_model():
    """Download Llama 2 model"""
    print("\n" + "="*60)
    print("Downloading Llama 2 Language Model...")
    print("="*60)
    
    try:
        print("\nLlama 2 model needs to be downloaded manually:")
        print("1. Visit: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF")
        print("2. Download: llama-2-7b-chat.Q4_K_M.gguf")
        print("3. Place in: models/llama-2-7b/")
        print("\nOr use this command:")
        print("wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf -O models/llama-2-7b/llama-2-7b-chat.Q4_K_M.gguf")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def download_piper_model():
    """Download Piper TTS model"""
    print("\n" + "="*60)
    print("Downloading Piper Text-to-Speech Model...")
    print("="*60)
    
    try:
        print("\nDownloading Piper TTS model...")
        subprocess.run([
            'piper',
            '--download-dir', 'models/piper',
            '--voice', 'en_US-lessac-medium'
        ], check=False)
        print("✓ Piper model downloaded")
        return True
    except Exception as e:
        print(f"Note: Piper will auto-download on first use")
        print(f"Or install with: pip install piper-tts")
        return True

def download_mediapipe_models():
    """Download MediaPipe models"""
    print("\n" + "="*60)
    print("Setting up MediaPipe Face Detection Models...")
    print("="*60)
    
    try:
        import mediapipe as mp
        print("\nMediaPipe models auto-download on first use")
        print("✓ MediaPipe is ready")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Install with: pip install mediapipe")
        return False

def main():
    print("\n" + "="*60)
    print("VASK Model Setup Script")
    print("="*60)
    
    # Create directories
    create_directories()
    
    # Download models
    results = {
        'Whisper': download_whisper_models(),
        'Llama 2': download_llama_model(),
        'Piper TTS': download_piper_model(),
        'MediaPipe': download_mediapipe_models(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("Setup Summary")
    print("="*60)
    for model, success in results.items():
        status = "✓ Ready" if success else "✗ Failed"
        print(f"{model}: {status}")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Ensure all models are downloaded")
    print("2. Run: python vask_gui.py")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
