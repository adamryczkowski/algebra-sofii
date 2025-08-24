# EquationWithSolution class for generating complex algebraic equations.
from __future__ import annotations

from .base import Complication
from .config import EQUATION_COMPLICATION_WEIGHTS, COMPLICATION_CLASSES
from ..expressions import Expression, Equals
from ..random_class import RandomClass


class EquationWithSolution:
    """Container for an equation with its solution and applied complications."""

    _solution: int
    _solution_swapped: bool
    _complications: list[Complication]
    _cached_current_form: Expression

    @staticmethod
    def MakeEquation(solution: int, swap: bool = False) -> EquationWithSolution:
        """Factory method to create an EquationWithSolution instance."""
        return EquationWithSolution(solution, swap, [])

    def __init__(self, solution: int, swap: bool, complications: list[Complication]):
        self._solution = solution
        self._solution_swapped = swap
        self._complications = complications
        self._cached_current_form = self._initial_equation

    @property
    def _initial_equation(self) -> Expression:
        """The initial equation before complications."""
        return Equals.from_solution(self._solution, self._solution_swapped)

    @property
    def solution(self) -> int:
        """The solution value for the equation."""
        return self._solution

    @property
    def complications(self) -> list[Complication]:
        """The list of complications applied to the equation."""
        return self._complications.copy()

    @property
    def cached_current_form(self) -> Expression:
        """The cached current form of the equation."""
        return self._cached_current_form

    def _update_cache(self):
        """Update the cached current form."""
        current = self._initial_equation
        for complication in self._complications:
            current = complication.apply(current)
        self._cached_current_form = current

    def add_random_complication(
        self, max_complexity: float, random_stream: RandomClass
    ) -> None:
        """Add a random complication within complexity limits."""
        current_complexity = self._cached_current_form.complexity()
        remaining_complexity = max_complexity - current_complexity

        # Determine which complications are applicable
        applicable_complications = []
        weights = []

        # Use equation weights since we're working with equations
        for comp_name, weight in EQUATION_COMPLICATION_WEIGHTS.items():
            comp_class = COMPLICATION_CLASSES[comp_name]

            # Try to create a sample complication to check minimal complexity
            # Use exclude_unknown=True to ensure equation remains linear
            sample_complication = comp_class.randomize_from_stream(
                random_stream=random_stream,
                base_expression=self._cached_current_form,
                complexity_budget=remaining_complexity,
                exclude_unknown=True,
            )

            if sample_complication is not None:
                applicable_complications.append(comp_name)
                weights.append(weight)

        if not applicable_complications:
            raise ValueError("Insufficient complexity budget for any complication")

        # Select a random complication based on weights
        selected_name = random_stream.choices(
            applicable_complications, weights=weights
        )[0]
        selected_class = COMPLICATION_CLASSES[selected_name]

        # Create the actual complication with exclude_unknown=True to maintain linearity
        complication = selected_class.randomize_from_stream(
            random_stream,
            self._cached_current_form,
            remaining_complexity,
            exclude_unknown=True,
        )

        if complication is None:
            raise ValueError(f"Failed to create {selected_name} within budget")

        # Apply the complication
        self.apply_complication(complication)

    def randomize(self, random_stream: RandomClass, max_complexity: float) -> None:
        """Randomize the equation up to the target complexity."""
        while True:
            current_complexity = self.get_total_complexity()

            if current_complexity >= max_complexity:
                break

            try:
                self.add_random_complication(max_complexity, random_stream)
            except ValueError:
                # No more complications can be added within budget
                break

    def apply_complication(self, complication: Complication):
        """Apply a complication and update the cached form."""
        self._complications.append(complication)
        self._update_cache()
        self.verify_solution()

    def get_current_equation(self) -> Expression:
        """Get the current form of the equation."""
        if self._cached_current_form is None:
            raise ValueError("No cached current form available")
        return self._cached_current_form

    def get_total_complexity(self) -> float:
        """Get the total complexity of the current equation."""
        if self._cached_current_form is None:
            raise ValueError("No cached current form available")
        return self._cached_current_form.complexity()

    def verify_solution(self) -> bool:
        """Verify that the equation still solves to the original solution."""
        if self._cached_current_form is None:
            return False
        try:
            # For equations, both sides should be equal
            if isinstance(self._cached_current_form, Equals):
                left_val = self._cached_current_form.left.evaluate(self._solution)
                right_val = self._cached_current_form.right.evaluate(self._solution)
                return abs(left_val - right_val) < 1e-10
            return True
        except (ZeroDivisionError, ValueError):
            return False

    def __repr__(self):
        return repr(self._cached_current_form)
