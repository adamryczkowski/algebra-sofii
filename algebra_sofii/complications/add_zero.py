# AddZeroComplication class for generating complex algebraic equations.

from typing import Optional

from overrides import overrides

from .base import Complication
from ..expressions import Expression, ExpressionIndex
from ..generators import random_expression
from ..random_class import RandomClass


class AddZeroComplication(Complication):
    """Complication that adds zero by adding expr + (original - expr)."""

    _index: ExpressionIndex
    _expr: Expression

    def __init__(self, index: ExpressionIndex, expr: Expression):
        self._index = index
        self._expr = expr

    @property
    def index(self) -> ExpressionIndex:
        """The index of the subexpression to target."""
        return self._index

    @property
    def expr(self) -> Expression:
        """The expression to use in the add-zero operation."""
        return self._expr

    @property
    @overrides
    def minimal_complexity(self) -> float:
        """Return the minimal complexity this complication will add."""
        # Adds: expr.complexity() + 1.0 (Addition) + 1.0 (ChangedSign)
        return self._expr.complexity() + 2.0

    @property
    @overrides
    def maximal_complexity(self) -> float:
        """Return the maximal complexity this complication can add."""
        return self.minimal_complexity

    @overrides
    def apply(self, expr: Expression) -> Expression:
        """Apply the add-zero complication to the specified subexpression."""
        target_expr = expr[self._index]
        new_expr = target_expr.add_zero(self._expr)
        return expr.replace_with(self._index, new_expr)

    @staticmethod
    @overrides
    def randomize_from_stream(
        random_stream: RandomClass,
        base_expression: Expression,
        complexity_budget: float,
        exclude_unknown: bool = False,
    ) -> Optional["AddZeroComplication"]:
        """Create a random AddZeroComplication within the complexity budget."""
        # Need at least 3.0 complexity for the minimal case (1.0 for expr + 2.0 for structure)
        if complexity_budget < 3.0:
            return None

        # Pick a random subexpression
        index = base_expression.random_subexpression(random_stream)

        # Generate expression with appropriate complexity, ensuring we stay within budget
        expr_budget = complexity_budget - 2.0  # Reserve 2.0 for structure
        expr = random_expression(random_stream, expr_budget, exclude_unknown)

        # Double check that the resulting complication fits within budget
        result = AddZeroComplication(index, expr)
        if result.minimal_complexity > complexity_budget:
            # If still too complex, try with a simpler expression
            expr = random_expression(random_stream, 1.0, exclude_unknown)
            result = AddZeroComplication(index, expr)

        return result

    @overrides
    def __repr__(self):
        return f"AddZeroComplication({self._index}, {self._expr})"
