# Hello Simi AI - Integrated GUI

## Overview

`hello_simi_ai_gui.py` is a new integrated GUI that combines:
- **Recording logic** from `vask_gui.py` (proven to work)
- **AI components** from `main.py` (spec-based architecture)

This allows us to test `main.py` components in real-life scenarios without breaking existing code.

## Architecture

```
hello_simi_ai_gui.py
├── GUI Layer (from vask_gui.py)
│   ├── Recording with silence detection
│   ├── Transcription display
│   ├── Response display
│   ├── Auto mode
│   └── History management
│
└── Backend (from main.py)
    ├── PersistenceLayer (SQLite database)
    ├── ContextManager (conversation context)
    ├── AIModelWrapper (response generation)
    └── ConversationContext (context management)
```

## Phase 1: Basic Integration

Currently implemented:
- ✅ Recording from `vask_gui.py`
- ✅ Transcription with Whisper
- ✅ AI response generation using `AIModelWrapper`
- ✅ Context management using `ContextManager`
- ✅ Auto mode
- ✅ History tracking
- ✅ Database persistence

## How to Run

```bash
python hello_simi_ai_gui.py
```

## Key Features

### 1. **Recording**
- Same recording logic as `vask_gui.py`
- Silence detection (3 seconds)
- PyAudio resource cleanup (fixes resource leak)

### 2. **AI Response Generation**
- Uses `AIModelWrapper` from `main.py`
- Maintains conversation context
- Response caching (1 hour TTL)

### 3. **Context Management**
- Uses `ContextManager` from `main.py`
- Tracks user profile
- Maintains conversation history
- Stores in SQLite database

### 4. **Auto Mode**
- Continuous recording → transcription → response → repeat
- Same as `vask_gui.py`

### 5. **Database**
- Separate database: `hello_simi_data.db`
- Doesn't interfere with `vask_data.db`

## Testing Checklist

### Phase 1 Tests (Current)
- [ ] Recording works without resource leak (20+ minutes)
- [ ] Transcription accurate
- [ ] AI response generation works
- [ ] Context is maintained across exchanges
- [ ] Auto mode works continuously
- [ ] Database stores conversations
- [ ] History export works
- [ ] No AI voice recorded during TTS

### Phase 2 Tests (Future)
- [ ] SessionManager integration
- [ ] MoodAnalysisEngine integration
- [ ] User profile learning
- [ ] Mood reporting

### Phase 3 Tests (Future)
- [ ] SpeechRecognitionEngine from main.py
- [ ] Full VaskApplication integration

## Debugging

### Check AI Model
```python
# In hello_simi_ai_gui.py
if self.ai_model:
    print(self.ai_model.get_model_info())
```

### Check Context Manager
```python
if self.context_manager:
    print(self.context_manager.get_model_info())
```

### Check Database
```bash
sqlite3 hello_simi_data.db
.tables
SELECT * FROM conversations;
```

## Differences from vask_gui.py

| Feature | vask_gui.py | hello_simi_ai_gui.py |
|---------|-------------|----------------------|
| Recording | ✅ | ✅ |
| Transcription | ✅ | ✅ |
| AI Response | Simple | Uses AIModelWrapper |
| Context | In-memory | ContextManager + DB |
| Database | vask_data.db | hello_simi_data.db |
| Session Management | None | ContextManager |
| User Profile | None | Tracked |
| Mood Analysis | None | Ready for Phase 2 |

## Next Steps

1. **Test Phase 1** - Verify all basic features work
2. **Debug Issues** - Fix any problems found
3. **Phase 2** - Add SessionManager and MoodAnalysisEngine
4. **Phase 3** - Full VaskApplication integration

## Notes

- `vask_gui.py` and `main.py` remain unchanged
- `hello_simi_ai_gui.py` is a new experimental file
- If issues occur, we can always revert to `vask_gui.py`
- Database is separate to avoid conflicts
