"""
Interfaces for the dependency injection system.

This module defines the contracts that services must implement
to be managed by the DI container.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, Type, TypeVar

T = TypeVar("T")


class DIContainerInterface(Protocol):
    """
    Interface for dependency injection containers.
    
    This protocol defines the contract that all DI containers must implement.
    """

    def register(
        self,
        interface: Type[T],
        implementation: Type[T],
        scope: "ServiceScope" = None,
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
        ...

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register a specific instance for an interface.
        
        Args:
            interface: The interface/protocol type
            instance: The instance to register
        """
        ...

    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a service instance for the given interface.
        
        Args:
            interface: The interface/protocol type to resolve
            
        Returns:
            An instance of the service
            
        Raises:
            ServiceNotRegisteredError: If the service is not registered
        """
        ...

    def is_registered(self, interface: Type[T]) -> bool:
        """
        Check if a service is registered for the given interface.
        
        Args:
            interface: The interface/protocol type
            
        Returns:
            True if the service is registered, False otherwise
        """
        ...


class ConfigInterface(Protocol):
    """
    Interface for configuration services.
    
    This protocol defines the contract for configuration management.
    """

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value using a key path.
        
        Args:
            *keys: The key path (e.g., 'tools', 'dict_to_bullet', 'enabled')
            default: Default value if key is not found
            
        Returns:
            The configuration value
        """
        ...

    def set(self, value: Any, *keys: str) -> None:
        """
        Set a configuration value using a key path.
        
        Args:
            value: The value to set
            *keys: The key path
        """
        ...

    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
        """
        ...


class AnnotationToolInterface(Protocol):
    """
    Interface for annotation tools.
    
    This protocol defines the contract that all annotation tools must implement.
    """

    @property
    def name(self) -> str:
        """Get the name of the tool."""
        ...

    @property
    def description(self) -> str:
        """Get the description of the tool."""
        ...

    def process_text(self, text: str) -> str:
        """
        Process text input and return the result.
        
        Args:
            text: The input text to process
            
        Returns:
            The processed text
        """
        ...


class TextAnnotationToolInterface(AnnotationToolInterface, Protocol):
    """
    Interface specifically for text annotation tools.
    
    This extends the base annotation tool interface with text-specific methods.
    """

    def validate_input(self, text: str) -> bool:
        """
        Validate that the input text is suitable for this tool.
        
        Args:
            text: The input text to validate
            
        Returns:
            True if the input is valid, False otherwise
        """
        ...


class ConversationToolInterface(AnnotationToolInterface, Protocol):
    """
    Interface for conversation/JSON visualization tools.
    
    This extends the base annotation tool interface with conversation-specific methods.
    """

    def format_conversation(self, conversation: list) -> str:
        """
        Format a conversation for display.
        
        Args:
            conversation: List of conversation messages
            
        Returns:
            Formatted conversation string
        """
        ...

    def search_conversation(self, conversation: list, query: str, case_sensitive: bool = False) -> list:
        """
        Search for text within a conversation.
        
        Args:
            conversation: List of conversation messages
            query: Search query
            case_sensitive: Whether to perform case-sensitive search
            
        Returns:
            List of matching results
        """
        ...


class UIWidgetInterface(Protocol):
    """
    Interface for UI widgets that use annotation tools.
    
    This protocol defines the contract for UI components that interact with annotation tools.
    """

    def set_tool(self, tool: AnnotationToolInterface) -> None:
        """
        Set the annotation tool for this widget.
        
        Args:
            tool: The annotation tool to use
        """
        ...

    def get_tool(self) -> Optional[AnnotationToolInterface]:
        """
        Get the current annotation tool.
        
        Returns:
            The current annotation tool, or None if not set
        """
        ...


class LoggerInterface(Protocol):
    """
    Interface for logging services.
    
    This protocol defines the contract for logging functionality.
    """

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        ...

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        ...

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        ...

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        ...

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an exception message."""
        ...