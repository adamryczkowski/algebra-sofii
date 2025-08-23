"""
Complication classes for generating complex algebraic equations.
"""

import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

from .expressions import Equals, Expression, ExpressionIndex
from .generators import random_expression


class OperationType(Enum):
    """Types of operations for complications."""

    ADD_ZERO = "add_zero"
    MULTIPLY_BY_ONE = "multiply_by_one"
    ADD = "add"
    MULTIPLY = "multiply"


class Complication(ABC):
    """Base class for all complications."""

    @abstractmethod
    def apply(self, expr: Expression) -> Expression:
        """Apply the complication to an expression."""
        pass

    @abstractmethod
    def complexity(self, expr: Expression) -> float:
        """Return complexity increase of applying the complication."""
        pass


class ExpressionComplication(Complication):
    """Complication for any subexpression."""

    _index: ExpressionIndex
    _operation: OperationType
    _expr: Expression

    def __init__(
        self, index: ExpressionIndex, operation: OperationType, expr: Expression
    ):
        self._index: ExpressionIndex = index
        self._operation: OperationType = operation
        self._expr: Expression = expr

    @property
    def index(self) -> ExpressionIndex:
        """The index of the subexpression to target."""
        return self._index

    @property
    def operation(self) -> OperationType:
        """The operation type to apply."""
        return self._operation

    @property
    def expr(self) -> Expression:
        """The expression to use in the operation."""
        return self._expr

    def apply(self, expr: Expression) -> Expression:
        """Apply the complication to the specified subexpression."""
        target_expr = expr[self._index]

        if self._operation == OperationType.ADD_ZERO:
            new_expr = target_expr.add_zero(self._expr)
        elif self._operation == OperationType.MULTIPLY_BY_ONE:
            new_expr = target_expr.multiply_by_one(self._expr)
        else:
            raise ValueError(
                f"Invalid operation for ExpressionComplication: {self._operation}"
            )

        return expr.replace_with(self._index, new_expr)

    def complexity(self, expr: Expression) -> float:
        """Return complexity increase."""
        base_complexity = self._expr.complexity()
        if self._operation == OperationType.ADD_ZERO:
            return base_complexity + 2.0  # Add and subtract operations
        elif self._operation == OperationType.MULTIPLY_BY_ONE:
            return base_complexity + 3.0  # Multiply and divide operations
        return base_complexity

    def __repr__(self):
        return f"ExpressionComplication({self._index}, {self._operation}, {self._expr})"


class EquationComplication(Complication):
    """Complication for equations (operations on both sides)."""

    _operation: OperationType
    _expr: Expression

    def __init__(self, operation: OperationType, expr: Expression):
        self._operation: OperationType = operation
        self._expr: Expression = expr

    @property
    def operation(self) -> OperationType:
        """The operation type to apply."""
        return self._operation

    @property
    def expr(self) -> Expression:
        """The expression to use in the operation."""
        return self._expr

    def apply(self, expr: Expression) -> Expression:
        """Apply the complication to both sides of an equation."""
        if not isinstance(expr, Equals):
            raise ValueError(
                "EquationComplication can only be applied to Equals expressions"
            )

        if self._operation == OperationType.ADD:
            return expr.add_to_sides(self._expr)
        elif self._operation == OperationType.MULTIPLY:
            return expr.multiply_sides_by(self._expr)
        else:
            raise ValueError(
                f"Invalid operation for EquationComplication: {self._operation}"
            )

    def complexity(self, expr: Expression) -> float:
        """Return complexity increase."""
        base_complexity = self._expr.complexity()
        if self._operation == OperationType.ADD:
            return base_complexity * 2  # Added to both sides
        elif self._operation == OperationType.MULTIPLY:
            return base_complexity * 2 + 1  # Multiplied on both sides
        return base_complexity

    def __repr__(self):
        return f"EquationComplication({self._operation}, {self._expr})"


class EquationElementMove(Complication):
    """Complication for moving elements between sides of an equation."""

    _right_side: bool
    _elem_index: int

    def __init__(self, right_side: bool, elem_index: int):
        self._right_side: bool = right_side  # False for left side
        self._elem_index: int = elem_index

    @property
    def right_side(self) -> bool:
        """Whether to move to the right side (False for left side)."""
        return self._right_side

    @property
    def elem_index(self) -> int:
        """The index of the element to move."""
        return self._elem_index

    def apply(self, expr: Expression) -> Expression:
        """Move an element from one side to another."""
        if not isinstance(expr, Equals):
            raise ValueError(
                "EquationElementMove can only be applied to Equals expressions"
            )

        # For now, implement a basic version
        # TODO: Implement proper element moving logic based on operation types
        return expr.swap_side_of_element(self._elem_index)

    def complexity(self, expr: Expression) -> float:
        """Return complexity increase."""
        return 1.0  # Moving elements doesn't add much complexity

    def __repr__(self):
        return f"EquationElementMove({self._right_side}, {self._elem_index})"


class EquationWithSolution:
    """Container for an equation with its solution and applied complications."""

    _solution: int
    _complications: List[Complication]
    _cached_current_form: Optional[Expression]
    _initial_equation: Expression

    def __init__(self, solution: int, swap: bool = False):
        self._solution: int = solution
        self._complications: List[Complication] = []
        self._cached_current_form: Optional[Expression] = None
        self._initial_equation: Expression = Equals.from_solution(solution, swap)
        self._update_cache()

    @property
    def solution(self) -> int:
        """The solution value for the equation."""
        return self._solution

    @property
    def complications(self) -> List[Complication]:
        """The list of complications applied to the equation."""
        return self._complications.copy()

    @property
    def cached_current_form(self) -> Optional[Expression]:
        """The cached current form of the equation."""
        return self._cached_current_form

    def _update_cache(self):
        """Update the cached current form."""
        current = self._initial_equation
        for complication in self._complications:
            current = complication.apply(current)
        self._cached_current_form = current

    def random_complication(
        self, max_complexity: float, random_stream=None
    ) -> Complication:
        """Generate a random complication within complexity limits."""
        if random_stream is None:
            random_stream = random.Random()

        if self._cached_current_form is None:
            raise ValueError("No cached current form available")

        current_complexity = self._cached_current_form.complexity()
        remaining_complexity = max_complexity - current_complexity

        if remaining_complexity <= 1.0:
            # Very simple complication
            return EquationElementMove(
                right_side=random_stream.choice([True, False]), elem_index=0
            )

        # Choose type of complication
        complication_types = ["expression", "equation"]
        if remaining_complexity < 3.0:
            # Prefer equation complications for low complexity
            complication_types = ["equation"] * 3 + ["expression"]

        comp_type = random_stream.choice(complication_types)

        if comp_type == "expression":
            # Generate expression complication
            index = self._cached_current_form.random_subexpression(random_stream)
            operation = random_stream.choice(
                [OperationType.ADD_ZERO, OperationType.MULTIPLY_BY_ONE]
            )

            # Generate expression with appropriate complexity
            target_complexity = min(remaining_complexity / 2, 3.0)
            expr = random_expression(random_stream, target_complexity)

            return ExpressionComplication(index, operation, expr)

        else:  # equation complication
            operation = random_stream.choice(
                [OperationType.ADD, OperationType.MULTIPLY]
            )

            # Generate expression with appropriate complexity
            target_complexity = min(remaining_complexity / 3, 2.0)
            expr = random_expression(random_stream, target_complexity)

            return EquationComplication(operation, expr)

    def apply_complication(self, complication: Complication):
        """Apply a complication and update the cached form."""
        self._complications.append(complication)
        self._update_cache()

    def get_current_equation(self) -> Expression:
        """Get the current form of the equation."""
        if self._cached_current_form is None:
            raise ValueError("No cached current form available")
        return self._cached_current_form

    def get_total_complexity(self) -> float:
        """Get the total complexity of the current equation."""
        if self._cached_current_form is None:
            raise ValueError("No cached current form available")
        return self._cached_current_form.complexity()

    def verify_solution(self) -> bool:
        """Verify that the equation still solves to the original solution."""
        if self._cached_current_form is None:
            return False
        try:
            # For equations, both sides should be equal
            if isinstance(self._cached_current_form, Equals):
                left_val = self._cached_current_form.left.evaluate(self._solution)
                right_val = self._cached_current_form.right.evaluate(self._solution)
                return abs(left_val - right_val) < 1e-10
            return True
        except (ZeroDivisionError, ValueError):
            return False

    def __repr__(self):
        return f"EquationWithSolution(solution={self._solution}, complications={len(self._complications)})"
