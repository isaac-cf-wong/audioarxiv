"""
This subpackage

Submodules:
-----------
- base: An Audio class to render the text into audio, using pyttsx3 as the backend.
"""
from __future__ import annotations

from . import base
from .base import Audio

__all__ = [
    'base',
    'Audio',
]
