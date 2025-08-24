"""
Complications package for generating complex algebraic equations.

This package contains individual complication classes that can be applied to
algebraic expressions and equations to make them more complex while preserving
their mathematical equivalence.
"""

# Import base class
from .base import Complication

# Import expression complications
from .add_zero import AddZeroComplication
from .multiply_by_one import MultiplyByOneComplication
from .insert_brackets import InsertBracketsComplication
from .negate import NegateComplication
from .invert import InvertComplication

# Import equation complications
from .add_to_equation import AddToEquationComplication
from .multiply_equation import MultiplyEquationComplication

# Import equation container
from .equation_with_solution import EquationWithSolution

# Import configuration
from .config import (
    EXPRESSION_COMPLICATION_WEIGHTS,
    EQUATION_COMPLICATION_WEIGHTS,
    COMPLICATION_CLASSES,
)

__all__ = [
    # Base class
    "Complication",
    # Expression complications
    "AddZeroComplication",
    "MultiplyByOneComplication",
    "InsertBracketsComplication",
    "NegateComplication",
    "InvertComplication",
    # Equation complications
    "AddToEquationComplication",
    "MultiplyEquationComplication",
    # Equation container
    "EquationWithSolution",
    # Configuration
    "EXPRESSION_COMPLICATION_WEIGHTS",
    "EQUATION_COMPLICATION_WEIGHTS",
    "COMPLICATION_CLASSES",
]
