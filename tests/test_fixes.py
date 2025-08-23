"""
Test script to verify the fixes for both issues:
1. NEGATE complication with 50% probability
2. Better complexity scaling for high target values
"""

import random
from algebra_sofii.cli import generate_equation_with_complexity


def test_negate_probability():
    """Test that NEGATE complication happens with roughly 50% probability."""
    # Generate multiple equations and count negate operations
    negate_count = 0
    total_tests = 100

    for i in range(total_tests):
        random_stream = random.Random(i)
        equation = generate_equation_with_complexity(random_stream, 5, 10.0)

        # Check if the equation contains ChangedSign (negation)
        equation_str = str(equation)
        if "-(" in equation_str:  # Simple check for negation
            negate_count += 1

    negate_percentage = (negate_count / total_tests) * 100

    # Assert that negation happens with reasonable frequency (30-70% range)
    assert 30 <= negate_percentage <= 70, (
        f"NEGATE percentage {negate_percentage:.1f}% is outside expected range 30-70%"
    )


def test_complexity_scaling():
    """Test that high complexity targets generate appropriately complex equations."""
    test_cases = [
        (50, "Low complexity", 42),
        (500, "Medium complexity", 43),
        (5000, "High complexity", 44),
    ]

    complexities = []

    for target_complexity, description, seed in test_cases:
        random_stream = random.Random(seed)  # Different seed for each test case
        equation = generate_equation_with_complexity(
            random_stream, 5, target_complexity
        )
        actual_complexity = equation.complexity()

        # Verify solution still works
        left_val = equation.left.evaluate(5)
        right_val = equation.right.evaluate(5)
        assert abs(left_val - right_val) < 1e-10, (
            f"Solution verification failed for {description}"
        )

        # Store complexity for trend analysis
        complexities.append((target_complexity, actual_complexity))

    # Verify that the highest target produces the highest complexity overall
    # (allowing for some variance in the middle values)
    low_complexity = complexities[0][1]  # target 50
    high_complexity = complexities[2][1]  # target 5000

    assert high_complexity > low_complexity * 2, (
        f"High complexity target should produce significantly higher complexity: "
        f"{high_complexity} should be > {low_complexity * 2}"
    )


def test_specific_high_complexity():
    """Test the specific case mentioned in the problem (target complexity 5000)."""
    random_stream = random.Random(42)
    equation = generate_equation_with_complexity(random_stream, 8, 5000)
    actual_complexity = equation.complexity()

    # Should be much higher than the previous 36.0
    assert actual_complexity > 100, (
        f"High complexity target should generate complexity > 100, got {actual_complexity:.1f}"
    )

    # Verify solution
    left_val = equation.left.evaluate(8)
    right_val = equation.right.evaluate(8)
    assert abs(left_val - right_val) < 1e-10, (
        "Solution verification failed for high complexity equation"
    )


def test_negate_complication_structure():
    """Test that NEGATE complication is applied to subexpressions, not entire sides."""
    # Generate several equations to test the fix
    for seed in [42, 123, 456]:
        random_stream = random.Random(seed)
        equation = generate_equation_with_complexity(random_stream, 2, 20)

        eq_str = str(equation)

        # Should not have the problematic ---- pattern
        assert "----" not in eq_str, f"Equation should not have ---- pattern: {eq_str}"

        # Verify solution
        left_val = equation.left.evaluate(2)
        right_val = equation.right.evaluate(2)
        assert abs(left_val - right_val) < 1e-10, (
            f"Solution verification failed for seed {seed}"
        )
