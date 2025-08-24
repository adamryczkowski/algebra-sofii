"""
Random expression generators for algebraic equations.
"""

from .expressions import Equals

from .expressions import (
    Addition,
    ChangedSign,
    Expression,
    Integer,
    Inverted,
    Multiplication,
    Unknown,
)
from .random_class import RandomClass


def random_expression(
    random_stream: RandomClass,
    complexity_target: float,
    exclude_unknown: bool = False,
) -> Expression:
    """
    Generate a random expression in the form of:
    a) (a*x ± b) - linear expression with both coefficient and constant
    b) (a*x) - linear expression with only coefficient (b=0)
    c) (b) - constant expression (a=0)

    Args:
        random_stream: Random number generator
        complexity_target: Target complexity for the expression
        exclude_unknown: If True, generates expressions without the unknown variable x
    """
    # If excluding unknown, generate only constant expressions
    if exclude_unknown:
        if complexity_target < 2.0:
            # Simple constant (complexity = 1.0)
            value = random_stream.randint(1, 9)
            return Integer(value)
        elif complexity_target < 4.0:
            # Constant with some complexity - inversion or sign change
            value = random_stream.randint(1, 9)
            expr = Integer(value)

            # Increased probability for divisions: was 0.5, now 0.7
            if complexity_target >= 2.5 and random_stream.rand_coinflip(0.7):
                expr = Inverted(expr)
            if random_stream.rand_coinflip(0.3):
                expr = ChangedSign(expr)

            return expr
        else:
            # More complex constant expression - addition of two constants
            val1 = random_stream.randint(1, 9)
            val2 = random_stream.randint(1, 9)

            expr1 = Integer(val1)
            expr2 = Integer(val2)

            # Increased probability for divisions: was 0.3, now 0.6, and lowered threshold
            if complexity_target >= 4.0 and random_stream.rand_coinflip(0.6):
                expr1 = Inverted(expr1)
            if random_stream.rand_coinflip(0.5):
                expr2 = ChangedSign(expr2)

            return Addition([expr1, expr2])

    # Original logic for expressions that can include unknown
    # Choose form based on complexity target more strictly
    if complexity_target < 2.0:
        # Simple constant (complexity = 1.0)
        value = random_stream.randint(1, 9)
        return Integer(value)
    elif complexity_target < 4.0:
        # Simple linear term (a*x) - complexity around 3.0
        coeff = random_stream.randint(1, 9)
        coeff_expr = Integer(coeff)

        # Increased probability for divisions: was 0.3, now 0.6, and lowered threshold
        if complexity_target >= 3.0 and random_stream.rand_coinflip(0.6):
            coeff_expr = Inverted(Integer(coeff))

        unknown = Unknown()
        # Occasionally negate unknown if complexity allows
        if complexity_target >= 3.0 and random_stream.rand_coinflip(0.2):
            unknown = ChangedSign(unknown)

        return Multiplication([coeff_expr, unknown])
    else:
        # Full linear expression (a*x ± b) - complexity around 5-7
        # Generate coefficient part
        coeff = random_stream.randint(1, 9)
        coeff_expr = Integer(coeff)

        # Increased probability for divisions: was 0.2, now 0.5, and lowered threshold
        if complexity_target >= 4.5 and random_stream.rand_coinflip(0.5):
            coeff_expr = Inverted(Integer(coeff))

        unknown = Unknown()
        if complexity_target >= 5.5 and random_stream.rand_coinflip(0.1):
            unknown = ChangedSign(unknown)

        linear_term = Multiplication([coeff_expr, unknown])

        # Generate constant part
        const_val = random_stream.randint(1, 9)
        const_expr = Integer(const_val)

        # Occasionally make constant negative or inverted
        if random_stream.rand_coinflip(0.3):
            const_expr = ChangedSign(const_expr)
        if complexity_target >= 6.0 and random_stream.rand_coinflip(0.2):
            const_expr = Inverted(const_expr)

        return Addition([linear_term, const_expr])


def random_nonzero_expression(
    random_stream, complexity_target: float, true_x: int, exclude_unknown: bool = False
) -> Expression:
    """
    Generate a random expression that evaluates to something other than zero.
    Attempts multiple times to avoid zero-valued expressions.

    Args:
        random_stream: Random number generator
        complexity_target: Target complexity for the expression
        true_x: Value to test the expression against to ensure it's non-zero
        exclude_unknown: If True, generates expressions without the unknown variable x
    """
    max_attempts = 10
    for _ in range(max_attempts):
        # Use slightly lower complexity target to allow for attempts
        actual_target = min(complexity_target, 4.0)
        expr = random_expression(random_stream, actual_target, exclude_unknown)
        try:
            value = expr.evaluate(true_x)
            if value != 0:
                return expr
        except (ZeroDivisionError, ValueError):
            # Skip expressions that cause division by zero or other errors
            continue

    # Fallback: return a simple non-zero expression
    return Integer(random_stream.randint(1, 9))


def generate_sample_style_equation(
    random_stream: RandomClass,
    solution: int,
    target_complexity: float,
) -> Equals:
    """
    Generate equations similar to the sample style with strategic fractions,
    nested parentheses, and meaningful structure.

    Creates equations that definitely have the correct solution by starting with
    simple forms and adding balanced complications.
    """
    from .expressions import (
        Equals,
        Addition,
        Multiplication,
        Integer,
        Unknown,
        Inverted,
    )

    # Choose coefficients for visually complex fractions
    coeffs = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    # Build terms that look complex but simplify nicely
    left_terms = []
    right_terms = []

    # Start with a base term that equals x
    base_coeff = random_stream.choice(coeffs)
    # Create base_coeff*x/base_coeff which equals x
    base_term = Multiplication(
        [
            Multiplication([Integer(base_coeff), Unknown()]),
            Inverted(Integer(base_coeff)),
        ]
    )
    left_terms.append(base_term)

    # Add a simple constant
    constant1 = random_stream.randint(3, 8)
    left_terms.append(Integer(constant1))

    # Add some complex-looking terms to the right side
    # These will be designed to match specific parts of the left side

    # Add a term like: coeff*((other_coeff*x)/other_coeff - offset)
    coeff1 = random_stream.choice([3, 4, 5, 6])
    other_coeff = random_stream.choice([2, 3, 4, 5])
    offset1 = random_stream.randint(4, 8)

    inner_x_term = Multiplication(
        [
            Multiplication([Integer(other_coeff), Unknown()]),
            Inverted(Integer(other_coeff)),
        ]
    )  # This equals x

    inner_expr = Addition([inner_x_term, Integer(-offset1)])  # x - offset1
    complex_term1 = Multiplication(
        [Integer(coeff1), inner_expr]
    )  # coeff1 * (x - offset1)
    right_terms.append(complex_term1)

    # Add another complex term: coeff2*((x + offset2)/offset2 + extra)
    coeff2 = random_stream.choice([2, 3, 4])
    offset2 = random_stream.choice([15, 16, 17, 18, 19, 20])
    extra = random_stream.randint(1, 3)

    inner_fraction = Multiplication(
        [
            Addition([Unknown(), Integer(offset2)]),
            Inverted(Integer(offset2)),
        ]
    )  # (x + offset2)/offset2 = x/offset2 + 1

    inner_with_extra = Addition(
        [inner_fraction, Integer(extra)]
    )  # x/offset2 + 1 + extra
    complex_term2 = Multiplication([Integer(coeff2), inner_with_extra])

    # We need to negate this term to balance the equation
    right_terms.append(ChangedSign(complex_term2))

    # Now calculate what the constant on the right should be
    # We have: base_coeff*x/base_coeff + constant1 = coeff1*(x - offset1) - coeff2*(x/offset2 + 1 + extra)
    # Simplify: x + constant1 = coeff1*x - coeff1*offset1 - coeff2*x/offset2 - coeff2 - coeff2*extra
    # At x = solution: solution + constant1 = coeff1*solution - coeff1*offset1 - coeff2*solution/offset2 - coeff2 - coeff2*extra

    right_constant = (solution + constant1) - (
        coeff1 * solution
        - coeff1 * offset1
        - coeff2 * solution / offset2
        - coeff2
        - coeff2 * extra
    )

    if abs(right_constant) > 0.1:  # If we need a balancing constant
        right_terms.append(Integer(int(round(right_constant))))

    # Build the final equation
    left_side = Addition(left_terms) if len(left_terms) > 1 else left_terms[0]

    if len(right_terms) == 0:
        right_side = Integer(0)
    elif len(right_terms) == 1:
        right_side = right_terms[0]
    else:
        right_side = Addition(right_terms)

    return Equals(left_side, right_side)
