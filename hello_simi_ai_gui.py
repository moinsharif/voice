"""
Hello Simi AI - Integrated GUI with main.py components
Combines vask_gui.py recording logic with main.py AI/Context management
Phase 1: Basic integration with AIModelWrapper and ContextManager
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import numpy as np
from datetime import datetime
import uuid

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.main import VaskApplication
from src.engines.ai_model_wrapper import AIModelWrapper, ConversationContext
from src.managers.context_manager import ContextManager
from src.models.data_models import Exchange
from src.persistence.persistence_layer import PersistenceLayer


class HelloSimiAIGUI:
    """Integrated GUI combining vask_gui recording with main.py AI components."""
    
    def __init__(self, root):
        """Initialize GUI."""
        self.root = root
        self.root.title("Hello Simi AI - Integrated Voice Assistant")
        self.root.geometry("1000x900")
        self.root.resizable(True, True)
        
        # Recording state
        self.is_recording = False
        self.audio_data = None
        self.sample_rate = None
        self.conversation_history = []
        self.silence_threshold = 0.02
        self.silence_duration = 3
        
        # Auto mode state
        self.auto_mode_active = False
        self.auto_mode_stop_event = threading.Event()
        self.tts_speaking = False
        self.tts_complete_event = threading.Event()
        
        # Main.py components
        self.app = None
        self.ai_model = None
        self.context_manager = None
        self.persistence_layer = None
        self.conversation_context = None
        
        # User session
        self.user_id = f"user_{uuid.uuid4().hex[:8]}"
        self.session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Whisper model for transcription
        self.whisper_model = None
        
        # Create UI
        self.create_ui()
        
        # Initialize components
        self.initialize_app()
        self.load_whisper_model()
        
        # Start auto mode by default
        self.root.after(2000, self._start_auto_mode_on_init)
    
    def create_ui(self):
        """Create user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT)
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.record_btn = ttk.Button(button_frame, text="🎤 Start Recording", command=self.toggle_recording)
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        self.auto_mode_var = tk.BooleanVar(value=False)
        self.auto_mode_btn = ttk.Checkbutton(button_frame, text="Auto Mode", variable=self.auto_mode_var, command=self.toggle_auto_mode)
        self.auto_mode_btn.pack(side=tk.LEFT, padx=5)
        
        self.transcribe_btn = ttk.Button(button_frame, text="📝 Transcribe", command=self.transcribe_audio, state=tk.DISABLED)
        self.transcribe_btn.pack(side=tk.LEFT, padx=5)
        
        self.playback_btn = ttk.Button(button_frame, text="🔊 Playback", command=self.playback_audio, state=tk.DISABLED)
        self.playback_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_all)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(button_frame, text="💾 Export", command=self.export_history)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="System Info", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_label = ttk.Label(info_frame, text="Initializing...", justify=tk.LEFT)
        self.info_label.pack(fill=tk.X)
        
        # Transcription frame
        trans_frame = ttk.LabelFrame(main_frame, text="Transcription", padding=10)
        trans_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        self.transcription_text = scrolledtext.ScrolledText(trans_frame, height=3, width=80)
        self.transcription_text.pack(fill=tk.BOTH, expand=True)
        
        # Response frame
        resp_frame = ttk.LabelFrame(main_frame, text="AI Response", padding=10)
        resp_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        self.response_text = scrolledtext.ScrolledText(resp_frame, height=3, width=80)
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # History frame
        hist_frame = ttk.LabelFrame(main_frame, text="Conversation History", padding=10)
        hist_frame.pack(fill=tk.BOTH, expand=True)
        
        self.history_text = scrolledtext.ScrolledText(hist_frame, height=10, width=80)
        self.history_text.pack(fill=tk.BOTH, expand=True)
    
    def update_status(self, message, color="black"):
        """Update status label."""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def update_info(self):
        """Update system info display."""
        info_text = f"User: {self.user_id}\n"
        info_text += f"Session: {self.session_id}\n"
        
        if self.ai_model:
            model_info = self.ai_model.get_model_info()
            info_text += f"AI Model: {'Loaded' if model_info['is_loaded'] else 'Not loaded'}\n"
            info_text += f"Response Tone: {model_info['response_tone']}\n"
        
        if self.context_manager:
            ctx_info = self.context_manager.get_model_info()
            info_text += f"Context Size: {ctx_info['context_size']}\n"
        
        info_text += f"Conversations: {len(self.conversation_history)}"
        
        self.info_label.config(text=info_text)
    
    def initialize_app(self):
        """Initialize application with main.py components."""
        try:
            self.update_status("Initializing components...", "blue")
            
            # Initialize persistence layer
            self.persistence_layer = PersistenceLayer(db_path="hello_simi_data.db")
            self.update_status("Persistence layer initialized", "blue")
            
            # Initialize context manager
            self.context_manager = ContextManager(
                persistence_layer=self.persistence_layer,
                max_context_exchanges=10
            )
            self.update_status("Context manager initialized", "blue")
            
            # Initialize AI model
            self.ai_model = AIModelWrapper()
            self.update_status("AI model initialized", "blue")
            
            # Initialize conversation context
            self.conversation_context = ConversationContext(max_exchanges=10)
            
            # Load user profile
            self.context_manager.load_user_profile(self.user_id)
            self.update_status("User profile loaded", "blue")
            
            # Start session
            self.context_manager.start_session(self.user_id, self.session_id)
            self.update_status("Session started", "green")
            
            self.update_info()
            
        except Exception as e:
            self.update_status(f"Initialization error: {e}", "red")
            messagebox.showerror("Error", f"Failed to initialize: {e}")
    
    def load_whisper_model(self):
        """Load Whisper model for transcription."""
        try:
            self.update_status("Loading Whisper model...", "blue")
            import whisper
            self.whisper_model = whisper.load_model("base")
            self.update_status("Whisper model loaded", "green")
        except Exception as e:
            self.update_status(f"Whisper load error: {e}", "red")
            messagebox.showwarning("Warning", f"Whisper model failed: {e}")
    
    def toggle_recording(self):
        """Toggle recording on/off."""
        if not self.is_recording:
            self.is_recording = True
            self.record_btn.config(state=tk.DISABLED, text="⏹️ Stop Recording")
            self.update_status("Recording...", "orange")
            
            thread = threading.Thread(target=self._record_thread, daemon=False)
            thread.start()
        else:
            self.is_recording = False
            self.update_status("Stopping recording...", "orange")
    
    def toggle_auto_mode(self):
        """Toggle auto mode."""
        if self.auto_mode_var.get():
            self.auto_mode_active = True
            self.auto_mode_stop_event.clear()
            self.update_status("Auto mode enabled", "blue")
            
            thread = threading.Thread(target=self._auto_mode_loop, daemon=False)
            thread.start()
        else:
            self.auto_mode_active = False
            self.auto_mode_stop_event.set()
            self.update_status("Auto mode disabled", "green")
    
    def _start_auto_mode_on_init(self):
        """Start auto mode on initialization."""
        if not self.auto_mode_var.get():
            self.auto_mode_var.set(True)
            self.toggle_auto_mode()
    
    def play_beep(self, frequency=1000, duration=0.2, volume=0.15):
        """Play beep sound."""
        try:
            import pyaudio
            import math
            
            p = pyaudio.PyAudio()
            sample_rate = 44100
            
            # Generate sine wave
            frames = []
            for i in range(int(sample_rate * duration)):
                sample = int(32767 * volume * math.sin(2 * math.pi * frequency * i / sample_rate))
                frames.append(sample.to_bytes(2, byteorder='little', signed=True))
            
            # Play
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True)
            stream.write(b''.join(frames))
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"Beep error: {e}")
    
    def _auto_mode_loop(self):
        """Continuous auto mode loop."""
        import time
        
        while self.auto_mode_active and not self.auto_mode_stop_event.is_set():
            try:
                # Record
                self.update_status("🎤 Auto: Recording...", "blue")
                self.start_recording()
                
                while self.is_recording and not self.auto_mode_stop_event.is_set():
                    time.sleep(0.1)
                
                if self.auto_mode_stop_event.is_set():
                    break
                
                # Transcribe
                self.update_status("📝 Auto: Transcribing...", "blue")
                time.sleep(0.5)
                
                if self.auto_mode_stop_event.is_set():
                    break
                
                # Wait for TTS
                self.update_status("⏳ Waiting for response...", "blue")
                max_wait = 600
                for i in range(max_wait):
                    if not self.tts_speaking:
                        break
                    time.sleep(0.1)
                
                # Wait before next cycle
                self.update_status("⏳ Waiting 1 second...", "green")
                for i in range(10):
                    if self.auto_mode_stop_event.is_set():
                        break
                    time.sleep(0.1)
                
            except Exception as e:
                self.update_status(f"Auto mode error: {e}", "red")
                time.sleep(1)
    
    def _record_thread(self):
        """Recording thread with silence detection."""
        import pyaudio
        import time
        
        p = None
        stream = None
        
        try:
            self.update_status("Recording... Speak now!", "orange")
            self.play_beep(frequency=800, duration=0.15, volume=0.15)
            
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
            max_chunks = int(RATE / CHUNK * 300)
            silence_chunks = 0
            silence_threshold_chunks = int(RATE / CHUNK * self.silence_duration)
            min_audio_chunks = int(RATE / CHUNK * 0.5)
            
            for i in range(0, max_chunks):
                if not self.is_recording:
                    break
                
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"Error reading audio chunk: {e}")
                    break
                
                # Silence detection in auto mode
                if self.auto_mode_var.get() and len(frames) > min_audio_chunks:
                    audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                    rms = np.sqrt(np.mean(audio_chunk ** 2))
                    
                    if rms < self.silence_threshold:
                        silence_chunks += 1
                    else:
                        silence_chunks = 0
                    
                    if silence_chunks > silence_threshold_chunks and len(frames) > int(RATE / CHUNK * 1):
                        self.update_status("Silence detected. Stopping...", "orange")
                        self.play_beep(frequency=1200, duration=0.15, volume=0.15)
                        break
                
                seconds = i * CHUNK / RATE
                self.update_status(f"Recording... {seconds:.1f}s", "orange")
            
            if frames:
                self.audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                self.sample_rate = RATE
                
                self.update_status("Recording complete.", "green")
                self.playback_btn.config(state=tk.NORMAL)
                self.transcribe_btn.config(state=tk.NORMAL)
                
                # Auto transcribe in auto mode
                if self.auto_mode_var.get():
                    self.update_status("Auto transcribing...", "blue")
                    thread = threading.Thread(target=self._transcribe_thread_auto, daemon=False)
                    thread.start()
            else:
                self.update_status("No audio recorded", "red")
                self.audio_data = None
            
            self.record_btn.config(state=tk.NORMAL, text="🎤 Start Recording")
            self.is_recording = False
            
        except Exception as e:
            self.update_status(f"Recording error: {e}", "red")
            self.record_btn.config(state=tk.NORMAL, text="🎤 Start Recording")
            self.is_recording = False
        
        finally:
            # Ensure proper cleanup of PyAudio resources
            try:
                if stream is not None:
                    try:
                        stream.stop_stream()
                    except:
                        pass
                    try:
                        stream.close()
                    except:
                        pass
            except Exception as e:
                print(f"Error closing stream: {e}")
            
            try:
                if p is not None:
                    p.terminate()
            except Exception as e:
                print(f"Error terminating PyAudio: {e}")
            
            # Force garbage collection to free resources
            import gc
            gc.collect()
    
    def start_recording(self):
        """Start recording."""
        if not self.is_recording:
            self.is_recording = True
            self.record_btn.config(state=tk.DISABLED, text="⏹️ Stop Recording")
            
            thread = threading.Thread(target=self._record_thread, daemon=False)
            thread.start()
    
    def transcribe_audio(self):
        """Transcribe audio."""
        if self.audio_data is None or len(self.audio_data) == 0:
            self.update_status("No audio to transcribe", "red")
            return
        
        thread = threading.Thread(target=self._transcribe_thread, daemon=False)
        thread.start()
    
    def _transcribe_thread(self):
        """Transcription thread."""
        try:
            self.update_status("Transcribing...", "blue")
            
            if self.whisper_model is None:
                self.update_status("Whisper model not loaded", "red")
                return
            
            audio_float = self.audio_data.astype(np.float32) / 32768.0
            
            result = self.whisper_model.transcribe(
                audio_float,
                language="en",
                fp16=False,
                verbose=False
            )
            
            text = result.get("text", "").strip()
            self.display_transcription(text)
            
            if text:
                self.analyze_transcription(text)
                self.generate_response(text)
            
        except Exception as e:
            self.update_status(f"Transcription error: {e}", "red")
    
    def _transcribe_thread_auto(self):
        """Transcription for auto mode."""
        try:
            self.update_status("Transcribing...", "blue")
            
            if self.audio_data is None or len(self.audio_data) == 0:
                self.update_status("No audio data", "orange")
                return
            
            if self.whisper_model is None:
                self.update_status("Whisper model not loaded", "red")
                return
            
            audio_float = self.audio_data.astype(np.float32) / 32768.0
            
            result = self.whisper_model.transcribe(
                audio_float,
                language="en",
                fp16=False,
                verbose=False
            )
            
            text = result.get("text", "").strip()
            self.audio_data = None
            
            if text:
                self.display_transcription(text)
                self.analyze_transcription(text)
                
                self.update_status("🤖 Auto: Generating response...", "blue")
                self.generate_response(text)
                
                import time
                self.update_status("⏳ Waiting for response...", "blue")
                
                max_wait = 600
                for i in range(max_wait):
                    if not self.tts_speaking:
                        break
                    time.sleep(0.1)
                
                time.sleep(0.5)
                self.update_status("✓ Response spoken. Waiting to listen...", "green")
            else:
                self.update_status("No speech detected", "orange")
        
        except Exception as e:
            self.update_status(f"Transcription error: {e}", "red")
    
    def display_transcription(self, text):
        """Display transcription."""
        self.transcription_text.config(state=tk.NORMAL)
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.insert(tk.END, text)
        self.transcription_text.config(state=tk.DISABLED)
    
    def analyze_transcription(self, text):
        """Analyze transcription (placeholder)."""
        pass
    
    def generate_response(self, text):
        """Generate response using AI model and context manager."""
        try:
            if not self.ai_model or not self.context_manager:
                self.update_status("AI components not initialized", "red")
                return
            
            self.update_status("🤖 Generating response...", "blue")
            
            # Check for basic responses first (time, date, etc.)
            text_lower = text.lower()
            basic_response = self._get_basic_response(text_lower)
            
            if basic_response:
                response = basic_response
            else:
                # Use AI model for other responses
                response = self.ai_model.generate_response(
                    self.conversation_context,
                    text
                )
            
            # Add user message to context
            exchange = Exchange(
                user_message=text,
                ai_response=response,
                timestamp=datetime.now()
            )
            self.context_manager.add_exchange(exchange)
            self.conversation_context.add_exchange(exchange)
            
            # Display response
            self.response_text.config(state=tk.NORMAL)
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(tk.END, response)
            self.response_text.config(state=tk.DISABLED)
            
            # Add to history
            self.add_to_history(text, response)
            
            # Speak response
            self._speak_response(response)
            
            self.update_status("✓ Response generated", "green")
            self.update_info()
            
        except Exception as e:
            self.update_status(f"Response generation error: {e}", "red")
    
    def _get_basic_response(self, text_lower):
        """Get basic responses for common queries."""
        from datetime import datetime
        
        # Greetings
        if any(word in text_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! Nice to meet you. How can I help you today?"
        
        elif any(word in text_lower for word in ["bye", "goodbye", "see you", "farewell"]):
            return "Goodbye! Have a great day!"
        
        elif any(word in text_lower for word in ["thanks", "thank you", "appreciate", "grateful"]):
            return "You're welcome! Happy to help."
        
        # Time and Date
        elif any(word in text_lower for word in ["time", "what time", "current time"]):
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}."
        
        elif any(word in text_lower for word in ["date", "what date", "today"]):
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {current_date}."
        
        # Identity
        elif any(word in text_lower for word in ["name", "who are you", "what are you"]):
            return "I'm Simi, your voice-based AI companion. I can help you with various tasks offline!"
        
        elif "how are you" in text_lower:
            return "I'm doing great, thanks for asking! I'm here to help you with anything you need."
        
        # Help
        elif any(word in text_lower for word in ["help", "assist", "support"]):
            return "I can help you with voice recognition, transcription, mood analysis, and more! What do you need?"
        
        # No basic response found
        return None
    
    def add_to_history(self, user_text, ai_response):
        """Add conversation to history."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        entry = {
            "timestamp": timestamp,
            "user": user_text,
            "ai": ai_response
        }
        self.conversation_history.append(entry)
        
        self.update_history_display()
    
    def update_history_display(self):
        """Update history display."""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        for entry in self.conversation_history:
            self.history_text.insert(tk.END, f"[{entry['timestamp']}] You: {entry['user']}\n")
            self.history_text.insert(tk.END, f"         AI: {entry['ai']}\n\n")
        
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
    
    def _speak_response(self, text):
        """Speak response using TTS."""
        try:
            self.tts_speaking = True
            self.tts_complete_event.clear()
            
            # Stop recording completely during TTS
            was_recording = self.is_recording
            if was_recording:
                self.is_recording = False
                import time
                time.sleep(0.2)  # Give recording thread time to stop
                # Clear audio buffer to ensure no TTS audio is captured
                self.audio_data = None
            
            self.update_status("🔊 Speaking...", "blue")
            
            try:
                import subprocess
                import sys
                import time
                
                script = f"""
import pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)
engine.say('{text.replace("'", "\\'")}')
engine.runAndWait()
"""
                
                process = subprocess.Popen(
                    [sys.executable, "-c", script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                stdout, stderr = process.communicate(timeout=30)
                
                if process.returncode != 0:
                    print(f"TTS error: {stderr.decode()}")
                
                self.update_status("✓ Response spoken", "green")
            
            except subprocess.TimeoutExpired:
                process.kill()
                self.update_status("TTS timeout", "orange")
            except Exception as e:
                print(f"TTS error: {e}")
                self.update_status(f"TTS error: {e}", "orange")
            
            # Resume recording if it was active
            if was_recording:
                import time
                # Wait for TTS subprocess to fully terminate and audio to stop playing
                # 1.2 seconds gives enough buffer for audio playback to complete
                time.sleep(1.2)
                # Clear audio buffer one more time before resuming
                self.audio_data = None
                # Now resume recording
                self.is_recording = True
        
        finally:
            self.tts_speaking = False
            self.tts_complete_event.set()
    
    def playback_audio(self):
        """Playback recorded audio."""
        if self.audio_data is None:
            self.update_status("No audio to playback", "red")
            return
        
        thread = threading.Thread(target=self._playback_thread, daemon=False)
        thread.start()
    
    def _playback_thread(self):
        """Playback thread."""
        try:
            import pyaudio
            
            self.update_status("Playing audio...", "blue")
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True
            )
            
            stream.write(self.audio_data.tobytes())
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            self.update_status("Playback complete", "green")
        
        except Exception as e:
            self.update_status(f"Playback error: {e}", "red")
    
    def clear_all(self):
        """Clear all data."""
        self.transcription_text.config(state=tk.NORMAL)
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.config(state=tk.DISABLED)
        
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete(1.0, tk.END)
        self.response_text.config(state=tk.DISABLED)
        
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
        
        self.audio_data = None
        self.conversation_history = []
        
        self.update_status("Cleared", "green")
    
    def export_history(self):
        """Export conversation history."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hello_simi_history_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("HELLO SIMI AI CONVERSATION HISTORY\n")
                f.write("=" * 80 + "\n\n")
                
                for entry in self.conversation_history:
                    f.write(f"[{entry['timestamp']}] You: {entry['user']}\n")
                    f.write(f"         AI: {entry['ai']}\n\n")
                
                f.write("=" * 80 + "\n")
                f.write(f"Total conversations: {len(self.conversation_history)}\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            self.update_status(f"Exported to {filename}", "green")
            messagebox.showinfo("Success", f"History exported to {filename}")
        
        except Exception as e:
            self.update_status(f"Export error: {e}", "red")
            messagebox.showerror("Error", f"Failed to export: {e}")


def main():
    """Main entry point."""
    root = tk.Tk()
    gui = HelloSimiAIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
