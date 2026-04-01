"""Unit tests for AudioCapture module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.engines.audio_capture import AudioCapture


class TestAudioCaptureInitialization:
    """Test AudioCapture initialization."""

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_initialization_with_defaults(self, mock_pyaudio):
        """Test initialization with default parameters."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        
        assert capture.sample_rate == 16000
        assert capture.chunk_size == 1024
        assert capture.channels == 1
        assert capture.silence_threshold == 0.02
        assert capture.is_recording is False

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_initialization_with_custom_params(self, mock_pyaudio):
        """Test initialization with custom parameters."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture(
            sample_rate=44100,
            chunk_size=2048,
            silence_threshold=0.05
        )
        
        assert capture.sample_rate == 44100
        assert capture.chunk_size == 2048
        assert capture.silence_threshold == 0.05


class TestAudioCaptureRecording:
    """Test audio recording functionality."""

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_start_recording(self, mock_pyaudio):
        """Test starting recording."""
        mock_audio_instance = MagicMock()
        mock_stream = MagicMock()
        mock_audio_instance.open.return_value = mock_stream
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        capture._capture_noise_profile = Mock()  # Mock noise profile capture
        
        capture.start_recording()
        
        assert capture.is_recording is True
        mock_audio_instance.open.assert_called_once()

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_stop_recording(self, mock_pyaudio):
        """Test stopping recording."""
        mock_audio_instance = MagicMock()
        mock_stream = MagicMock()
        mock_audio_instance.open.return_value = mock_stream
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        capture._capture_noise_profile = Mock()
        
        capture.start_recording()
        capture.stop_recording()
        
        assert capture.is_recording is False
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_start_recording_already_recording(self, mock_pyaudio):
        """Test starting recording when already recording."""
        mock_audio_instance = MagicMock()
        mock_stream = MagicMock()
        mock_audio_instance.open.return_value = mock_stream
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        capture._capture_noise_profile = Mock()
        
        capture.start_recording()
        initial_stream = capture.stream
        
        capture.start_recording()  # Try to start again
        
        # Stream should be the same (not opened again)
        assert capture.stream is initial_stream


class TestAudioChunkCapture:
    """Test audio chunk capture."""

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_get_audio_chunk_not_recording(self, mock_pyaudio):
        """Test getting audio chunk when not recording."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        
        chunk = capture.get_audio_chunk()
        
        assert chunk is None

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_get_audio_chunk_recording(self, mock_pyaudio):
        """Test getting audio chunk while recording."""
        mock_audio_instance = MagicMock()
        mock_stream = MagicMock()
        
        # Create test audio data
        test_audio = np.random.randn(1024).astype(np.float32)
        mock_stream.read.return_value = test_audio.tobytes()
        mock_audio_instance.open.return_value = mock_stream
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        capture._capture_noise_profile = Mock()
        capture.start_recording()
        
        chunk = capture.get_audio_chunk()
        
        assert chunk is not None
        assert len(chunk) == len(test_audio.tobytes())


class TestSilenceDetection:
    """Test silence detection."""

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_detect_silence_silent_audio(self, mock_pyaudio):
        """Test detecting silence in silent audio."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture(silence_threshold=0.02)
        
        # Create very quiet audio (below threshold)
        silent_audio = np.ones(1024, dtype=np.float32) * 0.001
        chunk = silent_audio.tobytes()
        
        is_silent = capture.detect_silence(chunk)
        
        assert is_silent == True

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_detect_silence_loud_audio(self, mock_pyaudio):
        """Test detecting silence in loud audio."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture(silence_threshold=0.02)
        
        # Create loud audio (above threshold)
        loud_audio = np.ones(1024, dtype=np.float32) * 0.5
        chunk = loud_audio.tobytes()
        
        is_silent = capture.detect_silence(chunk)
        
        assert is_silent == False

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_detect_silence_threshold_boundary(self, mock_pyaudio):
        """Test silence detection at threshold boundary."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture(silence_threshold=0.02)
        
        # Create audio at exactly the threshold
        threshold_audio = np.ones(1024, dtype=np.float32) * 0.02
        chunk = threshold_audio.tobytes()
        
        is_silent = capture.detect_silence(chunk)
        
        # Should be True since RMS equals threshold (< comparison)
        assert is_silent == True


class TestNoiseFiltering:
    """Test noise filtering."""

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_apply_noise_filter_no_profile(self, mock_pyaudio):
        """Test noise filtering without noise profile."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        capture.noise_profile = None
        
        test_audio = np.random.randn(1024).astype(np.float32)
        chunk = test_audio.tobytes()
        
        filtered = capture.apply_noise_filter(chunk)
        
        # Should return original audio if no profile
        assert filtered == chunk

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_apply_noise_filter_with_profile(self, mock_pyaudio):
        """Test noise filtering with noise profile."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        capture.noise_profile = 0.05
        
        # Create audio with noise and signal
        test_audio = np.random.randn(1024).astype(np.float32) * 0.1
        chunk = test_audio.tobytes()
        
        filtered = capture.apply_noise_filter(chunk)
        
        # Filtered should be different from original
        assert filtered != chunk
        assert len(filtered) == len(chunk)

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_apply_noise_filter_preserves_loud_signals(self, mock_pyaudio):
        """Test that noise filtering preserves loud signals."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        capture.noise_profile = 0.05
        
        # Create audio with loud signal
        test_audio = np.ones(1024, dtype=np.float32) * 0.5
        chunk = test_audio.tobytes()
        
        filtered = capture.apply_noise_filter(chunk)
        filtered_array = np.frombuffer(filtered, dtype=np.float32)
        
        # Loud signal should be preserved (not attenuated to near zero)
        # The high-pass filter will reduce the mean but signal should still be present
        assert np.max(np.abs(filtered_array)) > 0.1


class TestAudioQualityValidation:
    """Test audio quality validation."""

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_validate_audio_quality_good_audio(self, mock_pyaudio):
        """Test validation of good quality audio."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        
        # Create good quality audio
        test_audio = np.random.randn(16000).astype(np.float32) * 0.3
        chunk = test_audio.tobytes()
        
        result = capture.validate_audio_quality(chunk)
        
        assert result["is_valid"] is True
        assert result["rms"] > 0.01
        assert result["clipping_ratio"] < 0.05

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_validate_audio_quality_too_quiet(self, mock_pyaudio):
        """Test validation of too quiet audio."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        
        # Create very quiet audio
        test_audio = np.ones(16000, dtype=np.float32) * 0.001
        chunk = test_audio.tobytes()
        
        result = capture.validate_audio_quality(chunk)
        
        assert result["is_valid"] is False
        assert "Signal too quiet" in result["issues"]

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_validate_audio_quality_clipping(self, mock_pyaudio):
        """Test validation of clipped audio."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        
        # Create clipped audio
        test_audio = np.ones(16000, dtype=np.float32) * 0.99
        chunk = test_audio.tobytes()
        
        result = capture.validate_audio_quality(chunk)
        
        assert result["is_valid"] is False
        assert "Audio clipping detected" in result["issues"]

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_validate_audio_quality_metrics(self, mock_pyaudio):
        """Test that validation returns correct metrics."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture(sample_rate=16000)
        
        # Create test audio
        test_audio = np.random.randn(16000).astype(np.float32) * 0.3
        chunk = test_audio.tobytes()
        
        result = capture.validate_audio_quality(chunk)
        
        assert "rms" in result
        assert "peak" in result
        assert "mean_abs" in result
        assert "clipping_ratio" in result
        assert "duration_seconds" in result
        assert result["duration_seconds"] == 1.0  # 16000 samples at 16000 Hz


class TestAudioBuffer:
    """Test audio buffer functionality."""

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_get_audio_buffer_empty(self, mock_pyaudio):
        """Test getting empty audio buffer."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        
        buffer = capture.get_audio_buffer()
        
        assert buffer == b''

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_clear_buffer(self, mock_pyaudio):
        """Test clearing audio buffer."""
        mock_audio_instance = MagicMock()
        mock_stream = MagicMock()
        
        test_audio = np.random.randn(1024).astype(np.float32)
        mock_stream.read.return_value = test_audio.tobytes()
        mock_audio_instance.open.return_value = mock_stream
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        capture._capture_noise_profile = Mock()
        capture.start_recording()
        
        # Add some audio to buffer
        capture.get_audio_chunk()
        assert len(capture.audio_buffer) > 0
        
        # Clear buffer
        capture.clear_buffer()
        assert len(capture.audio_buffer) == 0


class TestMicrophoneInfo:
    """Test microphone information retrieval."""

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_get_microphone_info(self, mock_pyaudio):
        """Test getting microphone information."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        
        info = capture.get_microphone_info()
        
        assert info["sample_rate"] == 16000
        assert info["chunk_size"] == 1024
        assert info["channels"] == 1
        assert info["is_recording"] is False
        assert info["silence_threshold"] == 0.02

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_list_input_devices(self, mock_pyaudio):
        """Test listing input devices."""
        mock_audio_instance = MagicMock()
        
        # Mock device info
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
            }
        }
        
        mock_audio_instance.get_device_count.return_value = 2
        mock_audio_instance.get_device_info_by_index.side_effect = lambda i: device_info[i]
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        
        devices = capture.list_input_devices()
        
        assert len(devices) == 1
        assert devices[0]["name"] == "Microphone"
        assert devices[0]["channels"] == 2


class TestCleanup:
    """Test cleanup functionality."""

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_cleanup_while_recording(self, mock_pyaudio):
        """Test cleanup while recording."""
        mock_audio_instance = MagicMock()
        mock_stream = MagicMock()
        mock_audio_instance.open.return_value = mock_stream
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        capture._capture_noise_profile = Mock()
        capture.start_recording()
        
        capture.cleanup()
        
        assert capture.is_recording is False
        assert capture.audio is None
        mock_audio_instance.terminate.assert_called_once()

    @patch('src.engines.audio_capture.pyaudio.PyAudio')
    def test_cleanup_not_recording(self, mock_pyaudio):
        """Test cleanup when not recording."""
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        capture = AudioCapture()
        
        capture.cleanup()
        
        assert capture.audio is None
        mock_audio_instance.terminate.assert_called_once()
