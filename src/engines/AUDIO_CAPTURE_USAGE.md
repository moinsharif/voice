# AudioCapture Module Usage Guide

## Overview

The `AudioCapture` class provides real-time audio capture from the system microphone with integrated noise filtering, silence detection, and audio quality validation.

## Basic Usage

### Initialize AudioCapture

```python
from src.engines.audio_capture import AudioCapture

# Create with default settings (16kHz sample rate, 1024 chunk size)
capture = AudioCapture()

# Or with custom settings
capture = AudioCapture(
    sample_rate=44100,
    chunk_size=2048,
    silence_threshold=0.03,
    noise_duration=1.0
)
```

### Start Recording

```python
# Start capturing audio from microphone
capture.start_recording()

# Audio capture is now active
# The system will automatically capture a noise profile for filtering
```

### Get Audio Chunks

```python
# Get audio chunks in real-time
while capture.is_recording:
    chunk = capture.get_audio_chunk()
    if chunk:
        # Process the audio chunk
        pass
```

### Detect Silence

```python
# Check if audio chunk contains silence
chunk = capture.get_audio_chunk()
if chunk:
    is_silent = capture.detect_silence(chunk)
    if is_silent:
        print("Silence detected")
    else:
        print("Audio detected")
```

### Apply Noise Filtering

```python
# Apply spectral subtraction noise filtering
chunk = capture.get_audio_chunk()
if chunk:
    filtered_chunk = capture.apply_noise_filter(chunk)
    # Use filtered_chunk for speech recognition
```

### Validate Audio Quality

```python
# Check audio quality metrics
chunk = capture.get_audio_chunk()
if chunk:
    quality = capture.validate_audio_quality(chunk)
    
    print(f"Valid: {quality['is_valid']}")
    print(f"RMS: {quality['rms']:.4f}")
    print(f"Peak: {quality['peak']:.4f}")
    print(f"Clipping: {quality['clipping_ratio']:.2%}")
    print(f"Issues: {quality['issues']}")
```

### Stop Recording

```python
# Stop capturing audio
capture.stop_recording()
```

## Integration with Speech Recognition

```python
from src.engines.audio_capture import AudioCapture
from src.engines.speech_recognition_engine import SpeechRecognitionEngine

# Initialize components
capture = AudioCapture(sample_rate=16000)
speech_engine = SpeechRecognitionEngine()

# Start recording
capture.start_recording()

# Capture audio
audio_chunks = []
while len(audio_chunks) < 10:  # Capture 10 chunks
    chunk = capture.get_audio_chunk()
    if chunk:
        # Apply noise filtering
        filtered = capture.apply_noise_filter(chunk)
        
        # Check quality
        quality = capture.validate_audio_quality(filtered)
        if quality['is_valid']:
            audio_chunks.append(filtered)

# Combine chunks and transcribe
import numpy as np
audio_data = b''.join(audio_chunks)

# Transcribe using speech recognition engine
result = speech_engine.transcribe(audio_data)
print(f"Transcription: {result.text}")

# Stop recording
capture.stop_recording()
```

## Advanced Features

### Get Microphone Information

```python
# Get current configuration
info = capture.get_microphone_info()
print(f"Sample Rate: {info['sample_rate']} Hz")
print(f"Chunk Size: {info['chunk_size']}")
print(f"Channels: {info['channels']}")
print(f"Recording: {info['is_recording']}")
print(f"Noise Profile: {info['noise_profile']}")
```

### List Available Input Devices

```python
# Get list of available microphones
devices = capture.list_input_devices()
for device in devices:
    print(f"Device {device['index']}: {device['name']}")
    print(f"  Channels: {device['channels']}")
    print(f"  Sample Rate: {device['sample_rate']} Hz")
```

### Buffer Management

```python
# Get all buffered audio
buffer = capture.get_audio_buffer()

# Clear buffer
capture.clear_buffer()
```

### Cleanup

```python
# Clean up audio resources
capture.cleanup()
```

## Configuration Parameters

### Constructor Parameters

- **sample_rate** (int): Sample rate in Hz (default: 16000)
  - Common values: 8000, 16000, 44100, 48000
  
- **chunk_size** (int): Chunk size for real-time processing (default: 1024)
  - Larger chunks = lower latency but higher memory
  - Smaller chunks = higher latency but lower memory
  
- **channels** (int): Number of audio channels (default: 1 for mono)
  - 1 = Mono, 2 = Stereo
  
- **format_type** (int): PyAudio format type (default: paFloat32)
  - paFloat32 = 32-bit float
  - paInt16 = 16-bit integer
  
- **silence_threshold** (float): RMS threshold for silence detection (default: 0.02)
  - Lower values = more sensitive to silence
  - Higher values = less sensitive to silence
  
- **noise_duration** (float): Duration in seconds for noise profile (default: 0.5)
  - Longer duration = better noise profile estimation

## Audio Quality Metrics

The `validate_audio_quality()` method returns:

- **is_valid** (bool): Whether audio meets quality requirements
- **rms** (float): Root Mean Square (signal level)
- **peak** (float): Peak amplitude
- **mean_abs** (float): Mean absolute value
- **clipping_ratio** (float): Ratio of clipped samples (0.0-1.0)
- **duration_seconds** (float): Duration of audio in seconds
- **issues** (list): List of detected quality issues

## Error Handling

```python
try:
    capture = AudioCapture()
    capture.start_recording()
    
    chunk = capture.get_audio_chunk()
    if chunk is None:
        print("Failed to capture audio")
    
    capture.stop_recording()
except Exception as e:
    print(f"Error: {e}")
finally:
    capture.cleanup()
```

## Performance Considerations

- **Memory**: Audio buffer holds up to 10 seconds of audio
- **CPU**: Noise filtering uses spectral subtraction (low CPU overhead)
- **Latency**: Chunk-based processing enables real-time operation
- **Quality**: 16kHz sample rate is optimal for speech recognition

## Troubleshooting

### No audio captured
- Check microphone is connected and enabled
- Verify microphone permissions are granted
- Try listing devices: `capture.list_input_devices()`

### Audio quality issues
- Increase silence_threshold if detecting false silence
- Increase noise_duration for better noise profile
- Check microphone levels in system settings

### Noise filtering not working
- Ensure noise profile is captured (happens automatically on start_recording)
- Try adjusting noise_duration parameter
- Check audio quality metrics to verify filtering effect

## Requirements

- PyAudio: `pip install pyaudio`
- NumPy: `pip install numpy`
- Python 3.8+
