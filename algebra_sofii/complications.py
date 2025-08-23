"""
Complication classes for generating complex algebraic equations.
"""

import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

from .expressions import Addition, Equals, Expression, ExpressionIndex, Multiplication
from .generators import random_expression


class OperationType(Enum):
    """Types of operations for complications."""

    ADD_ZERO = "add_zero"
    MULTIPLY_BY_ONE = "multiply_by_one"
    ADD = "add"
    MULTIPLY = "multiply"
    INSERT_BRACKETS = "insert_brackets"


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
        original_complexity = expr.complexity()
        complicated_expr = self.apply(expr)
        new_complexity = complicated_expr.complexity()
        return new_complexity - original_complexity

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
        original_complexity = expr.complexity()
        complicated_expr = self.apply(expr)
        new_complexity = complicated_expr.complexity()
        return new_complexity - original_complexity

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


class InsertBracketsComplication(Complication):
    """Complication for inserting brackets around two elements in an addition with 3+ operands."""

    _index: ExpressionIndex
    _first_elem: int
    _second_elem: int
    _negate: bool

    def __init__(
        self, index: ExpressionIndex, first_elem: int, second_elem: int, negate: bool
    ):
        self._index: ExpressionIndex = index
        self._first_elem: int = first_elem
        self._second_elem: int = second_elem
        self._negate: bool = negate

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

    def apply(self, expr: Expression) -> Expression:
        """Apply the complication to the specified addition expression."""
        from .expressions import ChangedSign

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

    def complexity(self, expr: Expression) -> float:
        """Return complexity increase."""
        # Bracketing adds minimal complexity:
        # - Creates a new Addition node (adds 1.0)
        # - Potentially adds ChangedSign wrapper (adds 1.0 if negated)
        # - No net change in operand complexity since we're just regrouping
        base_increase = 1.0  # For the new Addition node
        if self._negate:
            base_increase += 1.0  # For the ChangedSign wrapper
        return base_increase

    def __repr__(self):
        return f"InsertBracketsComplication({self._index}, {self._first_elem}, {self._second_elem}, {self._negate})"


class EquationWithSolution:
    """Container for an equation with its solution and applied complications."""

    _solution: int
    _solution_swapped: bool
    _complications: List[Complication]
    _cached_current_form: Expression

    def __init__(self, solution: int, swap: bool = False):
        self._solution = solution
        self._solution_swapped = swap
        self._complications: List[Complication] = []
        self._cached_current_form = self._initial_equation

    @property
    def _initial_equation(self) -> Expression:
        """The initial equation before complications."""
        return Equals.from_solution(self._solution, self._solution_swapped)

    @property
    def solution(self) -> int:
        """The solution value for the equation."""
        return self._solution

    @property
    def complications(self) -> List[Complication]:
        """The list of complications applied to the equation."""
        return self._complications.copy()

    @property
    def cached_current_form(self) -> Expression:
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
            # Very simple complication - try InsertBrackets first since it has low cost
            brackets_complication = self._try_generate_insert_brackets(random_stream)
            if brackets_complication is not None:
                return brackets_complication

            # Fallback to element move
            return EquationElementMove(
                right_side=random_stream.choice([True, False]), elem_index=0
            )

        # Check if we can use InsertBrackets (low cost) - always use if available
        if remaining_complexity <= 3.0:
            brackets_complication = self._try_generate_insert_brackets(random_stream)
            if brackets_complication is not None:  # Always use brackets if available
                return brackets_complication

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
            subexpression = self.cached_current_form[index]

            # Generate expression with appropriate complexity
            target_complexity = min(remaining_complexity / 2, 3.0)

            # For MULTIPLY_BY_ONE, exclude unknown to maintain linearity
            exclude_unknown = (
                operation == OperationType.MULTIPLY_BY_ONE
                and subexpression.maximum_power_of_unknown() >= 1
            )
            expr = random_expression(random_stream, target_complexity, exclude_unknown)

            return ExpressionComplication(index, operation, expr)

        else:  # equation complication
            operation = random_stream.choice(
                [OperationType.ADD, OperationType.MULTIPLY]
            )

            # Generate expression with appropriate complexity
            target_complexity = min(remaining_complexity / 3, 2.0)

            # If maintaining linearity, exclude unknown from equation complications too
            # This prevents x * (expression with x) = quadratic terms
            exclude_unknown = operation == OperationType.MULTIPLY
            expr = random_expression(random_stream, target_complexity, exclude_unknown)

            return EquationComplication(operation, expr)

    def _try_generate_insert_brackets(self, random_stream) -> Complication | None:
        """Try to generate an InsertBrackets complication if possible."""
        if self._cached_current_form is None:
            return None

        # Find all Addition expressions with 3+ operands in the current equation
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
                # For Equals expressions
                find_additions(expr.left, ExpressionIndex(current_index.indices + [0]))
                find_additions(expr.right, ExpressionIndex(current_index.indices + [1]))
            elif hasattr(expr, "operand"):
                # For unary operators like ChangedSign
                find_additions(
                    expr.operand, ExpressionIndex(current_index.indices + [0])
                )

        find_additions(self._cached_current_form, ExpressionIndex([]))

        if not suitable_additions:
            return None

        # Pick a random suitable addition
        target_index = random_stream.choice(suitable_additions)
        target_addition = self._cached_current_form[target_index]

        # We know this is an Addition with 3+ operands from our search
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

        # Random chance of negation
        negate = random_stream.choice([True, False])

        return InsertBracketsComplication(target_index, first_elem, second_elem, negate)

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
