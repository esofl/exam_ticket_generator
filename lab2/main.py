"""
Главная точка входа приложения Лабораторной работы №2:
Десктопное приложение с графическим интерфейсом для генератора билетов.
"""

import logging
import sys
from ui_main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def main() -> None:
    app = MainWindow(
        students_filepath="students.xlsx",
        tickets_filepath="tickets.docx",
        results_filepath="results.xlsx"
    )
    app.mainloop()


if __name__ == "__main__":
    main()
