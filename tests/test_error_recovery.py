"""Tests for ErrorRecovery utility."""

import pytest
import time
import asyncio
from src.utils.error_recovery import (
    ErrorRecovery,
    RetryConfig,
    RetryStrategy,
)


class TestRetryConfig:
    """Test RetryConfig dataclass."""

    def test_default_config(self):
        """Test default retry configuration."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_factor == 2.0
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.jitter == 0.1

    def test_custom_config(self):
        """Test custom retry configuration."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=30.0,
            backoff_factor=1.5,
            strategy=RetryStrategy.LINEAR,
            jitter=0.2,
        )
        assert config.max_attempts == 5
        assert config.initial_delay == 0.5
        assert config.max_delay == 30.0
        assert config.backoff_factor == 1.5
        assert config.strategy == RetryStrategy.LINEAR
        assert config.jitter == 0.2


class TestErrorRecoveryBasics:
    """Test basic error recovery functionality."""

    def test_error_recovery_initialization(self):
        """Test error recovery initialization."""
        recovery = ErrorRecovery()
        assert recovery.config is not None
        assert recovery.config.max_attempts == 3

    def test_error_recovery_custom_config(self):
        """Test error recovery with custom config."""
        config = RetryConfig(max_attempts=5)
        recovery = ErrorRecovery(config=config)
        assert recovery.config.max_attempts == 5


class TestRetryMechanism:
    """Test retry mechanism."""

    def test_successful_function_no_retry(self):
        """Test successful function doesn't retry."""
        call_count = 0

        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        recovery = ErrorRecovery()
        result = recovery.retry(success_func)

        assert result == "success"
        assert call_count == 1

    def test_function_fails_then_succeeds(self):
        """Test function that fails then succeeds."""
        call_count = 0

        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("First attempt fails")
            return "success"

        recovery = ErrorRecovery()
        result = recovery.retry(failing_func)

        assert result == "success"
        assert call_count == 2

    def test_function_fails_all_attempts(self):
        """Test function that fails all attempts."""
        call_count = 0

        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        recovery = ErrorRecovery(config=RetryConfig(max_attempts=3))

        with pytest.raises(ValueError):
            recovery.retry(always_fails)

        assert call_count == 3

    def test_retry_with_arguments(self):
        """Test retry with function arguments."""
        def add(a, b):
            return a + b

        recovery = ErrorRecovery()
        result = recovery.retry(add, 2, 3)

        assert result == 5

    def test_retry_with_kwargs(self):
        """Test retry with keyword arguments."""
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        recovery = ErrorRecovery()
        result = recovery.retry(greet, "Alice", greeting="Hi")

        assert result == "Hi, Alice!"


class TestBackoffStrategies:
    """Test different backoff strategies."""

    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            initial_delay=1.0,
            backoff_factor=2.0,
            jitter=0.0,
        )
        recovery = ErrorRecovery(config=config)

        delay0 = recovery._calculate_delay(0)
        delay1 = recovery._calculate_delay(1)
        delay2 = recovery._calculate_delay(2)

        assert delay0 == 1.0
        assert delay1 == 2.0
        assert delay2 == 4.0

    def test_linear_backoff_calculation(self):
        """Test linear backoff delay calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.LINEAR,
            initial_delay=1.0,
            jitter=0.0,
        )
        recovery = ErrorRecovery(config=config)

        delay0 = recovery._calculate_delay(0)
        delay1 = recovery._calculate_delay(1)
        delay2 = recovery._calculate_delay(2)

        assert delay0 == 1.0
        assert delay1 == 2.0
        assert delay2 == 3.0

    def test_fixed_backoff_calculation(self):
        """Test fixed backoff delay calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.FIXED,
            initial_delay=1.0,
            jitter=0.0,
        )
        recovery = ErrorRecovery(config=config)

        delay0 = recovery._calculate_delay(0)
        delay1 = recovery._calculate_delay(1)
        delay2 = recovery._calculate_delay(2)

        assert delay0 == 1.0
        assert delay1 == 1.0
        assert delay2 == 1.0

    def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            initial_delay=1.0,
            max_delay=10.0,
            backoff_factor=2.0,
            jitter=0.0,
        )
        recovery = ErrorRecovery(config=config)

        delay5 = recovery._calculate_delay(5)
        assert delay5 <= 10.0

    def test_jitter_application(self):
        """Test that jitter is applied to delay."""
        config = RetryConfig(
            strategy=RetryStrategy.FIXED,
            initial_delay=1.0,
            jitter=0.5,
        )
        recovery = ErrorRecovery(config=config)

        delays = [recovery._calculate_delay(0) for _ in range(10)]

        # With jitter, delays should vary
        assert len(set(delays)) > 1
        # But should be around initial_delay
        assert all(0.5 <= d <= 1.5 for d in delays)


class TestRetryCallback:
    """Test retry callback functionality."""

    def test_on_retry_callback(self):
        """Test on_retry callback is called."""
        call_count = 0
        retry_attempts = []

        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Fails")
            return "success"

        def on_retry(attempt, exception):
            retry_attempts.append((attempt, str(exception)))

        recovery = ErrorRecovery(config=RetryConfig(max_attempts=3))
        result = recovery.retry(failing_func, on_retry=on_retry)

        assert result == "success"
        assert len(retry_attempts) == 2
        assert retry_attempts[0][0] == 1
        assert retry_attempts[1][0] == 2


class TestRetryWithFallback:
    """Test retry with fallback functionality."""

    def test_retry_with_fallback_success(self):
        """Test retry with fallback when function succeeds."""
        def success_func():
            return "success"

        recovery = ErrorRecovery()
        result = recovery.retry_with_fallback(success_func, "fallback")

        assert result == "success"

    def test_retry_with_fallback_failure(self):
        """Test retry with fallback when function fails."""
        def failing_func():
            raise ValueError("Always fails")

        recovery = ErrorRecovery(config=RetryConfig(max_attempts=2))
        result = recovery.retry_with_fallback(failing_func, "fallback")

        assert result == "fallback"

    def test_retry_with_fallback_custom_value(self):
        """Test retry with fallback using custom value."""
        def failing_func():
            raise ValueError("Fails")

        recovery = ErrorRecovery(config=RetryConfig(max_attempts=1))
        result = recovery.retry_with_fallback(failing_func, {"error": True})

        assert result == {"error": True}


class TestAsyncRetry:
    """Test async retry functionality."""

    @pytest.mark.asyncio
    async def test_async_retry_success(self):
        """Test async retry with successful function."""
        async def success_func():
            return "success"

        recovery = ErrorRecovery()
        result = await recovery.retry_async(success_func)

        assert result == "success"

    @pytest.mark.asyncio
    async def test_async_retry_with_failure(self):
        """Test async retry with failing function."""
        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("First attempt fails")
            return "success"

        recovery = ErrorRecovery()
        result = await recovery.retry_async(failing_func)

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_async_retry_all_failures(self):
        """Test async retry when all attempts fail."""
        async def always_fails():
            raise ValueError("Always fails")

        recovery = ErrorRecovery(config=RetryConfig(max_attempts=2))

        with pytest.raises(ValueError):
            await recovery.retry_async(always_fails)

    @pytest.mark.asyncio
    async def test_async_retry_with_fallback(self):
        """Test async retry with fallback."""
        async def failing_func():
            raise ValueError("Fails")

        recovery = ErrorRecovery(config=RetryConfig(max_attempts=1))
        result = await recovery.retry_async_with_fallback(failing_func, "fallback")

        assert result == "fallback"


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    def test_circuit_breaker_success(self):
        """Test circuit breaker with successful function."""
        def success_func():
            return "success"

        recovery = ErrorRecovery()
        result = recovery.circuit_breaker(success_func)

        assert result == "success"

    def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures."""
        call_count = 0

        def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Fails")

        recovery = ErrorRecovery()

        # First 5 calls should fail
        for _ in range(5):
            with pytest.raises(ValueError):
                recovery.circuit_breaker(failing_func, failure_threshold=5)

        # 6th call should raise circuit breaker error
        with pytest.raises(RuntimeError, match="Circuit breaker open"):
            recovery.circuit_breaker(failing_func, failure_threshold=5)

    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout."""
        call_count = 0

        def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Fails")

        recovery = ErrorRecovery()

        # Trigger circuit breaker
        for _ in range(5):
            with pytest.raises(ValueError):
                recovery.circuit_breaker(failing_func, failure_threshold=5)

        # Circuit should be open
        with pytest.raises(RuntimeError):
            recovery.circuit_breaker(failing_func, failure_threshold=5, recovery_timeout=0.1)

        # Wait for recovery timeout
        time.sleep(0.2)

        # Circuit should attempt recovery (half-open state)
        with pytest.raises(ValueError):
            recovery.circuit_breaker(failing_func, failure_threshold=5, recovery_timeout=0.1)

    def test_circuit_breaker_resets_on_success(self):
        """Test circuit breaker resets on success."""
        call_count = 0

        def sometimes_fails():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ValueError("Fails")
            return "success"

        recovery = ErrorRecovery()

        # First two calls fail
        for _ in range(2):
            with pytest.raises(ValueError):
                recovery.circuit_breaker(sometimes_fails, failure_threshold=5)

        # Third call succeeds
        result = recovery.circuit_breaker(sometimes_fails, failure_threshold=5)
        assert result == "success"

        # Circuit should be reset, so failure count should be 0
        # Next failure should not trigger circuit breaker immediately
        call_count = 0

        def always_fails():
            raise ValueError("Fails")

        # Should fail but not trigger circuit breaker yet
        with pytest.raises(ValueError):
            recovery.circuit_breaker(always_fails, failure_threshold=5)
