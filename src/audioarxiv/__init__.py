#   -------------------------------------------------------------
#   Copyright (c) Microsoft Corporation. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
"""Python Package Template"""
from __future__ import annotations

from . import audio, preprocess, resources

__version__ = "0.1.0"


def get_version_information() -> str:
    """Version information.

    Returns:
        str: Version information.
    """
    return __version__


__all__ = [
    'audio',
    'preprocess',
    'resources',
    'get_version_information',
]
