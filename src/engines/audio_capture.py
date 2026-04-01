"""Audio capture and preprocessing module using PyAudio."""

import pyaudio
import numpy as np
from typing import Optional, List
from collections import deque
from src.utils.logger import Logger


class AudioCapture:
    """Captures audio from system microphone with noise filtering and validation."""

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_size: int = 1024,
        channels: int = 1,
        format_type: int = pyaudio.paFloat32,
        silence_threshold: float = 0.02,
        noise_duration: float = 0.5
    ):
        """Initialize audio capture.
        
        Args:
            sample_rate: Sample rate in Hz (default 16000)
            chunk_size: Chunk size for real-time processing (default 1024)
            channels: Number of audio channels (default 1 for mono)
            format_type: PyAudio format type (default paFloat32)
            silence_threshold: RMS threshold for silence detection (default 0.02)
            noise_duration: Duration in seconds for noise profile (default 0.5)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.format_type = format_type
        self.silence_threshold = silence_threshold
        self.noise_duration = noise_duration
        
        self.logger = Logger("AudioCapture")
        self.audio = None
        self.stream = None
        self.is_recording = False
        self.audio_buffer = deque(maxlen=int(sample_rate * 10))  # 10 second buffer
        self.noise_profile = None
        self._initialize_audio()

    def _initialize_audio(self) -> None:
        """Initialize PyAudio instance."""
        try:
            self.audio = pyaudio.PyAudio()
            self.logger.info("PyAudio initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize PyAudio: {e}")
            raise

    def start_recording(self) -> None:
        """Start capturing audio from microphone."""
        try:
            if self.is_recording:
                self.logger.warning("Recording already in progress")
                return

            self.stream = self.audio.open(
                format=self.format_type,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                exception_on_overflow=False
            )
            
            self.is_recording = True
            self.audio_buffer.clear()
            self.logger.info("Started recording audio")
            
            # Capture noise profile for filtering
            self._capture_noise_profile()
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            self.is_recording = False
            raise

    def stop_recording(self) -> None:
        """Stop capturing audio from microphone."""
        try:
            if not self.is_recording:
                self.logger.warning("Recording not in progress")
                return

            self.is_recording = False
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            self.logger.info("Stopped recording audio")
            
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            raise

    def get_audio_chunk(self) -> Optional[bytes]:
        """Get next audio chunk from microphone.
        
        Returns:
            Audio chunk as bytes, or None if not recording
        """
        if not self.is_recording or not self.stream:
            return None

        try:
            chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
            
            # Convert bytes to numpy array for processing
            audio_array = np.frombuffer(chunk, dtype=np.float32)
            
            # Store in buffer
            self.audio_buffer.extend(audio_array)
            
            return chunk
            
        except Exception as e:
            self.logger.error(f"Failed to read audio chunk: {e}")
            return None

    def _capture_noise_profile(self) -> None:
        """Capture noise profile from initial audio for filtering."""
        try:
            noise_samples = int(self.sample_rate * self.noise_duration / self.chunk_size)
            noise_chunks = []
            
            for _ in range(noise_samples):
                chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_array = np.frombuffer(chunk, dtype=np.float32)
                noise_chunks.append(audio_array)
            
            if noise_chunks:
                noise_data = np.concatenate(noise_chunks)
                self.noise_profile = np.mean(np.abs(noise_data))
                self.logger.info(f"Noise profile captured: {self.noise_profile:.4f}")
            
        except Exception as e:
            self.logger.warning(f"Failed to capture noise profile: {e}")
            self.noise_profile = None

    def apply_noise_filter(self, audio_data: bytes) -> bytes:
        """Apply noise filtering using spectral subtraction.
        
        Args:
            audio_data: Raw audio data in bytes
            
        Returns:
            Filtered audio data in bytes
        """
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            if self.noise_profile is None:
                self.logger.warning("No noise profile available, returning unfiltered audio")
                return audio_data
            
            # Apply spectral subtraction
            # Estimate noise level and subtract it
            noise_threshold = self.noise_profile * 1.5
            
            # Apply noise gate - suppress audio below threshold
            filtered = np.where(
                np.abs(audio_array) > noise_threshold,
                audio_array,
                audio_array * 0.1  # Attenuate low-level noise
            )
            
            # Apply gentle high-pass filter to remove low-frequency noise
            # Simple first-order high-pass filter
            alpha = 0.95
            filtered_hp = np.zeros_like(filtered)
            filtered_hp[0] = filtered[0]
            for i in range(1, len(filtered)):
                filtered_hp[i] = alpha * (filtered_hp[i-1] + filtered[i] - filtered[i-1])
            
            # Normalize to prevent clipping
            max_val = np.max(np.abs(filtered_hp))
            if max_val > 0:
                filtered_hp = filtered_hp / max_val * 0.95
            
            return filtered_hp.astype(np.float32).tobytes()
            
        except Exception as e:
            self.logger.warning(f"Noise filtering failed: {e}")
            return audio_data

    def detect_silence(self, audio_chunk: bytes) -> bool:
        """Detect silence in audio chunk using RMS threshold.
        
        Args:
            audio_chunk: Audio chunk in bytes
            
        Returns:
            True if silence detected, False otherwise
        """
        try:
            audio_array = np.frombuffer(audio_chunk, dtype=np.float32)
            
            # Calculate RMS (Root Mean Square)
            rms = np.sqrt(np.mean(audio_array ** 2))
            
            is_silent = rms < self.silence_threshold
            
            return is_silent
            
        except Exception as e:
            self.logger.error(f"Failed to detect silence: {e}")
            return False

    def validate_audio_quality(self, audio_data: bytes) -> dict:
        """Validate audio quality and check for minimum requirements.
        
        Args:
            audio_data: Audio data in bytes
            
        Returns:
            Dictionary with quality metrics and validation status
        """
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Calculate metrics
            rms = np.sqrt(np.mean(audio_array ** 2))
            peak = np.max(np.abs(audio_array))
            mean_abs = np.mean(np.abs(audio_array))
            
            # Check for clipping (distortion)
            clipping_ratio = np.sum(np.abs(audio_array) > 0.95) / len(audio_array)
            
            # Determine quality
            is_valid = True
            issues = []
            
            # Check for minimum signal level
            if rms < 0.01:
                is_valid = False
                issues.append("Signal too quiet")
            
            # Check for clipping
            if clipping_ratio > 0.05:
                is_valid = False
                issues.append("Audio clipping detected")
            
            # Check for silence
            if rms < self.silence_threshold:
                issues.append("Silence detected")
            
            # Check for dynamic range
            if peak > 0 and (mean_abs / peak) < 0.1:
                issues.append("Low dynamic range")
            
            return {
                "is_valid": is_valid,
                "rms": float(rms),
                "peak": float(peak),
                "mean_abs": float(mean_abs),
                "clipping_ratio": float(clipping_ratio),
                "duration_seconds": len(audio_array) / self.sample_rate,
                "issues": issues
            }
            
        except Exception as e:
            self.logger.error(f"Audio quality validation failed: {e}")
            return {
                "is_valid": False,
                "rms": 0.0,
                "peak": 0.0,
                "mean_abs": 0.0,
                "clipping_ratio": 0.0,
                "duration_seconds": 0.0,
                "issues": [str(e)]
            }

    def get_audio_buffer(self) -> bytes:
        """Get all buffered audio data.
        
        Returns:
            Concatenated audio buffer as bytes
        """
        try:
            if not self.audio_buffer:
                return b''
            
            audio_array = np.array(list(self.audio_buffer), dtype=np.float32)
            return audio_array.tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to get audio buffer: {e}")
            return b''

    def clear_buffer(self) -> None:
        """Clear the audio buffer."""
        self.audio_buffer.clear()
        self.logger.info("Audio buffer cleared")

    def get_microphone_info(self) -> dict:
        """Get information about audio capture configuration.
        
        Returns:
            Dictionary with audio configuration info
        """
        return {
            "sample_rate": self.sample_rate,
            "chunk_size": self.chunk_size,
            "channels": self.channels,
            "is_recording": self.is_recording,
            "silence_threshold": self.silence_threshold,
            "noise_profile": float(self.noise_profile) if self.noise_profile else None,
            "buffer_size": len(self.audio_buffer)
        }

    def list_input_devices(self) -> List[dict]:
        """List available input devices.
        
        Returns:
            List of available input devices with info
        """
        try:
            devices = []
            if not self.audio:
                return devices
            
            device_count = self.audio.get_device_count()
            for i in range(device_count):
                info = self.audio.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    devices.append({
                        "index": i,
                        "name": info['name'],
                        "channels": info['maxInputChannels'],
                        "sample_rate": int(info['defaultSampleRate'])
                    })
            
            return devices
            
        except Exception as e:
            self.logger.error(f"Failed to list input devices: {e}")
            return []

    def cleanup(self) -> None:
        """Clean up audio resources."""
        try:
            if self.is_recording:
                self.stop_recording()
            
            if self.audio:
                self.audio.terminate()
                self.audio = None
            
            self.logger.info("Audio resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup audio resources: {e}")
