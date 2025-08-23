"""Direct test of the NEGATE fix"""

import random
from algebra_sofii.cli import generate_equation_with_complexity


def test_negate_direct_fix():
    """Direct test that NEGATE fix works correctly across multiple seeds."""
    test_seeds = [42, 123, 456]

    for seed in test_seeds:
        random_stream = random.Random(seed)
        equation = generate_equation_with_complexity(random_stream, 2, 20)

        eq_str = str(equation)

        # Check for the problematic ---- pattern
        assert "----" not in eq_str, (
            f"Seed {seed}: Still has ---- pattern in equation: {eq_str}"
        )

        # Verify solution
        left_val = equation.left.evaluate(2)
        right_val = equation.right.evaluate(2)
        assert abs(left_val - right_val) < 1e-10, (
            f"Seed {seed}: Solution verification failed"
        )


def test_negation_still_happens():
    """Test that negation complications are still being applied frequently."""
    equations_with_negation = 0
    total_tests = 20

    for i in range(total_tests):
        random_stream = random.Random(i + 1000)  # Different seed range
        equation = generate_equation_with_complexity(random_stream, 3, 25)

        eq_str = str(equation)
        if "-(" in eq_str:  # Simple check for negation patterns
            equations_with_negation += 1

    negation_percentage = (equations_with_negation / total_tests) * 100

    # Should still have reasonable amount of negation (at least 20%)
    assert negation_percentage >= 20, (
        f"Negation should happen frequently, got {negation_percentage:.1f}%"
    )


def test_negate_fix_summary():
    """Test that all aspects of the NEGATE fix are working properly."""
    # Test multiple scenarios
    test_cases = [(42, 2, 20), (100, 5, 15), (200, 8, 30)]

    for seed, solution, complexity in test_cases:
        random_stream = random.Random(seed)
        equation = generate_equation_with_complexity(
            random_stream, solution, complexity
        )

        eq_str = str(equation)

        # 1. No ugly ---- patterns from negating entire sides
        assert "----" not in eq_str, f"No ---- patterns: {eq_str}"

        # 2. Equations still solve correctly
        left_val = equation.left.evaluate(solution)
        right_val = equation.right.evaluate(solution)
        assert abs(left_val - right_val) < 1e-10, f"Solution correct for seed {seed}"

        # 3. Complexity is reasonable
        actual_complexity = equation.complexity()
        assert actual_complexity > 0, (
            f"Complexity should be positive: {actual_complexity}"
        )
