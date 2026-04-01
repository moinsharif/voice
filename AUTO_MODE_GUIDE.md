# Vask Auto Mode Guide

## What is Auto Mode?

Auto Mode enables continuous, hands-free conversation with Vask. Once enabled, the system will:

1. **Listen** - Start recording your voice
2. **Detect Silence** - Automatically stop recording after 3 seconds of silence
3. **Transcribe** - Convert your speech to text
4. **Respond** - Generate an AI response
5. **Repeat** - Wait 3 seconds, then listen again

## How to Use Auto Mode

### Starting Auto Mode
1. Click the **"Auto Mode"** checkbox in the GUI
2. The system will display: "Auto mode enabled. Starting continuous conversation..."
3. Start speaking - the system will begin recording

### During Auto Mode
- **Recording**: The status shows "🎤 Auto mode: Recording..."
- **Transcribing**: The status shows "📝 Auto mode: Transcribing..."
- **Responding**: The status shows "🤖 Auto mode: Generating response..."
- **Waiting**: The status shows "⏳ Auto mode: Waiting 3 seconds before next..."

### Stopping Auto Mode
1. Click the **"Auto Mode"** checkbox again to disable it
2. The system will stop recording and exit the loop
3. Status will show: "Auto mode disabled."

## How It Works

### Recording Phase
- Vask listens for your voice
- Automatically stops after **3 seconds of silence**
- Maximum recording time: 5 minutes (safety limit)

### Transcription Phase
- Your speech is converted to text using Whisper
- Language is auto-detected or uses your selected language
- Transcription appears in the "Transcription" text box

### Response Generation Phase
- Vask analyzes your input
- Generates an appropriate response
- Response appears in the "Response" text box
- Conversation is added to history

### Waiting Phase
- System waits **3 seconds** before listening again
- This gives you time to hear the response
- You can interrupt by clicking "Auto Mode" to disable it

## Tips for Best Results

1. **Speak Clearly**: Enunciate your words for better transcription
2. **Pause Between Sentences**: Use natural pauses to let the system detect silence
3. **Quiet Environment**: Background noise may affect transcription
4. **Wait for Response**: Let the system finish responding before speaking again
5. **Monitor Status**: Watch the status bar to understand what's happening

## Troubleshooting

### Auto Mode Not Starting
- Ensure Whisper model is loaded (check status bar)
- Check that your microphone is working
- Try clicking "Auto Mode" again

### Recording Stops Too Early
- The system detected 3 seconds of silence
- Speak more continuously or reduce silence threshold in code
- Check microphone sensitivity

### No Transcription
- Ensure audio was recorded (check "Playback" button)
- Try recording again with clearer speech
- Check that Whisper model is loaded

### Response Not Generated
- Check that your speech was transcribed
- Ensure the AI response generation is working
- Check the "Response" text box for any error messages

## Configuration

To adjust auto mode behavior, edit these values in `vask_gui.py`:

```python
self.silence_threshold = 0.02      # Lower = more sensitive to silence
self.silence_duration = 3          # Seconds of silence before stopping
```

## Example Conversation

```
User: "Hello"
Vask: "Hello! Nice to meet you. How can I help you today?"
[3 second wait]

User: "What time is it?"
Vask: "The current time is 02:30 PM."
[3 second wait]

User: "Goodbye"
Vask: "Goodbye! Have a great day!"
[Auto mode stops or continues...]
```

## Performance Notes

- First run may be slow as models are loaded
- Subsequent runs are faster due to model caching
- Auto mode uses significant CPU during transcription
- Ensure adequate system resources (RAM, CPU)

## Disabling Auto Mode

To disable auto mode:
1. Uncheck the "Auto Mode" checkbox
2. Or close the application
3. The system will gracefully stop the loop

---

**Enjoy hands-free conversation with Vask!**
