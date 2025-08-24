"""Test fixtures for algebra_sofii tests."""

import pytest
from algebra_sofii.expressions import Integer, Unknown, Addition, Multiplication, Equals
from algebra_sofii.random_class import RandomClass


@pytest.fixture
def sample_integer():
    """Sample integer expression for testing."""
    return Integer(5)


@pytest.fixture
def sample_unknown():
    """Sample unknown expression for testing."""
    return Unknown()


@pytest.fixture
def sample_addition():
    """Sample addition expression for testing."""
    return Addition([Integer(3), Unknown()])


@pytest.fixture
def sample_multiplication():
    """Sample multiplication expression for testing."""
    return Multiplication([Integer(2), Unknown()])


@pytest.fixture
def sample_equation():
    """Sample equation for testing."""
    return Equals(Unknown(), Integer(5))


@pytest.fixture
def complex_expression():
    """Complex nested expression for testing."""
    return Addition([Multiplication([Integer(2), Unknown()]), Integer(3)])


@pytest.fixture
def solution_values():
    """Solution values for testing."""
    return 5


@pytest.fixture
def random_stream():
    """Random stream for testing."""
    return RandomClass()
