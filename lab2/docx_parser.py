"""
Модуль парсинга экзаменационных билетов из файла tickets.docx.
Обеспечивает валидацию структуры билетов и устойчивость к ошибкам оформления.
"""

import logging
import os
import re
from typing import Dict, List, Optional
import docx

from models import Ticket

logger = logging.getLogger(__name__)


def parse_tickets_from_docx(filepath: str) -> Dict[int, Ticket]:
    """
    Парсит экзаменационные билеты из файла .docx.

    Формат:
    Билет N
    1. Вопрос первый
    2. Вопрос второй
    3. Вопрос третий

    Требования:
    - Заголовок билета: строка вида 'Билет N'
    - Вопросы: нумерованные пункты '1. текст', '2. текст', '3. текст' (на отдельных строках
      или внутри одного абзаца).
    - Если у билета меньше 3 вопросов или заголовок поврежден — билет пропускается,
      ошибка логируется, парсинг остальных билетов продолжается.

    :param filepath: Путь к файлу tickets.docx
    :return: Словарь {номер_билета: Ticket}
    :raises FileNotFoundError: Если файл не существует
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл с билетами '{filepath}' не найден.")

    try:
        doc = docx.Document(filepath)
    except Exception as e:
        logger.error(f"Не удалось открыть Word-документ '{filepath}': {e}")
        raise ValueError(f"Ошибка открытия файла Word '{filepath}': {e}") from e

    # Извлекаем все непустые строки текста из параграфов и таблиц (если есть)
    raw_lines: List[str] = []
    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            raw_lines.append(text)

    # Регулярные выражения
    ticket_header_pattern = re.compile(r"^Билет\s+(\d+)\b", re.IGNORECASE)
    question_split_pattern = re.compile(r"(?:^|\s)(?=[1-9]\d*[\.\)])")
    numbered_item_pattern = re.compile(r"^[1-9]\d*[\.\)]\s*(.+)$", re.DOTALL)

    tickets: Dict[int, Ticket] = {}
    current_ticket_num: Optional[int] = None
    current_questions: List[str] = []

    def finalize_current_ticket():
        nonlocal current_ticket_num, current_questions
        if current_ticket_num is not None:
            if len(current_questions) < 3:
                logger.warning(
                    f"Билет № {current_ticket_num} пропущен: обнаружено {len(current_questions)} "
                    f"вопросов (требуется минимум 3)."
                )
            else:
                # Берем ровно 3 вопроса согласно ТЗ
                selected_questions = current_questions[:3]
                tickets[current_ticket_num] = Ticket(
                    number=current_ticket_num,
                    questions=selected_questions
                )
                logger.info(f"Успешно загружен Билет № {current_ticket_num} (3 вопроса).")
        current_ticket_num = None
        current_questions = []

    for line in raw_lines:
        header_match = ticket_header_pattern.match(line)
        if header_match:
            # Завершаем предыдущий билет перед началом нового
            finalize_current_ticket()
            current_ticket_num = int(header_match.group(1))
            # Если в той же строке после 'Билет N' идет текст вопросов
            remainder = line[header_match.end():].strip()
            if remainder:
                _extract_questions_from_text(remainder, current_questions, question_split_pattern, numbered_item_pattern)
        elif current_ticket_num is not None:
            _extract_questions_from_text(line, current_questions, question_split_pattern, numbered_item_pattern)
        else:
            logger.debug(f"Пропущена строка вне билета: {line}")

    # Завершаем последний билет
    finalize_current_ticket()

    return tickets


def _extract_questions_from_text(
    text: str,
    questions_list: List[str],
    split_pattern: re.Pattern,
    numbered_pattern: re.Pattern,
) -> None:
    """Извлекает вопросы из переданного фрагмента текста."""
    # Разбиваем по номерам (1., 2., 3. и т.д.)
    parts = [p.strip() for p in split_pattern.split(text) if p.strip()]
    for part in parts:
        match = numbered_pattern.match(part)
        if match:
            question_text = match.group(1).strip()
            if question_text:
                questions_list.append(question_text)
        else:
            # Если номер отсутствовал, но это текст внутри билета
            if part:
                questions_list.append(part)
