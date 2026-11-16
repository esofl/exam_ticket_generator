"""
Абстракции источников данных (ISP/DIP) и их реализации поверх Excel/Word.
TicketService и веб-слой зависят только от Protocol-ов, а не от openpyxl/python-docx.
"""

from datetime import datetime
from typing import Dict, List, Optional, Protocol

from docx_parser import parse_tickets_from_docx
from excel_reader import get_group_names, get_students_for_group
from journal_manager import append_result_record, get_first_ticket_for_student
from models import Student, Ticket


class StudentSource(Protocol):
    def groups(self) -> List[str]: ...
    def students(self, group: str) -> List[Student]: ...


class TicketSource(Protocol):
    def tickets(self) -> Dict[int, Ticket]: ...


class ResultJournal(Protocol):
    def first_ticket(self, student: Student) -> Optional[int]: ...
    def append(self, student: Student, ticket_number: int, is_repeat: bool, at: datetime) -> None: ...


class ExcelStudentSource:
    def __init__(self, path: str) -> None:
        self._path = path

    def groups(self) -> List[str]:
        return get_group_names(self._path)

    def students(self, group: str) -> List[Student]:
        return get_students_for_group(self._path, group)


class DocxTicketSource:
    """Билеты перечитываются при каждом вызове: правка tickets.docx подхватывается без перезапуска."""

    def __init__(self, path: str) -> None:
        self._path = path

    def tickets(self) -> Dict[int, Ticket]:
        return parse_tickets_from_docx(self._path)


class ExcelResultJournal:
    """Журнал results.xlsx. При блокировке файла пробрасывает PermissionError — повтор решает UI."""

    def __init__(self, path: str) -> None:
        self._path = path

    def first_ticket(self, student: Student) -> Optional[int]:
        return get_first_ticket_for_student(self._path, student.group, student.last_name, student.first_name)

    def append(self, student: Student, ticket_number: int, is_repeat: bool, at: datetime) -> None:
        append_result_record(
            group=student.group,
            last_name=student.last_name,
            first_name=student.first_name,
            ticket_number=ticket_number,
            is_repeat=is_repeat,
            timestamp=at,
            filepath=self._path,
        )
