"""
Точка входа — composition root: здесь собираются конкретные реализации.
Чтобы заменить консоль/Excel/генератор, меняется только этот файл (OCP).
"""

from console_input import ConsoleInput, ConsoleOutput, wait_until_unlocked
from exam_session import ExamSession
from excel_manager import ExcelJournal
from ticket_generator import RandomTicketGenerator


def main() -> None:
    journal = ExcelJournal(on_locked=wait_until_unlocked)
    journal.ensure_exists()
    ExamSession(ConsoleInput(), ConsoleOutput(), RandomTicketGenerator(20), journal).run()


if __name__ == "__main__":
    main()
