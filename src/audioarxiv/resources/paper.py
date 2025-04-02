from __future__ import annotations

import re
import tempfile
from datetime import datetime

import arxiv
import fitz
from sympy import sympify


def process_math_equations(text):
    """Detects LaTeX-style math symbols and converts them to a readable format."""

    math_patterns = [r"\$(.*?)\$", r"\$\$(.*?)\$\$"]  # Inline and block math

    for pattern in math_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                readable_expr = sympify(match).srepr()  # Convert LaTeX to readable
                text = text.replace(f"${match}$", f"Math: {readable_expr}")
            except Exception:
                text = text.replace(f"${match}$", f"Equation: {match}")  # Fallback

    return text


class Paper:
    def __init__(self,
                 arxiv_id: str,
                 page_size: int = 100,
                 delay_seconds: float = 3.0,
                 num_retries: int = 3):
        """An arXiv paper.

        Args:
            arxiv_id (str): The arXiv ID.
            page_size (int, optional): Maximum number of results fetched in a single API request. Smaller pages can
            be retrieved faster, but may require more round-trips. The API's limit is 2000 results per page.
            Defaults to 100.
            delay_seconds (float, optional): Number of seconds to wait between API requests.
            [arXiv's Terms of Use](https://arxiv.org/help/api/tou) ask that you "make no
            more than one request every three seconds."
            Defaults to 3.0.
            num_retries (int, optional): Number of times to retry a failing API request before raising an Exception.
            Defaults to 3.
        """
        client = arxiv.Client(page_size=page_size,
                                   delay_seconds=delay_seconds,
                                   num_retries=num_retries)
        self.paper = next(client.results(arxiv.Search(id_list=[arxiv_id])))
        self._sections = []

    @property
    def title(self) -> str:
        """Title of the paper.

        Returns:
            str: Title of the paper.
        """
        return self.paper.title

    @property
    def abstract(self) -> str:
        """Abstract.

        Returns:
            str: Abstract.
        """
        return self.paper.summary

    @property
    def authors(self) -> list:
        """List of authors.

        Returns:
            list: List of authors.
        """
        return [author.name for author in self.paper.authors]

    @property
    def published(self) -> datetime:
        """Published date.

        Returns:
            datetime: Published date.
        """
        return self.paper.published

    @property
    def updated(self) -> datetime:
        """Updated date.

        Returns:
            datetime: Updated date.
        """
        return self.paper.updated

    def download_pdf(self,
                     dirpath: str = './',
                     filename: str = '') -> str:
        """Download the PDF.

        Args:
            dirpath (str, optional): Path to the directory. Defaults to './'.
            filename (str, optional): Name of the file. Defaults to ''.

        Returns:
            str: Path of the output PDF.
        """
        return self.paper.download_pdf(dirpath=dirpath, filename=filename)

    @property
    def sections(self) -> list:
        if len(self._sections) == 0:
            with tempfile.NamedTemporaryFile() as tmp:
                filename = tmp.name
                self.download_pdf(filename=filename)

                doc = fitz.open(filename)

                current_section = {"header": None, "content": []}

                for page in doc:
                    blocks = page.get_text("blocks")  # Extract text blocks

                    for block in blocks:
                        text = block[4].strip()

                        # Detect section headers using common patterns (uppercase, numbered, bold)
                        if (text.isupper() or
                            re.match(r"^\d+(\.\d+)*\s+\w+", text) or
                            text.endswith(":")):

                            # Store previous section before switching
                            if current_section["header"] or current_section["content"]:
                                self._sections.append(current_section)

                            current_section = {"header": text, "content": []}  # New section
                        else:
                            # Process math expressions
                            text = process_math_equations(text)
                            current_section["content"].append(text)

                # Append the last section
                if current_section["header"] or current_section["content"]:
                    self._sections.append(current_section)

        return self._sections


if __name__ == '__main__':
    paper = Paper('2503.22919')

    import pyttsx3

    engine = pyttsx3.init()
    engine.say('I am reading a paper.')
    engine.say('I am reading another paper.')
    engine.runAndWait()
    engine.stop()
