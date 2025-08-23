from algebra_sofii.expressions import Equals, Integer, Unknown
from algebra_sofii.complications import EquationComplication, OperationType
import sympy as sp

# Create the test case: x = 5, multiply by 3
expr = Equals(Unknown(), Integer(5))
added_expr = Integer(3)
complication = EquationComplication(OperationType.MULTIPLY, added_expr)

print("Original equation:", expr)
print("Original sympy:", expr.to_sympy_expr())

complicated = complication.apply(expr)
print("Complicated equation:", complicated)
print("Complicated sympy:", complicated.to_sympy_expr())

# Test with x=1
x = sp.Symbol("x")
orig_result = expr.to_sympy_expr().subs(x, 1)
comp_result = complicated.to_sympy_expr().subs(x, 1)
print(f"At x=1: original={orig_result}, complicated={comp_result}")

# Let's also see the structure
if isinstance(complicated, Equals):
    print("Complicated left:", complicated.left)
    print("Complicated right:", complicated.right)
