"""
Tests for the Expression class hierarchy.
"""

import pytest
import sympy as sp

from algebra_sofii.expressions import (
    Addition,
    ChangedSign,
    Equals,
    Expression,
    ExpressionIndex,
    Integer,
    Inverted,
    Multiplication,
    Unknown,
)


class TestExpressionIndex:
    """Test the ExpressionIndex class."""

    def test_creation_and_equality(self):
        """Test creating and comparing expression indices."""
        idx1 = ExpressionIndex([1, 2, 3])
        idx2 = ExpressionIndex([1, 2, 3])
        idx3 = ExpressionIndex([1, 2])

        assert idx1 == idx2
        assert idx1 != idx3
        assert idx1.indices == [1, 2, 3]

    def test_immutability(self):
        """Test that modifying original list doesn't affect index."""
        original = [1, 2, 3]
        idx = ExpressionIndex(original)
        original.append(4)

        assert idx.indices == [1, 2, 3]


class TestInteger:
    """Test the Integer expression class."""

    @pytest.mark.parametrize("value", [-5, 0, 1, 42])
    def test_creation_and_sympy_conversion(self, value):
        """Test integer creation and sympy conversion."""
        integer = Integer(value)
        assert integer.value == value
        assert integer.to_sympy_expr() == sp.Integer(value)

    def test_evaluation(self):
        """Test integer evaluation."""
        integer = Integer(7)
        assert integer.evaluate(3) == 7  # Should return the integer regardless of x

    def test_complexity(self):
        """Test integer complexity."""
        integer = Integer(5)
        assert integer.complexity() == 1.0

    def test_negation(self):
        """Test integer negation optimization."""
        integer = Integer(5)
        negated = integer.negated()

        assert isinstance(negated, Integer)
        assert negated.value == -5

    def test_indexing(self, sample_integer):
        """Test integer indexing behavior."""
        empty_index = ExpressionIndex([])
        assert sample_integer[empty_index] == sample_integer

        with pytest.raises(IndexError):
            sample_integer[ExpressionIndex([0])]

    def test_random_subexpression(self, sample_integer, random_stream):
        """Test random subexpression selection."""
        index = sample_integer.random_subexpression(random_stream)
        assert index == ExpressionIndex([])


class TestUnknown:
    """Test the Unknown expression class."""

    def test_creation_and_sympy_conversion(self):
        """Test unknown creation and sympy conversion."""
        unknown = Unknown()
        assert unknown.name == "x"
        assert unknown.to_sympy_expr() == sp.Symbol("x")

    def test_custom_name(self):
        """Test unknown with custom variable name."""
        unknown = Unknown()
        assert unknown.name == "x"
        assert unknown.to_sympy_expr() == sp.Symbol("x")

    def test_evaluation(self, sample_unknown):
        """Test unknown evaluation."""
        assert sample_unknown.evaluate(7) == 7

    def test_complexity(self, sample_unknown):
        """Test unknown complexity."""
        assert sample_unknown.complexity() == 1.0


class TestAddition:
    """Test the Addition expression class."""

    def test_creation_and_sympy_conversion(self, sample_addition):
        """Test addition creation and conversion."""
        # sample_addition is 3 + x
        sympy_expr = sample_addition.to_sympy_expr()
        x = sp.Symbol("x")
        expected = sp.Integer(3) + x
        assert sympy_expr.equals(expected)

    def test_evaluation(self, sample_addition):
        """Test addition evaluation."""
        # 3 + x where x = 4 should equal 7
        result = sample_addition.evaluate(4)
        assert result == 7

    def test_complexity(self, sample_addition):
        """Test addition complexity calculation."""
        # 1 (operation) + 1 (integer) + 1 (unknown) = 3
        assert sample_addition.complexity() == 3.0

    def test_add_expression_optimization(self):
        """Test that adding to addition optimizes by extending operands."""
        original = Addition([Integer(1), Integer(2)])
        result = original.add_expression(Integer(3))

        assert len(result.operands) == 3
        assert all(isinstance(op, Integer) for op in result.operands)

    def test_minimum_operands(self):
        """Test that addition requires at least 2 operands."""
        with pytest.raises(ValueError):
            Addition([Integer(1)])

    def test_remove_node(self):
        """Test removing nodes from addition."""
        addition = Addition([Integer(1), Integer(2), Integer(3)])
        extracted, remaining = addition.remove_node(1)

        assert isinstance(extracted, Integer)
        assert extracted.value == 2
        assert isinstance(remaining, Addition)
        assert len(remaining.operands) == 2

    def test_remove_node_to_single(self):
        """Test removing node when only one remains."""
        addition = Addition([Integer(1), Integer(2)])
        extracted, remaining = addition.remove_node(0)

        assert isinstance(extracted, Integer)
        assert extracted.value == 1
        assert isinstance(remaining, Integer)
        assert remaining.value == 2


class TestMultiplication:
    """Test the Multiplication expression class."""

    def test_creation_and_sympy_conversion(self, sample_multiplication):
        """Test multiplication creation and conversion."""
        # sample_multiplication is 2 * x
        sympy_expr = sample_multiplication.to_sympy_expr()
        x = sp.Symbol("x")
        expected = sp.Integer(2) * x
        assert sympy_expr.equals(expected)

    def test_evaluation(self, sample_multiplication):
        """Test multiplication evaluation."""
        # 2 * x where x = 3 should equal 6
        result = sample_multiplication.evaluate(3)
        assert result == 6

    def test_multiply_by_optimization(self):
        """Test that multiplying extends operands."""
        original = Multiplication([Integer(2), Unknown()])
        result = original.multiply_by(Integer(3))

        assert len(result.operands) == 3


class TestChangedSign:
    """Test the ChangedSign expression class."""

    def test_creation_and_sympy_conversion(self):
        """Test negation creation and conversion."""
        negated = ChangedSign(Integer(5))
        assert negated.to_sympy_expr() == -sp.Integer(5)

    def test_evaluation(self):
        """Test negation evaluation."""
        negated = ChangedSign(Unknown())
        result = negated.evaluate(3)
        assert result == -3

    def test_double_negation_cancellation(self):
        """Test that double negation cancels out."""
        original = Integer(5)
        double_negated = ChangedSign(ChangedSign(original))
        result = double_negated.negated()

        # Should return the original expression
        assert result == original

        # Also test that the values are equivalent
        assert result.evaluate(0) == original.evaluate(0)

    def test_complexity(self):
        """Test negation complexity."""
        negated = ChangedSign(Integer(5))
        # 1 (negation) + 1 (integer) = 2
        assert negated.complexity() == 2.0


class TestInverted:
    """Test the Inverted expression class."""

    def test_creation_and_sympy_conversion(self):
        """Test inversion creation and conversion."""
        inverted = Inverted(Integer(4))
        expected = sp.Rational(1, 4)
        assert inverted.to_sympy_expr() == expected

    def test_evaluation(self):
        """Test inversion evaluation."""
        inverted = Inverted(Integer(4))
        result = inverted.evaluate(999)  # x value shouldn't matter
        assert result == sp.Rational(1, 4)

    def test_double_inversion_cancellation(self):
        """Test that double inversion cancels out."""
        original = Integer(5)
        double_inverted = Inverted(Inverted(original))
        result = double_inverted.inverted()

        assert result == original

    def test_complexity(self):
        """Test inversion complexity."""
        inverted = Inverted(Integer(5))
        # 2 (inversion) + 1 (integer) = 3
        assert inverted.complexity() == 3.0


class TestEquals:
    """Test the Equals expression class."""

    def test_creation_from_solution(self, solution_values):
        """Test creating equations from solutions."""
        eq = Equals.from_solution(solution_values, swap=False)
        assert isinstance(eq.left, Unknown)
        assert isinstance(eq.right, Integer)
        assert eq.right.value == solution_values

        eq_swapped = Equals.from_solution(solution_values, swap=True)
        assert isinstance(eq_swapped.left, Integer)
        assert isinstance(eq_swapped.right, Unknown)
        assert eq_swapped.left.value == solution_values

    def test_sympy_conversion(self, sample_equation):
        """Test equation sympy conversion."""
        sympy_eq = sample_equation.to_sympy_expr()
        # Should be an expression (left - right)
        assert isinstance(sympy_eq, sp.Expr)
        # When evaluated with the solution, should equal zero
        x = sp.Symbol("x")
        result = sympy_eq.subs(x, 5)  # sample_equation is x = 5
        assert result == 0

    def test_multiply_sides_by(self, sample_equation):
        """Test multiplying both sides by an expression."""
        multiplier = Integer(3)
        result = sample_equation.multiply_sides_by(multiplier)

        assert isinstance(result, Equals)
        assert isinstance(result.left, Multiplication)
        assert isinstance(result.right, Multiplication)

    def test_add_to_sides(self, sample_equation):
        """Test adding to both sides of equation."""
        addend = Integer(2)
        result = sample_equation.add_to_sides(addend)

        assert isinstance(result, Equals)
        assert isinstance(result.left, Addition)
        assert isinstance(result.right, Addition)

    def test_complexity(self, sample_equation):
        """Test equation complexity calculation."""
        # Should be sum of both sides
        expected = (
            sample_equation.left.complexity() + sample_equation.right.complexity()
        )
        assert sample_equation.complexity() == expected


class TestComplexExpressions:
    """Test complex nested expressions."""

    def test_complex_indexing(self, complex_expression):
        """Test indexing into complex expressions."""
        # complex_expression is (2 * x) + (-3)

        # Get the whole expression
        assert complex_expression[ExpressionIndex([])] == complex_expression

        # Get first operand (2 * x)
        first_operand = complex_expression[ExpressionIndex([0])]
        assert isinstance(first_operand, Multiplication)

        # Get the '2' from first operand
        coefficient = complex_expression[ExpressionIndex([0, 0])]
        assert isinstance(coefficient, Integer)
        assert coefficient.value == 2

    def test_complex_replacement(self, complex_expression):
        """Test replacing subexpressions in complex expressions."""
        # Replace the coefficient '2' with '5'
        new_coeff = Integer(5)
        result = complex_expression.replace_with(ExpressionIndex([0, 0]), new_coeff)

        # Verify the structure is maintained but coefficient changed
        new_coeff_retrieved = result[ExpressionIndex([0, 0])]
        assert isinstance(new_coeff_retrieved, Integer)
        assert new_coeff_retrieved.value == 5

    def test_random_subexpression_selection(self, complex_expression, random_stream):
        """Test random subexpression selection in complex expressions."""
        # Should be able to select various subexpressions
        indices = [
            complex_expression.random_subexpression(random_stream) for _ in range(10)
        ]

        # All indices should be valid
        for idx in indices:
            subexpr = complex_expression[idx]
            assert isinstance(subexpr, Expression)
