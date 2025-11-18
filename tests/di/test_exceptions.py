"""
Unit tests for DI exceptions module.

This module tests all DI exception classes including DIException,
ServiceNotRegisteredError, CircularDependencyError, ServiceCreationError,
and InvalidServiceRegistrationError.
"""

import unittest

from annotation_toolkit.di.exceptions import (
    DIException,
    ServiceNotRegisteredError,
    CircularDependencyError,
    ServiceCreationError,
    InvalidServiceRegistrationError
)


# Test service classes
class TestService:
    """Mock service for testing."""
    pass


class AnotherService:
    """Another mock service for testing."""
    pass


class DependentService:
    """Service with dependencies."""
    pass


class TestDIException(unittest.TestCase):
    """Test DIException base class."""

    def test_di_exception_inherits_from_exception(self):
        """Test DIException inherits from Exception."""
        self.assertTrue(issubclass(DIException, Exception))

    def test_di_exception_can_be_raised(self):
        """Test DIException can be raised."""
        with self.assertRaises(DIException):
            raise DIException("Test exception")

    def test_di_exception_with_message(self):
        """Test DIException with custom message."""
        message = "Custom DI error message"
        exception = DIException(message)

        self.assertEqual(str(exception), message)

    def test_di_exception_can_be_caught_as_exception(self):
        """Test DIException can be caught as Exception."""
        try:
            raise DIException("Test")
        except Exception as e:
            self.assertIsInstance(e, DIException)


class TestServiceNotRegisteredError(unittest.TestCase):
    """Test ServiceNotRegisteredError exception."""

    def test_service_not_registered_error_inherits_from_di_exception(self):
        """Test ServiceNotRegisteredError inherits from DIException."""
        self.assertTrue(issubclass(ServiceNotRegisteredError, DIException))

    def test_service_not_registered_error_with_default_message(self):
        """Test ServiceNotRegisteredError generates default message."""
        exception = ServiceNotRegisteredError(TestService)

        expected_message = "Service not registered for interface: TestService"
        self.assertEqual(str(exception), expected_message)

    def test_service_not_registered_error_with_custom_message(self):
        """Test ServiceNotRegisteredError with custom message."""
        custom_message = "Custom error message for TestService"
        exception = ServiceNotRegisteredError(TestService, custom_message)

        self.assertEqual(str(exception), custom_message)

    def test_service_not_registered_error_stores_interface_type(self):
        """Test ServiceNotRegisteredError stores interface_type."""
        exception = ServiceNotRegisteredError(TestService)

        self.assertEqual(exception.interface_type, TestService)

    def test_service_not_registered_error_can_be_raised(self):
        """Test ServiceNotRegisteredError can be raised."""
        with self.assertRaises(ServiceNotRegisteredError) as cm:
            raise ServiceNotRegisteredError(TestService)

        self.assertIn("TestService", str(cm.exception))

    def test_service_not_registered_error_can_be_caught_as_di_exception(self):
        """Test ServiceNotRegisteredError can be caught as DIException."""
        try:
            raise ServiceNotRegisteredError(TestService)
        except DIException as e:
            self.assertIsInstance(e, ServiceNotRegisteredError)

    def test_service_not_registered_error_with_different_interface_types(self):
        """Test ServiceNotRegisteredError with different interface types."""
        exception1 = ServiceNotRegisteredError(TestService)
        exception2 = ServiceNotRegisteredError(AnotherService)

        self.assertIn("TestService", str(exception1))
        self.assertIn("AnotherService", str(exception2))
        self.assertEqual(exception1.interface_type, TestService)
        self.assertEqual(exception2.interface_type, AnotherService)


class TestCircularDependencyError(unittest.TestCase):
    """Test CircularDependencyError exception."""

    def test_circular_dependency_error_inherits_from_di_exception(self):
        """Test CircularDependencyError inherits from DIException."""
        self.assertTrue(issubclass(CircularDependencyError, DIException))

    def test_circular_dependency_error_with_default_message(self):
        """Test CircularDependencyError generates default message."""
        dependency_chain = [TestService, AnotherService, TestService]
        exception = CircularDependencyError(dependency_chain)

        expected_message = "Circular dependency detected: TestService -> AnotherService -> TestService"
        self.assertEqual(str(exception), expected_message)

    def test_circular_dependency_error_with_custom_message(self):
        """Test CircularDependencyError with custom message."""
        dependency_chain = [TestService, AnotherService]
        custom_message = "Custom circular dependency error"
        exception = CircularDependencyError(dependency_chain, custom_message)

        self.assertEqual(str(exception), custom_message)

    def test_circular_dependency_error_stores_dependency_chain(self):
        """Test CircularDependencyError stores dependency_chain."""
        dependency_chain = [TestService, AnotherService, TestService]
        exception = CircularDependencyError(dependency_chain)

        self.assertEqual(exception.dependency_chain, dependency_chain)

    def test_circular_dependency_error_can_be_raised(self):
        """Test CircularDependencyError can be raised."""
        dependency_chain = [TestService, AnotherService, TestService]

        with self.assertRaises(CircularDependencyError) as cm:
            raise CircularDependencyError(dependency_chain)

        self.assertIn("Circular dependency detected", str(cm.exception))

    def test_circular_dependency_error_can_be_caught_as_di_exception(self):
        """Test CircularDependencyError can be caught as DIException."""
        dependency_chain = [TestService, AnotherService]

        try:
            raise CircularDependencyError(dependency_chain)
        except DIException as e:
            self.assertIsInstance(e, CircularDependencyError)

    def test_circular_dependency_error_with_long_chain(self):
        """Test CircularDependencyError with long dependency chain."""
        dependency_chain = [
            TestService,
            AnotherService,
            DependentService,
            TestService
        ]
        exception = CircularDependencyError(dependency_chain)

        message = str(exception)
        self.assertIn("TestService", message)
        self.assertIn("AnotherService", message)
        self.assertIn("DependentService", message)
        self.assertIn("->", message)

    def test_circular_dependency_error_with_single_element_chain(self):
        """Test CircularDependencyError with single element chain."""
        dependency_chain = [TestService]
        exception = CircularDependencyError(dependency_chain)

        self.assertEqual(str(exception), "Circular dependency detected: TestService")


class TestServiceCreationError(unittest.TestCase):
    """Test ServiceCreationError exception."""

    def test_service_creation_error_inherits_from_di_exception(self):
        """Test ServiceCreationError inherits from DIException."""
        self.assertTrue(issubclass(ServiceCreationError, DIException))

    def test_service_creation_error_with_default_message(self):
        """Test ServiceCreationError generates default message."""
        exception = ServiceCreationError(TestService)

        expected_message = "Failed to create service for interface: TestService"
        self.assertEqual(str(exception), expected_message)

    def test_service_creation_error_with_custom_message(self):
        """Test ServiceCreationError with custom message."""
        custom_message = "Custom creation error"
        exception = ServiceCreationError(TestService, message=custom_message)

        self.assertEqual(str(exception), custom_message)

    def test_service_creation_error_stores_interface_type(self):
        """Test ServiceCreationError stores interface_type."""
        exception = ServiceCreationError(TestService)

        self.assertEqual(exception.interface_type, TestService)

    def test_service_creation_error_with_original_exception(self):
        """Test ServiceCreationError with original exception."""
        original = ValueError("Original error")
        exception = ServiceCreationError(TestService, original_exception=original)

        self.assertEqual(exception.original_exception, original)
        self.assertIn("Original error", str(exception))

    def test_service_creation_error_message_includes_original_exception(self):
        """Test ServiceCreationError message includes original exception details."""
        original = TypeError("Type mismatch")
        exception = ServiceCreationError(TestService, original_exception=original)

        message = str(exception)
        self.assertIn("TestService", message)
        self.assertIn("Type mismatch", message)

    def test_service_creation_error_can_be_raised(self):
        """Test ServiceCreationError can be raised."""
        with self.assertRaises(ServiceCreationError) as cm:
            raise ServiceCreationError(TestService)

        self.assertIn("Failed to create service", str(cm.exception))

    def test_service_creation_error_can_be_caught_as_di_exception(self):
        """Test ServiceCreationError can be caught as DIException."""
        try:
            raise ServiceCreationError(TestService)
        except DIException as e:
            self.assertIsInstance(e, ServiceCreationError)

    def test_service_creation_error_without_original_exception(self):
        """Test ServiceCreationError without original exception."""
        exception = ServiceCreationError(TestService)

        self.assertIsNone(exception.original_exception)
        self.assertNotIn(" - ", str(exception))

    def test_service_creation_error_with_all_parameters(self):
        """Test ServiceCreationError with all parameters."""
        original = RuntimeError("Runtime problem")
        custom_message = "Complete custom message"
        exception = ServiceCreationError(
            TestService,
            original_exception=original,
            message=custom_message
        )

        self.assertEqual(str(exception), custom_message)
        self.assertEqual(exception.interface_type, TestService)
        self.assertEqual(exception.original_exception, original)


class TestInvalidServiceRegistrationError(unittest.TestCase):
    """Test InvalidServiceRegistrationError exception."""

    def test_invalid_registration_error_inherits_from_di_exception(self):
        """Test InvalidServiceRegistrationError inherits from DIException."""
        self.assertTrue(issubclass(InvalidServiceRegistrationError, DIException))

    def test_invalid_registration_error_with_default_message(self):
        """Test InvalidServiceRegistrationError generates default message."""
        exception = InvalidServiceRegistrationError(TestService)

        expected_message = "Invalid service registration for interface: TestService"
        self.assertEqual(str(exception), expected_message)

    def test_invalid_registration_error_with_custom_message(self):
        """Test InvalidServiceRegistrationError with custom message."""
        custom_message = "Custom invalid registration error"
        exception = InvalidServiceRegistrationError(TestService, custom_message)

        self.assertEqual(str(exception), custom_message)

    def test_invalid_registration_error_stores_interface_type(self):
        """Test InvalidServiceRegistrationError stores interface_type."""
        exception = InvalidServiceRegistrationError(TestService)

        self.assertEqual(exception.interface_type, TestService)

    def test_invalid_registration_error_can_be_raised(self):
        """Test InvalidServiceRegistrationError can be raised."""
        with self.assertRaises(InvalidServiceRegistrationError) as cm:
            raise InvalidServiceRegistrationError(TestService)

        self.assertIn("Invalid service registration", str(cm.exception))

    def test_invalid_registration_error_can_be_caught_as_di_exception(self):
        """Test InvalidServiceRegistrationError can be caught as DIException."""
        try:
            raise InvalidServiceRegistrationError(TestService)
        except DIException as e:
            self.assertIsInstance(e, InvalidServiceRegistrationError)

    def test_invalid_registration_error_with_different_interface_types(self):
        """Test InvalidServiceRegistrationError with different interface types."""
        exception1 = InvalidServiceRegistrationError(TestService)
        exception2 = InvalidServiceRegistrationError(AnotherService)

        self.assertIn("TestService", str(exception1))
        self.assertIn("AnotherService", str(exception2))
        self.assertEqual(exception1.interface_type, TestService)
        self.assertEqual(exception2.interface_type, AnotherService)


class TestExceptionHierarchy(unittest.TestCase):
    """Test exception hierarchy and relationships."""

    def test_all_di_exceptions_inherit_from_di_exception(self):
        """Test all DI exceptions inherit from DIException."""
        di_exceptions = [
            ServiceNotRegisteredError,
            CircularDependencyError,
            ServiceCreationError,
            InvalidServiceRegistrationError
        ]

        for exc_class in di_exceptions:
            self.assertTrue(
                issubclass(exc_class, DIException),
                f"{exc_class.__name__} should inherit from DIException"
            )

    def test_all_di_exceptions_can_be_caught_as_di_exception(self):
        """Test all DI exceptions can be caught as DIException."""
        exceptions = [
            ServiceNotRegisteredError(TestService),
            CircularDependencyError([TestService]),
            ServiceCreationError(TestService),
            InvalidServiceRegistrationError(TestService)
        ]

        for exc in exceptions:
            try:
                raise exc
            except DIException as e:
                self.assertIsInstance(e, DIException)

    def test_di_exception_can_be_caught_as_base_exception(self):
        """Test DIException can be caught as base Exception."""
        di_exceptions = [
            DIException("test"),
            ServiceNotRegisteredError(TestService),
            CircularDependencyError([TestService]),
            ServiceCreationError(TestService),
            InvalidServiceRegistrationError(TestService)
        ]

        for exc in di_exceptions:
            try:
                raise exc
            except Exception as e:
                self.assertIsInstance(e, Exception)


class TestExceptionUsagePatterns(unittest.TestCase):
    """Test common exception usage patterns."""

    def test_catching_specific_di_exception(self):
        """Test catching specific DI exception type."""
        caught = False

        try:
            raise ServiceNotRegisteredError(TestService)
        except ServiceNotRegisteredError:
            caught = True
        except DIException:
            pass

        self.assertTrue(caught)

    def test_catching_base_di_exception(self):
        """Test catching base DIException catches all DI exceptions."""
        caught = False

        try:
            raise ServiceCreationError(TestService)
        except DIException:
            caught = True

        self.assertTrue(caught)

    def test_exception_chaining_with_original_exception(self):
        """Test exception chaining with original exception."""
        try:
            try:
                raise ValueError("Original problem")
            except ValueError as e:
                raise ServiceCreationError(TestService, original_exception=e)
        except ServiceCreationError as e:
            self.assertIsInstance(e.original_exception, ValueError)
            self.assertEqual(str(e.original_exception), "Original problem")

    def test_extracting_interface_type_from_exception(self):
        """Test extracting interface_type from various exceptions."""
        exceptions = [
            ServiceNotRegisteredError(TestService),
            ServiceCreationError(AnotherService),
            InvalidServiceRegistrationError(DependentService)
        ]

        expected_types = [TestService, AnotherService, DependentService]

        for exc, expected_type in zip(exceptions, expected_types):
            self.assertEqual(exc.interface_type, expected_type)


if __name__ == "__main__":
    unittest.main()
