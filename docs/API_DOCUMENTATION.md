# Vask API Documentation

## Overview

Vask is a locally-operated, voice-based AI companion system that combines speech recognition, conversational AI, facial expression analysis, and mood detection. This document provides comprehensive API documentation for all components.

## Table of Contents

1. [Main Application](#main-application)
2. [Data Models](#data-models)
3. [Engines](#engines)
4. [Analysis Modules](#analysis-modules)
5. [Managers](#managers)
6. [Persistence Layer](#persistence-layer)
7. [Configuration System](#configuration-system)
8. [Utilities](#utilities)

## Main Application

### VaskApplication

The main application class that orchestrates all components.

```python
from src.main import VaskApplication

# Initialize application
app = VaskApplication(config_path="config/default_config.yaml")

# Start application
app.start()

# Start a conversation session
app.start_session("user-1")

# Process voice input
response = app.process_voice_input(audio_data)

# End session
app.end_session()

# Stop application
app.stop()
```

#### Methods

- `__init__(config_path: str = None, encryption_key: Optional[str] = None)` - Initialize application
- `start()` - Start the application
- `stop()` - Stop the application gracefully
- `start_session(user_id: str) -> bool` - Start a new conversation session
- `end_session() -> bool` - End current session
- `process_voice_input(audio_data: bytes) -> Optional[str]` - Process voice input
- `get_user_profile(user_id: str)` - Get user profile
- `get_mood_report(user_id: str, period: str = "session")` - Get mood report
- `export_conversation_history(user_id: str, format: str = "json") -> Optional[str]` - Export conversations
- `get_application_info() -> dict` - Get application information

## Data Models

### UserProfile

Represents a user's profile with preferences and learning data.

```python
from src.models.data_models import UserProfile
from datetime import datetime

profile = UserProfile(
    user_id="user-1",
    created_at=datetime.now(),
    last_interaction=datetime.now(),
    communication_style="casual",
    preferred_topics=["work", "hobbies"],
    language="en",
    voice_id="en_US-lessac-medium",
    speaking_rate=1.0
)

# Serialize to JSON
json_str = profile.to_json()

# Deserialize from JSON
profile = UserProfile.from_json(json_str)
```

#### Fields

- `user_id: str` - Unique user identifier
- `created_at: datetime` - Profile creation timestamp
- `last_interaction: datetime` - Last interaction timestamp
- `communication_style: str` - "formal", "casual", or "technical"
- `preferred_topics: List[str]` - Topics user prefers
- `response_preferences: Dict[str, float]` - Response type preferences
- `mood_history: List[MoodEntry]` - Historical mood entries
- `average_mood: str` - Average mood classification
- `mood_trends: Dict[str, float]` - Mood frequency trends
- `learned_preferences: Dict[str, Any]` - Learned preferences
- `interaction_count: int` - Total interactions
- `last_learning_update: Optional[datetime]` - Last learning update
- `language: str` - Language code
- `voice_id: str` - Voice identifier
- `speaking_rate: float` - Speaking rate (0.5-2.0)
- `listening_sensitivity: float` - Listening sensitivity (0.0-1.0)
- `mood_sensitivity: float` - Mood sensitivity (0.0-1.0)

### Session

Represents a complete conversation session.

```python
from src.models.data_models import Session, Exchange
from datetime import datetime

session = Session(
    session_id="session-1",
    user_id="user-1",
    created_at=datetime.now()
)

# Add exchanges
exchange = Exchange(
    timestamp=datetime.now(),
    user_message="Hello",
    ai_response="Hi there!"
)
session.exchanges.append(exchange)

# Serialize to JSON
json_str = session.to_json()

# Deserialize from JSON
session = Session.from_json(json_str)
```

#### Fields

- `session_id: str` - Unique session identifier
- `user_id: str` - User identifier
- `created_at: datetime` - Session creation timestamp
- `ended_at: Optional[datetime]` - Session end timestamp
- `exchanges: List[Exchange]` - List of exchanges
- `mood_summary: Optional[MoodSummary]` - Mood summary
- `metadata: Optional[SessionMetadata]` - Session metadata
- `audio_data: Optional[bytes]` - Encrypted audio data
- `transcript: str` - Session transcript

### Mood

Represents a mood classification.

```python
from src.models.data_models import Mood
from datetime import datetime

mood = Mood(
    timestamp=datetime.now(),
    classification="positive",
    confidence=0.8,
    voice_tone="upbeat",
    facial_expression="happy"
)
```

#### Fields

- `timestamp: datetime` - Mood detection timestamp
- `classification: str` - "positive", "neutral", "negative", or "mixed"
- `confidence: float` - Confidence score (0.0-1.0)
- `facial_expression: Optional[str]` - Detected facial expression
- `voice_tone: Optional[str]` - Detected voice tone
- `conversation_topic: Optional[str]` - Conversation topic
- `time_of_day: Optional[str]` - Time of day

## Engines

### SpeechRecognitionEngine

Converts audio input to text using Whisper.

```python
from src.engines.speech_recognition_engine import SpeechRecognitionEngine

engine = SpeechRecognitionEngine(model_size="base", language="en")

# Start listening
engine.start_listening()

# Transcribe audio
result = engine.transcribe(audio_data)
print(f"Text: {result.text}")
print(f"Confidence: {result.confidence}")

# Stop listening
engine.stop_listening()

# Set language
engine.set_language("es")

# Apply noise filtering
filtered_audio = engine.apply_noise_filter(audio_data)
```

#### Methods

- `start_listening()` - Start listening for audio
- `stop_listening()` - Stop listening
- `transcribe(audio_data: bytes) -> TranscriptionResult` - Transcribe audio
- `set_language(language_code: str)` - Set language
- `apply_noise_filter(audio_data: bytes) -> bytes` - Apply noise filtering
- `get_model_info() -> dict` - Get model information

### AIModelWrapper

Generates contextual responses using Llama 2.

```python
from src.engines.ai_model_wrapper import AIModelWrapper, ConversationContext

model = AIModelWrapper()

# Create context
context = ConversationContext(max_exchanges=10)

# Generate response
response = model.generate_response(context, "Hello")

# Set response tone
model.set_response_tone("empathetic")

# Check if model is available
if model.is_model_available():
    print("Model is ready")

# Clear cache
model.clear_cache()
```

#### Methods

- `generate_response(context: ConversationContext, user_message: str) -> str` - Generate response
- `set_response_tone(tone: str)` - Set response tone
- `is_model_available() -> bool` - Check if model is available
- `clear_cache()` - Clear response cache
- `get_model_info() -> dict` - Get model information

### TextToSpeechEngine

Converts text to speech using Piper.

```python
from src.engines.text_to_speech_engine import TextToSpeechEngine

engine = TextToSpeechEngine(voice_id="en_US-lessac-medium", enabled=True)

# Synthesize text
audio = engine.synthesize("Hello world")

# Play audio
engine.play_audio(audio)

# Set voice
engine.set_voice("en_US-ryan-medium")

# Set speaking rate
engine.set_speaking_rate(1.5)

# Get available voices
voices = engine.get_available_voices()

# Enable/disable TTS
engine.set_enabled(False)
```

#### Methods

- `synthesize(text: str) -> Optional[bytes]` - Synthesize text to audio
- `play_audio(audio_data: bytes) -> bool` - Play audio
- `set_voice(voice_id: str) -> bool` - Set voice
- `set_speaking_rate(rate: float)` - Set speaking rate
- `set_enabled(enabled: bool)` - Enable/disable TTS
- `is_enabled() -> bool` - Check if TTS is enabled
- `get_available_voices() -> List[str]` - Get available voices
- `get_model_info() -> dict` - Get engine information

## Analysis Modules

### MoodAnalysisEngine

Analyzes user emotional state from voice and facial expressions.

```python
from src.analysis.mood_analysis import MoodAnalysisEngine
from src.models.data_models import Expression

engine = MoodAnalysisEngine()

# Analyze mood from audio
mood = engine.analyze_mood(audio_data=audio_data)

# Analyze mood from expression
expression = Expression(
    expression_type="happy",
    confidence=0.9,
    intensity=0.8
)
mood = engine.analyze_mood(expression=expression)

# Get mood history
history = engine.get_mood_history("user-1", period="session")

# Generate mood report
report = engine.generate_mood_report("user-1", period="day")

# Correlate mood with topics
correlations = engine.correlate_mood_with_topics("user-1")

# Clear history
engine.clear_history()
```

#### Methods

- `analyze_mood(audio_data: Optional[bytes] = None, face: Optional[Face] = None, expression: Optional[Expression] = None) -> Mood` - Analyze mood
- `get_mood_history(user_id: str = "", period: str = "session") -> List[Mood]` - Get mood history
- `generate_mood_report(user_id: str = "", period: str = "session") -> MoodSummary` - Generate mood report
- `correlate_mood_with_topics(user_id: str = "") -> Dict[str, float]` - Correlate mood with topics
- `clear_history()` - Clear mood history
- `get_model_info() -> dict` - Get engine information

## Managers

### ContextManager

Manages conversation context and user profile.

```python
from src.managers.context_manager import ContextManager
from src.persistence.persistence_layer import PersistenceLayer

persistence = PersistenceLayer()
context = ContextManager(persistence_layer=persistence)

# Load user profile
profile = context.load_user_profile("user-1")

# Save user profile
context.save_user_profile()

# Add exchange
context.add_exchange(exchange)

# Get context string
context_str = context.get_context_string()

# Start session
session = context.start_session("user-1", "session-1")

# End session
session = context.end_session()

# Load conversation history
history = context.load_conversation_history("user-1", limit=10)

# Update preferences
context.update_user_preferences({"communication_style": "formal"})
```

#### Methods

- `load_user_profile(user_id: str) -> Optional[UserProfile]` - Load user profile
- `save_user_profile() -> bool` - Save user profile
- `add_exchange(exchange: Exchange)` - Add exchange to context
- `get_context_string() -> str` - Get formatted context string
- `get_recent_exchanges(count: int = 5) -> List[Exchange]` - Get recent exchanges
- `clear_context()` - Clear context
- `start_session(user_id: str, session_id: str) -> Session` - Start session
- `end_session() -> Optional[Session]` - End session
- `load_conversation_history(user_id: str, limit: int = 10) -> List[Session]` - Load history
- `get_user_profile() -> Optional[UserProfile]` - Get current user profile
- `update_user_preferences(preferences: dict) -> bool` - Update preferences
- `get_model_info() -> dict` - Get manager information

### SessionManager

Manages conversation lifecycle and coordinates components.

```python
from src.managers.session_manager import SessionManager

manager = SessionManager(context)

# Initialize components
manager.initialize_components(speech_engine, ai_model, tts_engine, mood_engine)

# Start session
session = manager.start_session("user-1")

# Process user input
response = manager.process_user_input(audio_data)

# Pause/resume session
manager.pause_session()
manager.resume_session()

# End session
session = manager.end_session()

# Get session state
state = manager.get_session_state()

# Replay session
manager.replay_session("session-1")
```

#### Methods

- `initialize_components(...)` - Initialize processing components
- `start_session(user_id: str) -> Optional[Session]` - Start session
- `end_session() -> Optional[Session]` - End session
- `pause_session() -> bool` - Pause session
- `resume_session() -> bool` - Resume session
- `process_user_input(audio_data: bytes) -> Optional[str]` - Process user input
- `get_session_state() -> dict` - Get session state
- `replay_session(session_id: str) -> bool` - Replay session
- `get_model_info() -> dict` - Get manager information

### LearningSystem

Analyzes daily interactions and improves response quality.

```python
from src.managers.learning_system import LearningSystem

system = LearningSystem()

# Analyze day
insights = system.analyze_day("user-1", sessions)

# Identify patterns
patterns = system.identify_patterns(exchanges)

# Update user profile
system.update_user_profile(profile, insights)

# Apply learnings
learnings = system.apply_learnings(profile)
```

#### Methods

- `analyze_day(user_id: str, sessions: List[Session]) -> LearningInsights` - Analyze day
- `identify_patterns(exchanges: List[Exchange]) -> List[Pattern]` - Identify patterns
- `update_user_profile(profile: UserProfile, insights: LearningInsights)` - Update profile
- `apply_learnings(profile: UserProfile) -> Dict[str, Any]` - Apply learnings
- `get_model_info() -> dict` - Get system information

## Persistence Layer

### PersistenceLayer

Handles all data persistence with encryption.

```python
from src.persistence.persistence_layer import PersistenceLayer

persistence = PersistenceLayer(db_path="vask_data.db", encryption_key="secret")

# Save conversation
persistence.save_conversation(session)

# Load conversation
session = persistence.load_conversation("session-1")

# Save user profile
persistence.save_user_profile(profile)

# Load user profile
profile = persistence.load_user_profile("user-1")

# Search conversations
results = persistence.search_conversations(
    "user-1",
    query="work",
    mood="positive"
)

# Delete conversation
persistence.delete_conversation("session-1")

# Export conversations
exported = persistence.export_conversations("user-1", format="json")

# Create backup
backup_id = persistence.create_backup()

# Restore backup
persistence.restore_backup(backup_id)

# Configuration storage
persistence.save_configuration("language", "en")
value = persistence.load_configuration("language")
```

#### Methods

- `save_conversation(session: Session)` - Save conversation
- `load_conversation(session_id: str) -> Optional[Session]` - Load conversation
- `save_user_profile(profile: UserProfile)` - Save user profile
- `load_user_profile(user_id: str) -> Optional[UserProfile]` - Load user profile
- `search_conversations(user_id: str, query: Optional[str] = None, ...) -> List[Session]` - Search conversations
- `delete_conversation(session_id: str) -> bool` - Delete conversation
- `export_conversations(user_id: str, format: str = "json") -> Optional[str]` - Export conversations
- `create_backup() -> Optional[str]` - Create backup
- `restore_backup(backup_id: str) -> bool` - Restore backup
- `save_configuration(key: str, value: Any)` - Save configuration
- `load_configuration(key: str) -> Optional[Any]` - Load configuration

## Configuration System

### ConfigurationSystem

Parses and validates configuration files.

```python
from src.config.config_system import ConfigurationSystem

system = ConfigurationSystem()

# Parse configuration
config = system.parse_config_file("config/default_config.yaml")

# Validate configuration
result = system.validate_configuration(config_dict)

# Save configuration
system.save_configuration(config, "config/custom.yaml")

# Load configuration
config = system.load_configuration()
```

#### Methods

- `parse_config_file(filepath: str) -> Configuration` - Parse configuration file
- `validate_configuration(config_data: Dict[str, Any])` - Validate configuration
- `save_configuration(config: Configuration, filepath: str)` - Save configuration
- `load_configuration() -> Configuration` - Load configuration

## Utilities

### Logger

Logging utility with encryption support.

```python
from src.utils.logger import Logger

logger = Logger("ComponentName")

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### EncryptionManager

Encryption utility for data protection.

```python
from src.utils.encryption import EncryptionManager

manager = EncryptionManager(password="secret")

# Encrypt data
encrypted = manager.encrypt("sensitive data")

# Decrypt data
decrypted = manager.decrypt(encrypted)
```

### FallbackResponses

Predefined fallback responses for error handling.

```python
from src.utils.fallback_responses import FallbackResponses

response = FallbackResponses.get_response("speech_recognition_failed")
```

## Usage Examples

### Complete Conversation Flow

```python
from src.main import VaskApplication

# Initialize application
app = VaskApplication(config_path="config/default_config.yaml")
app.start()

# Start session
app.start_session("user-1")

# Process voice input (in real scenario, this would be from microphone)
import numpy as np
audio_data = np.random.randn(16000).astype(np.float32).tobytes()

# Get response
response = app.process_voice_input(audio_data)
print(f"Response: {response}")

# Get mood report
mood_report = app.get_mood_report("user-1")
print(f"Mood: {mood_report.primary_mood}")

# End session
app.end_session()

# Export conversation history
history = app.export_conversation_history("user-1", format="json")

# Stop application
app.stop()
```

### User Profile Management

```python
from src.main import VaskApplication

app = VaskApplication()
app.start()

# Get user profile
profile = app.get_user_profile("user-1")

# Update preferences
profile.communication_style = "formal"
profile.preferred_topics = ["technology", "science"]

# Save profile
app.context_manager.save_user_profile()

app.stop()
```

## Error Handling

All components include comprehensive error handling with fallback mechanisms:

- Speech recognition failures return user-friendly error messages
- AI model failures provide fallback responses
- Face detection failures allow voice-only mode
- Database errors attempt recovery from backups
- Configuration errors load defaults

See `src/utils/fallback_responses.py` for available fallback responses.
