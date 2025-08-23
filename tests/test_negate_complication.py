"""Test the fixed NEGATE complication"""

import random
from algebra_sofii.cli import generate_equation_with_complexity


def test_negate_fix():
    """Test that NEGATE complication no longer creates ---- patterns."""
    # Test with multiple seeds to ensure consistent behavior
    for i in range(5):
        random_stream = random.Random(i + 100)
        equation = generate_equation_with_complexity(random_stream, 2, 20)

        # Verify solution
        left_val = equation.left.evaluate(2)
        right_val = equation.right.evaluate(2)
        assert abs(left_val - right_val) < 1e-10, (
            f"Solution verification failed for test {i + 1}"
        )

        # Check for the problematic pattern
        equation_str = str(equation)
        assert "----" not in equation_str, (
            f"Test {i + 1}: Still has ---- pattern in equation: {equation_str}"
        )


def test_negate_patterns_are_clean():
    """Test that negation patterns in equations are clean and well-formed."""
    test_cases = [(42, 2, 15), (123, 3, 25), (456, 5, 30)]

    for seed, solution, complexity in test_cases:
        random_stream = random.Random(seed)
        equation = generate_equation_with_complexity(
            random_stream, solution, complexity
        )

        equation_str = str(equation)

        # Should not have multiple consecutive minus signs
        assert "--" not in equation_str, (
            f"Equation has consecutive minus signs: {equation_str}"
        )

        # Should not have the problematic quadruple minus pattern
        assert "----" not in equation_str, f"Equation has ---- pattern: {equation_str}"

        # Verify the equation still solves correctly
        left_val = equation.left.evaluate(solution)
        right_val = equation.right.evaluate(solution)
        assert abs(left_val - right_val) < 1e-10, (
            f"Solution verification failed for seed {seed}"
        )
