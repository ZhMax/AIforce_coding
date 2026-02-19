"""
Utility functions for bot testing
"""

import re


def regex_to_sample_message(pattern: str) -> str:
    """
    Convert a regex pattern into a concrete sample message for testing.

    This is a best-effort conversion for common chatbot patterns.

    Args:
        pattern: Regex pattern from a match edge

    Returns:
        A concrete message string that should match the pattern

    Examples:
        >>> regex_to_sample_message("/start|начать|привет")
        '/start'
        >>> regex_to_sample_message("^help$")
        'help'
        >>> regex_to_sample_message("test.*value")
        'test value'
    """
    if not pattern:
        return "test"

    # Take first alternative if multiple options (e.g., "a|b|c" -> "a")
    if "|" in pattern:
        pattern = pattern.split("|")[0]

    # Strip anchors
    pattern = pattern.lstrip("^").rstrip("$")

    # Replace common regex patterns with literals
    replacements = [
        (r"\s+", " "),      # whitespace -> space
        (r"\s*", " "),      # optional whitespace -> space
        (r"\.+", " "),      # one or more any char -> space
        (r"\.\*", " "),     # zero or more any char -> space
        (r"\\d+", "1"),     # one or more digits -> "1"
        (r"\\d\*", "1"),    # zero or more digits -> "1"
        (r"\\w+", "a"),     # one or more word chars -> "a"
        (r"\\w\*", "a"),    # zero or more word chars -> "a"
    ]

    for regex_pat, replacement in replacements:
        pattern = re.sub(regex_pat, replacement, pattern)

    # Remove remaining regex special chars (but keep the text)
    pattern = pattern.replace("\\", "")

    # Clean up multiple spaces
    pattern = " ".join(pattern.split())

    # If pattern is still empty or just whitespace, use default
    if not pattern.strip():
        return "test"

    return pattern.strip()
