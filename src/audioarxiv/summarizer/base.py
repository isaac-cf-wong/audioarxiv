from __future__ import annotations

from abc import ABC, abstractmethod


class Summarizer(ABC):
    """Abstract base class for summarizers.
    """
    @abstractmethod
    def summarize(self, text: str, max_length: int = 150) -> str:
        """Summarize the input text.

        Args:
            text (str): Text to summarize (e.g., abstract or full paper)
            max_length (int, optional): Approximate maximum length of the summary in words. Defaults to 150.

        Returns:
            str: Summarized text.
        """
        pass
