# Tests for MultiplyEquationComplication class.
import random
import pytest
from algebra_sofii.complications import MultiplyEquationComplication
from algebra_sofii.expressions import Integer, Unknown, Equals
from algebra_sofii.random_class import RandomClass


def test_multiply_equation_complication_init():
    """Test MultiplyEquationComplication initialization."""
    expr = Integer(5)
    complication = MultiplyEquationComplication(expr, left_side=True)

    assert complication.expr == expr


def test_multiply_equation_complication_minimal_complexity():
    """Test that minimal_complexity returns expected value."""
    expr = Integer(5)
    complication = MultiplyEquationComplication(expr, left_side=True)

    # Multiplying both sides duplicates the expression complexity
    assert complication.minimal_complexity == 2 * expr.complexity()


def test_multiply_equation_complication_maximal_complexity():
    """Test that maximal_complexity returns expected value."""
    expr = Integer(5)
    complication = MultiplyEquationComplication(expr, left_side=True)

    # Should be same as minimal_complexity
    assert complication.maximal_complexity == complication.minimal_complexity


def test_multiply_equation_complication_apply():
    """Test applying MultiplyEquationComplication to an equation."""
    expr = Integer(5)
    complication = MultiplyEquationComplication(expr, left_side=True)
    equation = Equals(Unknown(), Integer(10))

    result = complication.apply(equation)

    # Should multiply both sides by 5
    assert str(result) == "5*x = 5*10"


def test_multiply_equation_complication_apply_non_equation():
    """Test applying MultiplyEquationComplication to non-equation raises error."""
    expr = Integer(5)
    complication = MultiplyEquationComplication(expr, left_side=True)
    non_equation = Integer(42)

    with pytest.raises(ValueError):
        complication.apply(non_equation)


def test_multiply_equation_complication_randomize_from_stream():
    """Test static factory method for random generation."""
    random.seed(42)  # Set seed for reproducibility
    random_stream = RandomClass()  # Use current random state
    base_expr = Equals(Unknown(), Integer(10))
    complexity_budget = 5.0

    complication = MultiplyEquationComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    assert complication is not None
    assert isinstance(complication, MultiplyEquationComplication)
    assert complication.minimal_complexity <= complexity_budget


@pytest.mark.parametrize("complexity_budget", [2.0, 3.0, 5.0, 10.0])
def test_multiply_equation_complication_respects_complexity_budget(complexity_budget):
    """Test that generated complications respect complexity budget."""
    random.seed(42)  # Set seed for reproducibility
    random_stream = RandomClass()  # Use current random state
    base_expr = Equals(Unknown(), Integer(10))

    complication = MultiplyEquationComplication.randomize_from_stream(
        random_stream, base_expr, complexity_budget
    )

    if complication is not None:
        assert complication.minimal_complexity <= complexity_budget
