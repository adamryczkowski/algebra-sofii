"""
MultiplyEquationComplication class for generating complex algebraic equations.
"""

import random
from typing import Optional

from .base import Complication
from ..expressions import Expression, Equals
from ..generators import random_expression


class MultiplyEquationComplication(Complication):
    """Complication that multiplies both sides of an equation by an expression."""

    def __init__(self, expr: Expression):
        self._expr = expr

    @property
    def expr(self) -> Expression:
        """The expression to multiply both sides by."""
        return self._expr

    @property
    def minimal_complexity(self) -> float:
        """Return the minimal complexity this complication will add."""
        # Adds the expression to both sides (2 * expr.complexity())
        return 2 * self._expr.complexity()

    @property
    def maximal_complexity(self) -> float:
        """Return the maximal complexity this complication can add."""
        return self.minimal_complexity

    def apply(self, expr: Expression) -> Expression:
        """Apply the multiply-equation complication to both sides of an equation."""
        if not isinstance(expr, Equals):
            raise ValueError(
                "MultiplyEquationComplication can only be applied to Equals expressions"
            )

        return expr.multiply_sides_by(self._expr)

    @staticmethod
    def randomize_from_stream(
        random_stream: random.Random,
        base_expression: Expression,
        complexity_budget: float,
        exclude_unknown: bool = False,
    ) -> Optional["MultiplyEquationComplication"]:
        """Create a random MultiplyEquationComplication within the complexity budget."""
        # Need at least 2.0 complexity for the minimal case
        if complexity_budget < 2.0:
            return None

        # Generate expression with appropriate complexity
        expr_budget = complexity_budget / 2.0  # Since we duplicate it

        # Ensure we have a reasonable minimum budget for expression generation
        expr_budget = min(expr_budget, 2.5) if exclude_unknown else expr_budget

        # Always exclude unknown to maintain linearity (override parameter)
        expr = random_expression(random_stream, expr_budget, exclude_unknown=True)

        # Double check that the resulting complication fits within budget
        result = MultiplyEquationComplication(expr)
        if result.minimal_complexity > complexity_budget:
            # If still too complex, try with a minimal expression
            expr = random_expression(random_stream, 1.0, exclude_unknown=True)
            result = MultiplyEquationComplication(expr)

            # If still doesn't fit, return None
            if result.minimal_complexity > complexity_budget:
                return None

        return result

    def __repr__(self):
        return f"MultiplyEquationComplication({self._expr})"
