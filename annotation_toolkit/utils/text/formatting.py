"""
Text formatting utilities for the annotation toolkit.

This module provides functions for formatting text data in various ways.
"""

import re
import urllib.parse
import urllib.request
from typing import Dict, Optional


def dict_to_bullet_list(data: Dict[str, str], as_markdown: bool = True) -> str:
    """
    Convert a dictionary to a bullet list string.

    Args:
        data: Dictionary with string keys and values.
        as_markdown: Whether to format URLs as markdown links.

    Returns:
        A bullet list representation of the dictionary.
    """
    result = []

    for key, value in data.items():
        # Check if value is a URL
        is_url = value.startswith(("http://", "https://"))

        if is_url and as_markdown:
            # For URLs in markdown mode, create a markdown link
            title = extract_url_title(value)
            result.append(f"- **{key}**: [{title}]({value})")
        else:
            # For non-URLs or plain text mode, just show the value
            result.append(f"- **{key}**: {value}")

    return "\n".join(result)


def extract_url_title(url: str) -> str:
    """
    Extract the title from a URL.

    This function attempts to fetch the webpage and extract its title.
    If it fails, it returns a formatted version of the URL.

    Args:
        url: The URL to extract the title from.

    Returns:
        The title of the webpage or a formatted URL.
    """
    try:
        # Try to fetch the webpage
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=3) as response:
            html = response.read().decode("utf-8")

        # Extract the title using a regular expression
        title_match = re.search(
            r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL
        )
        if title_match:
            title = title_match.group(1).strip()
            # Limit the title length
            if len(title) > 50:
                title = title[:50] + "..."
            return title
    except Exception:
        # If anything goes wrong, fall back to formatting the URL
        pass

    # Format the URL as a fallback
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    # Remove www. prefix if present
    if domain.startswith("www."):
        domain = domain[4:]

    # Format the path
    if path and path != "/":
        # Remove trailing slash
        if path.endswith("/"):
            path = path[:-1]
        # Get the last part of the path
        path_parts = path.split("/")
        last_part = path_parts[-1]
        # Replace hyphens and underscores with spaces
        last_part = last_part.replace("-", " ").replace("_", " ")
        # Capitalize words
        last_part = " ".join(word.capitalize() for word in last_part.split())
        return f"{domain}: {last_part}"
    else:
        # Just use the domain if there's no meaningful path
        return domain
