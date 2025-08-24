"""Tests for MultiplyEquationComplication class."""

"""Tests for AddToEquationComplication class."""
import random
import pytest
from algebra_sofii.complications import MultiplyEquationComplication
from algebra_sofii.expressions import Integer, Unknown, Equals


def test_multiply_equation_complication_init():
    """Test MultiplyEquationComplication initialization."""
    expr = Integer(5)
    complication = MultiplyEquationComplication(expr)

    assert complication.expr == expr


def test_multiply_equation_complication_minimal_complexity():
    """Test that minimal_complexity returns expected value."""
    expr = Integer(5)
    complication = MultiplyEquationComplication(expr)

    # Multiplying both sides duplicates the expression complexity
    # No additional structural complexity since it's just multiplying existing sides
    expected_min = 2 * expr.complexity()
    assert complication.minimal_complexity == expected_min


def test_multiply_equation_complication_maximal_complexity():
    """Test that maximal_complexity returns expected value."""
    expr = Integer(5)
    complication = MultiplyEquationComplication(expr)

    # For MultiplyEquation, max is same as min since complexity is deterministic
    assert complication.maximal_complexity == complication.minimal_complexity


def test_multiply_equation_complication_apply():
    """Test applying MultiplyEquationComplication to an equation."""
    expr = Integer(5)
    complication = MultiplyEquationComplication(expr)

    # Apply to equation x = 10
    original = Equals(Unknown(), Integer(10))
    result = complication.apply(original)

    # Should create: x * 5 = 10 * 5
    assert isinstance(result, Equals)


def test_multiply_equation_complication_apply_non_equation():
    """Test applying MultiplyEquationComplication to non-equation raises error."""
    expr = Integer(5)
    complication = MultiplyEquationComplication(expr)

    # Apply to non-equation
    original = Unknown()

    with pytest.raises(ValueError, match="can only be applied to Equals expressions"):
        complication.apply(original)


def test_multiply_equation_complication_randomize_from_stream():
    """Test static factory method for random generation."""
    random_stream = random.Random(42)
    base_expr = Equals(Unknown(), Integer(10))
    complexity_budget = 5.0

    complication = MultiplyEquationComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    assert isinstance(complication, MultiplyEquationComplication)
    assert complication.minimal_complexity <= complexity_budget


@pytest.mark.parametrize("complexity_budget", [2.0, 3.0, 5.0, 10.0])
def test_multiply_equation_complication_respects_complexity_budget(complexity_budget):
    """Test that generated complications respect complexity budget."""
    random_stream = random.Random(42)
    base_expr = Equals(Unknown(), Integer(10))

    complication = MultiplyEquationComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    if complication is not None:
        assert complication.minimal_complexity <= complexity_budget


import pytest
from algebra_sofii.complications import AddToEquationComplication


def test_add_to_equation_complication_init():
    """Test AddToEquationComplication initialization."""
    expr = Integer(5)
    complication = AddToEquationComplication(expr)

    assert complication.expr == expr


def test_add_to_equation_complication_minimal_complexity():
    """Test that minimal_complexity returns expected value."""
    expr = Integer(5)
    complication = AddToEquationComplication(expr)

    # Adding to both sides duplicates the expression complexity
    # No additional structural complexity since it's just adding to existing sides
    expected_min = 2 * expr.complexity()
    assert complication.minimal_complexity == expected_min


def test_add_to_equation_complication_maximal_complexity():
    """Test that maximal_complexity returns expected value."""
    expr = Integer(5)
    complication = AddToEquationComplication(expr)

    # For AddToEquation, max is same as min since complexity is deterministic
    assert complication.maximal_complexity == complication.minimal_complexity


def test_add_to_equation_complication_apply():
    """Test applying AddToEquationComplication to an equation."""
    expr = Integer(5)
    complication = AddToEquationComplication(expr)

    # Apply to equation x = 10
    original = Equals(Unknown(), Integer(10))
    result = complication.apply(original)

    # Should create: x + 5 = 10 + 5
    assert isinstance(result, Equals)


def test_add_to_equation_complication_apply_non_equation():
    """Test applying AddToEquationComplication to non-equation raises error."""
    expr = Integer(5)
    complication = AddToEquationComplication(expr)

    # Apply to non-equation
    original = Unknown()

    with pytest.raises(ValueError, match="can only be applied to Equals expressions"):
        complication.apply(original)


def test_add_to_equation_complication_randomize_from_stream():
    """Test static factory method for random generation."""
    random_stream = random.Random(42)
    base_expr = Equals(Unknown(), Integer(10))
    complexity_budget = 5.0

    complication = AddToEquationComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    assert isinstance(complication, AddToEquationComplication)
    assert complication.minimal_complexity <= complexity_budget


@pytest.mark.parametrize("complexity_budget", [2.0, 3.0, 5.0, 10.0])
def test_add_to_equation_complication_respects_complexity_budget(complexity_budget):
    """Test that generated complications respect complexity budget."""
    random_stream = random.Random(42)
    base_expr = Equals(Unknown(), Integer(10))

    complication = AddToEquationComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    if complication is not None:
        assert complication.minimal_complexity <= complexity_budget
