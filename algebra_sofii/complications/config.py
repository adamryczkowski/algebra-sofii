"""
Configuration for complication weights and class mappings.
"""

from typing import Dict, Type

# Import all complication classes
from .base import Complication
from .add_zero import AddZeroComplication
from .multiply_by_one import MultiplyByOneComplication
from .insert_brackets import InsertBracketsComplication
from .negate import NegateComplication
from .invert import InvertComplication
from .add_to_equation import AddToEquationComplication
from .multiply_equation import MultiplyEquationComplication


# Global dictionaries for complication weights
EXPRESSION_COMPLICATION_WEIGHTS: Dict[str, float] = {
    "AddZeroComplication": 2.0,
    "MultiplyByOneComplication": 2.0,
    "InsertBracketsComplication": 3.0,  # Higher weight since it's often applicable and low cost
    "NegateComplication": 1.0,
    "InvertComplication": 0.5,  # Lower weight due to potential for division issues
}

EQUATION_COMPLICATION_WEIGHTS: Dict[str, float] = {
    # Include all expression complications
    **EXPRESSION_COMPLICATION_WEIGHTS,
    # Add equation-specific complications
    "AddToEquationComplication": 2.5,
    "MultiplyEquationComplication": 1.5,  # Lower weight to avoid too many multiplications
}

# Mapping from names to classes
COMPLICATION_CLASSES: Dict[str, Type[Complication]] = {
    "AddZeroComplication": AddZeroComplication,
    "MultiplyByOneComplication": MultiplyByOneComplication,
    "InsertBracketsComplication": InsertBracketsComplication,
    "NegateComplication": NegateComplication,
    "InvertComplication": InvertComplication,
    "AddToEquationComplication": AddToEquationComplication,
    "MultiplyEquationComplication": MultiplyEquationComplication,
}
