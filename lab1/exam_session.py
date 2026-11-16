"""
Сценарий работы с экзаменом (SRP: только порядок шагов).
Зависит от абстракций из protocols.py — реализации подставляются в main.py.
"""

from datetime import datetime
from typing import Callable

from protocols import InputSource, Journal, Output, TicketGenerator


class ExamSession:
    def __init__(
        self,
        reader: InputSource,
        output: Output,
        generator: TicketGenerator,
        journal: Journal,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._reader = reader
        self._output = output
        self._generator = generator
        self._journal = journal
        self._clock = clock

    def run(self) -> None:
        self._output.show("Для выхода нажмите ESC.")
        try:
            while self.serve_one_student():
                pass
        except KeyboardInterrupt:
            pass
        finally:
            self._output.show("Работа приложения завершена.")

    def serve_one_student(self) -> bool:
        """Обслуживает одного студента. False — пользователь нажал ESC."""
        last_name = self._reader.ask("Last name: ")
        if last_name is None:
            return False
        first_name = self._reader.ask("First name: ")
        if first_name is None:
            return False

        ticket = self._generator.next_ticket()
        self._output.show(f"Билет № {ticket}")
        # Сохраняем сразу после каждого студента, а не при выходе.
        self._journal.append(last_name, first_name, ticket, self._clock())
        return True
