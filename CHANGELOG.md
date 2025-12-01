# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2025-12-01

### Added
- LazyToolRegistry for deferred tool resolution with on-demand loading
- FontManager for centralized UI typography with platform-specific font selection
- TTLCache automatic cleanup to prevent memory bloat in long-running processes
- Comprehensive tests for code quality improvements

### Changed
- Integrated v2 Swiss knife logo and icon across all platforms
- Updated logo aspect ratio in main menu widget for better visual balance

### Performance
- Lazy configuration loading with pre-compiled regex patterns in security module
- O(1) bounded statistics storage using deque in profiling module
- TTLCache now automatically cleans up expired entries every 60 seconds

### Fixed
- Replaced bare except clauses with specific OSError handling in file_utils

### Infrastructure
- Removed debug builds from all platforms for cleaner release artifacts

## [0.5.3] - 2025-11-25

### Added
- Application SVG logo asset with animated rendering
- Hero banner with animated logo to main menu

### Changed
- Enhanced dynamic theme integration across widgets
- All build scripts now install package in editable mode before building executables
- Simplified PyInstaller entry point by removing runtime path manipulation
- All PyInstaller spec files now use `collect_all()` for comprehensive package bundling

### Fixed
- **Critical**: Series of PyInstaller bundling issues causing executable failures across all platforms:
  - Missing `annotation_toolkit` package module
    - Root cause: Package not installed before PyInstaller build
    - Solution: Build scripts now run `pip install -e .` before building
    - Removed broken path manipulation in `build_app.py` that failed when frozen
  - Missing standard library modules (json, xml, webbrowser, and 40+ others)
    - Root cause: PyInstaller's `collect_all()` interfered with automatic stdlib detection
    - Solution: Added comprehensive explicit hiddenimports for all stdlib modules used in codebase
    - Includes: argparse, asyncio, atexit, collections, copy, datetime, enum, functools, hashlib, html, inspect, io, json, logging, math, os, pathlib, re, shutil, statistics, sys, tempfile, threading, time, traceback, typing, urllib, uuid, weakref, webbrowser, xml, and more
  - Missing `PyQt5.QtSvg` module
    - Root cause: SVG logo feature added but PyQt5.QtSvg dependency not included in build config
    - Solution: Added PyQt5.QtSvg to hiddenimports in all 6 spec files
  - Also added external dependency: chardet
- All built executables (Windows .exe, macOS .app, Linux binary) now work correctly with full functionality

### Infrastructure
- Enhanced PyInstaller spec files with proper package collection for reliable builds
- Improved build consistency across Windows, macOS, and Linux platforms
- Comprehensive hiddenimports prevent future missing module errors

## [0.5.1] - 2025-01-18

### Changed
- Reorganized UI components for better code organization:
  * Moved PlainTextEdit and PlainLineEdit from widgets to components
  * Extracted DraggableFieldFrame as a reusable component with callback pattern
- Removed unused Config imports from conversation generator and text collector widgets

### Fixed
- Python 3.8 compatibility issue with Union types in DI exceptions
- Test expectations updated for renamed "URL Dictionary to Clickables" tool
- JSON fixer logging now prevents duplicate handlers and handles cross-platform log directories
- JSON fixer logging fallback improved for AppImage and restricted environments

### Removed
- Duplicate json_fixer.py from widgets directory (canonical version is in utils/json/fixer.py)

## [0.5.0] - 2025-01-18

### Added
- Copy JSON to clipboard button in conversation preview with character count confirmation
- Comprehensive test coverage for DI system, adapters, CLI, GUI utilities, and XML formatter
- Theme-aware color support for GlassButton component

### Changed
- Renamed "Dictionary to Bullet List" tool to "URL Dictionary to Clickables" for clarity
- Updated documentation to use generic corporate terminology for broader applicability
- Updated JSON parser patterns to use generic AI terminology
- Reduced UI component sizes for more compact, space-efficient layout:
  * Tool cards: 400x280 → 340x240
  * Grid spacing: 20 → 14
  * Section headers: 20pt → 16pt
  * Title: 36pt → 28pt
- GlassButton now uses theme colors instead of hardcoded values

### Fixed
- Text spacing and rendering issues across all UI components caused by Qt font system
- Auto-save backup rotation race condition (now rotates before saving)
- JSON cleaner regex to properly handle multi-line JSON with DOTALL flag
- Undo/redo cleanChanged signal emission using intermediary method
- XML formatter regex by removing unnecessary DOTALL flags

### Removed
- Problematic custom placeholder text implementation (55 lines) that interfered with Qt behavior

### Infrastructure
- Updated macOS bundle identifiers to vendor-neutral format
- Added uv.lock to gitignore
- Removed unused image file from docs
- Added 17 new test files with 6,221 lines of test coverage

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
[Unreleased]: https://github.com/9scorp4/annotator-swiss-knife/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.6.0
[0.5.3]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.5.3
[0.5.2-beta.3]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.5.2-beta.3
[0.5.2-beta.2]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.5.2-beta.2
[0.5.2-beta.1]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.5.2-beta.1
[0.5.1]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.5.1
[0.5.0]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.5.0
[0.4.0]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.4.0
[0.3.0]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.3.0
[0.2.0]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.2.0
[0.1.0]: https://github.com/9scorp4/annotator-swiss-knife/releases/tag/v0.1.0
