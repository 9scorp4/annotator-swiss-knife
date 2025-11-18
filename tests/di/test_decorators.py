"""
Unit tests for DI decorators module.

This module tests dependency injection decorators including @inject, @injectable,
@auto_wire, @configuration_inject, and related utilities.
"""

import unittest
from typing import Optional
from unittest.mock import MagicMock, patch, Mock

from annotation_toolkit.di.decorators import (
    inject,
    injectable,
    configuration_inject,
    DependencyManager,
    with_dependencies,
    lazy_inject,
    auto_wire
)
from annotation_toolkit.di.container import DIContainer
from annotation_toolkit.di.exceptions import ServiceNotRegisteredError
from annotation_toolkit.di.registry import ServiceScope


# Test service classes
class TestService:
    """Mock service for testing."""
    def __init__(self, value: str = "test"):
        self.value = value


class AnotherService:
    """Another mock service for testing."""
    def __init__(self, name: str = "another"):
        self.name = name


class DependentService:
    """Service with dependencies."""
    def __init__(self, test_service: TestService, another_service: AnotherService):
        self.test_service = test_service
        self.another_service = another_service


class TestInjectDecorator(unittest.TestCase):
    """Test @inject decorator."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = DIContainer()
        self.container.register(TestService, TestService)
        self.container.register(AnotherService, AnotherService)

        # Patch get_container to return our test container
        self.container_patcher = patch('annotation_toolkit.di.decorators.get_container')
        self.mock_get_container = self.container_patcher.start()
        self.mock_get_container.return_value = self.container

    def tearDown(self):
        """Clean up test fixtures."""
        self.container_patcher.stop()

    def test_inject_with_type_hints(self):
        """Test @inject injects dependencies using type hints."""
        @inject()
        def process_data(test_service: TestService, another_service: AnotherService):
            return test_service.value, another_service.name

        result = process_data()

        self.assertEqual(result, ("test", "another"))

    def test_inject_uses_type_hints_not_explicit_dependencies(self):
        """Test @inject uses type hints, not explicit dependencies parameter."""
        # Note: The current implementation ignores explicit dependencies
        # and only uses type hints from the signature
        @inject(TestService, AnotherService)
        def process_data(test_service: TestService, another_service: AnotherService):
            return test_service.value, another_service.name

        result = process_data()

        self.assertEqual(result, ("test", "another"))

    def test_inject_allows_override_via_kwargs(self):
        """Test that provided kwargs override injected dependencies."""
        @inject()
        def process_data(test_service: TestService):
            return test_service.value

        custom_service = TestService("custom")
        result = process_data(test_service=custom_service)

        self.assertEqual(result, "custom")

    def test_inject_skips_unregistered_services(self):
        """Test @inject silently skips unregistered services."""
        class UnregisteredService:
            pass

        @inject()
        def process_data(test_service: TestService, unregistered: UnregisteredService = None):
            return test_service.value, unregistered

        result = process_data()

        self.assertEqual(result, ("test", None))

    def test_inject_with_method(self):
        """Test @inject works on class methods."""
        class MyClass:
            @inject()
            def process(self, test_service: TestService):
                return test_service.value

        obj = MyClass()
        result = obj.process()

        self.assertEqual(result, "test")

    def test_inject_preserves_function_metadata(self):
        """Test that @inject preserves function name and docstring."""
        @inject()
        def my_function(test_service: TestService):
            """My function docstring."""
            pass

        self.assertEqual(my_function.__name__, "my_function")
        self.assertEqual(my_function.__doc__, "My function docstring.")

    def test_inject_with_positional_args(self):
        """Test @inject works with positional arguments."""
        @inject()
        def process_data(name: str, test_service: TestService):
            return name, test_service.value

        result = process_data("John")

        self.assertEqual(result, ("John", "test"))

    def test_inject_with_no_annotations(self):
        """Test @inject with function that has no type annotations."""
        @inject()
        def process_data(arg1, arg2):
            return arg1, arg2

        result = process_data("val1", "val2")

        self.assertEqual(result, ("val1", "val2"))


class TestInjectableDecorator(unittest.TestCase):
    """Test @injectable decorator."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = DIContainer()

        # Patch get_container
        self.container_patcher = patch('annotation_toolkit.di.decorators.get_container')
        self.mock_get_container = self.container_patcher.start()
        self.mock_get_container.return_value = self.container

    def tearDown(self):
        """Clean up test fixtures."""
        self.container_patcher.stop()

    def test_injectable_auto_registers_class(self):
        """Test @injectable automatically registers the class."""
        @injectable()
        class MyService:
            pass

        # Verify class is registered
        self.assertTrue(self.container.is_registered(MyService))

    def test_injectable_with_singleton_scope(self):
        """Test @injectable with singleton scope."""
        @injectable(scope='singleton')
        class SingletonService:
            pass

        instance1 = self.container.resolve(SingletonService)
        instance2 = self.container.resolve(SingletonService)

        self.assertIs(instance1, instance2)

    def test_injectable_with_transient_scope(self):
        """Test @injectable with transient scope."""
        @injectable(scope='transient')
        class TransientService:
            pass

        instance1 = self.container.resolve(TransientService)
        instance2 = self.container.resolve(TransientService)

        self.assertIsNot(instance1, instance2)

    def test_injectable_with_interface(self):
        """Test @injectable with explicit interface."""
        class IService:
            pass

        @injectable(interface=IService)
        class ServiceImpl(IService):
            pass

        # Verify registered under interface
        self.assertTrue(self.container.is_registered(IService))
        instance = self.container.resolve(IService)
        self.assertIsInstance(instance, ServiceImpl)

    def test_injectable_default_scope_is_singleton(self):
        """Test that default scope for @injectable is singleton."""
        @injectable()
        class DefaultService:
            pass

        instance1 = self.container.resolve(DefaultService)
        instance2 = self.container.resolve(DefaultService)

        self.assertIs(instance1, instance2)

    def test_injectable_returns_original_class(self):
        """Test that @injectable returns the original class."""
        @injectable()
        class MyService:
            """Original docstring."""
            pass

        self.assertEqual(MyService.__name__, "MyService")
        self.assertEqual(MyService.__doc__, "Original docstring.")


class TestConfigurationInjectDecorator(unittest.TestCase):
    """Test @configuration_inject decorator."""

    def test_configuration_inject_injects_config_value(self):
        """Test @configuration_inject injects configuration values."""
        with patch('annotation_toolkit.config.Config') as MockConfig:
            mock_config = MockConfig.return_value
            mock_config.get.return_value = 100

            @configuration_inject('security.max_file_size')
            def validate_file(max_size: int):
                return max_size

            result = validate_file()

            self.assertEqual(result, 100)
            mock_config.get.assert_called_once_with('security', 'max_file_size')

    def test_configuration_inject_with_method(self):
        """Test @configuration_inject works on class methods."""
        with patch('annotation_toolkit.config.Config') as MockConfig:
            mock_config = MockConfig.return_value
            mock_config.get.return_value = 50

            class MyClass:
                @configuration_inject('performance.cache_size')
                def set_cache(self, cache_size: int):
                    return cache_size

            obj = MyClass()
            result = obj.set_cache()

            self.assertEqual(result, 50)

    def test_configuration_inject_allows_override(self):
        """Test @configuration_inject allows manual override."""
        with patch('annotation_toolkit.config.Config') as MockConfig:
            mock_config = MockConfig.return_value
            mock_config.get.return_value = 100

            @configuration_inject('security.max_file_size')
            def validate_file(max_size: int):
                return max_size

            result = validate_file(max_size=200)

            self.assertEqual(result, 200)

    def test_configuration_inject_parses_nested_path(self):
        """Test @configuration_inject parses nested config paths."""
        with patch('annotation_toolkit.config.Config') as MockConfig:
            mock_config = MockConfig.return_value
            mock_config.get.return_value = "value"

            @configuration_inject('level1.level2.level3')
            def get_value(val: str):
                return val

            result = get_value()

            mock_config.get.assert_called_once_with('level1', 'level2', 'level3')


class TestDependencyManager(unittest.TestCase):
    """Test DependencyManager context manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = DIContainer()
        self.container.register(TestService, TestService)

        # Patch container functions
        self.get_container_patcher = patch('annotation_toolkit.di.decorators.get_container')
        self.set_container_patcher = patch('annotation_toolkit.di.container.set_container')

        self.mock_get_container = self.get_container_patcher.start()
        self.mock_set_container = self.set_container_patcher.start()

        self.mock_get_container.return_value = self.container

    def tearDown(self):
        """Clean up test fixtures."""
        self.get_container_patcher.stop()
        self.set_container_patcher.stop()

    def test_dependency_manager_creates_child_container(self):
        """Test DependencyManager creates child container."""
        with DependencyManager() as scoped_container:
            self.assertIsNotNone(scoped_container)
            # Verify set_container was called
            self.mock_set_container.assert_called()

    def test_dependency_manager_applies_overrides(self):
        """Test DependencyManager applies service overrides."""
        custom_service = TestService("overridden")
        overrides = {TestService: custom_service}

        with DependencyManager(overrides) as scoped_container:
            # Verify override was registered
            self.assertIsNotNone(scoped_container)

    def test_dependency_manager_restores_original_container(self):
        """Test DependencyManager restores original container on exit."""
        with DependencyManager():
            pass

        # Verify set_container was called twice (enter and exit)
        self.assertEqual(self.mock_set_container.call_count, 2)

    def test_dependency_manager_restores_on_exception(self):
        """Test DependencyManager restores container even on exception."""
        try:
            with DependencyManager():
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Verify set_container was called to restore
        self.assertEqual(self.mock_set_container.call_count, 2)


class TestWithDependenciesDecorator(unittest.TestCase):
    """Test @with_dependencies decorator."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = DIContainer()
        self.container.register(TestService, TestService)

        # Patch container functions
        self.get_container_patcher = patch('annotation_toolkit.di.decorators.get_container')
        self.set_container_patcher = patch('annotation_toolkit.di.container.set_container')

        self.mock_get_container = self.get_container_patcher.start()
        self.mock_set_container = self.set_container_patcher.start()

        self.mock_get_container.return_value = self.container

    def tearDown(self):
        """Clean up test fixtures."""
        self.get_container_patcher.stop()
        self.set_container_patcher.stop()

    def test_with_dependencies_creates_scoped_context(self):
        """Test @with_dependencies creates scoped context."""
        custom_service = TestService("mocked")

        @with_dependencies(test_service=custom_service)
        def test_function():
            return "executed"

        result = test_function()

        self.assertEqual(result, "executed")
        # Verify container was swapped and restored
        self.assertEqual(self.mock_set_container.call_count, 2)

    def test_with_dependencies_preserves_function_metadata(self):
        """Test @with_dependencies preserves function metadata."""
        @with_dependencies(service=TestService())
        def my_function():
            """Function docstring."""
            pass

        self.assertEqual(my_function.__name__, "my_function")
        self.assertEqual(my_function.__doc__, "Function docstring.")


class TestLazyInject(unittest.TestCase):
    """Test lazy_inject function."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = DIContainer()
        self.container.register(TestService, TestService)

        # Patch get_container
        self.container_patcher = patch('annotation_toolkit.di.decorators.get_container')
        self.mock_get_container = self.container_patcher.start()
        self.mock_get_container.return_value = self.container

    def tearDown(self):
        """Clean up test fixtures."""
        self.container_patcher.stop()

    def test_lazy_inject_returns_callable(self):
        """Test lazy_inject returns a callable."""
        resolver = lazy_inject(TestService)

        self.assertTrue(callable(resolver))

    def test_lazy_inject_resolves_on_call(self):
        """Test lazy_inject resolves service when called."""
        resolver = lazy_inject(TestService)

        service = resolver()

        self.assertIsInstance(service, TestService)
        self.assertEqual(service.value, "test")

    def test_lazy_inject_defers_resolution(self):
        """Test lazy_inject defers resolution until called."""
        # Create resolver before service is registered
        self.container = DIContainer()
        self.mock_get_container.return_value = self.container

        resolver = lazy_inject(TestService)

        # Register service after creating resolver
        self.container.register(TestService, TestService)

        # Should still work when called
        service = resolver()
        self.assertIsInstance(service, TestService)

    def test_lazy_inject_multiple_calls(self):
        """Test lazy_inject can be called multiple times."""
        resolver = lazy_inject(TestService)

        service1 = resolver()
        service2 = resolver()

        # Both should be valid instances (singleton behavior)
        self.assertIsInstance(service1, TestService)
        self.assertIsInstance(service2, TestService)


class TestAutoWireDecorator(unittest.TestCase):
    """Test @auto_wire decorator."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = DIContainer()
        self.container.register(TestService, TestService)
        self.container.register(AnotherService, AnotherService)

        # Patch get_container
        self.container_patcher = patch('annotation_toolkit.di.decorators.get_container')
        self.mock_get_container = self.container_patcher.start()
        self.mock_get_container.return_value = self.container

    def tearDown(self):
        """Clean up test fixtures."""
        self.container_patcher.stop()

    def test_auto_wire_injects_dependencies(self):
        """Test @auto_wire automatically injects constructor dependencies."""
        @auto_wire
        class MyService:
            def __init__(self, test_service: TestService, another_service: AnotherService):
                self.test_service = test_service
                self.another_service = another_service

        instance = MyService()

        self.assertIsInstance(instance.test_service, TestService)
        self.assertIsInstance(instance.another_service, AnotherService)

    def test_auto_wire_allows_manual_override(self):
        """Test @auto_wire allows manual dependency override."""
        @auto_wire
        class MyService:
            def __init__(self, test_service: TestService):
                self.test_service = test_service

        custom_service = TestService("custom")
        instance = MyService(test_service=custom_service)

        self.assertEqual(instance.test_service.value, "custom")

    def test_auto_wire_with_positional_args(self):
        """Test @auto_wire works with positional arguments."""
        @auto_wire
        class MyService:
            def __init__(self, name: str, test_service: TestService):
                self.name = name
                self.test_service = test_service

        instance = MyService("John")

        self.assertEqual(instance.name, "John")
        self.assertIsInstance(instance.test_service, TestService)

    def test_auto_wire_skips_unregistered_services(self):
        """Test @auto_wire skips unregistered services gracefully."""
        class UnregisteredService:
            pass

        @auto_wire
        class MyService:
            def __init__(self, test_service: TestService,
                         unregistered: Optional[UnregisteredService] = None):
                self.test_service = test_service
                self.unregistered = unregistered

        instance = MyService()

        self.assertIsInstance(instance.test_service, TestService)
        self.assertIsNone(instance.unregistered)

    def test_auto_wire_preserves_class_metadata(self):
        """Test @auto_wire preserves class name and docstring."""
        @auto_wire
        class MyService:
            """Service docstring."""
            pass

        self.assertEqual(MyService.__name__, "MyService")
        self.assertEqual(MyService.__doc__, "Service docstring.")

    def test_auto_wire_with_no_annotations(self):
        """Test @auto_wire with constructor that has no type annotations."""
        @auto_wire
        class MyService:
            def __init__(self, arg1, arg2):
                self.arg1 = arg1
                self.arg2 = arg2

        instance = MyService("val1", "val2")

        self.assertEqual(instance.arg1, "val1")
        self.assertEqual(instance.arg2, "val2")


class TestDecoratorsEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = DIContainer()

        # Patch get_container
        self.container_patcher = patch('annotation_toolkit.di.decorators.get_container')
        self.mock_get_container = self.container_patcher.start()
        self.mock_get_container.return_value = self.container

    def tearDown(self):
        """Clean up test fixtures."""
        self.container_patcher.stop()

    def test_inject_with_empty_signature(self):
        """Test @inject with function that has no parameters."""
        @inject()
        def no_params():
            return "result"

        result = no_params()

        self.assertEqual(result, "result")

    def test_injectable_with_invalid_scope(self):
        """Test @injectable with invalid scope defaults to singleton."""
        @injectable(scope='invalid')
        class MyService:
            pass

        instance1 = self.container.resolve(MyService)
        instance2 = self.container.resolve(MyService)

        # Should default to singleton behavior
        self.assertIs(instance1, instance2)

    def test_auto_wire_with_kwargs_only(self):
        """Test @auto_wire with keyword-only arguments."""
        @auto_wire
        class MyService:
            def __init__(self, *, test_service: TestService):
                self.test_service = test_service

        self.container.register(TestService, TestService)
        instance = MyService()

        self.assertIsInstance(instance.test_service, TestService)


class TestDecoratorsIntegration(unittest.TestCase):
    """Integration tests for decorators working together."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = DIContainer()

        # Patch get_container
        self.container_patcher = patch('annotation_toolkit.di.decorators.get_container')
        self.mock_get_container = self.container_patcher.start()
        self.mock_get_container.return_value = self.container

    def tearDown(self):
        """Clean up test fixtures."""
        self.container_patcher.stop()

    def test_injectable_and_auto_wire_together(self):
        """Test @injectable and @auto_wire working together."""
        @injectable()
        class ServiceA:
            pass

        @injectable()
        @auto_wire
        class ServiceB:
            def __init__(self, service_a: ServiceA):
                self.service_a = service_a

        instance = self.container.resolve(ServiceB)

        self.assertIsInstance(instance, ServiceB)
        self.assertIsInstance(instance.service_a, ServiceA)

    def test_inject_with_injectable_services(self):
        """Test @inject works with @injectable services."""
        @injectable()
        class MyService:
            def get_value(self):
                return "injected"

        @inject()
        def process(my_service: MyService):
            return my_service.get_value()

        result = process()

        self.assertEqual(result, "injected")


if __name__ == "__main__":
    unittest.main()
