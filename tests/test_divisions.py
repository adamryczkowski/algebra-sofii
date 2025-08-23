"""
Tests for division (Inverted expression) generation in random expressions.
"""

import pytest
from algebra_sofii.expressions import Inverted, Multiplication, Addition, Unknown
from algebra_sofii.generators import random_expression


class TestDivisionGeneration:
    """Test that divisions (Inverted expressions) are properly generated."""

    @pytest.mark.parametrize("complexity", [3.0, 5.0, 6.0])
    def test_divisions_generated_at_medium_complexity(self, complexity, random_stream):
        """Test that divisions are generated at medium to high complexity levels."""
        divisions_found = 0
        total_tests = 100  # Increased for better statistics

        for _ in range(total_tests):
            expr = random_expression(random_stream, complexity)
            if self._contains_division(expr):
                divisions_found += 1

        # At complexity 3+, we should see some divisions based on actual generation logic
        percentage = (divisions_found / total_tests) * 100

        if complexity >= 5.0:
            # At high complexity, expect reasonable division rate
            assert percentage >= 15, (
                f"Expected at least 15% divisions at complexity {complexity}, got {percentage:.1f}%"
            )
        elif complexity >= 3.0:
            # At medium complexity, expect some divisions but allow variability
            assert percentage >= 5, (
                f"Expected at least 5% divisions at complexity {complexity}, got {percentage:.1f}%"
            )

    def test_no_divisions_at_low_complexity(self, random_stream):
        """Test that very low complexity expressions don't generate divisions."""
        divisions_found = 0
        total_tests = 20

        for _ in range(total_tests):
            expr = random_expression(random_stream, 1.5)  # Very low complexity
            if self._contains_division(expr):
                divisions_found += 1

        # Should be very rare or nonexistent at such low complexity
        assert divisions_found <= 2, (
            f"Too many divisions ({divisions_found}) at low complexity"
        )

    def test_division_structure_is_valid(self, random_stream):
        """Test that generated divisions have valid structure."""
        for complexity in [3.0, 4.0, 5.0]:
            for _ in range(20):
                expr = random_expression(random_stream, complexity)
                divisions = self._find_all_divisions(expr)

                for division in divisions:
                    # Divisions should have non-zero operands
                    assert division.operand is not None

                    # Should be able to evaluate without error
                    try:
                        result = division.evaluate(2)  # Test with x=2
                        assert result != 0
                    except ZeroDivisionError:
                        pytest.fail("Division generated with zero denominator")

    def test_divisions_in_exclude_unknown_mode(self, random_stream):
        """Test that divisions are still generated when excluding unknown variables."""
        divisions_found = 0
        total_tests = 30

        for _ in range(total_tests):
            expr = random_expression(random_stream, 4.0, exclude_unknown=True)
            if self._contains_division(expr):
                divisions_found += 1
                # Verify no unknown variables are present
                assert not self._contains_unknown(expr)

        assert divisions_found > 0, "No divisions found in exclude_unknown mode"

    def _contains_division(self, expr) -> bool:
        """Check if expression contains any Inverted (division) operations."""
        if isinstance(expr, Inverted):
            return True
        elif isinstance(expr, (Addition, Multiplication)):
            return any(self._contains_division(op) for op in expr.operands)
        elif hasattr(expr, "operand"):  # ChangedSign
            return self._contains_division(expr.operand)
        return False

    def _contains_unknown(self, expr) -> bool:
        """Check if expression contains Unknown variables."""
        if isinstance(expr, Unknown):
            return True
        elif isinstance(expr, (Addition, Multiplication)):
            return any(self._contains_unknown(op) for op in expr.operands)
        elif hasattr(expr, "operand"):  # ChangedSign, Inverted
            return self._contains_unknown(expr.operand)
        return False

    def _find_all_divisions(self, expr) -> list:
        """Find all Inverted expressions in the given expression."""
        divisions = []
        if isinstance(expr, Inverted):
            divisions.append(expr)
        elif isinstance(expr, (Addition, Multiplication)):
            for op in expr.operands:
                divisions.extend(self._find_all_divisions(op))
        elif hasattr(expr, "operand"):  # ChangedSign
            divisions.extend(self._find_all_divisions(expr.operand))
        return divisions
