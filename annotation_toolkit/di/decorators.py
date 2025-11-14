"""
Dependency injection decorators and utilities.

This module provides decorators and utilities to simplify dependency injection
in classes and functions.
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, TypeVar, get_type_hints
import inspect

from .container import get_container
from .exceptions import ServiceNotRegisteredError

T = TypeVar('T')


def inject(*dependencies: Type) -> Callable:
    """
    Decorator to automatically inject dependencies into a function or method.

    Args:
        *dependencies: Types to inject. If not specified, uses type hints.

    Example:
        @inject
        def process_data(self, parser: JsonParser, validator: Validator):
            # parser and validator will be automatically injected
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            container = get_container()

            # Get type hints if no explicit dependencies provided
            deps = dependencies if dependencies else []
            if not deps:
                type_hints = get_type_hints(func)
                # Skip 'self' and 'return' annotations
                deps = [hint for name, hint in type_hints.items()
                       if name not in ('self', 'return')]

            # Resolve dependencies
            injected_kwargs = {}
            sig = inspect.signature(func)

            for param_name, param in sig.parameters.items():
                if param_name in kwargs:
                    continue  # Already provided

                if param.annotation != inspect.Parameter.empty:
                    try:
                        injected_kwargs[param_name] = container.resolve(param.annotation)
                    except ServiceNotRegisteredError:
                        # Don't inject if service not registered
                        pass

            return func(*args, **{**injected_kwargs, **kwargs})
        return wrapper
    return decorator


def injectable(scope: Optional[str] = None, interface: Optional[Type] = None):
    """
    Class decorator to mark a class as injectable and auto-register it.

    Args:
        scope: Service scope ('singleton', 'transient', 'scoped')
        interface: Interface to register this class under

    Example:
        @injectable(scope='singleton')
        class JsonParser:
            pass
    """
    def decorator(cls: Type[T]) -> Type[T]:
        container = get_container()

        # Determine interface
        registration_interface = interface or cls

        # Determine scope
        from .registry import ServiceScope
        scope_map = {
            'singleton': ServiceScope.SINGLETON,
            'transient': ServiceScope.TRANSIENT,
            'scoped': ServiceScope.SCOPED,
        }
        service_scope = scope_map.get(scope, ServiceScope.SINGLETON)

        # Auto-register the class
        container.register(registration_interface, cls, service_scope)

        return cls
    return decorator


def configuration_inject(config_path: str):
    """
    Decorator to inject configuration values into a method or function.

    Args:
        config_path: Dot-separated path to configuration value

    Example:
        @configuration_inject('security.max_file_size')
        def validate_file(self, max_size: int):
            # max_size will be injected from config
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from ..config import Config
            config = Config()

            # Parse config path
            keys = config_path.split('.')
            config_value = config.get(*keys)

            # Get parameter name from signature
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())

            # Skip 'self' parameter for methods
            if param_names and param_names[0] == 'self':
                param_names = param_names[1:]

            # Inject configuration value as first parameter
            if param_names and param_names[0] not in kwargs:
                kwargs[param_names[0]] = config_value

            return func(*args, **kwargs)
        return wrapper
    return decorator


class DependencyManager:
    """
    Context manager for scoped dependency management.

    This allows creating a scope where certain services can be overridden
    or where scoped services are isolated.
    """

    def __init__(self, overrides: Optional[Dict[Type, Any]] = None):
        """
        Initialize dependency manager.

        Args:
            overrides: Dictionary of interface -> instance overrides
        """
        self.overrides = overrides or {}
        self.original_container = None
        self.scoped_container = None

    def __enter__(self):
        """Enter the scoped context."""
        self.original_container = get_container()
        self.scoped_container = self.original_container.create_child_container()

        # Apply overrides
        for interface, instance in self.overrides.items():
            self.scoped_container.register_instance(interface, instance)

        # Set as current container
        from .container import set_container
        set_container(self.scoped_container)

        return self.scoped_container

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the scoped context."""
        if self.original_container:
            from .container import set_container
            set_container(self.original_container)


def with_dependencies(**dependency_overrides):
    """
    Context manager decorator for dependency overrides.

    Args:
        **dependency_overrides: Keyword arguments of interface=instance pairs

    Example:
        @with_dependencies(parser=MockJsonParser())
        def test_parsing():
            # test code here will use MockJsonParser
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with DependencyManager(dependency_overrides):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def lazy_inject(interface: Type[T]) -> Callable[[], T]:
    """
    Create a lazy-loaded dependency resolver.

    Args:
        interface: The interface type to resolve

    Returns:
        A function that resolves the dependency when called

    Example:
        get_parser = lazy_inject(JsonParser)
        # Later...
        parser = get_parser()  # Resolves at call time
    """
    def resolver() -> T:
        return get_container().resolve(interface)
    return resolver


def auto_wire(cls: Type[T]) -> Type[T]:
    """
    Class decorator that automatically injects dependencies into __init__.

    Args:
        cls: The class to auto-wire

    Returns:
        The modified class with dependency injection

    Example:
        @auto_wire
        class DataProcessor:
            def __init__(self, parser: JsonParser, validator: Validator):
                self.parser = parser
                self.validator = validator
    """
    original_init = cls.__init__

    @wraps(original_init)
    def new_init(self, *args, **kwargs):
        container = get_container()

        # Get constructor signature
        sig = inspect.signature(original_init)

        # Inject dependencies for parameters not provided
        for param_name, param in sig.parameters.items():
            if param_name in ('self',) or param_name in kwargs:
                continue

            if param.annotation != inspect.Parameter.empty:
                try:
                    if param_name not in kwargs:
                        kwargs[param_name] = container.resolve(param.annotation)
                except ServiceNotRegisteredError:
                    # Don't inject if service not registered
                    pass

        original_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls