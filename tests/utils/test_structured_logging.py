"""
Comprehensive tests for structured logging utilities.
"""

import unittest
import time
import json
from unittest.mock import patch, MagicMock, call

from annotation_toolkit.utils.structured_logging import (
    LogContext,
    PerformanceMetrics,
    AuditEvent,
    StructuredLogger,
    LoggingContext,
    PerformanceTracker,
    AuditLogger,
    get_structured_logger,
    log_performance,
    with_logging_context,
    audit_file_operation,
    correlation_id,
    user_id,
    operation_name,
)


class TestLogContext(unittest.TestCase):
    """Test cases for LogContext dataclass."""

    def test_log_context_creation(self):
        """Test creating log context."""
        context = LogContext(
            correlation_id="corr123",
            user_id="user456",
            operation_name="test_op",
            component="test_component",
            extra_data={"key": "value"}
        )
        self.assertEqual(context.correlation_id, "corr123")
        self.assertEqual(context.user_id, "user456")
        self.assertEqual(context.operation_name, "test_op")

    def test_log_context_to_dict(self):
        """Test converting log context to dict."""
        context = LogContext(
            correlation_id="corr123",
            user_id="user456"
        )
        result = context.to_dict()
        self.assertEqual(result["correlation_id"], "corr123")
        self.assertEqual(result["user_id"], "user456")

    def test_log_context_to_dict_excludes_none(self):
        """Test that to_dict excludes None values."""
        context = LogContext(correlation_id="corr123")
        result = context.to_dict()
        self.assertIn("correlation_id", result)
        self.assertNotIn("user_id", result)
        self.assertNotIn("operation_name", result)


class TestPerformanceMetrics(unittest.TestCase):
    """Test cases for PerformanceMetrics dataclass."""

    def test_performance_metrics_creation(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(
            operation="test_op",
            duration_ms=123.45,
            start_time=1000.0,
            end_time=1000.12345,
            success=True,
            error=None,
            memory_usage_mb=50.0,
            cpu_usage_percent=25.0
        )
        self.assertEqual(metrics.operation, "test_op")
        self.assertEqual(metrics.duration_ms, 123.45)
        self.assertTrue(metrics.success)

    def test_performance_metrics_with_error(self):
        """Test performance metrics with error."""
        metrics = PerformanceMetrics(
            operation="failed_op",
            duration_ms=10.0,
            start_time=1000.0,
            end_time=1000.01,
            success=False,
            error="ValueError: test error"
        )
        self.assertFalse(metrics.success)
        self.assertIsNotNone(metrics.error)


class TestAuditEvent(unittest.TestCase):
    """Test cases for AuditEvent dataclass."""

    def test_audit_event_creation(self):
        """Test creating audit event."""
        event = AuditEvent(
            event_type="file_access",
            timestamp=time.time(),
            user_id="user123",
            resource="/path/to/file",
            action="read",
            result="success",
            details={"size": 1024},
            correlation_id="corr456"
        )
        self.assertEqual(event.event_type, "file_access")
        self.assertEqual(event.action, "read")
        self.assertEqual(event.result, "success")


class TestStructuredLogger(unittest.TestCase):
    """Test cases for StructuredLogger class."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = StructuredLogger(
            name="test_logger",
            enable_metrics=True,
            enable_audit=True
        )

    def test_initialization(self):
        """Test logger initialization."""
        self.assertTrue(self.logger.enable_metrics)
        self.assertTrue(self.logger.enable_audit)
        self.assertEqual(len(self.logger._metrics), 0)
        self.assertEqual(len(self.logger._audit_events), 0)

    def test_initialization_disabled_features(self):
        """Test logger with disabled features."""
        logger = StructuredLogger(
            enable_metrics=False,
            enable_audit=False
        )
        self.assertFalse(logger.enable_metrics)
        self.assertFalse(logger.enable_audit)

    @patch('annotation_toolkit.utils.structured_logging.get_logger')
    def test_debug_logging(self, mock_get_logger):
        """Test debug logging."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger()
        logger.debug("Debug message", component="test", extra_data={"key": "value"})

        mock_logger.debug.assert_called_once()
        call_arg = mock_logger.debug.call_args[0][0]
        self.assertIsInstance(call_arg, str)
        data = json.loads(call_arg)
        self.assertEqual(data["message"], "Debug message")

    @patch('annotation_toolkit.utils.structured_logging.get_logger')
    def test_info_logging(self, mock_get_logger):
        """Test info logging."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger()
        logger.info("Info message")

        mock_logger.info.assert_called_once()

    @patch('annotation_toolkit.utils.structured_logging.get_logger')
    def test_warning_logging(self, mock_get_logger):
        """Test warning logging."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger()
        logger.warning("Warning message")

        mock_logger.warning.assert_called_once()

    @patch('annotation_toolkit.utils.structured_logging.get_logger')
    def test_error_logging(self, mock_get_logger):
        """Test error logging."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        logger = StructuredLogger()
        error = ValueError("test error")
        logger.error("Error message", error=error)

        mock_logger.error.assert_called_once()
        call_arg = mock_logger.error.call_args[0][0]
        data = json.loads(call_arg)
        self.assertEqual(data["message"], "Error message")
        self.assertIn("error_type", data["data"])
        self.assertEqual(data["data"]["error_type"], "ValueError")

    def test_record_metrics(self):
        """Test recording metrics."""
        metrics = PerformanceMetrics(
            operation="test_op",
            duration_ms=100.0,
            start_time=1000.0,
            end_time=1000.1,
            success=True
        )
        self.logger.record_metrics(metrics)

        recorded = self.logger.get_metrics()
        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded[0].operation, "test_op")

    def test_record_metrics_disabled(self):
        """Test that metrics are not recorded when disabled."""
        logger = StructuredLogger(enable_metrics=False)
        metrics = PerformanceMetrics(
            operation="test_op",
            duration_ms=100.0,
            start_time=1000.0,
            end_time=1000.1,
            success=True
        )
        logger.record_metrics(metrics)

        recorded = logger.get_metrics()
        self.assertEqual(len(recorded), 0)

    def test_record_audit_event(self):
        """Test recording audit event."""
        event = AuditEvent(
            event_type="file_access",
            timestamp=time.time(),
            user_id="user123",
            resource="/file.txt",
            action="read",
            result="success"
        )
        self.logger.record_audit_event(event)

        recorded = self.logger.get_audit_events()
        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded[0].event_type, "file_access")

    def test_record_audit_event_disabled(self):
        """Test that audit events are not recorded when disabled."""
        logger = StructuredLogger(enable_audit=False)
        event = AuditEvent(
            event_type="file_access",
            timestamp=time.time(),
            user_id="user123",
            resource="/file.txt",
            action="read",
            result="success"
        )
        logger.record_audit_event(event)

        recorded = logger.get_audit_events()
        self.assertEqual(len(recorded), 0)

    def test_get_metrics_filtered(self):
        """Test getting metrics filtered by operation."""
        metrics1 = PerformanceMetrics(
            operation="op1",
            duration_ms=100.0,
            start_time=1000.0,
            end_time=1000.1,
            success=True
        )
        metrics2 = PerformanceMetrics(
            operation="op2",
            duration_ms=200.0,
            start_time=1000.0,
            end_time=1000.2,
            success=True
        )
        self.logger.record_metrics(metrics1)
        self.logger.record_metrics(metrics2)

        op1_metrics = self.logger.get_metrics(operation="op1")
        self.assertEqual(len(op1_metrics), 1)
        self.assertEqual(op1_metrics[0].operation, "op1")

    def test_get_audit_events_filtered(self):
        """Test getting audit events with filters."""
        event1 = AuditEvent(
            event_type="file_access",
            timestamp=time.time(),
            user_id="user1",
            resource="/file1.txt",
            action="read",
            result="success"
        )
        event2 = AuditEvent(
            event_type="file_access",
            timestamp=time.time(),
            user_id="user2",
            resource="/file2.txt",
            action="write",
            result="success"
        )
        self.logger.record_audit_event(event1)
        self.logger.record_audit_event(event2)

        user1_events = self.logger.get_audit_events(user_id="user1")
        self.assertEqual(len(user1_events), 1)
        self.assertEqual(user1_events[0].user_id, "user1")

        file1_events = self.logger.get_audit_events(resource="/file1.txt")
        self.assertEqual(len(file1_events), 1)

    def test_clear_metrics(self):
        """Test clearing metrics."""
        metrics = PerformanceMetrics(
            operation="test",
            duration_ms=100.0,
            start_time=1000.0,
            end_time=1000.1,
            success=True
        )
        self.logger.record_metrics(metrics)
        self.assertEqual(len(self.logger.get_metrics()), 1)

        self.logger.clear_metrics()
        self.assertEqual(len(self.logger.get_metrics()), 0)

    def test_clear_audit_events(self):
        """Test clearing audit events."""
        event = AuditEvent(
            event_type="test",
            timestamp=time.time(),
            user_id="user1",
            resource="resource",
            action="action",
            result="success"
        )
        self.logger.record_audit_event(event)
        self.assertEqual(len(self.logger.get_audit_events()), 1)

        self.logger.clear_audit_events()
        self.assertEqual(len(self.logger.get_audit_events()), 0)


class TestLoggingContext(unittest.TestCase):
    """Test cases for LoggingContext context manager."""

    def test_context_manager_sets_correlation_id(self):
        """Test that context manager sets correlation ID."""
        with LoggingContext(correlation_id="test123"):
            self.assertEqual(correlation_id.get(), "test123")

    def test_context_manager_sets_user_id(self):
        """Test that context manager sets user ID."""
        with LoggingContext(user_id="user456"):
            self.assertEqual(user_id.get(), "user456")

    def test_context_manager_sets_operation_name(self):
        """Test that context manager sets operation name."""
        with LoggingContext(operation_name="test_op"):
            self.assertEqual(operation_name.get(), "test_op")

    def test_context_manager_generates_correlation_id(self):
        """Test that context manager generates correlation ID if not provided."""
        with LoggingContext() as ctx:
            self.assertIsNotNone(ctx.correlation_id)
            self.assertEqual(correlation_id.get(), ctx.correlation_id)

    def test_context_manager_resets_after_exit(self):
        """Test that context is reset after exiting."""
        # Set initial value
        token = correlation_id.set("initial")

        with LoggingContext(correlation_id="temporary"):
            self.assertEqual(correlation_id.get(), "temporary")

        # Should be reset to initial
        self.assertEqual(correlation_id.get(), "initial")

        # Clean up
        correlation_id.set(token.old_value)

    def test_nested_contexts(self):
        """Test nested logging contexts."""
        with LoggingContext(correlation_id="outer"):
            self.assertEqual(correlation_id.get(), "outer")

            with LoggingContext(correlation_id="inner"):
                self.assertEqual(correlation_id.get(), "inner")

            # Should be back to outer
            self.assertEqual(correlation_id.get(), "outer")


class TestPerformanceTracker(unittest.TestCase):
    """Test cases for PerformanceTracker context manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = StructuredLogger(enable_metrics=True)
        # Mock the info method to avoid serialization issues
        self.logger.info = MagicMock()

    def test_performance_tracker_basic(self):
        """Test basic performance tracking."""
        with PerformanceTracker("test_op", self.logger):
            time.sleep(0.01)

        metrics = self.logger.get_metrics()
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0].operation, "test_op")
        self.assertGreater(metrics[0].duration_ms, 10)
        self.assertTrue(metrics[0].success)

    def test_performance_tracker_records_error(self):
        """Test that performance tracker records errors."""
        try:
            with PerformanceTracker("failing_op", self.logger):
                raise ValueError("test error")
        except ValueError:
            pass

        metrics = self.logger.get_metrics()
        self.assertEqual(len(metrics), 1)
        self.assertFalse(metrics[0].success)
        # Error contains just the message, not the exception type
        self.assertIn("test error", metrics[0].error)


class TestAuditLogger(unittest.TestCase):
    """Test cases for AuditLogger class."""

    def setUp(self):
        """Set up test fixtures."""
        self.structured_logger = StructuredLogger(enable_audit=True)
        # Mock the info method to avoid serialization issues
        self.structured_logger.info = MagicMock()
        self.audit_logger = AuditLogger(self.structured_logger)

    def test_log_file_access(self):
        """Test logging file access."""
        self.audit_logger.log_file_access(
            "/path/to/file.txt",
            "read",
            True,
            {"bytes_read": 1024}
        )

        events = self.structured_logger.get_audit_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "file_access")
        self.assertEqual(events[0].action, "read")
        self.assertEqual(events[0].result, "success")

    def test_log_file_access_failure(self):
        """Test logging failed file access."""
        self.audit_logger.log_file_access(
            "/path/to/file.txt",
            "write",
            False
        )

        events = self.structured_logger.get_audit_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].result, "failure")

    def test_log_security_event(self):
        """Test logging security event."""
        self.audit_logger.log_security_event(
            "authentication",
            "user_login",
            True,
            {"ip_address": "192.168.1.1"}
        )

        events = self.structured_logger.get_audit_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "security")

    def test_log_configuration_change(self):
        """Test logging configuration change."""
        self.audit_logger.log_configuration_change(
            "max_retries",
            3,
            5,
            True
        )

        events = self.structured_logger.get_audit_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "configuration")
        self.assertEqual(events[0].details["old_value"], 3)
        self.assertEqual(events[0].details["new_value"], 5)


class TestGetStructuredLogger(unittest.TestCase):
    """Test cases for get_structured_logger function."""

    def test_get_structured_logger_returns_instance(self):
        """Test getting global structured logger."""
        logger = get_structured_logger()
        self.assertIsInstance(logger, StructuredLogger)

    def test_get_structured_logger_returns_same_instance(self):
        """Test that multiple calls return the same instance."""
        logger1 = get_structured_logger()
        logger2 = get_structured_logger()
        self.assertIs(logger1, logger2)


class TestLogPerformanceDecorator(unittest.TestCase):
    """Test cases for log_performance decorator."""

    @patch('annotation_toolkit.utils.structured_logging.get_structured_logger')
    def test_log_performance_decorator_basic(self, mock_get_logger):
        """Test basic usage of log_performance decorator."""
        mock_logger = MagicMock()
        mock_logger.get_metrics.return_value = [
            PerformanceMetrics(
                operation="test_operation",
                duration_ms=10.0,
                start_time=1000.0,
                end_time=1000.01,
                success=True
            )
        ]
        mock_get_logger.return_value = mock_logger

        @log_performance("test_operation")
        def test_function():
            time.sleep(0.01)
            return "result"

        result = test_function()
        self.assertEqual(result, "result")

        # Verify that record_metrics was called
        self.assertTrue(mock_logger.record_metrics.called)

    @patch('annotation_toolkit.utils.structured_logging.get_structured_logger')
    def test_log_performance_decorator_with_error(self, mock_get_logger):
        """Test log_performance decorator with error."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        @log_performance("failing_operation")
        def failing_function():
            raise ValueError("test error")

        with self.assertRaises(ValueError):
            failing_function()

        # Verify that record_metrics was called
        self.assertTrue(mock_logger.record_metrics.called)
        # Check that the metrics show failure
        call_args = mock_logger.record_metrics.call_args
        metrics = call_args[0][0]
        self.assertFalse(metrics.success)


class TestWithLoggingContextDecorator(unittest.TestCase):
    """Test cases for with_logging_context decorator."""

    def test_with_logging_context_decorator(self):
        """Test with_logging_context decorator."""
        @with_logging_context(operation_name="test_op", user_id="user123")
        def test_function():
            self.assertEqual(operation_name.get(), "test_op")
            self.assertEqual(user_id.get(), "user123")
            return "result"

        result = test_function()
        self.assertEqual(result, "result")


class TestAuditFileOperationDecorator(unittest.TestCase):
    """Test cases for audit_file_operation decorator."""

    @patch('annotation_toolkit.utils.structured_logging.get_structured_logger')
    def test_audit_file_operation_decorator_success(self, mock_get_logger):
        """Test audit_file_operation decorator on successful operation."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        @audit_file_operation("read")
        def read_file(file_path):
            return f"contents of {file_path}"

        result = read_file("/test/file.txt")
        self.assertEqual(result, "contents of /test/file.txt")

        # Verify audit event was recorded
        self.assertTrue(mock_logger.record_audit_event.called)
        call_args = mock_logger.record_audit_event.call_args
        event = call_args[0][0]
        self.assertEqual(event.action, "read")
        self.assertEqual(event.result, "success")

    @patch('annotation_toolkit.utils.structured_logging.get_structured_logger')
    def test_audit_file_operation_decorator_failure(self, mock_get_logger):
        """Test audit_file_operation decorator on failed operation."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        @audit_file_operation("write")
        def write_file(file_path):
            raise IOError("write failed")

        with self.assertRaises(IOError):
            write_file("/test/file.txt")

        # Verify audit event was recorded
        self.assertTrue(mock_logger.record_audit_event.called)
        call_args = mock_logger.record_audit_event.call_args
        event = call_args[0][0]
        self.assertEqual(event.result, "failure")

    @patch('annotation_toolkit.utils.structured_logging.get_structured_logger')
    def test_audit_file_operation_with_kwarg(self, mock_get_logger):
        """Test audit_file_operation with file_path as kwarg."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        @audit_file_operation("read")
        def read_file(file_path):
            return "contents"

        result = read_file(file_path="/test/file.txt")
        self.assertEqual(result, "contents")

        # Verify audit event was recorded
        self.assertTrue(mock_logger.record_audit_event.called)


if __name__ == "__main__":
    unittest.main()
