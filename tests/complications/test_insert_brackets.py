"""
Test script to demonstrate the InsertBrackets complication type.
"""

import random
from algebra_sofii.complications import EquationWithSolution, InsertBracketsComplication
from algebra_sofii.expressions import Addition, ExpressionIndex, Integer, Unknown


def test_insert_brackets():
    """Test the InsertBrackets complication."""
    print("Testing InsertBrackets complication...")

    # Create an equation with solution x = 5
    eq_with_sol = EquationWithSolution.MakeEquation(solution=5)
    print(f"Initial equation: {eq_with_sol}")

    # Apply some complications to create additions with 3+ operands
    from algebra_sofii.random_class import RandomClass

    random.seed(42)  # Set seed for reproducibility
    random_stream = RandomClass()  # Use current random state

    # Add some complications to make the equation more complex
    # Use a higher budget and fewer iterations to avoid negative budget issues
    for i in range(2):  # Reduce from 3 to 2 iterations
        try:
            eq_with_sol.add_random_complication(25.0, random_stream)  # Increase budget
            print(f"\nAfter complication {i + 1}: {eq_with_sol.get_current_equation()}")
            print(f"Complexity: {eq_with_sol.get_total_complexity()}")
        except ValueError as e:
            print(f"Could not add complication {i + 1}: {e}")
            break

    # Try to apply an InsertBrackets complication
    brackets_complication = InsertBracketsComplication.randomize_from_stream(
        random_stream, eq_with_sol.get_current_equation(), 5.0, exclude_unknown=True
    )
    if brackets_complication:
        print("\nFound suitable addition for bracketing!")
        print(f"Before brackets: {eq_with_sol.get_current_equation()}")
        eq_with_sol.apply_complication(brackets_complication)
        print(f"After brackets: {eq_with_sol.get_current_equation()}")
        print(f"Brackets complication: {brackets_complication}")
        print(f"Complexity increase: {brackets_complication.minimal_complexity}")
    else:
        print("\nNo suitable additions found for bracketing in this equation.")

    # Verify solution still works
    print(f"\nSolution verification: {eq_with_sol.verify_solution()}")
    print(f"Final complexity: {eq_with_sol.get_total_complexity()}")


def test_manual_insert_brackets():
    """Test InsertBrackets on a manually created addition."""
    print("\n" + "=" * 50)
    print("Testing manual InsertBrackets...")

    # Create a simple addition: x + 2 + 3 + 1
    addition = Addition([Unknown(), Integer(2), Integer(3), Integer(1)])
    print(f"Original addition: {addition}")
    print(f"Original complexity: {addition.complexity()}")

    # Create an InsertBrackets complication to bracket elements 1 and 2 (2 + 3)
    brackets_comp = InsertBracketsComplication(
        index=ExpressionIndex([]),  # Target the root addition
        first_elem=1,  # Element at index 1 (Integer(2))
        second_elem=2,  # Element at index 2 (Integer(3))
        negate=False,  # Don't negate
    )

    # Apply the complication
    result = brackets_comp.apply(addition)
    print(f"After bracketing (2 + 3): {result}")
    print(f"New complexity: {result.complexity()}")
    print(f"Complexity increase: {brackets_comp.minimal_complexity}")

    # Test with negation
    brackets_comp_neg = InsertBracketsComplication(
        index=ExpressionIndex([]),  # Target the root addition
        first_elem=0,  # Element at index 0 (Unknown())
        second_elem=2,  # Element at index 2 (Integer(1)) - note: indices shift after previous operation
        negate=True,  # Negate the bracketed expression
    )

    # Apply to original addition
    result_neg = brackets_comp_neg.apply(addition)
    print(f"After bracketing -(x + 1): {result_neg}")
    print(f"Complexity increase with negation: {brackets_comp_neg.minimal_complexity}")
