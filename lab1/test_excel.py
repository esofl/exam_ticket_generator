"""Тесты ЛР1: журнал Excel, ввод, генератор и сценарий на фейках (возможно благодаря DIP)."""

import os
import random
import unittest
from datetime import datetime
from unittest.mock import patch

from openpyxl import load_workbook

from console_input import prompt_non_empty
from exam_session import ExamSession
from excel_manager import HEADERS, ExcelJournal
from ticket_generator import RandomTicketGenerator

TEST_FILE = "test_journal_tmp.xlsx"


class FakeInput:
    def __init__(self, answers):
        self._answers = list(answers)

    def ask(self, prompt):
        return self._answers.pop(0)


class FakeOutput:
    def __init__(self):
        self.lines = []

    def show(self, message):
        self.lines.append(message)


class FakeJournal:
    def __init__(self):
        self.rows = []

    def append(self, last_name, first_name, ticket, at):
        self.rows.append((last_name, first_name, ticket, at))


class FixedGenerator:
    def next_ticket(self):
        return 7


class TestExcelJournal(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def test_creates_header(self):
        ExcelJournal(TEST_FILE).ensure_exists()
        ws = load_workbook(TEST_FILE).active
        self.assertEqual(ws.max_row, 1)
        self.assertEqual([c.value for c in ws[1]], HEADERS)

    def test_append_preserves_previous_rows(self):
        j = ExcelJournal(TEST_FILE)
        j.append("Петров", "Петр", 5, datetime(2026, 9, 23, 10, 0, 0))
        j.append("Сидоров", "Алексей", 12, datetime(2026, 9, 23, 10, 5, 0))
        ws = load_workbook(TEST_FILE).active
        self.assertEqual(ws.max_row, 3)
        self.assertEqual([c.value for c in ws[2]], ["Петров", "Петр", 5, "2026-09-23 10:00:00"])
        self.assertEqual([c.value for c in ws[3]], ["Сидоров", "Алексей", 12, "2026-09-23 10:05:00"])

    def test_locked_file_calls_callback_and_retries(self):
        calls = []
        j = ExcelJournal(TEST_FILE, on_locked=calls.append)
        j.ensure_exists()
        real_load = load_workbook
        attempts = iter([True, False])

        def flaky(path):
            if next(attempts):
                raise PermissionError
            return real_load(path)

        with patch("excel_manager.load_workbook", side_effect=flaky):
            j.append("Иванов", "Иван", 1, datetime(2026, 1, 1))
        self.assertEqual(calls, [TEST_FILE])
        self.assertEqual(load_workbook(TEST_FILE).active.max_row, 2)


class TestTicketGenerator(unittest.TestCase):
    def test_range(self):
        g = RandomTicketGenerator(20, random.Random(1))
        self.assertTrue(all(1 <= g.next_ticket() <= 20 for _ in range(200)))

    def test_invalid_max(self):
        with self.assertRaises(ValueError):
            RandomTicketGenerator(0)


class TestPrompt(unittest.TestCase):
    @patch("console_input.read_line_or_esc", side_effect=["", "   ", "Иванов"])
    def test_retries_on_empty(self, mock_read):
        self.assertEqual(prompt_non_empty("Last name: "), "Иванов")
        self.assertEqual(mock_read.call_count, 3)

    @patch("console_input.read_line_or_esc", side_effect=[None])
    def test_none_on_esc(self, _):
        self.assertIsNone(prompt_non_empty("Last name: "))


class TestExamSession(unittest.TestCase):
    def test_two_students_then_esc(self):
        journal, out = FakeJournal(), FakeOutput()
        at = datetime(2026, 1, 1)
        ExamSession(FakeInput(["Иванов", "Иван", "Петров", "Пётр", None]),
                    out, FixedGenerator(), journal, clock=lambda: at).run()
        self.assertEqual(journal.rows, [("Иванов", "Иван", 7, at), ("Петров", "Пётр", 7, at)])
        self.assertIn("Билет № 7", out.lines)
        self.assertEqual(out.lines[-1], "Работа приложения завершена.")

    def test_esc_on_first_name_writes_nothing(self):
        journal = FakeJournal()
        ExamSession(FakeInput(["Иванов", None]), FakeOutput(), FixedGenerator(), journal).run()
        self.assertEqual(journal.rows, [])


if __name__ == "__main__":
    unittest.main()
