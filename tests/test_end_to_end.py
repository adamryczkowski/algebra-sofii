from algebra_sofii import EquationWithSolution, RandomClass, ExpressionIndex
from algebra_sofii.complications import (
    NegateComplication,
    MultiplyEquationComplication,
    InsertBracketsComplication,
    AddToEquationComplication,
)
from algebra_sofii.expressions import Addition, Integer, Unknown, Inverted
import random


def test_manual_complications():
    eq = EquationWithSolution.MakeEquation(solution=5)  # An equation where x=5
    print(f"Original equation: {eq}")
    assert repr(eq) == "x = 5"

    # 1. Add (x + 3) to both sides on the right
    eq.apply_complication(
        AddToEquationComplication(Addition([Unknown(), Integer(3)]), left_side=False)
    )
    assert repr(eq) == "x + (x + 3) = 5 + (x + 3)"

    # 2. Add -1 to both sides on the left
    eq.apply_complication(AddToEquationComplication(Integer(-1), left_side=True))
    assert repr(eq) == "-1 + x + (x + 3) = -1 + 5 + (x + 3)"

    # 3. Add parentheses around first and last term on left side
    eq.apply_complication(InsertBracketsComplication(ExpressionIndex([0]), 0, 2, False))
    assert repr(eq) == "x + (-1 + (x + 3)) = -1 + 5 + (x + 3)"

    # 4. Add parentheses around first and second term on right side, but with negation
    eq.apply_complication(InsertBracketsComplication(ExpressionIndex([1]), 0, 1, True))
    assert repr(eq) == "x + (-1 + (x + 3)) = -(1 - 5) + (x + 3)"

    # 5. Multiply both sides by 2
    eq.apply_complication(MultiplyEquationComplication(Integer(2), left_side=True))
    assert repr(eq) == "2 * (x + (-1 + (x + 3))) = 2 * (-(1 - 5) + (x + 3))"

    # 6. Divide both sides by 4
    eq.apply_complication(
        MultiplyEquationComplication(Inverted(Integer(2)), left_side=False)
    )
    assert repr(eq) == "2 * (x + (-1 + (x + 3)))/2 = 2 * (-(1 - 5) + (x + 3))/2"

    # 7. Add "x - 1" to both sides on the left
    eq.apply_complication(
        AddToEquationComplication(Addition([Unknown(), Integer(-1)]), left_side=True)
    )
    assert (
        repr(eq)
        == "x - 1 + 2 * (x + (-1 + (x + 3)))/2 = x - 1 + 2 * (-(1 - 5) + (x + 3))/2"
    )

    # 8. Add parantheses around first and the second term on the left side
    eq.apply_complication(InsertBracketsComplication(ExpressionIndex([0]), 0, 1, False))
    assert (
        repr(eq)
        == "(x - 1) + 2 * (x + (-1 + (x + 3)))/2 = x - 1 + 2 * (-(1 - 5) + (x + 3))/2"
    )

    # 9. Negate the first term on the left side
    eq.apply_complication(NegateComplication(ExpressionIndex([0, 0])))
    assert (
        repr(eq)
        == "-(-x + 1) + 2 * (x + (-1 + (x + 3)))/2 = x - 1 + 2 * (-(1 - 5) + (x + 3))/2"
    )


def test_one():
    eq = EquationWithSolution.MakeEquation(solution=3)  # An equation where x=3
    print(f"Non-randomized equation: {eq}")
    assert repr(eq) == "x = 3"
    random.seed(42)
    random_state = RandomClass()
    eq.randomize(random_stream=random_state, max_complexity=20)
    print(f"Randomized equation: {eq}")
    assert repr(eq) == "(1/7 - 6 + (x - (1/7 - 6))) * 2 = 3 * 2"


if __name__ == "__main__":
    test_one()
