# Dependency Injection Implementation

This document describes the dependency injection (DI) system that has been implemented in the Annotation Swiss Knife project.

## Overview

The dependency injection system was implemented to improve code modularity, testability, and maintainability by reducing tight coupling between components. The system follows standard DI patterns and provides a clean separation of concerns.

## Architecture

### Core Components

1. **DI Container** (`annotation_toolkit/di/container.py`)
   - Main container that manages service registrations and resolution
   - Supports singleton, transient, and scoped service lifetimes
   - Provides circular dependency detection
   - Thread-safe service resolution

2. **Service Registry** (`annotation_toolkit/di/registry.py`)
   - Manages service registrations and their metadata
   - Handles service creation through implementations, instances, or factories
   - Supports automatic dependency injection in constructors

3. **Interfaces** (`annotation_toolkit/di/interfaces.py`)
   - Defines protocols/interfaces for all services
   - Ensures contract compliance through Python's Protocol system
   - Includes interfaces for tools, configuration, logging, and UI widgets

4. **Bootstrap Module** (`annotation_toolkit/di/bootstrap.py`)
   - Provides application-level service configuration
   - Factory functions for creating tools with dependencies
   - Validation and utility functions for container management

5. **Exception System** (`annotation_toolkit/di/exceptions.py`)
   - Custom exceptions for DI-related errors
   - Detailed error messages with context information
   - Hierarchical exception inheritance

## Service Scopes

The DI system supports three service scopes:

- **Singleton**: One instance per container (default)
- **Transient**: New instance every time resolved
- **Scoped**: One instance per scope (for future request scoping)

## Integration Points

### GUI Application

The main GUI application (`annotation_toolkit/ui/gui/app.py`) has been updated to:
- Accept an optional DI container in its constructor
- Bootstrap a DI container if none is provided
- Resolve tools from the container instead of direct instantiation
- Include fallback mechanism for compatibility

### CLI Commands

All CLI commands (`annotation_toolkit/ui/cli/commands.py`) now:
- Bootstrap a DI container for each command execution
- Resolve tools from the container
- Validate container configuration before proceeding
- Handle DI-related errors gracefully

### Configuration Integration

The configuration system is integrated with DI:
- Config instance is registered as both interface and concrete type
- Factory functions use configuration to create properly configured tools
- Command-line arguments can override DI-configured settings

## Usage Examples

### Basic Service Registration

```python
from annotation_toolkit.di import DIContainer, ServiceScope

container = DIContainer()

# Register a singleton service
container.register(MyInterface, MyImplementation, ServiceScope.SINGLETON)

# Register a transient service
container.register(MyInterface, MyImplementation, ServiceScope.TRANSIENT)

# Register an instance
container.register_instance(MyInterface, my_instance)

# Register with factory
container.register_factory(MyInterface, my_factory_function)
```

### Application Bootstrap

```python
from annotation_toolkit.di.bootstrap import bootstrap_application

# Bootstrap with default configuration
container = bootstrap_application()

# Bootstrap with custom configuration
config = Config("my_config.yaml")
container = bootstrap_application(config)

# Get tool instances
tools = get_tool_instances(container)
dict_tool = tools["Dictionary to Bullet List"]
```

### Service Resolution

```python
from annotation_toolkit.di import resolve

# Resolve from global container
tool = resolve(DictToBulletList)

# Resolve from specific container
tool = container.resolve(DictToBulletList)
```

## Benefits Achieved

### 1. **Improved Testability**
- Easy to mock dependencies in unit tests
- Isolated testing of individual components
- Test-specific service configurations

### 2. **Reduced Coupling**
- Components depend on interfaces, not concrete implementations
- Constructor injection makes dependencies explicit
- Easier to swap implementations

### 3. **Enhanced Maintainability**
- Centralized service configuration
- Clear separation of concerns
- Consistent service lifecycle management

### 4. **Better Extensibility**
- Easy to add new services without modifying existing code
- Plugin-like architecture for tools
- Support for different service scopes

### 5. **Configuration Integration**
- Services can be configured through external configuration files
- Runtime configuration changes possible
- Environment-specific service configurations

## Backward Compatibility

The implementation maintains backward compatibility:

1. **Fallback Mechanisms**
   - GUI application falls back to manual tool creation if DI fails
   - Existing code paths remain functional

2. **Optional DI Usage**
   - DI container can be optionally provided to constructors
   - Default behavior creates and configures DI automatically

3. **Gradual Migration**
   - Components can be migrated to DI incrementally
   - Mixed DI and non-DI usage is supported during transition

## Testing

Comprehensive tests validate the DI implementation:

- **Container Tests**: Service registration, resolution, and lifecycle
- **Bootstrap Tests**: Application-level service configuration
- **Integration Tests**: End-to-end tool functionality through DI
- **Error Handling Tests**: Exception scenarios and error recovery

All tests pass, confirming the implementation is stable and functional.

## Future Enhancements

The DI system is designed to support future enhancements:

1. **Request Scoping**: Support for request-scoped services in web scenarios
2. **Configuration Validation**: JSON Schema validation for service configurations
3. **Service Discovery**: Automatic service discovery and registration
4. **Performance Optimizations**: Caching and optimization for high-frequency resolution
5. **Plugin System**: Full plugin architecture built on top of DI

## Migration Guide

For developers working with the codebase:

1. **New Components**: Use constructor injection and register services in bootstrap
2. **Existing Components**: Gradually migrate to accept dependencies through constructors
3. **Testing**: Use DI container in tests to provide mock dependencies
4. **Configuration**: Use the ConfigInterface instead of direct Config access where possible

The dependency injection system provides a solid foundation for the application's architecture while maintaining simplicity and ease of use.