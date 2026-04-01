"""Error recovery mechanisms with exponential backoff retry logic."""

import time
import asyncio
from typing import Callable, TypeVar, Optional, Any
from dataclasses import dataclass
from enum import Enum

T = TypeVar("T")


class RetryStrategy(Enum):
    """Retry strategy enumeration."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


@dataclass
class RetryConfig:
    """Configuration for retry behavior.
    
    Attributes:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for exponential backoff
        strategy: Retry strategy (exponential, linear, fixed)
        jitter: Add random jitter to delay (0.0-1.0)
    """

    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    jitter: float = 0.1


class ErrorRecovery:
    """Error recovery with exponential backoff retry logic.
    
    Provides mechanisms for automatic retry with configurable backoff strategies.
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize error recovery.
        
        Args:
            config: Retry configuration (uses defaults if not provided)
        """
        self.config = config or RetryConfig()

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        if self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.initial_delay * (
                self.config.backoff_factor ** attempt
            )
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.initial_delay * (attempt + 1)
        else:  # FIXED
            delay = self.config.initial_delay

        # Cap at max delay
        delay = min(delay, self.config.max_delay)

        # Add jitter
        if self.config.jitter > 0:
            import random

            jitter_amount = delay * self.config.jitter
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay)  # Ensure non-negative

        return delay

    def retry(
        self,
        func: Callable[..., T],
        *args,
        on_retry: Optional[Callable[[int, Exception], None]] = None,
        **kwargs,
    ) -> T:
        """Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            *args: Positional arguments for function
            on_retry: Callback on retry (attempt_number, exception)
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            Exception: Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(self.config.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)

                    if on_retry:
                        on_retry(attempt + 1, e)

                    time.sleep(delay)

        raise last_exception

    async def retry_async(
        self,
        func: Callable[..., Any],
        *args,
        on_retry: Optional[Callable[[int, Exception], None]] = None,
        **kwargs,
    ) -> T:
        """Retry an async function with exponential backoff.
        
        Args:
            func: Async function to retry
            *args: Positional arguments for function
            on_retry: Callback on retry (attempt_number, exception)
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            Exception: Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)

                    if on_retry:
                        on_retry(attempt + 1, e)

                    await asyncio.sleep(delay)

        raise last_exception

    def retry_with_fallback(
        self,
        func: Callable[..., T],
        fallback: T,
        *args,
        on_retry: Optional[Callable[[int, Exception], None]] = None,
        **kwargs,
    ) -> T:
        """Retry a function, returning fallback value if all retries fail.
        
        Args:
            func: Function to retry
            fallback: Fallback value if all retries fail
            *args: Positional arguments for function
            on_retry: Callback on retry (attempt_number, exception)
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result or fallback value
        """
        try:
            return self.retry(func, *args, on_retry=on_retry, **kwargs)
        except Exception:
            return fallback

    async def retry_async_with_fallback(
        self,
        func: Callable[..., Any],
        fallback: T,
        *args,
        on_retry: Optional[Callable[[int, Exception], None]] = None,
        **kwargs,
    ) -> T:
        """Retry an async function, returning fallback value if all retries fail.
        
        Args:
            func: Async function to retry
            fallback: Fallback value if all retries fail
            *args: Positional arguments for function
            on_retry: Callback on retry (attempt_number, exception)
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result or fallback value
        """
        try:
            return await self.retry_async(func, *args, on_retry=on_retry, **kwargs)
        except Exception:
            return fallback

    def circuit_breaker(
        self,
        func: Callable[..., T],
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        *args,
        **kwargs,
    ) -> T:
        """Execute function with circuit breaker pattern.
        
        Circuit breaker prevents repeated calls to failing function.
        
        Args:
            func: Function to execute
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if not hasattr(self, "_circuit_state"):
            self._circuit_state = {}

        func_name = func.__name__
        if func_name not in self._circuit_state:
            self._circuit_state[func_name] = {
                "failures": 0,
                "last_failure_time": None,
                "state": "closed",  # closed, open, half-open
            }

        state = self._circuit_state[func_name]

        # Check if circuit should recover
        if state["state"] == "open":
            if (
                time.time() - state["last_failure_time"] > recovery_timeout
            ):
                state["state"] = "half-open"
                state["failures"] = 0
            else:
                raise RuntimeError(
                    f"Circuit breaker open for {func_name}. "
                    f"Retry after {recovery_timeout}s"
                )

        try:
            result = func(*args, **kwargs)
            # Success - reset state
            state["failures"] = 0
            state["state"] = "closed"
            return result
        except Exception as e:
            state["failures"] += 1
            state["last_failure_time"] = time.time()

            if state["failures"] >= failure_threshold:
                state["state"] = "open"

            raise e
