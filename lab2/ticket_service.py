"""
Сервисный слой генератора билетов.
Объединяет парсинг Word, чтение списков студентов из Excel,
бизнес-логику назначения билетов (с проверкой повторов) и сохранение в журнал.
"""

import logging
import random
from typing import Callable, Dict, List, Optional, Tuple

from docx_parser import parse_tickets_from_docx
from excel_reader import get_group_names, get_students_for_group
from journal_manager import append_result_record, get_first_ticket_for_student
from models import Student, Ticket

logger = logging.getLogger(__name__)


class TicketService:
    def __init__(
        self,
        students_filepath: str = "students.xlsx",
        tickets_filepath: str = "tickets.docx",
        results_filepath: str = "results.xlsx",
    ):
        self.students_filepath = students_filepath
        self.tickets_filepath = tickets_filepath
        self.results_filepath = results_filepath
        self._tickets: Optional[Dict[int, Ticket]] = None

    def load_groups(self) -> List[str]:
        """Возвращает список доступных групп из students.xlsx."""
        return get_group_names(self.students_filepath)

    def load_students(self, group_name: str) -> List[Student]:
        """Возвращает список студентов указанной группы."""
        return get_students_for_group(self.students_filepath, group_name)

    def load_tickets(self, force_reload: bool = False) -> Dict[int, Ticket]:
        """
        Загружает билеты из tickets.docx. Кэширует результат.
        """
        if self._tickets is None or force_reload:
            self._tickets = parse_tickets_from_docx(self.tickets_filepath)
        return self._tickets

    def generate_or_get_ticket(
        self,
        student: Student,
        on_lock_retry: Optional[Callable[[], bool]] = None,
    ) -> Tuple[Ticket, bool]:
        """
        Назначает билет студенту:
        1. Если студент уже есть в results.xlsx -> берется номер билета из самой первой записи.
           Повтор = 'да'.
        2. Если студента нет -> выбирается случайный билет из доступных в tickets.docx.
           Повтор = 'нет'.
        3. Результат немедленно дописывается в results.xlsx.

        :param student: Объект Student (группа, фамилия, имя)
        :param on_lock_retry: Callback при блокировке results.xlsx
        :return: Кортеж (Ticket, is_repeat)
        """
        tickets_dict = self.load_tickets()
        if not tickets_dict:
            raise ValueError("В файле tickets.docx не найдено ни одного корректного билета.")

        # Проверяем историю в results.xlsx
        first_ticket_num = get_first_ticket_for_student(
            self.results_filepath,
            group=student.group,
            last_name=student.last_name,
            first_name=student.first_name,
        )

        if first_ticket_num is not None:
            # Идемпотентность: повторный выбор возвращает тот же билет
            ticket_number = first_ticket_num
            is_repeat = True
        else:
            # Новый студент: случайный выбор среди доступных билетов
            ticket_number = random.choice(list(tickets_dict.keys()))
            is_repeat = False

        # Получаем объект билета (если номер есть в файле билетов)
        if ticket_number in tickets_dict:
            ticket = tickets_dict[ticket_number]
        else:
            # Защитный случай: если номер из старого журнала не найден в текущем tickets.docx
            ticket = Ticket(
                number=ticket_number,
                questions=[
                    f"Вопрос 1 (Билет №{ticket_number})",
                    f"Вопрос 2 (Билет №{ticket_number})",
                    f"Вопрос 3 (Билет №{ticket_number})"
                ]
            )

        # Сохранение в results.xlsx сразу после генерации
        append_result_record(
            group=student.group,
            last_name=student.last_name,
            first_name=student.first_name,
            ticket_number=ticket_number,
            is_repeat=is_repeat,
            filepath=self.results_filepath,
            on_lock_retry=on_lock_retry,
        )

        return ticket, is_repeat
