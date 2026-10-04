"""
Text cleaning and normalization module for agricultural documents.
"""

import re
import unicodedata


class TextCleaner:
    """Provides sanitization, unicode normalization, and formatting for extracted agricultural text."""

    @staticmethod
    def clean(text: str) -> str:
        """
        Cleans raw extracted text:
        - Normalizes Unicode characters (NFKC)
        - Normalizes bullet points and dashes
        - Cleans excessive whitespace and trailing lines
        - Joins broken hyphenated words across lines
        """
        if not text:
            return ""

        # Normalize Unicode
        text = unicodedata.normalize("NFKC", text)

        # Fix hyphenated words broken across linebreaks (e.g. "Rhizoc-\ntonia")
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Standardize bullet markers
        text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219]', '•', text)

        # Replace multiple spaces/tabs with single space (preserve intentional linebreaks)
        lines = []
        for line in text.split("\n"):
            cleaned_line = re.sub(r'[ \t]+', ' ', line).strip()
            if cleaned_line:
                lines.append(cleaned_line)

        return "\n".join(lines)

    @staticmethod
    def clean_query(query: str) -> str:
        """Clean a search or retrieval query string."""
        if not query:
            return ""
        q = unicodedata.normalize("NFKC", query)
        q = re.sub(r'[^\w\s\-\.\,\%]', ' ', q)
        return re.sub(r'\s+', ' ', q).strip()
