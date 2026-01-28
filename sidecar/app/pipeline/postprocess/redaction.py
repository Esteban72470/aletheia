"""PII redaction utilities."""

import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class RedactionMatch:
    """A detected PII pattern."""

    type: str
    value: str
    start: int
    end: int
    replacement: str


class Redactor:
    """Detect and redact personally identifiable information (PII)."""

    # Common PII patterns
    PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b",
        "ssn": r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",
        "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    }

    # Replacement strings
    REPLACEMENTS = {
        "email": "[EMAIL]",
        "phone": "[PHONE]",
        "ssn": "[SSN]",
        "credit_card": "[CARD]",
        "ip_address": "[IP]",
    }

    def __init__(self, patterns: List[str] = None):
        """
        Initialize redactor.

        Args:
            patterns: List of pattern types to detect (default: all)
        """
        self.active_patterns = patterns or list(self.PATTERNS.keys())

    def detect(self, text: str) -> List[RedactionMatch]:
        """
        Detect PII patterns in text.

        Args:
            text: Input text

        Returns:
            List of detected PII matches
        """
        matches = []

        for pattern_type in self.active_patterns:
            pattern = self.PATTERNS.get(pattern_type)
            if not pattern:
                continue

            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(
                    RedactionMatch(
                        type=pattern_type,
                        value=match.group(),
                        start=match.start(),
                        end=match.end(),
                        replacement=self.REPLACEMENTS[pattern_type],
                    )
                )

        return sorted(matches, key=lambda m: m.start)

    def redact(self, text: str) -> Tuple[str, List[RedactionMatch]]:
        """
        Redact PII from text.

        Args:
            text: Input text

        Returns:
            Tuple of (redacted text, list of matches)
        """
        matches = self.detect(text)

        # Apply redactions in reverse order to preserve positions
        result = text
        for match in reversed(matches):
            result = result[: match.start] + match.replacement + result[match.end :]

        return result, matches

    def add_pattern(self, name: str, pattern: str, replacement: str):
        """
        Add a custom pattern.

        Args:
            name: Pattern name
            pattern: Regex pattern
            replacement: Replacement string
        """
        self.PATTERNS[name] = pattern
        self.REPLACEMENTS[name] = replacement
        if name not in self.active_patterns:
            self.active_patterns.append(name)
