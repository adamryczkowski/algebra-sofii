#!/usr/bin/env python3

from algebra_sofii.expressions import Integer, Unknown, Addition, ExpressionIndex
from algebra_sofii.complications.equation_with_solution import EquationWithSolution
from algebra_sofii.complications.add_to_equation import AddToEquationComplication
from algebra_sofii.complications.insert_brackets import InsertBracketsComplication
from algebra_sofii.complications.multiply_equation import MultiplyEquationComplication
from algebra_sofii.expressions import Inverted

def debug_equation_steps():
    # Reproduce the test steps up to the failing point
    eq = EquationWithSolution.MakeEquation(solution=5)
    print(f"Step 0: {eq}")
    
    # 1. Add (x + 3) to both sides on the right
    eq.apply_complication(
        AddToEquationComplication(Addition([Unknown(), Integer(3)]), left_side=False)
    )
    print(f"Step 1: {eq}")
    
    # 2. Add -1 to both sides on the left
    eq.apply_complication(AddToEquationComplication(Integer(-1), left_side=True))
    print(f"Step 2: {eq}")
    
    # 3. Add parentheses around first and last term on left side
    eq.apply_complication(InsertBracketsComplication(ExpressionIndex([0]), 0, 2, False))
    print(f"Step 3: {eq}")
    
    # 4. Add parentheses around first and second term on right side, but with negation
    eq.apply_complication(InsertBracketsComplication(ExpressionIndex([1]), 0, 1, True))
    print(f"Step 4: {eq}")
    
    # 5. Multiply both sides by 2
    eq.apply_complication(MultiplyEquationComplication(Integer(2), left_side=True))
    print(f"Step 5: {eq}")
    
    # 6. Divide both sides by 2
    eq.apply_complication(
        MultiplyEquationComplication(Inverted(Integer(2)), left_side=False)
    )
    print(f"Step 6: {eq}")
    
    # 7. Add "x - 1" to both sides on the left
    eq.apply_complication(
        AddToEquationComplication(Addition([Unknown(), Integer(-1)]), left_side=True)
    )
    print(f"Step 7: {eq}")
    
    # Debug: Check the structure of the left side before step 8
    left_side = eq.equation[ExpressionIndex([0])]
    print(f"Left side type: {type(left_side)}")
    if hasattr(left_side, 'operands'):
        print(f"Left side operands count: {len(left_side.operands)}")
        for i, op in enumerate(left_side.operands):
            print(f"  Operand {i}: {op} (type: {type(op)})")
    
    # Now try step 8
    try:
        eq.apply_complication(InsertBracketsComplication(ExpressionIndex([0]), 0, 1, False))
        print(f"Step 8: {eq}")
    except Exception as e:
        print(f"Step 8 failed: {e}")

if __name__ == "__main__":
    debug_equation_steps()
