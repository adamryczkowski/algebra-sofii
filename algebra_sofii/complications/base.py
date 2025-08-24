# Base complication class for generating complex algebraic equations.

from abc import ABC, abstractmethod
from typing import Optional

from ..expressions import Expression
from ..random_class import RandomClass


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
        random_stream: RandomClass,
        base_expression: Expression,
        complexity_budget: float,
        exclude_unknown: bool = False,
    ) -> Optional["Complication"]:
        """Create a random instance of this complication within the complexity budget."""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass
