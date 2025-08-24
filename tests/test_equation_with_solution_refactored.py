"""Tests for EquationWithSolution refactored methods."""

import random
import pytest
from algebra_sofii.complications import EquationWithSolution


def test_equation_with_solution_add_random_complication():
    """Test the new add_random_complication method."""
    eq_with_sol = EquationWithSolution(5)
    random_stream = random.Random(42)

    initial_complexity = eq_with_sol.get_total_complexity()
    max_complexity = (
        initial_complexity + 5.0
    )  # Increase budget to account for minimum complication complexity

    # Add a random complication
    eq_with_sol.add_random_complication(max_complexity, random_stream)

    # Should have added exactly one complication
    assert len(eq_with_sol.complications) == 1
    assert eq_with_sol.get_total_complexity() <= max_complexity


def test_equation_with_solution_add_random_complication_insufficient_budget():
    """Test add_random_complication with insufficient complexity budget."""
    eq_with_sol = EquationWithSolution(5)
    random_stream = random.Random(42)

    current_complexity = eq_with_sol.get_total_complexity()
    # Set budget too low for any complication
    max_complexity = current_complexity + 0.5

    with pytest.raises(ValueError, match="Insufficient complexity budget"):
        eq_with_sol.add_random_complication(max_complexity, random_stream)


def test_equation_with_solution_randomize():
    """Test the new randomize method."""
    eq_with_sol = EquationWithSolution(5)
    random_stream = random.Random(42)

    initial_complexity = eq_with_sol.get_total_complexity()
    target_complexity = initial_complexity + 10.0

    # Randomize up to target complexity
    eq_with_sol.randomize(random_stream, target_complexity)

    # Should have added multiple complications
    assert len(eq_with_sol.complications) > 0
    assert eq_with_sol.get_total_complexity() <= target_complexity

    # Should be close to target (within one complication's worth)
    final_complexity = eq_with_sol.get_total_complexity()
    assert final_complexity >= initial_complexity


def test_equation_with_solution_randomize_low_target():
    """Test randomize method with low target complexity."""
    eq_with_sol = EquationWithSolution(5)
    random_stream = random.Random(42)

    # Set target below current complexity
    target_complexity = eq_with_sol.get_total_complexity() - 1.0

    # Should not add any complications
    eq_with_sol.randomize(random_stream, target_complexity)
    assert len(eq_with_sol.complications) == 0


@pytest.mark.parametrize("seed", [42, 123, 456])
def test_equation_with_solution_randomize_deterministic(seed):
    """Test that randomize is deterministic with same seed."""
    # Create two identical equation instances
    eq1 = EquationWithSolution(5)
    eq2 = EquationWithSolution(5)

    # Use same random streams
    stream1 = random.Random(seed)
    stream2 = random.Random(seed)

    target_complexity = eq1.get_total_complexity() + 8.0

    # Randomize both
    eq1.randomize(stream1, target_complexity)
    eq2.randomize(stream2, target_complexity)

    # Should produce identical results
    assert len(eq1.complications) == len(eq2.complications)
    assert eq1.get_total_complexity() == eq2.get_total_complexity()


def test_equation_with_solution_complication_weights():
    """Test that complication weights are properly defined."""
    from algebra_sofii.complications import (
        EXPRESSION_COMPLICATION_WEIGHTS,
        EQUATION_COMPLICATION_WEIGHTS,
    )

    # Expression weights should include all expression complications
    expected_expr_complications = {
        "AddZeroComplication",
        "MultiplyByOneComplication",
        "InsertBracketsComplication",
        "NegateComplication",
        "InvertComplication",
    }

    assert set(EXPRESSION_COMPLICATION_WEIGHTS.keys()) == expected_expr_complications
    assert all(weight > 0 for weight in EXPRESSION_COMPLICATION_WEIGHTS.values())

    # Equation weights should include all equation complications plus expression ones
    expected_eq_complications = expected_expr_complications | {
        "AddToEquationComplication",
        "MultiplyEquationComplication",
    }

    assert set(EQUATION_COMPLICATION_WEIGHTS.keys()) == expected_eq_complications
    assert all(weight > 0 for weight in EQUATION_COMPLICATION_WEIGHTS.values())
