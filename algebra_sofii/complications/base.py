"""
Base complication class for generating complex algebraic equations.
"""

import random
from abc import ABC, abstractmethod
from typing import Optional

from ..expressions import Expression


class Complication(ABC):
    """Base class for all complications."""

    @abstractmethod
    def apply(self, expr: Expression) -> Expression:
        """Apply the complication to an expression."""
        pass

    @property
    @abstractmethod
    def minimal_complexity(self) -> float:
        """Return the minimal complexity this complication will add."""
        pass

    @property
    @abstractmethod
    def maximal_complexity(self) -> float:
        """Return the maximal complexity this complication can add."""
        pass

    @staticmethod
    @abstractmethod
    def randomize_from_stream(
        random_stream: random.Random,
        base_expression: Expression,
        complexity_budget: float,
    ) -> Optional["Complication"]:
        """Create a random instance of this complication within the complexity budget."""
        pass
