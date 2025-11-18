"""
Unit tests for DI registry module.

This module tests ServiceScope, ServiceRegistration, and ServiceRegistry
classes for service lifecycle management and registration.
"""

import unittest
from typing import Optional
from unittest.mock import MagicMock, Mock

from annotation_toolkit.di.registry import (
    ServiceScope,
    ServiceRegistration,
    ServiceRegistry
)


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


class TestServiceScope(unittest.TestCase):
    """Test ServiceScope enum."""

    def test_service_scope_singleton_value(self):
        """Test SINGLETON scope has correct value."""
        self.assertEqual(ServiceScope.SINGLETON.value, "singleton")

    def test_service_scope_transient_value(self):
        """Test TRANSIENT scope has correct value."""
        self.assertEqual(ServiceScope.TRANSIENT.value, "transient")

    def test_service_scope_scoped_value(self):
        """Test SCOPED scope has correct value."""
        self.assertEqual(ServiceScope.SCOPED.value, "scoped")

    def test_service_scope_enum_members(self):
        """Test ServiceScope has all expected members."""
        scopes = [s.name for s in ServiceScope]
        self.assertIn("SINGLETON", scopes)
        self.assertIn("TRANSIENT", scopes)
        self.assertIn("SCOPED", scopes)


class TestServiceRegistration(unittest.TestCase):
    """Test ServiceRegistration class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock container
        self.mock_container = MagicMock()
        self.mock_container.is_registered = MagicMock(return_value=False)

    def test_registration_with_implementation(self):
        """Test registration with implementation class."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService
        )

        self.assertEqual(registration.interface, TestService)
        self.assertEqual(registration.implementation, TestService)
        self.assertIsNone(registration.instance)
        self.assertIsNone(registration.factory)
        self.assertEqual(registration.scope, ServiceScope.SINGLETON)

    def test_registration_with_instance(self):
        """Test registration with pre-created instance."""
        instance = TestService("custom")
        registration = ServiceRegistration(
            interface=TestService,
            instance=instance
        )

        self.assertEqual(registration.interface, TestService)
        self.assertIsNone(registration.implementation)
        self.assertEqual(registration.instance, instance)
        self.assertIsNone(registration.factory)

    def test_registration_with_factory(self):
        """Test registration with factory function."""
        def factory() -> TestService:
            return TestService("factory")

        registration = ServiceRegistration(
            interface=TestService,
            factory=factory
        )

        self.assertEqual(registration.interface, TestService)
        self.assertIsNone(registration.implementation)
        self.assertIsNone(registration.instance)
        self.assertEqual(registration.factory, factory)

    def test_registration_with_transient_scope(self):
        """Test registration with transient scope."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService,
            scope=ServiceScope.TRANSIENT
        )

        self.assertEqual(registration.scope, ServiceScope.TRANSIENT)

    def test_registration_with_constructor_args(self):
        """Test registration with constructor arguments."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService,
            value="custom_value"
        )

        self.assertEqual(registration.constructor_args, {"value": "custom_value"})

    def test_create_instance_returns_pre_created_instance(self):
        """Test create_instance returns pre-created instance if provided."""
        instance = TestService("custom")
        registration = ServiceRegistration(
            interface=TestService,
            instance=instance
        )

        created = registration.create_instance(self.mock_container)

        self.assertIs(created, instance)

    def test_create_instance_from_implementation(self):
        """Test create_instance creates instance from implementation class."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService,
            value="test_value"
        )

        instance = registration.create_instance(self.mock_container)

        self.assertIsInstance(instance, TestService)
        self.assertEqual(instance.value, "test_value")

    def test_create_instance_from_factory(self):
        """Test create_instance creates instance from factory function."""
        def factory(value: str) -> TestService:
            return TestService(value)

        registration = ServiceRegistration(
            interface=TestService,
            factory=factory,
            value="factory_value"
        )

        instance = registration.create_instance(self.mock_container)

        self.assertIsInstance(instance, TestService)
        self.assertEqual(instance.value, "factory_value")

    def test_create_instance_singleton_caches_instance(self):
        """Test create_instance caches singleton instances."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService,
            scope=ServiceScope.SINGLETON
        )

        instance1 = registration.create_instance(self.mock_container)
        instance2 = registration.create_instance(self.mock_container)

        self.assertIs(instance1, instance2)

    def test_create_instance_transient_creates_new_instances(self):
        """Test create_instance creates new instances for transient scope."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService,
            scope=ServiceScope.TRANSIENT
        )

        instance1 = registration.create_instance(self.mock_container)
        instance2 = registration.create_instance(self.mock_container)

        self.assertIsNot(instance1, instance2)

    def test_create_instance_raises_error_for_invalid_registration(self):
        """Test create_instance raises error for invalid registration."""
        registration = ServiceRegistration(
            interface=TestService
            # No implementation, instance, or factory
        )

        with self.assertRaises(ValueError) as cm:
            registration.create_instance(self.mock_container)

        self.assertIn("Invalid service registration", str(cm.exception))

    def test_resolve_constructor_args_with_registered_services(self):
        """Test constructor argument resolution with registered services."""
        # Set up mock container to resolve dependencies
        test_service_instance = TestService()
        another_service_instance = AnotherService()

        def mock_is_registered(service_type):
            return service_type in [TestService, AnotherService]

        def mock_resolve(service_type):
            if service_type == TestService:
                return test_service_instance
            elif service_type == AnotherService:
                return another_service_instance
            return None

        self.mock_container.is_registered = mock_is_registered
        self.mock_container.resolve = mock_resolve

        registration = ServiceRegistration(
            interface=DependentService,
            implementation=DependentService,
            test_service=TestService,
            another_service=AnotherService
        )

        instance = registration.create_instance(self.mock_container)

        self.assertIsInstance(instance, DependentService)
        self.assertIs(instance.test_service, test_service_instance)
        self.assertIs(instance.another_service, another_service_instance)

    def test_resolve_constructor_args_with_literal_values(self):
        """Test constructor argument resolution with literal values."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService,
            value="literal_value"
        )

        resolved_args = registration._resolve_constructor_args(self.mock_container)

        self.assertEqual(resolved_args, {"value": "literal_value"})

    def test_create_from_factory_calls_factory(self):
        """Test _create_from_factory calls the factory function."""
        factory_called = False

        def factory() -> TestService:
            nonlocal factory_called
            factory_called = True
            return TestService("from_factory")

        registration = ServiceRegistration(
            interface=TestService,
            factory=factory
        )

        instance = registration._create_from_factory(self.mock_container)

        self.assertTrue(factory_called)
        self.assertEqual(instance.value, "from_factory")

    def test_create_from_implementation_calls_constructor(self):
        """Test _create_from_implementation calls the constructor."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService,
            value="from_implementation"
        )

        instance = registration._create_from_implementation(self.mock_container)

        self.assertIsInstance(instance, TestService)
        self.assertEqual(instance.value, "from_implementation")


class TestServiceRegistry(unittest.TestCase):
    """Test ServiceRegistry class."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = ServiceRegistry()

    def test_registry_initialization(self):
        """Test ServiceRegistry initializes empty."""
        self.assertEqual(len(self.registry._registrations), 0)

    def test_register_service_with_implementation(self):
        """Test registering a service with implementation."""
        self.registry.register(
            interface=TestService,
            implementation=TestService
        )

        self.assertTrue(self.registry.is_registered(TestService))

    def test_register_service_with_instance(self):
        """Test registering a service with instance."""
        instance = TestService("custom")
        self.registry.register(
            interface=TestService,
            instance=instance
        )

        registration = self.registry.get_registration(TestService)
        self.assertIsNotNone(registration)
        self.assertEqual(registration.instance, instance)

    def test_register_service_with_factory(self):
        """Test registering a service with factory."""
        def factory() -> TestService:
            return TestService("factory")

        self.registry.register(
            interface=TestService,
            factory=factory
        )

        registration = self.registry.get_registration(TestService)
        self.assertIsNotNone(registration)
        self.assertEqual(registration.factory, factory)

    def test_register_service_with_custom_scope(self):
        """Test registering a service with custom scope."""
        self.registry.register(
            interface=TestService,
            implementation=TestService,
            scope=ServiceScope.TRANSIENT
        )

        registration = self.registry.get_registration(TestService)
        self.assertEqual(registration.scope, ServiceScope.TRANSIENT)

    def test_register_service_with_constructor_args(self):
        """Test registering a service with constructor arguments."""
        self.registry.register(
            interface=TestService,
            implementation=TestService,
            value="custom"
        )

        registration = self.registry.get_registration(TestService)
        self.assertEqual(registration.constructor_args, {"value": "custom"})

    def test_register_overwrites_existing_registration(self):
        """Test registering same interface twice overwrites."""
        self.registry.register(
            interface=TestService,
            implementation=TestService,
            value="first"
        )
        self.registry.register(
            interface=TestService,
            implementation=TestService,
            value="second"
        )

        registration = self.registry.get_registration(TestService)
        self.assertEqual(registration.constructor_args["value"], "second")

    def test_get_registration_returns_registration(self):
        """Test get_registration returns correct registration."""
        self.registry.register(
            interface=TestService,
            implementation=TestService
        )

        registration = self.registry.get_registration(TestService)

        self.assertIsNotNone(registration)
        self.assertEqual(registration.interface, TestService)

    def test_get_registration_returns_none_for_unregistered(self):
        """Test get_registration returns None for unregistered service."""
        registration = self.registry.get_registration(TestService)

        self.assertIsNone(registration)

    def test_is_registered_returns_true_for_registered_service(self):
        """Test is_registered returns True for registered service."""
        self.registry.register(
            interface=TestService,
            implementation=TestService
        )

        self.assertTrue(self.registry.is_registered(TestService))

    def test_is_registered_returns_false_for_unregistered_service(self):
        """Test is_registered returns False for unregistered service."""
        self.assertFalse(self.registry.is_registered(TestService))

    def test_get_all_registrations_returns_all(self):
        """Test get_all_registrations returns all registrations."""
        self.registry.register(interface=TestService, implementation=TestService)
        self.registry.register(interface=AnotherService, implementation=AnotherService)

        all_registrations = self.registry.get_all_registrations()

        self.assertEqual(len(all_registrations), 2)
        self.assertIn(TestService, all_registrations)
        self.assertIn(AnotherService, all_registrations)

    def test_get_all_registrations_returns_copy(self):
        """Test get_all_registrations returns a copy."""
        self.registry.register(interface=TestService, implementation=TestService)

        all_registrations = self.registry.get_all_registrations()
        all_registrations.clear()

        # Original should still have the registration
        self.assertTrue(self.registry.is_registered(TestService))

    def test_clear_removes_all_registrations(self):
        """Test clear removes all registrations."""
        self.registry.register(interface=TestService, implementation=TestService)
        self.registry.register(interface=AnotherService, implementation=AnotherService)

        self.registry.clear()

        self.assertFalse(self.registry.is_registered(TestService))
        self.assertFalse(self.registry.is_registered(AnotherService))
        self.assertEqual(len(self.registry._registrations), 0)

    def test_remove_removes_registered_service(self):
        """Test remove removes a registered service."""
        self.registry.register(interface=TestService, implementation=TestService)

        result = self.registry.remove(TestService)

        self.assertTrue(result)
        self.assertFalse(self.registry.is_registered(TestService))

    def test_remove_returns_false_for_unregistered_service(self):
        """Test remove returns False for unregistered service."""
        result = self.registry.remove(TestService)

        self.assertFalse(result)

    def test_remove_does_not_affect_other_services(self):
        """Test remove only removes specified service."""
        self.registry.register(interface=TestService, implementation=TestService)
        self.registry.register(interface=AnotherService, implementation=AnotherService)

        self.registry.remove(TestService)

        self.assertFalse(self.registry.is_registered(TestService))
        self.assertTrue(self.registry.is_registered(AnotherService))


class TestServiceRegistrationEdgeCases(unittest.TestCase):
    """Test edge cases for ServiceRegistration."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_container = MagicMock()
        self.mock_container.is_registered = MagicMock(return_value=False)

    def test_registration_with_scoped_scope(self):
        """Test registration with SCOPED scope."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService,
            scope=ServiceScope.SCOPED
        )

        # SCOPED doesn't cache instances (behaves like TRANSIENT for now)
        instance1 = registration.create_instance(self.mock_container)
        instance2 = registration.create_instance(self.mock_container)

        # SCOPED creates new instances (no caching implemented yet)
        self.assertIsNot(instance1, instance2)

    def test_registration_with_no_constructor_args(self):
        """Test registration with no constructor arguments."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService
        )

        self.assertEqual(registration.constructor_args, {})

    def test_registration_with_multiple_constructor_args(self):
        """Test registration with multiple constructor arguments."""
        registration = ServiceRegistration(
            interface=DependentService,
            implementation=DependentService,
            test_service=TestService,
            another_service=AnotherService
        )

        self.assertEqual(len(registration.constructor_args), 2)
        self.assertIn("test_service", registration.constructor_args)
        self.assertIn("another_service", registration.constructor_args)

    def test_singleton_instance_cached_after_first_call(self):
        """Test singleton instance is cached after first create_instance call."""
        registration = ServiceRegistration(
            interface=TestService,
            implementation=TestService,
            scope=ServiceScope.SINGLETON
        )

        self.assertIsNone(registration._singleton_instance)

        instance = registration.create_instance(self.mock_container)

        self.assertIsNotNone(registration._singleton_instance)
        self.assertIs(instance, registration._singleton_instance)


class TestServiceRegistryIntegration(unittest.TestCase):
    """Integration tests for ServiceRegistry."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = ServiceRegistry()

    def test_register_and_retrieve_multiple_services(self):
        """Test registering and retrieving multiple services."""
        self.registry.register(interface=TestService, implementation=TestService)
        self.registry.register(interface=AnotherService, implementation=AnotherService)

        test_reg = self.registry.get_registration(TestService)
        another_reg = self.registry.get_registration(AnotherService)

        self.assertIsNotNone(test_reg)
        self.assertIsNotNone(another_reg)
        self.assertEqual(test_reg.interface, TestService)
        self.assertEqual(another_reg.interface, AnotherService)

    def test_register_clear_and_re_register(self):
        """Test clearing registry and re-registering services."""
        self.registry.register(interface=TestService, implementation=TestService)

        self.registry.clear()
        self.assertFalse(self.registry.is_registered(TestService))

        self.registry.register(interface=TestService, implementation=TestService)
        self.assertTrue(self.registry.is_registered(TestService))

    def test_multiple_registrations_with_different_scopes(self):
        """Test registering services with different scopes."""
        self.registry.register(
            interface=TestService,
            implementation=TestService,
            scope=ServiceScope.SINGLETON
        )
        self.registry.register(
            interface=AnotherService,
            implementation=AnotherService,
            scope=ServiceScope.TRANSIENT
        )

        test_reg = self.registry.get_registration(TestService)
        another_reg = self.registry.get_registration(AnotherService)

        self.assertEqual(test_reg.scope, ServiceScope.SINGLETON)
        self.assertEqual(another_reg.scope, ServiceScope.TRANSIENT)


if __name__ == "__main__":
    unittest.main()
