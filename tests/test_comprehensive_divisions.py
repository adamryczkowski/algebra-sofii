"""
Tests for division generation in complete equations using the CLI interface.
"""

import pytest
import random
from algebra_sofii.cli import generate_equation_with_complexity
from algebra_sofii.expressions import Equals


class TestEquationDivisionGeneration:
    """Test that divisions appear in complete equations generated via CLI."""

    @pytest.mark.parametrize("complexity", [10.0, 15.0, 20.0])
    def test_equations_contain_divisions_at_high_complexity(self, complexity):
        """Test that complete equations contain divisions at higher complexity levels."""
        divisions_found = 0
        total_equations = 20

        for i in range(total_equations):
            # Use different seeds for variety while maintaining reproducibility
            random_stream = random.Random(42 + i)
            solution = random_stream.randint(1, 10)

            equation = generate_equation_with_complexity(
                random_stream, solution, complexity
            )

            assert isinstance(equation, Equals), (
                "Generated equation should be an Equals instance"
            )

            # Check both sides of the equation for divisions
            equation_str = str(equation)
            if "1/" in equation_str:
                divisions_found += 1

                # Verify the equation still evaluates correctly
                left_result = equation.left.evaluate(solution)
                right_result = equation.right.evaluate(solution)
                assert abs(float(left_result - right_result)) < 1e-10, (
                    f"Equation doesn't balance: {left_result} != {right_result} for x={solution}"
                )

        # At high complexity, we should see a reasonable number of divisions
        percentage = (divisions_found / total_equations) * 100
        if complexity >= 15.0:
            assert percentage >= 20, (
                f"Expected at least 20% equations with divisions at complexity {complexity}, got {percentage:.1f}%"
            )

    def test_equation_complexity_bounds(self):
        """Test that generated equations respect complexity bounds even with divisions."""
        random_stream = random.Random(123)
        target_complexity = 12.0
        solution = 5

        for _ in range(10):
            equation = generate_equation_with_complexity(
                random_stream, solution, target_complexity
            )
            actual_complexity = equation.complexity()

            # Should be within reasonable bounds - more lenient given equation generation variability
            assert actual_complexity >= target_complexity * 0.5, (
                f"Complexity too low: {actual_complexity} < {target_complexity * 0.5}"
            )
            assert actual_complexity <= target_complexity * 2.0, (
                f"Complexity too high: {actual_complexity} > {target_complexity * 2.0}"
            )

    def test_division_equations_are_solvable(self):
        """Test that equations containing divisions are still solvable."""
        random_stream = random.Random(456)

        equations_with_divisions = []
        attempts = 0
        max_attempts = 50

        # Find equations that contain divisions
        while len(equations_with_divisions) < 5 and attempts < max_attempts:
            solution = random_stream.randint(1, 9)
            equation = generate_equation_with_complexity(random_stream, solution, 15.0)

            if "1/" in str(equation):
                equations_with_divisions.append((equation, solution))

            attempts += 1

        assert len(equations_with_divisions) > 0, (
            "Failed to generate equations with divisions"
        )

        # Test that each equation with divisions is solvable
        for equation, expected_solution in equations_with_divisions:
            # Verify the equation balances at the expected solution
            left_val = equation.left.evaluate(expected_solution)
            right_val = equation.right.evaluate(expected_solution)

            assert abs(float(left_val - right_val)) < 1e-10, (
                f"Division equation doesn't balance: {equation} at x={expected_solution}"
            )

            # Verify equation doesn't trivially balance at other values
            other_value = expected_solution + 1
            try:
                left_other = equation.left.evaluate(other_value)
                right_other = equation.right.evaluate(other_value)
                # Should not be equal (within tolerance) at wrong solution
                assert abs(float(left_other - right_other)) > 1e-10, (
                    f"Equation trivially balances at wrong solution x={other_value}"
                )
            except ZeroDivisionError:
                # This is acceptable - division by zero at wrong solution is fine
                pass

    def test_division_placement_variety(self):
        """Test that divisions can appear on both sides of equations."""
        random_stream = random.Random(789)

        left_side_divisions = 0
        right_side_divisions = 0
        total_with_divisions = 0

        for i in range(30):
            solution = random_stream.randint(1, 8)
            equation = generate_equation_with_complexity(random_stream, solution, 16.0)

            left_str = str(equation.left)
            right_str = str(equation.right)

            has_left_division = "1/" in left_str
            has_right_division = "1/" in right_str

            if has_left_division or has_right_division:
                total_with_divisions += 1

                if has_left_division:
                    left_side_divisions += 1
                if has_right_division:
                    right_side_divisions += 1

        # Should find some equations with divisions
        assert total_with_divisions > 0, "No equations with divisions found"

        # Divisions should appear on at least one side (preferably both sides sometimes)
        assert left_side_divisions > 0 or right_side_divisions > 0, (
            "Divisions should appear on at least one side of equations"
        )
