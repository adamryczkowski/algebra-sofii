"""
Algebra equation generator for 12-year-old students.
"""

from .complications import (
    Complication,
    EquationComplication,
    EquationElementMove,
    EquationWithSolution,
    ExpressionComplication,
)
from .expressions import (
    Addition,
    ChangedSign,
    Equals,
    Expression,
    ExpressionIndex,
    Integer,
    Inverted,
    Multiplication,
    Unknown,
)
from .generators import random_expression, random_nonzero_expression

__version__ = "0.1.0"
__all__ = [
    "Expression",
    "Integer",
    "Unknown",
    "Addition",
    "Multiplication",
    "ChangedSign",
    "Inverted",
    "Equals",
    "ExpressionIndex",
    "random_expression",
    "random_nonzero_expression",
    "Complication",
    "ExpressionComplication",
    "EquationComplication",
    "EquationElementMove",
    "EquationWithSolution",
]
