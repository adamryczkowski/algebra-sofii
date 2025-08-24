"""
Command-line interface for algebra equation generator.
"""

from typing import Optional

import click

from .expressions import Equals, Integer, Unknown, Addition, Multiplication
from .generators import random_expression
from .random_class import RandomClass


def generate_equation_with_complexity(
    random_stream: RandomClass, solution: int, target_complexity: float
) -> Equals:
    """Generate an equation with approximately the target complexity."""

    if target_complexity < 2.5:
        # Simple equation: x = solution
        return Equals.from_solution(solution, swap=random_stream.choice([True, False]))

    elif target_complexity < 5.0:
        # Medium complexity: linear expression = solution
        # Generate a simple linear expression
        coeff = random_stream.randint(1, 5)
        constant = random_stream.randint(-5, 5)

        # Create ax + b = solution, so x should equal (solution - b) / a
        # But we want x = solution, so we create ax + b = a*solution + b
        left_side = Addition(
            [Multiplication([Integer(coeff), Unknown()]), Integer(constant)]
        )
        right_value = coeff * solution + constant
        right_side = Integer(right_value)

        equation = Equals(left_side, right_side)

        # Add some complications if complexity target is higher
        if target_complexity > 3.5:
            equation = add_simple_complications(random_stream, equation, 1)

        return equation

    else:
        # High complexity: build equation progressively to match target
        # Start with a simple base equation
        coeff = random_stream.randint(1, 3)
        constant = random_stream.randint(-3, 3)

        left_side = Addition(
            [Multiplication([Integer(coeff), Unknown()]), Integer(constant)]
        )
        right_value = coeff * solution + constant
        right_side = Integer(right_value)

        base_equation = Equals(left_side, right_side)

        # Calculate how many complications we need
        current_complexity = base_equation.complexity()
        remaining_complexity = target_complexity - current_complexity

        # Estimate complexity per complication more conservatively
        estimated_complexity_per_complication = 3.0
        num_complications = max(
            0, int(remaining_complexity / estimated_complexity_per_complication)
        )

        # Cap complications to prevent runaway complexity
        num_complications = min(num_complications, int(target_complexity / 2))

        equation = add_simple_complications(
            random_stream, base_equation, num_complications
        )

        return equation


def add_simple_complications(
    random_stream: RandomClass, equation: Equals, num_complications: int
) -> Equals:
    """Add simple complications to an equation."""
    current_equation = equation

    for _ in range(num_complications):
        # Choose a random complication type
        complication_types = ["add_zero", "multiply_by_one", "negate"]
        complication_type = random_stream.choice(complication_types)

        # Generate a small random expression for the complication
        try:
            if complication_type == "add_zero":
                # Add the same expression to both sides
                complication_expr = random_expression(
                    random_stream, 2.0, exclude_unknown=False
                )
                current_equation = current_equation.add_to_sides(
                    complication_expr, left_side=random_stream.rand_coinflip(0.5)
                )
            elif complication_type == "multiply_by_one":
                # Multiply both sides by the expression
                complication_expr = random_expression(
                    random_stream, 2.0, exclude_unknown=True
                )
                current_equation = current_equation.multiply_sides_by(
                    complication_expr, left_side=random_stream.rand_coinflip(0.5)
                )
            elif complication_type == "negate":
                # Apply negation to BOTH sides to maintain equation balance
                from .expressions import ChangedSign

                new_left = ChangedSign(current_equation.left)
                new_right = ChangedSign(current_equation.right)
                current_equation = Equals(new_left, new_right)
        except Exception:
            # If complication fails, skip it
            continue

    return current_equation


@click.group()
def cli():
    """Algebra equation generator for 12-year-old students."""
    pass


@cli.command()
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
def generate(cost_target: float, seed: Optional[int]) -> None:
    """
    Generate a single algebraic equation with solution.

    The cost-target parameter controls the complexity of the generated equation:
    - 1-2: Simple constants or basic linear terms
    - 3-4: Linear expressions with coefficients
    - 5-7: Full linear expressions with complications
    - 8+: Complex equations with multiple complications
    """
    if seed is not None:
        random_stream = RandomClass.FromFixedSeed(seed)
    else:
        random_stream = RandomClass()

    # Generate a random solution between 1 and 10 (appropriate for 12-year-olds)
    solution = random_stream.randint(1, 10)

    # Generate equation with target complexity
    equation = generate_equation_with_complexity(random_stream, solution, cost_target)
    current_complexity = equation.complexity()

    # Format output
    click.echo("Generated Algebra Equation:")
    click.echo("=" * 40)
    click.echo(f"Equation: {str(equation)}")
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


@cli.command()
@click.argument("count", type=int)
@click.option(
    "-c",
    "--cost-target",
    type=float,
    default=5.0,
    help="Target complexity/cost for the generated equations (default: 5.0)",
)
@click.option(
    "--seed", type=int, default=None, help="Random seed for reproducible results"
)
@click.option(
    "--verify/--no-verify",
    default=False,
    help="Verify solutions for each equation (default: False)",
)
def batch(count: int, cost_target: float, seed: Optional[int], verify: bool) -> None:
    """
    Generate multiple algebraic equations with solutions.

    COUNT is the number of equations to generate.

    Example: algebra-equation batch 30 -c 50
    """
    if count <= 0:
        click.echo("Error: Count must be a positive integer")
        return

    if seed is not None:
        random_stream = RandomClass.FromFixedSeed(seed)
    else:
        random_stream = RandomClass()

    equations = []
    solutions = []
    verified_count = 0
    failed_count = 0

    # Generate all equations and solutions
    for i in range(count):
        # Generate a random solution between 1 and 10 (appropriate for 12-year-olds)
        solution = random_stream.randint(1, 7)

        # Generate equation with target complexity
        equation = generate_equation_with_complexity(
            random_stream, solution, cost_target
        )

        equations.append(str(equation))
        solutions.append(solution)

        # Optional verification
        if verify:
            try:
                if hasattr(equation, "left") and hasattr(equation, "right"):
                    left_val = equation.left.evaluate(solution)  # type: ignore
                    right_val = equation.right.evaluate(solution)  # type: ignore
                    if abs(left_val - right_val) < 1e-10:
                        verified_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
            except Exception:
                failed_count += 1

    # Output in the requested format
    click.echo("Equations:")
    for i, equation in enumerate(equations, 1):
        click.echo(f"{i}. {equation}")

    click.echo("")  # Vertical space

    click.echo("Solutions:")
    for i, solution in enumerate(solutions, 1):
        click.echo(f"{i}. x = {solution}")

    # Optional verification summary
    if verify:
        click.echo("")
        if failed_count > 0:
            click.echo(f"Verification: {verified_count} passed, {failed_count} failed")
        else:
            click.echo(f"All {verified_count} solutions verified successfully")
