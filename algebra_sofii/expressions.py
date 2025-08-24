# Expression class hierarchy for algebraic equation generation.
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple

import sympy as sp
from overrides import overrides

from .random_class import RandomClass


class ExpressionIndex:
    """Wrapper around list of integers that comprise an index into an expression."""

    _indices: List[int]

    def __init__(self, indices: List[int]):
        self._indices: List[int] = indices.copy()

    @property
    def indices(self) -> List[int]:
        """The list of indices that comprise this expression index."""
        return self._indices.copy()

    def __repr__(self) -> str:
        return f"ExpressionIndex({self._indices})"

    def __eq__(self, other):
        return isinstance(other, ExpressionIndex) and self._indices == other.indices


class Expression(ABC):
    """Base class for all algebraic expressions."""

    @abstractmethod
    def maximum_power_of_unknown(self) -> int:
        """Return the maximum power of the unknown variable in this expression."""
        pass

    @abstractmethod
    def to_sympy_expr(self) -> sp.Expr:
        """Convert to sympy expression."""
        pass

    def _to_sympy_expr_depth_limited(self, max_depth: int) -> sp.Expr:
        """Default implementation that delegates to to_sympy_expr."""
        return self.to_sympy_expr()

    def evaluate(self, true_x: int) -> sp.Expr:
        """Evaluate the expression using sympy."""
        x = sp.Symbol("x")
        expr = self.to_sympy_expr()
        return expr.subs(x, true_x)

    @abstractmethod
    def random_subexpression(self, random_stream: RandomClass) -> ExpressionIndex:
        """Return an index to a random subexpression."""
        pass

    @abstractmethod
    def __getitem__(self, index: ExpressionIndex) -> Expression:
        """Return an expression stored by the index."""
        pass

    @abstractmethod
    def complexity(self) -> float:
        """Return the complexity measure of the expression."""
        pass

    def _complexity_depth_limited(self, max_depth: int) -> float:
        """Default implementation that delegates to complexity."""
        return self.complexity()

    @abstractmethod
    def replace_with(self, index: ExpressionIndex, expr: Expression) -> Expression:
        """Replace the subnode with a new one."""
        pass

    def add_expression(self, expr: Expression, left_side: bool) -> Addition:
        """Add the expression `expr`."""
        if left_side:
            return Addition([expr, self])
        else:
            return Addition([self, expr])

    def add_zero(self, expr: Expression) -> Addition:
        """Replace the node with a sum of the `expr` and a subtraction of former value minus the `expr`."""
        return Addition([expr, Addition([self, ChangedSign(expr)])])

    def multiply_by_one(self, expr: Expression) -> Multiplication:
        """Replace the node with the `expr` times division of former value by `expr`."""
        return Multiplication([expr, Multiplication([self, Inverted(expr)])])

    def multiply_by(self, expr: Expression, left_side: bool) -> Multiplication:
        """Multiply by the given expression."""
        if left_side:
            return Multiplication([expr, self])
        else:
            return Multiplication([self, expr])

    def negated(self) -> Expression:
        """Return the expression with changed sign operator."""
        return ChangedSign(self)

    def inverted(self) -> Expression:
        """Return a division of 1/self."""
        return Inverted(self)


class Integer(Expression):
    """Integer constant expression."""

    _value: int

    def __init__(self, value: int):
        self._value: int = value

    @property
    def value(self) -> int:
        """The integer value."""
        return self._value

    @overrides
    def maximum_power_of_unknown(self) -> int:
        """Integer constants have no unknown variable, so power is 0."""
        return 0

    @overrides
    def to_sympy_expr(self) -> sp.Expr:
        return sp.Integer(self._value)

    @overrides
    def _to_sympy_expr_depth_limited(self, max_depth: int) -> sp.Expr:
        if max_depth <= 0:
            # Return a simple placeholder if we hit depth limit
            return sp.Integer(0)

        return super()._to_sympy_expr_depth_limited(max_depth)

    @overrides
    def random_subexpression(self, random_stream) -> ExpressionIndex:
        return ExpressionIndex([])

    @overrides
    def __getitem__(self, index: ExpressionIndex) -> Expression:
        if not index.indices:
            return self
        raise IndexError("Integer has no subexpressions")

    @overrides
    def complexity(self) -> float:
        return 1.0

    @overrides
    def _complexity_depth_limited(self, max_depth: int) -> float:
        if max_depth <= 0:
            return 1.0  # Return base complexity if we've hit the depth limit

        return super()._complexity_depth_limited(max_depth)

    @overrides
    def replace_with(self, index: ExpressionIndex, expr: Expression) -> Expression:
        if not index.indices:
            return expr
        raise IndexError("Integer has no subexpressions")

    @overrides
    def negated(self) -> Expression:
        return Integer(-self._value)

    @overrides
    def __repr__(self):
        return str(self._value)

    @overrides
    def __eq__(self, other):
        return isinstance(other, Integer) and self._value == other.value


class Unknown(Expression):
    """Unknown variable expression (x)."""

    def __init__(self):
        pass

    @property
    def name(self) -> str:
        """The name of the unknown variable."""
        return "x"

    @overrides
    def maximum_power_of_unknown(self) -> int:
        """Unknown variable has power 1."""
        return 1

    @overrides
    def to_sympy_expr(self) -> sp.Expr:
        return sp.Symbol(self.name)

    @overrides
    def _to_sympy_expr_depth_limited(self, max_depth: int) -> sp.Expr:
        if max_depth <= 0:
            # Return a simple placeholder if we hit depth limit
            return sp.Integer(0)

        return super()._to_sympy_expr_depth_limited(max_depth)

    @overrides
    def random_subexpression(self, random_stream: RandomClass) -> ExpressionIndex:
        return ExpressionIndex([])

    @overrides
    def __getitem__(self, index: ExpressionIndex) -> Expression:
        if not index.indices:
            return self
        raise IndexError("Unknown has no subexpressions")

    @overrides
    def complexity(self) -> float:
        return 1.0

    @overrides
    def _complexity_depth_limited(self, max_depth: int) -> float:
        if max_depth <= 0:
            return 1.0  # Return base complexity if we've hit the depth limit

        return super()._complexity_depth_limited(max_depth)

    @overrides
    def replace_with(self, index: ExpressionIndex, expr: Expression) -> Expression:
        if not index.indices:
            return expr
        raise IndexError("Unknown has no subexpressions")

    @overrides
    def __repr__(self):
        return self.name

    @overrides
    def __eq__(self, other):
        return isinstance(other, Unknown) and self.name == other.name


class MathOperator(Expression):
    """Base class for mathematical operations with multiple operands."""

    _operands: List[Expression]

    def __init__(self, operands: List[Expression]):
        if len(operands) < 2:
            raise ValueError("MathOperator requires at least 2 operands")
        self._operands: List[Expression] = operands.copy()

    @property
    def operands(self) -> List[Expression]:
        """The list of operands for this mathematical operation."""
        return self._operands.copy()

    @overrides
    def random_subexpression(self, random_stream: RandomClass) -> ExpressionIndex:
        # Choose random operand or self
        choices = list(range(len(self._operands))) + [-1]  # -1 for self
        choice = random_stream.choice(choices)
        if choice == -1:
            return ExpressionIndex([])
        else:
            sub_index = self._operands[choice].random_subexpression(random_stream)
            return ExpressionIndex([choice] + sub_index.indices)

    @overrides
    def __getitem__(self, index: ExpressionIndex) -> Expression:
        if not index.indices:
            return self
        operand_idx = index.indices[0]
        if operand_idx >= len(self._operands):
            raise IndexError("Operand index out of range")
        remaining_index = ExpressionIndex(index.indices[1:])
        return self._operands[operand_idx][remaining_index]

    @overrides
    def complexity(self) -> float:
        # Use depth-limited complexity calculation to prevent infinite recursion
        return self._complexity_depth_limited(max_depth=50)

    @overrides
    def _complexity_depth_limited(self, max_depth: int) -> float:
        if max_depth <= 0:
            return 1.0  # Return base complexity if we've hit the depth limit

        return 1.0 + sum(
            op._complexity_depth_limited(max_depth - 1)
            if hasattr(op, "_complexity_depth_limited")
            else op.complexity()
            for op in self._operands
        )

    @overrides
    def replace_with(self, index: ExpressionIndex, expr: Expression) -> Expression:
        if not index.indices:
            return expr

        operand_idx = index.indices[0]
        if operand_idx >= len(self._operands):
            raise IndexError("Operand index out of range")

        new_operands = self._operands.copy()
        remaining_index = ExpressionIndex(index.indices[1:])
        new_operands[operand_idx] = new_operands[operand_idx].replace_with(
            remaining_index, expr
        )

        return self.__class__(new_operands)

    def remove_node(self, node_index: int) -> Tuple[Expression, Expression]:
        """Remove a node and return the extracted expression and what's left."""
        if node_index >= len(self._operands):
            raise IndexError("Node index out of range")

        extracted = self._operands[node_index]
        remaining_operands = [
            op for i, op in enumerate(self._operands) if i != node_index
        ]

        if len(remaining_operands) == 1:
            return extracted, remaining_operands[0]
        else:
            return extracted, self.__class__(remaining_operands)


class Addition(MathOperator):
    """Addition operation."""

    @overrides
    def maximum_power_of_unknown(self) -> int:
        """For addition, return the maximum power among all operands."""
        return max(op.maximum_power_of_unknown() for op in self._operands)

    @overrides
    def to_sympy_expr(self) -> sp.Expr:
        # Add recursion protection to prevent infinite loops
        return self._to_sympy_expr_depth_limited(max_depth=50)

    @overrides
    def _to_sympy_expr_depth_limited(self, max_depth: int) -> sp.Expr:
        if max_depth <= 0:
            # Return a simple placeholder if we hit depth limit
            return sp.Integer(0)

        if not self._operands:
            return sp.Integer(0)
        result = (
            self._operands[0]._to_sympy_expr_depth_limited(max_depth - 1)
            if hasattr(self._operands[0], "_to_sympy_expr_depth_limited")
            else self._operands[0].to_sympy_expr()
        )
        for op in self._operands[1:]:
            op_expr = (
                op._to_sympy_expr_depth_limited(max_depth - 1)
                if hasattr(op, "_to_sympy_expr_depth_limited")
                else op.to_sympy_expr()
            )
            result = result + op_expr
        return result

    @overrides
    def add_expression(self, expr: Expression, left_side: bool) -> Addition:
        """Override to take advantage of addition associativity and flatten nested additions."""
        if isinstance(expr, Addition):
            # Flatten nested Addition expressions
            expr_operands = expr.operands
        else:
            expr_operands = [expr]

        if left_side:
            return Addition(expr_operands + self._operands)
        else:
            return Addition(self._operands + expr_operands)

    @overrides
    def __repr__(self):
        if not self._operands:
            return "0"
        parts = []
        for i, operand in enumerate(self._operands):
            operand_str = str(operand)
            # Handle negative operands to show subtraction instead of + -
            if isinstance(operand, ChangedSign) and i > 0:
                # Special case: if the first operand is also ChangedSign and this is ChangedSign(Integer),
                # show as + (-n) to preserve explicit negation structure
                if isinstance(self._operands[0], ChangedSign) and isinstance(
                    operand.operand, Integer
                ):
                    # Wrap the entire ChangedSign in parentheses for integers
                    parts.append(f" + ({operand_str})")
                # For other ChangedSign of Integer, show as subtraction (- n)
                elif isinstance(operand.operand, Integer):
                    inner_operand = str(operand.operand)
                    parts.append(f" - {inner_operand}")
                else:
                    # For other ChangedSign operands, show as subtraction
                    inner_operand = str(operand.operand)
                    # Only add parentheses for addition expressions
                    if isinstance(operand.operand, Addition):
                        inner_operand = f"({inner_operand})"
                    parts.append(f" - {inner_operand}")
            # Handle negative integers to show as subtraction instead of + -3
            elif isinstance(operand, Integer) and operand.value < 0 and i > 0:
                # Show as subtraction (remove the negative sign and use - operator)
                positive_value = str(-operand.value)
                parts.append(f" - {positive_value}")
            else:
                # Add parentheses around complex expressions for clarity
                if isinstance(operand, Addition) and i > 0:
                    operand_str = f"({operand_str})"
                if i == 0:
                    parts.append(operand_str)
                else:
                    parts.append(f" + {operand_str}")
        return "".join(parts)

    @overrides
    def negated(self) -> Expression:
        """Override to distribute negation over addition."""
        negated_operands = [op.negated() for op in self._operands]
        return Addition(negated_operands)


class Multiplication(MathOperator):
    """Multiplication operation."""

    @overrides
    def maximum_power_of_unknown(self) -> int:
        """For multiplication, return the sum of powers of all operands."""
        return sum(op.maximum_power_of_unknown() for op in self._operands)

    @overrides
    def to_sympy_expr(self) -> sp.Expr:
        # Add recursion protection to prevent infinite loops
        return self._to_sympy_expr_depth_limited(max_depth=50)

    @overrides
    def _to_sympy_expr_depth_limited(self, max_depth: int) -> sp.Expr:
        if max_depth <= 0:
            # Return a simple placeholder if we hit depth limit
            return sp.Integer(1)

        result = (
            self._operands[0]._to_sympy_expr_depth_limited(max_depth - 1)
            if hasattr(self._operands[0], "_to_sympy_expr_depth_limited")
            else self._operands[0].to_sympy_expr()
        )
        for op in self._operands[1:]:
            op_expr = (
                op._to_sympy_expr_depth_limited(max_depth - 1)
                if hasattr(op, "_to_sympy_expr_depth_limited")
                else op.to_sympy_expr()
            )
            result *= op_expr
        return result

    @overrides
    def multiply_by(self, expr: Expression, left_side: bool) -> Multiplication:
        """Override to take advantage of multiplication associativity."""
        if left_side:
            return Multiplication([expr] + self._operands)
        else:
            return Multiplication(self._operands + [expr])

    @overrides
    def __repr__(self):
        if not self._operands:
            return "1"

        # Check if we have exactly one inverted operand and one regular operand
        # In that case, we might want to show as multiplication with 1/x format
        if len(self._operands) == 2:
            regular_ops = [op for op in self._operands if not isinstance(op, Inverted)]
            inverted_ops = [op for op in self._operands if isinstance(op, Inverted)]

            if len(regular_ops) == 1 and len(inverted_ops) == 1:
                # Show as explicit multiplication, preserving order
                parts = []
                for operand in self._operands:
                    if isinstance(operand, Inverted):
                        inverted_str = str(operand)  # This will give us "1/x" format
                        parts.append(inverted_str)
                    else:
                        operand_str = str(operand)
                        if isinstance(operand, Addition):
                            operand_str = f"({operand_str})"
                        elif isinstance(operand, Integer) and operand.value < 0:
                            operand_str = f"({operand_str})"
                        elif isinstance(operand, ChangedSign) and isinstance(
                            operand.operand, Integer
                        ):
                            operand_str = f"({operand_str})"
                        parts.append(operand_str)

                return " * ".join(parts)

        # Separate regular operands from inverted ones for general case
        regular_parts = []
        inverted_parts = []

        for operand in self._operands:
            if isinstance(operand, Inverted):
                # For inverted operands, we'll show as division
                operand_str = str(operand.operand)
                # Add parentheses around complex expressions in denominator
                if isinstance(
                    operand.operand, (Addition, Multiplication, ChangedSign, Inverted)
                ):
                    operand_str = f"({operand_str})"
                inverted_parts.append(operand_str)
            else:
                operand_str = str(operand)
                # Add parentheses around addition expressions for clarity
                if isinstance(operand, Addition):
                    operand_str = f"({operand_str})"
                # Add parentheses around negative integers to avoid ambiguity (e.g., x * (-3) not x * -3)
                elif isinstance(operand, Integer) and operand.value < 0:
                    operand_str = f"({operand_str})"
                # Add parentheses around ChangedSign of integers to avoid ambiguity (e.g., x * (-3) not x * -3)
                elif isinstance(operand, ChangedSign) and isinstance(
                    operand.operand, Integer
                ):
                    operand_str = f"({operand_str})"
                regular_parts.append(operand_str)

        # Build the result
        if regular_parts:
            result = " * ".join(regular_parts)
        else:
            result = "1"

        # Add division parts
        for inv_part in inverted_parts:
            result = f"{result}/{inv_part}"

        return result

    @overrides
    def inverted(self) -> Expression:
        """Override to distribute inversion over multiplication."""
        inverted_operands = [op.inverted() for op in self._operands]
        return Multiplication(inverted_operands)

    @overrides
    def negated(self) -> Expression:
        """Override to distribute negation over multiplication."""
        # Negate the first operand
        new_operands = [self._operands[0].negated()] + self._operands[1:]
        return Multiplication(new_operands)


class ChangedSign(Expression):
    """Negation operation."""

    _operand: Expression

    def __init__(self, operand: Expression):
        self._operand: Expression = operand

    @property
    def operand(self) -> Expression:
        """The operand being negated."""
        return self._operand

    @overrides
    def maximum_power_of_unknown(self) -> int:
        """For negation, return the same power as the operand."""
        return self._operand.maximum_power_of_unknown()

    @overrides
    def to_sympy_expr(self) -> sp.Expr:
        # Add recursion protection to prevent infinite loops
        return self._to_sympy_expr_depth_limited(max_depth=50)

    @overrides
    def _to_sympy_expr_depth_limited(self, max_depth: int) -> sp.Expr:
        if max_depth <= 0:
            # Return a simple placeholder if we hit depth limit
            return sp.Integer(0)

        operand_expr = (
            self._operand._to_sympy_expr_depth_limited(max_depth - 1)
            if hasattr(self._operand, "_to_sympy_expr_depth_limited")
            else self._operand.to_sympy_expr()
        )
        return -operand_expr

    @overrides
    def random_subexpression(self, random_stream: RandomClass) -> ExpressionIndex:
        choices = [ExpressionIndex([]), ExpressionIndex([0])]
        choice = random_stream.choice(choices)
        if choice.indices == [0]:
            sub_index = self._operand.random_subexpression(random_stream)
            return ExpressionIndex([0] + sub_index.indices)
        return choice

    @overrides
    def __getitem__(self, index: ExpressionIndex) -> Expression:
        if not index.indices:
            return self
        if index.indices[0] == 0:
            remaining_index = ExpressionIndex(index.indices[1:])
            return self._operand[remaining_index]
        raise IndexError("ChangedSign has only one operand at index 0")

    @overrides
    def complexity(self) -> float:
        # Use depth-limited complexity calculation to prevent infinite recursion
        return self._complexity_depth_limited(max_depth=50)

    @overrides
    def _complexity_depth_limited(self, max_depth: int) -> float:
        if max_depth <= 0:
            return 1.0  # Return base complexity if we've hit the depth limit

        return 1.0 + (
            self._operand._complexity_depth_limited(max_depth - 1)
            if hasattr(self._operand, "_complexity_depth_limited")
            else self._operand.complexity()
        )

    @overrides
    def replace_with(self, index: ExpressionIndex, expr: Expression) -> Expression:
        if not index.indices:
            return expr
        if index.indices[0] == 0:
            remaining_index = ExpressionIndex(index.indices[1:])
            new_operand = self._operand.replace_with(remaining_index, expr)
            return ChangedSign(new_operand)
        raise IndexError("ChangedSign has only one operand at index 0")

    @overrides
    def negated(self) -> Expression:
        """Cancel out double negation."""
        # If operand is also a ChangedSign, return its operand (cancels out double negation)
        if isinstance(self._operand, ChangedSign):
            return self._operand.operand
        # Otherwise return the operand (single negation cancellation)
        return self._operand

    @overrides
    def __repr__(self):
        operand_str = str(self._operand)
        # Add parentheses around complex expressions for clarity, but not around Inverted
        # since -1/x is clearer than -(1/x)
        if isinstance(self._operand, (Addition, Multiplication, ChangedSign)):
            operand_str = f"({operand_str})"
        return f"-{operand_str}"

    @overrides
    def __eq__(self, other):
        return isinstance(other, ChangedSign) and self._operand == other.operand


class Inverted(Expression):
    """Division by expression (1/x operation)."""

    _operand: Expression

    def __init__(self, operand: Expression):
        self._operand: Expression = operand

    @property
    def operand(self) -> Expression:
        """The operand being inverted."""
        return self._operand

    @overrides
    def maximum_power_of_unknown(self) -> int:
        """For division (1/operand), return negative of operand's power."""
        return -self._operand.maximum_power_of_unknown()

    @overrides
    def to_sympy_expr(self) -> sp.Expr:
        # Add recursion protection to prevent infinite loops
        return self._to_sympy_expr_depth_limited(max_depth=50)

    @overrides
    def _to_sympy_expr_depth_limited(self, max_depth: int) -> sp.Expr:
        if max_depth <= 0:
            # Return a simple placeholder if we hit depth limit
            return sp.Integer(1)

        operand_expr = (
            self._operand._to_sympy_expr_depth_limited(max_depth - 1)
            if hasattr(self._operand, "_to_sympy_expr_depth_limited")
            else self._operand.to_sympy_expr()
        )
        return 1 / operand_expr

    @overrides
    def random_subexpression(self, random_stream: RandomClass) -> ExpressionIndex:
        choices = [ExpressionIndex([]), ExpressionIndex([0])]
        choice = random_stream.choice(choices)
        if choice.indices == [0]:
            sub_index = self._operand.random_subexpression(random_stream)
            return ExpressionIndex([0] + sub_index.indices)
        return choice

    @overrides
    def __getitem__(self, index: ExpressionIndex) -> Expression:
        if not index.indices:
            return self
        if index.indices[0] == 0:
            remaining_index = ExpressionIndex(index.indices[1:])
            return self._operand[remaining_index]
        raise IndexError("Inverted has only one operand at index 0")

    @overrides
    def complexity(self) -> float:
        # Use depth-limited complexity calculation to prevent infinite recursion
        return self._complexity_depth_limited(max_depth=50)

    @overrides
    def _complexity_depth_limited(self, max_depth: int) -> float:
        if max_depth <= 0:
            return 2.0  # Return base complexity if we've hit the depth limit

        return 2.0 + (
            self._operand._complexity_depth_limited(max_depth - 1)
            if hasattr(self._operand, "_complexity_depth_limited")
            else self._operand.complexity()
        )

    @overrides
    def replace_with(self, index: ExpressionIndex, expr: Expression) -> Expression:
        if not index.indices:
            return expr
        if index.indices[0] == 0:
            remaining_index = ExpressionIndex(index.indices[1:])
            new_operand = self._operand.replace_with(remaining_index, expr)
            return Inverted(new_operand)
        raise IndexError("Inverted has only one operand at index 0")

    @overrides
    def inverted(self) -> Expression:
        """Cancel out double inversion."""
        # If operand is also an Inverted, return its operand (cancels out double inversion)
        if isinstance(self._operand, Inverted):
            return self._operand.operand
        # Otherwise return the operand (single inversion cancellation)
        return self._operand

    @overrides
    def __repr__(self):
        operand_str = str(self._operand)
        # Add parentheses around complex expressions for clarity in denominator
        # Include Inverted to handle cases like 1/(1/x)
        if isinstance(self._operand, (Addition, Multiplication, ChangedSign, Inverted)):
            operand_str = f"({operand_str})"
        return f"1/{operand_str}"

    @overrides
    def __eq__(self, other):
        return isinstance(other, Inverted) and self._operand == other.operand


class Equals(Expression):
    """Equation with left and right sides."""

    _left: Expression
    _right: Expression

    def __init__(self, left: Expression, right: Expression):
        self._left: Expression = left
        self._right: Expression = right

    @property
    def left(self) -> Expression:
        """The left side of the equation."""
        return self._left

    @property
    def right(self) -> Expression:
        """The right side of the equation."""
        return self._right

    @classmethod
    def from_solution(cls, solution: int, swap: bool = False) -> Equals:
        """Create trivial equation x == solution or solution == x."""
        unknown = Unknown()
        integer = Integer(solution)
        if swap:
            return cls(integer, unknown)
        else:
            return cls(unknown, integer)

    @overrides
    def maximum_power_of_unknown(self) -> int:
        """For equations, return the maximum power between left and right sides."""
        return max(
            self._left.maximum_power_of_unknown(),
            self._right.maximum_power_of_unknown(),
        )

    @overrides
    def to_sympy_expr(self) -> sp.Expr:
        # Return the equation as an expression (left - right = 0)
        return self._left.to_sympy_expr() - self._right.to_sympy_expr()

    @overrides
    def random_subexpression(self, random_stream: RandomClass) -> ExpressionIndex:
        choices = [ExpressionIndex([0]), ExpressionIndex([1])]  # left or right side
        choice = random_stream.choice(choices)
        if choice.indices[0] == 0:
            sub_index = self._left.random_subexpression(random_stream)
            return ExpressionIndex([0] + sub_index.indices)
        else:
            sub_index = self._right.random_subexpression(random_stream)
            return ExpressionIndex([1] + sub_index.indices)

    @overrides
    def __getitem__(self, index: ExpressionIndex) -> Expression:
        if not index.indices:
            return self
        side_idx = index.indices[0]
        remaining_index = ExpressionIndex(index.indices[1:])
        if side_idx == 0:
            return self._left[remaining_index]
        elif side_idx == 1:
            return self._right[remaining_index]
        else:
            raise IndexError("Equals has only left (0) and right (1) sides")

    @overrides
    def complexity(self) -> float:
        return self._left.complexity() + self._right.complexity()

    @overrides
    def replace_with(self, index: ExpressionIndex, expr: Expression) -> Expression:
        if not index.indices:
            return expr

        side_idx = index.indices[0]
        remaining_index = ExpressionIndex(index.indices[1:])

        if side_idx == 0:
            new_left = self._left.replace_with(remaining_index, expr)
            return Equals(new_left, self._right)
        elif side_idx == 1:
            new_right = self._right.replace_with(remaining_index, expr)
            return Equals(self._left, new_right)
        else:
            raise IndexError("Equals has only left (0) and right (1) sides")

    def multiply_sides_by(self, expr: Expression, left_side: bool) -> Equals:
        """Multiply both sides by an expression."""
        new_left = self._left.multiply_by(expr, left_side)
        new_right = self._right.multiply_by(expr, left_side)
        return Equals(new_left, new_right)

    def add_to_sides(self, expr: Expression, left_side: bool) -> Equals:
        """Add an expression to both sides of an equation."""
        new_left = self._left.add_expression(expr, left_side)
        new_right = self._right.add_expression(expr, left_side)
        return Equals(new_left, new_right)

    def swap_side_of_element(self, elem_index: int) -> Equals:
        """Swap sides of an element, changing operation as needed."""
        # This is a complex operation that depends on the structure
        # For now, implement a basic version
        # TODO: Implement proper element swapping logic
        return self

    @overrides
    def __repr__(self):
        return f"{self._left} = {self._right}"


class ParenthesizedExpression(Expression):
    """Wrapper that forces parentheses around an expression in string representation."""

    _operand: Expression

    def __init__(self, operand: Expression):
        self._operand = operand

    @property
    def operand(self) -> Expression:
        """The wrapped operand."""
        return self._operand

    @overrides
    def maximum_power_of_unknown(self) -> int:
        """Return the same power as the operand."""
        return self._operand.maximum_power_of_unknown()

    @overrides
    def to_sympy_expr(self) -> sp.Expr:
        return self._operand.to_sympy_expr()

    @overrides
    def random_subexpression(self, random_stream: RandomClass) -> ExpressionIndex:
        sub_index = self._operand.random_subexpression(random_stream)
        return ExpressionIndex([0] + sub_index.indices)

    @overrides
    def __getitem__(self, index: ExpressionIndex) -> Expression:
        if not index.indices:
            return self
        if index.indices[0] == 0:
            remaining_index = ExpressionIndex(index.indices[1:])
            return self._operand[remaining_index]
        raise IndexError("ParenthesizedExpression has only one operand at index 0")

    @overrides
    def complexity(self) -> float:
        return self._operand.complexity()

    @overrides
    def replace_with(self, index: ExpressionIndex, expr: Expression) -> Expression:
        if not index.indices:
            return expr
        if index.indices[0] == 0:
            remaining_index = ExpressionIndex(index.indices[1:])
            new_operand = self._operand.replace_with(remaining_index, expr)
            return ParenthesizedExpression(new_operand)
        raise IndexError("ParenthesizedExpression has only one operand at index 0")

    @overrides
    def negated(self) -> Expression:
        """Negate the wrapped operand and keep parentheses."""
        return ParenthesizedExpression(self._operand.negated())

    @overrides
    def __repr__(self):
        return f"({self._operand})"

    @overrides
    def __eq__(self, other):
        return (
            isinstance(other, ParenthesizedExpression)
            and self._operand == other.operand
        )
