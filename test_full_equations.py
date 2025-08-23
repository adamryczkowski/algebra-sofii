#!/usr/bin/env python3
"""
Test script to generate complete equations with divisions.
"""

import random
from algebra_sofii.cli import generate_equation_with_complexity


def test_full_equations():
    """Generate and display complete equations to check for divisions."""
    print("Testing complete equation generation with divisions:")
    print("=" * 60)

    for i in range(5):
        random.seed(42 + i)
        random_stream = random.Random(42 + i)
        solution = random.randint(1, 10)

        equation = generate_equation_with_complexity(random_stream, solution, 10.0)
        equation_str = str(equation)
        complexity = equation.complexity()

        print(f"\nEquation {i + 1}:")
        print(f"  {equation_str}")
        print(f"  Solution: x = {solution}")
        print(f"  Complexity: {complexity:.1f}")

        # Check for divisions
        if "1/" in equation_str:
            print("  ✓ Contains divisions!")
        else:
            print("  ○ No divisions found")


if __name__ == "__main__":
    test_full_equations()
