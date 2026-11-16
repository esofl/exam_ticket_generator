"""
Журнал journal.xlsx (SRP: только хранение).
Не общается с пользователем напрямую: при блокировке файла вызывает
переданный колбэк on_locked (DIP) — консоль/GUI сами решают, как ждать.
"""

import os
from datetime import datetime
from typing import Callable

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font

HEADERS = ["Last name", "First name", "Номер билета", "Дата и время"]
DEFAULT_FILENAME = "journal.xlsx"


class ExcelJournal:
    def __init__(self, filepath: str = DEFAULT_FILENAME, on_locked: Callable[[str], None] | None = None) -> None:
        self._path = filepath
        self._on_locked = on_locked or (lambda _path: None)

    def ensure_exists(self) -> None:
        """Создаёт файл с шапкой, если его нет. Существующий не трогает."""
        if os.path.exists(self._path):
            return
        wb = Workbook()
        ws = wb.active
        ws.title = "Журнал"
        ws.append(HEADERS)
        for col in range(1, len(HEADERS) + 1):
            ws.cell(row=1, column=col).font = Font(bold=True)
            ws.cell(row=1, column=col).alignment = Alignment(horizontal="center")
        for letter, width in {"A": 18, "B": 18, "C": 16, "D": 22}.items():
            ws.column_dimensions[letter].width = width
        self._save(wb)

    def append(self, last_name: str, first_name: str, ticket: int, at: datetime) -> None:
        """Дописывает строку в конец и сразу сохраняет; при блокировке ждёт и повторяет."""
        self.ensure_exists()
        while True:
            try:
                wb = load_workbook(self._path)
                break
            except PermissionError:
                self._on_locked(self._path)
        ws = wb.active
        ws.append([last_name, first_name, ticket, at.strftime("%Y-%m-%d %H:%M:%S")])
        for col in (3, 4):
            ws.cell(row=ws.max_row, column=col).alignment = Alignment(horizontal="center")
        self._save(wb)

    def _save(self, wb: Workbook) -> None:
        while True:
            try:
                wb.save(self._path)
                return
            except PermissionError:
                self._on_locked(self._path)
