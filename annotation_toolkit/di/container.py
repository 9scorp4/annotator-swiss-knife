"""
Dependency Injection Container implementation.

This module provides the main DI container that manages service resolution,
lifecycle, and dependency injection.
"""

from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar

from .exceptions import (
    CircularDependencyError,
    ServiceCreationError,
    ServiceNotRegisteredError,
)
from .interfaces import DIContainerInterface
from .registry import ServiceRegistry, ServiceScope

T = TypeVar("T")


class DIContainer:
    """
    Dependency injection container.
    
    This is the main container that manages service registrations and provides
    dependency resolution with circular dependency detection.
    """

    def __init__(self):
        """Initialize the DI container."""
        self._registry = ServiceRegistry()
        self._resolution_stack: List[Type] = []

    def register(
        self,
        interface: Type[T],
        implementation: Optional[Type[T]] = None,
        scope: ServiceScope = ServiceScope.SINGLETON,
        **kwargs: Any
    ) -> None:
        """
        Register a service implementation for an interface.
        
        Args:
            interface: The interface/protocol type
            implementation: The concrete implementation type
            scope: The service lifecycle scope
            **kwargs: Additional configuration parameters
        """
        if implementation is None:
            implementation = interface
            
        self._registry.register(
            interface=interface,
            implementation=implementation,
            scope=scope,
            **kwargs
        )

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register a specific instance for an interface.
        
        Args:
            interface: The interface/protocol type
            instance: The instance to register
        """
        self._registry.register(
            interface=interface,
            instance=instance,
            scope=ServiceScope.SINGLETON
        )

    def register_factory(
        self,
        interface: Type[T],
        factory: Callable[..., T],
        scope: ServiceScope = ServiceScope.SINGLETON,
        **kwargs: Any
    ) -> None:
        """
        Register a factory function for an interface.
        
        Args:
            interface: The interface/protocol type
            factory: Factory function to create instances
            scope: The service lifecycle scope
            **kwargs: Additional arguments to pass to the factory
        """
        self._registry.register(
            interface=interface,
            factory=factory,
            scope=scope,
            **kwargs
        )

    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a service instance for the given interface.
        
        Args:
            interface: The interface/protocol type to resolve
            
        Returns:
            An instance of the service
            
        Raises:
            ServiceNotRegisteredError: If the service is not registered
            CircularDependencyError: If a circular dependency is detected
            ServiceCreationError: If the service cannot be created
        """
        # Check for circular dependencies
        if interface in self._resolution_stack:
            cycle_start = self._resolution_stack.index(interface)
            cycle = self._resolution_stack[cycle_start:] + [interface]
            raise CircularDependencyError(cycle)

        # Check if service is registered
        registration = self._registry.get_registration(interface)
        if registration is None:
            raise ServiceNotRegisteredError(interface)

        # Add to resolution stack for circular dependency detection
        self._resolution_stack.append(interface)
        
        try:
            # Create the instance
            instance = registration.create_instance(self)
            return instance
        except Exception as e:
            if isinstance(e, (ServiceNotRegisteredError, CircularDependencyError)):
                raise
            raise ServiceCreationError(interface, e)
        finally:
            # Remove from resolution stack
            if self._resolution_stack and self._resolution_stack[-1] == interface:
                self._resolution_stack.pop()

    def is_registered(self, interface: Type[T]) -> bool:
        """
        Check if a service is registered for the given interface.
        
        Args:
            interface: The interface/protocol type
            
        Returns:
            True if the service is registered, False otherwise
        """
        return self._registry.is_registered(interface)

    def get_registered_services(self) -> List[Type]:
        """
        Get a list of all registered service interfaces.
        
        Returns:
            List of registered interface types
        """
        return list(self._registry.get_all_registrations().keys())

    def clear(self) -> None:
        """Clear all service registrations."""
        self._registry.clear()

    def remove_service(self, interface: Type[T]) -> bool:
        """
        Remove a service registration.
        
        Args:
            interface: The interface/protocol type to remove
            
        Returns:
            True if the service was removed, False if it wasn't registered
        """
        return self._registry.remove(interface)

    def create_child_container(self) -> "DIContainer":
        """
        Create a child container that inherits registrations from this container.
        
        This is useful for creating scoped containers that can override
        certain services while inheriting others.
        
        Returns:
            A new child container
        """
        child = DIContainer()
        
        # Copy all registrations to the child container
        for interface, registration in self._registry.get_all_registrations().items():
            child._registry.register(
                interface=registration.interface,
                implementation=registration.implementation,
                instance=registration.instance,
                factory=registration.factory,
                scope=registration.scope,
                **registration.constructor_args
            )
        
        return child

    def __enter__(self) -> "DIContainer":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - clear resolution stack."""
        self._resolution_stack.clear()


# Global default container instance
_default_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """
    Get the global default DI container.
    
    This function provides access to a global singleton DI container
    that can be used throughout the application.
    
    Returns:
        The global DI container instance
    """
    global _default_container
    if _default_container is None:
        _default_container = DIContainer()
    return _default_container


def set_container(container: DIContainer) -> None:
    """
    Set the global default DI container.
    
    This function allows replacing the global DI container, which is
    useful for testing or when you need a custom configured container.
    
    Args:
        container: The DI container to set as the global default
    """
    global _default_container
    _default_container = container


def clear_container() -> None:
    """
    Clear and reset the global default DI container.
    
    This function creates a new empty DI container and sets it as
    the global default, effectively clearing all registrations.
    """
    global _default_container
    _default_container = DIContainer()


# Convenience functions for common operations
def register(
    interface: Type[T],
    implementation: Optional[Type[T]] = None,
    scope: ServiceScope = ServiceScope.SINGLETON,
    **kwargs: Any
) -> None:
    """
    Register a service in the global container.
    
    Args:
        interface: The interface/protocol type
        implementation: The concrete implementation type
        scope: The service lifecycle scope
        **kwargs: Additional configuration parameters
    """
    get_container().register(interface, implementation, scope, **kwargs)


def register_instance(interface: Type[T], instance: T) -> None:
    """
    Register an instance in the global container.
    
    Args:
        interface: The interface/protocol type
        instance: The instance to register
    """
    get_container().register_instance(interface, instance)


def register_factory(
    interface: Type[T],
    factory: Callable[..., T],
    scope: ServiceScope = ServiceScope.SINGLETON,
    **kwargs: Any
) -> None:
    """
    Register a factory in the global container.
    
    Args:
        interface: The interface/protocol type
        factory: Factory function to create instances
        scope: The service lifecycle scope
        **kwargs: Additional arguments to pass to the factory
    """
    get_container().register_factory(interface, factory, scope, **kwargs)


def resolve(interface: Type[T]) -> T:
    """
    Resolve a service from the global container.
    
    Args:
        interface: The interface/protocol type to resolve
        
    Returns:
        An instance of the service
    """
    return get_container().resolve(interface)