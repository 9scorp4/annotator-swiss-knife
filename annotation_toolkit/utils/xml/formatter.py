"""
XML formatting utilities.

This module provides functions for formatting and processing XML content
within JSON and other text formats.
"""

import re
import json
from typing import Any, Dict, List, Optional, Tuple
from html import escape, unescape

from ..logger import get_logger

logger = get_logger()


class XmlFormatter:
    """Formatter for XML content within various contexts."""

    def __init__(self, indent_size: int = 4, max_line_length: int = 120):
        """
        Initialize the XML formatter.

        Args:
            indent_size: Number of spaces for indentation.
            max_line_length: Maximum line length before wrapping.
        """
        self.indent_size = indent_size
        self.max_line_length = max_line_length
        self._tag_pattern = re.compile(
            r'(<([A-Za-z_][A-Za-z0-9_]*)>)(.*?)(</\2>)',
            re.DOTALL
        )
        self._single_tag_pattern = re.compile(r'</?[A-Za-z_][A-Za-z0-9_]*>')

    def format_xml_in_text(self, text: str, preserve_quotes: bool = True) -> str:
        """
        Format XML tags in plain text for display.

        Args:
            text: The text containing XML tags.
            preserve_quotes: Whether to preserve quotes around the text.

        Returns:
            Formatted text with structured XML tags.
        """
        logger.debug(f"Formatting XML in text (length: {len(text)})")

        # Handle quoted strings
        if preserve_quotes and text.startswith('"') and text.endswith('"'):
            # Process the content inside quotes
            inner_text = text[1:-1]
            formatted_inner = self._format_xml_content(inner_text)
            return f'"{formatted_inner}"'

        return self._format_xml_content(text)

    def format_xml_in_html(self, text: str) -> str:
        """
        Format XML tags for HTML display with syntax highlighting.

        Args:
            text: The text containing XML tags.

        Returns:
            HTML-formatted string with highlighted XML tags.
        """
        logger.debug("Formatting XML for HTML display")

        def format_xml_block(match):
            open_tag = match.group(1)
            tag_name = match.group(2)
            content = match.group(3)
            close_tag = match.group(4)

            # Escape HTML entities
            open_tag = escape(open_tag)
            close_tag = escape(close_tag)
            content = escape(content)

            # Format with HTML styling
            formatted = f'''<pre style="margin: 0; padding: 0;">
<span style="color: #9c27b0; font-weight: bold;">{open_tag}</span>
        {content}
<span style="color: #9c27b0; font-weight: bold;">{close_tag}</span>
</pre>'''
            return formatted

        # Process XML tag pairs
        formatted = re.sub(self._tag_pattern, format_xml_block, text, flags=re.DOTALL)

        # Handle remaining individual tags
        formatted = re.sub(
            self._single_tag_pattern,
            lambda m: f'<span style="color: #9c27b0; font-weight: bold;">{escape(m.group(0))}</span>',
            formatted
        )

        return formatted

    def format_xml_in_json(self, text: str) -> str:
        """
        Format XML tags within JSON strings.

        Args:
            text: The text containing XML tags.

        Returns:
            JSON-safe formatted string.
        """
        logger.debug("Formatting XML for JSON")

        # Escape the text first
        escaped_text = text.replace('"', '\\"')

        def format_xml_block(match):
            open_tag = match.group(1)
            content = match.group(3)
            close_tag = match.group(4)

            # Format with explicit newlines and indentation
            indent = ' ' * self.indent_size
            formatted = f"\\n{open_tag}\\n{indent}{content}\\n{close_tag}"
            return formatted

        # Replace each XML block with formatted version
        formatted_text = re.sub(
            self._tag_pattern,
            format_xml_block,
            escaped_text,
            flags=re.DOTALL
        )

        return f'"{formatted_text}"'

    def _format_xml_content(self, text: str) -> str:
        """
        Internal method to format XML content.

        Args:
            text: The text to format.

        Returns:
            Formatted text.
        """
        # Find all XML tag pairs
        def format_block(match):
            open_tag = match.group(1)
            content = match.group(3).strip()
            close_tag = match.group(4)

            # Format based on content length
            if len(content) > self.max_line_length:
                # Multi-line format for long content
                indent = ' ' * self.indent_size
                lines = self._wrap_text(content, self.max_line_length - self.indent_size)
                formatted_content = f'\n{indent}'.join(lines)
                return f"{open_tag}\n{indent}{formatted_content}\n{close_tag}"
            else:
                # Single line for short content
                return f"{open_tag}{content}{close_tag}"

        return re.sub(self._tag_pattern, format_block, text, flags=re.DOTALL)

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """
        Wrap text to specified width.

        Args:
            text: Text to wrap.
            max_width: Maximum line width.

        Returns:
            List of wrapped lines.
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)

            if current_length + word_length + len(current_line) <= max_width:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def validate_xml_tags(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validate that XML tags are properly paired.

        Args:
            text: Text containing XML tags.

        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        errors = []
        tag_stack = []

        # Find all tags
        tag_pattern = re.compile(r'<(/?)([A-Za-z_][A-Za-z0-9_]*)>')

        for match in tag_pattern.finditer(text):
            is_closing = match.group(1) == '/'
            tag_name = match.group(2)

            if is_closing:
                if not tag_stack:
                    errors.append(f"Closing tag </{tag_name}> without opening tag")
                elif tag_stack[-1] != tag_name:
                    errors.append(
                        f"Mismatched tags: expected </{tag_stack[-1]}>, found </{tag_name}>"
                    )
                else:
                    tag_stack.pop()
            else:
                tag_stack.append(tag_name)

        # Check for unclosed tags
        for tag in tag_stack:
            errors.append(f"Unclosed tag: <{tag}>")

        is_valid = len(errors) == 0
        return is_valid, errors

    def extract_xml_content(self, text: str) -> List[Dict[str, str]]:
        """
        Extract XML tag content from text.

        Args:
            text: Text containing XML tags.

        Returns:
            List of dictionaries with tag_name and content.
        """
        results = []

        for match in self._tag_pattern.finditer(text):
            tag_name = match.group(2)
            content = match.group(3).strip()
            results.append({
                'tag_name': tag_name,
                'content': content,
                'full_match': match.group(0)
            })

        return results


def format_xml_tags(text: str, output_format: str = 'text',
                   indent_size: int = 4) -> str:
    """
    Convenience function to format XML tags.

    Args:
        text: Text containing XML tags.
        output_format: Output format ('text', 'html', 'json').
        indent_size: Indentation size.

    Returns:
        Formatted text.
    """
    formatter = XmlFormatter(indent_size=indent_size)

    if output_format == 'html':
        return formatter.format_xml_in_html(text)
    elif output_format == 'json':
        return formatter.format_xml_in_json(text)
    else:
        return formatter.format_xml_in_text(text)


def parse_xml_content(text: str) -> List[Dict[str, str]]:
    """
    Parse and extract XML content from text.

    Args:
        text: Text containing XML tags.

    Returns:
        List of parsed XML elements.
    """
    formatter = XmlFormatter()
    return formatter.extract_xml_content(text)