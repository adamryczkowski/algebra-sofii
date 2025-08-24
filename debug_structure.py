#!/usr/bin/env python3

from algebra_sofii.expressions import Integer, Unknown, Addition, ExpressionIndex
from algebra_sofii.complications.equation_with_solution import EquationWithSolution
from algebra_sofii.complications.add_to_equation import AddToEquationComplication

# Test step 7 specifically to see the structure
eq = EquationWithSolution.MakeEquation(solution=5)
print(f"Initial: {eq}")

# Skip to step 6 (before the problematic addition)
# ... (doing all the previous steps quickly)

# Simulate what the equation looks like before step 7
# Based on the test output, it should be:
# 2*(x + (-1 + (x + 3))) = 2*(-(1 - 5) + (x + 3))

# Let's manually create what should be the structure and check operand counts
left_complex = "2*(x + (-1 + (x + 3)))/2"  # This is one operand
addition_to_add = Addition([Unknown(), Integer(-1)])  # This becomes x - 1

# When we add "x - 1" to the left, we should get:
# (x - 1) + 2*(x + (-1 + (x + 3)))/2
# This should have 2 operands: [Addition([Unknown(), Integer(-1)]), complex_expr]
# But the test expects to bracket operands 0 and 1, so it needs at least 3 operands

print(f"Addition to add: {addition_to_add}")
print(f"Addition operands: {addition_to_add.operands}")
print(f"Addition operand count: {len(addition_to_add.operands)}")

# The issue is that when we add Addition([Unknown(), Integer(-1)]) to the left,
# it might be flattening into individual operands: [Unknown(), Integer(-1), complex_expr]
# That would give us 3 operands, which should work.

# Let's test this theory by creating a manual addition
from algebra_sofii.expressions import Multiplication, Inverted
complex_expr = Multiplication([Integer(2), Addition([Unknown(), Addition([Integer(-1), Addition([Unknown(), Integer(3)])])]), Inverted(Integer(2))])
print(f"Complex expr: {complex_expr}")

# Now add the two expressions
test_addition = Addition([Unknown(), Integer(-1), complex_expr])
print(f"Test addition: {test_addition}")
print(f"Test addition operands: {len(test_addition.operands)}")
for i, op in enumerate(test_addition.operands):
    print(f"  Operand {i}: {op} (type: {type(op).__name__})")
