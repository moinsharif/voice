"""Tests for FallbackResponses utility."""

import pytest
from src.utils.fallback_responses import FallbackResponses


class TestFallbackResponsesBasics:
    """Test basic fallback response functionality."""

    def test_speech_recognition_failed_response(self):
        """Test speech recognition failed response."""
        response = FallbackResponses.SPEECH_RECOGNITION_FAILED
        assert isinstance(response, str)
        assert len(response) > 0
        assert "didn't catch" in response.lower()

    def test_ai_model_failed_response(self):
        """Test AI model failed response."""
        response = FallbackResponses.AI_MODEL_FAILED
        assert isinstance(response, str)
        assert len(response) > 0
        assert "trouble" in response.lower()

    def test_face_detection_failed_response(self):
        """Test face detection failed response."""
        response = FallbackResponses.FACE_DETECTION_FAILED
        assert isinstance(response, str)
        assert len(response) > 0

    def test_tts_failed_response(self):
        """Test text-to-speech failed response."""
        response = FallbackResponses.TTS_FAILED
        assert isinstance(response, str)
        assert len(response) > 0

    def test_database_error_response(self):
        """Test database error response."""
        response = FallbackResponses.DATABASE_ERROR
        assert isinstance(response, str)
        assert len(response) > 0


class TestGetResponse:
    """Test get_response method."""

    def test_get_response_by_name(self):
        """Test retrieving response by name."""
        response = FallbackResponses.get_response("SPEECH_RECOGNITION_FAILED")
        assert response == FallbackResponses.SPEECH_RECOGNITION_FAILED

    def test_get_response_invalid_name(self):
        """Test retrieving response with invalid name."""
        response = FallbackResponses.get_response("INVALID_ERROR")
        assert response == FallbackResponses.GENERIC_ERROR

    def test_get_response_custom_default(self):
        """Test retrieving response with custom default."""
        custom_default = "Custom error message"
        response = FallbackResponses.get_response("INVALID_ERROR", default=custom_default)
        assert response == custom_default

    def test_get_response_all_error_types(self):
        """Test retrieving all error types."""
        error_types = [
            "SPEECH_RECOGNITION_FAILED",
            "AI_MODEL_FAILED",
            "FACE_DETECTION_FAILED",
            "TTS_FAILED",
            "DATABASE_ERROR",
            "CONFIG_INVALID",
            "SYSTEM_ERROR",
        ]

        for error_type in error_types:
            response = FallbackResponses.get_response(error_type)
            assert isinstance(response, str)
            assert len(response) > 0


class TestGetAllResponses:
    """Test get_all_responses method."""

    def test_get_all_responses_returns_dict(self):
        """Test that get_all_responses returns dictionary."""
        responses = FallbackResponses.get_all_responses()
        assert isinstance(responses, dict)

    def test_get_all_responses_not_empty(self):
        """Test that get_all_responses returns non-empty dictionary."""
        responses = FallbackResponses.get_all_responses()
        assert len(responses) > 0

    def test_get_all_responses_contains_expected_keys(self):
        """Test that get_all_responses contains expected keys."""
        responses = FallbackResponses.get_all_responses()

        expected_keys = [
            "SPEECH_RECOGNITION_FAILED",
            "AI_MODEL_FAILED",
            "FACE_DETECTION_FAILED",
            "TTS_FAILED",
            "DATABASE_ERROR",
        ]

        for key in expected_keys:
            assert key in responses

    def test_get_all_responses_values_are_strings(self):
        """Test that all response values are strings."""
        responses = FallbackResponses.get_all_responses()

        for key, value in responses.items():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_get_all_responses_no_private_attributes(self):
        """Test that get_all_responses excludes private attributes."""
        responses = FallbackResponses.get_all_responses()

        for key in responses.keys():
            assert not key.startswith("_")


class TestResponseCategories:
    """Test response categories."""

    def test_speech_recognition_responses(self):
        """Test speech recognition error responses."""
        responses = [
            FallbackResponses.SPEECH_RECOGNITION_FAILED,
            FallbackResponses.SPEECH_RECOGNITION_TIMEOUT,
            FallbackResponses.SPEECH_RECOGNITION_NOISE,
        ]

        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0

    def test_ai_model_responses(self):
        """Test AI model error responses."""
        responses = [
            FallbackResponses.AI_MODEL_FAILED,
            FallbackResponses.AI_MODEL_TIMEOUT,
            FallbackResponses.AI_MODEL_CONTEXT_ERROR,
        ]

        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0

    def test_face_detection_responses(self):
        """Test face detection error responses."""
        responses = [
            FallbackResponses.FACE_DETECTION_FAILED,
            FallbackResponses.FACE_DETECTION_TIMEOUT,
            FallbackResponses.FACE_DETECTION_CAMERA_ERROR,
        ]

        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0

    def test_database_responses(self):
        """Test database error responses."""
        responses = [
            FallbackResponses.DATABASE_ERROR,
            FallbackResponses.DATABASE_CORRUPTION,
            FallbackResponses.DATABASE_SAVE_ERROR,
        ]

        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0

    def test_system_responses(self):
        """Test system error responses."""
        responses = [
            FallbackResponses.SYSTEM_ERROR,
            FallbackResponses.SYSTEM_RESOURCE_ERROR,
            FallbackResponses.SYSTEM_OFFLINE_ERROR,
        ]

        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0


class TestResponseUserFriendliness:
    """Test that responses are user-friendly."""

    def test_responses_are_conversational(self):
        """Test that responses use conversational language."""
        responses = FallbackResponses.get_all_responses()

        # Check for conversational patterns
        conversational_patterns = ["I", "me", "let", "try", "please", "sorry"]

        for response in responses.values():
            # At least one conversational pattern should be present
            has_pattern = any(
                pattern.lower() in response.lower() for pattern in conversational_patterns
            )
            assert has_pattern, f"Response not conversational: {response}"

    def test_responses_are_not_technical(self):
        """Test that responses avoid technical jargon."""
        responses = FallbackResponses.get_all_responses()

        # Technical terms to avoid
        technical_terms = ["exception", "traceback", "null", "undefined", "crash"]

        for response in responses.values():
            for term in technical_terms:
                assert term.lower() not in response.lower()

    def test_responses_are_actionable(self):
        """Test that responses are helpful and user-friendly."""
        responses = FallbackResponses.get_all_responses()

        # Helpful patterns - responses should either suggest action or be informative
        helpful_patterns = ["try", "please", "let", "again", "continue", "remind", "tell", "could", "will", "i'm", "i'll"]

        for response in responses.values():
            has_helpful = any(
                pattern.lower() in response.lower() for pattern in helpful_patterns
            )
            # All responses should be helpful or informative
            assert has_helpful, f"Response not helpful: {response}"
