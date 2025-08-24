"""
MultiplyByOneComplication class for generating complex algebraic equations.
"""

import random
from typing import Optional

from .base import Complication
from ..expressions import Expression, ExpressionIndex
from ..generators import random_expression


class MultiplyByOneComplication(Complication):
    """Complication that multiplies by one using expr * (original / expr)."""

    def __init__(self, index: ExpressionIndex, expr: Expression):
        self._index = index
        self._expr = expr

    @property
    def index(self) -> ExpressionIndex:
        """The index of the subexpression to target."""
        return self._index

    @property
    def expr(self) -> Expression:
        """The expression to use in the multiply-by-one operation."""
        return self._expr

    @property
    def minimal_complexity(self) -> float:
        """Return the minimal complexity this complication will add."""
        # Adds: expr.complexity() + 1.0 (Multiplication) + 1.0 (Inverted)
        return self._expr.complexity() + 2.0

    @property
    def maximal_complexity(self) -> float:
        """Return the maximal complexity this complication can add."""
        return self.minimal_complexity

    def apply(self, expr: Expression) -> Expression:
        """Apply the multiply-by-one complication to the specified subexpression."""
        target_expr = expr[self._index]
        new_expr = target_expr.multiply_by_one(self._expr)
        return expr.replace_with(self._index, new_expr)

    @staticmethod
    def randomize_from_stream(
        random_stream: random.Random,
        base_expression: Expression,
        complexity_budget: float,
        exclude_unknown: bool = False,
    ) -> Optional["MultiplyByOneComplication"]:
        """Create a random MultiplyByOneComplication within the complexity budget."""
        # Need at least 3.0 complexity for the minimal case (1.0 for expr + 2.0 for structure)
        if complexity_budget < 3.0:
            return None

        # Pick a random subexpression
        index = base_expression.random_subexpression(random_stream)
        subexpression = base_expression[index]

        # Generate expression with appropriate complexity
        expr_budget = complexity_budget - 2.0  # Reserve 2.0 for structure

        # Exclude unknown if requested OR if multiplying by expression containing unknown to maintain linearity
        exclude_unknown_final = (
            exclude_unknown or subexpression.maximum_power_of_unknown() >= 1
        )
        expr = random_expression(random_stream, expr_budget, exclude_unknown_final)

        # Double check that the resulting complication fits within budget
        result = MultiplyByOneComplication(index, expr)
        if result.minimal_complexity > complexity_budget:
            # If still too complex, try with a simpler expression
            expr = random_expression(random_stream, 1.0, exclude_unknown_final)
            result = MultiplyByOneComplication(index, expr)

        return result

    def __repr__(self):
        return f"MultiplyByOneComplication({self._index}, {self._expr})"
