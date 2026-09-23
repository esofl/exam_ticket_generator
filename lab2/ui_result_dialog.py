"""
Диалоговое окно отображения экзаменационного билета и 3 вопросов.
Закрывается по нажатию клавиши ESC, не завершая работу приложения.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from models import Student, Ticket


class ResultDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Tk,
        ticket: Ticket,
        student: Student,
        is_repeat: bool = False
    ):
        super().__init__(parent)
        self.parent = parent
        self.ticket = ticket
        self.student = student
        self.is_repeat = is_repeat

        self.title("Экзаменационный билет")
        self.geometry("560x520")
        self.minsize(450, 400)

        # Модальный режим
        self.transient(parent)
        self.grab_set()

        # Центрирование относительно родительского окна
        self._center_window()

        self._build_ui()

        # Привязка клавиши ESC: закрывает ТОЛЬКО окно результата
        self.bind("<Escape>", lambda event: self._close_dialog())
        self.protocol("WM_DELETE_WINDOW", self._close_dialog)

        # Фокус на диалоговом окне для немедленной работы ESC
        self.focus_set()

    def _center_window(self) -> None:
        self.update_idletasks()
        p_x = self.parent.winfo_x()
        p_y = self.parent.winfo_y()
        p_w = self.parent.winfo_width()
        p_h = self.parent.winfo_height()

        w = 560
        h = 520
        x = p_x + max(0, (p_w - w) // 2)
        y = p_y + max(0, (p_h - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Плашка повтора (если это повторная выдача)
        if self.is_repeat:
            repeat_label = tk.Label(
                main_frame,
                text="⚠️ Повторная выдача: билет взят из первой записи в журнале",
                font=("Segoe UI", 10, "bold"),
                bg="#fff3cd",
                fg="#856404",
                padx=10,
                pady=6,
                relief="groove"
            )
            repeat_label.pack(fill=tk.X, pady=(0, 10))

        # Студент и группа
        student_label = ttk.Label(
            main_frame,
            text=f"Студент: {self.student.full_name} | Группа: {self.student.group}",
            font=("Segoe UI", 11)
        )
        student_label.pack(anchor="w", pady=(0, 8))

        # Заголовок билета
        ticket_header = tk.Label(
            main_frame,
            text=f"Ваш билет № {self.ticket.number}",
            font=("Segoe UI", 18, "bold"),
            fg="#1a5fb4",
            pady=8
        )
        ticket_header.pack(fill=tk.X, pady=(0, 12))

        # Разделитель
        sep = ttk.Separator(main_frame, orient="horizontal")
        sep.pack(fill=tk.X, pady=(0, 12))

        # Блок с вопросами
        questions_frame = ttk.LabelFrame(main_frame, text=" Вопросы билета ", padding=12)
        questions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Вывод 3 вопросов
        for idx in range(3):
            q_num = idx + 1
            q_text = self.ticket.questions[idx] if idx < len(self.ticket.questions) else "—"

            q_box = ttk.Frame(questions_frame)
            q_box.pack(fill=tk.X, pady=6, anchor="w")

            num_lbl = ttk.Label(
                q_box,
                text=f"{q_num}.",
                font=("Segoe UI", 11, "bold"),
                foreground="#1c71d8"
            )
            num_lbl.pack(side=tk.LEFT, anchor="nw", padx=(0, 8))

            text_lbl = ttk.Label(
                q_box,
                text=q_text,
                font=("Segoe UI", 10),
                wraplength=450,
                justify=tk.LEFT
            )
            text_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor="w")

        # Кнопка закрытия
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

        tip_label = ttk.Label(
            btn_frame,
            text="Нажмите ESC для возврата к выбору",
            font=("Segoe UI", 9),
            foreground="#666666"
        )
        tip_label.pack(side=tk.LEFT, pady=4)

        close_btn = ttk.Button(
            btn_frame,
            text="Закрыть (ESC)",
            command=self._close_dialog
        )
        close_btn.pack(side=tk.RIGHT)

    def _close_dialog(self) -> None:
        """Закрывает только диалоговое окно и передает фокус родительскому окну."""
        self.grab_release()
        self.destroy()
        self.parent.focus_set()
