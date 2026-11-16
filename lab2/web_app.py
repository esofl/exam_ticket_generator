"""
Веб-слой (SRP: только HTTP <-> сервис). Сервис внедряется в create_app (DIP),
поэтому e2e-тесты подставляют свои файлы или фейковый журнал.
"""

import logging

from flask import Flask, jsonify, render_template, request

from models import Student
from ticket_service import NoTicketsError, TicketService

logger = logging.getLogger(__name__)


def create_app(service: TicketService) -> Flask:
    app = Flask(__name__)

    @app.errorhandler(FileNotFoundError)
    def missing_source(e):
        return jsonify(error=f"{e} Положите файл рядом с приложением и обновите страницу."), 503

    @app.errorhandler(NoTicketsError)
    def no_tickets(e):
        return jsonify(error=str(e)), 422

    @app.errorhandler(PermissionError)
    def locked(e):
        logger.warning("results.xlsx заблокирован: %s", e)
        return jsonify(error="Файл results.xlsx открыт в другой программе (например, Excel). "
                             "Закройте его и нажмите «Повторить».", retry=True), 423

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/groups")
    def groups():
        return jsonify(service.load_groups())

    @app.get("/api/students")
    def students():
        group = request.args.get("group", "")
        return jsonify([{"last_name": s.last_name, "first_name": s.first_name, "full_name": s.full_name}
                        for s in service.load_students(group)])

    @app.post("/api/tickets")
    def generate():
        data = request.get_json(silent=True) or {}
        group, last, first = (str(data.get(k, "")).strip() for k in ("group", "last_name", "first_name"))
        if not (group and last and first):
            return jsonify(error="Выберите группу и студента."), 400
        # Доверяем только студентам из students.xlsx, а не произвольному JSON.
        if not any(s.last_name == last and s.first_name == first for s in service.load_students(group)):
            return jsonify(error="Студент не найден в выбранной группе."), 400
        ticket, is_repeat = service.generate_or_get_ticket(Student(group, last, first))
        return jsonify(number=ticket.number, questions=ticket.questions, is_repeat=is_repeat)

    return app
