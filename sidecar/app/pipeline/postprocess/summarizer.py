"""Text summarization utilities."""

from typing import List, Optional


class Summarizer:
    """Generate summaries at different abstraction levels."""

    def __init__(self, max_length: int = 150):
        """
        Initialize summarizer.

        Args:
            max_length: Maximum summary length in words
        """
        self.max_length = max_length

    def summarize_block(self, text: str) -> str:
        """
        Generate a concise summary of a text block.

        Args:
            text: Input text

        Returns:
            Summary string
        """
        # Simple extractive summary: first N words
        words = text.split()
        if len(words) <= self.max_length:
            return text
        return " ".join(words[: self.max_length]) + "..."

    def summarize_page(self, blocks: List[str]) -> str:
        """
        Generate a page-level summary.

        Args:
            blocks: List of text blocks

        Returns:
            Page summary
        """
        # Combine blocks and summarize
        full_text = " ".join(blocks)
        return self.summarize_block(full_text)

    def summarize_document(
        self,
        pages: List[str],
        level: str = "L1",
    ) -> str:
        """
        Generate a document-level summary.

        Args:
            pages: List of page texts
            level: Summary level (L1-L3)

        Returns:
            Document summary
        """
        # Adjust length based on level
        length_map = {
            "L1": self.max_length,
            "L2": self.max_length // 2,
            "L3": self.max_length // 4,
        }

        target_length = length_map.get(level, self.max_length)
        full_text = " ".join(pages)
        words = full_text.split()

        if len(words) <= target_length:
            return full_text
        return " ".join(words[:target_length]) + "..."

    def extract_key_sentences(
        self,
        text: str,
        num_sentences: int = 3,
    ) -> List[str]:
        """
        Extract key sentences from text.

        Args:
            text: Input text
            num_sentences: Number of sentences to extract

        Returns:
            List of key sentences
        """
        # Simple approach: take first N sentences
        sentences = text.replace("!", ".").replace("?", ".").split(".")
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences[:num_sentences]
