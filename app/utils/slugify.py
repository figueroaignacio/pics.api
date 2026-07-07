"""Slug generation utility."""

import re
import unicodedata


def slugify(text: str) -> str:
    """
    Convert a text string into a URL-safe slug.

    Examples:
        >>> slugify("Torres del Paine")
        'torres-del-paine'
        >>> slugify("Café & Food!")
        'cafe-food'
    """
    # Normalise unicode → ASCII
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Lowercase
    text = text.lower()
    # Keep only alphanumeric, spaces, and hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    # Collapse whitespace / hyphens into a single hyphen
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")
