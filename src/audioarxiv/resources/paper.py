"""
A class to fetch papers from arXiv.
"""
from __future__ import annotations

import re
import tempfile
from datetime import datetime

import arxiv
import fitz


def validate_paper_arguments(paper_size: int,
                             delay_seconds: float,
                             num_retries: int) -> dict:
    """Validate the arguments for Paper.

    Args:
        page_size (int, optional): Maximum number of results fetched in a single API request. Smaller pages can
        be retrieved faster, but may require more round-trips. The API's limit is 2000 results per page.
        Defaults to 100.
        delay_seconds (float, optional): Number of seconds to wait between API requests.
        [arXiv's Terms of Use](https://arxiv.org/help/api/tou) ask that you "make no
        more than one request every three seconds."
        Defaults to 3.0.
        num_retries (int, optional): Number of times to retry a failing API request before raising an Exception.
        Defaults to 3.

    Returns:
        dict: paper_size, delay_seconds, num_retries
    """
    return {'paper_size': paper_size,
            'delay_seconds': delay_seconds,
            'num_retries': num_retries}


class Paper:
    """A class to fetch papers from arXiv.
    """
    def __init__(self,
                 page_size: int = 100,
                 delay_seconds: float = 3.0,
                 num_retries: int = 3,
                 validate_arguments: bool = True):
        """An arXiv paper.

        Args:
            page_size (int, optional): Maximum number of results fetched in a single API request. Smaller pages can
            be retrieved faster, but may require more round-trips. The API's limit is 2000 results per page.
            Defaults to 100.
            delay_seconds (float, optional): Number of seconds to wait between API requests.
            [arXiv's Terms of Use](https://arxiv.org/help/api/tou) ask that you "make no
            more than one request every three seconds."
            Defaults to 3.0.
            num_retries (int, optional): Number of times to retry a failing API request before raising an Exception.
            Defaults to 3.
            validate_arguments (bool, optional): If True, validate the arguments. Defaults to True.
        """
        if validate_arguments:
            arguments = validate_paper_arguments(paper_size=page_size,
                                                 delay_seconds=delay_seconds,
                                                 num_retries=num_retries)
            page_size = arguments['paper_size']
            delay_seconds = arguments['delay_seconds']
            num_retries = arguments['num_retries']
        self._client = arxiv.Client(page_size=page_size,
                                    delay_seconds=delay_seconds,
                                    num_retries=num_retries)
        self._sections = []

    @property
    def client(self) -> arxiv.Client:
        """Get the arxiv client.

        Returns:
            arxiv.Client: arxiv client.
        """
        return self._client

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

    def search_by_arxiv_id(self, arxiv_id: str):
        """Search paper by arXiv ID.

        Args:
            arxiv_id (str): arXiv ID.
        """
        self.paper = next(self.client.results(arxiv.Search(id_list=[arxiv_id])))

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
        """Get the sections of the paper.

        Returns:
            list: A list of sections. Each section is a dict with the header as the key and the content as the value.
        """
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
                        if (text.isupper() or re.match(r"^\d+(\.\d+)*\s+\w+", text) or text.endswith(":")):

                            # Store previous section before switching
                            if current_section["header"] or current_section["content"]:
                                self._sections.append(current_section)

                            current_section = {"header": text, "content": []}  # New section
                        else:
                            current_section["content"].append(text)

                # Append the last section
                if current_section["header"] or current_section["content"]:
                    self._sections.append(current_section)

        return self._sections
