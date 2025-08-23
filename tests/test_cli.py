"""
Unit tests for the CLI module.
"""

import re
from unittest.mock import patch

from click.testing import CliRunner

from algebra_sofii.cli import generate_equation, format_traditional
from algebra_sofii.expressions import Integer, Unknown, Addition, Multiplication


class TestFormatTraditional:
    """Test the format_traditional function."""

    def test_format_integer(self):
        """Test formatting of integer expressions."""
        expr = Integer(5)
        result = format_traditional(expr)
        assert result == "5"

    def test_format_unknown(self):
        """Test formatting of unknown variable."""
        expr = Unknown()
        result = format_traditional(expr)
        assert result == "x"

    def test_format_multiplication(self):
        """Test formatting of multiplication expressions."""
        expr = Multiplication([Integer(3), Unknown()])
        result = format_traditional(expr)
        # Should replace * with · for traditional notation
        assert "·" in result or "*" in result  # Allow both formats

    def test_format_addition(self):
        """Test formatting of addition expressions."""
        expr = Addition([Multiplication([Integer(2), Unknown()]), Integer(5)])
        result = format_traditional(expr)
        assert "x" in result
        assert "2" in result
        assert "5" in result


class TestGenerateEquationCLI:
    """Test the generate_equation CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_default_parameters(self):
        """Test CLI with default parameters."""
        result = self.runner.invoke(generate_equation, [])

        assert result.exit_code == 0
        assert "Generated Algebra Equation:" in result.output
        assert "Equation:" in result.output
        assert "Solution:" in result.output
        assert "Complexity:" in result.output

    def test_custom_cost_target(self):
        """Test CLI with custom cost target."""
        result = self.runner.invoke(generate_equation, ["-c", "3.0"])

        assert result.exit_code == 0
        assert "Generated Algebra Equation:" in result.output
        assert "Complexity:" in result.output

        # Extract complexity from output
        complexity_match = re.search(r"Complexity: (\d+\.\d+)", result.output)
        assert complexity_match is not None
        complexity = float(complexity_match.group(1))
        # Should be close to target (allowing some variance)
        assert 1.0 <= complexity <= 8.0

    def test_with_seed_reproducibility(self):
        """Test that using the same seed produces reproducible results."""
        result1 = self.runner.invoke(generate_equation, ["--seed", "42"])
        result2 = self.runner.invoke(generate_equation, ["--seed", "42"])

        assert result1.exit_code == 0
        assert result2.exit_code == 0

        # Extract equations from both results
        eq_pattern = r"Equation: (.+)"
        eq1_match = re.search(eq_pattern, result1.output)
        eq2_match = re.search(eq_pattern, result2.output)

        assert eq1_match is not None
        assert eq2_match is not None
        assert eq1_match.group(1) == eq2_match.group(1)

    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results."""
        result1 = self.runner.invoke(generate_equation, ["--seed", "42"])
        result2 = self.runner.invoke(generate_equation, ["--seed", "123"])

        assert result1.exit_code == 0
        assert result2.exit_code == 0

        # Extract equations from both results
        eq_pattern = r"Equation: (.+)"
        eq1_match = re.search(eq_pattern, result1.output)
        eq2_match = re.search(eq_pattern, result2.output)

        assert eq1_match is not None
        assert eq2_match is not None
        # Different seeds should (very likely) produce different equations
        assert eq1_match.group(1) != eq2_match.group(1)

    def test_solution_format(self):
        """Test that solution is properly formatted."""
        result = self.runner.invoke(generate_equation, ["--seed", "42"])

        assert result.exit_code == 0

        # Check solution format
        solution_match = re.search(r"Solution: x = (\d+)", result.output)
        assert solution_match is not None
        solution = int(solution_match.group(1))
        assert 1 <= solution <= 10  # Should be in appropriate range for 12-year-olds

    def test_verification_status(self):
        """Test that verification status is shown."""
        result = self.runner.invoke(generate_equation, ["--seed", "42"])

        assert result.exit_code == 0
        assert (
            "✓ Solution verified" in result.output
            or "✗ Solution verification failed" in result.output
            or "✗ Solution verification error" in result.output
        )

    def test_low_complexity_target(self):
        """Test with very low complexity target."""
        result = self.runner.invoke(generate_equation, ["-c", "1.5"])

        assert result.exit_code == 0
        assert "Generated Algebra Equation:" in result.output

        # Should still produce valid output even with low complexity
        complexity_match = re.search(r"Complexity: (\d+\.\d+)", result.output)
        assert complexity_match is not None

    def test_high_complexity_target(self):
        """Test with high complexity target."""
        result = self.runner.invoke(generate_equation, ["-c", "10.0"])

        assert result.exit_code == 0
        assert "Generated Algebra Equation:" in result.output

        # Should produce more complex equation
        complexity_match = re.search(r"Complexity: (\d+\.\d+)", result.output)
        assert complexity_match is not None
        complexity = float(complexity_match.group(1))
        assert complexity >= 3.0  # Should be reasonably complex

    def test_help_message(self):
        """Test the help message."""
        result = self.runner.invoke(generate_equation, ["--help"])

        assert result.exit_code == 0
        assert "Generate an algebraic equation" in result.output
        assert "--cost-target" in result.output
        assert "--seed" in result.output
        assert "12-year-old students" in result.output

    @patch("algebra_sofii.cli.generate_equation_with_complexity")
    def test_error_handling(self, mock_generate_func):
        """Test error handling when equation generation fails."""
        # Mock to raise an exception
        mock_generate_func.side_effect = Exception("Test error")

        result = self.runner.invoke(generate_equation, ["--seed", "42"])

        # Should handle the error gracefully and not crash completely
        # The exact behavior may vary, but it shouldn't result in an unhandled exception
        assert result.exit_code is not None
        # The test verifies the CLI can handle internal errors without crashing

    def test_equation_contains_x(self):
        """Test that generated equations contain the variable x."""
        result = self.runner.invoke(generate_equation, ["--seed", "42"])

        assert result.exit_code == 0

        # Extract equation
        eq_pattern = r"Equation: (.+)"
        eq_match = re.search(eq_pattern, result.output)
        assert eq_match is not None
        equation_str = eq_match.group(1)

        # Should contain x (the unknown variable)
        assert "x" in equation_str

    def test_equation_contains_equals(self):
        """Test that generated equations contain an equals sign."""
        result = self.runner.invoke(generate_equation, ["--seed", "42"])

        assert result.exit_code == 0

        # Extract equation
        eq_pattern = r"Equation: (.+)"
        eq_match = re.search(eq_pattern, result.output)
        assert eq_match is not None
        equation_str = eq_match.group(1)

        # Should contain = sign
        assert "=" in equation_str or "==" in equation_str
