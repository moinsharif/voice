# Vask - Technical Design Document

## Overview

Vask is a locally-operated, voice-based AI companion system that combines speech recognition, conversational AI, facial expression analysis, and mood detection to provide personalized, context-aware interactions. The system operates entirely offline using open-source models (Whisper for speech recognition, Llama 2 for AI responses, MediaPipe for face detection, Piper for text-to-speech) and stores all user data locally with AES-256 encryption.

The architecture prioritizes privacy, performance, and personalization through a modular design where components communicate via well-defined interfaces. The system learns from daily interactions to improve response quality and maintains separate user profiles for multi-user households.

## Architecture

### High-Level System Architecture

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
│  ┌───────────────────────────────────────────────────────────┐   │
│  │              Text-to-Speech Engine                        │   │
│  │  - Piper integration                                      │   │
│  │  - Voice selection & rate control                         │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │              Configuration System                         │   │
│  │  - YAML/JSON parsing                                      │   │
│  │  - Settings validation                                    │   │
│  │  - Runtime configuration updates                          │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input Flow**: User speaks → Speech Recognition Engine → Text → Context Manager
2. **Processing Flow**: Context Manager → AI Model Wrapper → Response generation
3. **Mood Analysis Flow**: Audio + Face Detection → Mood Analyzer → Mood classification
4. **Output Flow**: AI Response → Text-to-Speech Engine → Audio playback
5. **Learning Flow**: Session data → Learning System → User Profile updates
6. **Persistence Flow**: All data → Encryption → SQLite storage

### Module Interactions

- **Session Manager** orchestrates all components and manages lifecycle
- **Context Manager** acts as central hub for conversation state and user data
- **Persistence Layer** handles all data storage with encryption
- **Learning System** operates asynchronously on completed sessions
- **Configuration System** provides runtime settings to all components

## Components and Interfaces

### 1. Speech Recognition Engine

**Purpose**: Convert audio input to text with noise filtering and multi-language support.

**Technology**: Whisper (OpenAI's open-source model)

**Key Interfaces**:
```python
class SpeechRecognitionEngine:
    def start_listening() -> None
    def stop_listening() -> None
    def get_transcription() -> Transcription
    def set_language(language_code: str) -> None
    def apply_noise_filter(audio_data: bytes) -> bytes
```

**Responsibilities**:
- Capture audio from system microphone
- Apply noise filtering for background noise
- Transcribe audio to text with ≥85% accuracy
- Complete recognition within 3 seconds of speech completion
- Support multiple languages
- Handle recognition failures gracefully

**Error Handling**:
- Return user-friendly error messages on recognition failure
- Implement retry logic with exponential backoff
- Log failed recognition attempts for debugging

### 2. AI Model Wrapper

**Purpose**: Generate contextual responses using locally-stored language model.

**Technology**: Llama 2 7B (locally quantized)

**Key Interfaces**:
```python
class AIModelWrapper:
    def generate_response(context: ConversationContext, user_message: str) -> str
    def set_response_tone(tone: str) -> None
    def load_model() -> None
    def unload_model() -> None
    def is_model_available() -> bool
```

**Responsibilities**:
- Generate responses based on conversation context
- Consider user mood state in response generation
- Maintain context of last 10 exchanges
- Generate responses within 2 seconds
- Operate entirely offline
- Adapt tone based on user preferences

**Performance Considerations**:
- Use model quantization (4-bit or 8-bit) to reduce memory footprint
- Implement response caching for common queries
- Batch process when possible

### 3. Face Detection Module

**Purpose**: Detect faces and analyze facial expressions for mood inference.

**Technology**: OpenCV + MediaPipe Face Detection

**Key Interfaces**:
```python
class FaceDetectionModule:
    def start_camera() -> None
    def stop_camera() -> None
    def detect_faces() -> List[Face]
    def get_facial_landmarks(face: Face) -> List[Point]
    def analyze_expression(face: Face) -> Expression
    def is_camera_available() -> bool
```

**Responsibilities**:
- Access system webcam
- Detect faces in video frames
- Identify facial landmarks
- Classify expressions (happiness, sadness, anger, surprise, neutral)
- Process frames at 15 FPS minimum
- Gracefully handle missing faces
- Support disabling camera mode

**Performance Considerations**:
- Process frames asynchronously to avoid blocking main thread
- Implement frame skipping if processing falls behind
- Cache face detection results for 100ms intervals

### 4. Mood Analysis Engine

**Purpose**: Classify user emotional state from voice and facial expressions.

**Technology**: Custom analysis combining voice tone analysis and facial expression classification

**Key Interfaces**:
```python
class MoodAnalysisEngine:
    def analyze_mood(audio: bytes, face: Optional[Face]) -> Mood
    def get_mood_history(user_id: str, period: str) -> List[Mood]
    def generate_mood_report(user_id: str, period: str) -> MoodReport
    def correlate_mood_with_topics(user_id: str) -> Dict[str, float]
```

**Responsibilities**:
- Detect emotional state from voice tone and facial expressions
- Classify mood into: positive, neutral, negative, mixed
- Maintain mood history per session
- Generate mood summaries at session end
- Default to neutral when inconclusive
- Track mood patterns over time
- Correlate mood with conversation topics and times

**Mood Classification Logic**:
- Positive: Happy expression + upbeat voice tone
- Negative: Sad/angry expression + downbeat voice tone
- Neutral: Neutral expression + neutral voice tone
- Mixed: Conflicting signals between face and voice

### 5. Learning System

**Purpose**: Analyze daily interactions and improve response quality through pattern recognition.

**Technology**: Pattern matching and preference tracking

**Key Interfaces**:
```python
class LearningSystem:
    def analyze_day(user_id: str, date: str) -> LearningInsights
    def identify_patterns(interactions: List[Interaction]) -> List[Pattern]
    def update_user_profile(user_id: str, insights: LearningInsights) -> None
    def get_response_feedback_score(response_id: str) -> float
    def apply_learnings(user_id: str) -> None
```

**Responsibilities**:
- Analyze all interactions from completed day
- Identify patterns in user preferences and communication style
- Track response types that received positive feedback
- Update User Profile with learned preferences
- Apply previous day's learnings to response generation
- Run asynchronously at end of day

**Learning Patterns**:
- Topic preferences (topics user engages with most)
- Communication style (formal vs casual, verbose vs concise)
- Time-based patterns (when user is most active)
- Response type preferences (humor, technical detail, empathy)

### 6. Persistence Layer

**Purpose**: Store and retrieve all user data with encryption and integrity checks.

**Technology**: SQLite + AES-256 encryption

**Key Interfaces**:
```python
class PersistenceLayer:
    def save_conversation(session: Session) -> None
    def load_conversation(session_id: str) -> Session
    def save_user_profile(profile: UserProfile) -> None
    def load_user_profile(user_id: str) -> UserProfile
    def save_configuration(config: Configuration) -> None
    def load_configuration() -> Configuration
    def delete_conversation(session_id: str) -> None
    def search_conversations(query: SearchQuery) -> List[Session]
```

**Responsibilities**:
- Persist conversation history to SQLite
- Encrypt sensitive data at rest (AES-256)
- Load conversation history on session start
- Support searching by date, mood, keyword
- Securely delete conversations on request
- Maintain data integrity with checksums
- Handle data corruption with backup recovery
- Support data export in JSON/CSV formats

**Storage Schema**:
- Conversations table: session_id, user_id, timestamp, encrypted_data
- User profiles table: user_id, encrypted_profile_data
- Mood history table: user_id, timestamp, mood_classification
- Configuration table: key, value, last_updated

### 7. Text-to-Speech Engine

**Purpose**: Convert AI responses to natural-sounding audio output.

**Technology**: Piper (offline TTS)

**Key Interfaces**:
```python
class TextToSpeechEngine:
    def synthesize(text: str) -> bytes
    def play_audio(audio: bytes) -> None
    def set_voice(voice_id: str) -> None
    def set_speaking_rate(rate: float) -> None
    def get_available_voices() -> List[str]
    def is_enabled() -> bool
    def set_enabled(enabled: bool) -> None
```

**Responsibilities**:
- Convert text responses to audio
- Play audio through system speakers
- Support multiple voices and speaking rates
- Complete synthesis within 1 second per 100 words
- Support disabling audio output
- Operate entirely offline
- Handle text with special characters and punctuation

**Performance Targets**:
- Synthesis latency: <1 second per 100 words
- Audio playback: immediate start after synthesis

### 8. Session Manager

**Purpose**: Manage conversation lifecycle and coordinate all components.

**Technology**: State machine pattern

**Key Interfaces**:
```python
class SessionManager:
    def start_session(user_id: str) -> Session
    def end_session(session_id: str) -> None
    def pause_session(session_id: str) -> None
    def resume_session(session_id: str) -> None
    def process_user_input(session_id: str, input_data: InputData) -> Response
    def get_session_state(session_id: str) -> SessionState
    def replay_session(session_id: str) -> None
```

**Responsibilities**:
- Create new session records with timestamps
- Continuously listen for voice input during active session
- Begin recording on wake word or button press
- Pause/resume recording on user request
- Save session data to conversation history on end
- Support session replay
- Coordinate all components during session lifecycle

**Session States**:
- IDLE: Waiting for user initiation
- LISTENING: Capturing audio input
- PROCESSING: Generating response
- SPEAKING: Playing audio response
- PAUSED: Temporarily suspended
- ENDED: Session complete

### 9. Configuration System

**Purpose**: Parse, validate, and manage application settings.

**Technology**: YAML/JSON parsing with schema validation

**Key Interfaces**:
```python
class ConfigurationSystem:
    def parse_config_file(filepath: str) -> Configuration
    def validate_configuration(config: Configuration) -> ValidationResult
    def save_configuration(config: Configuration) -> None
    def load_configuration() -> Configuration
    def update_setting(key: str, value: Any) -> None
    def get_setting(key: str) -> Any
    def reset_to_defaults() -> None
```

**Responsibilities**:
- Parse YAML and JSON configuration files
- Validate configuration against schema
- Persist settings to local storage
- Support runtime configuration updates
- Provide clear error messages with line numbers
- Support configuration reset to defaults
- Handle configuration migrations for version upgrades

**Configurable Settings**:
- Language selection
- Voice and speaking rate
- Listening sensitivity
- Mood sensitivity
- Response tone
- Camera enable/disable
- Audio output enable/disable

## Data Models

### User Profile

```python
@dataclass
class UserProfile:
    user_id: str
    created_at: datetime
    last_interaction: datetime
    
    # Personalization
    communication_style: str  # "formal", "casual", "technical"
    preferred_topics: List[str]
    response_preferences: Dict[str, float]  # response_type -> preference_score
    
    # Mood patterns
    mood_history: List[MoodEntry]
    average_mood: str
    mood_trends: Dict[str, float]  # mood_type -> frequency
    
    # Learning data
    learned_preferences: Dict[str, Any]
    interaction_count: int
    last_learning_update: datetime
    
    # Settings
    language: str
    voice_id: str
    speaking_rate: float
    listening_sensitivity: float
    mood_sensitivity: float
```

### Conversation History

```python
@dataclass
class Session:
    session_id: str
    user_id: str
    created_at: datetime
    ended_at: Optional[datetime]
    
    exchanges: List[Exchange]
    mood_summary: MoodSummary
    metadata: Dict[str, Any]
    
    # Audio recording
    audio_data: Optional[bytes]  # encrypted
    transcript: str

@dataclass
class Exchange:
    timestamp: datetime
    user_message: str
    ai_response: str
    mood_detected: Mood
    response_feedback: Optional[float]  # 0.0-1.0 rating
```

### Mood Data

```python
@dataclass
class Mood:
    timestamp: datetime
    classification: str  # "positive", "neutral", "negative", "mixed"
    confidence: float  # 0.0-1.0
    
    # Contributing factors
    facial_expression: Optional[str]
    voice_tone: Optional[str]
    
    # Context
    conversation_topic: Optional[str]
    time_of_day: str

@dataclass
class MoodSummary:
    session_id: str
    primary_mood: str
    mood_transitions: List[Mood]
    average_confidence: float
    mood_stability: float  # 0.0-1.0, higher = more stable
```

### Session Data

```python
@dataclass
class SessionMetadata:
    duration_seconds: int
    exchange_count: int
    topics_discussed: List[str]
    user_initiated: bool
    completion_status: str  # "completed", "interrupted", "error"
    error_messages: List[str]
```

### Configuration Schema

```python
@dataclass
class Configuration:
    # System
    version: str
    offline_mode: bool
    
    # Audio
    language: str
    voice_id: str
    speaking_rate: float  # 0.5-2.0
    listening_sensitivity: float  # 0.0-1.0
    
    # Features
    enable_camera: bool
    enable_audio_output: bool
    enable_learning: bool
    
    # Performance
    max_context_exchanges: int  # default 10
    response_timeout_seconds: int  # default 2
    
    # Privacy
    encryption_enabled: bool
    auto_delete_after_days: Optional[int]
    
    # Model paths
    whisper_model_path: str
    llama_model_path: str
    piper_model_path: str
```

## API/Interface Design

### Main Application Interface

```python
class VaskApplication:
    def __init__(self, config_path: str):
        """Initialize Vask with configuration file."""
        
    def start(self) -> None:
        """Start the application and begin listening."""
        
    def stop(self) -> None:
        """Stop the application gracefully."""
        
    def process_voice_input(audio_data: bytes) -> Response:
        """Process voice input and return response."""
        
    def get_user_profile(user_id: str) -> UserProfile:
        """Retrieve user profile."""
        
    def update_user_preferences(user_id: str, preferences: Dict) -> None:
        """Update user preferences."""
        
    def get_mood_report(user_id: str, period: str) -> MoodReport:
        """Generate mood report for specified period."""
        
    def export_conversation_history(user_id: str, format: str) -> bytes:
        """Export conversation history in JSON or CSV format."""
```

### Component Interfaces

**Speech Recognition**:
```python
class ISpeechRecognition:
    def transcribe(audio_data: bytes) -> TranscriptionResult
    def set_language(language_code: str) -> None
```

**AI Model**:
```python
class IAIModel:
    def generate(context: ConversationContext, prompt: str) -> str
    def set_tone(tone: str) -> None
```

**Face Detection**:
```python
class IFaceDetection:
    def detect(frame: bytes) -> List[Face]
    def analyze_expression(face: Face) -> Expression
```

**Mood Analysis**:
```python
class IMoodAnalysis:
    def analyze(audio: bytes, face: Optional[Face]) -> Mood
    def get_history(user_id: str) -> List[Mood]
```

**Persistence**:
```python
class IPersistence:
    def save(key: str, data: bytes) -> None
    def load(key: str) -> bytes
    def delete(key: str) -> None
    def search(query: SearchQuery) -> List[bytes]
```

### Configuration Interface

```python
class IConfiguration:
    def parse(filepath: str) -> Configuration
    def validate(config: Configuration) -> ValidationResult
    def save(config: Configuration) -> None
    def get(key: str) -> Any
    def set(key: str, value: Any) -> None
```

## Technology Choices and Rationale

### Speech Recognition: Whisper

**Why Whisper**:
- Offline operation (no API calls required)
- Robust to accents and background noise
- Supports 99 languages
- Open-source and freely available
- Achieves 85%+ accuracy on clear speech
- Multiple model sizes available (tiny to large)

**Trade-offs**:
- Larger models require more VRAM
- Inference slower than cloud APIs
- Requires local model storage (~1-3GB depending on size)

### AI Model: Llama 2 7B

**Why Llama 2 7B**:
- Fully open-source with commercial license
- Runs locally on consumer hardware (4GB+ RAM)
- Good balance of quality and performance
- Quantization support (4-bit, 8-bit) reduces memory
- Active community and tooling
- Suitable for conversational tasks

**Trade-offs**:
- Smaller than larger models (13B, 70B)
- Requires quantization for consumer hardware
- Slower inference than cloud APIs
- Needs fine-tuning for best personalization

### Face Detection: OpenCV + MediaPipe

**Why MediaPipe**:
- Lightweight and fast (real-time on CPU)
- Accurate facial landmark detection
- Expression classification built-in
- Cross-platform support
- Open-source

**Why OpenCV**:
- Mature, well-tested computer vision library
- Efficient video capture and frame processing
- Extensive documentation and community support

### Text-to-Speech: Piper

**Why Piper**:
- Offline operation (no API calls)
- Fast synthesis (<1 second per 100 words)
- Multiple voices available
- Open-source
- Lightweight model (~50MB per voice)
- Natural-sounding output

### Data Storage: SQLite + AES-256

**Why SQLite**:
- Serverless, file-based database
- No external dependencies
- ACID compliance for data integrity
- Efficient for local storage
- Easy backup and migration

**Why AES-256**:
- Military-grade encryption
- Industry standard for data protection
- Widely supported in Python (cryptography library)
- Protects data at rest

### Configuration: YAML/JSON

**Why YAML/JSON**:
- Human-readable formats
- Easy to parse and validate
- Version control friendly
- Standard formats for data exchange
- Support for complex nested structures

## Performance Considerations

### Memory Optimization

**Target**: ≤2GB RAM during normal operation

**Strategies**:
- Use model quantization (4-bit or 8-bit) for Llama 2
- Implement lazy loading for models (load only when needed)
- Limit conversation context to last 10 exchanges
- Stream audio processing instead of buffering entire files
- Implement garbage collection for completed sessions

**Memory Breakdown** (estimated):
- Llama 2 7B (4-bit quantized): ~2GB
- Whisper (base model): ~500MB
- MediaPipe + OpenCV: ~200MB
- Application state: ~100MB
- **Total**: ~2.8GB (with optimization)

### CPU/GPU Utilization

**Strategies**:
- Process audio asynchronously to avoid blocking UI
- Implement frame skipping in face detection if processing falls behind
- Use GPU acceleration if available (CUDA/Metal)
- Batch process when possible
- Implement response caching for common queries

**Performance Targets**:
- Speech recognition: Complete within 3 seconds of speech end
- AI response generation: Complete within 2 seconds
- Face detection: Process at 15 FPS minimum
- TTS synthesis: <1 second per 100 words

### Response Time Targets

| Operation | Target | Strategy |
|-----------|--------|----------|
| Speech recognition | 3 seconds | Streaming recognition, early termination |
| AI response generation | 2 seconds | Model quantization, response caching |
| Face detection | 15 FPS | Async processing, frame skipping |
| TTS synthesis | 1 sec/100 words | Piper optimization, streaming playback |
| Conversation retrieval | 500ms | SQLite indexing, caching |

### Caching Strategies

- **Response Cache**: Cache AI responses for identical queries (TTL: 1 hour)
- **Face Detection Cache**: Cache face detection results for 100ms intervals
- **User Profile Cache**: Keep loaded profile in memory during session
- **Configuration Cache**: Cache parsed configuration in memory

## Security & Privacy

### Data Encryption at Rest

**Implementation**:
- All sensitive data encrypted with AES-256-CBC
- Encryption keys derived from user password using PBKDF2
- Separate encryption keys per user
- Encrypted data stored in SQLite BLOB fields

**Data Encrypted**:
- Conversation history
- User profiles
- Mood history
- Audio recordings

### Local-Only Operation

**Guarantees**:
- No internet connectivity required
- No external API calls
- All processing on local machine
- No data transmission outside device

**Verification**:
- Network access disabled for all components
- Configuration validation ensures offline mode
- Error messages if external resources required

### User Data Isolation

**Multi-User Support**:
- Separate encryption keys per user
- Isolated conversation histories
- Independent user profiles
- Face detection for user identification

**Data Separation**:
- User ID as primary key in all tables
- Encryption keys include user ID
- Query filters ensure user-specific data access

### Configuration Security

**Sensitive Settings**:
- Encryption keys stored securely
- Configuration files encrypted if containing sensitive data
- Default secure settings (encryption enabled, offline mode)
- Validation prevents insecure configurations

## Error Handling Strategy

### Graceful Degradation

**Component Failures**:
- Speech recognition fails → Request user retry with friendly message
- AI model fails → Provide fallback response ("I'm having trouble thinking right now...")
- Face detection fails → Continue with voice-only mood detection
- TTS fails → Display text response instead
- Camera unavailable → Continue without visual input

**System Failures**:
- Database corruption → Attempt recovery from backups
- Configuration invalid → Load defaults and notify user
- Model missing → Provide clear installation instructions
- Insufficient memory → Reduce processing quality gracefully

### Fallback Mechanisms

```python
class FallbackResponses:
    SPEECH_RECOGNITION_FAILED = "I didn't catch that. Could you please repeat?"
    AI_MODEL_FAILED = "I'm having trouble thinking right now. Let me try again."
    FACE_DETECTION_FAILED = "I can't see you right now, but I'm still listening."
    TTS_FAILED = "[Response displayed as text]"
    DATABASE_ERROR = "I'm having trouble remembering. Let's start fresh."
```

### Error Logging

**Log Levels**:
- ERROR: Critical failures requiring user attention
- WARNING: Degraded functionality but system continues
- INFO: Normal operation milestones
- DEBUG: Detailed diagnostic information

**Log Storage**:
- Logs stored locally in encrypted format
- Automatic rotation (keep last 30 days)
- User can export logs for debugging
- Sensitive data redacted from logs

**Error Recovery**:
- Automatic retry with exponential backoff
- Circuit breaker pattern for repeated failures
- Graceful shutdown if critical component fails
- Attempt recovery before notifying user

## Testing Strategy

### Unit Testing Approach

**Focus Areas**:
- Individual component functionality
- Edge cases and error conditions
- Data validation and transformation
- Configuration parsing and validation

**Example Unit Tests**:
- Speech recognition with various audio qualities
- AI response generation with different contexts
- Mood classification with conflicting signals
- Configuration parsing with invalid inputs
- Data serialization/deserialization

**Testing Framework**: pytest with fixtures for mocking components

### Integration Testing

**Focus Areas**:
- Component interactions
- End-to-end conversation flow
- Data persistence and retrieval
- Multi-user scenarios

**Test Scenarios**:
- Complete conversation session (input → processing → output)
- User profile creation and updates
- Conversation history persistence and retrieval
- Mood analysis across multiple sessions
- Configuration changes during runtime

### Property-Based Testing

Property-based testing validates universal properties across many generated inputs, ensuring correctness guarantees.

