"""A tiny demo package. This file runs once, on the first `import geometry`."""

from .shapes import Circle, Rectangle
from .utils import total_area

__all__ = ["Circle", "Rectangle", "total_area"]
__version__ = "1.0.0"

print(f"(geometry package imported from {__name__})")   # shows the module runs exactly once
