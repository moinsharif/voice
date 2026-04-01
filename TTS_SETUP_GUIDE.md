# Text-to-Speech (TTS) Setup Guide for Vask

## Overview

Vask now supports voice output! The AI responses will be spoken aloud using Text-to-Speech technology.

## Supported TTS Engines

### 1. Piper TTS (Recommended - Offline, High Quality)
- **Pros**: Offline, high-quality voice, fast
- **Cons**: Requires separate installation
- **Best for**: Production use, offline operation

### 2. pyttsx3 (Fallback - Built-in)
- **Pros**: Works out of the box, no extra setup
- **Cons**: Lower quality, uses system voices
- **Best for**: Quick testing, fallback option

## Installation

### Option 1: Using Piper TTS (Recommended)

#### Windows
```bash
# Install piper-tts
pip install piper-tts

# Download voice model
piper --download-dir models/piper --voice en_US-lessac-medium
```

#### macOS
```bash
# Install piper-tts
pip install piper-tts

# Download voice model
piper --download-dir models/piper --voice en_US-lessac-medium
```

#### Linux
```bash
# Install piper-tts
pip install piper-tts

# Download voice model
piper --download-dir models/piper --voice en_US-lessac-medium
```

### Option 2: Using pyttsx3 (Automatic Fallback)

pyttsx3 is automatically installed with requirements.txt and requires no additional setup.

## Configuration

### Piper TTS Settings

Edit `vask_gui.py` to customize Piper:

```python
# In load_tts_engine() method
subprocess.run([
    "piper",
    "--model", "en_US-lessac-medium",  # Change voice here
    "--output-file", temp_file,
    "--speaker", "0",                   # Speaker ID (if multi-speaker model)
    "--length-scale", "1.0"             # Speed (0.5-2.0)
])
```

### pyttsx3 Settings

Edit `vask_gui.py` to customize pyttsx3:

```python
# In load_tts_engine() method
self.tts_engine.setProperty('rate', 150)      # Speed (50-300)
self.tts_engine.setProperty('volume', 0.9)    # Volume (0.0-1.0)
self.tts_engine.setProperty('voice', voice_id) # Voice selection
```

## Available Piper Voices

Popular English voices:

| Voice ID | Description | Quality |
|----------|-------------|---------|
| en_US-lessac-medium | Female, clear | High |
| en_US-libritts-high | Female, natural | Very High |
| en_US-glow-tts | Female, expressive | High |
| en_GB-alba-medium | British female | High |
| en_GB-aru-medium | British female | High |

Download additional voices:
```bash
piper --download-dir models/piper --voice en_GB-alba-medium
```

## Usage

### Manual Mode
1. Record audio or type text
2. Click "Generate Response"
3. Response will be spoken automatically

### Auto Mode
1. Enable "Auto Mode"
2. Speak to Vask
3. Response will be transcribed and spoken
4. System waits 3 seconds before listening again

## Troubleshooting

### No Sound Output
- Check system volume
- Verify speakers are connected
- Test with `python -c "import pyttsx3; pyttsx3.init().say('test'); pyttsx3.init().runAndWait()"`

### Piper Not Found
- Ensure piper is installed: `pip install piper-tts`
- Check PATH: `which piper` (Linux/Mac) or `where piper` (Windows)
- Fallback to pyttsx3 will be used automatically

### Poor Audio Quality
- Try different voice: `piper --voice en_US-libritts-high`
- Adjust speed: `--length-scale 0.9` (faster) or `1.1` (slower)
- Check system audio settings

### TTS Slow
- Piper first run downloads model (~100MB)
- Subsequent runs are faster
- pyttsx3 is faster but lower quality

## Performance Tips

1. **First Run**: Piper downloads voice model (~100MB) - this is normal
2. **Caching**: Models are cached locally for faster subsequent runs
3. **CPU Usage**: TTS uses CPU during synthesis - expect brief spike
4. **Memory**: Piper uses ~200MB RAM, pyttsx3 uses ~50MB

## Advanced Configuration

### Custom Voice Speed

Edit `_speak_response()` method:

```python
# For piper
subprocess.run([
    "piper",
    "--model", "en_US-lessac-medium",
    "--output-file", temp_file,
    "--length-scale", "0.8"  # 0.8 = 20% faster
])

# For pyttsx3
self.tts_engine.setProperty('rate', 200)  # Faster
```

### Multiple Voices

```python
def set_voice(self, voice_name):
    """Switch between voices."""
    if isinstance(self.tts_engine, str) and self.tts_engine == "piper":
        self.current_voice = voice_name
    else:
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[0].id)
```

## Testing TTS

### Test Piper
```bash
echo "Hello, this is a test" | piper --model en_US-lessac-medium --output-file test.wav
```

### Test pyttsx3
```python
import pyttsx3
engine = pyttsx3.init()
engine.say("Hello, this is a test")
engine.runAndWait()
```

## Disabling TTS

To disable TTS output:

1. Edit `vask_gui.py`
2. In `generate_response()`, comment out:
   ```python
   # thread = threading.Thread(target=self._speak_response, args=(response,))
   # thread.daemon = True
   # thread.start()
   ```

Or set `self.tts_engine = None` in `load_tts_engine()`.

## System Requirements

- **Piper**: 200MB disk space, 200MB RAM, 1-2 seconds per response
- **pyttsx3**: 50MB RAM, <1 second per response
- **Audio Output**: Working speakers/headphones

## FAQ

**Q: Can I use different voices?**
A: Yes! Download different Piper voices or configure pyttsx3 voices.

**Q: Is TTS offline?**
A: Yes! Both Piper and pyttsx3 work completely offline.

**Q: Can I adjust speech speed?**
A: Yes! See "Advanced Configuration" section above.

**Q: Why is first run slow?**
A: Piper downloads voice model (~100MB) on first use. Subsequent runs are fast.

**Q: Can I use both Piper and pyttsx3?**
A: Yes! The system automatically falls back to pyttsx3 if Piper is unavailable.

---

**Enjoy voice interaction with Vask!**
