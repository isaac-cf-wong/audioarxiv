"""
This subpackage provides functions to preprocess articles for better audio rendering.

Submodules:
-----------
- article: Text and preprocessing functions
- math_equation: Math equation preprocessing functions
"""
from __future__ import annotations

from .article import \
    get_sentences  # noqa: F401  # pylint: disable=unused-import
from .math_equation import \
    process_math_equations  # noqa: F401  # pylint: disable=unused-import
