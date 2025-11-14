"""
Enhanced error recovery strategies.

This module provides various error recovery patterns including circuit breakers,
retry strategies, and fallback mechanisms.
"""

import time
import random
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from functools import wraps
import asyncio

from .logger import get_logger
from .errors import ErrorCode, AnnotationToolkitError

logger = get_logger()


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RecoveryAttempt:
    """Information about a recovery attempt."""
    timestamp: float
    error: Exception
    attempt_number: int
    delay: float


class ErrorRecoveryStrategy:
    """Base class for error recovery strategies."""

    def __init__(self, name: str):
        """
        Initialize recovery strategy.

        Args:
            name: Strategy name for logging.
        """
        self.name = name

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if operation should be retried.

        Args:
            error: The error that occurred.
            attempt: Current attempt number.

        Returns:
            True if should retry, False otherwise.
        """
        return False

    def get_delay(self, attempt: int, error: Exception) -> float:
        """
        Get delay before next retry attempt.

        Args:
            attempt: Current attempt number.
            error: The error that occurred.

        Returns:
            Delay in seconds.
        """
        return 0.0

    def on_success(self, attempt: int):
        """
        Called when operation succeeds.

        Args:
            attempt: Number of attempts it took.
        """
        pass

    def on_failure(self, error: Exception, attempts: int):
        """
        Called when all retry attempts fail.

        Args:
            error: The final error.
            attempts: Total number of attempts made.
        """
        pass


class ExponentialBackoffStrategy(ErrorRecoveryStrategy):
    """Exponential backoff retry strategy."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0,
                 max_delay: float = 60.0, exponential_base: float = 2.0,
                 jitter: bool = True):
        """
        Initialize exponential backoff strategy.

        Args:
            max_retries: Maximum number of retry attempts.
            base_delay: Initial delay between retries.
            max_delay: Maximum delay between retries.
            exponential_base: Base for exponential calculation.
            jitter: Whether to add random jitter to delays.
        """
        super().__init__("exponential_backoff")
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Check if should retry based on attempt count."""
        return attempt < self.max_retries

    def get_delay(self, attempt: int, error: Exception) -> float:
        """Calculate exponential backoff delay."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add random jitter (±25%)
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)


class LinearBackoffStrategy(ErrorRecoveryStrategy):
    """Linear backoff retry strategy."""

    def __init__(self, max_retries: int = 3, delay: float = 1.0,
                 delay_increment: float = 1.0):
        """
        Initialize linear backoff strategy.

        Args:
            max_retries: Maximum number of retry attempts.
            delay: Initial delay between retries.
            delay_increment: Amount to increase delay by each attempt.
        """
        super().__init__("linear_backoff")
        self.max_retries = max_retries
        self.delay = delay
        self.delay_increment = delay_increment

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Check if should retry based on attempt count."""
        return attempt < self.max_retries

    def get_delay(self, attempt: int, error: Exception) -> float:
        """Calculate linear backoff delay."""
        return self.delay + (attempt * self.delay_increment)


class ConditionalRetryStrategy(ErrorRecoveryStrategy):
    """Retry strategy based on error conditions."""

    def __init__(self, max_retries: int = 3, delay: float = 1.0,
                 retryable_exceptions: Optional[List[Type[Exception]]] = None,
                 non_retryable_exceptions: Optional[List[Type[Exception]]] = None):
        """
        Initialize conditional retry strategy.

        Args:
            max_retries: Maximum number of retry attempts.
            delay: Delay between retries.
            retryable_exceptions: List of exception types that should be retried.
            non_retryable_exceptions: List of exception types that should not be retried.
        """
        super().__init__("conditional_retry")
        self.max_retries = max_retries
        self.delay = delay
        self.retryable_exceptions = retryable_exceptions or []
        self.non_retryable_exceptions = non_retryable_exceptions or []

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Check if should retry based on error type and attempt count."""
        if attempt >= self.max_retries:
            return False

        # Check non-retryable exceptions first
        if self.non_retryable_exceptions:
            if any(isinstance(error, exc_type) for exc_type in self.non_retryable_exceptions):
                return False

        # Check retryable exceptions
        if self.retryable_exceptions:
            return any(isinstance(error, exc_type) for exc_type in self.retryable_exceptions)

        # Default behavior if no specific exceptions configured
        return True

    def get_delay(self, attempt: int, error: Exception) -> float:
        """Get fixed delay."""
        return self.delay


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0,
                 expected_exception: Type[Exception] = Exception):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit.
            reset_timeout: Time to wait before attempting to close circuit.
            expected_exception: Exception type that triggers circuit breaker.
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.expected_exception = expected_exception

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._lock = Lock()

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker.

        Args:
            func: Function to call.
            *args: Function arguments.
            **kwargs: Function keyword arguments.

        Returns:
            Function result.

        Raises:
            CircuitBreakerOpenError: If circuit is open.
        """
        with self._lock:
            if self._state == CircuitBreakerState.OPEN:
                if time.time() - self._last_failure_time >= self.reset_timeout:
                    self._state = CircuitBreakerState.HALF_OPEN
                    logger.info("Circuit breaker moving to HALF_OPEN state")
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful operation."""
        with self._lock:
            if self._state == CircuitBreakerState.HALF_OPEN:
                self._state = CircuitBreakerState.CLOSED
                logger.info("Circuit breaker CLOSED - service recovered")
            self._failure_count = 0

    def _on_failure(self):
        """Handle failed operation."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if (self._state == CircuitBreakerState.CLOSED and
                self._failure_count >= self.failure_threshold):
                self._state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker OPEN - {self._failure_count} failures")
            elif self._state == CircuitBreakerState.HALF_OPEN:
                self._state = CircuitBreakerState.OPEN
                logger.warning("Circuit breaker OPEN - half-open test failed")

    def reset(self):
        """Manually reset circuit breaker."""
        with self._lock:
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._last_failure_time = 0.0
            logger.info("Circuit breaker manually reset")


class FallbackHandler:
    """Handler for fallback mechanisms."""

    def __init__(self):
        """Initialize fallback handler."""
        self.fallbacks: List[Callable] = []

    def add_fallback(self, fallback: Callable):
        """
        Add a fallback function.

        Args:
            fallback: Fallback function to add.
        """
        self.fallbacks.append(fallback)

    def execute_with_fallback(self, primary_func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with fallback options.

        Args:
            primary_func: Primary function to try.
            *args: Function arguments.
            **kwargs: Function keyword arguments.

        Returns:
            Result from primary function or fallback.

        Raises:
            Exception: If all options fail.
        """
        errors = []

        # Try primary function
        try:
            return primary_func(*args, **kwargs)
        except Exception as e:
            errors.append(e)
            logger.warning(f"Primary function failed: {e}")

        # Try fallbacks
        for i, fallback in enumerate(self.fallbacks):
            try:
                logger.info(f"Trying fallback {i + 1}")
                return fallback(*args, **kwargs)
            except Exception as e:
                errors.append(e)
                logger.warning(f"Fallback {i + 1} failed: {e}")

        # All options failed
        raise FallbackExhaustedError("All fallback options failed", errors)


class RetryableOperation:
    """Wrapper for operations with retry logic."""

    def __init__(self, strategy: ErrorRecoveryStrategy):
        """
        Initialize retryable operation.

        Args:
            strategy: Recovery strategy to use.
        """
        self.strategy = strategy
        self.attempts: List[RecoveryAttempt] = []

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute.
            *args: Function arguments.
            **kwargs: Function keyword arguments.

        Returns:
            Function result.

        Raises:
            Exception: If all retry attempts fail.
        """
        attempt = 0
        last_error = None

        while True:
            try:
                result = func(*args, **kwargs)
                self.strategy.on_success(attempt + 1)
                logger.debug(f"Operation succeeded after {attempt + 1} attempts")
                return result

            except Exception as e:
                attempt += 1
                last_error = e

                # Record attempt
                self.attempts.append(RecoveryAttempt(
                    timestamp=time.time(),
                    error=e,
                    attempt_number=attempt,
                    delay=0.0
                ))

                if not self.strategy.should_retry(e, attempt):
                    self.strategy.on_failure(e, attempt)
                    logger.error(f"Operation failed after {attempt} attempts: {e}")
                    raise

                # Calculate delay and wait
                delay = self.strategy.get_delay(attempt, e)
                self.attempts[-1].delay = delay

                logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay:.2f}s")
                if delay > 0:
                    time.sleep(delay)


# Custom exceptions
class CircuitBreakerOpenError(AnnotationToolkitError):
    """Raised when circuit breaker is open."""
    def __init__(self, message: str = "Circuit breaker is open"):
        super().__init__(ErrorCode.OPERATION_FAILED, message)


class FallbackExhaustedError(AnnotationToolkitError):
    """Raised when all fallback options are exhausted."""
    def __init__(self, message: str, errors: List[Exception]):
        super().__init__(ErrorCode.OPERATION_FAILED, message)
        self.errors = errors


# Decorators for easy use
def retry_with_strategy(strategy: ErrorRecoveryStrategy):
    """
    Decorator for adding retry logic to functions.

    Args:
        strategy: Recovery strategy to use.

    Example:
        @retry_with_strategy(ExponentialBackoffStrategy(max_retries=3))
        def unreliable_function():
            # might fail sometimes
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation = RetryableOperation(strategy)
            return operation.execute(func, *args, **kwargs)
        return wrapper
    return decorator


def circuit_breaker(failure_threshold: int = 5, reset_timeout: float = 60.0):
    """
    Decorator for adding circuit breaker pattern to functions.

    Args:
        failure_threshold: Number of failures before opening circuit.
        reset_timeout: Time to wait before attempting to close circuit.

    Example:
        @circuit_breaker(failure_threshold=3, reset_timeout=30.0)
        def external_service_call():
            # call to external service
            pass
    """
    breaker = CircuitBreaker(failure_threshold, reset_timeout)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


def with_fallback(*fallbacks: Callable):
    """
    Decorator for adding fallback mechanisms to functions.

    Args:
        *fallbacks: Fallback functions to try.

    Example:
        @with_fallback(backup_parser, simple_parser)
        def parse_data(data):
            # primary parsing logic
            pass
    """
    handler = FallbackHandler()
    for fallback in fallbacks:
        handler.add_fallback(fallback)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return handler.execute_with_fallback(func, *args, **kwargs)
        return wrapper
    return decorator


# Convenience functions
def exponential_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Convenience decorator for exponential backoff retry."""
    strategy = ExponentialBackoffStrategy(max_retries, base_delay)
    return retry_with_strategy(strategy)


def linear_retry(max_retries: int = 3, delay: float = 1.0):
    """Convenience decorator for linear backoff retry."""
    strategy = LinearBackoffStrategy(max_retries, delay)
    return retry_with_strategy(strategy)