"""AI Model Wrapper for Llama 2 integration."""

from typing import Optional, List
from datetime import datetime, timedelta
import hashlib
from src.models.data_models import Exchange
from src.utils.logger import Logger


class ConversationContext:
    """Manages conversation context for AI model."""

    def __init__(self, max_exchanges: int = 10):
        """Initialize context manager.
        
        Args:
            max_exchanges: Maximum number of exchanges to keep in context
        """
        self.max_exchanges = max_exchanges
        self.exchanges: List[Exchange] = []
        self.user_profile = None
        self.mood_state = "neutral"

    def add_exchange(self, exchange: Exchange) -> None:
        """Add exchange to context.
        
        Args:
            exchange: Exchange to add
        """
        self.exchanges.append(exchange)
        # Keep only last N exchanges
        if len(self.exchanges) > self.max_exchanges:
            self.exchanges = self.exchanges[-self.max_exchanges:]

    def get_context_string(self) -> str:
        """Get formatted context string for model input.
        
        Returns:
            Formatted context string
        """
        context_lines = []
        for exchange in self.exchanges[-5:]:  # Last 5 exchanges for context
            context_lines.append(f"User: {exchange.user_message}")
            context_lines.append(f"Assistant: {exchange.ai_response}")
        return "\n".join(context_lines)

    def clear(self) -> None:
        """Clear context."""
        self.exchanges = []


class AIModelWrapper:
    """Wrapper for Llama 2 language model."""

    def __init__(self, model_path: Optional[str] = None):
        """Initialize AI model wrapper.
        
        Args:
            model_path: Path to Llama 2 model file
        """
        self.model_path = model_path
        self.logger = Logger("AIModelWrapper")
        self.model = None
        self.response_cache = {}
        self.cache_ttl = timedelta(hours=1)
        self.response_tone = "friendly"
        self._load_model()

    def _load_model(self) -> None:
        """Load Llama 2 model."""
        try:
            # For now, we'll use a mock implementation
            # In production, this would load llama-cpp-python
            self.logger.info("AI Model initialized (mock mode)")
            self.model = True  # Placeholder
        except Exception as e:
            self.logger.error(f"Failed to load AI model: {e}")
            self.model = None

    def generate_response(self, context: ConversationContext, user_message: str) -> str:
        """Generate response based on context and user message.
        
        Args:
            context: Conversation context
            user_message: User's message
            
        Returns:
            Generated response
        """
        try:
            if not self.model:
                return "I'm having trouble thinking right now. Let me try again."

            # Check cache
            cache_key = self._get_cache_key(user_message)
            if cache_key in self.response_cache:
                cached_response, timestamp = self.response_cache[cache_key]
                if datetime.now() - timestamp < self.cache_ttl:
                    self.logger.info("Using cached response")
                    return cached_response

            # Generate response (mock implementation)
            response = self._generate_response_impl(context, user_message)

            # Cache response
            self.response_cache[cache_key] = (response, datetime.now())

            self.logger.info(f"Generated response: {response[:100]}...")
            return response

        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            return "I'm having trouble thinking right now. Let me try again."

    def _generate_response_impl(self, context: ConversationContext, user_message: str) -> str:
        """Internal response generation implementation.
        
        Args:
            context: Conversation context
            user_message: User's message
            
        Returns:
            Generated response
        """
        # Mock implementation - in production would use actual model
        tone_prefix = {
            "friendly": "That's interesting! ",
            "formal": "I understand. ",
            "empathetic": "I hear you. ",
            "technical": "Technically speaking, ",
        }.get(self.response_tone, "")

        # Simple response generation based on keywords
        if any(word in user_message.lower() for word in ["hello", "hi", "hey"]):
            return tone_prefix + "Hello! How can I help you today?"
        elif any(word in user_message.lower() for word in ["how are you", "how's it going"]):
            return tone_prefix + "I'm doing well, thank you for asking! How are you?"
        elif any(word in user_message.lower() for word in ["bye", "goodbye", "see you"]):
            return tone_prefix + "Goodbye! It was nice talking to you."
        else:
            return tone_prefix + f"That's an interesting point about {user_message[:20]}..."

    def set_response_tone(self, tone: str) -> None:
        """Set response tone.
        
        Args:
            tone: Tone type ("friendly", "formal", "empathetic", "technical")
        """
        valid_tones = ["friendly", "formal", "empathetic", "technical"]
        if tone in valid_tones:
            self.response_tone = tone
            self.logger.info(f"Response tone set to {tone}")
        else:
            self.logger.warning(f"Invalid tone: {tone}")

    def is_model_available(self) -> bool:
        """Check if model is available.
        
        Returns:
            True if model is loaded and available
        """
        return self.model is not None

    def clear_cache(self) -> None:
        """Clear response cache."""
        self.response_cache.clear()
        self.logger.info("Response cache cleared")

    def _get_cache_key(self, message: str) -> str:
        """Generate cache key for message.
        
        Args:
            message: Message to cache
            
        Returns:
            Cache key
        """
        return hashlib.md5(message.encode()).hexdigest()

    def get_model_info(self) -> dict:
        """Get information about loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_path": self.model_path,
            "is_loaded": self.model is not None,
            "response_tone": self.response_tone,
            "cache_size": len(self.response_cache)
        }
