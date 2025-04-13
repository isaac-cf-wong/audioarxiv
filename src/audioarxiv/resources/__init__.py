"""
This subpackage provides functions to fetch research articles from arXiv.

Submodules:
-----------
- paper: A Paper class to provide a user-friendly interface to fetch research articles from arXiv.
"""
from __future__ import annotations

from .paper import Paper

__all__ = [
    'Paper',
]
