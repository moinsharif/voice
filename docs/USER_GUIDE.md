# Vask User Guide

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Using Vask](#using-vask)
5. [Features](#features)
6. [Troubleshooting](#troubleshooting)

## Installation

### System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- Dual-core processor minimum
- Microphone for voice input
- Webcam (optional, for face detection)
- 5GB disk space for models

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vask.git
cd vask
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download required models (optional, will auto-download on first use):
```bash
python -c "import whisper; whisper.load_model('base')"
```

## Quick Start

### Basic Usage

```python
from src.main import VaskApplication

# Initialize Vask
app = VaskApplication()

# Start the application
app.start()

# Start a conversation session
app.start_session("user-1")

# Process voice input (in real usage, this comes from microphone)
import numpy as np
audio_data = np.random.randn(16000).astype(np.float32).tobytes()
response = app.process_voice_input(audio_data)

print(f"Vask: {response}")

# End the session
app.end_session()

# Stop the application
app.stop()
```

### Running from Command Line

```bash
python src/main.py
```

## Configuration

### Configuration File

Vask uses YAML configuration files. Default location: `config/default_config.yaml`

### Configuration Options

```yaml
# System
version: "1.0.0"
offline_mode: true

# Audio
language: "en"
voice_id: "en_US-lessac-medium"
speaking_rate: 1.0
listening_sensitivity: 0.5

# Features
enable_camera: true
enable_audio_output: true
enable_learning: true

# Performance
max_context_exchanges: 10
response_timeout_seconds: 2

# Privacy
encryption_enabled: true
auto_delete_after_days: null

# Model paths
whisper_model_path: "models/whisper"
llama_model_path: "models/llama"
piper_model_path: "models/piper"
```

### Customizing Configuration

1. Create a custom configuration file:
```bash
cp config/default_config.yaml config/my_config.yaml
```

2. Edit the file with your preferences

3. Use it when initializing Vask:
```python
app = VaskApplication(config_path="config/my_config.yaml")
```

## Using Vask

### Starting a Conversation

```python
from src.main import VaskApplication

app = VaskApplication()
app.start()

# Start session with user ID
app.start_session("user-1")

# Now ready to process voice input
```

### Processing Voice Input

```python
# In a real application, you would capture audio from microphone
# For now, using dummy audio data
import numpy as np

audio_data = np.random.randn(16000).astype(np.float32).tobytes()
response = app.process_voice_input(audio_data)

if response:
    print(f"Vask: {response}")
else:
    print("Failed to process input")
```

### Ending a Conversation

```python
# End the current session
app.end_session()

# Stop the application
app.stop()
```

### Viewing Conversation History

```python
# Export conversation history
history = app.export_conversation_history("user-1", format="json")

# Save to file
with open("conversation_history.json", "w") as f:
    f.write(history)
```

### Checking Mood Reports

```python
# Get mood report for current session
mood_report = app.get_mood_report("user-1", period="session")

print(f"Primary mood: {mood_report.primary_mood}")
print(f"Mood stability: {mood_report.mood_stability}")
print(f"Average confidence: {mood_report.average_confidence}")
```

### Managing User Profiles

```python
# Get user profile
profile = app.get_user_profile("user-1")

# View profile information
print(f"Communication style: {profile.communication_style}")
print(f"Preferred topics: {profile.preferred_topics}")
print(f"Interaction count: {profile.interaction_count}")

# Update preferences
profile.communication_style = "formal"
profile.preferred_topics = ["technology", "science"]
app.context_manager.save_user_profile()
```

## Features

### Speech Recognition

- Supports 99 languages
- Automatic language detection
- Noise filtering for background noise
- ≥85% accuracy for clear speech
- Completes within 3 seconds of speech end

### Conversational AI

- Context-aware responses
- Maintains last 10 exchanges
- Considers user mood state
- Adapts tone based on preferences
- Operates entirely offline

### Mood Analysis

- Detects emotional state from voice tone
- Analyzes facial expressions (with camera)
- Classifies mood: positive, neutral, negative, mixed
- Tracks mood patterns over time
- Generates mood reports

### Learning System

- Analyzes daily interactions
- Identifies communication patterns
- Tracks response preferences
- Updates user profile automatically
- Improves responses over time

### Multi-User Support

- Separate profiles per user
- Face detection for user identification
- Manual user selection fallback
- Isolated conversation histories
- Secure data separation

### Data Privacy

- All data stored locally
- AES-256 encryption at rest
- No external API calls
- No data transmission
- Secure deletion on request

## Troubleshooting

### Issue: "Model not found" error

**Solution**: Models will auto-download on first use. Ensure you have internet connection for initial setup.

```bash
# Manual model download
python -c "import whisper; whisper.load_model('base')"
```

### Issue: Microphone not detected

**Solution**: Check system audio settings and permissions.

```python
# Test microphone access
from src.engines.speech_recognition_engine import SpeechRecognitionEngine
engine = SpeechRecognitionEngine()
engine.start_listening()
# If no error, microphone is working
```

### Issue: High CPU usage

**Solution**: Reduce model size or disable features.

```yaml
# In config file, use smaller model
whisper_model_path: "models/whisper-tiny"

# Disable camera if not needed
enable_camera: false
```

### Issue: Slow response generation

**Solution**: Increase response timeout or reduce context size.

```yaml
response_timeout_seconds: 5
max_context_exchanges: 5
```

### Issue: Database errors

**Solution**: Restore from backup.

```python
from src.persistence.persistence_layer import PersistenceLayer

persistence = PersistenceLayer()

# List available backups
# Restore from backup
persistence.restore_backup("backup_id")
```

### Issue: Face detection not working

**Solution**: Check camera permissions and ensure camera is available.

```python
from src.analysis.face_detection import FaceDetectionModule

detector = FaceDetectionModule()
if detector.start_camera():
    print("Camera is working")
else:
    print("Camera not available")
```

### Issue: Audio output not working

**Solution**: Check system audio settings and enable audio output.

```yaml
enable_audio_output: true
```

### Issue: Encryption errors

**Solution**: Ensure encryption key is correct and consistent.

```python
# Use same encryption key for all operations
app = VaskApplication(encryption_key="your-secret-key")
```

## Performance Optimization

### Memory Usage

- Vask uses ~2GB RAM during normal operation
- Reduce context size to save memory:
```yaml
max_context_exchanges: 5
```

- Disable camera if not needed:
```yaml
enable_camera: false
```

### CPU Usage

- Use smaller Whisper model:
```yaml
whisper_model_path: "models/whisper-tiny"
```

- Reduce face detection frame rate
- Disable learning system if not needed:
```yaml
enable_learning: false
```

### Disk Space

- Conversation history is stored locally
- Enable auto-deletion of old conversations:
```yaml
auto_delete_after_days: 30
```

- Export and archive old conversations:
```python
history = app.export_conversation_history("user-1", format="json")
# Save to archive
```

## Advanced Usage

### Custom Configuration

```python
from src.config.config_system import ConfigurationSystem

system = ConfigurationSystem()
config = system.parse_config_file("config/custom.yaml")

# Modify configuration
config.language = "es"
config.speaking_rate = 1.5

# Save modified configuration
system.save_configuration(config, "config/modified.yaml")
```

### Accessing Components Directly

```python
from src.main import VaskApplication

app = VaskApplication()
app.start()

# Access individual components
speech_engine = app.speech_engine
ai_model = app.ai_model
mood_engine = app.mood_engine

# Use components directly
transcription = speech_engine.transcribe(audio_data)
mood = mood_engine.analyze_mood(audio_data)
```

### Batch Processing

```python
from src.main import VaskApplication

app = VaskApplication()
app.start()

# Process multiple users
users = ["user-1", "user-2", "user-3"]

for user_id in users:
    app.start_session(user_id)
    # Process user data
    app.end_session()

app.stop()
```

## Support and Feedback

For issues, questions, or feedback:

1. Check the troubleshooting section above
2. Review API documentation in `docs/API_DOCUMENTATION.md`
3. Check application logs in `logs/` directory
4. Submit issues on GitHub

## License

Vask is released under the MIT License. See LICENSE file for details.

## Acknowledgments

Vask uses the following open-source projects:

- Whisper (OpenAI) - Speech recognition
- Llama 2 (Meta) - Language model
- MediaPipe (Google) - Face detection
- Piper (Rhasspy) - Text-to-speech
- SQLite - Database
- Cryptography - Encryption

Thank you to all contributors and the open-source community!
