"""
Functions to preprocess math equations.
"""
from __future__ import annotations

import re

from sympy import sympify


def process_math_equations(text: str) -> str:
    """Detects LaTeX-style math symbols and converts them to a readable format.

    Args:
        text (str): LaTeX-style math equations to process.

    Returns:
        str: Processed LaTeX-style math equations.
    """

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
