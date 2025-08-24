#!/usr/bin/env python3

from algebra_sofii.expressions import Integer, Unknown, Addition, Multiplication, Inverted

# Test multiplication formatting (should not have spaces)
mult = Multiplication([Integer(2), Addition([Unknown(), Integer(3)])])
print(f"Multiplication: {mult}")
print(f"Expected: 2*(x + 3)")

# Test division formatting (should use / not *1/)
div = Multiplication([Integer(2), Addition([Unknown(), Integer(3)]), Inverted(Integer(2))])
print(f"Division: {div}")
print(f"Expected: 2*(x + 3)/2")

# Test pure inversion
inv = Inverted(Integer(2))
print(f"Pure inversion: {inv}")
print(f"Expected: 1/2")
