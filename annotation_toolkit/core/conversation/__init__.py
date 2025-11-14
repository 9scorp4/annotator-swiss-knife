"""
Conversation module for the Annotation Toolkit.

This package provides tools for visualizing and formatting conversation data from various formats.
It includes functionality to display, search, and analyze conversation structures, as well as
generating new conversation JSON from user input.
"""

from .generator import ConversationGenerator
from .visualizer import JsonVisualizer

__all__ = ["ConversationGenerator", "JsonVisualizer"]
