from __future__ import annotations

import logging

from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer

from .base import Summarizer

logger = logging.getLogger('audioarxiv')


class SumySummarizer(Summarizer):
    """A sumy summarizer."""
    def __init__(self, algorithm: str = 'TextRank'):
        """Sumy summarizer.

        Args:
            algorithm (str, optional): Algorithm to use.
                Supported algorithms: ["TextRank", "LexRank", "Lsa", "Luhn"].
                Defaults to 'TextRank'.
        """
        match algorithm:
            case 'TextRank':
                self.summarizer_cls = TextRankSummarizer
            case 'LexRank':
                self.summarizer_cls = LexRankSummarizer
            case 'Lsa':
                self.summarizer_cls = LsaSummarizer
            case 'Luhn':
                self.summarizer_cls = LuhnSummarizer
            case _:
                logger.warning(f'sumy algorithm = {algorithm} is not recognized.')
                logger.warning('Supported algorithms: ["TextRank", "LexRank", "Lsa", "Luhn"].')
                logger.warning('The summarizer is set to be the default TextRankSummarizer.')
                self.summarizer_cls = TextRankSummarizer

    def summarize(self, text: str, max_length: int = 150) -> str:
        """Summarize the input text.

        Args:
            text (str): Text to summarize (e.g., abstract or full paper)
            max_length (int, optional): Approximate maximum length of the summary in words. Defaults to 150.

        Returns:
            str: Summarized text.
        """
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = self.summarizer_cls()
        sentence_count = max(1, max_length // 15)
        sentences = summarizer(parser.document, sentence_count)
        return " ".join(str(sentence) for sentence in sentences)
