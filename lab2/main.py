"""
Точка входа ЛР2 (composition root): собирает сервис из файлов и запускает веб-интерфейс.
Открывает браузер на http://127.0.0.1:5000.
"""

import logging
import threading
import webbrowser

from ticket_service import TicketService
from web_app import create_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

HOST, PORT = "127.0.0.1", 5000


def main() -> None:
    service = TicketService.from_files("students.xlsx", "tickets.docx", "results.xlsx")
    threading.Timer(1.0, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()
    create_app(service).run(host=HOST, port=PORT)


if __name__ == "__main__":
    main()
