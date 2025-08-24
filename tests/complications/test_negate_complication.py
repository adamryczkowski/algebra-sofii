"""Tests for NegateComplication class."""

import pytest
from algebra_sofii.complications import NegateComplication
from algebra_sofii.expressions import Integer, Unknown, ExpressionIndex, Equals
from algebra_sofii import RandomClass


def test_negate_complication_init():
    """Test NegateComplication initialization."""
    index = ExpressionIndex([0])
    complication = NegateComplication(index)

    assert complication.index == index


def test_negate_complication_minimal_complexity():
    """Test that minimal_complexity returns expected value."""
    index = ExpressionIndex([0])
    complication = NegateComplication(index)

    # Double negate wraps expression in two ChangedSign layers, adding 2.0 complexity
    assert complication.minimal_complexity == 2.0


def test_negate_complication_maximal_complexity():
    """Test that maximal_complexity returns expected value."""
    index = ExpressionIndex([0])
    complication = NegateComplication(index)

    # For Negate, max is same as min since complexity is deterministic
    assert complication.maximal_complexity == 2.0


def test_negate_complication_apply():
    """Test applying NegateComplication to an expression."""
    index = ExpressionIndex([0])  # Target left side of equation
    complication = NegateComplication(index)

    # Apply to x = 5 (use equation instead of just Unknown)
    original = Equals(Unknown(), Integer(5))
    result = complication.apply(original)

    # Should create: -(-x) = 5 (double negation, which is a no-op)
    assert isinstance(result, Equals)
    from algebra_sofii.expressions import ChangedSign

    assert isinstance(result.left, ChangedSign)
    assert isinstance(result.left.operand, ChangedSign)
    assert result.left.operand.operand == Unknown()


def test_negate_complication_randomize_from_stream():
    """Test static factory method for random generation."""
    random_stream = RandomClass.FromFixedSeed(42)
    base_expr = Unknown()
    complexity_budget = 2.0

    complication = NegateComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    assert isinstance(complication, NegateComplication)
    assert complication.minimal_complexity <= complexity_budget


def test_negate_complication_randomize_insufficient_budget():
    """Test randomize_from_stream with insufficient complexity budget."""
    random_stream = RandomClass.FromFixedSeed(42)
    base_expr = Unknown()
    complexity_budget = 1.5  # Less than minimal_complexity of 2.0

    result = NegateComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    # Should return None when budget is insufficient
    assert result is None


@pytest.mark.parametrize("complexity_budget", [2.0, 3.0, 5.0])
def test_negate_complication_respects_complexity_budget(complexity_budget):
    """Test that generated complications respect complexity budget."""
    random_stream = RandomClass.FromFixedSeed(42)
    base_expr = Unknown()

    complication = NegateComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    if complication is not None:
        assert complication.minimal_complexity <= complexity_budget
