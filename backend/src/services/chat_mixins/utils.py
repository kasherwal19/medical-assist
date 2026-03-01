"""
Utility functions for chat service.
"""

import re


def clean_text(text: str) -> str:
    """
    Remove markdown, bullets, headers, and formatting
    from clinical/scientific text for NLP processing.
    """
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"-{3,}", " ", text)
    text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
