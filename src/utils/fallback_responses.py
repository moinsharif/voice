"""Fallback responses for error handling."""


class FallbackResponses:
    """Predefined error messages for graceful error handling.
    
    Provides user-friendly fallback responses when system components fail.
    """

    # Speech Recognition Errors
    SPEECH_RECOGNITION_FAILED = "I didn't catch that. Could you please repeat?"
    SPEECH_RECOGNITION_TIMEOUT = "I didn't hear anything. Please try again."
    SPEECH_RECOGNITION_NOISE = "There's too much background noise. Could you speak up?"
    SPEECH_RECOGNITION_LANGUAGE_ERROR = "I'm having trouble with the language setting. Let me try again."

    # AI Model Errors
    AI_MODEL_FAILED = "I'm having trouble thinking right now. Let me try again."
    AI_MODEL_TIMEOUT = "I'm taking too long to think. Let me try a simpler response."
    AI_MODEL_CONTEXT_ERROR = "I lost track of our conversation. Could you remind me what we were talking about?"
    AI_MODEL_UNAVAILABLE = "I'm not available right now. Please try again later."

    # Face Detection Errors
    FACE_DETECTION_FAILED = "I can't see you right now, but I'm still listening."
    FACE_DETECTION_TIMEOUT = "I'm having trouble seeing you. Let me continue without visual input."
    FACE_DETECTION_CAMERA_ERROR = "I can't access your camera. I'll continue with voice only."
    FACE_DETECTION_NO_FACE = "I don't see a face in the camera. Please position yourself in front of the camera."

    # Mood Analysis Errors
    MOOD_ANALYSIS_FAILED = "I'm having trouble understanding your mood. I'll assume you're doing okay."
    MOOD_ANALYSIS_INCONCLUSIVE = "I'm not sure how you're feeling. Could you tell me?"

    # Text-to-Speech Errors
    TTS_FAILED = "I'm having trouble speaking. Here's your response as text instead."
    TTS_TIMEOUT = "I'm taking too long to speak. Here's your response as text."
    TTS_VOICE_ERROR = "I can't use that voice right now. Let me use the default voice."

    # Database Errors
    DATABASE_ERROR = "I'm having trouble remembering. Let's start fresh."
    DATABASE_CORRUPTION = "I found an issue with my memory. I'm recovering from a backup."
    DATABASE_SAVE_ERROR = "I couldn't save our conversation. Let me try again."
    DATABASE_LOAD_ERROR = "I couldn't load our previous conversation. Starting fresh."

    # Configuration Errors
    CONFIG_INVALID = "I found an issue with my settings. Let me use defaults instead."
    CONFIG_MISSING = "I can't find my configuration. I'll use default settings."
    CONFIG_PARSE_ERROR = "I couldn't understand my settings file. Let me use defaults."

    # System Errors
    SYSTEM_ERROR = "Something went wrong. Let me try to recover."
    SYSTEM_RESOURCE_ERROR = "I'm running low on resources. Some features may be limited."
    SYSTEM_OFFLINE_ERROR = "I need to be online for this feature. Please check your connection."

    # Generic Errors
    GENERIC_ERROR = "I encountered an error. Please try again."
    GENERIC_RETRY = "Let me try that again."
    GENERIC_CONTINUE = "I'll continue with what I can do."

    @classmethod
    def get_response(cls, error_type: str, default: str = GENERIC_ERROR) -> str:
        """Get fallback response by error type.
        
        Args:
            error_type: Type of error (e.g., 'SPEECH_RECOGNITION_FAILED')
            default: Default response if error type not found
            
        Returns:
            Fallback response message
        """
        return getattr(cls, error_type, default)

    @classmethod
    def get_all_responses(cls) -> dict[str, str]:
        """Get all fallback responses.
        
        Returns:
            Dictionary of all fallback responses
        """
        responses = {}
        for attr_name in dir(cls):
            if not attr_name.startswith("_") and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, str):
                    responses[attr_name] = attr_value
        return responses
