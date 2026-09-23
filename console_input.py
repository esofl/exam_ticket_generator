"""
Модуль для консольного ввода с поддержкой перехвата клавиши ESC,
редактирования строки (Backspace), ввода символов Unicode (русские/латиница)
и валидации непустого значения.
"""

import sys

try:
    import msvcrt
except ImportError:
    msvcrt = None


def read_line_or_esc(prompt: str) -> str | None:
    """
    Считывает строку с консоли посимвольно.
    - При нажатии ESC возвращает None (сигнал к выходу).
    - При нажатии Enter возвращает введенную строку с обрезанными по краям пробелами.
    - Поддерживает клавишу Backspace для стирания символов.
    - Игнорирует управляющие/стрелочные последовательности.
    """
    if msvcrt is None:
        # Fallback для сред без msvcrt (например, Linux/CI)
        try:
            raw = input(prompt)
            return raw.strip()
        except (KeyboardInterrupt, EOFError):
            return None

    sys.stdout.write(prompt)
    sys.stdout.flush()

    buffer: list[str] = []

    while True:
        ch = msvcrt.getwch()

        # Нажата клавиша ESC (ASCII 27 / 0x1B)
        if ch == "\x1b":
            sys.stdout.write("\n")
            sys.stdout.flush()
            return None

        # Нажата клавиша Enter
        if ch in ("\r", "\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "".join(buffer).strip()

        # Нажата клавиша Backspace
        if ch == "\b":
            if buffer:
                buffer.pop()
                # Удаляем символ из консоли: возврат курсора, пробел, возврат курсора
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            continue

        # Префикс служебных клавиш (стрелки, F1-F12 и т.д.)
        if ch in ("\x00", "\xe0"):
            msvcrt.getwch()  # считываем второй байт кода клавиши и пропускаем его
            continue

        # Прерывание по Ctrl+C
        if ch == "\x03":
            raise KeyboardInterrupt

        # Печатаемые символы (включая русские буквы в Unicode)
        if ord(ch) >= 32:
            buffer.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()


def prompt_non_empty(prompt: str) -> str | None:
    """
    Запрашивает строку у пользователя до тех пор, пока не будет введено
    непустое значение (пустая строка или строка из одних пробелов не принимается).
    Если нажат ESC — немедленно возвращает None для завершения работы.
    """
    while True:
        value = read_line_or_esc(prompt)
        if value is None:
            return None
        value = value.strip()
        if value:
            return value
