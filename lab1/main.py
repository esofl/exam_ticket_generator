"""
Главный модуль консольного приложения:
Генератор экзаменационных билетов.
"""

import random
import sys
from console_input import prompt_non_empty
from excel_manager import append_record, init_journal_if_needed


def main() -> None:
    # Инициализация Excel файла с шапкой при первом запуске
    init_journal_if_needed()

    print("Для выхода нажмите ESC.")

    try:
        while True:
            # Шаг 2: Запрос Last name
            last_name = prompt_non_empty("Last name: ")
            if last_name is None:
                break

            # Шаг 3: Запрос First name
            first_name = prompt_non_empty("First name: ")
            if first_name is None:
                break

            # Шаг 4: Генерация номера билета от 1 до 20
            ticket_number = random.randint(1, 20)

            # Шаг 5: Вывод номера в консоль
            print(f"Билет № {ticket_number}")

            # Шаг 6: Запись в Excel-файл (сохранение сразу после каждого студента)
            append_record(last_name, first_name, ticket_number)

    except KeyboardInterrupt:
        pass
    finally:
        print("Работа приложения завершена.")


if __name__ == "__main__":
    main()
