"""
Dependency Injection module for the annotation toolkit.

This module provides a simple but effective dependency injection system
that helps decouple components and improves testability.
"""

from .container import DIContainer, ServiceScope, get_container, resolve, register, register_instance, register_factory
from .exceptions import (
    DIException,
    ServiceNotRegisteredError,
    CircularDependencyError,
    ServiceCreationError,
    InvalidServiceRegistrationError,
)
from .interfaces import (
    AnnotationToolInterface,
    ConfigInterface,
    DIContainerInterface,
    TextAnnotationToolInterface,
    ConversationToolInterface,
    UIWidgetInterface,
    LoggerInterface,
)
from .registry import ServiceRegistry

__all__ = [
    # Container
    "DIContainer",
    "ServiceScope",
    "get_container",
    "resolve",
    "register",
    "register_instance",
    "register_factory",
    # Exceptions
    "DIException",
    "ServiceNotRegisteredError",
    "CircularDependencyError",
    "ServiceCreationError",
    "InvalidServiceRegistrationError",
    # Interfaces
    "AnnotationToolInterface",
    "ConfigInterface",
    "DIContainerInterface",
    "TextAnnotationToolInterface",
    "ConversationToolInterface",
    "UIWidgetInterface",
    "LoggerInterface",
    # Registry
    "ServiceRegistry",
]