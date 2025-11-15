"""
Annotation Toolkit - A comprehensive yet simple toolkit designed to streamline various data annotation tasks.

This package integrates multiple annotation tools into a cohesive application with proper architecture,
making it more maintainable, extensible, and user-friendly.

Features:
- Dictionary to Bullet List: Convert dictionaries with URLs to formatted bullet lists with hyperlinks
- Conversation Visualizer: Visualize and format conversation data from JSON or text formats
"""

# Version is managed by setuptools-scm and derived from git tags
try:
    from ._version import __version__
except ImportError:
    # Fallback for development environments without proper installation
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            __version__ = version("annotation-toolkit")
        except PackageNotFoundError:
            __version__ = "0.0.0.dev0"
    except ImportError:
        # Python < 3.8 fallback
        __version__ = "0.0.0.dev0"
