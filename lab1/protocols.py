"""
Абстракции (DIP/ISP): сценарий приложения зависит от этих интерфейсов,
а не от конкретных реализаций консоли, генератора или Excel.
"""

from datetime import datetime
from typing import Protocol


class InputSource(Protocol):
    def ask(self, prompt: str) -> str | None:
        """Непустая строка или None, если пользователь нажал ESC."""


class Output(Protocol):
    def show(self, message: str) -> None: ...


class TicketGenerator(Protocol):
    def next_ticket(self) -> int: ...


class Journal(Protocol):
    def append(self, last_name: str, first_name: str, ticket: int, at: datetime) -> None: ...
