from __future__ import annotations
import random


class RandomClass:
    _state: tuple[int, ...]

    @staticmethod
    def FromFixedSeed(seed: int) -> RandomClass:
        old_state = random.getstate()
        random.seed(seed)
        ans = RandomClass(random.getstate())
        random.setstate(old_state)
        return ans

    def __init__(self, state: tuple[int, ...] | None = None) -> None:
        if state is None:
            self._state = random.getstate()
        else:
            self._state = state

    def choices(
        self, population: list, weights: list | None = None, k: int = 1
    ) -> list:
        random.setstate(self._state)
        ans = random.choices(population, weights=weights, k=k)
        self._state = random.getstate()
        return ans

    def choice(self, population: list):
        random.setstate(self._state)
        ans = random.choice(population)
        self._state = random.getstate()
        return ans

    def randint(self, a: int, b: int) -> int:
        random.setstate(self._state)
        ans = random.randint(a, b)
        self._state = random.getstate()
        return ans

    # def rand_01(self) -> float:
    #     random.setstate(self._state)
    #     ans = random.random()
    #     self._state = random.getstate()
    #     return ans

    def rand_coinflip(self, bias: float = 0.5) -> bool:
        random.setstate(self._state)
        ans = random.random() < bias
        self._state = random.getstate()
        return ans
