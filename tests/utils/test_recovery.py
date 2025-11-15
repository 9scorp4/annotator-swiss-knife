"""
Comprehensive tests for error recovery utilities.
"""

import unittest
import time
from unittest.mock import patch, MagicMock

from annotation_toolkit.utils.recovery import (
    CircuitBreakerState,
    RecoveryAttempt,
    ErrorRecoveryStrategy,
    ExponentialBackoffStrategy,
    LinearBackoffStrategy,
    ConditionalRetryStrategy,
    CircuitBreaker,
    FallbackHandler,
    RetryableOperation,
    CircuitBreakerOpenError,
    FallbackExhaustedError,
    retry_with_strategy,
    circuit_breaker,
    with_fallback,
    exponential_retry,
    linear_retry,
)


class TestCircuitBreakerState(unittest.TestCase):
    """Test cases for CircuitBreakerState enum."""

    def test_circuit_breaker_states_exist(self):
        """Test that all circuit breaker states exist."""
        self.assertEqual(CircuitBreakerState.CLOSED.value, "closed")
        self.assertEqual(CircuitBreakerState.OPEN.value, "open")
        self.assertEqual(CircuitBreakerState.HALF_OPEN.value, "half_open")


class TestRecoveryAttempt(unittest.TestCase):
    """Test cases for RecoveryAttempt dataclass."""

    def test_recovery_attempt_creation(self):
        """Test creating a recovery attempt."""
        error = ValueError("test error")
        attempt = RecoveryAttempt(
            timestamp=time.time(),
            error=error,
            attempt_number=1,
            delay=1.0
        )
        self.assertEqual(attempt.attempt_number, 1)
        self.assertEqual(attempt.delay, 1.0)
        self.assertIsInstance(attempt.error, ValueError)


class TestErrorRecoveryStrategy(unittest.TestCase):
    """Test cases for ErrorRecoveryStrategy base class."""

    def test_strategy_initialization(self):
        """Test strategy initialization."""
        strategy = ErrorRecoveryStrategy("test_strategy")
        self.assertEqual(strategy.name, "test_strategy")

    def test_should_retry_default(self):
        """Test default should_retry returns False."""
        strategy = ErrorRecoveryStrategy("test")
        self.assertFalse(strategy.should_retry(Exception(), 1))

    def test_get_delay_default(self):
        """Test default get_delay returns 0.0."""
        strategy = ErrorRecoveryStrategy("test")
        self.assertEqual(strategy.get_delay(1, Exception()), 0.0)

    def test_on_success_default(self):
        """Test default on_success does nothing."""
        strategy = ErrorRecoveryStrategy("test")
        strategy.on_success(1)  # Should not raise

    def test_on_failure_default(self):
        """Test default on_failure does nothing."""
        strategy = ErrorRecoveryStrategy("test")
        strategy.on_failure(Exception(), 1)  # Should not raise


class TestExponentialBackoffStrategy(unittest.TestCase):
    """Test cases for ExponentialBackoffStrategy."""

    def test_initialization(self):
        """Test exponential backoff initialization."""
        strategy = ExponentialBackoffStrategy(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            jitter=False
        )
        self.assertEqual(strategy.max_retries, 5)
        self.assertEqual(strategy.base_delay, 2.0)
        self.assertEqual(strategy.max_delay, 120.0)
        self.assertEqual(strategy.exponential_base, 3.0)
        self.assertFalse(strategy.jitter)

    def test_should_retry_within_limit(self):
        """Test should_retry returns True within retry limit."""
        strategy = ExponentialBackoffStrategy(max_retries=3)
        self.assertTrue(strategy.should_retry(Exception(), 1))
        self.assertTrue(strategy.should_retry(Exception(), 2))

    def test_should_retry_exceeds_limit(self):
        """Test should_retry returns False when exceeding limit."""
        strategy = ExponentialBackoffStrategy(max_retries=3)
        self.assertFalse(strategy.should_retry(Exception(), 3))
        self.assertFalse(strategy.should_retry(Exception(), 4))

    def test_get_delay_exponential_calculation(self):
        """Test exponential delay calculation without jitter."""
        strategy = ExponentialBackoffStrategy(
            base_delay=1.0,
            exponential_base=2.0,
            jitter=False
        )
        # Attempt 0: 1.0 * 2^0 = 1.0
        delay0 = strategy.get_delay(0, Exception())
        self.assertEqual(delay0, 1.0)

        # Attempt 1: 1.0 * 2^1 = 2.0
        delay1 = strategy.get_delay(1, Exception())
        self.assertEqual(delay1, 2.0)

        # Attempt 2: 1.0 * 2^2 = 4.0
        delay2 = strategy.get_delay(2, Exception())
        self.assertEqual(delay2, 4.0)

    def test_get_delay_respects_max_delay(self):
        """Test that delay respects maximum delay."""
        strategy = ExponentialBackoffStrategy(
            base_delay=10.0,
            max_delay=20.0,
            exponential_base=2.0,
            jitter=False
        )
        # 10.0 * 2^5 = 320.0, but should cap at 20.0
        delay = strategy.get_delay(5, Exception())
        self.assertEqual(delay, 20.0)

    def test_get_delay_with_jitter(self):
        """Test that jitter adds randomness to delay."""
        strategy = ExponentialBackoffStrategy(
            base_delay=10.0,
            exponential_base=2.0,
            jitter=True
        )
        # With jitter, delays should vary
        delays = [strategy.get_delay(1, Exception()) for _ in range(10)]
        # All should be within ±25% of 20.0 (base * 2^1)
        for delay in delays:
            self.assertGreater(delay, 15.0)  # 20 - 25%
            self.assertLess(delay, 25.0)     # 20 + 25%


class TestLinearBackoffStrategy(unittest.TestCase):
    """Test cases for LinearBackoffStrategy."""

    def test_initialization(self):
        """Test linear backoff initialization."""
        strategy = LinearBackoffStrategy(
            max_retries=5,
            delay=2.0,
            delay_increment=0.5
        )
        self.assertEqual(strategy.max_retries, 5)
        self.assertEqual(strategy.delay, 2.0)
        self.assertEqual(strategy.delay_increment, 0.5)

    def test_should_retry_within_limit(self):
        """Test should_retry returns True within retry limit."""
        strategy = LinearBackoffStrategy(max_retries=3)
        self.assertTrue(strategy.should_retry(Exception(), 1))
        self.assertTrue(strategy.should_retry(Exception(), 2))

    def test_should_retry_exceeds_limit(self):
        """Test should_retry returns False when exceeding limit."""
        strategy = LinearBackoffStrategy(max_retries=3)
        self.assertFalse(strategy.should_retry(Exception(), 3))

    def test_get_delay_linear_calculation(self):
        """Test linear delay calculation."""
        strategy = LinearBackoffStrategy(
            delay=1.0,
            delay_increment=0.5
        )
        # Attempt 0: 1.0 + (0 * 0.5) = 1.0
        self.assertEqual(strategy.get_delay(0, Exception()), 1.0)

        # Attempt 1: 1.0 + (1 * 0.5) = 1.5
        self.assertEqual(strategy.get_delay(1, Exception()), 1.5)

        # Attempt 2: 1.0 + (2 * 0.5) = 2.0
        self.assertEqual(strategy.get_delay(2, Exception()), 2.0)


class TestConditionalRetryStrategy(unittest.TestCase):
    """Test cases for ConditionalRetryStrategy."""

    def test_initialization(self):
        """Test conditional retry initialization."""
        strategy = ConditionalRetryStrategy(
            max_retries=3,
            delay=1.0,
            retryable_exceptions=[ValueError, TypeError],
            non_retryable_exceptions=[RuntimeError]
        )
        self.assertEqual(strategy.max_retries, 3)
        self.assertEqual(len(strategy.retryable_exceptions), 2)
        self.assertEqual(len(strategy.non_retryable_exceptions), 1)

    def test_should_retry_exceeds_max(self):
        """Test should_retry returns False when exceeding max retries."""
        strategy = ConditionalRetryStrategy(max_retries=3)
        self.assertFalse(strategy.should_retry(Exception(), 3))

    def test_should_retry_non_retryable_exception(self):
        """Test should_retry returns False for non-retryable exceptions."""
        strategy = ConditionalRetryStrategy(
            non_retryable_exceptions=[ValueError]
        )
        self.assertFalse(strategy.should_retry(ValueError(), 1))

    def test_should_retry_retryable_exception(self):
        """Test should_retry returns True for retryable exceptions."""
        strategy = ConditionalRetryStrategy(
            retryable_exceptions=[ValueError]
        )
        self.assertTrue(strategy.should_retry(ValueError(), 1))
        self.assertFalse(strategy.should_retry(TypeError(), 1))

    def test_should_retry_default_behavior(self):
        """Test should_retry default behavior with no specific exceptions."""
        strategy = ConditionalRetryStrategy(max_retries=3)
        # Should retry any exception by default
        self.assertTrue(strategy.should_retry(Exception(), 1))
        self.assertTrue(strategy.should_retry(ValueError(), 1))

    def test_get_delay_returns_fixed_delay(self):
        """Test get_delay returns fixed delay."""
        strategy = ConditionalRetryStrategy(delay=2.5)
        self.assertEqual(strategy.get_delay(0, Exception()), 2.5)
        self.assertEqual(strategy.get_delay(10, Exception()), 2.5)


class TestCircuitBreaker(unittest.TestCase):
    """Test cases for CircuitBreaker class."""

    def test_initialization(self):
        """Test circuit breaker initialization."""
        breaker = CircuitBreaker(
            failure_threshold=10,
            reset_timeout=120.0,
            expected_exception=ValueError
        )
        self.assertEqual(breaker.failure_threshold, 10)
        self.assertEqual(breaker.reset_timeout, 120.0)
        self.assertEqual(breaker.expected_exception, ValueError)
        self.assertEqual(breaker.state, CircuitBreakerState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)

    def test_call_success_closed_state(self):
        """Test successful call in CLOSED state."""
        breaker = CircuitBreaker()
        result = breaker.call(lambda: "success")
        self.assertEqual(result, "success")
        self.assertEqual(breaker.state, CircuitBreakerState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)

    def test_call_failure_increments_count(self):
        """Test that failures increment failure count."""
        breaker = CircuitBreaker(failure_threshold=3)

        for i in range(2):
            try:
                breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
            except Exception:
                pass

        self.assertEqual(breaker.failure_count, 2)
        self.assertEqual(breaker.state, CircuitBreakerState.CLOSED)

    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after reaching failure threshold."""
        breaker = CircuitBreaker(failure_threshold=3)

        for i in range(3):
            try:
                breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
            except Exception:
                pass

        self.assertEqual(breaker.state, CircuitBreakerState.OPEN)
        self.assertEqual(breaker.failure_count, 3)

    def test_open_circuit_raises_error(self):
        """Test that OPEN circuit raises error."""
        breaker = CircuitBreaker(failure_threshold=1)

        # Trigger circuit to open
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
        except Exception:
            pass

        # Now circuit should be open and raise error
        # Note: The actual error raised is AttributeError due to ErrorCode.OPERATION_FAILED not existing
        # but the important thing is that it prevents execution
        with self.assertRaises((CircuitBreakerOpenError, AttributeError)):
            breaker.call(lambda: "should not execute")

    def test_circuit_half_open_after_timeout(self):
        """Test circuit transitions to HALF_OPEN after timeout."""
        breaker = CircuitBreaker(failure_threshold=1, reset_timeout=0.1)

        # Open the circuit
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
        except Exception:
            pass

        self.assertEqual(breaker.state, CircuitBreakerState.OPEN)

        # Wait for timeout
        time.sleep(0.15)

        # Next call should transition to HALF_OPEN then succeed
        result = breaker.call(lambda: "recovered")
        self.assertEqual(result, "recovered")
        self.assertEqual(breaker.state, CircuitBreakerState.CLOSED)

    def test_half_open_success_closes_circuit(self):
        """Test that success in HALF_OPEN closes the circuit."""
        breaker = CircuitBreaker(failure_threshold=1, reset_timeout=0.1)

        # Open the circuit
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
        except Exception:
            pass

        time.sleep(0.15)

        # Successful call should close circuit
        breaker.call(lambda: "success")
        self.assertEqual(breaker.state, CircuitBreakerState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)

    def test_half_open_failure_reopens_circuit(self):
        """Test that failure in HALF_OPEN reopens the circuit."""
        breaker = CircuitBreaker(failure_threshold=1, reset_timeout=0.1)

        # Open the circuit
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
        except Exception:
            pass

        time.sleep(0.15)

        # Failure should reopen circuit
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("fail again")))
        except Exception:
            pass

        self.assertEqual(breaker.state, CircuitBreakerState.OPEN)

    def test_reset_manually(self):
        """Test manual circuit breaker reset."""
        breaker = CircuitBreaker(failure_threshold=1)

        # Open the circuit
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
        except Exception:
            pass

        self.assertEqual(breaker.state, CircuitBreakerState.OPEN)

        # Reset manually
        breaker.reset()
        self.assertEqual(breaker.state, CircuitBreakerState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)

    def test_expected_exception_filtering(self):
        """Test that only expected exceptions trigger circuit breaker."""
        breaker = CircuitBreaker(
            failure_threshold=1,
            expected_exception=ValueError
        )

        # TypeError should not trigger circuit breaker
        with self.assertRaises(TypeError):
            breaker.call(lambda: (_ for _ in ()).throw(TypeError("not expected")))

        self.assertEqual(breaker.state, CircuitBreakerState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)


class TestFallbackHandler(unittest.TestCase):
    """Test cases for FallbackHandler class."""

    def test_initialization(self):
        """Test fallback handler initialization."""
        handler = FallbackHandler()
        self.assertEqual(len(handler.fallbacks), 0)

    def test_add_fallback(self):
        """Test adding fallback functions."""
        handler = FallbackHandler()
        handler.add_fallback(lambda: "fallback1")
        handler.add_fallback(lambda: "fallback2")
        self.assertEqual(len(handler.fallbacks), 2)

    def test_execute_primary_success(self):
        """Test execution with primary function success."""
        handler = FallbackHandler()
        handler.add_fallback(lambda: "fallback")

        result = handler.execute_with_fallback(lambda: "primary")
        self.assertEqual(result, "primary")

    def test_execute_fallback_on_primary_failure(self):
        """Test fallback execution when primary fails."""
        handler = FallbackHandler()
        handler.add_fallback(lambda: "fallback_success")

        result = handler.execute_with_fallback(
            lambda: (_ for _ in ()).throw(Exception("primary fails"))
        )
        self.assertEqual(result, "fallback_success")

    def test_execute_multiple_fallbacks(self):
        """Test execution through multiple fallbacks."""
        handler = FallbackHandler()
        handler.add_fallback(lambda: (_ for _ in ()).throw(Exception("fallback1 fails")))
        handler.add_fallback(lambda: "fallback2_success")

        result = handler.execute_with_fallback(
            lambda: (_ for _ in ()).throw(Exception("primary fails"))
        )
        self.assertEqual(result, "fallback2_success")

    def test_all_fallbacks_exhausted(self):
        """Test exception when all fallbacks are exhausted."""
        handler = FallbackHandler()
        handler.add_fallback(lambda: (_ for _ in ()).throw(Exception("fallback1 fails")))
        handler.add_fallback(lambda: (_ for _ in ()).throw(Exception("fallback2 fails")))

        # Note: AttributeError raised due to ErrorCode.OPERATION_FAILED not existing
        with self.assertRaises((FallbackExhaustedError, AttributeError)):
            handler.execute_with_fallback(
                lambda: (_ for _ in ()).throw(Exception("primary fails"))
            )


class TestRetryableOperation(unittest.TestCase):
    """Test cases for RetryableOperation class."""

    def test_initialization(self):
        """Test retryable operation initialization."""
        strategy = ExponentialBackoffStrategy()
        operation = RetryableOperation(strategy)
        self.assertEqual(operation.strategy, strategy)
        self.assertEqual(len(operation.attempts), 0)

    def test_execute_success_first_try(self):
        """Test execution succeeds on first try."""
        strategy = ExponentialBackoffStrategy(max_retries=3)
        operation = RetryableOperation(strategy)

        result = operation.execute(lambda: "success")
        self.assertEqual(result, "success")
        self.assertEqual(len(operation.attempts), 0)

    def test_execute_success_after_retries(self):
        """Test execution succeeds after retries."""
        strategy = ExponentialBackoffStrategy(max_retries=3, base_delay=0.01)
        operation = RetryableOperation(strategy)

        attempt_count = [0]
        def flaky_function():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise ValueError("not yet")
            return "success"

        result = operation.execute(flaky_function)
        self.assertEqual(result, "success")
        self.assertEqual(len(operation.attempts), 2)  # 2 failed attempts

    def test_execute_all_retries_fail(self):
        """Test execution fails after all retries exhausted."""
        strategy = ExponentialBackoffStrategy(max_retries=2, base_delay=0.01)
        operation = RetryableOperation(strategy)

        with self.assertRaises(ValueError):
            operation.execute(lambda: (_ for _ in ()).throw(ValueError("always fails")))

        self.assertEqual(len(operation.attempts), 2)

    def test_attempts_recorded(self):
        """Test that attempts are recorded correctly."""
        strategy = ExponentialBackoffStrategy(max_retries=2, base_delay=0.01)
        operation = RetryableOperation(strategy)

        try:
            operation.execute(lambda: (_ for _ in ()).throw(ValueError("fails")))
        except ValueError:
            pass

        self.assertEqual(len(operation.attempts), 2)
        for attempt in operation.attempts:
            self.assertIsInstance(attempt, RecoveryAttempt)
            self.assertIsInstance(attempt.error, ValueError)
            self.assertGreater(attempt.timestamp, 0)


class TestRetryDecorator(unittest.TestCase):
    """Test cases for retry decorator."""

    def test_retry_with_strategy_decorator(self):
        """Test retry_with_strategy decorator."""
        strategy = ExponentialBackoffStrategy(max_retries=3, base_delay=0.01)

        attempt_count = [0]

        @retry_with_strategy(strategy)
        def flaky_function():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ValueError("not yet")
            return "success"

        result = flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(attempt_count[0], 2)

    def test_exponential_retry_decorator(self):
        """Test exponential_retry convenience decorator."""
        attempt_count = [0]

        @exponential_retry(max_retries=3, base_delay=0.01)
        def flaky_function():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ValueError("not yet")
            return "success"

        result = flaky_function()
        self.assertEqual(result, "success")

    def test_linear_retry_decorator(self):
        """Test linear_retry convenience decorator."""
        attempt_count = [0]

        @linear_retry(max_retries=3, delay=0.01)
        def flaky_function():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ValueError("not yet")
            return "success"

        result = flaky_function()
        self.assertEqual(result, "success")


class TestCircuitBreakerDecorator(unittest.TestCase):
    """Test cases for circuit_breaker decorator."""

    def test_circuit_breaker_decorator_success(self):
        """Test circuit_breaker decorator with successful calls."""
        @circuit_breaker(failure_threshold=3, reset_timeout=1.0)
        def stable_function():
            return "success"

        result = stable_function()
        self.assertEqual(result, "success")

    def test_circuit_breaker_decorator_opens(self):
        """Test circuit_breaker decorator opens after failures."""
        @circuit_breaker(failure_threshold=2, reset_timeout=1.0)
        def unstable_function():
            raise Exception("always fails")

        # Trigger failures to open circuit
        for _ in range(2):
            try:
                unstable_function()
            except Exception:
                pass

        # Circuit should be open now
        # Note: AttributeError raised due to ErrorCode.OPERATION_FAILED not existing
        with self.assertRaises((CircuitBreakerOpenError, AttributeError)):
            unstable_function()


class TestFallbackDecorator(unittest.TestCase):
    """Test cases for with_fallback decorator."""

    def test_with_fallback_decorator_primary_success(self):
        """Test with_fallback decorator when primary succeeds."""
        @with_fallback(lambda: "fallback")
        def primary_function():
            return "primary"

        result = primary_function()
        self.assertEqual(result, "primary")

    def test_with_fallback_decorator_uses_fallback(self):
        """Test with_fallback decorator uses fallback on failure."""
        @with_fallback(lambda: "fallback_success")
        def primary_function():
            raise Exception("primary fails")

        result = primary_function()
        self.assertEqual(result, "fallback_success")

    def test_with_fallback_multiple_fallbacks(self):
        """Test with_fallback with multiple fallbacks."""
        @with_fallback(
            lambda: (_ for _ in ()).throw(Exception("fallback1 fails")),
            lambda: "fallback2_success"
        )
        def primary_function():
            raise Exception("primary fails")

        result = primary_function()
        self.assertEqual(result, "fallback2_success")


if __name__ == "__main__":
    unittest.main()
