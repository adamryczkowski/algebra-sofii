"""
AddToEquationComplication class for generating complex algebraic equations.
"""

import random
from typing import Optional

from .base import Complication
from ..expressions import Expression, Equals
from ..generators import random_expression


class AddToEquationComplication(Complication):
    """Complication that adds an expression to both sides of an equation."""

    def __init__(self, expr: Expression):
        self._expr = expr

    @property
    def expr(self) -> Expression:
        """The expression to add to both sides."""
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
        """Apply the add-to-equation complication to both sides of an equation."""
        if not isinstance(expr, Equals):
            raise ValueError(
                "AddToEquationComplication can only be applied to Equals expressions"
            )

        return expr.add_to_sides(self._expr)

    @staticmethod
    def randomize_from_stream(
        random_stream: random.Random,
        base_expression: Expression,
        complexity_budget: float,
    ) -> Optional["AddToEquationComplication"]:
        """Create a random AddToEquationComplication within the complexity budget."""
        # Need at least 2.0 complexity for the minimal case (2 * 1.0 for empty expr)
        if complexity_budget < 2.0:
            return None

        # Generate expression with appropriate complexity
        expr_budget = complexity_budget / 2.0  # Since we duplicate it
        expr = random_expression(random_stream, expr_budget, exclude_unknown=False)

        # Double check that the resulting complication fits within budget
        result = AddToEquationComplication(expr)
        if result.minimal_complexity > complexity_budget:
            # If still too complex, try with a simpler expression
            expr = random_expression(random_stream, 1.0, exclude_unknown=False)
            result = AddToEquationComplication(expr)

        return result

    def __repr__(self):
        return f"AddToEquationComplication({self._expr})"
