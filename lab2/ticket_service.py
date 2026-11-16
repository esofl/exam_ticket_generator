"""
Бизнес-логика назначения билетов (SRP: только правило «первый билет / случайный»).
Источники данных приходят через конструктор (DIP), поэтому сервис
тестируется на фейках и не знает ни про Excel, ни про веб.
"""

import random
from datetime import datetime
from typing import Callable, List, Sequence, Tuple, TypeVar

from models import Student, Ticket
from repositories import (
    DocxTicketSource,
    ExcelResultJournal,
    ExcelStudentSource,
    ResultJournal,
    StudentSource,
    TicketSource,
)

T = TypeVar("T")


class NoTicketsError(ValueError):
    """В tickets.docx нет ни одного корректного билета."""


class TicketService:
    def __init__(
        self,
        students: StudentSource,
        tickets: TicketSource,
        journal: ResultJournal,
        choose: Callable[[Sequence[int]], int] = random.choice,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._students = students
        self._tickets = tickets
        self._journal = journal
        self._choose = choose
        self._clock = clock

    @classmethod
    def from_files(cls, students_path: str, tickets_path: str, results_path: str) -> "TicketService":
        return cls(ExcelStudentSource(students_path), DocxTicketSource(tickets_path), ExcelResultJournal(results_path))

    def load_groups(self) -> List[str]:
        return self._students.groups()

    def load_students(self, group: str) -> List[Student]:
        return self._students.students(group)

    def generate_or_get_ticket(self, student: Student) -> Tuple[Ticket, bool]:
        """
        Повторный студент -> номер из его самой первой записи, Повтор = да.
        Новый -> случайный билет 1..N, Повтор = нет.
        Запись в журнал — сразу, до возврата результата.
        """
        tickets = self._tickets.tickets()
        if not tickets:
            raise NoTicketsError("В файле tickets.docx не найдено ни одного корректного билета.")

        first = self._journal.first_ticket(student)
        is_repeat = first is not None
        number = first if is_repeat else self._choose(sorted(tickets))

        # Номер из старого журнала мог исчезнуть из текущего tickets.docx — не падаем.
        ticket = tickets.get(number) or Ticket(number, [f"Вопрос {i} (билет № {number} отсутствует в tickets.docx)" for i in (1, 2, 3)])

        self._journal.append(student, number, is_repeat, self._clock())
        return ticket, is_repeat
