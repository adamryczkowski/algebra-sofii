# InvertComplication class for generating complex algebraic equations.

from typing import Optional

from .base import Complication
from ..expressions import Expression, ExpressionIndex, Inverted
from ..random_class import RandomClass
from overrides import overrides


class InvertComplication(Complication):
    """Complication that inverts a subexpression (1/expr)."""

    def __init__(self, index: ExpressionIndex):
        self._index = index

    @property
    def index(self) -> ExpressionIndex:
        """The index of the subexpression to target."""
        return self._index

    @property
    @overrides
    def minimal_complexity(self) -> float:
        """Return the minimal complexity this complication will add."""
        # Adds double Inverted wrapper (2.0) but it's a no-op
        return 2.0

    @property
    @overrides
    def maximal_complexity(self) -> float:
        """Return the maximal complexity this complication can add."""
        return 2.0

    @overrides
    def apply(self, expr: Expression) -> Expression:
        """Apply the invert complication twice to the specified subexpression (no-op)."""
        target_expr = expr[self._index]
        # Apply inversion twice to make it a no-op: 1/(1/expr) = expr
        new_expr = Inverted(target_expr.inverted())
        return expr.replace_with(self._index, new_expr)

    @staticmethod
    @overrides
    def randomize_from_stream(
        random_stream: RandomClass,
        base_expression: Expression,
        complexity_budget: float,
        exclude_unknown: bool = False,
    ) -> Optional["InvertComplication"]:
        """Create a random InvertComplication within the complexity budget."""
        # Need at least 2.0 complexity for double inversion
        if complexity_budget < 2.0:
            return None

        # Pick a random subexpression
        index = base_expression.random_subexpression(random_stream)

        return InvertComplication(index)

    @overrides
    def __repr__(self) -> str:
        return f"InvertComplication({self._index})"
