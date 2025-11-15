# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Updated documentation to use generic corporate terminology for broader applicability
- Updated JSON parser patterns to use generic AI terminology

### Infrastructure
- Updated macOS bundle identifiers to vendor-neutral format
- Added uv.lock to gitignore
- Removed unused image file from docs

## [0.4.0] - 2025-01-14

### Added
- Automated CI/CD pipeline with GitHub Actions
- Cross-platform executable builds (macOS, Windows, Linux)
- Dynamic versioning using setuptools-scm based on git tags
- Comprehensive release workflow with automated GitHub Releases
- SHA256 checksums for release artifacts
- Linux build support with PyInstaller spec and build script
- Comprehensive testing infrastructure with pytest configuration
- Extensive test coverage for core modules and utilities

### Changed
- Version management now uses git tags as the single source of truth
- Build scripts updated to support dynamic versioning
- Documentation updated to reflect CI/CD pipeline and release process

### Infrastructure
- Added setuptools-scm for version management
- Created Linux build spec and build script
- Enhanced release documentation (RELEASE_PROCESS.md)
- Added CHANGELOG.md following keepachangelog.com format
- Updated CLAUDE.md with CI/CD and version management sections

## [0.3.0] - Previous Release

### Added
- Advanced infrastructure modules (profiling, streaming, validation, recovery)
- Structured logging with context tracking
- Resource management utilities
- Security utilities (path validation, rate limiting, input sanitization)
- Conversation generator tool
- Comprehensive testing infrastructure with pytest

### Changed
- Improved dependency injection system
- Enhanced error handling framework
- Updated configuration system with security and performance settings

### Fixed
- Various bug fixes and stability improvements

## [0.2.0] - Earlier Release

### Added
- JSON Visualizer tool for conversation data
- Text Cleaner utility
- Dictionary to Bullet List converter
- CLI interface for all tools
- GUI application with PyQt5

### Changed
- Refactored architecture with dependency injection
- Improved error handling

## [0.1.0] - Initial Release

### Added
- Basic annotation toolkit framework
- Core tool base classes
- Initial GUI and CLI interfaces
- Configuration system
- Build scripts for macOS and Windows

---

## How to Use This Changelog

### For Developers
When adding changes, place them under `[Unreleased]` in the appropriate category:

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Now removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes
- **Infrastructure**: Changes to build, CI/CD, or development tools

### For Releases
When creating a release:
1. Move items from `[Unreleased]` to a new version section
2. Add the release date
3. Update the version links at the bottom

### Version Links
[Unreleased]: https://github.com/9scorp4/annotator-swiss-knife/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.4.0
[0.3.0]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.3.0
[0.2.0]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.2.0
[0.1.0]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.1.0
