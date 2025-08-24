"""
NegateComplication class for generating complex algebraic equations.
"""

import random
from typing import Optional

from .base import Complication
from ..expressions import Expression, ExpressionIndex, ChangedSign


class NegateComplication(Complication):
    """Complication that negates a subexpression."""

    def __init__(self, index: ExpressionIndex):
        self._index = index

    @property
    def index(self) -> ExpressionIndex:
        """The index of the subexpression to target."""
        return self._index

    @property
    def minimal_complexity(self) -> float:
        """Return the minimal complexity this complication will add."""
        # Adds ChangedSign wrapper (1.0)
        return 1.0

    @property
    def maximal_complexity(self) -> float:
        """Return the maximal complexity this complication can add."""
        return 1.0

    def apply(self, expr: Expression) -> Expression:
        """Apply the negate complication to the specified subexpression."""
        target_expr = expr[self._index]
        new_expr = ChangedSign(target_expr)
        return expr.replace_with(self._index, new_expr)

    @staticmethod
    def randomize_from_stream(
        random_stream: random.Random,
        base_expression: Expression,
        complexity_budget: float,
    ) -> Optional["NegateComplication"]:
        """Create a random NegateComplication within the complexity budget."""
        # Need at least 1.0 complexity
        if complexity_budget < 1.0:
            return None

        # Pick a random subexpression
        index = base_expression.random_subexpression(random_stream)

        return NegateComplication(index)

    def __repr__(self):
        return f"NegateComplication({self._index})"
