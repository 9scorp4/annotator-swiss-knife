"""
Service bootstrap module for dependency injection.

This module provides functions to configure and bootstrap the DI container
with all the necessary services for the annotation toolkit.
"""

from typing import Optional

from ..config import Config
from ..core.conversation.generator import ConversationGenerator
from ..core.conversation.visualizer import JsonVisualizer
from ..core.text.dict_to_bullet import DictToBulletList
from ..core.text.text_cleaner import TextCleaner
from ..core.text.text_collector import TextCollector
from ..utils import logger
from .container import DIContainer, ServiceScope
from .exceptions import (
    DIException,
    ServiceNotRegisteredError,
    ServiceCreationError,
    CircularDependencyError,
)
from .interfaces import (
    AnnotationToolInterface,
    ConfigInterface,
    ConversationToolInterface,
    LoggerInterface,
    TextAnnotationToolInterface,
)


class LoggerAdapter:
    """
    Adapter class to make the existing logger compatible with LoggerInterface.

    This class wraps the existing logger module to provide the interface
    expected by the DI system. It includes safeguards to prevent duplicate logging.
    """

    def __init__(self):
        """Initialize the logger adapter with deduplication tracking."""
        self._initialized_components = set()

    def _should_log_initialization(self, component_name: str) -> bool:
        """
        Check if we should log the initialization of a component to prevent duplicates.

        Args:
            component_name: Name of the component being initialized

        Returns:
            True if we should log, False if it's a duplicate
        """
        if component_name in self._initialized_components:
            return False
        self._initialized_components.add(component_name)
        return True

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log a debug message."""
        logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log an info message."""
        logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log a warning message."""
        logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log an error message."""
        logger.error(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Log an exception message."""
        logger.exception(message, *args, **kwargs)


def create_dict_to_bullet_tool(
    config: ConfigInterface, logger_service: LoggerInterface
) -> DictToBulletList:
    """
    Factory function to create a DictToBulletList tool with dependencies.

    Args:
        config: The configuration service
        logger_service: The logger service

    Returns:
        A configured DictToBulletList instance
    """
    # Get configuration for the tool
    markdown_output = config.get(
        "tools", "dict_to_bullet", "markdown_output", default=True
    )

    logger_service.debug(
        f"Creating DictToBulletList with markdown_output={markdown_output}"
    )
    return DictToBulletList(markdown_output=markdown_output)


def create_json_visualizer_tool(
    config: ConfigInterface, logger_service: LoggerInterface
) -> JsonVisualizer:
    """
    Factory function to create a JsonVisualizer tool with dependencies.

    Args:
        config: The configuration service
        logger_service: The logger service

    Returns:
        A configured JsonVisualizer instance
    """
    # Get configuration for the tool
    output_format = config.get(
        "tools", "json_visualizer", "output_format", default="text"
    )
    user_message_color = config.get(
        "tools", "json_visualizer", "user_message_color", default="#00FFFF"
    )
    ai_message_color = config.get(
        "tools", "json_visualizer", "ai_message_color", default="#00FF7F"
    )

    logger_service.debug(
        f"Creating JsonVisualizer with format={output_format}, "
        f"user_color={user_message_color}, ai_color={ai_message_color}"
    )

    return JsonVisualizer(
        output_format=output_format,
        user_message_color=user_message_color,
        ai_message_color=ai_message_color,
    )


def create_text_cleaner_tool(
    config: ConfigInterface, logger_service: LoggerInterface
) -> TextCleaner:
    """
    Factory function to create a TextCleaner tool with dependencies.

    Args:
        config: The configuration service
        logger_service: The logger service

    Returns:
        A configured TextCleaner instance
    """
    logger_service.debug("Creating TextCleaner tool")
    return TextCleaner()


def create_conversation_generator_tool(
    config: ConfigInterface, logger_service: LoggerInterface
) -> ConversationGenerator:
    """
    Factory function to create a ConversationGenerator tool with dependencies.

    Args:
        config: The configuration service
        logger_service: The logger service

    Returns:
        A configured ConversationGenerator instance
    """
    # Get configuration for the tool
    max_turns = config.get(
        "tools", "conversation_generator", "max_turns", default=20
    )

    logger_service.debug(
        f"Creating ConversationGenerator with max_turns={max_turns}"
    )
    return ConversationGenerator(max_turns=max_turns)


def create_text_collector_tool(
    config: ConfigInterface, logger_service: LoggerInterface
) -> TextCollector:
    """
    Factory function to create a TextCollector tool with dependencies.

    Args:
        config: The configuration service
        logger_service: The logger service

    Returns:
        A configured TextCollector instance
    """
    # Get configuration for the tool
    max_fields = config.get(
        "tools", "text_collector", "max_fields", default=20
    )
    filter_empty = config.get(
        "tools", "text_collector", "filter_empty", default=True
    )

    logger_service.debug(
        f"Creating TextCollector with max_fields={max_fields}, filter_empty={filter_empty}"
    )
    return TextCollector(max_fields=max_fields, filter_empty=filter_empty)



def configure_services(container: DIContainer, config: Optional[Config] = None) -> None:
    """
    Configure all services in the DI container.

    This function registers all the core services of the annotation toolkit
    with their appropriate interfaces and dependencies.

    Args:
        container: The DI container to configure
        config: Optional configuration instance to use
    """
    # Register configuration service
    if config is None:
        config = Config()

    container.register_instance(ConfigInterface, config)
    container.register_instance(Config, config)  # Also register concrete type

    # Register logger service
    logger_adapter = LoggerAdapter()
    container.register_instance(LoggerInterface, logger_adapter)

    # Register annotation tools using factory functions
    container.register_factory(
        interface=DictToBulletList,
        factory=create_dict_to_bullet_tool,
        scope=ServiceScope.SINGLETON,
        config=ConfigInterface,
        logger_service=LoggerInterface,
    )

    container.register_factory(
        interface=JsonVisualizer,
        factory=create_json_visualizer_tool,
        scope=ServiceScope.SINGLETON,
        config=ConfigInterface,
        logger_service=LoggerInterface,
    )

    container.register_factory(
        interface=TextCleaner,
        factory=create_text_cleaner_tool,
        scope=ServiceScope.SINGLETON,
        config=ConfigInterface,
        logger_service=LoggerInterface,
    )

    container.register_factory(
        interface=ConversationGenerator,
        factory=create_conversation_generator_tool,
        scope=ServiceScope.SINGLETON,
        config=ConfigInterface,
        logger_service=LoggerInterface,
    )

    container.register_factory(
        interface=TextCollector,
        factory=create_text_collector_tool,
        scope=ServiceScope.SINGLETON,
        config=ConfigInterface,
        logger_service=LoggerInterface,
    )


def bootstrap_application(config: Optional[Config] = None) -> DIContainer:
    """
    Bootstrap the entire application with dependency injection.

    This function creates and configures a DI container with all the
    necessary services for the annotation toolkit application.

    Args:
        config: Optional configuration instance to use

    Returns:
        A fully configured DI container
    """
    container = DIContainer()
    configure_services(container, config)

    # Log the configured services
    registered_services = container.get_registered_services()
    logger.info(f"DI container bootstrapped with {len(registered_services)} services:")
    for service in registered_services:
        logger.debug(f"  - {service.__name__}")

    return container


class LazyToolRegistry:
    """
    Lazy-loading registry for annotation tools.

    Tools are only resolved from the DI container when first accessed,
    reducing startup time by avoiding unnecessary instantiation.
    """

    # Mapping of tool classes to their name attribute
    TOOL_CLASSES = [
        DictToBulletList,
        JsonVisualizer,
        TextCleaner,
        ConversationGenerator,
        TextCollector,
    ]

    # DI exceptions that indicate expected resolution failures
    _DI_EXCEPTIONS = (ServiceNotRegisteredError, ServiceCreationError, CircularDependencyError)

    def __init__(self, container: DIContainer):
        """
        Initialize the lazy tool registry.

        Args:
            container: The configured DI container
        """
        self._container = container
        self._resolved_tools: dict = {}
        self._failed_tools: set = set()

    def get_tool(self, tool_class: type):
        """
        Get a tool instance by its class type.

        Resolves the tool from the container on first access and caches it.

        Args:
            tool_class: The tool class to resolve

        Returns:
            The tool instance, or None if resolution failed
        """
        # Return cached tool if already resolved
        if tool_class in self._resolved_tools:
            return self._resolved_tools[tool_class]

        # Don't retry previously failed resolutions
        if tool_class in self._failed_tools:
            return None

        # Resolve tool lazily
        try:
            tool = self._container.resolve(tool_class)
            self._resolved_tools[tool_class] = tool
            logger.debug(f"Lazily resolved tool: {tool_class.__name__}")
            return tool
        except self._DI_EXCEPTIONS as e:
            self._failed_tools.add(tool_class)
            logger.warning(f"Failed to resolve {tool_class.__name__}: {e}")
            return None

    def get_tool_by_name(self, name: str):
        """
        Get a tool instance by its name.

        Args:
            name: The tool's name attribute

        Returns:
            The tool instance, or None if not found
        """
        for tool_class in self.TOOL_CLASSES:
            tool = self.get_tool(tool_class)
            if tool and tool.name == name:
                return tool
        return None

    def get_all_tools(self) -> dict:
        """
        Get all tool instances (resolves all tools).

        Returns:
            Dictionary mapping tool names to tool instances
        """
        tools = {}
        for tool_class in self.TOOL_CLASSES:
            tool = self.get_tool(tool_class)
            if tool:
                tools[tool.name] = tool
        return tools

    def get_available_tool_names(self) -> list:
        """
        Get names of all available tools (resolves all tools).

        Returns:
            List of tool names
        """
        return list(self.get_all_tools().keys())


def get_tool_instances(container: DIContainer) -> dict:
    """
    Get instances of all annotation tools from the container.

    This is a convenience function that resolves all the annotation tools
    and returns them in a dictionary format compatible with the existing
    application structure.

    Note: For better performance with lazy loading, consider using
    LazyToolRegistry directly.

    Args:
        container: The configured DI container

    Returns:
        Dictionary mapping tool names to tool instances
    """
    registry = LazyToolRegistry(container)
    tools = registry.get_all_tools()
    logger.info(f"Retrieved {len(tools)} tool instances from DI container")
    return tools


def validate_container_configuration(container: DIContainer) -> bool:
    """
    Validate that the DI container is properly configured.

    This function checks that all expected services can be resolved
    and returns True if the configuration is valid.

    Args:
        container: The DI container to validate

    Returns:
        True if the container is properly configured, False otherwise
    """
    required_services = [
        ConfigInterface,
        LoggerInterface,
        DictToBulletList,
        JsonVisualizer,
        TextCleaner,
        ConversationGenerator,
        TextCollector,
    ]

    for service in required_services:
        if not container.is_registered(service):
            logger.error(f"Required service not registered: {service.__name__}")
            return False

        try:
            instance = container.resolve(service)
            if instance is None:
                logger.error(f"Service resolved to None: {service.__name__}")
                return False
        except DIException as e:
            # Catch all DI-related exceptions (registration, creation, circular deps)
            logger.error(f"Failed to resolve service {service.__name__}: {e}")
            return False

    logger.info("DI container configuration validation passed")
    return True
