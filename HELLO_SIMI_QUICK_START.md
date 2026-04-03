# Hello Simi AI - Quick Start Guide

## Installation

No additional installation needed. Uses existing dependencies from `requirements.txt`.

## Running the Application

```bash
python hello_simi_ai_gui.py
```

## First Time Setup

1. Application initializes components:
   - Persistence layer (SQLite)
   - Context manager
   - AI model
   - User profile

2. Whisper model loads (first time may take a minute)

3. Auto mode starts automatically

## Basic Usage

### Manual Recording
1. Click **"🎤 Start Recording"** button
2. Speak your message
3. Wait for 3 seconds of silence (auto-stop)
4. Transcription appears in "Transcription" box
5. AI response appears in "AI Response" box
6. Response is spoken aloud

### Auto Mode
- **Enabled by default** on startup
- Continuous loop: Record → Transcribe → Respond → Repeat
- Click **"Auto Mode"** checkbox to toggle

### Manual Transcription
1. Record audio manually
2. Click **"📝 Transcribe"** button
3. Transcription appears

### Playback
1. Record audio
2. Click **"🔊 Playback"** button
3. Hear the recorded audio

### Export History
1. Click **"💾 Export"** button
2. Saves to `hello_simi_history_YYYYMMDD_HHMMSS.txt`

### Clear All
1. Click **"🗑️ Clear"** button
2. Clears transcription, response, and history

## System Info Display

Shows:
- User ID
- Session ID
- AI Model status
- Response tone
- Context size
- Number of conversations

## Troubleshooting

### Whisper Model Not Loading
```
Error: "Whisper model not loaded"
Solution: Check internet connection, model will download on first run
```

### No Audio Recorded
```
Error: "No audio recorded"
Solution: Check microphone is connected and working
```

### AI Response Not Generated
```
Error: "AI components not initialized"
Solution: Check console for initialization errors
```

### Database Error
```
Error: "Failed to save conversation"
Solution: Check disk space, ensure write permissions
```

## Testing Checklist

### Day 1 - Basic Features
- [ ] Application starts without errors
- [ ] Recording works
- [ ] Transcription works
- [ ] AI response generated
- [ ] Response spoken aloud
- [ ] History displayed
- [ ] Export works

### Day 2 - Auto Mode
- [ ] Auto mode runs for 10 minutes
- [ ] No crashes
- [ ] Responses make sense
- [ ] History accumulates

### Day 3 - Extended Testing
- [ ] Auto mode runs for 30+ minutes
- [ ] No resource leak (recording still works)
- [ ] Database stores all conversations
- [ ] No AI voice recorded in transcription

### Day 4 - Comparison
- [ ] Compare voice recognition quality with vask_gui.py
- [ ] Check response quality
- [ ] Verify context is maintained

## Key Differences from vask_gui.py

| Feature | vask_gui.py | hello_simi_ai_gui.py |
|---------|-------------|----------------------|
| Recording | ✅ | ✅ |
| Transcription | ✅ | ✅ |
| AI Response | Simple | Context-aware |
| Database | vask_data.db | hello_simi_data.db |
| Context | None | Full context tracking |
| User Profile | None | Tracked |

## Database Location

- **vask_gui.py**: `vask_data.db`
- **hello_simi_ai_gui.py**: `hello_simi_data.db`

They don't interfere with each other.

## Logs

Check console output for:
- Component initialization status
- Transcription results
- AI response generation
- Database operations
- Errors and warnings

## Performance

Expected performance:
- Recording: Real-time
- Transcription: 2-5 seconds (depends on audio length)
- AI Response: <1 second (cached responses)
- TTS: 2-10 seconds (depends on response length)

## Tips

1. **Speak clearly** for better transcription
2. **Wait for beeps** - start beep (800Hz) = recording started, stop beep (1200Hz) = recording stopped
3. **Auto mode** - let it run for extended testing
4. **Check history** - verify conversations are stored correctly
5. **Export regularly** - backup your conversation history

## Next Steps

After testing Phase 1:
1. Report any issues found
2. Compare with vask_gui.py
3. Decide on Phase 2 features (SessionManager, MoodAnalysisEngine)
4. Plan full VaskApplication integration

## Support

If you encounter issues:
1. Check console output for error messages
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Check microphone is working
4. Ensure sufficient disk space
5. Check database file permissions

## Files

- `hello_simi_ai_gui.py` - Main application
- `hello_simi_data.db` - Database (created on first run)
- `hello_simi_history_*.txt` - Exported histories
