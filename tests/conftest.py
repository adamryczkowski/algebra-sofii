"""
Test configuration and shared fixtures for algebra-sofii tests.
"""

import random

import pytest

from algebra_sofii.expressions import (
    Addition,
    ChangedSign,
    Equals,
    Integer,
    Multiplication,
    Unknown,
)


@pytest.fixture
def random_stream():
    """Provide a seeded random stream for reproducible tests."""
    return random.Random(42)


@pytest.fixture
def sample_integer():
    """Sample integer expression."""
    return Integer(5)


@pytest.fixture
def sample_unknown():
    """Sample unknown expression."""
    return Unknown()


@pytest.fixture
def sample_addition():
    """Sample addition expression: 3 + x."""
    return Addition([Integer(3), Unknown()])


@pytest.fixture
def sample_multiplication():
    """Sample multiplication expression: 2 * x."""
    return Multiplication([Integer(2), Unknown()])


@pytest.fixture
def sample_equation():
    """Sample equation: x = 5."""
    return Equals(Unknown(), Integer(5))


@pytest.fixture
def complex_expression():
    """Complex expression: (2 * x) + (-3)."""
    return Addition([Multiplication([Integer(2), Unknown()]), ChangedSign(Integer(3))])


@pytest.fixture(params=[1, 2, 3, 4, 5, 6, 7, 8, 9])
def solution_values(request):
    """Parametrized fixture for solution values 1-9."""
    return request.param
