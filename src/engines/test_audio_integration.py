"""Integration tests for AudioCapture with SpeechRecognitionEngine."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.engines.audio_capture import AudioCapture
from src.engines.speech_recognition_engine import SpeechRecognitionEngine


class TestAudioCaptureIntegration:
    """Test AudioCapture integration with other components."""

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    @patch('src.engines.speech_recognition_engine.whisper.load_model')
    def test_audio_capture_with_speech_recognition(self, mock_whisper, mock_pyaudio):
        """Test audio capture workflow with speech recognition."""
        # Setup mocks
        mock_audio_instance = MagicMock()
        mock_stream = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        mock_audio_instance.open.return_value = mock_stream
        
        mock_model = MagicMock()
        mock_whisper.return_value = mock_model
        
        # Create test audio
        test_audio = np.random.randn(16000).astype(np.float32) * 0.3
        mock_stream.read.return_value = test_audio.tobytes()
        
        # Initialize components
        audio_capture = AudioCapture(sample_rate=16000)
        audio_capture._capture_noise_profile = Mock()
        
        speech_engine = SpeechRecognitionEngine()
        
        # Start recording
        audio_capture.start_recording()
        assert audio_capture.is_recording is True
        
        # Get audio chunk
        chunk = audio_capture.get_audio_chunk()
        assert chunk is not None
        
        # Validate audio quality
        quality = audio_capture.validate_audio_quality(chunk)
        assert "is_valid" in quality
        assert "rms" in quality
        
        # Apply noise filter
        filtered = audio_capture.apply_noise_filter(chunk)
        assert len(filtered) == len(chunk)
        
        # Stop recording
        audio_capture.stop_recording()
        assert audio_capture.is_recording is False

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_audio_capture_silence_detection_workflow(self, mock_pyaudio):
        """Test silence detection in audio capture workflow."""
        mock_audio_instance = MagicMock()
        mock_stream = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        mock_audio_instance.open.return_value = mock_stream
        
        capture = AudioCapture(silence_threshold=0.02)
        capture._capture_noise_profile = Mock()
        
        # Test with silent audio
        silent_audio = np.ones(1024, dtype=np.float32) * 0.001
        assert capture.detect_silence(silent_audio.tobytes()) == True
        
        # Test with loud audio
        loud_audio = np.ones(1024, dtype=np.float32) * 0.5
        assert capture.detect_silence(loud_audio.tobytes()) == False

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_audio_capture_noise_filtering_workflow(self, mock_pyaudio):
        """Test noise filtering workflow."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        capture.noise_profile = 0.05
        
        # Create audio with noise
        noise = np.random.randn(1024).astype(np.float32) * 0.02
        signal = np.sin(np.linspace(0, 2*np.pi, 1024)).astype(np.float32) * 0.3
        noisy_audio = noise + signal
        
        # Apply filter
        filtered = capture.apply_noise_filter(noisy_audio.tobytes())
        filtered_array = np.frombuffer(filtered, dtype=np.float32)
        
        # Verify filtering occurred
        assert len(filtered) == len(noisy_audio.tobytes())
        assert filtered != noisy_audio.tobytes()

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_audio_capture_quality_validation_workflow(self, mock_pyaudio):
        """Test audio quality validation workflow."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        
        # Test good quality audio
        good_audio = np.random.randn(16000).astype(np.float32) * 0.3
        quality = capture.validate_audio_quality(good_audio.tobytes())
        assert quality["is_valid"] is True
        assert quality["rms"] > 0.01
        
        # Test poor quality audio
        poor_audio = np.ones(16000, dtype=np.float32) * 0.001
        quality = capture.validate_audio_quality(poor_audio.tobytes())
        assert quality["is_valid"] is False
        assert "Signal too quiet" in quality["issues"]

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_audio_capture_buffer_management(self, mock_pyaudio):
        """Test audio buffer management."""
        mock_audio_instance = MagicMock()
        mock_stream = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        mock_audio_instance.open.return_value = mock_stream
        
        test_audio = np.random.randn(1024).astype(np.float32)
        mock_stream.read.return_value = test_audio.tobytes()
        
        capture = AudioCapture()
        capture._capture_noise_profile = Mock()
        capture.start_recording()
        
        # Add multiple chunks to buffer
        for _ in range(5):
            capture.get_audio_chunk()
        
        # Get buffer
        buffer = capture.get_audio_buffer()
        assert len(buffer) > 0
        
        # Clear buffer
        capture.clear_buffer()
        assert len(capture.audio_buffer) == 0
        
        capture.stop_recording()

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_audio_capture_device_listing(self, mock_pyaudio):
        """Test listing available audio devices."""
        mock_audio_instance = MagicMock()
        
        device_info = {
            0: {
                'name': 'Microphone',
                'maxInputChannels': 2,
                'defaultSampleRate': 44100
            },
            1: {
                'name': 'Speaker',
                'maxInputChannels': 0,
                'defaultSampleRate': 44100
            },
            2: {
                'name': 'Line In',
                'maxInputChannels': 1,
                'defaultSampleRate': 48000
            }
        }
        
        mock_audio_instance.get_device_count.return_value = 3
        mock_audio_instance.get_device_info_by_index.side_effect = lambda i: device_info[i]
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        devices = capture.list_input_devices()
        
        # Should only list input devices
        assert len(devices) == 2
        assert devices[0]["name"] == "Microphone"
        assert devices[1]["name"] == "Line In"

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_audio_capture_microphone_info(self, mock_pyaudio):
        """Test getting microphone information."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture(
            sample_rate=44100,
            chunk_size=2048,
            silence_threshold=0.05
        )
        
        info = capture.get_microphone_info()
        
        assert info["sample_rate"] == 44100
        assert info["chunk_size"] == 2048
        assert info["channels"] == 1
        assert info["silence_threshold"] == 0.05
        assert info["is_recording"] is False
