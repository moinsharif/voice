"""
Vask Voice AI - Graphical User Interface with Auto Mode
Real-time voice recording, transcription, and AI response
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import numpy as np
from datetime import datetime

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.main import VaskApplication


class VaskGUI:
    """Graphical User Interface for Vask Voice AI."""
    
    def __init__(self, root):
        """Initialize GUI."""
        self.root = root
        self.root.title("Vask - Voice AI Companion")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        
        # Application
        self.app = None
        self.is_recording = False
        self.audio_data = None
        self.sample_rate = None
        self.whisper_model = None
        self.tts_engine = None
        self.conversation_history = []
        self.silence_threshold = 0.02
        self.silence_duration = 3
        self.auto_mode_active = False
        self.auto_mode_stop_event = threading.Event()
        self.tts_speaking = False  # Track if TTS is currently speaking
        self.tts_complete_event = threading.Event()  # Signal when TTS is done
        
        # Create UI
        self.create_ui()
        
        # Initialize app and load model
        self.initialize_app()
        self.load_whisper_model()
        
        # Start auto mode by default
        self.root.after(2000, self._start_auto_mode_on_init)
    
    def create_ui(self):
        """Create user interface."""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🎤 Vask - Voice AI Companion",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            font=("Arial", 12),
            foreground="green"
        )
        self.status_label.pack()
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Record button
        self.record_btn = ttk.Button(
            control_frame,
            text="🎤 Start Recording",
            command=self.toggle_recording
        )
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        # Playback button
        self.playback_btn = ttk.Button(
            control_frame,
            text="🔊 Playback",
            command=self.playback_audio,
            state=tk.DISABLED
        )
        self.playback_btn.pack(side=tk.LEFT, padx=5)
        
        # Transcribe button
        self.transcribe_btn = ttk.Button(
            control_frame,
            text="📝 Transcribe",
            command=self.transcribe_audio,
            state=tk.DISABLED
        )
        self.transcribe_btn.pack(side=tk.LEFT, padx=5)
        
        # Language selection
        lang_frame = ttk.Frame(control_frame)
        lang_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT, padx=2)
        
        self.language_var = tk.StringVar(value="en")
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=["en", "bn", "hi", "es", "fr"],
            state="readonly",
            width=5
        )
        lang_combo.pack(side=tk.LEFT, padx=2)
        
        # Auto mode checkbox
        self.auto_mode_var = tk.BooleanVar(value=True)  # Enable by default
        auto_check = ttk.Checkbutton(
            control_frame,
            text="🤖 Auto Mode",
            variable=self.auto_mode_var,
            command=self.toggle_auto_mode
        )
        auto_check.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = ttk.Button(
            control_frame,
            text="🗑️ Clear",
            command=self.clear_all
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear Cache button
        cache_btn = ttk.Button(
            control_frame,
            text="🧹 Clear Cache",
            command=self.clear_cache
        )
        cache_btn.pack(side=tk.LEFT, padx=5)
        
        # Help button
        help_btn = ttk.Button(
            control_frame,
            text="❓ Help",
            command=self.show_help
        )
        help_btn.pack(side=tk.LEFT, padx=5)
        
        # Transcription frame
        trans_frame = ttk.LabelFrame(main_frame, text="Transcription", padding="10")
        trans_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.transcription_text = scrolledtext.ScrolledText(
            trans_frame,
            height=3,
            width=80,
            font=("Arial", 11),
            state=tk.DISABLED
        )
        self.transcription_text.pack(fill=tk.BOTH, expand=True)
        
        # Analysis frame
        analysis_frame = ttk.LabelFrame(main_frame, text="Analysis", padding="10")
        analysis_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.analysis_text = scrolledtext.ScrolledText(
            analysis_frame,
            height=3,
            width=80,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        
        # AI Response frame
        response_frame = ttk.LabelFrame(main_frame, text="AI Response", padding="10")
        response_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.response_text = scrolledtext.ScrolledText(
            response_frame,
            height=2,
            width=80,
            font=("Arial", 11),
            state=tk.DISABLED
        )
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # History frame
        history_frame = ttk.LabelFrame(main_frame, text="Conversation History", padding="10")
        history_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            height=3,
            width=80,
            font=("Arial", 9),
            state=tk.DISABLED
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=1)
        main_frame.rowconfigure(5, weight=1)
        main_frame.rowconfigure(6, weight=1)
    
    def initialize_app(self):
        """Initialize Vask application."""
        try:
            self.update_status("Initializing Vask...", "blue")
            self.app = VaskApplication()
            
            # Check offline operation - show warning if models missing
            offline_status = self.app.verify_offline_operation()
            if not offline_status:
                model_report = self.app.get_offline_verification_report()
                response = messagebox.askyesno(
                    "Missing Models",
                    f"Some models are missing:\n\n{model_report}\n\nContinue anyway?",
                    icon=messagebox.WARNING
                )
                if not response:
                    self.update_status("Initialization cancelled", "red")
                    return
            
            self.app.start()
            self.update_status("Ready", "green")
        except Exception as e:
            self.update_status(f"Error: {e}", "red")
            messagebox.showerror("Error", f"Failed to initialize: {e}")
    
    def load_whisper_model(self):
        """Load Whisper model once and cache it."""
        try:
            self.update_status("Loading Whisper model (first time only)...", "blue")
            import whisper
            self.whisper_model = whisper.load_model("base")
            self.update_status("Whisper model loaded", "green")
            
            # Load TTS engine
            self.load_tts_engine()
        except Exception as e:
            self.update_status(f"Error loading model: {e}", "red")
            messagebox.showerror("Error", f"Failed to load Whisper model: {e}")
    
    def load_tts_engine(self):
        """Load Text-to-Speech engine."""
        try:
            self.update_status("Loading TTS engine...", "blue")
            
            # Try pyttsx3 first (most reliable)
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.update_status("pyttsx3 TTS loaded", "green")
                return
            except Exception as e:
                print(f"pyttsx3 error: {e}")
            
            # Fallback to piper
            try:
                import subprocess
                result = subprocess.run(["piper", "--help"], capture_output=True)
                if result.returncode == 0:
                    self.tts_engine = "piper"
                    self.update_status("Piper TTS loaded", "green")
                    return
            except:
                pass
            
            self.update_status("Warning: TTS not available", "orange")
            self.tts_engine = None
        except Exception as e:
            self.update_status(f"Warning: TTS not available: {e}", "orange")
            self.tts_engine = None
    
    def update_status(self, message, color="black"):
        """Update status label."""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def toggle_recording(self):
        """Toggle recording on/off."""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def toggle_auto_mode(self):
        """Toggle auto mode on/off."""
        if self.auto_mode_var.get():
            self.update_status("Auto mode enabled. Starting continuous conversation...", "blue")
            self.auto_mode_active = True
            self.auto_mode_stop_event.clear()
            
            # Start auto mode loop in a separate thread
            thread = threading.Thread(target=self._auto_mode_loop)
            thread.daemon = True
            thread.start()
        else:
            self.update_status("Auto mode disabled.", "blue")
            self.auto_mode_active = False
            self.auto_mode_stop_event.set()
            if self.is_recording:
                self.stop_recording()
    
    def _start_auto_mode_on_init(self):
        """Start auto mode on initialization."""
        if self.whisper_model is not None and self.auto_mode_var.get():
            self.toggle_auto_mode()
    
    def _auto_mode_loop(self):
        """Continuous auto mode loop: record -> transcribe -> respond -> repeat."""
        import time
        
        while self.auto_mode_active and not self.auto_mode_stop_event.is_set():
            try:
                # Step 1: Record audio
                self.update_status("🎤 Auto mode: Recording...", "blue")
                self.start_recording()
                
                # Wait for recording to complete
                while self.is_recording and not self.auto_mode_stop_event.is_set():
                    time.sleep(0.1)
                
                if self.auto_mode_stop_event.is_set():
                    break
                
                # Step 2: Transcribe audio
                if self.audio_data is not None:
                    self.update_status("📝 Auto mode: Transcribing...", "blue")
                    self._transcribe_thread_auto()
                    
                    # Wait a bit for transcription to complete
                    time.sleep(1)
                
                if self.auto_mode_stop_event.is_set():
                    break
                
                # Step 3: Generate response (happens in transcribe thread)
                # Wait 3 seconds before next cycle
                self.update_status("⏳ Auto mode: Waiting 3 seconds before next...", "green")
                for i in range(30):  # 3 seconds in 0.1s increments
                    if self.auto_mode_stop_event.is_set():
                        break
                    time.sleep(0.1)
                
            except Exception as e:
                self.update_status(f"Auto mode error: {e}", "red")
                time.sleep(1)
    
    def _transcribe_thread_auto(self):
        """Transcription for auto mode (with auto response)."""
        try:
            self.update_status("Transcribing...", "blue")
            
            if self.audio_data is None or len(self.audio_data) == 0:
                self.update_status("No audio data. Listening again...", "orange")
                return
            
            # Get selected language
            language = self.language_var.get()
            
            # Convert audio to float32 for whisper
            import numpy as np
            audio_float = self.audio_data.astype(np.float32) / 32768.0
            
            # Transcribe
            result = self.whisper_model.transcribe(
                audio_float,
                language=language if language != "auto" else None,
                fp16=False
            )
            
            text = result.get("text", "").strip()
            
            if text:
                self.display_transcription(text)
                self.analyze_transcription(text)
                
                # Auto generate response
                self.update_status("🤖 Auto mode: Generating response...", "blue")
                self.generate_response(text)
                
                # Wait for TTS to finish speaking
                import time
                self.update_status("⏳ Waiting for response to finish...", "blue")
                
                # Wait for TTS to complete (max 30 seconds)
                for i in range(300):  # 30 seconds max
                    if not self.tts_speaking:
                        break
                    time.sleep(0.1)
                
                self.update_status("✓ Response spoken. Waiting to listen again...", "green")
            else:
                self.update_status("No speech detected. Listening again...", "orange")
        
        except Exception as e:
            print(f"Transcription error: {e}")
            import traceback
            traceback.print_exc()
            self.update_status(f"Transcription error: {e}", "red")
    
    def start_recording(self):
        """Start recording voice."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.record_btn.config(state=tk.NORMAL, text="⏹️ Stop Recording")
        self.playback_btn.config(state=tk.DISABLED)
        self.transcribe_btn.config(state=tk.DISABLED)
        
        # Run in thread
        thread = threading.Thread(target=self._record_thread)
        thread.daemon = True
        thread.start()
    
    def stop_recording(self):
        """Stop recording."""
        self.is_recording = False
        self.record_btn.config(text="🎤 Start Recording")
        self.update_status("Recording stopped", "green")
    
    def playback_audio(self):
        """Playback recorded audio."""
        if self.audio_data is None:
            messagebox.showwarning("Warning", "No audio recorded. Please record first.")
            return
        
        self.playback_btn.config(state=tk.DISABLED)
        
        # Run in thread
        thread = threading.Thread(target=self._playback_thread)
        thread.daemon = True
        thread.start()
    
    def _playback_thread(self):
        """Playback thread."""
        try:
            self.update_status("Playing back audio...", "blue")
            
            import pyaudio
            
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=CHUNK
            )
            
            # Play audio
            audio_bytes = self.audio_data.tobytes()
            for i in range(0, len(audio_bytes), CHUNK * 2):
                chunk = audio_bytes[i:i + CHUNK * 2]
                stream.write(chunk)
                
                # Update progress
                progress = int((i / len(audio_bytes)) * 100)
                self.update_status(f"Playing... {progress}%", "blue")
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            self.update_status("Playback complete", "green")
            self.playback_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.update_status(f"Playback error: {e}", "red")
            self.playback_btn.config(state=tk.NORMAL)
    
    def _record_thread(self):
        """Recording thread with auto silence detection."""
        try:
            self.update_status("Recording... Speak now!", "orange")
            
            import pyaudio
            
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            frames = []
            max_chunks = int(RATE / CHUNK * 300)  # Max 5 minutes
            silence_chunks = 0
            silence_threshold_chunks = int(RATE / CHUNK * self.silence_duration)  # 3 seconds
            min_audio_chunks = int(RATE / CHUNK * 0.5)  # Minimum 0.5 seconds of audio
            
            for i in range(0, max_chunks):
                if not self.is_recording:
                    break
                
                data = stream.read(CHUNK)
                frames.append(data)
                
                # Check for silence in auto mode (only after minimum audio)
                if self.auto_mode_var.get() and len(frames) > min_audio_chunks:
                    audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                    rms = np.sqrt(np.mean(audio_chunk ** 2))
                    
                    if rms < self.silence_threshold:
                        silence_chunks += 1
                    else:
                        silence_chunks = 0
                    
                    # Auto stop after 3 seconds of silence (and at least 1 second of audio)
                    if silence_chunks > silence_threshold_chunks and len(frames) > int(RATE / CHUNK * 1):
                        self.update_status("Silence detected. Stopping recording...", "orange")
                        break
                
                # Update progress
                seconds = i * CHUNK / RATE
                self.update_status(f"Recording... {seconds:.1f}s", "orange")
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Convert to numpy array
            if frames:
                self.audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                self.sample_rate = RATE
                
                self.update_status("Recording complete.", "green")
                self.playback_btn.config(state=tk.NORMAL)
                self.transcribe_btn.config(state=tk.NORMAL)
                
                # Auto transcribe if auto mode is enabled
                if self.auto_mode_var.get():
                    self.update_status("Auto transcribing...", "blue")
                    self.transcribe_audio()
            else:
                self.update_status("No audio recorded", "red")
            
            self.record_btn.config(state=tk.NORMAL, text="🎤 Start Recording")
            self.is_recording = False
            
        except Exception as e:
            self.update_status(f"Recording error: {e}", "red")
            self.record_btn.config(state=tk.NORMAL, text="🎤 Start Recording")
            self.is_recording = False
    
    def transcribe_audio(self):
        """Transcribe recorded audio."""
        if self.audio_data is None:
            messagebox.showwarning("Warning", "No audio recorded. Please record first.")
            return
        
        self.transcribe_btn.config(state=tk.DISABLED)
        
        # Run in thread
        thread = threading.Thread(target=self._transcribe_thread)
        thread.daemon = True
        thread.start()
    
    def _transcribe_thread(self):
        """Transcription thread."""
        try:
            self.update_status("Transcribing...", "blue")
            
            # Get selected language
            language = self.language_var.get()
            
            # Save audio temporarily
            import wave
            temp_file = "temp_audio.wav"
            
            with wave.open(temp_file, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(self.audio_data.tobytes())
            
            # Transcribe using cached model
            from scipy.io import wavfile
            
            # Load audio with scipy
            sample_rate, audio_data = wavfile.read(temp_file)
            
            # Convert to float32
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            
            # If stereo, convert to mono
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Resample if needed
            if sample_rate != 16000:
                from scipy import signal
                num_samples = int(len(audio_data) * 16000 / sample_rate)
                audio_data = signal.resample(audio_data, num_samples)
            
            # Transcribe using cached model
            if self.whisper_model is None:
                self.update_status("Model not loaded", "red")
                return
            
            result = self.whisper_model.transcribe(audio_data, language=language)
            
            text = result["text"].strip()
            
            # Display transcription
            self.display_transcription(text)
            
            # Analyze
            self.analyze_transcription(text)
            
            # Generate AI response
            self.generate_response(text)
            
            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            self.update_status("Transcription complete", "green")
            self.transcribe_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.update_status(f"Transcription error: {e}", "red")
            self.transcribe_btn.config(state=tk.NORMAL)
            import traceback
            traceback.print_exc()
    
    def display_transcription(self, text):
        """Display transcribed text."""
        self.transcription_text.config(state=tk.NORMAL)
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.insert(tk.END, f'"{text}"')
        self.transcription_text.config(state=tk.DISABLED)
    
    def analyze_transcription(self, text):
        """Analyze transcribed text."""
        text_lower = text.lower()
        
        analysis = []
        analysis.append(f"Length: {len(text)} characters, {len(text.split())} words")
        
        # Keyword detection
        keywords = {
            "hello": "hello" in text_lower,
            "hi": "hi" in text_lower,
            "bye": "bye" in text_lower or "goodbye" in text_lower,
            "thanks": "thank" in text_lower,
            "yes": "yes" in text_lower,
            "no": "no" in text_lower,
            "help": "help" in text_lower,
        }
        
        found = [k for k, v in keywords.items() if v]
        if found:
            analysis.append(f"Keywords detected: {', '.join(found)}")
        else:
            analysis.append("No keywords detected")
        
        # Display analysis
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "\n".join(analysis))
        self.analysis_text.config(state=tk.DISABLED)
    
    def generate_response(self, text):
        """Generate AI response using offline knowledge base."""
        text_lower = text.lower()
        
        # ENGLISH RESPONSES
        if any(word in text_lower for word in ["hello", "hi", "hey", "greetings"]):
            response = "Hello! Nice to meet you. How can I help you today?"
        elif any(word in text_lower for word in ["bye", "goodbye", "see you", "farewell"]):
            response = "Goodbye! Have a great day!"
        elif any(word in text_lower for word in ["thanks", "thank you", "appreciate", "grateful"]):
            response = "You're welcome! Happy to help."
        elif any(word in text_lower for word in ["time", "what time", "current time"]):
            current_time = datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}."
        elif any(word in text_lower for word in ["date", "what date", "today"]):
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            response = f"Today is {current_date}."
        elif any(word in text_lower for word in ["name", "who are you", "what are you"]):
            response = "I'm Vask, your voice-based AI companion. I can help you with various tasks offline!"
        elif "how are you" in text_lower:
            response = "I'm doing great, thanks for asking! I'm here to help you with anything you need."
        elif any(word in text_lower for word in ["help", "assist", "support"]):
            response = "I can help you with voice recognition, transcription, mood analysis, and more! What do you need?"
        else:
            response = f"That's interesting! You mentioned '{text}'. Tell me more about that."
        
        # Display response
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, f"🤖 {response}")
        self.response_text.config(state=tk.DISABLED)
        
        # Speak response in a separate thread (non-blocking start, but blocking execution)
        thread = threading.Thread(target=self._speak_response, args=(response,))
        thread.daemon = False  # Don't make it daemon so we can wait for it
        thread.start()
        
        # Add to history
        self.add_to_history(text, response)
    
    def add_to_history(self, user_text, ai_response):
        """Add conversation to history."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add to list
        self.conversation_history.append({
            "time": timestamp,
            "user": user_text,
            "ai": ai_response
        })
        
        # Update display
        self.update_history_display()
    
    def _speak_response(self, text):
        """Speak the response using TTS - blocking call."""
        try:
            if self.tts_engine is None:
                return
            
            self.tts_speaking = True
            self.tts_complete_event.clear()
            
            self.update_status("🔊 Speaking response...", "blue")
            
            try:
                # Use subprocess to run pyttsx3 in separate process (avoids the runAndWait bug)
                import subprocess
                import sys
                
                # Create a simple Python script to speak
                script = f"""
import pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)
engine.say('{text.replace("'", "\\'")}')
engine.runAndWait()
"""
                
                # Run in subprocess
                process = subprocess.Popen(
                    [sys.executable, "-c", script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Wait for process to complete
                stdout, stderr = process.communicate(timeout=30)
                
                if process.returncode != 0:
                    print(f"TTS subprocess error: {stderr.decode()}")
                
                self.update_status("✓ Response spoken", "green")
            
            except subprocess.TimeoutExpired:
                process.kill()
                self.update_status("TTS timeout", "orange")
            except Exception as e:
                print(f"pyttsx3 error: {e}")
                self.update_status(f"TTS error: {e}", "orange")
        
        finally:
            self.tts_speaking = False
            self.tts_complete_event.set()  # Signal that TTS is complete
    
    def _play_tts_audio(self, audio_file):
        """Play TTS audio file."""
        try:
            import pyaudio
            from scipy.io import wavfile
            
            # Load audio
            sample_rate, audio_data = wavfile.read(audio_file)
            
            # Play audio
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1 if len(audio_data.shape) == 1 else audio_data.shape[1]
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=sample_rate,
                output=True,
                frames_per_buffer=CHUNK
            )
            
            # Write audio data
            audio_bytes = audio_data.tobytes()
            for i in range(0, len(audio_bytes), CHUNK * 2):
                chunk = audio_bytes[i:i + CHUNK * 2]
                stream.write(chunk)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        except Exception as e:
            self.update_status(f"Audio playback error: {e}", "orange")
    
    def update_history_display(self):
        """Update history text display."""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        # Show last 5 conversations
        for item in self.conversation_history[-5:]:
            line = f"[{item['time']}] You: {item['user']}\n"
            line += f"         AI: {item['ai']}\n\n"
            self.history_text.insert(tk.END, line)
        
        self.history_text.config(state=tk.DISABLED)
    
    def clear_all(self):
        """Clear all text."""
        self.transcription_text.config(state=tk.NORMAL)
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.config(state=tk.DISABLED)
        
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.config(state=tk.DISABLED)
        
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete(1.0, tk.END)
        self.response_text.config(state=tk.DISABLED)
        
        self.audio_data = None
        self.sample_rate = None
        self.playback_btn.config(state=tk.DISABLED)
        self.transcribe_btn.config(state=tk.DISABLED)
        self.update_status("Cleared", "blue")
    
    def clear_cache(self):
        """Clear Whisper cache and temporary files."""
        try:
            self.update_status("Clearing cache...", "blue")
            
            # Clear Whisper cache
            import shutil
            cache_dir = Path.home() / ".cache" / "whisper"
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                self.update_status("Cache cleared successfully", "green")
            else:
                self.update_status("No cache found", "green")
            
            # Clear temporary files
            temp_files = list(Path(".").glob("temp_audio*.wav"))
            for f in temp_files:
                f.unlink()
            
            if temp_files:
                self.update_status(f"Cleared {len(temp_files)} temporary files", "green")
            
        except Exception as e:
            self.update_status(f"Cache clear error: {e}", "red")
    
    def show_help(self):
        """Show help window with available commands."""
        help_window = tk.Toplevel(self.root)
        help_window.title("Vask - Help & Commands")
        help_window.geometry("700x600")
        
        # Title
        title_label = ttk.Label(
            help_window,
            text="Available Commands & Questions",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Help text
        help_text = scrolledtext.ScrolledText(
            help_window,
            height=30,
            width=80,
            font=("Courier", 10),
            wrap=tk.WORD
        )
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Commands list
        commands = """
GREETING COMMANDS:
  • "Hello" / "Hi" / "Hey"
    → Response: Hello! Nice to meet you. How can I help you today?

FAREWELL COMMANDS:
  • "Bye" / "Goodbye" / "See you"
    → Response: Goodbye! Have a great day!

GRATITUDE COMMANDS:
  • "Thanks" / "Thank you" / "Appreciate"
    → Response: You're welcome! Happy to help.

TIME COMMANDS:
  • "What time is it?" / "Current time"
    → Response: The current time is [HH:MM AM/PM].

DATE COMMANDS:
  • "What date is it?" / "Today" / "What's today?"
    → Response: Today is [Day, Month DD, YYYY].

IDENTITY COMMANDS:
  • "Who are you?" / "What are you?" / "Your name?"
    → Response: I'm Vask, your voice-based AI companion...

STATUS COMMANDS:
  • "How are you?"
    → Response: I'm doing great, thanks for asking!

HELP COMMANDS:
  • "Help" / "Assist" / "Support"
    → Response: I can help you with voice recognition, transcription...

AUTO MODE:
  • Enable "🤖 Auto Mode" checkbox
  • Recording starts automatically
  • Stops after 3 seconds of silence
  • Automatically transcribes
  • Generates AI response

FEATURES:
  ✓ Record voice (Start/Stop anytime)
  ✓ Playback your recording
  ✓ Transcribe speech to text
  ✓ AI responses (offline)
  ✓ Conversation history
  ✓ Auto mode with silence detection
  ✓ No internet required

TIPS:
  • Click "Start Recording" to begin
  • Click "Stop Recording" to stop
  • Click "Playback" to hear your recording
  • Click "Transcribe" to convert speech to text
  • Enable "Auto Mode" for hands-free operation
  • View conversation history at the bottom
        """
        
        help_text.insert(tk.END, commands)
        help_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy
        )
        close_btn.pack(pady=10)


def main():
    """Main entry point."""
    root = tk.Tk()
    gui = VaskGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
