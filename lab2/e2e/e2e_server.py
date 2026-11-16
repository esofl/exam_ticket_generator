"""
Сервер для Playwright e2e: поднимает приложение на временных файлах.
  python e2e/e2e_server.py <port>            — обычные демо-данные
  python e2e/e2e_server.py <port> --missing  — без students.xlsx (проверка валидации источников)

Журнал оборачивается LockableJournal (декоратор, OCP: поведение расширено без правки
ExcelResultJournal), а тест может «заблокировать» results.xlsx через /__e2e__/lock.
"""

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import jsonify  # noqa: E402

from create_sample_data import create_sample_students_xlsx, create_sample_tickets_docx  # noqa: E402
from repositories import DocxTicketSource, ExcelResultJournal, ExcelStudentSource  # noqa: E402
from ticket_service import TicketService  # noqa: E402
from web_app import create_app  # noqa: E402


class LockableJournal:
    def __init__(self, inner):
        self._inner = inner
        self.locked = False

    def first_ticket(self, student):
        return self._inner.first_ticket(student)

    def append(self, student, ticket_number, is_repeat, at):
        if self.locked:
            raise PermissionError("results.xlsx locked (e2e)")
        self._inner.append(student, ticket_number, is_repeat, at)


def build(port: int, missing: bool):
    tmp = tempfile.mkdtemp(prefix=f"lab2_e2e_{port}_")
    students, tickets, results = (os.path.join(tmp, n) for n in ("students.xlsx", "tickets.docx", "results.xlsx"))
    if not missing:
        create_sample_students_xlsx(students)
    create_sample_tickets_docx(tickets)
    journal = LockableJournal(ExcelResultJournal(results))
    app = create_app(TicketService(ExcelStudentSource(students), DocxTicketSource(tickets), journal))

    @app.post("/__e2e__/reset")
    def reset():
        journal.locked = False
        if os.path.exists(results):
            os.remove(results)
        return jsonify(ok=True)

    @app.post("/__e2e__/lock/<int:on>")
    def lock(on):
        journal.locked = bool(on)
        return jsonify(ok=True)

    @app.get("/__e2e__/journal")
    def rows():
        from journal_manager import get_all_records
        return jsonify([[r.group, r.last_name, r.first_name, r.ticket_number, r.timestamp_str, r.is_repeat]
                        for r in get_all_records(results)])

    return app, tmp


if __name__ == "__main__":
    port = int(sys.argv[1])
    app, tmp = build(port, "--missing" in sys.argv)
    try:
        app.run(host="127.0.0.1", port=port)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
