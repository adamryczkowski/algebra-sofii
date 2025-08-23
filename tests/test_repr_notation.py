"""
Unit tests for the __repr__ methods of expression classes.
Tests mathematical notation output against expected strings.
"""

import unittest
from algebra_sofii.expressions import (
    Addition,
    ChangedSign,
    Equals,
    Integer,
    Inverted,
    Multiplication,
    Unknown,
)


class TestMathematicalRepr(unittest.TestCase):
    """Test that __repr__ methods display proper mathematical notation."""

    def setUp(self):
        """Set up common expressions for testing."""
        self.x = Unknown()
        self.zero = Integer(0)
        self.one = Integer(1)
        self.two = Integer(2)
        self.three = Integer(3)
        self.five = Integer(5)
        self.neg_two = Integer(-2)

    def test_basic_expressions(self):
        """Test basic expression representations."""
        # Test cases: (expression, expected_string)
        test_cases = [
            (self.x, "x"),
            (self.zero, "0"),
            (self.one, "1"),
            (self.five, "5"),
            (self.neg_two, "-2"),
        ]

        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                self.assertEqual(str(expr), expected)

    def test_simple_operations(self):
        """Test simple operations without nested complexity."""
        test_cases = [
            # Addition
            (Addition([self.x, self.five]), "x + 5"),
            (Addition([self.two, self.three]), "2 + 3"),
            (Addition([self.x, self.two, self.three]), "x + 2 + 3"),
            # Multiplication
            (Multiplication([self.x, self.five]), "x * 5"),
            (Multiplication([self.two, self.three]), "2 * 3"),
            (Multiplication([self.x, self.two, self.three]), "x * 2 * 3"),
            # Negation
            (ChangedSign(self.x), "-x"),
            (ChangedSign(self.five), "-5"),
            # Inversion
            (Inverted(self.x), "1/x"),
            (Inverted(self.five), "1/5"),
            # Equation
            (Equals(self.x, self.five), "x = 5"),
        ]

        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                self.assertEqual(str(expr), expected)

    def test_subtraction_handling(self):
        """Test that addition with negated operands displays as subtraction."""
        test_cases = [
            # Simple subtraction
            (Addition([self.five, ChangedSign(self.x)]), "5 - x"),
            (Addition([self.x, ChangedSign(self.two)]), "x - 2"),
            (Addition([self.five, ChangedSign(self.two)]), "5 - 2"),
            # Multiple terms with subtraction
            (Addition([self.x, self.five, ChangedSign(self.two)]), "x + 5 - 2"),
            (Addition([self.x, ChangedSign(self.two), self.three]), "x - 2 + 3"),
        ]

        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                self.assertEqual(str(expr), expected)

    def test_parentheses_in_multiplication(self):
        """Test that parentheses are correctly added in multiplication."""
        # Addition needs parentheses when multiplied
        add_expr = Addition([self.x, self.two])

        test_cases = [
            (Multiplication([add_expr, self.three]), "(x + 2) * 3"),
            (Multiplication([self.three, add_expr]), "3 * (x + 2)"),
            (Multiplication([add_expr, add_expr]), "(x + 2) * (x + 2)"),
            # Multiple additions in multiplication
            (
                Multiplication([add_expr, Addition([self.x, self.five])]),
                "(x + 2) * (x + 5)",
            ),
            # No parentheses needed for simple terms
            (Multiplication([self.x, self.three]), "x * 3"),
            (Multiplication([ChangedSign(self.x), self.three]), "-x * 3"),
            (Multiplication([Inverted(self.x), self.three]), "1/x * 3"),
        ]

        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                self.assertEqual(str(expr), expected)

    def test_parentheses_in_negation(self):
        """Test that parentheses are correctly added in negation."""
        test_cases = [
            # Complex expressions need parentheses when negated
            (ChangedSign(Addition([self.x, self.two])), "-(x + 2)"),
            (ChangedSign(Multiplication([self.x, self.two])), "-(x * 2)"),
            # Simple expressions don't need extra parentheses
            (ChangedSign(self.x), "-x"),
            (ChangedSign(Inverted(self.x)), "-1/x"),
        ]

        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                self.assertEqual(str(expr), expected)

    def test_parentheses_in_inversion(self):
        """Test that parentheses are correctly added in inversion."""
        test_cases = [
            # Complex expressions need parentheses in denominator
            (Inverted(Addition([self.x, self.two])), "1/(x + 2)"),
            (Inverted(Multiplication([self.x, self.two])), "1/(x * 2)"),
            (Inverted(ChangedSign(self.x)), "1/(-x)"),
            # Simple expressions don't need extra parentheses
            (Inverted(self.x), "1/x"),
            (Inverted(self.five), "1/5"),
        ]

        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                self.assertEqual(str(expr), expected)

    def test_complex_nested_expressions(self):
        """Test complex nested expressions with multiple levels."""
        test_cases = [
            # Nested addition and multiplication
            (Addition([Multiplication([self.two, self.x]), self.three]), "2 * x + 3"),
            # Addition with negated multiplication
            (
                Addition([self.x, ChangedSign(Multiplication([self.two, self.three]))]),
                "x - 2 * 3",
            ),
            # Multiplication of addition and negation
            (
                Multiplication([Addition([self.x, self.one]), ChangedSign(self.two)]),
                "(x + 1) * -2",
            ),
            # Complex fraction
            (
                Inverted(Addition([Multiplication([self.two, self.x]), self.one])),
                "1/(2 * x + 1)",
            ),
            # Negated fraction
            (ChangedSign(Inverted(Addition([self.x, self.one]))), "-1/(x + 1)"),
            # Fraction with complex numerator (hypothetical Division class behavior)
            # Using multiplication with inverted denominator
            (
                Multiplication(
                    [
                        Addition([self.x, self.one]),
                        Inverted(Addition([self.x, self.two])),
                    ]
                ),
                "(x + 1) * 1/(x + 2)",
            ),
        ]

        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                self.assertEqual(str(expr), expected)

    def test_deeply_nested_expressions(self):
        """Test deeply nested expressions with multiple operation types."""
        test_cases = [
            # Triple nesting: ((x + 1) * 2) + 3
            (
                Addition(
                    [
                        Multiplication([Addition([self.x, self.one]), self.two]),
                        self.three,
                    ]
                ),
                "(x + 1) * 2 + 3",
            ),
            # Negation of complex multiplication: -((x + 1) * (x + 2))
            (
                ChangedSign(
                    Multiplication(
                        [Addition([self.x, self.one]), Addition([self.x, self.two])]
                    )
                ),
                "-((x + 1) * (x + 2))",
            ),
            # Inversion of nested operations: 1/((x + 1) * 2)
            (
                Inverted(Multiplication([Addition([self.x, self.one]), self.two])),
                "1/((x + 1) * 2)",
            ),
            # Complex addition with multiple operation types
            (
                Addition(
                    [
                        Multiplication([self.three, self.x]),
                        ChangedSign(self.two),
                        Inverted(Addition([self.x, self.one])),
                    ]
                ),
                "3 * x - 2 + 1/(x + 1)",
            ),
            # Multiplication with negated addition
            (
                Multiplication([self.two, ChangedSign(Addition([self.x, self.three]))]),
                "2 * -(x + 3)",
            ),
        ]

        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                self.assertEqual(str(expr), expected)

    def test_equation_representations(self):
        """Test various equation formats."""
        test_cases = [
            # Simple equations
            (Equals(self.x, self.five), "x = 5"),
            (Equals(self.five, self.x), "5 = x"),
            # Equations with operations on left side
            (Equals(Addition([self.x, self.two]), self.five), "x + 2 = 5"),
            (Equals(Multiplication([self.two, self.x]), Integer(10)), "2 * x = 10"),
            # Equations with operations on both sides
            (
                Equals(Addition([self.x, self.two]), Addition([self.three, self.x])),
                "x + 2 = 3 + x",
            ),
            # Complex equations
            (
                Equals(
                    Addition([Multiplication([self.two, self.x]), self.three]),
                    Addition([Integer(7), self.x]),
                ),
                "2 * x + 3 = 7 + x",
            ),
            # Equation with fractions
            (Equals(Inverted(self.x), Inverted(self.five)), "1/x = 1/5"),
        ]

        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                self.assertEqual(str(expr), expected)

    def test_edge_cases_and_special_scenarios(self):
        """Test edge cases and special formatting scenarios."""
        test_cases = [
            # Multiple negations
            (ChangedSign(ChangedSign(self.x)), "--x"),  # Should show double negation
            # Multiple inversions
            (Inverted(Inverted(self.x)), "1/(1/x)"),
            # Addition with zero
            (Addition([self.x, self.zero]), "x + 0"),
            # Multiplication with one
            (Multiplication([self.x, self.one]), "x * 1"),
            # Complex subtraction chain
            (
                Addition(
                    [self.x, ChangedSign(self.two), ChangedSign(self.three), self.five]
                ),
                "x - 2 - 3 + 5",
            ),
            # Nested parentheses preservation
            (
                Multiplication(
                    [Addition([self.x, Addition([self.two, self.three])]), self.five]
                ),
                "(x + (2 + 3)) * 5",
            ),
        ]

        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                self.assertEqual(str(expr), expected)


if __name__ == "__main__":
    unittest.main()
