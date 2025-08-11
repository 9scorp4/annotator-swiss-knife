"""
Tests for the dependency injection system.

This module tests the DI container, service registration, and resolution.
"""

import unittest

from annotation_toolkit.config import Config
from annotation_toolkit.core.conversation.visualizer import JsonVisualizer
from annotation_toolkit.core.text.dict_to_bullet import DictToBulletList
from annotation_toolkit.core.text.text_cleaner import TextCleaner
from annotation_toolkit.di import (
    DIContainer,
    ServiceScope,
    ConfigInterface,
    LoggerInterface,
    ServiceNotRegisteredError,
    CircularDependencyError,
)
from annotation_toolkit.di.bootstrap import (
    bootstrap_application,
    configure_services,
    get_tool_instances,
    validate_container_configuration,
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

    def test_validate_container_configuration(self):
        """Test container configuration validation."""
        # Create a properly configured container
        config = Config()
        container = bootstrap_application(config)
        
        # Should pass validation
        self.assertTrue(validate_container_configuration(container))

    def test_get_tool_instances(self):
        """Test getting tool instances from the container."""
        # Create a properly configured container
        config = Config()
        container = bootstrap_application(config)
        
        # Get tool instances
        tools = get_tool_instances(container)
        
        # Should have the expected tools
        self.assertIsInstance(tools, dict)
        self.assertIn("Dictionary to Bullet List", tools)
        self.assertIn("JSON Visualizer", tools)
        self.assertIn("Text Cleaner", tools)
        
        # Tools should be the correct types
        dict_tool = tools["Dictionary to Bullet List"]
        json_tool = tools["JSON Visualizer"]
        text_tool = tools["Text Cleaner"]
        
        self.assertIsInstance(dict_tool, DictToBulletList)
        self.assertIsInstance(json_tool, JsonVisualizer)
        self.assertIsInstance(text_tool, TextCleaner)

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


if __name__ == "__main__":
    unittest.main()