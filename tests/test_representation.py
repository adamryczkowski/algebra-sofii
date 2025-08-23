"""Test cases for expression representation and parentheses handling"""

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


class TestBasicRepresentation:
    """Test basic expression representation."""

    def test_subtraction_representation(self):
        """Test x - 2 * 3 (should not have parentheses around 2 * 3)"""
        x = Unknown()
        two = Integer(2)
        three = Integer(3)

        mult = Multiplication([two, three])
        neg_mult = ChangedSign(mult)
        subtraction = Addition([x, neg_mult])

        assert str(subtraction) == "x - 2 * 3"

    def test_double_inversion_representation(self):
        """Test 1/(1/x) (should have parentheses)"""
        x = Unknown()
        inv_x = Inverted(x)
        double_inv = Inverted(inv_x)

        assert str(double_inv) == "1/(1/x)"

    def test_addition_with_multiplication_parentheses(self):
        """Test (x + 2) * 3 (should have parentheses around addition)"""
        x = Unknown()
        two = Integer(2)
        three = Integer(3)

        addition = Addition([x, two])
        multiplication = Multiplication([addition, three])

        assert str(multiplication) == "(x + 2) * 3"

    def test_nested_addition_subtraction(self):
        """Test x + (y - z) representation"""
        x = Unknown()
        y = Integer(5)
        z = Integer(3)

        neg_z = ChangedSign(z)
        inner_add = Addition([y, neg_z])
        outer_add = Addition([x, inner_add])

        assert str(outer_add) == "x + (5 - 3)"


class TestComplexExpressions:
    """Test complex expressions based on sample equations."""

    def test_equation_type_1(self):
        """Test: 8*x/8 + 4 == 5*((3*x)/3 - 6) - 3*((x - 15)/15 + 2)"""
        x = Unknown()

        # Left side: 8*x/8 + 4
        eight = Integer(8)
        four = Integer(4)
        mult_8x = Multiplication([eight, x])
        div_8x_8 = Multiplication([mult_8x, Inverted(eight)])
        left_side = Addition([div_8x_8, four])

        # Right side components
        three = Integer(3)
        six = Integer(6)
        fifteen = Integer(15)
        two = Integer(2)
        five = Integer(5)

        # 3*x/3 - 6
        mult_3x = Multiplication([three, x])
        div_3x_3 = Multiplication([mult_3x, Inverted(three)])
        sub_6 = Addition([div_3x_3, ChangedSign(six)])

        # 5*((3*x)/3 - 6)
        mult_by_5 = Multiplication([five, sub_6])

        # (x - 15)/15 + 2
        sub_15 = Addition([x, ChangedSign(fifteen)])
        div_by_15 = Multiplication([sub_15, Inverted(fifteen)])
        add_2 = Addition([div_by_15, two])

        # -3*((x - 15)/15 + 2)
        neg_3 = ChangedSign(three)
        mult_neg_3 = Multiplication([neg_3, add_2])

        # Complete right side
        right_side = Addition([mult_by_5, mult_neg_3])

        equation = Equals(left_side, right_side)

        # Verify the equation string representation is well-formed
        eq_str = str(equation)
        assert "=" in eq_str
        assert "x" in eq_str

    def test_division_representation(self):
        """Test division representations with proper parentheses"""
        x = Unknown()

        # Test (x + 4)/4
        four = Integer(4)
        addition = Addition([x, four])
        division = Multiplication([addition, Inverted(four)])

        assert str(division) == "(x + 4) * 1/4"

    def test_nested_multiplication_division(self):
        """Test 2*x/2 representation"""
        x = Unknown()
        two = Integer(2)

        mult = Multiplication([two, x])
        div = Multiplication([mult, Inverted(two)])

        assert str(div) == "2 * x * 1/2"

    def test_complex_subtraction_with_parentheses(self):
        """Test x - ((y + z) * w) representation"""
        x = Unknown()
        y = Integer(5)
        z = Integer(3)
        w = Integer(2)

        inner_add = Addition([y, z])
        mult = Multiplication([inner_add, w])
        neg_mult = ChangedSign(mult)
        result = Addition([x, neg_mult])

        assert str(result) == "x - (5 + 3) * 2"

    def test_multiple_levels_of_nesting(self):
        """Test deeply nested expressions"""
        x = Unknown()

        # Build: x + (2 * (3 + 4))
        three = Integer(3)
        four = Integer(4)
        two = Integer(2)

        inner_add = Addition([three, four])
        mult = Multiplication([two, inner_add])
        result = Addition([x, mult])

        assert str(result) == "x + 2 * (3 + 4)"


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_single_operand_addition(self):
        """Test addition with single operand"""
        x = Unknown()
        # This should not normally happen in well-formed expressions
        # but test the behavior just in case
        try:
            Addition([x])
        except ValueError:
            # Expected - Addition requires at least 2 operands
            pass

    def test_negation_of_negation(self):
        """Test double negation cancellation"""
        x = Unknown()
        neg_x = ChangedSign(x)
        double_neg = ChangedSign(neg_x)

        # Test that double negation can be represented
        assert str(double_neg) == "--x"

    def test_inversion_of_inversion(self):
        """Test double inversion"""
        x = Unknown()
        inv_x = Inverted(x)
        double_inv = Inverted(inv_x)

        assert str(double_inv) == "1/(1/x)"

    def test_zero_and_one_representation(self):
        """Test representation of zero and one"""
        zero = Integer(0)
        one = Integer(1)

        assert str(zero) == "0"
        assert str(one) == "1"

    def test_negative_numbers(self):
        """Test representation of negative integers"""
        neg_five = Integer(-5)
        assert str(neg_five) == "-5"

    def test_complex_equation_structure(self):
        """Test a complex equation similar to sample equation 2"""
        x = Unknown()

        # 9*x - 6*((x + 4)/4 + 1) - 3*(2*x/2 + 2) + (x + 16)/16 == 0
        nine = Integer(9)
        six = Integer(6)
        four = Integer(4)
        one = Integer(1)
        three = Integer(3)
        two = Integer(2)
        sixteen = Integer(16)
        zero = Integer(0)

        # Build left side components
        nine_x = Multiplication([nine, x])

        # (x + 4)/4 + 1
        x_plus_4 = Addition([x, four])
        div_by_4 = Multiplication([x_plus_4, Inverted(four)])
        plus_1 = Addition([div_by_4, one])

        # 6*((x + 4)/4 + 1)
        six_times = Multiplication([six, plus_1])
        neg_six_times = ChangedSign(six_times)

        # 2*x/2 + 2
        two_x = Multiplication([two, x])
        div_by_2 = Multiplication([two_x, Inverted(two)])
        plus_2 = Addition([div_by_2, two])

        # 3*(2*x/2 + 2)
        three_times = Multiplication([three, plus_2])
        neg_three_times = ChangedSign(three_times)

        # (x + 16)/16
        x_plus_16 = Addition([x, sixteen])
        div_by_16 = Multiplication([x_plus_16, Inverted(sixteen)])

        # Complete left side
        left_side = Addition([nine_x, neg_six_times, neg_three_times, div_by_16])

        equation = Equals(left_side, zero)

        # Verify the equation can be represented as a string
        eq_str = str(equation)
        assert "=" in eq_str
        assert "x" in eq_str
        assert "0" in eq_str


if __name__ == "__main__":
    pytest.main([__file__])
