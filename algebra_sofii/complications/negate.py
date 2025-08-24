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
        # Adds double ChangedSign wrapper (2.0) but it's a no-op
        return 2.0

    @property
    def maximal_complexity(self) -> float:
        """Return the maximal complexity this complication can add."""
        return 2.0

    def apply(self, expr: Expression) -> Expression:
        """Apply the negate complication twice to the specified subexpression (no-op)."""
        target_expr = expr[self._index]
        # Apply negation twice to make it a no-op: -(-expr) = expr
        new_expr = ChangedSign(ChangedSign(target_expr))
        return expr.replace_with(self._index, new_expr)

    @staticmethod
    def randomize_from_stream(
        random_stream: random.Random,
        base_expression: Expression,
        complexity_budget: float,
        exclude_unknown: bool = False,
    ) -> Optional["NegateComplication"]:
        """Create a random NegateComplication within the complexity budget."""
        # Need at least 2.0 complexity for double negation
        if complexity_budget < 2.0:
            return None

        # Pick a random subexpression
        index = base_expression.random_subexpression(random_stream)

        return NegateComplication(index)

    def __repr__(self):
        return f"NegateComplication({self._index})"
