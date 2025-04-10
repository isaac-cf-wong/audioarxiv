"""
audioarxiv: A python package to let you fetch the research papers from arXiv and read them aloud.

This package provides tools to:
- Fetch research papers from arXiv
- Preprocess the articles for better audio rendering

Submodules:
-----------
- audio: Core audio generation and playback utilities
- preprocess: Text and paper preprocessing functions
- resources: Paper models and utilities for paper handling

Usage example:
--------------
$ audioarxiv --id <arxiv-id>
"""
from __future__ import annotations

from . import audio  # noqa: F401  # pylint: disable=unused-import
from . import preprocess  # noqa: F401  # pylint: disable=unused-import
from . import resources  # noqa: F401  # pylint: disable=unused-import
from .utils import logger, setup_logger

__version__ = "0.1.0"

setup_logger(logger)
