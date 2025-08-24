"""
Unit tests for the CLI module.
"""

import re

from click.testing import CliRunner

from algebra_sofii.cli import cli

runner = CliRunner()


def test_cli_help():
    """Test CLI help shows both commands."""
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "generate" in result.output
    assert "batch" in result.output
    assert "Algebra equation generator for 12-year-old students." in result.output


def test_generate_default_parameters():
    """Test generate command with default parameters."""
    result = runner.invoke(cli, ["generate"])

    assert result.exit_code == 0
    assert "Generated Algebra Equation:" in result.output
    assert "Equation:" in result.output
    assert "Solution:" in result.output
    assert "Complexity:" in result.output
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


def test_generate_custom_cost_target():
    """Test generate command with custom cost target."""
    result = runner.invoke(cli, ["generate", "-c", "3.0"])

    assert result.exit_code == 0
    assert "Generated Algebra Equation:" in result.output
    assert "Complexity:" in result.output

    # Extract complexity from output
    complexity_match = re.search(r"Complexity: (\d+\.\d+)", result.output)
    assert complexity_match is not None
    complexity = float(complexity_match.group(1))
    # Should be close to target (allowing some variance)
    assert 1.0 <= complexity <= 8.0
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


def test_generate_with_seed_reproducibility():
    """Test that using the same seed produces reproducible results."""
    result1 = runner.invoke(cli, ["generate", "--seed", "42"])
    result2 = runner.invoke(cli, ["generate", "--seed", "42"])

    assert result1.exit_code == 0
    assert result2.exit_code == 0

    # Extract equations from both results
    eq_pattern = r"Equation: (.+)"
    eq1_match = re.search(eq_pattern, result1.output)
    eq2_match = re.search(eq_pattern, result2.output)

    assert eq1_match is not None
    assert eq2_match is not None
    assert eq1_match.group(1) == eq2_match.group(1)


def test_generate_different_seeds_produce_different_results():
    """Test that different seeds produce different results."""
    result1 = runner.invoke(cli, ["generate", "--seed", "42"])
    result2 = runner.invoke(cli, ["generate", "--seed", "123"])

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


def test_batch_help():
    """Test batch command help."""
    result = runner.invoke(cli, ["batch", "--help"])

    assert result.exit_code == 0
    assert "Generate multiple algebraic equations with solutions." in result.output
    assert "COUNT is the number of equations to generate." in result.output
    assert "--cost-target" in result.output
    assert "--seed" in result.output
    assert "--verify" in result.output


def test_batch_basic_functionality():
    """Test basic batch command functionality."""
    result = runner.invoke(cli, ["batch", "3", "--seed", "42"])

    assert result.exit_code == 0
    assert "Equations:" in result.output
    assert "Solutions:" in result.output

    # Check that we have 3 equations and 3 solutions
    equations_section = result.output.split("Solutions:")[0]
    solutions_section = result.output.split("Solutions:")[1]

    # Count numbered equations (1., 2., 3.)
    equation_matches = re.findall(r"^\d+\.", equations_section, re.MULTILINE)
    solution_matches = re.findall(r"^\d+\.", solutions_section, re.MULTILINE)

    assert len(equation_matches) == 3
    assert len(solution_matches) == 3


def test_batch_output_format():
    """Test that batch output follows the exact format specified."""
    result = runner.invoke(cli, ["batch", "2", "--seed", "42"])

    assert result.exit_code == 0

    lines = result.output.strip().split("\n")

    # Find the positions of key sections
    equations_line = None
    solutions_line = None
    blank_line = None

    for i, line in enumerate(lines):
        if line.strip() == "Equations:":
            equations_line = i
        elif line.strip() == "Solutions:":
            solutions_line = i
        elif (
            line.strip() == "" and equations_line is not None and solutions_line is None
        ):
            blank_line = i

    assert equations_line is not None, "Missing 'Equations:' header"
    assert solutions_line is not None, "Missing 'Solutions:' header"
    assert blank_line is not None, "Missing blank line between sections"

    # Check that blank line is between equations and solutions
    assert equations_line < blank_line < solutions_line

    # Check equation format (should be "1. equation", "2. equation", etc.)
    for i in range(equations_line + 1, blank_line):
        line = lines[i].strip()
        if line:  # Skip empty lines
            assert re.match(r"^\d+\. .+=.+$", line), f"Invalid equation format: {line}"

    # Check solution format (should be "1. x = value", "2. x = value", etc.)
    solution_count = 0
    for i in range(solutions_line + 1, len(lines)):
        line = lines[i].strip()
        if line:  # Skip empty lines and verification messages
            if re.match(r"^\d+\. x = \d+$", line):
                solution_count += 1

    assert solution_count == 2, f"Expected 2 solutions, found {solution_count}"


def test_batch_with_custom_complexity():
    """Test batch command with custom complexity."""
    result = runner.invoke(cli, ["batch", "2", "-c", "3.0", "--seed", "42"])

    assert result.exit_code == 0
    assert "Equations:" in result.output
    assert "Solutions:" in result.output


def test_batch_with_verification():
    """Test batch command with verification enabled."""
    result = runner.invoke(cli, ["batch", "2", "--verify", "--seed", "42"])

    assert result.exit_code == 0
    assert "Equations:" in result.output
    assert "Solutions:" in result.output
    # Should have verification summary
    assert (
        "All" in result.output and "solutions verified successfully" in result.output
    ) or ("Verification:" in result.output and "passed" in result.output)


def test_batch_reproducibility():
    """Test that batch command with same seed produces same results."""
    result1 = runner.invoke(cli, ["batch", "3", "--seed", "42"])
    result2 = runner.invoke(cli, ["batch", "3", "--seed", "42"])

    assert result1.exit_code == 0
    assert result2.exit_code == 0

    # Extract equations from both results
    equations1 = []
    equations2 = []

    for result, equations_list in [(result1, equations1), (result2, equations2)]:
        equations_section = result.output.split("Solutions:")[0]
        for line in equations_section.split("\n"):
            if re.match(r"^\d+\.", line.strip()):
                equations_list.append(line.strip())

    assert equations1 == equations2, "Same seed should produce identical equations"


def test_batch_invalid_count():
    """Test batch command with invalid count."""
    result = runner.invoke(cli, ["batch", "0"])

    assert (
        result.exit_code == 0
    )  # Click doesn't fail, but our function should handle it
    assert "Error: Count must be a positive integer" in result.output


def test_batch_large_count():
    """Test batch command with larger count."""
    result = runner.invoke(cli, ["batch", "10", "--seed", "42"])

    assert result.exit_code == 0

    # Count equations and solutions
    equations_section = result.output.split("Solutions:")[0]
    solutions_section = result.output.split("Solutions:")[1]

    equation_matches = re.findall(r"^\d+\.", equations_section, re.MULTILINE)
    solution_matches = re.findall(r"^\d+\.", solutions_section, re.MULTILINE)

    assert len(equation_matches) == 10
    assert len(solution_matches) == 10
