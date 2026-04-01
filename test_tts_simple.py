#!/usr/bin/env python3
"""
Simple TTS debug script - Test if text-to-speech works
"""

import sys
from datetime import datetime

def test_pyttsx3():
    """Test pyttsx3 TTS."""
    print("Testing pyttsx3 TTS...")
    try:
        import pyttsx3
        
        # Initialize engine
        engine = pyttsx3.init()
        
        # Set properties
        engine.setProperty('rate', 150)  # Speed
        engine.setProperty('volume', 0.9)  # Volume
        
        # Test text
        text = f"Today is {datetime.now().strftime('%A')}"
        print(f"Speaking: '{text}'")
        
        # Speak
        engine.say(text)
        engine.runAndWait()
        
        print("✓ pyttsx3 works!")
        return True
    
    except Exception as e:
        print(f"✗ pyttsx3 error: {e}")
        return False

def test_piper():
    """Test Piper TTS."""
    print("\nTesting Piper TTS...")
    try:
        import subprocess
        import tempfile
        from pathlib import Path
        
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = f.name
        
        # Test text
        text = f"Today is {datetime.now().strftime('%A')}"
        print(f"Speaking: '{text}'")
        
        # Try to use piper
        process = subprocess.Popen(
            ["piper", "--model", "en_US-lessac-medium", "--output-file", temp_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=text.encode())
        
        if process.returncode == 0:
            print("✓ Piper works!")
            
            # Try to play audio
            try:
                import pyaudio
                from scipy.io import wavfile
                import numpy as np
                
                sample_rate, audio_data = wavfile.read(temp_file)
                
                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 1 if len(audio_data.shape) == 1 else audio_data.shape[1]
                
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=sample_rate,
                    output=True,
                    frames_per_buffer=CHUNK
                )
                
                audio_bytes = audio_data.tobytes()
                for i in range(0, len(audio_bytes), CHUNK * 2):
                    chunk = audio_bytes[i:i + CHUNK * 2]
                    stream.write(chunk)
                
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                print("✓ Audio played successfully!")
            except Exception as e:
                print(f"✗ Audio playback error: {e}")
            
            return True
        else:
            print(f"✗ Piper error: {stderr.decode()}")
            return False
    
    except FileNotFoundError:
        print("✗ Piper not found in PATH")
        return False
    except Exception as e:
        print(f"✗ Piper error: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("TTS Debug Script")
    print("=" * 60)
    print()
    
    # Test pyttsx3
    pyttsx3_ok = test_pyttsx3()
    
    # Test piper
    piper_ok = test_piper()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"pyttsx3: {'✓ OK' if pyttsx3_ok else '✗ FAILED'}")
    print(f"Piper:   {'✓ OK' if piper_ok else '✗ FAILED'}")
    
    if pyttsx3_ok or piper_ok:
        print("\n✓ At least one TTS engine works!")
        print("You can now use Vask with voice output.")
    else:
        print("\n✗ No TTS engine working!")
        print("Install pyttsx3: pip install pyttsx3")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
