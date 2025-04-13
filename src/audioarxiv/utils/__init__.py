"""
Utility functions.

Submodules:
-----------
- log: Functions for logging.
"""
from __future__ import annotations

import logging

from .log import setup_logger

logger = logging.getLogger('audioarxiv')
setup_logger(logger)

__all__ = [
    'logger',
    'setup_logger',
]
