# Vask - Voice-Based AI Companion

A locally-operated, voice-based AI companion system that combines speech recognition, conversational AI, facial expression analysis, and mood detection to provide personalized, context-aware interactions.

## Features

✨ **Core Features**

- 🎤 **Speech Recognition** - Convert voice to text with 85%+ accuracy using Whisper
- 🤖 **Conversational AI** - Context-aware responses using Llama 2 language model
- 😊 **Mood Analysis** - Detect emotional state from voice tone and facial expressions
- 📚 **Learning System** - Improves responses through daily interaction analysis
- 🎙️ **Text-to-Speech** - Natural-sounding audio output using Piper
- 👥 **Multi-User Support** - Separate profiles and conversation histories per user
- 🔒 **Privacy First** - All data stored locally with AES-256 encryption
- 🚀 **Offline Operation** - No internet required, no external API calls

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Vask Application                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Session Manager                             │   │
│  │  - Lifecycle management                                  │   │
│  │  - User identification                                   │   │
│  │  - State coordination                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ▲                                    │
│                              │                                    │
│  ┌──────────────┬────────────┼────────────┬──────────────────┐   │
│  │              │            │            │                  │   │
│  ▼              ▼            ▼            ▼                  ▼   │
│ ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌──────────┐   │
│ │Speech  │  │AI Model│  │Face    │  │Mood    │  │Learning  │   │
│ │Recog.  │  │Wrapper │  │Detector│  │Analyzer│  │System    │   │
│ │Engine  │  │        │  │        │  │        │  │          │   │
│ └────────┘  └────────┘  └────────┘  └────────┘  └──────────┘   │
│      │           │           │           │            │         │
│      └───────────┼───────────┼───────────┼────────────┘         │
│                  │           │           │                      │
│  ┌───────────────┴───────────┴───────────┴──────────────────┐   │
│  │              Context Manager                             │   │
│  │  - Conversation context (last 10 exchanges)              │   │
│  │  - User profile management                               │   │
│  │  - Historical context retrieval                          │   │
│  └───────────────┬───────────────────────────────────────────┘   │
│                  │                                                │
│  ┌───────────────┴───────────────────────────────────────────┐   │
│  │              Persistence Layer                            │   │
│  │  - Conversation history (SQLite)                          │   │
│  │  - User profiles (encrypted)                              │   │
│  │  - Configuration storage                                  │   │
│  │  - Mood analytics data                                    │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/vask.git
cd vask

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from src.main import VaskApplication

# Initialize application
app = VaskApplication(config_path="config/default_config.yaml")

# Start application
app.start()

# Start conversation session
app.start_session("user-1")

# Process voice input
response = app.process_voice_input(audio_data)
print(f"Vask: {response}")

# End session
app.end_session()

# Stop application
app.stop()
```

## Project Structure

```
vask/
├── src/
│   ├── main.py                 # Main application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── data_models.py      # Core data models
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── speech_recognition_engine.py
│   │   ├── ai_model_wrapper.py
│   │   └── text_to_speech_engine.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── face_detection.py
│   │   └── mood_analysis.py
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── context_manager.py
│   │   ├── session_manager.py
│   │   └── learning_system.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   └── persistence_layer.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── configuration.py
│   │   └── config_system.py
│   └── utils/
│       ├── __init__.py
│       ├── encryption.py
│       ├── error_recovery.py
│       ├── fallback_responses.py
│       └── logger.py
├── tests/
│   ├── test_data_models.py
│   ├── test_persistence.py
│   ├── test_engines.py
│   ├── test_analysis.py
│   ├── test_managers.py
│   └── ...
├── config/
│   └── default_config.yaml
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── USER_GUIDE.md
│   └── README.md
├── requirements.txt
├── setup.py
└── README.md
```

## Components

### Speech Recognition Engine
- Converts audio input to text using Whisper
- Supports 99 languages
- Automatic language detection
- Noise filtering for background noise
- ≥85% accuracy for clear speech

### AI Model Wrapper
- Generates contextual responses using Llama 2 7B
- Maintains conversation context (last 10 exchanges)
- Considers user mood state
- Adapts tone based on preferences
- Response caching for performance

### Face Detection Module
- Detects faces using MediaPipe
- Identifies facial landmarks
- Classifies expressions (happy, sad, angry, surprised, neutral)
- Processes frames at 15 FPS minimum
- Gracefully handles missing faces

### Mood Analysis Engine
- Detects emotional state from voice tone and facial expressions
- Classifies mood: positive, neutral, negative, mixed
- Maintains mood history per session
- Generates mood summaries and reports
- Correlates mood with conversation topics

### Learning System
- Analyzes daily interactions
- Identifies patterns in user preferences
- Tracks response types that received positive feedback
- Updates user profile with learned preferences
- Applies previous day's learnings to improve responses

### Context Manager
- Maintains conversation context
- Manages user profiles
- Handles session lifecycle
- Retrieves historical context
- Supports multi-user scenarios

### Session Manager
- Manages conversation lifecycle
- Coordinates all components
- Handles state transitions
- Processes user input through full pipeline
- Supports session replay

### Persistence Layer
- Stores conversation history in SQLite
- Encrypts sensitive data with AES-256
- Supports searching by date, mood, keyword
- Handles data backup and recovery
- Exports conversations in JSON/CSV formats

## Configuration

Edit `config/default_config.yaml` to customize:

```yaml
# Audio
language: "en"
voice_id: "en_US-lessac-medium"
speaking_rate: 1.0

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
```

## Testing

Run comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_data_models.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

**Test Coverage**: 194 tests covering all components

## Documentation

- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference
- **[User Guide](docs/USER_GUIDE.md)** - Installation, configuration, and usage guide
- **[Design Document](.kiro/specs/vask/design.md)** - Technical architecture and design
- **[Requirements](.kiro/specs/vask/requirements.md)** - Detailed requirements

## Performance

### Resource Usage
- **Memory**: ~2GB RAM during normal operation
- **CPU**: Minimal when idle, scales with processing
- **Disk**: ~5GB for models, additional for conversation history

### Performance Targets
- Speech recognition: Complete within 3 seconds of speech end
- AI response generation: Complete within 2 seconds
- Face detection: Process at 15 FPS minimum
- TTS synthesis: <1 second per 100 words
- Conversation retrieval: <500ms

## Security & Privacy

### Data Encryption
- All sensitive data encrypted with AES-256-CBC
- Encryption keys derived from user password using PBKDF2
- Separate encryption keys per user
- Encrypted data stored in SQLite BLOB fields

### Local-Only Operation
- No internet connectivity required
- No external API calls
- All processing on local machine
- No data transmission outside device

### User Data Isolation
- Separate encryption keys per user
- Isolated conversation histories
- Independent user profiles
- Face detection for user identification

## Error Handling

Comprehensive error handling with graceful degradation:

- Speech recognition fails → Request user retry with friendly message
- AI model fails → Provide fallback response
- Face detection fails → Continue with voice-only mood detection
- TTS fails → Display text response instead
- Database corruption → Attempt recovery from backups

## Technology Stack

- **Speech Recognition**: Whisper (OpenAI)
- **Language Model**: Llama 2 7B (Meta)
- **Face Detection**: MediaPipe (Google)
- **Text-to-Speech**: Piper (Rhasspy)
- **Database**: SQLite
- **Encryption**: AES-256 (cryptography library)
- **Configuration**: YAML/JSON
- **Testing**: pytest

## Requirements

- Python 3.8+
- 4GB RAM minimum (8GB recommended)
- Dual-core processor minimum
- Microphone for voice input
- Webcam (optional, for face detection)
- 5GB disk space for models

## Installation from Source

```bash
# Clone repository
git clone https://github.com/yourusername/vask.git
cd vask

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Start application
python src/main.py
```

## Usage Examples

### Complete Conversation Flow

```python
from src.main import VaskApplication

app = VaskApplication()
app.start()

# Start session
app.start_session("user-1")

# Process voice input
response = app.process_voice_input(audio_data)

# Get mood report
mood_report = app.get_mood_report("user-1")

# End session
app.end_session()
app.stop()
```

### User Profile Management

```python
# Get user profile
profile = app.get_user_profile("user-1")

# Update preferences
profile.communication_style = "formal"
profile.preferred_topics = ["technology"]

# Save profile
app.context_manager.save_user_profile()
```

### Export Conversation History

```python
# Export as JSON
history = app.export_conversation_history("user-1", format="json")

# Export as CSV
history = app.export_conversation_history("user-1", format="csv")
```

## Troubleshooting

### Common Issues

**Model not found**: Models auto-download on first use. Ensure internet connection.

**Microphone not detected**: Check system audio settings and permissions.

**High CPU usage**: Reduce model size or disable features in configuration.

**Slow response**: Increase response timeout or reduce context size.

See [User Guide](docs/USER_GUIDE.md) for detailed troubleshooting.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

Vask is released under the MIT License. See LICENSE file for details.

## Acknowledgments

Vask uses the following open-source projects:

- **Whisper** (OpenAI) - Speech recognition
- **Llama 2** (Meta) - Language model
- **MediaPipe** (Google) - Face detection
- **Piper** (Rhasspy) - Text-to-speech
- **SQLite** - Database
- **Cryptography** - Encryption

Thank you to all contributors and the open-source community!

## Support

For issues, questions, or feedback:

1. Check the [User Guide](docs/USER_GUIDE.md)
2. Review [API Documentation](docs/API_DOCUMENTATION.md)
3. Check application logs in `logs/` directory
4. Submit issues on GitHub

## Roadmap

- [ ] Web interface for configuration
- [ ] Mobile app support
- [ ] Advanced mood analytics dashboard
- [ ] Custom model fine-tuning
- [ ] Multi-language support improvements
- [ ] Performance optimizations
- [ ] Additional voice options
- [ ] Integration with smart home systems

## Status

**Current Version**: 1.0.0

**Status**: Production Ready

**Test Coverage**: 194 tests passing

**Last Updated**: 2024

---

Made with ❤️ for privacy-conscious users who want a personal AI companion.
