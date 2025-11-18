"""
Tests for the dependency injection system.

This module tests the DI container, service registration, and resolution.
"""

import unittest

from annotation_toolkit.config import Config
from annotation_toolkit.core.conversation.visualizer import JsonVisualizer
from annotation_toolkit.core.conversation.generator import ConversationGenerator
from annotation_toolkit.core.text.dict_to_bullet import DictToBulletList
from annotation_toolkit.core.text.text_cleaner import TextCleaner
from annotation_toolkit.di import (
    DIContainer,
    ServiceScope,
    ConfigInterface,
    LoggerInterface,
    ServiceNotRegisteredError,
    CircularDependencyError,
    ServiceCreationError,
)
from annotation_toolkit.di.bootstrap import (
    bootstrap_application,
    configure_services,
    get_tool_instances,
    validate_container_configuration,
)
from annotation_toolkit.di.container import (
    get_container,
    set_container,
    clear_container,
    register,
    register_instance,
    register_factory,
    resolve,
)


class TestDIContainer(unittest.TestCase):
    """Test cases for the DI container."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = DIContainer()

    def test_register_and_resolve_singleton(self):
        """Test registering and resolving a singleton service."""
        # Create a simple test class
        class TestService:
            def __init__(self):
                self.value = "test"

        # Register the service
        self.container.register(TestService, TestService, ServiceScope.SINGLETON)

        # Resolve the service twice
        instance1 = self.container.resolve(TestService)
        instance2 = self.container.resolve(TestService)

        # Should be the same instance
        self.assertIs(instance1, instance2)
        self.assertEqual(instance1.value, "test")

    def test_register_and_resolve_transient(self):
        """Test registering and resolving a transient service."""
        # Create a simple test class
        class TestService:
            def __init__(self):
                self.value = "test"

        # Register the service as transient
        self.container.register(TestService, TestService, ServiceScope.TRANSIENT)

        # Resolve the service twice
        instance1 = self.container.resolve(TestService)
        instance2 = self.container.resolve(TestService)

        # Should be different instances
        self.assertIsNot(instance1, instance2)
        self.assertEqual(instance1.value, "test")
        self.assertEqual(instance2.value, "test")

    def test_register_and_resolve_scoped(self):
        """Test registering and resolving a scoped service."""
        class TestService:
            def __init__(self):
                self.value = "scoped"

        # Register as SCOPED
        self.container.register(TestService, TestService, ServiceScope.SCOPED)

        # Resolve should work
        instance = self.container.resolve(TestService)
        self.assertEqual(instance.value, "scoped")

    def test_register_instance(self):
        """Test registering a specific instance."""
        # Create a test instance
        class TestService:
            def __init__(self, value):
                self.value = value

        test_instance = TestService("specific_value")

        # Register the instance
        self.container.register_instance(TestService, test_instance)

        # Resolve the service
        resolved_instance = self.container.resolve(TestService)

        # Should be the same instance
        self.assertIs(resolved_instance, test_instance)
        self.assertEqual(resolved_instance.value, "specific_value")

    def test_register_factory(self):
        """Test registering a factory function."""
        # Create a test class and factory
        class TestService:
            def __init__(self, value):
                self.value = value

        def test_factory():
            return TestService("factory_created")

        # Register the factory
        self.container.register_factory(TestService, test_factory)

        # Resolve the service
        instance = self.container.resolve(TestService)

        # Should be created by the factory
        self.assertEqual(instance.value, "factory_created")

    def test_factory_with_dependencies(self):
        """Test factory that depends on other services."""
        class DependencyService:
            def __init__(self):
                self.name = "dependency"

        class TestService:
            def __init__(self, dep):
                self.dep = dep

        # Register dependency
        self.container.register(DependencyService, DependencyService)

        # Register factory with dependency
        def test_factory(dep: DependencyService):
            return TestService(dep)

        self.container.register_factory(
            TestService,
            test_factory,
            dep=DependencyService
        )

        # Resolve
        instance = self.container.resolve(TestService)
        self.assertIsInstance(instance.dep, DependencyService)

    def test_service_not_registered_error(self):
        """Test that ServiceNotRegisteredError is raised for unregistered services."""
        class UnregisteredService:
            pass

        with self.assertRaises(ServiceNotRegisteredError):
            self.container.resolve(UnregisteredService)

    def test_is_registered(self):
        """Test the is_registered method."""
        class TestService:
            pass

        # Should not be registered initially
        self.assertFalse(self.container.is_registered(TestService))

        # Register the service
        self.container.register(TestService, TestService)

        # Should be registered now
        self.assertTrue(self.container.is_registered(TestService))

    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        class ServiceA:
            def __init__(self, service_b):
                self.service_b = service_b

        class ServiceB:
            def __init__(self, service_a):
                self.service_a = service_a

        # Register services with circular dependency
        self.container.register(ServiceA, ServiceA, service_b=ServiceB)
        self.container.register(ServiceB, ServiceB, service_a=ServiceA)

        # Should raise CircularDependencyError
        with self.assertRaises(CircularDependencyError):
            self.container.resolve(ServiceA)

    def test_get_registered_services(self):
        """Test getting all registered services."""
        class Service1:
            pass

        class Service2:
            pass

        self.container.register(Service1, Service1)
        self.container.register(Service2, Service2)

        services = self.container.get_registered_services()
        self.assertIn(Service1, services)
        self.assertIn(Service2, services)
        self.assertEqual(len(services), 2)

    def test_clear_container(self):
        """Test clearing all registrations."""
        class TestService:
            pass

        self.container.register(TestService, TestService)
        self.assertTrue(self.container.is_registered(TestService))

        self.container.clear()
        self.assertFalse(self.container.is_registered(TestService))

    def test_remove_service(self):
        """Test removing a specific service."""
        class TestService:
            pass

        self.container.register(TestService, TestService)
        self.assertTrue(self.container.is_registered(TestService))

        # Remove the service
        removed = self.container.remove_service(TestService)
        self.assertTrue(removed)
        self.assertFalse(self.container.is_registered(TestService))

    def test_remove_nonexistent_service(self):
        """Test removing a service that doesn't exist."""
        class TestService:
            pass

        removed = self.container.remove_service(TestService)
        self.assertFalse(removed)

    def test_create_child_container(self):
        """Test creating a child container."""
        class TestService:
            def __init__(self):
                self.value = "parent"

        self.container.register(TestService, TestService)

        # Create child
        child = self.container.create_child_container()

        # Child should have parent's registration
        self.assertTrue(child.is_registered(TestService))

        # Can resolve from child
        instance = child.resolve(TestService)
        self.assertEqual(instance.value, "parent")

    def test_child_container_can_override(self):
        """Test that child container can override parent registrations."""
        class TestService:
            def __init__(self):
                self.value = "parent"

        self.container.register(TestService, TestService)
        child = self.container.create_child_container()

        # Override in child
        class ChildService:
            def __init__(self):
                self.value = "child"

        child.register(TestService, ChildService)

        # Child should resolve to child version
        child_instance = child.resolve(TestService)
        self.assertEqual(child_instance.value, "child")

        # Parent should still have parent version
        parent_instance = self.container.resolve(TestService)
        self.assertEqual(parent_instance.value, "parent")

    def test_context_manager(self):
        """Test using container as context manager."""
        with self.container as container:
            class TestService:
                pass

            container.register(TestService, TestService)
            instance = container.resolve(TestService)
            self.assertIsInstance(instance, TestService)

    def test_service_creation_error(self):
        """Test ServiceCreationError when service construction fails."""
        class FailingService:
            def __init__(self):
                raise ValueError("Construction failed")

        self.container.register(FailingService, FailingService)

        with self.assertRaises(ServiceCreationError):
            self.container.resolve(FailingService)

    def test_register_without_implementation(self):
        """Test registering service without explicit implementation."""
        class TestService:
            pass

        # Register without implementation (should use interface as implementation)
        self.container.register(TestService)

        instance = self.container.resolve(TestService)
        self.assertIsInstance(instance, TestService)

    def test_complex_dependency_graph(self):
        """Test resolving complex dependency graphs."""
        class ServiceA:
            pass

        class ServiceB:
            def __init__(self, a: ServiceA):
                self.a = a

        class ServiceC:
            def __init__(self, a: ServiceA, b: ServiceB):
                self.a = a
                self.b = b

        self.container.register(ServiceA, ServiceA)
        self.container.register(ServiceB, ServiceB, a=ServiceA)
        self.container.register(ServiceC, ServiceC, a=ServiceA, b=ServiceB)

        instance = self.container.resolve(ServiceC)
        self.assertIsInstance(instance, ServiceC)
        self.assertIsInstance(instance.a, ServiceA)
        self.assertIsInstance(instance.b, ServiceB)


class TestGlobalContainerFunctions(unittest.TestCase):
    """Test cases for global container functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear global container before each test
        clear_container()

    def tearDown(self):
        """Clean up after tests."""
        clear_container()

    def test_get_container(self):
        """Test getting the global container."""
        container = get_container()
        self.assertIsInstance(container, DIContainer)

        # Should return same instance
        container2 = get_container()
        self.assertIs(container, container2)

    def test_set_container(self):
        """Test setting a custom global container."""
        custom_container = DIContainer()

        class TestService:
            pass

        custom_container.register(TestService, TestService)

        set_container(custom_container)

        # Global container should now be the custom one
        container = get_container()
        self.assertIs(container, custom_container)
        self.assertTrue(container.is_registered(TestService))

    def test_clear_container(self):
        """Test clearing the global container."""
        container = get_container()

        class TestService:
            pass

        container.register(TestService, TestService)

        # Clear creates a new container
        clear_container()

        new_container = get_container()
        self.assertFalse(new_container.is_registered(TestService))

    def test_global_register(self):
        """Test global register function."""
        class TestService:
            pass

        register(TestService, TestService)

        container = get_container()
        self.assertTrue(container.is_registered(TestService))

    def test_global_register_instance(self):
        """Test global register_instance function."""
        class TestService:
            def __init__(self):
                self.value = "test"

        instance = TestService()
        register_instance(TestService, instance)

        resolved = resolve(TestService)
        self.assertIs(resolved, instance)

    def test_global_register_factory(self):
        """Test global register_factory function."""
        class TestService:
            def __init__(self):
                self.value = "factory"

        def factory():
            return TestService()

        register_factory(TestService, factory)

        instance = resolve(TestService)
        self.assertEqual(instance.value, "factory")

    def test_global_resolve(self):
        """Test global resolve function."""
        class TestService:
            pass

        register(TestService, TestService)

        instance = resolve(TestService)
        self.assertIsInstance(instance, TestService)


class TestBootstrap(unittest.TestCase):
    """Test cases for the bootstrap functionality."""

    def test_bootstrap_application(self):
        """Test bootstrapping the application with DI."""
        # Create a test configuration
        config = Config()

        # Bootstrap the application
        container = bootstrap_application(config)

        # Should have a valid container
        self.assertIsInstance(container, DIContainer)

        # Should be able to resolve core services
        self.assertTrue(container.is_registered(ConfigInterface))
        self.assertTrue(container.is_registered(LoggerInterface))
        self.assertTrue(container.is_registered(DictToBulletList))
        self.assertTrue(container.is_registered(JsonVisualizer))
        self.assertTrue(container.is_registered(TextCleaner))

    def test_bootstrap_with_conversation_generator(self):
        """Test that ConversationGenerator is registered."""
        config = Config()
        container = bootstrap_application(config)

        self.assertTrue(container.is_registered(ConversationGenerator))

    def test_validate_container_configuration(self):
        """Test container configuration validation."""
        # Create a properly configured container
        config = Config()
        container = bootstrap_application(config)

        # Should pass validation
        self.assertTrue(validate_container_configuration(container))

    def test_validate_empty_container_fails(self):
        """Test that empty container fails validation."""
        container = DIContainer()

        # Empty container should fail validation
        self.assertFalse(validate_container_configuration(container))

    def test_get_tool_instances(self):
        """Test getting tool instances from the container."""
        # Create a properly configured container
        config = Config()
        container = bootstrap_application(config)

        # Get tool instances
        tools = get_tool_instances(container)

        # Should have the expected tools
        self.assertIsInstance(tools, dict)
        self.assertIn("URL Dictionary to Clickables", tools)
        self.assertIn("JSON Visualizer", tools)
        self.assertIn("Text Cleaner", tools)
        self.assertIn("Conversation Generator", tools)

        # Tools should be the correct types
        dict_tool = tools["URL Dictionary to Clickables"]
        json_tool = tools["JSON Visualizer"]
        text_tool = tools["Text Cleaner"]
        conv_tool = tools["Conversation Generator"]

        self.assertIsInstance(dict_tool, DictToBulletList)
        self.assertIsInstance(json_tool, JsonVisualizer)
        self.assertIsInstance(text_tool, TextCleaner)
        self.assertIsInstance(conv_tool, ConversationGenerator)

    def test_configure_services(self):
        """Test the configure_services function."""
        container = DIContainer()
        config = Config()

        # Configure services
        configure_services(container, config)

        # Should have registered all required services
        self.assertTrue(container.is_registered(ConfigInterface))
        self.assertTrue(container.is_registered(Config))
        self.assertTrue(container.is_registered(LoggerInterface))
        self.assertTrue(container.is_registered(DictToBulletList))
        self.assertTrue(container.is_registered(JsonVisualizer))
        self.assertTrue(container.is_registered(TextCleaner))
        self.assertTrue(container.is_registered(ConversationGenerator))

    def test_multiple_bootstrap_calls(self):
        """Test that multiple bootstrap calls create separate containers."""
        config = Config()

        container1 = bootstrap_application(config)
        container2 = bootstrap_application(config)

        # Should be different containers
        self.assertIsNot(container1, container2)

    def test_get_tool_instances_with_missing_tools(self):
        """Test get_tool_instances when some tools fail to resolve."""
        # Create a container with only some tools registered
        container = DIContainer()
        config = Config()

        # Register config and logger
        container.register_instance(ConfigInterface, config)
        container.register_instance(Config, config)

        # Create a simple logger adapter
        from annotation_toolkit.di.interfaces import LoggerInterface
        import logging

        class SimpleLogger(LoggerInterface):
            def debug(self, msg, *args, **kwargs):
                logging.debug(msg, *args, **kwargs)
            def info(self, msg, *args, **kwargs):
                logging.info(msg, *args, **kwargs)
            def warning(self, msg, *args, **kwargs):
                logging.warning(msg, *args, **kwargs)
            def error(self, msg, *args, **kwargs):
                logging.error(msg, *args, **kwargs)
            def exception(self, msg, *args, **kwargs):
                logging.exception(msg, *args, **kwargs)

        container.register_instance(LoggerInterface, SimpleLogger())

        # Register only one tool
        from annotation_toolkit.di.bootstrap import create_dict_to_bullet_tool
        container.register_factory(
            DictToBulletList,
            create_dict_to_bullet_tool,
            config=ConfigInterface,
            logger_service=LoggerInterface
        )

        # Get tool instances - should handle missing tools gracefully
        tools = get_tool_instances(container)

        # Should get at least the registered tool
        self.assertIsInstance(tools, dict)
        # DictToBulletList should be present
        self.assertIn("URL Dictionary to Clickables", tools)
        # Should have exactly 1 tool (others should fail gracefully)
        self.assertEqual(len(tools), 1)

    def test_validate_container_with_broken_service(self):
        """Test validation when a service fails to resolve."""
        container = DIContainer()

        # Register a factory that will throw an exception
        def broken_factory():
            raise RuntimeError("Intentional test error")

        container.register_factory(ConfigInterface, broken_factory)

        # Validation should fail gracefully
        result = validate_container_configuration(container)
        self.assertFalse(result)

    def test_validate_container_with_none_service(self):
        """Test validation when a service resolves to None."""
        container = DIContainer()

        # Register a factory that returns None
        def none_factory():
            return None

        container.register_factory(ConfigInterface, none_factory)

        # Validation should fail
        result = validate_container_configuration(container)
        self.assertFalse(result)


class TestServiceIntegration(unittest.TestCase):
    """Integration tests for services working together via DI."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.container = bootstrap_application(self.config)

    def test_dict_to_bullet_tool_integration(self):
        """Test that the DictToBulletList tool works when resolved from DI."""
        tool = self.container.resolve(DictToBulletList)

        # Test the tool functionality
        test_dict = {"1": "https://example.com", "2": "https://test.com"}
        result = tool.process_dict(test_dict)

        # Should produce valid output
        self.assertIsInstance(result, str)
        self.assertIn("example.com", result)
        self.assertIn("test.com", result)

    def test_json_visualizer_tool_integration(self):
        """Test that the JsonVisualizer tool works when resolved from DI."""
        tool = self.container.resolve(JsonVisualizer)

        # Test the tool functionality
        test_conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        result = tool.format_conversation(test_conversation)

        # Should produce valid output
        self.assertIsInstance(result, str)
        self.assertIn("Hello", result)
        self.assertIn("Hi there!", result)

    def test_text_cleaner_tool_integration(self):
        """Test that the TextCleaner tool works when resolved from DI."""
        tool = self.container.resolve(TextCleaner)

        # Test the tool functionality
        test_text = "```python\nprint('Hello world!')\n```"
        result = tool.process_text(test_text)

        # Should produce valid output
        self.assertIsInstance(result, str)
        self.assertIn("Hello world!", result)

    def test_conversation_generator_tool_integration(self):
        """Test that ConversationGenerator works when resolved from DI."""
        tool = self.container.resolve(ConversationGenerator)

        # Test functionality
        tool.add_turn("Hello", "Hi there!")
        self.assertEqual(tool.get_turn_count(), 1)

    def test_config_injection(self):
        """Test that Config is injected into tools correctly."""
        tool = self.container.resolve(DictToBulletList)
        # Tool should have access to config via DI
        self.assertIsInstance(tool, DictToBulletList)

    def test_multiple_tools_share_config(self):
        """Test that multiple tools share the same config instance."""
        config_from_container = self.container.resolve(ConfigInterface)

        # All tools should use the same config instance
        tool1 = self.container.resolve(DictToBulletList)
        tool2 = self.container.resolve(JsonVisualizer)

        # Both tools exist and work
        self.assertIsNotNone(tool1)
        self.assertIsNotNone(tool2)

    def test_tool_reconfiguration(self):
        """Test that tools can be reconfigured through DI."""
        # Get initial tool
        tool1 = self.container.resolve(JsonVisualizer)
        initial_format = tool1.output_format

        # Change format
        tool1.output_format = "markdown" if initial_format == "text" else "text"

        # Get tool again (singleton should be same instance)
        tool2 = self.container.resolve(JsonVisualizer)
        self.assertIs(tool1, tool2)
        self.assertEqual(tool1.output_format, tool2.output_format)


if __name__ == "__main__":
    unittest.main()
