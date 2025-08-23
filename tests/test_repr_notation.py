"""
Unit tests for the __repr__ methods of expression classes.
Tests mathematical notation output against expected strings.
"""

import pytest
from algebra_sofii.expressions import (
    Addition,
    ChangedSign,
    Equals,
    Integer,
    Inverted,
    Multiplication,
    Unknown,
)

# Common test variables
x = Unknown()
zero = Integer(0)
one = Integer(1)
two = Integer(2)
three = Integer(3)
five = Integer(5)
neg_two = Integer(-2)


@pytest.mark.parametrize(
    "expr,expected",
    [
        (x, "x"),
        (zero, "0"),
        (one, "1"),
        (five, "5"),
        (neg_two, "-2"),
    ],
)
def test_basic_expressions(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (Addition([x, five]), "x + 5"),
        (Addition([two, three]), "2 + 3"),
        (Addition([x, two, three]), "x + 2 + 3"),
        (Multiplication([x, five]), "x * 5"),
        (Multiplication([two, three]), "2 * 3"),
        (Multiplication([x, two, three]), "x * 2 * 3"),
        (ChangedSign(x), "-x"),
        (ChangedSign(five), "-5"),
        (Inverted(x), "1/x"),
        (Inverted(five), "1/5"),
        (Equals(x, five), "x = 5"),
    ],
)
def test_simple_operations(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (Addition([five, ChangedSign(x)]), "5 - x"),
        (Addition([x, ChangedSign(two)]), "x - 2"),
        (Addition([five, ChangedSign(two)]), "5 - 2"),
        (Addition([x, five, ChangedSign(two)]), "x + 5 - 2"),
        (Addition([x, ChangedSign(two), three]), "x - 2 + 3"),
    ],
)
def test_subtraction_handling(expr, expected):
    assert str(expr) == expected


add_expr = Addition([x, two])


@pytest.mark.parametrize(
    "expr,expected",
    [
        (Multiplication([add_expr, three]), "(x + 2) * 3"),
        (Multiplication([three, add_expr]), "3 * (x + 2)"),
        (Multiplication([add_expr, add_expr]), "(x + 2) * (x + 2)"),
        (Multiplication([add_expr, Addition([x, five])]), "(x + 2) * (x + 5)"),
        (Multiplication([x, three]), "x * 3"),
        (Multiplication([ChangedSign(x), three]), "-x * 3"),
        (Multiplication([Inverted(x), three]), "1/x * 3"),
    ],
)
def test_parentheses_in_multiplication(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (ChangedSign(Addition([x, two])), "-(x + 2)"),
        (ChangedSign(Multiplication([x, two])), "-(x * 2)"),
        (ChangedSign(x), "-x"),
        (ChangedSign(Inverted(x)), "-1/x"),
    ],
)
def test_parentheses_in_negation(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (Inverted(Addition([x, two])), "1/(x + 2)"),
        (Inverted(Multiplication([x, two])), "1/(x * 2)"),
        (Inverted(ChangedSign(x)), "1/(-x)"),
        (Inverted(x), "1/x"),
        (Inverted(five), "1/5"),
    ],
)
def test_parentheses_in_inversion(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (Addition([Multiplication([two, x]), three]), "2 * x + 3"),
        (Addition([x, ChangedSign(Multiplication([two, three]))]), "x - 2 * 3"),
        (Multiplication([Addition([x, one]), ChangedSign(two)]), "(x + 1) * -2"),
        (Inverted(Addition([Multiplication([two, x]), one])), "1/(2 * x + 1)"),
        (ChangedSign(Inverted(Addition([x, one]))), "-1/(x + 1)"),
        (
            Multiplication([Addition([x, one]), Inverted(Addition([x, two]))]),
            "(x + 1) * 1/(x + 2)",
        ),
    ],
)
def test_complex_nested_expressions(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (
            Addition([Multiplication([Addition([x, one]), two]), three]),
            "(x + 1) * 2 + 3",
        ),
        (
            ChangedSign(Multiplication([Addition([x, one]), Addition([x, two])])),
            "-((x + 1) * (x + 2))",
        ),
        (Inverted(Multiplication([Addition([x, one]), two])), "1/((x + 1) * 2)"),
        (
            Addition(
                [
                    Multiplication([three, x]),
                    ChangedSign(two),
                    Inverted(Addition([x, one])),
                ]
            ),
            "3 * x - 2 + 1/(x + 1)",
        ),
        (Multiplication([two, ChangedSign(Addition([x, three]))]), "2 * -(x + 3)"),
    ],
)
def test_deeply_nested_expressions(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (Equals(x, five), "x = 5"),
        (Equals(five, x), "5 = x"),
        (Equals(Addition([x, two]), five), "x + 2 = 5"),
        (Equals(Multiplication([two, x]), Integer(10)), "2 * x = 10"),
        (Equals(Addition([x, two]), Addition([three, x])), "x + 2 = 3 + x"),
        (
            Equals(
                Addition([Multiplication([two, x]), three]), Addition([Integer(7), x])
            ),
            "2 * x + 3 = 7 + x",
        ),
        (Equals(Inverted(x), Inverted(five)), "1/x = 1/5"),
    ],
)
def test_equation_representations(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (ChangedSign(ChangedSign(x)), "--x"),
        (Inverted(Inverted(x)), "1/(1/x)"),
        (Addition([x, zero]), "x + 0"),
        (Multiplication([x, one]), "x * 1"),
        (Addition([x, ChangedSign(two), ChangedSign(three), five]), "x - 2 - 3 + 5"),
        (
            Multiplication([Addition([x, Addition([two, three])]), five]),
            "(x + (2 + 3)) * 5",
        ),
    ],
)
def test_edge_cases_and_special_scenarios(expr, expected):
    assert str(expr) == expected
