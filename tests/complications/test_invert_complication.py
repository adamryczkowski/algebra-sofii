"""Tests for InvertComplication class."""

import pytest
from algebra_sofii.complications import InvertComplication
from algebra_sofii import RandomClass
from algebra_sofii.expressions import Integer, Unknown, ExpressionIndex, Equals


def test_invert_complication_init():
    """Test InvertComplication initialization."""
    index = ExpressionIndex([0])
    complication = InvertComplication(index)

    assert complication.index == index


def test_invert_complication_minimal_complexity():
    """Test that minimal_complexity returns expected value."""
    index = ExpressionIndex([0])
    complication = InvertComplication(index)

    # Double invert wraps expression in two Inverted layers, adding 2.0 complexity
    assert complication.minimal_complexity == 2.0


def test_invert_complication_maximal_complexity():
    """Test that maximal_complexity returns expected value."""
    index = ExpressionIndex([0])
    complication = InvertComplication(index)

    # For Invert, max is same as min since complexity is deterministic
    assert complication.maximal_complexity == 2.0


def test_invert_complication_apply():
    """Test applying InvertComplication to an expression."""
    index = ExpressionIndex([0])  # Target left side of equation
    complication = InvertComplication(index)

    # Apply to x = 5 (use equation instead of just Unknown)
    original = Equals(Unknown(), Integer(5))
    result = complication.apply(original)

    # Should create: 1/(1/x) = 5 (double inversion, which is a no-op)
    assert isinstance(result, Equals)
    from algebra_sofii.expressions import Inverted

    assert isinstance(result.left, Inverted)
    assert isinstance(result.left.operand, Inverted)
    assert result.left.operand.operand == Unknown()


def test_invert_complication_randomize_from_stream():
    """Test static factory method for random generation."""
    random_stream = RandomClass.FromFixedSeed(42)
    base_expr = Integer(5)  # Use non-zero integer to avoid division by zero
    complexity_budget = 2.0

    complication = InvertComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    assert isinstance(complication, InvertComplication)
    assert complication.minimal_complexity <= complexity_budget


def test_invert_complication_randomize_insufficient_budget():
    """Test randomize_from_stream with insufficient complexity budget."""
    random_stream = RandomClass.FromFixedSeed(42)
    base_expr = Integer(5)
    complexity_budget = 1.5  # Less than minimal_complexity of 2.0

    result = InvertComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    # Should return None when budget is insufficient
    assert result is None


@pytest.mark.parametrize("complexity_budget", [2.0, 3.0, 5.0])
def test_invert_complication_respects_complexity_budget(complexity_budget):
    """Test that generated complications respect complexity budget."""
    random_stream = RandomClass.FromFixedSeed(42)
    base_expr = Integer(5)

    complication = InvertComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    if complication is not None:
        assert complication.minimal_complexity <= complexity_budget
