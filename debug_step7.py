#!/usr/bin/env python3

from algebra_sofii.expressions import Integer, Unknown, Addition, ExpressionIndex
from algebra_sofii.complications.equation_with_solution import EquationWithSolution
from algebra_sofii.complications.add_to_equation import AddToEquationComplication
from algebra_sofii.complications.insert_brackets import InsertBracketsComplication
from algebra_sofii.complications.multiply_equation import MultiplyEquationComplication
from algebra_sofii.expressions import Inverted

def trace_step_7():
    """Debug the exact structure at step 7 to understand the operand count issue."""
    
    # Start with a simple test of Addition flattening
    print("=== Testing Addition Flattening ===")
    base_expr = Addition([Unknown(), Integer(5)])  # x + 5
    add_expr = Addition([Unknown(), Integer(-1)])  # x - 1
    
    # Test left-side addition (flattening)
    result = base_expr.add_expression(add_expr, left_side=True)
    print(f"Base: {base_expr}")
    print(f"Add: {add_expr}")
    print(f"Result: {result}")
    print(f"Result operands count: {len(result.operands)}")
    for i, op in enumerate(result.operands):
        print(f"  Operand {i}: {op} (type: {type(op).__name__})")
    
    print("\n=== Reproducing the actual test scenario ===")
    
    # Now let's reproduce the exact scenario from the test
    # After step 6, we should have: 2*(x + (-1 + (x + 3)))/2 = 2*(-(1 - 5) + (x + 3))/2
    
    # Let's manually build what the left side should look like after step 6
    from algebra_sofii.expressions import Multiplication, ChangedSign
    
    # Build: x + (-1 + (x + 3))
    inner_addition = Addition([Integer(-1), Addition([Unknown(), Integer(3)])])  # -1 + (x + 3)
    left_complex_part = Addition([Unknown(), inner_addition])  # x + (-1 + (x + 3))
    
    # Build: 2*(x + (-1 + (x + 3)))/2
    mult_part = Multiplication([Integer(2), left_complex_part, Inverted(Integer(2))])  # 2*(x + (-1 + (x + 3)))/2
    
    print(f"Complex part before step 7: {mult_part}")
    
    # Now add "x - 1" to the left side (this is step 7)
    addition_to_add = Addition([Unknown(), Integer(-1)])  # x - 1
    
    # This should use the base Expression.add_expression method since mult_part is a Multiplication, not Addition
    step_7_result = mult_part.add_expression(addition_to_add, left_side=True)
    
    print(f"After step 7: {step_7_result}")
    print(f"Step 7 result type: {type(step_7_result)}")
    print(f"Step 7 operands count: {len(step_7_result.operands)}")
    for i, op in enumerate(step_7_result.operands):
        print(f"  Operand {i}: {op} (type: {type(op).__name__})")

if __name__ == "__main__":
    trace_step_7()
