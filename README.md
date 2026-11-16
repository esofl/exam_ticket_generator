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
├── lab2/                   # Лабораторная работа №2 (Веб-интерфейс, Flask)
│   ├── main.py             # Точка входа GUI-приложения
│   ├── web_app.py          # Flask: HTTP API + страница (create_app(service))
│   ├── templates/index.html# Веб-интерфейс: зависимые списки, модальное окно, ESC
│   ├── repositories.py     # Интерфейсы источников данных + Excel/Word-реализации
│   ├── docx_io.py          # Чтение/запись .docx на стандартной библиотеке
│   ├── e2e/                # Playwright e2e-тесты и тестовый сервер
│   ├── docx_parser.py      # Отказоустойчивый парсинг tickets.docx
│   ├── excel_reader.py     # Чтение групп и студентов из students.xlsx
│   ├── journal_manager.py  # Журнал results.xlsx с защитой от блокировки
│   ├── ticket_service.py   # Бизнес-логика повторов (идемпотентность)
│   ├── models.py           # Датаклассы Student, Ticket, JournalRecord
│   ├── create_sample_data.py # Генерация тестовых students.xlsx и tickets.docx
│   ├── test_lab2.py        # Комплексные unit-тесты ЛР2
│   ├── requirements.txt    # Зависимости (openpyxl, flask, pytest)
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

### Лабораторная работа №2 (Веб-интерфейс, http://127.0.0.1:5000)
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
python -m pytest -v test_lab2.py      # unit
npm install && npx playwright install chromium
npx playwright test                    # e2e в браузере (Playwright)
```

---

## 🧱 SOLID

Обе работы построены на принципах SOLID: бизнес-логика (`ExamSession` в ЛР1, `TicketService` в ЛР2) зависит только от интерфейсов (`typing.Protocol`), а конкретные реализации (консоль, Excel, Word, веб) собираются в `main.py`. Подробные таблицы — в `lab1/README.md` и `lab2/README.md`.
