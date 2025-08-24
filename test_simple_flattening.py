#!/usr/bin/env python3

from algebra_sofii.expressions import Integer, Unknown, Addition

# Test the specific case that's failing
print("Testing Addition flattening:")

# Create "x - 1" 
x_minus_1 = Addition([Unknown(), Integer(-1)])
print(f"x - 1: {x_minus_1}")
print(f"x - 1 operands: {len(x_minus_1.operands)}")
for i, op in enumerate(x_minus_1.operands):
    print(f"  Operand {i}: {op} (type: {type(op).__name__})")

# Create some other expression
other_expr = Unknown()  # Just x
print(f"Other expr: {other_expr}")

# Test adding them
result = other_expr.add_expression(x_minus_1, left_side=True)
print(f"Result: {result}")
print(f"Result operands: {len(result.operands)}")
for i, op in enumerate(result.operands):
    print(f"  Operand {i}: {op} (type: {type(op).__name__})")

print("\nExpected: Unknown, Integer(-1), Unknown")
print("This should give us 3 operands total.")
