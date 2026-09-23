"""
Главное окно графического интерфейса приложения генерации экзаменационных билетов.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional

from models import Student
from ticket_service import TicketService
from ui_result_dialog import ResultDialog


class MainWindow(tk.Tk):
    def __init__(
        self,
        students_filepath: str = "students.xlsx",
        tickets_filepath: str = "tickets.docx",
        results_filepath: str = "results.xlsx",
    ):
        super().__init__()
        self.students_filepath = students_filepath
        self.tickets_filepath = tickets_filepath
        self.results_filepath = results_filepath

        self.service = TicketService(
            students_filepath=students_filepath,
            tickets_filepath=tickets_filepath,
            results_filepath=results_filepath,
        )

        self.current_students: Dict[str, Student] = {}  # "Фамилия Имя" -> Student

        self.title("Генератор экзаменационных билетов")
        self.geometry("540x380")
        self.minsize(480, 320)

        self._init_styles()
        self._build_ui()
        self._load_initial_data()

    def _init_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground="#2c3e50")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#555555")
        style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=8)

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttk.Label(
            container,
            text="Генератор экзаменационных билетов",
            style="Title.TLabel"
        )
        title_label.pack(anchor="w", pady=(0, 4))

        subtitle_label = ttk.Label(
            container,
            text="Выберите группу и студента для назначения билета",
            style="Sub.TLabel"
        )
        subtitle_label.pack(anchor="w", pady=(0, 20))

        # Форма выбора
        form_frame = ttk.LabelFrame(container, text=" Выбор студента ", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 15))

        # 1. Поле выбора группы
        group_lbl = ttk.Label(form_frame, text="Группа:", font=("Segoe UI", 10, "bold"))
        group_lbl.grid(row=0, column=0, sticky="w", pady=6, padx=(0, 10))

        self.group_combo = ttk.Combobox(form_frame, state="readonly", font=("Segoe UI", 10), width=35)
        self.group_combo.grid(row=0, column=1, sticky="ew", pady=6)
        self.group_combo.bind("<<ComboboxSelected>>", self._on_group_selected)

        # 2. Поле выбора студента
        student_lbl = ttk.Label(form_frame, text="Студент:", font=("Segoe UI", 10, "bold"))
        student_lbl.grid(row=1, column=0, sticky="w", pady=6, padx=(0, 10))

        self.student_combo = ttk.Combobox(form_frame, state="disabled", font=("Segoe UI", 10), width=35)
        self.student_combo.grid(row=1, column=1, sticky="ew", pady=6)
        self.student_combo.bind("<<ComboboxSelected>>", self._on_student_selected)

        form_frame.columnconfigure(1, weight=1)

        # 3. Кнопка «Сгенерировать билет» (неактивна до выбора группы и студента)
        self.generate_btn = ttk.Button(
            container,
            text="Сгенерировать билет",
            style="Action.TButton",
            state="disabled",
            command=self._on_generate_clicked
        )
        self.generate_btn.pack(fill=tk.X, pady=(5, 15))

        # Статусная строка
        self.status_var = tk.StringVar(value="Готово к работе.")
        self.status_bar = ttk.Label(
            container,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            foreground="#666666",
            relief="sunken",
            padding=5
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _load_initial_data(self) -> None:
        """Проверяет наличие входных файлов и загружает список групп."""
        missing_files = []
        if not os.path.exists(self.students_filepath):
            missing_files.append(f"Файл со студентами: {self.students_filepath}")
        if not os.path.exists(self.tickets_filepath):
            missing_files.append(f"Файл с билетами: {self.tickets_filepath}")

        if missing_files:
            msg = "Отсутствуют обязательные файлы для работы приложения:\n\n" + "\n".join(missing_files)
            msg += "\n\nПожалуйста, разместите файлы в рабочей папке и перезапустите приложение."
            self.status_var.set("Ошибка: не найдены входные файлы.")
            messagebox.showerror("Ошибка входных данных", msg, parent=self)
            return

        try:
            groups = self.service.load_groups()
            if not groups:
                self.status_var.set("Предупреждение: в students.xlsx нет листов с группами.")
                messagebox.showwarning(
                    "Пустой файл",
                    "Файл students.xlsx не содержит листов с группами.",
                    parent=self
                )
                return

            self.group_combo["values"] = groups
            self.status_var.set(f"Загружено групп: {len(groups)}. Выберите группу.")
        except Exception as e:
            self.status_var.set(f"Ошибка загрузки групп: {e}")
            messagebox.showerror("Ошибка чтения", f"Не удалось прочитать groups из students.xlsx:\n{e}", parent=self)

    def _on_group_selected(self, event=None) -> None:
        """Обработчик выбора группы из выпадающего списка."""
        group_name = self.group_combo.get().strip()
        if not group_name:
            return

        # Сброс выбора студента и блокировка кнопки
        self.student_combo.set("")
        self.student_combo["values"] = []
        self.generate_btn.config(state="disabled")
        self.current_students.clear()

        try:
            students = self.service.load_students(group_name)
            if not students:
                # Пустая группа: второй список пуст, кнопка неактивна, без исключения
                self.student_combo.config(state="disabled")
                self.status_var.set(f"В группе '{group_name}' нет студентов.")
                return

            # Формируем отображение «Фамилия Имя»
            student_display_names = []
            for s in students:
                name_key = s.full_name
                # Защита от дублей имен внутри группы
                if name_key in self.current_students:
                    name_key = f"{s.full_name} ({s.group})"
                self.current_students[name_key] = s
                student_display_names.append(name_key)

            self.student_combo["values"] = student_display_names
            self.student_combo.config(state="readonly")
            self.status_var.set(f"Группа '{group_name}': загружено студентов: {len(students)}.")
        except Exception as e:
            self.status_var.set(f"Ошибка чтения студентов: {e}")
            messagebox.showerror("Ошибка чтения", f"Не удалось прочитать список студентов:\n{e}", parent=self)

    def _on_student_selected(self, event=None) -> None:
        """Обработчик выбора студента."""
        selected_name = self.student_combo.get().strip()
        if selected_name and selected_name in self.current_students:
            # Кнопка становится активной только при наличии обоих выборов
            self.generate_btn.config(state="normal")
            self.status_var.set(f"Выбран: {selected_name}. Нажмите «Сгенерировать билет».")
        else:
            self.generate_btn.config(state="disabled")

    def _handle_file_lock_retry(self) -> bool:
        """
        Диалог при блокировке файла results.xlsx другим приложением (Excel).
        Возвращает True для повтора, False для отмены.
        """
        return messagebox.askretrycancel(
            "Файл заблокирован",
            f"Файл '{self.results_filepath}' открыт в Microsoft Excel или другой программе.\n\n"
            "Пожалуйста, закройте файл в Excel и нажмите «Повторить».",
            parent=self
        )

    def _on_generate_clicked(self) -> None:
        """Генерация или получение билета с немедленным сохранением в results.xlsx."""
        selected_name = self.student_combo.get().strip()
        student = self.current_students.get(selected_name)
        if not student:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите студента из списка.", parent=self)
            return

        try:
            ticket, is_repeat = self.service.generate_or_get_ticket(
                student=student,
                on_lock_retry=self._handle_file_lock_retry
            )

            # Открываем окно результата
            ResultDialog(
                parent=self,
                ticket=ticket,
                student=student,
                is_repeat=is_repeat
            )

            status_text = (
                f"Билет №{ticket.number} назначен: {student.full_name} "
                f"({'повторно' if is_repeat else 'новый'}). Записано в {self.results_filepath}."
            )
            self.status_var.set(status_text)

        except PermissionError:
            self.status_var.set("Операция сохранения отменена из-за блокировки файла.")
            messagebox.showwarning(
                "Сохранение отменено",
                f"Запись в файл '{self.results_filepath}' не была выполнена, так как файл заблокирован.",
                parent=self
            )
        except Exception as e:
            self.status_var.set(f"Ошибка генерации: {e}")
            messagebox.showerror(
                "Ошибка",
                f"Не удалось сгенерировать билет:\n{e}",
                parent=self
            )
