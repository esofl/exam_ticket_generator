"""Генерация номера билета (SRP: только выбор номера)."""

import random


class RandomTicketGenerator:
    def __init__(self, max_ticket: int = 20, rng: random.Random | None = None) -> None:
        if max_ticket < 1:
            raise ValueError("max_ticket must be >= 1")
        self._max = max_ticket
        self._rng = rng or random.Random()

    def next_ticket(self) -> int:
        return self._rng.randint(1, self._max)
