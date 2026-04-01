# Voice Recording Guide

## Where to Save Audio Files

Save all audio files in the **`audio_samples`** folder:
```
C:\Backup Files\personal\Personal Project\voice\audio_samples\
```

## How to Record Voice

### Option 1: Windows Sound Recorder (Easiest)

1. Press **Windows + R**
2. Type: `soundrecorder`
3. Press **Enter**
4. Click **"Start Recording"** button
5. Speak your message (e.g., "hello", "how are you")
6. Click **"Stop Recording"** button
7. Save the file as **WAV format** in the `audio_samples` folder
   - Filename example: `hello.wav`, `test.wav`, `my_voice.wav`

### Option 2: Audacity (Free, More Features)

1. Download from: https://www.audacityteam.org/
2. Open Audacity
3. Click **"Record"** button (red circle)
4. Speak your message
5. Click **"Stop"** button (black square)
6. Go to **File → Export → Export as WAV**
7. Save in the `audio_samples` folder

### Option 3: Online Recorder

1. Go to: https://online-voice-recorder.com/
2. Click **"Allow"** to access microphone
3. Click **"Start Recording"**
4. Speak your message
5. Click **"Stop Recording"**
6. Download as WAV
7. Save in the `audio_samples` folder

## After Recording

1. Run the test script:
   ```bash
   python test_voice_minimal.py
   ```

2. Choose option **1** to transcribe

3. The script will:
   - Find your audio file
   - Transcribe it using Whisper
   - Show what you said
   - Detect keywords

## Example

```
>>> Available Audio Files
Found 1 audio files in 'audio_samples' folder:
  1. hello.wav (0.05 MB)

>>> Transcription
Transcribing: hello.wav

📝 Transcription Result:
   "hello how are you"

>>> Analysis
Text Statistics:
  Characters: 18
  Words: 4

Keyword Detection:
  ✓ hello
```

## Troubleshooting

### "No audio files found"
- Make sure you saved the file in the `audio_samples` folder
- Check the file extension is `.wav` or `.mp3`
- Refresh and try again

### "Whisper not installed"
- Run: `pip install openai-whisper`

### "SmartScreen blocked"
- This is Windows security
- The script is safe, it just records and transcribes
- You can disable SmartScreen or use a different recorder

## File Format

- **Recommended**: WAV format (`.wav`)
- **Also supported**: MP3 format (`.mp3`)
- **Sample rate**: 16000 Hz (standard)
- **Duration**: Any length (1 second to several minutes)

## Next Steps

After recording and transcribing:
1. The system will detect keywords
2. You can integrate with the main Vask application
3. The AI will generate responses based on your input
