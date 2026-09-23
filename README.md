# Генератор экзаменационных билетов (Exam Ticket Generator)

Репозиторий содержит решения двух лабораторных работ по автоматизации распределения экзаменационных билетов:

---

## 📁 Структура репозитория

```
exam_ticket_generator/
├── lab1/                   # Лабораторная работа №1 (Консольное приложение)
│   ├── console_input.py    # Посимвольный ввод, перехват ESC, Unicode, валидация
│   ├── excel_manager.py    # Работа с journal.xlsx, обработка блокировок файла
│   ├── main.py             # Главный цикл консольного приложения
│   ├── test_excel.py       # Автоматические тесты функционала ЛР1
│   ├── requirements.txt    # Зависимости (openpyxl)
│   └── README.md           # Документация по ЛР1
│
├── lab2/                   # Лабораторная работа №2 (Десктопное UI-приложение)
│   ├── main.py             # Точка входа GUI-приложения
│   ├── ui_main_window.py   # Главное окно (зависимые Combobox, валидация)
│   ├── ui_result_dialog.py # Окно билета и 3 вопросов, закрытие по ESC
│   ├── docx_parser.py      # Отказоустойчивый парсинг tickets.docx
│   ├── excel_reader.py     # Чтение групп и студентов из students.xlsx
│   ├── journal_manager.py  # Журнал results.xlsx с защитой от блокировки
│   ├── ticket_service.py   # Бизнес-логика повторов (идемпотентность)
│   ├── models.py           # Датаклассы Student, Ticket, JournalRecord
│   ├── create_sample_data.py # Генерация тестовых students.xlsx и tickets.docx
│   ├── test_lab2.py        # Комплексные unit-тесты ЛР2
│   ├── requirements.txt    # Зависимости (openpyxl, python-docx)
│   └── README.md           # Документация по ЛР2
│
├── requirements.txt        # Общие зависимости проекта
└── README.md               # Общее описание репозитория
```

---

## 🚀 Быстрый запуск

### Лабораторная работа №1 (Консоль)
```bash
cd lab1
pip install -r requirements.txt
python main.py
```

### Лабораторная работа №2 (Графический интерфейс)
```bash
cd lab2
pip install -r requirements.txt
python main.py
```

---

## 🧪 Запуск тестов

### Тесты ЛР1:
```bash
cd lab1
python -m unittest test_excel.py -v
```

### Тесты ЛР2:
```bash
cd lab2
python -m unittest test_lab2.py -v
```
