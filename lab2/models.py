"""
Модели данных для приложения генератора экзаменационных билетов.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Student:
    """Представление данных студента."""
    group: str
    last_name: str
    first_name: str

    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name}"

    def __str__(self) -> str:
        return self.full_name


@dataclass
class Ticket:
    """Представление экзаменационного билета с вопросами."""
    number: int
    questions: List[str]


@dataclass
class JournalRecord:
    """Запись в журнале results.xlsx."""
    group: str
    last_name: str
    first_name: str
    ticket_number: int
    timestamp_str: str
    is_repeat: bool  # True -> "да", False -> "нет"
