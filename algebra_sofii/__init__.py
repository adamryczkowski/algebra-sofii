"""
Algebra equation generator for 12-year-old students.
"""

from .complications import (
    Complication,
    AddZeroComplication,
    MultiplyByOneComplication,
    InsertBracketsComplication,
    NegateComplication,
    InvertComplication,
    AddToEquationComplication,
    MultiplyEquationComplication,
    EquationWithSolution,
    EXPRESSION_COMPLICATION_WEIGHTS,
    EQUATION_COMPLICATION_WEIGHTS,
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
from .generators import random_expression

__all__ = [
    # Complications
    "Complication",
    "AddZeroComplication",
    "MultiplyByOneComplication",
    "InsertBracketsComplication",
    "NegateComplication",
    "InvertComplication",
    "AddToEquationComplication",
    "MultiplyEquationComplication",
    "EquationWithSolution",
    "EXPRESSION_COMPLICATION_WEIGHTS",
    "EQUATION_COMPLICATION_WEIGHTS",
    # Expressions
    "Addition",
    "ChangedSign",
    "Equals",
    "Expression",
    "ExpressionIndex",
    "Integer",
    "Inverted",
    "Multiplication",
    "Unknown",
    # Generators
    "random_expression",
]
