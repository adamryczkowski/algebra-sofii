"""
Command-line interface for algebra equation generator.
"""

import random
from typing import Optional

import click

from .complications import EquationWithSolution


def format_traditional(expression) -> str:
    """Format expression in traditional mathematical notation."""
    # Handle Equals expressions specially to show both sides
    if hasattr(expression, "left") and hasattr(expression, "right"):
        # This is an Equals expression, format both sides
        left_sympy = expression.left.to_sympy_expr()
        right_sympy = expression.right.to_sympy_expr()
        left_str = str(left_sympy).replace("**", "^").replace("*", "·")
        right_str = str(right_sympy).replace("**", "^").replace("*", "·")
        return f"{left_str} = {right_str}"
    else:
        # Regular expression
        sympy_expr = expression.to_sympy_expr()
        return str(sympy_expr).replace("**", "^").replace("*", "·")


@click.command()
@click.option(
    "-c",
    "--cost-target",
    type=float,
    default=5.0,
    help="Target complexity/cost for the generated equation (default: 5.0)",
)
@click.option(
    "--seed", type=int, default=None, help="Random seed for reproducible results"
)
def generate_equation(cost_target: float, seed: Optional[int]) -> None:
    """
    Generate an algebraic equation with solution for 12-year-old students.

    The cost-target parameter controls the complexity of the generated equation:
    - 1-2: Simple constants or basic linear terms
    - 3-4: Linear expressions with coefficients
    - 5-7: Full linear expressions with complications
    - 8+: Complex equations with multiple complications
    """
    if seed is not None:
        random.seed(seed)

    # Generate a random solution between 1 and 10 (appropriate for 12-year-olds)
    solution = random.randint(1, 10)

    # Create equation with solution
    equation_with_solution = EquationWithSolution(solution)

    # Apply complications to reach target complexity
    # Use the same seed for the random stream to ensure reproducibility
    random_stream = random.Random(seed) if seed is not None else random.Random()
    current_complexity = equation_with_solution.get_total_complexity()

    while current_complexity < cost_target:
        try:
            complication = equation_with_solution.random_complication(
                cost_target, random_stream, maintain_linearity=True
            )
            equation_with_solution.apply_complication(complication)

            # Verify the solution is still valid
            if not equation_with_solution.verify_solution():
                # If solution becomes invalid, remove the last complication
                equation_with_solution._complications.pop()
                equation_with_solution._update_cache()
                break

            current_complexity = equation_with_solution.get_total_complexity()

            # Safety check to prevent infinite loops
            if len(equation_with_solution.complications) > 10:
                break

        except Exception:
            # If any error occurs during complication, stop adding them
            break

    # Get the final equation
    equation = equation_with_solution.get_current_equation()

    # Format output
    click.echo("Generated Algebra Equation:")
    click.echo("=" * 40)
    click.echo(f"Equation: {format_traditional(equation)}")
    click.echo(f"Solution: x = {solution}")
    click.echo(f"Complexity: {current_complexity:.1f}")

    # Verification - we know equation is an Equals expression
    try:
        if hasattr(equation, "left") and hasattr(equation, "right"):
            left_val = equation.left.evaluate(solution)  # type: ignore
            right_val = equation.right.evaluate(solution)  # type: ignore
            if abs(left_val - right_val) < 1e-10:
                click.echo("✓ Solution verified")
            else:
                click.echo("✗ Solution verification failed")
        else:
            click.echo("✗ Solution verification error: equation format unexpected")
    except Exception as e:
        click.echo(f"✗ Solution verification error: {e}")


if __name__ == "__main__":
    generate_equation()
