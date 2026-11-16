# Генератор экзаменационных билетов — Лабораторные работы №1 и №2

Репозиторий содержит две лабораторные работы по автоматизации выдачи экзаменационных билетов. Обе написаны на Python по принципам **SOLID**.

| Папка | Лабораторная | Что это | Интерфейс | Подробный гайд |
| :--- | :--- | :--- | :--- | :--- |
| [`lab1/`](lab1/) | №1 | Ввод фамилии и имени → случайный билет 1–20 → запись в `journal.xlsx` | Консоль (ESC — выход) | [lab1/README.md](lab1/README.md) |
| [`lab2/`](lab2/) | №2 | Студенты из `students.xlsx`, билеты из `tickets.docx`, журнал `results.xlsx`, повторный студент получает тот же билет | Веб-страница (Flask), http://127.0.0.1:5000 | [lab2/README.md](lab2/README.md) |

---

## Быстрый старт

```powershell
git clone https://github.com/esofl/exam_ticket_generator.git
cd exam_ticket_generator
python -m pip install -r requirements.txt

# Лабораторная №1 — консоль
cd lab1
python main.py

# Лабораторная №2 — веб (браузер откроется сам)
cd ..\lab2
python main.py
```

Требования: Windows 10/11, Python 3.10+. Для e2e-тестов ЛР2 дополнительно Node.js 18+.

---

## Тесты

```powershell
# ЛР1 — 9 unit-тестов
cd lab1
python -m unittest test_excel.py -v

# ЛР2 — 11 unit-тестов
cd ..\lab2
python -m pytest -v test_lab2.py

# ЛР2 — 8 e2e-тестов Playwright в браузере
npm install
npx playwright install chromium
npx playwright test
```

---

## Структура

```text
exam_ticket_generator/
├── lab1/                      # ЛР1: консоль
│   ├── main.py                # composition root
│   ├── protocols.py           # интерфейсы InputSource, Output, TicketGenerator, Journal
│   ├── exam_session.py        # сценарий: ввод → билет → запись
│   ├── ticket_generator.py    # случайный номер билета
│   ├── excel_manager.py       # журнал journal.xlsx
│   ├── console_input.py       # посимвольный ввод с ESC
│   └── test_excel.py
├── lab2/                      # ЛР2: веб
│   ├── main.py                # composition root, запуск Flask
│   ├── web_app.py             # HTTP API + страница
│   ├── templates/index.html   # интерфейс: списки, модальное окно, ESC
│   ├── ticket_service.py      # правило назначения билета
│   ├── repositories.py        # интерфейсы источников данных + реализации
│   ├── docx_parser.py, docx_io.py, excel_reader.py, journal_manager.py
│   ├── create_sample_data.py  # демо students.xlsx и tickets.docx
│   ├── test_lab2.py           # unit-тесты
│   └── e2e/                   # Playwright: тесты и тестовый сервер
└── requirements.txt
```

---

## SOLID в двух словах

В обеих работах бизнес-логика (`ExamSession` в ЛР1, `TicketService` в ЛР2) зависит только от интерфейсов (`typing.Protocol`). Конкретные реализации — консоль, Excel, Word, веб — подставляются в `main.py`. Поэтому логику можно тестировать на фейках без файлов и консоли, а замена хранилища или интерфейса не трогает бизнес-правила. Таблицы по каждому принципу — в README каждой лабораторной.
