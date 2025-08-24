"""Tests for MultiplyByOneComplication class."""

import pytest
import random

from algebra_sofii.complications import MultiplyByOneComplication
from algebra_sofii.expressions import Integer, Unknown, Equals, ExpressionIndex
from algebra_sofii.random_class import RandomClass


def test_multiply_by_one_complication_init():
    """Test MultiplyByOneComplication initialization."""
    expr = Integer(5)
    index = ExpressionIndex([0])
    complication = MultiplyByOneComplication(index, expr)

    assert complication.expr == expr
    assert complication.index == index


def test_multiply_by_one_complication_minimal_complexity():
    """Test that minimal_complexity returns expected value."""
    expr = Integer(5)
    index = ExpressionIndex([0])
    complication = MultiplyByOneComplication(index, expr)

    # Should be expr.complexity() + 2.0 (multiplication + division structure)
    expected = expr.complexity() + 2.0
    assert complication.minimal_complexity == expected


def test_multiply_by_one_complication_maximal_complexity():
    """Test that maximal_complexity returns expected value."""
    expr = Integer(5)
    index = ExpressionIndex([0])
    complication = MultiplyByOneComplication(index, expr)

    # Should be same as minimal_complexity
    assert complication.maximal_complexity == complication.minimal_complexity


def test_multiply_by_one_complication_apply():
    """Test applying MultiplyByOneComplication to an expression."""
    expr = Integer(5)
    index = ExpressionIndex([])
    complication = MultiplyByOneComplication(index, expr)
    base_expr = Unknown()

    result = complication.apply(base_expr)

    # Should replace with expr * (base_expr / expr) = 5 * (x / 5)
    assert "5" in str(result) and "x" in str(result)


def test_multiply_by_one_complication_apply_invalid_index():
    """Test applying MultiplyByOneComplication with invalid index raises error."""
    expr = Integer(5)
    index = ExpressionIndex([99])  # Invalid index
    complication = MultiplyByOneComplication(index, expr)
    base_expr = Unknown()

    with pytest.raises(IndexError):
        complication.apply(base_expr)


def test_multiply_by_one_complication_randomize_from_stream():
    """Test static factory method for random generation."""
    random.seed(42)  # Set seed for reproducibility
    random_stream = RandomClass()  # Use current random state
    base_expr = Equals(Unknown(), Integer(5))  # Use equation as base
    complexity_budget = 5.0

    complication = MultiplyByOneComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    if complication is not None:
        assert isinstance(complication, MultiplyByOneComplication)
        assert complication.minimal_complexity <= complexity_budget


@pytest.mark.parametrize("complexity_budget", [3.0, 4.0, 5.0, 10.0])
def test_multiply_by_one_complication_respects_complexity_budget(complexity_budget):
    """Test that generated complications respect complexity budget."""
    random.seed(42)  # Set seed for reproducibility
    random_stream = RandomClass()  # Use current random state
    base_expr = Equals(Unknown(), Integer(5))  # Use equation as base

    complication = MultiplyByOneComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    if complication is not None:
        assert complication.minimal_complexity <= complexity_budget
