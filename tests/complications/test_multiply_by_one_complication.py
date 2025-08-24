"""Tests for MultiplyByOneComplication class."""

import random
import pytest
from algebra_sofii.complications import MultiplyByOneComplication
from algebra_sofii.expressions import (
    Integer,
    Unknown,
    Multiplication,
    ExpressionIndex,
    Equals,
)


def test_multiply_by_one_complication_init():
    """Test MultiplyByOneComplication initialization."""
    index = ExpressionIndex([0])
    expr = Integer(5)
    complication = MultiplyByOneComplication(index, expr)

    assert complication.index == index
    assert complication.expr == expr


def test_multiply_by_one_complication_minimal_complexity():
    """Test that minimal_complexity returns expected value."""
    index = ExpressionIndex([0])
    expr = Integer(5)
    complication = MultiplyByOneComplication(index, expr)

    # MultiplyByOne creates: expr * (original / expr)
    # This adds complexity of: expr.complexity() + 1.0 (for Multiplication) + 1.0 (for Inverted)
    expected_min = expr.complexity() + 2.0
    assert complication.minimal_complexity == expected_min


def test_multiply_by_one_complication_maximal_complexity():
    """Test that maximal_complexity returns expected value."""
    index = ExpressionIndex([0])
    expr = Integer(5)
    complication = MultiplyByOneComplication(index, expr)

    # For MultiplyByOne, max is same as min since complexity is deterministic
    assert complication.maximal_complexity == complication.minimal_complexity


def test_multiply_by_one_complication_apply():
    """Test applying MultiplyByOneComplication to an expression."""
    index = ExpressionIndex([0])  # Target left side of equation
    one_expr = Integer(3)
    complication = MultiplyByOneComplication(index, one_expr)

    # Apply to x = 5 (use equation instead of just Unknown)
    original = Equals(Unknown(), Integer(5))
    result = complication.apply(original)

    # Should create: 3 * (x / 3) = 5
    assert isinstance(result, Equals)
    assert isinstance(result.left, Multiplication)
    assert len(result.left.operands) == 2
    assert result.left.operands[0] == one_expr


def test_multiply_by_one_complication_randomize_from_stream():
    """Test static factory method for random generation."""
    random_stream = random.Random(42)
    base_expr = Equals(Unknown(), Integer(5))  # Use equation as base
    complexity_budget = 5.0

    complication = MultiplyByOneComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    assert isinstance(complication, MultiplyByOneComplication)
    assert complication.minimal_complexity <= complexity_budget


@pytest.mark.parametrize("complexity_budget", [3.0, 4.0, 5.0, 10.0])
def test_multiply_by_one_complication_respects_complexity_budget(complexity_budget):
    """Test that generated complications respect complexity budget."""
    random_stream = random.Random(42)
    base_expr = Equals(Unknown(), Integer(5))  # Use equation as base

    complication = MultiplyByOneComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    if complication is not None:
        assert complication.minimal_complexity <= complexity_budget


def test_multiply_by_one_complication_insufficient_budget():
    """Test that insufficient budget returns None."""
    random_stream = random.Random(42)
    base_expr = Equals(Unknown(), Integer(5))
    complexity_budget = 2.0  # Less than minimum 3.0

    complication = MultiplyByOneComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    assert complication is None
