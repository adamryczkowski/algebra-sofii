#!/usr/bin/env python3

from algebra_sofii.expressions import Integer, Unknown, Addition, ExpressionIndex
from algebra_sofii.complications.equation_with_solution import EquationWithSolution
from algebra_sofii.complications.add_to_equation import AddToEquationComplication
from algebra_sofii.complications.insert_brackets import InsertBracketsComplication
from algebra_sofii.complications.multiply_equation import MultiplyEquationComplication
from algebra_sofii.expressions import Inverted

def debug_step_8():
    """Debug what exactly happens at step 8."""

    # Reproduce all steps up to step 7
    eq = EquationWithSolution.MakeEquation(solution=5)
    print(f"Step 0: {eq}")

    # Step 1: Add (x + 3) to both sides on the right
    eq.apply_complication(
        AddToEquationComplication(Addition([Unknown(), Integer(3)]), left_side=False)
    )
    print(f"Step 1: {eq}")

    # Step 2: Add -1 to both sides on the left
    eq.apply_complication(AddToEquationComplication(Integer(-1), left_side=True))
    print(f"Step 2: {eq}")

    # Step 3: Add parentheses around first and last term on left side
    eq.apply_complication(InsertBracketsComplication(ExpressionIndex([0]), 0, 2, False))
    print(f"Step 3: {eq}")

    # Step 4: Add parentheses around first and second term on right side, but with negation
    eq.apply_complication(InsertBracketsComplication(ExpressionIndex([1]), 0, 1, True))
    print(f"Step 4: {eq}")

    # Step 5: Multiply both sides by 2
    eq.apply_complication(MultiplyEquationComplication(Integer(2), left_side=True))
    print(f"Step 5: {eq}")

    # Step 6: Divide both sides by 2
    eq.apply_complication(
        MultiplyEquationComplication(Inverted(Integer(2)), left_side=False)
    )
    print(f"Step 6: {eq}")

    # Step 7: Add "x - 1" to both sides on the left
    eq.apply_complication(
        AddToEquationComplication(Addition([Unknown(), Integer(-1)]), left_side=True)
    )
    print(f"Step 7: {eq}")

    # Debug the left side structure before step 8
    print("\n=== Debugging Step 8 ===")
    left_side = eq.cached_current_form[ExpressionIndex([0])]
    print(f"Left side type: {type(left_side)}")
    print(f"Left side: {left_side}")

    if hasattr(left_side, 'operands'):
        print(f"Left side operands count: {len(left_side.operands)}")
        for i, op in enumerate(left_side.operands):
            print(f"  Operand {i}: '{op}' (type: {type(op).__name__})")
            # If it's an Addition, show its operands too
            if hasattr(op, 'operands'):
                print(f"    Sub-operands: {len(op.operands)}")
                for j, sub_op in enumerate(op.operands):
                    print(f"      Sub-operand {j}: '{sub_op}' (type: {type(sub_op).__name__})")

if __name__ == "__main__":
    debug_step_8()
