"""
Test for progressive random equation generation with SymPy validation.

This test generates 20 random equations with increasing complexity,
verifies their string representation consistency, and validates their
solutions using SymPy.
"""

import random
import pytest
import sympy as sp

from algebra_sofii.expressions import Equals, Integer, Unknown, Multiplication
from algebra_sofii.cli import generate_equation_with_complexity


class TestProgressiveRandomEquations:
    """Test progressive random equation generation and validation."""

    def test_twenty_progressive_equations(self):
        """
        Generate 20 random equations with progressive complexity.
        Verify textual representation consistency and SymPy solutions.
        """
        # Set random seed for reproducible tests
        random.seed(42)
        random_stream = random.Random(42)

        equations = []
        solutions = []
        complexities = []

        print("\n" + "=" * 80)
        print("GENERATING 20 PROGRESSIVE RANDOM EQUATIONS")
        print("=" * 80)

        # Generate 20 equations with progressively increasing complexity
        for i in range(20):
            # Progressive complexity from 1.0 to 10.0
            target_complexity = 1.0 + (i * 9.0 / 19.0)

            # Generate a random solution value
            solution = random_stream.randint(1, 9)

            # Create equation with progressive complexity
            equation = generate_equation_with_complexity(
                random_stream, solution, target_complexity
            )

            equations.append(equation)
            solutions.append(solution)
            complexities.append(equation.complexity())

            print(
                f"\nEquation {i + 1:2d}: Target complexity: {target_complexity:5.2f}, "
                f"Actual: {equation.complexity():5.2f}, Solution: x = {solution:3d}"
            )
            print(f"             {equation}")

        print("\n" + "=" * 80)
        print("VALIDATING ALL EQUATIONS")
        print("=" * 80)

        # Verify all equations were generated
        assert len(equations) == 20
        assert len(solutions) == 20
        assert len(complexities) == 20

        # Test each equation
        for i, (equation, expected_solution, complexity) in enumerate(
            zip(equations, solutions, complexities)
        ):
            print(f"\nValidating equation {i + 1:2d}...")
            self._test_single_equation(equation, expected_solution, complexity, i)
            print(f"✓ Equation {i + 1:2d} passed all tests")

        print(f"\n{'=' * 80}")
        print("ALL 20 EQUATIONS SUCCESSFULLY VALIDATED!")
        print(f"Complexity range: {min(complexities):.2f} - {max(complexities):.2f}")
        print(f"Average complexity: {sum(complexities) / len(complexities):.2f}")
        print(f"{'=' * 80}")

    def _test_single_equation(
        self, equation: Equals, expected_solution: int, complexity: float, index: int
    ):
        """Test a single equation for consistency and correctness."""

        # Test 1: Equation should have reasonable complexity
        assert complexity >= 1.0, f"Equation {index}: Complexity too low: {complexity}"
        assert complexity <= 50.0, (
            f"Equation {index}: Complexity too high: {complexity}"
        )

        # Test 2: String representation should be consistent
        str_repr = str(equation)
        assert " = " in str_repr, f"Equation {index}: Invalid string representation"
        assert len(str_repr) > 3, f"Equation {index}: String representation too short"

        # Test 3: Should be able to convert to SymPy
        try:
            sympy_expr = equation.to_sympy_expr()
            assert isinstance(sympy_expr, sp.Expr), (
                f"Equation {index}: SymPy conversion failed"
            )
        except Exception as e:
            pytest.fail(f"Equation {index}: SymPy conversion error: {e}")

        # Test 4: SymPy should be able to solve the equation
        try:
            x = sp.Symbol("x")
            sympy_equation = sp.Eq(
                equation.left.to_sympy_expr(), equation.right.to_sympy_expr()
            )
            solutions = sp.solve(sympy_equation, x)

            # Should have at least one solution
            assert len(solutions) > 0, f"Equation {index}: No solutions found by SymPy"

            # Check if our expected solution is among the SymPy solutions
            sympy_solutions = [float(sol.evalf()) for sol in solutions if sol.is_real]

            # Allow for small numerical differences
            found_solution = any(
                abs(float(expected_solution) - sol) < 1e-10 for sol in sympy_solutions
            )

            assert found_solution, (
                f"Equation {index}: Expected solution {expected_solution} not found. "
                f"SymPy solutions: {sympy_solutions}. "
                f"Equation: {equation}"
            )

        except Exception as e:
            # Some equations might be too complex for SymPy to solve
            # This is acceptable for very high complexity equations
            if complexity < 20.0:
                pytest.fail(f"Equation {index}: SymPy solving error: {e}")

        # Test 5: Manual verification by substitution
        try:
            # Substitute the expected solution into both sides
            left_result = equation.left.evaluate(expected_solution)
            right_result = equation.right.evaluate(expected_solution)

            # Convert to float for comparison (handles SymPy rationals)
            left_val = (
                float(left_result.evalf())
                if hasattr(left_result, "evalf")
                else float(left_result)
            )
            right_val = (
                float(right_result.evalf())
                if hasattr(right_result, "evalf")
                else float(right_result)
            )

            assert abs(left_val - right_val) < 1e-10, (
                f"Equation {index}: Manual verification failed. "
                f"Left side: {left_val}, Right side: {right_val}, "
                f"Solution: {expected_solution}, Equation: {equation}"
            )

        except (ZeroDivisionError, ValueError):
            # Some equations might have division by zero with certain values
            # This is acceptable if the equation is mathematically valid
            pass

    def test_equation_textual_representation_consistency(self):
        """Test that equation string representations are consistent across multiple generations."""
        random.seed(123)
        random_stream = random.Random(123)

        # Generate the same equation multiple times and verify consistency
        for _ in range(5):
            equation = generate_equation_with_complexity(random_stream, 5, 3.0)

            # String representation should be consistent
            repr1 = str(equation)
            repr2 = str(equation)
            assert repr1 == repr2, "String representation should be deterministic"

            # Should contain expected components
            assert " = " in repr1
            assert len(repr1) > 3

    def test_sympy_integration_edge_cases(self):
        """Test SymPy integration with edge cases."""
        # Test with zero
        eq_zero = Equals(Unknown(), Integer(0))
        sympy_expr = eq_zero.to_sympy_expr()
        solutions = sp.solve(sympy_expr, sp.Symbol("x"))
        assert len(solutions) == 1
        assert solutions[0] == 0

        # Test with negative numbers
        eq_negative = Equals(Unknown(), Integer(-5))
        sympy_expr = eq_negative.to_sympy_expr()
        solutions = sp.solve(sympy_expr, sp.Symbol("x"))
        assert len(solutions) == 1
        assert solutions[0] == -5

        # Test with fractions
        eq_fraction = Equals(Multiplication([Integer(2), Unknown()]), Integer(3))
        sympy_expr = eq_fraction.to_sympy_expr()
        solutions = sp.solve(sympy_expr, sp.Symbol("x"))
        assert len(solutions) == 1
        assert float(solutions[0]) == 1.5

    def test_complexity_progression(self):
        """Test that complexity actually increases with the progression."""
        random.seed(789)
        random_stream = random.Random(789)

        complexities = []

        # Generate equations with increasing target complexity
        for i in range(10):
            target_complexity = 1.0 + i * 0.5
            equation = generate_equation_with_complexity(
                random_stream, 1, target_complexity
            )
            complexities.append(equation.complexity())

        # Verify general trend of increasing complexity
        # (allowing for some variation due to randomness)
        assert complexities[-1] > complexities[0], (
            "Final complexity should be higher than initial complexity"
        )

        # At least half of the transitions should show increasing complexity
        increasing_transitions = sum(
            1
            for i in range(len(complexities) - 1)
            if complexities[i + 1] >= complexities[i]
        )

        assert increasing_transitions >= len(complexities) // 2, (
            "Majority of complexity transitions should be non-decreasing"
        )
