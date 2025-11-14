"""
Structured logging utilities.

This module provides structured logging with context, metrics collection,
and audit trail capabilities.
"""

import json
import time
import uuid
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from contextvars import ContextVar
from functools import wraps
import logging
import threading
from pathlib import Path

from .logger import get_logger

# Context variables for tracking request/operation context
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
operation_name: ContextVar[Optional[str]] = ContextVar('operation_name', default=None)


@dataclass
class LogContext:
    """Structured log context."""
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    operation_name: Optional[str] = None
    component: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                result[key] = value
        return result


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""
    operation: str
    duration_ms: float
    start_time: float
    end_time: float
    success: bool
    error: Optional[str] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    extra_metrics: Optional[Dict[str, Any]] = None


@dataclass
class AuditEvent:
    """Audit trail event."""
    event_type: str
    timestamp: float
    user_id: Optional[str]
    resource: str
    action: str
    result: str  # success/failure
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None


class StructuredLogger:
    """Enhanced logger with structured logging capabilities."""

    def __init__(self, name: str = "annotation_toolkit",
                 enable_metrics: bool = True,
                 enable_audit: bool = True):
        """
        Initialize structured logger.

        Args:
            name: Logger name.
            enable_metrics: Whether to collect performance metrics.
            enable_audit: Whether to maintain audit trail.
        """
        self.logger = get_logger(name)
        self.enable_metrics = enable_metrics
        self.enable_audit = enable_audit
        self._metrics: List[PerformanceMetrics] = []
        self._audit_events: List[AuditEvent] = []
        self._lock = threading.Lock()

    def _get_current_context(self) -> LogContext:
        """Get current logging context."""
        return LogContext(
            correlation_id=correlation_id.get(),
            user_id=user_id.get(),
            operation_name=operation_name.get()
        )

    def _format_message(self, message: str, context: LogContext,
                       extra_data: Optional[Dict[str, Any]] = None) -> str:
        """Format message with structured context."""
        log_data = {
            "message": message,
            "timestamp": time.time(),
            "context": context.to_dict()
        }

        if extra_data:
            log_data["data"] = extra_data

        return json.dumps(log_data, default=str)

    def debug(self, message: str, component: Optional[str] = None,
              extra_data: Optional[Dict[str, Any]] = None):
        """Log debug message with context."""
        context = self._get_current_context()
        context.component = component
        context.extra_data = extra_data
        formatted = self._format_message(message, context, extra_data)
        self.logger.debug(formatted)

    def info(self, message: str, component: Optional[str] = None,
             extra_data: Optional[Dict[str, Any]] = None):
        """Log info message with context."""
        context = self._get_current_context()
        context.component = component
        context.extra_data = extra_data
        formatted = self._format_message(message, context, extra_data)
        self.logger.info(formatted)

    def warning(self, message: str, component: Optional[str] = None,
                extra_data: Optional[Dict[str, Any]] = None):
        """Log warning message with context."""
        context = self._get_current_context()
        context.component = component
        context.extra_data = extra_data
        formatted = self._format_message(message, context, extra_data)
        self.logger.warning(formatted)

    def error(self, message: str, error: Optional[Exception] = None,
              component: Optional[str] = None,
              extra_data: Optional[Dict[str, Any]] = None):
        """Log error message with context."""
        context = self._get_current_context()
        context.component = component

        if error:
            error_data = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "error_details": getattr(error, 'details', None)
            }
            if extra_data:
                error_data.update(extra_data)
            extra_data = error_data

        context.extra_data = extra_data
        formatted = self._format_message(message, context, extra_data)
        self.logger.error(formatted)

    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics."""
        if not self.enable_metrics:
            return

        with self._lock:
            self._metrics.append(metrics)

        # Log metrics
        self.info(
            f"Performance metrics for {metrics.operation}",
            component="metrics",
            extra_data={
                "operation": metrics.operation,
                "duration_ms": metrics.duration_ms,
                "success": metrics.success,
                "error": metrics.error,
                "memory_usage_mb": metrics.memory_usage_mb,
                "cpu_usage_percent": metrics.cpu_usage_percent,
                "extra_metrics": metrics.extra_metrics
            }
        )

    def record_audit_event(self, event: AuditEvent):
        """Record audit event."""
        if not self.enable_audit:
            return

        with self._lock:
            self._audit_events.append(event)

        # Log audit event
        self.info(
            f"Audit: {event.action} on {event.resource}",
            component="audit",
            extra_data={
                "event_type": event.event_type,
                "user_id": event.user_id,
                "resource": event.resource,
                "action": event.action,
                "result": event.result,
                "details": event.details,
                "correlation_id": event.correlation_id
            }
        )

    def get_metrics(self, operation: Optional[str] = None) -> List[PerformanceMetrics]:
        """
        Get collected metrics.

        Args:
            operation: Filter by operation name.

        Returns:
            List of metrics.
        """
        with self._lock:
            if operation:
                return [m for m in self._metrics if m.operation == operation]
            return self._metrics.copy()

    def get_audit_events(self, user_id: Optional[str] = None,
                        resource: Optional[str] = None) -> List[AuditEvent]:
        """
        Get audit events.

        Args:
            user_id: Filter by user ID.
            resource: Filter by resource.

        Returns:
            List of audit events.
        """
        with self._lock:
            events = self._audit_events.copy()

        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if resource:
            events = [e for e in events if e.resource == resource]

        return events

    def clear_metrics(self):
        """Clear collected metrics."""
        with self._lock:
            self._metrics.clear()

    def clear_audit_events(self):
        """Clear audit events."""
        with self._lock:
            self._audit_events.clear()


class LoggingContext:
    """Context manager for structured logging context."""

    def __init__(self, correlation_id: Optional[str] = None,
                 user_id: Optional[str] = None,
                 operation_name: Optional[str] = None):
        """
        Initialize logging context.

        Args:
            correlation_id: Correlation ID for request tracking.
            user_id: User ID for audit trail.
            operation_name: Name of the operation being performed.
        """
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.user_id = user_id
        self.operation_name = operation_name
        self._tokens = []

    def __enter__(self):
        """Enter context and set context variables."""
        self._tokens.append(correlation_id.set(self.correlation_id))
        if self.user_id:
            self._tokens.append(user_id.set(self.user_id))
        if self.operation_name:
            self._tokens.append(operation_name.set(self.operation_name))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and reset context variables."""
        for token in reversed(self._tokens):
            if token:
                token.var.set(token.old_value)


class PerformanceTracker:
    """Performance tracking context manager."""

    def __init__(self, operation: str, logger: StructuredLogger,
                 track_memory: bool = False, track_cpu: bool = False):
        """
        Initialize performance tracker.

        Args:
            operation: Name of the operation to track.
            logger: Structured logger instance.
            track_memory: Whether to track memory usage.
            track_cpu: Whether to track CPU usage.
        """
        self.operation = operation
        self.logger = logger
        self.track_memory = track_memory
        self.track_cpu = track_cpu
        self.start_time = 0.0
        self.end_time = 0.0
        self.success = True
        self.error: Optional[str] = None

    def __enter__(self):
        """Start performance tracking."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End performance tracking and record metrics."""
        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000

        if exc_type is not None:
            self.success = False
            self.error = str(exc_val) if exc_val else str(exc_type)

        # Get system metrics if requested
        memory_usage = None
        cpu_usage = None

        if self.track_memory:
            try:
                import psutil
                process = psutil.Process()
                memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            except ImportError:
                pass

        if self.track_cpu:
            try:
                import psutil
                cpu_usage = psutil.cpu_percent()
            except ImportError:
                pass

        metrics = PerformanceMetrics(
            operation=self.operation,
            duration_ms=duration_ms,
            start_time=self.start_time,
            end_time=self.end_time,
            success=self.success,
            error=self.error,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage
        )

        self.logger.record_metrics(metrics)


class AuditLogger:
    """Specialized logger for audit events."""

    def __init__(self, logger: StructuredLogger):
        """
        Initialize audit logger.

        Args:
            logger: Structured logger instance.
        """
        self.logger = logger

    def log_file_access(self, file_path: str, action: str, success: bool,
                       details: Optional[Dict[str, Any]] = None):
        """Log file access event."""
        event = AuditEvent(
            event_type="file_access",
            timestamp=time.time(),
            user_id=user_id.get(),
            resource=file_path,
            action=action,
            result="success" if success else "failure",
            details=details,
            correlation_id=correlation_id.get()
        )
        self.logger.record_audit_event(event)

    def log_security_event(self, event_type: str, resource: str,
                          success: bool, details: Optional[Dict[str, Any]] = None):
        """Log security-related event."""
        event = AuditEvent(
            event_type="security",
            timestamp=time.time(),
            user_id=user_id.get(),
            resource=resource,
            action=event_type,
            result="success" if success else "failure",
            details=details,
            correlation_id=correlation_id.get()
        )
        self.logger.record_audit_event(event)

    def log_configuration_change(self, setting: str, old_value: Any,
                                new_value: Any, success: bool):
        """Log configuration change event."""
        event = AuditEvent(
            event_type="configuration",
            timestamp=time.time(),
            user_id=user_id.get(),
            resource=setting,
            action="update",
            result="success" if success else "failure",
            details={
                "old_value": old_value,
                "new_value": new_value
            },
            correlation_id=correlation_id.get()
        )
        self.logger.record_audit_event(event)


# Global structured logger instance
_global_logger: Optional[StructuredLogger] = None


def get_structured_logger() -> StructuredLogger:
    """Get global structured logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger()
    return _global_logger


# Decorators for easy use
def log_performance(operation: str, track_memory: bool = False,
                   track_cpu: bool = False):
    """
    Decorator for automatic performance logging.

    Args:
        operation: Name of the operation.
        track_memory: Whether to track memory usage.
        track_cpu: Whether to track CPU usage.

    Example:
        @log_performance("data_processing", track_memory=True)
        def process_data(data):
            # processing logic
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_structured_logger()
            with PerformanceTracker(operation, logger, track_memory, track_cpu):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def with_logging_context(correlation_id: Optional[str] = None,
                        user_id: Optional[str] = None,
                        operation_name: Optional[str] = None):
    """
    Decorator for setting logging context.

    Args:
        correlation_id: Correlation ID.
        user_id: User ID.
        operation_name: Operation name.

    Example:
        @with_logging_context(operation_name="file_processing")
        def process_file(file_path):
            # processing logic
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with LoggingContext(correlation_id, user_id, operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def audit_file_operation(action: str):
    """
    Decorator for auditing file operations.

    Args:
        action: Description of the file action.

    Example:
        @audit_file_operation("read")
        def read_file(file_path):
            # file reading logic
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract file path from arguments
            file_path = None
            if args:
                file_path = str(args[0])  # Assume first arg is file path
            elif 'file_path' in kwargs:
                file_path = str(kwargs['file_path'])

            logger = get_structured_logger()
            audit_logger = AuditLogger(logger)

            try:
                result = func(*args, **kwargs)
                if file_path:
                    audit_logger.log_file_access(file_path, action, True)
                return result
            except Exception as e:
                if file_path:
                    audit_logger.log_file_access(
                        file_path, action, False,
                        {"error": str(e)}
                    )
                raise
        return wrapper
    return decorator