"""
Test script to verify that the exclude_unknown flag works correctly
to ensure linear equations are maintained.
"""

import random
from algebra_sofii.generators import random_expression
from algebra_sofii.expressions import Unknown
from algebra_sofii.complications import (
    EquationWithSolution,
    OperationType,
    ExpressionComplication,
)


def contains_unknown(expr) -> bool:
    """Check if an expression contains the unknown variable x."""
    if isinstance(expr, Unknown):
        return True
    if hasattr(expr, "operands"):
        return any(contains_unknown(op) for op in expr.operands)
    if hasattr(expr, "operand"):
        return contains_unknown(expr.operand)
    return False


def test_exclude_unknown_flag():
    """Test that exclude_unknown=True generates expressions without x."""
    random_stream = random.Random(42)

    print("Testing exclude_unknown=True...")
    for complexity in [1.0, 2.0, 3.0, 4.0, 5.0]:
        for _ in range(10):
            expr = random_expression(random_stream, complexity, exclude_unknown=True)
            if contains_unknown(expr):
                print(
                    f"ERROR: Expression {expr} with complexity {complexity} contains unknown!"
                )
                return False
            print(f"✓ Complexity {complexity}: {expr} (no unknown)")

    print("\nTesting exclude_unknown=False (default)...")
    unknown_found = False
    for complexity in [3.0, 4.0, 5.0]:
        for _ in range(20):
            expr = random_expression(random_stream, complexity, exclude_unknown=False)
            if contains_unknown(expr):
                unknown_found = True
                print(f"✓ Complexity {complexity}: {expr} (contains unknown)")
                break

    if not unknown_found:
        print("WARNING: No expressions with unknown found in default mode")

    return True


def test_multiply_by_one_linearity():
    """Test that MULTIPLY_BY_ONE complications maintain linearity."""
    print("\nTesting MULTIPLY_BY_ONE complications for linearity...")

    random_stream = random.Random(123)

    for solution in [1, 3, 5]:
        eq_with_sol = EquationWithSolution(solution)

        # Generate several complications and check linearity
        for _ in range(10):
            try:
                complication = eq_with_sol.random_complication(10.0, random_stream)
                eq_with_sol.apply_complication(complication)

                # Check if solution is still valid
                if not eq_with_sol.verify_solution():
                    print(
                        f"ERROR: Solution {solution} no longer valid after complication"
                    )
                    return False

                # For MULTIPLY_BY_ONE complications, check that the expression doesn't contain unknown
                if (
                    isinstance(complication, ExpressionComplication)
                    and complication.operation == OperationType.MULTIPLY_BY_ONE
                ):
                    if contains_unknown(complication.expr):
                        print(
                            f"ERROR: MULTIPLY_BY_ONE used expression with unknown: {complication.expr}"
                        )
                        return False
                    else:
                        print(
                            f"✓ MULTIPLY_BY_ONE with safe expression: {complication.expr}"
                        )

            except Exception as e:
                print(f"ERROR during complication: {e}")
                return False

    return True


if __name__ == "__main__":
    print("Testing exclude_unknown functionality...\n")

    success = True
    success &= test_exclude_unknown_flag()
    success &= test_multiply_by_one_linearity()

    if success:
        print("\n✅ All tests passed! The exclude_unknown flag works correctly.")
    else:
        print("\n❌ Some tests failed!")

    exit(0 if success else 1)
