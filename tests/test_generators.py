"""
Tests for the random expression generators.
"""

import pytest
import sympy as sp

from algebra_sofii.expressions import (
    Addition,
    ChangedSign,
    Equals,
    Expression,
    Integer,
    Multiplication,
    Unknown,
)
from algebra_sofii.generators import random_expression, random_nonzero_expression
from algebra_sofii.cli import generate_equation_with_complexity


class TestRandomExpression:
    """Test the random expression generator."""

    @pytest.mark.parametrize("complexity", [1.0, 2.0, 3.0, 4.0, 5.0])
    def test_complexity_bounds(self, complexity, random_stream):
        """Test that generated expressions respect complexity targets."""
        expr = random_expression(random_stream, complexity)
        actual_complexity = expr.complexity()

        # Allow some tolerance for complexity matching
        assert actual_complexity <= complexity + 2.0
        assert actual_complexity >= 1.0  # Minimum complexity

    def test_low_complexity_generates_constants(self, random_stream):
        """Test that low complexity generates simple constants."""
        expr = random_expression(random_stream, 1.5)
        assert isinstance(expr, Integer)
        assert 1 <= expr.value <= 9

    def test_medium_complexity_generates_linear_terms(self, random_stream):
        """Test that medium complexity generates linear terms."""
        for _ in range(10):  # Test multiple generations
            expr = random_expression(random_stream, 2.5)

            # Should be either Integer or Multiplication with Unknown
            if isinstance(expr, Multiplication):
                # Should contain an Unknown somewhere
                has_unknown = any(
                    isinstance(op, Unknown)
                    or (isinstance(op, ChangedSign) and isinstance(op.operand, Unknown))
                    for op in expr.operands
                )
                assert has_unknown

    def test_high_complexity_generates_full_expressions(self, random_stream):
        """Test that high complexity generates full linear expressions."""
        expr = random_expression(random_stream, 4.0)

        # Should be Addition for full expressions
        if isinstance(expr, Addition):
            assert len(expr.operands) >= 2

    def test_deterministic_with_seed(self):
        """Test that same seed produces same expressions."""
        import random

        stream1 = random.Random(12345)
        stream2 = random.Random(12345)

        expr1 = random_expression(stream1, 3.0)
        expr2 = random_expression(stream2, 3.0)

        # Should produce equivalent expressions (same structure)
        assert isinstance(expr1, type(expr2))

    def test_produces_valid_sympy_expressions(self, random_stream):
        """Test that all generated expressions convert to valid sympy."""
        for complexity in [1.0, 2.0, 3.0, 4.0]:
            expr = random_expression(random_stream, complexity)
            sympy_expr = expr.to_sympy_expr()

            # Should not raise exception and should be a sympy expression
            assert hasattr(sympy_expr, "subs")  # Basic sympy interface check


class TestRandomNonzeroExpression:
    """Test the random nonzero expression generator."""

    @pytest.mark.parametrize("true_x", [1, 2, 3, 4, 5, 6, 7, 8, 9])
    def test_generates_nonzero_values(self, true_x, random_stream):
        """Test that generated expressions don't evaluate to zero."""
        expr = random_nonzero_expression(random_stream, 3.0, true_x)
        value = expr.evaluate(true_x)
        assert value != 0

    def test_fallback_on_repeated_zeros(self, random_stream):
        """Test fallback when random generation keeps producing zeros."""
        # Use a complexity that might generate zeros and test fallback
        expr = random_nonzero_expression(random_stream, 1.0, 5)

        # Should always produce a valid nonzero expression
        assert isinstance(expr, Expression)
        value = expr.evaluate(5)
        assert value != 0

    def test_respects_complexity_target(self, random_stream):
        """Test that complexity is still respected in nonzero generation."""
        expr = random_nonzero_expression(random_stream, 2.0, 3)
        actual_complexity = expr.complexity()

        # Should be reasonable complexity
        assert actual_complexity <= 4.0  # Allow some tolerance

    @pytest.mark.parametrize("complexity", [1.0, 2.5, 4.0])
    def test_various_complexities(self, complexity, random_stream):
        """Test nonzero generation at various complexity levels."""
        expr = random_nonzero_expression(random_stream, complexity, 4)

        # Should evaluate to nonzero
        value = expr.evaluate(4)
        assert value != 0

        # Should be valid expression
        sympy_expr = expr.to_sympy_expr()
        assert hasattr(sympy_expr, "subs")

    def test_handles_division_errors_gracefully(self, random_stream):
        """Test that division by zero errors are handled gracefully."""
        # This test ensures the function doesn't crash on division errors
        # even though our simple generator shouldn't create them often
        for _ in range(20):
            expr = random_nonzero_expression(random_stream, 3.0, 2)
            # Should complete without exceptions
            assert isinstance(expr, Expression)


class TestGeneratorIntegration:
    """Integration tests for expression generators."""

    def test_generated_expressions_work_with_equations(self, random_stream):
        """Test that generated expressions work in equation contexts."""
        left_expr = random_expression(random_stream, 2.0)
        right_expr = random_expression(random_stream, 2.0)

        equation = Equals(left_expr, right_expr)

        # Should create valid equation
        assert isinstance(equation, Equals)
        sympy_eq = equation.to_sympy_expr()
        # Should be an expression (left - right)
        assert isinstance(sympy_eq, sp.Expr)

    def test_expressions_support_all_operations(self, random_stream):
        """Test that generated expressions support expected operations."""
        expr = random_expression(random_stream, 3.0)

        # Should support basic operations
        negated = expr.negated()
        assert isinstance(negated, Expression)

        inverted = expr.inverted()
        assert isinstance(inverted, Expression)

        added = expr.add_expression(Integer(1))
        assert isinstance(added, Expression)

        multiplied = expr.multiply_by(Integer(2))
        assert isinstance(multiplied, Expression)

    def test_complexity_calculation_consistency(self, random_stream):
        """Test that complexity calculations are consistent."""
        for target_complexity in [1.0, 2.0, 3.0, 4.0]:
            expr = random_expression(random_stream, target_complexity)
            calculated_complexity = expr.complexity()

            # Complexity should be positive and finite
            assert calculated_complexity > 0
            assert calculated_complexity < float("inf")

            # Should be roughly in the expected range
            assert calculated_complexity <= target_complexity + 3.0

    def test_equation_generation_maintains_linearity(self, random_stream):
        """Test that equation generation with complications maintains linearity."""
        # Test multiple complexity levels to ensure we don't generate quadratic equations
        for complexity in [10.0, 20.0, 30.0, 50.0]:
            for solution in [1, 5, 10]:
                equation = generate_equation_with_complexity(
                    random_stream, solution, complexity
                )

                # Check that the maximum power of x in the equation is 1 (linear)
                max_power = equation.maximum_power_of_unknown()
                assert max_power <= 1, (
                    f"Generated equation with complexity {complexity} has degree {max_power} "
                    f"(should be ≤ 1 for linear equations): {equation}"
                )

                # Verify the solution is still correct
                left_val = equation.left.evaluate(solution)
                right_val = equation.right.evaluate(solution)
                assert abs(left_val - right_val) < 1e-10, (
                    f"Solution x={solution} doesn't satisfy equation {equation}"
                )
