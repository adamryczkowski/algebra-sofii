"""
Pytest unit tests for testing linear expressions with high complexity.
"""

import pytest
from algebra_sofii.generators import random_expression
from algebra_sofii import RandomClass


def test_high_complexity_linear_expressions():
    """Test that random expressions with high complexity target have maximum power of unknown = 1."""
    random_stream = RandomClass.FromFixedSeed(42)

    # Test with complexity target of 200 as requested
    complexity_target = 200.0

    # Generate several random expressions and check they are linear (power = 1)
    for i in range(10):
        expr = random_expression(random_stream, complexity_target)
        max_power = expr.maximum_power_of_unknown()

        # Assert that the expression is linear (maximum power of unknown should be 1)
        assert max_power == 1, f"Expression {expr} has power {max_power}, expected 1"


def test_various_complexity_targets():
    """Test linear expressions with various high complexity targets."""
    random_stream = RandomClass.FromFixedSeed(123)

    # Test different high complexity values
    complexity_targets = [100.0, 150.0, 200.0, 250.0, 300.0]

    for complexity_target in complexity_targets:
        for i in range(5):
            expr = random_expression(random_stream, complexity_target)
            max_power = expr.maximum_power_of_unknown()

            # Assert that all expressions remain linear
            assert max_power == 1, (
                f"Expression {expr} with complexity target {complexity_target} has power {max_power}, expected 1"
            )


def test_maximum_power_calculation():
    """Test the maximum_power_of_unknown method with known expressions."""
    from algebra_sofii.expressions import (
        Unknown,
        Integer,
        Addition,
        Multiplication,
        ChangedSign,
        Inverted,
    )

    # Test simple cases
    x = Unknown()
    assert x.maximum_power_of_unknown() == 1

    five = Integer(5)
    assert five.maximum_power_of_unknown() == 0

    # Test addition: max(powers)
    addition = Addition([x, five])  # x + 5
    assert addition.maximum_power_of_unknown() == 1

    # Test multiplication: sum(powers)
    multiplication = Multiplication([x, five])  # x * 5
    assert multiplication.maximum_power_of_unknown() == 1

    # Test negation: same power
    negated = ChangedSign(x)  # -x
    assert negated.maximum_power_of_unknown() == 1

    # Test inversion: negative power
    inverted = Inverted(x)  # 1/x
    assert inverted.maximum_power_of_unknown() == -1

    # Test complex expression: 5*x + 3
    complex_expr = Addition([Multiplication([five, x]), Integer(3)])
    assert complex_expr.maximum_power_of_unknown() == 1


def test_quadratic_expression():
    """Test a specific quadratic expression: 56·x^2 = 8·x·(6·x + 4)"""
    from algebra_sofii.expressions import (
        Unknown,
        Integer,
        Addition,
        Multiplication,
        Equals,
    )

    x = Unknown()

    # Build left side: 56·x^2
    # x^2 is represented as x * x
    x_squared = Multiplication([x, x])
    left_side = Multiplication([Integer(56), x_squared])

    # Build right side: 8·x·(6·x + 4)
    # First build (6·x + 4)
    six_x = Multiplication([Integer(6), x])
    inner_expr = Addition([six_x, Integer(4)])

    # Then build 8·x·(6·x + 4)
    eight_x = Multiplication([Integer(8), x])
    right_side = Multiplication([eight_x, inner_expr])

    # Build the equation: 56·x^2 = 8·x·(6·x + 4)
    equation = Equals(left_side, right_side)

    # Verify that the maximum power is 2
    max_power = equation.maximum_power_of_unknown()
    assert max_power == 2, f"Expression {equation} has power {max_power}, expected 2"

    print(f"Built equation: {equation}")
    print(f"Maximum power of unknown: {max_power}")


if __name__ == "__main__":
    pytest.main([__file__])
