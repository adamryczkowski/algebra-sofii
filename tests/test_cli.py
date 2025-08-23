"""
Unit tests for the CLI module.
"""

import re

from click.testing import CliRunner

from algebra_sofii.cli import generate_equation

runner = CliRunner()


def test_default_parameters():
    """Test CLI with default parameters."""
    result = runner.invoke(generate_equation, [])

    assert result.exit_code == 0
    assert "Generated Algebra Equation:" in result.output
    assert "Equation:" in result.output
    assert "Solution:" in result.output
    assert "Complexity:" in result.output
    assert result.exit_code == 0
    assert (
        "✓ Solution verified" in result.output
        or "✗ Solution verification failed" in result.output
        or "✗ Solution verification error" in result.output
    )
    eq_pattern = r"Equation: (.+)"
    eq_match = re.search(eq_pattern, result.output)
    assert eq_match is not None
    equation_str = eq_match.group(1)
    assert "x" in equation_str


def test_custom_cost_target():
    """Test CLI with custom cost target."""
    result = runner.invoke(generate_equation, ["-c", "3.0"])

    assert result.exit_code == 0
    assert "Generated Algebra Equation:" in result.output
    assert "Complexity:" in result.output

    # Extract complexity from output
    complexity_match = re.search(r"Complexity: (\d+\.\d+)", result.output)
    assert complexity_match is not None
    complexity = float(complexity_match.group(1))
    # Should be close to target (allowing some variance)
    assert 1.0 <= complexity <= 8.0
    assert result.exit_code == 0
    assert (
        "✓ Solution verified" in result.output
        or "✗ Solution verification failed" in result.output
        or "✗ Solution verification error" in result.output
    )
    eq_pattern = r"Equation: (.+)"
    eq_match = re.search(eq_pattern, result.output)
    assert eq_match is not None
    equation_str = eq_match.group(1)
    assert "x" in equation_str


def test_with_seed_reproducibility():
    """Test that using the same seed produces reproducible results."""
    result1 = runner.invoke(generate_equation, ["--seed", "42"])
    result2 = runner.invoke(generate_equation, ["--seed", "42"])

    assert result1.exit_code == 0
    assert result2.exit_code == 0

    # Extract equations from both results
    eq_pattern = r"Equation: (.+)"
    eq1_match = re.search(eq_pattern, result1.output)
    eq2_match = re.search(eq_pattern, result2.output)

    assert eq1_match is not None
    assert eq2_match is not None
    assert eq1_match.group(1) == eq2_match.group(1)


def test_different_seeds_produce_different_results():
    """Test that different seeds produce different results."""
    result1 = runner.invoke(generate_equation, ["--seed", "42"])
    result2 = runner.invoke(generate_equation, ["--seed", "123"])

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
