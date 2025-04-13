"""
Utility functions.

Submodules:
-----------
- log: Functions for logging.
"""
from __future__ import annotations

from .log import logger, setup_logger

setup_logger(logger)

__all__ = [
    'logger',
    'setup_logger',
]
