"""
InsertBracketsComplication class for generating complex algebraic equations.
"""

import random
from typing import Optional

from .base import Complication
from ..expressions import (
    Addition,
    Expression,
    ExpressionIndex,
    Multiplication,
    Equals,
    ChangedSign,
)


class InsertBracketsComplication(Complication):
    """Complication that inserts brackets around two elements in an addition with 3+ operands."""

    def __init__(
        self, index: ExpressionIndex, first_elem: int, second_elem: int, negate: bool
    ):
        self._index = index
        self._first_elem = first_elem
        self._second_elem = second_elem
        self._negate = negate

    @property
    def index(self) -> ExpressionIndex:
        """The index of the addition expression to target."""
        return self._index

    @property
    def first_elem(self) -> int:
        """The index of the first element to bracket."""
        return self._first_elem

    @property
    def second_elem(self) -> int:
        """The index of the second element to bracket."""
        return self._second_elem

    @property
    def negate(self) -> bool:
        """Whether to negate the bracketed expression."""
        return self._negate

    @property
    def minimal_complexity(self) -> float:
        """Return the minimal complexity this complication will add."""
        # Creates new Addition node (1.0) + optionally ChangedSign (1.0)
        base_increase = 1.0
        if self._negate:
            base_increase += 1.0
        return base_increase

    @property
    def maximal_complexity(self) -> float:
        """Return the maximal complexity this complication can add."""
        return self.minimal_complexity

    def apply(self, expr: Expression) -> Expression:
        """Apply the insert-brackets complication to the specified addition expression."""
        target_expr = expr[self._index]

        if not isinstance(target_expr, Addition):
            raise ValueError(
                "InsertBracketsComplication can only be applied to Addition expressions"
            )

        if len(target_expr.operands) < 3:
            raise ValueError(
                "InsertBracketsComplication requires Addition with 3+ operands"
            )

        # Get the operands
        operands = target_expr.operands

        # Extract the two elements to bracket
        first_operand = operands[self._first_elem]
        second_operand = operands[self._second_elem]

        # Create the bracketed expression (addition of the two elements)
        bracketed_expr = Addition([first_operand, second_operand])

        # Apply negation if needed
        if self._negate:
            bracketed_expr = ChangedSign(bracketed_expr)

        # Create new operands list with the bracketed expression
        new_operands = []
        for i, operand in enumerate(operands):
            if i == self._first_elem:
                # Replace first element with bracketed expression
                new_operands.append(bracketed_expr)
            elif i == self._second_elem:
                # Skip second element (it's now part of the bracketed expression)
                continue
            else:
                new_operands.append(operand)

        # Create new addition with updated operands
        new_expr = Addition(new_operands)

        return expr.replace_with(self._index, new_expr)

    @staticmethod
    def randomize_from_stream(
        random_stream: random.Random,
        base_expression: Expression,
        complexity_budget: float,
        exclude_unknown: bool = False,
    ) -> Optional["InsertBracketsComplication"]:
        """Create a random InsertBracketsComplication within the complexity budget."""
        # Need at least 1.0 complexity for the minimal case
        if complexity_budget < 1.0:
            return None

        # Find all Addition expressions with 3+ operands in the base expression
        suitable_additions = []

        def find_additions(expr, current_index):
            if isinstance(expr, Addition) and len(expr.operands) >= 3:
                suitable_additions.append(current_index)

            # Recursively search in subexpressions
            if isinstance(expr, Addition) or isinstance(expr, Multiplication):
                for i, operand in enumerate(expr.operands):
                    find_additions(
                        operand, ExpressionIndex(current_index.indices + [i])
                    )
            elif isinstance(expr, Equals):
                find_additions(expr.left, ExpressionIndex(current_index.indices + [0]))
                find_additions(expr.right, ExpressionIndex(current_index.indices + [1]))
            elif hasattr(expr, "operand"):
                find_additions(
                    expr.operand, ExpressionIndex(current_index.indices + [0])
                )

        find_additions(base_expression, ExpressionIndex([]))

        if not suitable_additions:
            return None

        # Pick a random suitable addition
        target_index = random_stream.choice(suitable_additions)
        target_addition = base_expression[target_index]

        assert isinstance(target_addition, Addition)

        # Pick two random elements to bracket
        operand_count = len(target_addition.operands)
        first_elem = random_stream.randint(0, operand_count - 1)
        second_elem = random_stream.randint(0, operand_count - 1)

        # Ensure they are different
        while second_elem == first_elem:
            second_elem = random_stream.randint(0, operand_count - 1)

        # Ensure first_elem < second_elem for consistent ordering
        if first_elem > second_elem:
            first_elem, second_elem = second_elem, first_elem

        # Random chance of negation (but only if budget allows)
        negate = complexity_budget >= 2.0 and random_stream.choice([True, False])

        return InsertBracketsComplication(target_index, first_elem, second_elem, negate)

    def __repr__(self):
        return f"InsertBracketsComplication({self._index}, {self._first_elem}, {self._second_elem}, {self._negate})"
