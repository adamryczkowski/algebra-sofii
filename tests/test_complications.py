"""
Tests for the complication system.
"""

import pytest
import sympy as sp

from algebra_sofii.complications import (
    EquationComplication,
    EquationElementMove,
    EquationWithSolution,
    ExpressionComplication,
    OperationType,
)
from algebra_sofii.expressions import (
    Addition,
    Equals,
    ExpressionIndex,
    Integer,
    Multiplication,
    Unknown,
)


class TestOperationType:
    """Test the OperationType enum."""

    def test_enum_values(self):
        """Test that all expected operation types exist."""
        assert OperationType.ADD_ZERO.value == "add_zero"
        assert OperationType.MULTIPLY_BY_ONE.value == "multiply_by_one"
        assert OperationType.ADD.value == "add"
        assert OperationType.MULTIPLY.value == "multiply"


class TestExpressionComplication:
    """Test the ExpressionComplication class."""

    @pytest.fixture
    def simple_expr(self):
        """Simple expression for testing: 2 * x."""
        return Multiplication([Integer(2), Unknown()])

    def test_add_zero_complication(self, simple_expr):
        """Test adding zero complication."""
        index = ExpressionIndex([0])  # Target the coefficient
        added_expr = Integer(3)
        complication = ExpressionComplication(index, OperationType.ADD_ZERO, added_expr)

        result = complication.apply(simple_expr)

        # Should still evaluate to the same value
        original_value = simple_expr.evaluate(5)
        new_value = result.evaluate(5)
        assert abs(original_value - new_value) < 1e-10

        # But should be more complex
        assert result.complexity() > simple_expr.complexity()

    def test_multiply_by_one_complication(self, simple_expr):
        """Test multiply by one complication."""
        index = ExpressionIndex([0])  # Target the coefficient
        mult_expr = Integer(4)
        complication = ExpressionComplication(
            index, OperationType.MULTIPLY_BY_ONE, mult_expr
        )

        result = complication.apply(simple_expr)

        # Should still evaluate to the same value
        original_value = simple_expr.evaluate(7)
        new_value = result.evaluate(7)
        assert abs(original_value - new_value) < 1e-10

        # But should be more complex
        assert result.complexity() > simple_expr.complexity()

    def test_complexity_calculation(self):
        """Test complexity calculation for expression complications."""
        expr = Integer(3)
        index = ExpressionIndex([])

        add_zero_comp = ExpressionComplication(index, OperationType.ADD_ZERO, expr)
        mult_one_comp = ExpressionComplication(
            index, OperationType.MULTIPLY_BY_ONE, expr
        )

        # Multiply by one should add more complexity than add zero
        add_complexity = add_zero_comp.complexity(expr)
        mult_complexity = mult_one_comp.complexity(expr)

        assert mult_complexity > add_complexity
        assert add_complexity == expr.complexity() + 2.0
        assert mult_complexity == expr.complexity() + 3.0

    def test_invalid_operation_raises_error(self, simple_expr):
        """Test that invalid operations raise appropriate errors."""
        index = ExpressionIndex([0])
        expr = Integer(3)

        # Should raise error for equation operations on expressions
        with pytest.raises(ValueError):
            complication = ExpressionComplication(index, OperationType.ADD, expr)
            complication.apply(simple_expr)


class TestEquationComplication:
    """Test the EquationComplication class."""

    @pytest.fixture
    def simple_equation(self):
        """Simple equation for testing: x = 5."""
        return Equals(Unknown(), Integer(5))

    def test_add_complication(self, simple_equation):
        """Test adding to both sides of equation."""
        addend = Integer(3)
        complication = EquationComplication(OperationType.ADD, addend)

        result = complication.apply(simple_equation)

        # Should be an equation with additions on both sides
        assert isinstance(result, Equals)
        assert isinstance(result.left, Addition)
        assert isinstance(result.right, Addition)

        # Should still solve to the same value
        # x + 3 = 5 + 3 should still solve to x = 5
        left_val = result.left.evaluate(5)
        right_val = result.right.evaluate(5)
        assert abs(left_val - right_val) < 1e-10

    def test_multiply_complication(self, simple_equation):
        """Test multiplying both sides of equation."""
        multiplier = Integer(2)
        complication = EquationComplication(OperationType.MULTIPLY, multiplier)

        result = complication.apply(simple_equation)

        # Should be an equation with multiplications on both sides
        assert isinstance(result, Equals)
        assert isinstance(result.left, Multiplication)
        assert isinstance(result.right, Multiplication)

        # Should still solve to the same value
        left_val = result.left.evaluate(5)
        right_val = result.right.evaluate(5)
        assert abs(left_val - right_val) < 1e-10

    def test_complexity_calculation(self, simple_equation):
        """Test complexity calculation for equation complications."""
        expr = Integer(3)

        add_comp = EquationComplication(OperationType.ADD, expr)
        mult_comp = EquationComplication(OperationType.MULTIPLY, expr)

        add_complexity = add_comp.complexity(simple_equation)
        mult_complexity = mult_comp.complexity(simple_equation)

        # Should add complexity based on expression complexity * 2
        assert add_complexity == expr.complexity() * 2
        assert mult_complexity == expr.complexity() * 2 + 1

    def test_non_equation_raises_error(self):
        """Test that applying to non-equations raises error."""
        expr = Integer(5)
        complication = EquationComplication(OperationType.ADD, Integer(3))

        with pytest.raises(ValueError):
            complication.apply(expr)


class TestEquationElementMove:
    """Test the EquationElementMove class."""

    def test_creation(self):
        """Test creating equation element move complications."""
        move = EquationElementMove(right_side=True, elem_index=0)
        assert move.right_side is True
        assert move.elem_index == 0

    def test_complexity_is_minimal(self):
        """Test that element moves add minimal complexity."""
        move = EquationElementMove(right_side=False, elem_index=1)
        equation = Equals(Unknown(), Integer(5))

        complexity = move.complexity(equation)
        assert complexity == 1.0


class TestEquationWithSolution:
    """Test the EquationWithSolution container class."""

    @pytest.mark.parametrize("solution", [1, 3, 5, 7, 9])
    def test_creation_and_verification(self, solution):
        """Test creating equations with solutions and verifying them."""
        eq_with_sol = EquationWithSolution(solution)

        assert eq_with_sol.solution == solution
        assert len(eq_with_sol.complications) == 0
        assert eq_with_sol.verify_solution()

        # Current equation should be x = solution
        current = eq_with_sol.get_current_equation()
        assert isinstance(current, Equals)

    def test_swapped_creation(self, solution_values):
        """Test creating swapped equations."""
        eq_with_sol = EquationWithSolution(solution_values, swap=True)
        current = eq_with_sol.get_current_equation()

        # Should be solution = x instead of x = solution
        assert isinstance(current, Equals)
        assert isinstance(current.left, Integer)
        assert isinstance(current.right, Unknown)
        assert current.left.value == solution_values

    def test_applying_complications_preserves_solution(self, random_stream):
        """Test that applying complications preserves the solution."""
        solution = 6
        eq_with_sol = EquationWithSolution(solution)

        # Apply several complications
        for _ in range(3):
            complication = eq_with_sol.random_complication(10.0, random_stream)
            eq_with_sol.apply_complication(complication)

            # Solution should still be preserved
            assert eq_with_sol.verify_solution()
            assert eq_with_sol.solution == solution

    def test_complexity_increases_with_complications(self, random_stream):
        """Test that complexity increases as complications are added."""
        eq_with_sol = EquationWithSolution(4)
        initial_complexity = eq_with_sol.get_total_complexity()

        # Add a complication
        complication = eq_with_sol.random_complication(20.0, random_stream)
        eq_with_sol.apply_complication(complication)

        new_complexity = eq_with_sol.get_total_complexity()
        assert new_complexity > initial_complexity

    def test_random_complication_respects_complexity_limits(self, random_stream):
        """Test that random complications respect complexity limits."""
        eq_with_sol = EquationWithSolution(3)
        max_complexity = 5.0

        # Generate multiple complications within limit
        for _ in range(5):
            current_complexity = eq_with_sol.get_total_complexity()
            if current_complexity >= max_complexity:
                break

            complication = eq_with_sol.random_complication(
                max_complexity, random_stream
            )
            eq_with_sol.apply_complication(complication)

            # Should not exceed the limit by too much
            new_complexity = eq_with_sol.get_total_complexity()
            assert new_complexity <= max_complexity + 3.0  # Allow some tolerance

    def test_complication_types_are_varied(self, random_stream):
        """Test that different types of complications are generated."""
        eq_with_sol = EquationWithSolution(7)
        complication_types = set()

        # Generate many complications to see variety
        for _ in range(20):
            complication = eq_with_sol.random_complication(15.0, random_stream)
            complication_types.add(type(complication))

        # Should have multiple types
        assert len(complication_types) >= 2

    def test_cache_updates_correctly(self, random_stream):
        """Test that cached current form updates correctly."""
        eq_with_sol = EquationWithSolution(5)

        # Get initial form
        initial_form = eq_with_sol.get_current_equation()
        initial_complexity = initial_form.complexity()

        # Apply complication
        complication = eq_with_sol.random_complication(10.0, random_stream)
        eq_with_sol.apply_complication(complication)

        # Cached form should be updated
        new_form = eq_with_sol.get_current_equation()
        new_complexity = new_form.complexity()

        assert new_complexity > initial_complexity
        assert new_form != initial_form


class TestComplicationIntegration:
    """Integration tests for the complication system."""

    def test_multiple_complications_preserve_solution(self, random_stream):
        """Test that multiple complications preserve solution correctness."""
        for solution in [1, 4, 7]:
            eq_with_sol = EquationWithSolution(solution)

            # Apply many complications
            for _ in range(10):
                if eq_with_sol.get_total_complexity() > 25.0:
                    break

                complication = eq_with_sol.random_complication(30.0, random_stream)
                eq_with_sol.apply_complication(complication)

            # Should still solve correctly
            assert eq_with_sol.verify_solution()

    def test_complicated_equations_are_solvable(self, random_stream):
        """Test that complicated equations remain mathematically valid."""
        eq_with_sol = EquationWithSolution(6)

        # Add substantial complications
        for _ in range(5):
            complication = eq_with_sol.random_complication(20.0, random_stream)
            eq_with_sol.apply_complication(complication)

        current_eq = eq_with_sol.get_current_equation()

        # Should convert to sympy without errors
        sympy_eq = current_eq.to_sympy_expr()
        # Should be an expression (left - right = 0)
        assert isinstance(sympy_eq, sp.Expr)
        # When evaluated with the solution, should equal zero
        x = sp.Symbol("x")
        result = sympy_eq.subs(x, 6)
        assert abs(result) < 1e-10  # Should be approximately zero

        # Should still verify solution
        assert eq_with_sol.verify_solution()
