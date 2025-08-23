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


def random_expression(random_stream, complexity_target: float) -> Expression:
    """
    Generate a random expression in the form of:
    a) (a*x ± b) - linear expression with both coefficient and constant
    b) (a*x) - linear expression with only coefficient (b=0)
    c) (b) - constant expression (a=0)
    """
    # Choose form based on complexity target more strictly
    if complexity_target < 2.0:
        # Simple constant (complexity = 1.0)
        value = random_stream.randint(1, 9)
        return Integer(value)
    elif complexity_target < 4.0:
        # Simple linear term (a*x) - complexity around 3.0
        coeff = random_stream.randint(1, 9)
        coeff_expr = Integer(coeff)

        # Occasionally add complexity with inversion (but only if target allows)
        if complexity_target >= 3.5 and random_stream.random() < 0.3:
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

        # Add complexity modestly
        if complexity_target >= 6.0 and random_stream.random() < 0.2:
            coeff_expr = Inverted(Integer(coeff))

        unknown = Unknown()
        if complexity_target >= 5.5 and random_stream.random() < 0.1:
            unknown = ChangedSign(unknown)

        linear_term = Multiplication([coeff_expr, unknown])

        # Generate constant part
        constant = random_stream.randint(1, 9)
        constant_expr = Integer(constant)

        # Add complexity sparingly
        if complexity_target >= 7.0 and random_stream.random() < 0.1:
            constant_expr = Inverted(constant_expr)
        if random_stream.random() < 0.5:  # 50% chance to subtract instead of add
            constant_expr = ChangedSign(constant_expr)

        return Addition([linear_term, constant_expr])


def random_nonzero_expression(
    random_stream, complexity_target: float, true_x: int
) -> Expression:
    """
    Generate a random expression that evaluates to something other than zero.
    Attempts multiple times to avoid zero-valued expressions.
    """
    max_attempts = 10
    for _ in range(max_attempts):
        # Use slightly lower complexity target to allow for attempts
        actual_target = min(complexity_target, 4.0)
        expr = random_expression(random_stream, actual_target)
        try:
            value = expr.evaluate(true_x)
            if value != 0:
                return expr
        except (ZeroDivisionError, ValueError):
            # Skip expressions that cause division by zero or other errors
            continue

    # Fallback: return a simple non-zero expression
    return Integer(random_stream.randint(1, 9))
