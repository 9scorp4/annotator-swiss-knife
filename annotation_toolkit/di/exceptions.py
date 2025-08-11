"""
Exceptions for the dependency injection system.

This module defines custom exceptions that can be raised by the DI container.
"""


class DIException(Exception):
    """
    Base exception for dependency injection related errors.
    
    All DI-specific exceptions inherit from this base class.
    """
    pass


class ServiceNotRegisteredError(DIException):
    """
    Exception raised when trying to resolve a service that is not registered.
    
    This exception is raised when the DI container cannot find a registration
    for the requested service interface.
    """
    
    def __init__(self, interface_type: type, message: str = None):
        """
        Initialize the exception.
        
        Args:
            interface_type: The interface type that was not found
            message: Optional custom error message
        """
        if message is None:
            message = f"Service not registered for interface: {interface_type.__name__}"
        
        super().__init__(message)
        self.interface_type = interface_type


class CircularDependencyError(DIException):
    """
    Exception raised when a circular dependency is detected.
    
    This exception is raised when the DI container detects that resolving
    a service would create a circular dependency chain.
    """
    
    def __init__(self, dependency_chain: list, message: str = None):
        """
        Initialize the exception.
        
        Args:
            dependency_chain: The chain of dependencies that forms the cycle
            message: Optional custom error message
        """
        if message is None:
            chain_names = [dep.__name__ for dep in dependency_chain]
            message = f"Circular dependency detected: {' -> '.join(chain_names)}"
        
        super().__init__(message)
        self.dependency_chain = dependency_chain


class ServiceCreationError(DIException):
    """
    Exception raised when a service cannot be created.
    
    This exception is raised when the DI container encounters an error
    while trying to create an instance of a service.
    """
    
    def __init__(self, interface_type: type, original_exception: Exception = None, message: str = None):
        """
        Initialize the exception.
        
        Args:
            interface_type: The interface type that could not be created
            original_exception: The original exception that caused the creation to fail
            message: Optional custom error message
        """
        if message is None:
            message = f"Failed to create service for interface: {interface_type.__name__}"
            if original_exception:
                message += f" - {str(original_exception)}"
        
        super().__init__(message)
        self.interface_type = interface_type
        self.original_exception = original_exception


class InvalidServiceRegistrationError(DIException):
    """
    Exception raised when a service registration is invalid.
    
    This exception is raised when trying to register a service with
    invalid or incomplete registration information.
    """
    
    def __init__(self, interface_type: type, message: str = None):
        """
        Initialize the exception.
        
        Args:
            interface_type: The interface type with invalid registration
            message: Optional custom error message
        """
        if message is None:
            message = f"Invalid service registration for interface: {interface_type.__name__}"
        
        super().__init__(message)
        self.interface_type = interface_type