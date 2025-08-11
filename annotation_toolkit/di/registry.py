"""
Service registry for the dependency injection system.

This module manages service registrations, lifecycle, and scopes.
"""

from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class ServiceScope(Enum):
    """
    Enumeration of service lifecycle scopes.
    
    - SINGLETON: One instance per container (default)
    - TRANSIENT: New instance every time
    - SCOPED: One instance per scope (for future use with request scoping)
    """
    
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class ServiceRegistration:
    """
    Represents a service registration in the DI container.
    
    This class holds all the information needed to create and manage
    a service instance, including its implementation type, lifecycle scope,
    and any factory functions or constructor arguments.
    """

    def __init__(
        self,
        interface: Type[T],
        implementation: Optional[Type[T]] = None,
        instance: Optional[T] = None,
        factory: Optional[Callable[..., T]] = None,
        scope: ServiceScope = ServiceScope.SINGLETON,
        **kwargs: Any
    ):
        """
        Initialize a service registration.
        
        Args:
            interface: The interface/protocol type
            implementation: The concrete implementation type (optional if instance or factory provided)
            instance: A pre-created instance (for singleton registration)
            factory: A factory function to create instances
            scope: The service lifecycle scope
            **kwargs: Additional arguments to pass to the constructor or factory
        """
        self.interface = interface
        self.implementation = implementation
        self.instance = instance
        self.factory = factory
        self.scope = scope
        self.constructor_args = kwargs
        self._singleton_instance: Optional[T] = None

    def create_instance(self, container: "DIContainerInterface") -> T:
        """
        Create a new instance of the service.
        
        Args:
            container: The DI container for resolving dependencies
            
        Returns:
            A new instance of the service
            
        Raises:
            ValueError: If the registration is incomplete
        """
        # If we have a pre-created instance, return it
        if self.instance is not None:
            return self.instance

        # For singleton scope, return cached instance if available
        if self.scope == ServiceScope.SINGLETON and self._singleton_instance is not None:
            return self._singleton_instance

        # Create new instance
        instance = None
        
        if self.factory is not None:
            # Use factory function
            instance = self._create_from_factory(container)
        elif self.implementation is not None:
            # Use implementation class
            instance = self._create_from_implementation(container)
        else:
            raise ValueError(f"Invalid service registration for {self.interface}: no implementation, instance, or factory provided")

        # Cache singleton instances
        if self.scope == ServiceScope.SINGLETON:
            self._singleton_instance = instance

        return instance

    def _create_from_factory(self, container: "DIContainerInterface") -> T:
        """
        Create an instance using the factory function.
        
        Args:
            container: The DI container for resolving dependencies
            
        Returns:
            A new instance created by the factory
        """
        # Resolve constructor arguments that are registered services
        resolved_args = self._resolve_constructor_args(container)
        return self.factory(**resolved_args)

    def _create_from_implementation(self, container: "DIContainerInterface") -> T:
        """
        Create an instance using the implementation class.
        
        Args:
            container: The DI container for resolving dependencies
            
        Returns:
            A new instance of the implementation class
        """
        # Resolve constructor arguments that are registered services
        resolved_args = self._resolve_constructor_args(container)
        return self.implementation(**resolved_args)

    def _resolve_constructor_args(self, container: "DIContainerInterface") -> Dict[str, Any]:
        """
        Resolve constructor arguments by injecting registered services.
        
        Args:
            container: The DI container for resolving dependencies
            
        Returns:
            Dictionary of resolved constructor arguments
        """
        resolved_args = {}
        
        for arg_name, arg_value in self.constructor_args.items():
            if isinstance(arg_value, type) and container.is_registered(arg_value):
                # If the argument is a registered service type, resolve it
                resolved_args[arg_name] = container.resolve(arg_value)
            else:
                # Otherwise, use the value as-is
                resolved_args[arg_name] = arg_value
                
        return resolved_args


class ServiceRegistry:
    """
    Registry that manages service registrations.
    
    This class provides a centralized way to manage all service registrations
    and their associated metadata.
    """

    def __init__(self):
        """Initialize the service registry."""
        self._registrations: Dict[Type, ServiceRegistration] = {}

    def register(
        self,
        interface: Type[T],
        implementation: Optional[Type[T]] = None,
        instance: Optional[T] = None,
        factory: Optional[Callable[..., T]] = None,
        scope: ServiceScope = ServiceScope.SINGLETON,
        **kwargs: Any
    ) -> None:
        """
        Register a service in the registry.
        
        Args:
            interface: The interface/protocol type
            implementation: The concrete implementation type
            instance: A pre-created instance
            factory: A factory function to create instances
            scope: The service lifecycle scope
            **kwargs: Additional constructor arguments
        """
        registration = ServiceRegistration(
            interface=interface,
            implementation=implementation,
            instance=instance,
            factory=factory,
            scope=scope,
            **kwargs
        )
        
        self._registrations[interface] = registration

    def get_registration(self, interface: Type[T]) -> Optional[ServiceRegistration]:
        """
        Get the service registration for an interface.
        
        Args:
            interface: The interface/protocol type
            
        Returns:
            The service registration, or None if not found
        """
        return self._registrations.get(interface)

    def is_registered(self, interface: Type[T]) -> bool:
        """
        Check if a service is registered.
        
        Args:
            interface: The interface/protocol type
            
        Returns:
            True if the service is registered, False otherwise
        """
        return interface in self._registrations

    def get_all_registrations(self) -> Dict[Type, ServiceRegistration]:
        """
        Get all service registrations.
        
        Returns:
            Dictionary of all service registrations
        """
        return self._registrations.copy()

    def clear(self) -> None:
        """Clear all service registrations."""
        self._registrations.clear()

    def remove(self, interface: Type[T]) -> bool:
        """
        Remove a service registration.
        
        Args:
            interface: The interface/protocol type to remove
            
        Returns:
            True if the service was removed, False if it wasn't registered
        """
        if interface in self._registrations:
            del self._registrations[interface]
            return True
        return False