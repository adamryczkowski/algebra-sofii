"""Tests for InsertBracketsComplication class."""

import random
import pytest
from algebra_sofii.complications import InsertBracketsComplication
from algebra_sofii.expressions import Integer, Unknown, Addition, ExpressionIndex


def test_insert_brackets_complication_init():
    """Test InsertBracketsComplication initialization."""
    index = ExpressionIndex([0])
    first_elem = 0
    second_elem = 2
    negate = False
    complication = InsertBracketsComplication(index, first_elem, second_elem, negate)

    assert complication.index == index
    assert complication.first_elem == first_elem
    assert complication.second_elem == second_elem
    assert complication.negate == negate


def test_insert_brackets_complication_minimal_complexity():
    """Test that minimal_complexity returns expected value."""
    index = ExpressionIndex([0])
    complication = InsertBracketsComplication(index, 0, 2, False)

    # InsertBrackets creates a new Addition node (adds 1.0)
    # Without negation, that's the only complexity increase
    assert complication.minimal_complexity == 1.0


def test_insert_brackets_complication_minimal_complexity_with_negation():
    """Test minimal_complexity with negation."""
    index = ExpressionIndex([0])
    complication = InsertBracketsComplication(index, 0, 2, True)

    # InsertBrackets with negation creates Addition (1.0) + ChangedSign (1.0)
    assert complication.minimal_complexity == 2.0


def test_insert_brackets_complication_maximal_complexity():
    """Test that maximal_complexity returns expected value."""
    index = ExpressionIndex([0])
    complication = InsertBracketsComplication(index, 0, 2, False)

    # For InsertBrackets, max is same as min since complexity is deterministic
    assert complication.maximal_complexity == complication.minimal_complexity


def test_insert_brackets_complication_apply():
    """Test applying InsertBracketsComplication to an expression."""
    # Create an addition with 3 operands: x + 2 + 3
    original = Addition([Unknown(), Integer(2), Integer(3)])
    index = ExpressionIndex([])  # Apply to root

    complication = InsertBracketsComplication(index, 0, 2, False)
    result = complication.apply(original)

    # Should create: (x + 3) + 2
    assert isinstance(result, Addition)
    assert len(result.operands) == 2


def test_insert_brackets_complication_apply_with_negation():
    """Test applying InsertBracketsComplication with negation."""
    original = Addition([Unknown(), Integer(2), Integer(3)])
    index = ExpressionIndex([])

    complication = InsertBracketsComplication(index, 0, 2, True)
    result = complication.apply(original)

    # Should create: -(x + 3) + 2
    assert isinstance(result, Addition)
    assert len(result.operands) == 2


def test_insert_brackets_complication_randomize_from_stream():
    """Test static factory method for random generation."""
    random_stream = random.Random(42)
    # Create base expression with addition having 3+ operands
    base_expr = Addition([Unknown(), Integer(2), Integer(3)])
    complexity_budget = 3.0

    complication = InsertBracketsComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    assert isinstance(complication, InsertBracketsComplication)
    assert complication.minimal_complexity <= complexity_budget


def test_insert_brackets_complication_randomize_no_suitable_additions():
    """Test randomize_from_stream when no suitable additions exist."""
    random_stream = random.Random(42)
    # Base expression without additions with 3+ operands
    base_expr = Unknown()
    complexity_budget = 3.0

    result = InsertBracketsComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    # Should return None when no suitable additions found
    assert result is None


@pytest.mark.parametrize("complexity_budget", [1.0, 2.0, 3.0, 5.0])
def test_insert_brackets_complication_respects_complexity_budget(complexity_budget):
    """Test that generated complications respect complexity budget."""
    random_stream = random.Random(42)
    base_expr = Addition([Unknown(), Integer(2), Integer(3)])

    complication = InsertBracketsComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    if complication is not None:
        assert complication.minimal_complexity <= complexity_budget
