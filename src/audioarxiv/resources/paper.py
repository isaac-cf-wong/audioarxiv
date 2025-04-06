from __future__ import annotations

import re
import tempfile
from datetime import datetime
from typing import Union

import arxiv
import fitz


class Paper:
    def __init__(self,
                 page_size: int = 100,
                 delay_seconds: float = 3.0,
                 num_retries: int = 3):
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
        """
        self.page_size = page_size
        self.delay_seconds = delay_seconds
        self.num_retries = num_retries
        self._client = None
        self._sections = []

    @property
    def page_size(self) -> int:
        """Get the page size.

        Returns:
            int: Page size.
        """
        return self._page_size

    @page_size.setter
    def page_size(self, value: int):
        """Set the page size.

        Args:
            value (int): Page size.

        Raises:
            ValueError: value has to be int.
        """
        if not isinstance(value, int):
            raise ValueError(f'value = {value} ({type(value)}) has to be int.')
        self._page_size = value
        self._client = None

    @property
    def delay_seconds(self) -> float:
        """Get the delay in seconds.

        Returns:
            float: Delay in seconds.
        """
        return self._delay_seconds

    @delay_seconds.setter
    def delay_seconds(self, value: int | float):
        """Set the delay in seconds.

        Args:
            value (Union[int, float]): Delay in seconds.
        """
        if not isinstance(value, int):
            if not isinstance(value, float):
                raise ValueError(f'value = {value} ({type(value)}) has to be int or float.')
        self._delay_seconds = value
        self._client = None

    @property
    def num_retries(self) -> int:
        """Get the number of retries.

        Returns:
            int: Number of retries.
        """
        return self._num_retries

    @num_retries.setter
    def num_retries(self, value: int):
        """Set the number of retries.

        Args:
            value (int): Number of retries.

        Raises:
            ValueError: value has to be int.
        """
        if not isinstance(value, int):
            raise ValueError(f'value = {value} ({type(value)}) has to be int.')
        self._num_retries = value
        self._client

    @property
    def settings(self) -> dict:
        """Get the settings of the client.

        Returns:
            dict: Settings of the client.
        """
        return {'page_size': self.page_size,
                'delay_seconds': self.delay_seconds,
                'num_retries': self.num_retries}

    @settings.setter
    def settings(self, values: dict):
        """Set the client settings.

        Args:
            values (dict): A dictionary of the settings for the client.

        Raises:
            ValueError: values has to be dict.
        """
        if not isinstance(values, dict):
            raise ValueError(f'values = {values} ({type(values)}) has to be dict.')
        for prop in ['page_size', 'delay_seconds', 'num_retries']:
            if prop in values:
                setattr(self, prop, values[prop])

    @property
    def client(self) -> arxiv.Client:
        """Get the arxiv client.

        Returns:
            arxiv.Client: arxiv client.
        """
        if self._client is None:
            self._client = arxiv.Client(page_size=self.page_size,
                                        delay_seconds=self.delay_seconds,
                                        num_retries=self.num_retries)
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
