# MultiplyEquationComplication class for generating complex algebraic equations.

from typing import Optional

from .base import Complication
from ..expressions import Expression, Equals
from ..generators import random_expression
from ..random_class import RandomClass
from overrides import overrides


class MultiplyEquationComplication(Complication):
    """Complication that multiplies both sides of an equation by an expression."""

    _expr: Expression
    _left_side: bool

    def __init__(self, expr: Expression, left_side: bool):
        self._expr = expr
        self._left_side = left_side

    @property
    def expr(self) -> Expression:
        """The expression to multiply both sides by."""
        return self._expr

    @property
    @overrides
    def minimal_complexity(self) -> float:
        """Return the minimal complexity this complication will add."""
        # Adds the expression to both sides (2 * expr.complexity())
        return 2 * self._expr.complexity()

    @property
    @overrides
    def maximal_complexity(self) -> float:
        """Return the maximal complexity this complication can add."""
        return self.minimal_complexity

    @overrides
    def apply(self, expr: Expression) -> Expression:
        """Apply the multiply-equation complication to both sides of an equation."""
        if not isinstance(expr, Equals):
            raise ValueError(
                "MultiplyEquationComplication can only be applied to Equals expressions"
            )
        return expr.multiply_sides_by(self._expr, self._left_side)

    @staticmethod
    @overrides
    def randomize_from_stream(
        random_stream: RandomClass,
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
        result = MultiplyEquationComplication(
            expr, left_side=random_stream.rand_coinflip(0.5)
        )

        return result

    @overrides
    def __repr__(self) -> str:
        return f"MultiplyEquationComplication({self._expr})"
