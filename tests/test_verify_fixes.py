"""Simple verification that both fixes work"""

import random
from algebra_sofii.cli import generate_equation_with_complexity


def test_high_complexity_scaling():
    """Test high complexity scaling (addressing issue 2)."""
    random_stream = random.Random(42)
    equation = generate_equation_with_complexity(random_stream, 8, 5000)
    actual_complexity = equation.complexity()

    # Should be much higher than the previous 36
    assert actual_complexity > 100, (
        f"High complexity scaling failed: {actual_complexity:.1f} should be > 100"
    )

    # Verify solution still works
    left_val = equation.left.evaluate(8)
    right_val = equation.right.evaluate(8)
    assert abs(left_val - right_val) < 1e-10, (
        "Solution verification failed for high complexity equation"
    )


def test_negate_complication_probability():
    """Test NEGATE complication probability (addressing issue 1)."""
    negate_count = 0
    total_tests = 20

    for i in range(total_tests):
        rs = random.Random(i + 100)  # Different seed range
        eq = generate_equation_with_complexity(rs, 5, 20.0)  # Medium complexity
        if "-(" in str(eq):  # Check for negation patterns
            negate_count += 1

    percentage = (negate_count / total_tests) * 100

    # Should be in reasonable range around 50%
    assert 20 <= percentage <= 80, (
        f"NEGATE probability {percentage:.1f}% outside reasonable range 20-80%"
    )


def test_solution_verification_with_complexity():
    """Test that solution verification still works with high complexity."""
    test_cases = [(42, 8, 5000), (123, 5, 1000), (456, 3, 500)]

    for seed, solution, target_complexity in test_cases:
        random_stream = random.Random(seed)
        equation = generate_equation_with_complexity(
            random_stream, solution, target_complexity
        )

        left_val = equation.left.evaluate(solution)
        right_val = equation.right.evaluate(solution)
        assert abs(left_val - right_val) < 1e-10, (
            f"Solution verification failed for seed {seed}, solution {solution}"
        )


def test_both_fixes_integration():
    """Integration test that both fixes work together properly."""
    # Generate a high-complexity equation that should have both fixes applied
    random_stream = random.Random(999)
    equation = generate_equation_with_complexity(random_stream, 7, 100)

    # Should have reasonable complexity
    actual_complexity = equation.complexity()
    assert actual_complexity > 50, (
        f"Complexity should be substantial: {actual_complexity}"
    )

    # Should not have problematic ---- patterns
    eq_str = str(equation)
    assert "----" not in eq_str, f"Should not have ---- patterns: {eq_str}"

    # Should still solve correctly
    left_val = equation.left.evaluate(7)
    right_val = equation.right.evaluate(7)
    assert abs(left_val - right_val) < 1e-10, (
        "Integration test: solution verification failed"
    )
