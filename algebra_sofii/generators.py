"""
Random expression generators for algebraic equations.
"""

from .expressions import (
    Addition,
    ChangedSign,
    Expression,
    Integer,
    Inverted,
    Multiplication,
    Unknown,
)


def random_expression(
    random_stream, complexity_target: float, exclude_unknown: bool = False
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
            if complexity_target >= 2.5 and random_stream.random() < 0.7:
                expr = Inverted(expr)
            if random_stream.random() < 0.3:
                expr = ChangedSign(expr)

            return expr
        else:
            # More complex constant expression - addition of two constants
            val1 = random_stream.randint(1, 9)
            val2 = random_stream.randint(1, 9)

            expr1 = Integer(val1)
            expr2 = Integer(val2)

            # Increased probability for divisions: was 0.3, now 0.6, and lowered threshold
            if complexity_target >= 4.0 and random_stream.random() < 0.6:
                expr1 = Inverted(expr1)
            if random_stream.random() < 0.5:
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
        if complexity_target >= 3.0 and random_stream.random() < 0.6:
            coeff_expr = Inverted(Integer(coeff))

        unknown = Unknown()
        # Occasionally negate unknown if complexity allows
        if complexity_target >= 3.0 and random_stream.random() < 0.2:
            unknown = ChangedSign(unknown)

        return Multiplication([coeff_expr, unknown])
    else:
        # Full linear expression (a*x ± b) - complexity around 5-7
        # Generate coefficient part
        coeff = random_stream.randint(1, 9)
        coeff_expr = Integer(coeff)

        # Increased probability for divisions: was 0.2, now 0.5, and lowered threshold
        if complexity_target >= 4.5 and random_stream.random() < 0.5:
            coeff_expr = Inverted(Integer(coeff))

        unknown = Unknown()
        if complexity_target >= 5.5 and random_stream.random() < 0.1:
            unknown = ChangedSign(unknown)

        linear_term = Multiplication([coeff_expr, unknown])

        # Generate constant part
        constant = random_stream.randint(1, 9)
        constant_expr = Integer(constant)

        # Increased probability for divisions: was 0.1, now 0.4, and lowered threshold
        if complexity_target >= 5.0 and random_stream.random() < 0.4:
            constant_expr = Inverted(constant_expr)
        if random_stream.random() < 0.5:  # 50% chance to subtract instead of add
            constant_expr = ChangedSign(constant_expr)

        return Addition([linear_term, constant_expr])


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
