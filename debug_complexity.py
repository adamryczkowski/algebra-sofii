from algebra_sofii.expressions import Equals, Multiplication, Addition, Integer, Unknown
from algebra_sofii.complications import EquationComplication, OperationType

# Test case 1: Complex equation multiplication
print("=== Case 1: Complex equation multiplication ===")
expr = Equals(Multiplication([Integer(2), Unknown()]), Integer(10))  # 2*x = 10
added_expr = Multiplication([Integer(2), Unknown()])  # 2*x
complication = EquationComplication(OperationType.MULTIPLY, added_expr)

print("Original expr:", expr)
print("Original complexity:", expr.complexity())
print("Added expr:", added_expr)
print("Added expr complexity:", added_expr.complexity())
print("Expected increase:", complication.complexity(expr))

complicated = complication.apply(expr)
print("Complicated expr:", complicated)
print("Complicated complexity:", complicated.complexity())
print("Actual increase:", complicated.complexity() - expr.complexity())

print("\n=== Case 2: Addition sides test ===")
# Test case 2: Addition sides
left = Addition([Unknown(), Integer(2)])  # x + 2
right = Addition([Integer(7), Integer(3)])  # 7 + 3
expr2 = Equals(left, right)
added_expr2 = Integer(5)
complication2 = EquationComplication(OperationType.ADD, added_expr2)

print("Original expr:", expr2)
print("Original complexity:", expr2.complexity())
print("Added expr:", added_expr2)
print("Added expr complexity:", added_expr2.complexity())
print("Expected increase:", complication2.complexity(expr2))

complicated2 = complication2.apply(expr2)
print("Complicated expr:", complicated2)
print("Complicated complexity:", complicated2.complexity())
print("Actual increase:", complicated2.complexity() - expr2.complexity())

# Let's also examine the structure in detail
print("\n=== Detailed structure analysis ===")
if isinstance(complicated2, Equals):
    print("Complicated left side:", complicated2.left)
    print("Complicated right side:", complicated2.right)
    print("Left side complexity:", complicated2.left.complexity())
    print("Right side complexity:", complicated2.right.complexity())
