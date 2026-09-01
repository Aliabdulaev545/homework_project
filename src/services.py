# src/services.py

import re
import json
import pandas as pd
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simple_search(search_query: str, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Простой поиск транзакций по подстроке.

    Args:
        search_query: строка для поиска
        transactions: список транзакций

    Returns:
        Список транзакций, содержащих запрос в описании или категории
    """
    if not search_query or not search_query.strip():
        return transactions

    search_query = search_query.lower().strip()

    results = []
    for trans in transactions:
        # Проверяем категорию
        category = str(trans.get("Категория", "")).lower()
        description = str(trans.get("Описание", "")).lower()

        if search_query in category or search_query in description:
            results.append(trans)

    logger.info(f"Найдено {len(results)} транзакций по запросу '{search_query}'")
    return results


def simple_search_from_excel(search_query: str, excel_path: str = "data/operations.xlsx") -> List[Dict[str, Any]]:
    """Поиск транзакций в Excel-файле"""
    try:
        df = pd.read_excel(excel_path)
        transactions = df.to_dict("records")
        return simple_search(search_query, transactions)
    except FileNotFoundError:
        logger.error(f"Файл {excel_path} не найден")
        return []
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel: {e}")
        return []


# Пример использования
if __name__ == "__main__":
    results = simple_search_from_excel("перевод")
    print(json.dumps(results, ensure_ascii=False, indent=2))



    def search_by_phone(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Поиск транзакций, содержащих мобильные номера в описании.

        Поддерживаемые форматы:
        - +7 921 11-22-33
        - +7 995 555-55-55
        - 8 921 333-44-55
        - 89000000000
        - +7 (900) 000-00-00
        - 8 (900) 000-00-00
        """
        # Регулярное выражение для поиска телефонных номеров (разные форматы)
        phone_pattern = re.compile(
            r"""
            (\+7|8)                         # Код страны или 8
            \s*                             # Возможные пробелы
            (?:\(?\d{3}\)?)?               # Код оператора (с скобками или без)
            [\s\-]?                         # Разделитель
            \d{3}                           # 3 цифры
            [\s\-]?                         # Разделитель
            \d{2}                           # 2 цифры
            [\s\-]?                         # Разделитель
            \d{2}                           # 2 цифры
            """,
            re.VERBOSE
        )

        results = []
        for trans in transactions:
            description = str(trans.get("Описание", ""))

            # Ищем номер телефона в описании
            if phone_pattern.search(description):
                results.append(trans)

        logger.info(f"Найдено {len(results)} транзакций с номерами телефонов")
        return results


    def search_by_phone_from_excel(excel_path: str = "data/operations.xlsx") -> List[Dict[str, Any]]:
        """Поиск транзакций с телефонами в Excel-файле"""
        try:
            df = pd.read_excel(excel_path)
            transactions = df.to_dict("records")
            return search_by_phone(transactions)
        except FileNotFoundError:
            logger.error(f"Файл {excel_path} не найден")
            return []
        except Exception as e:
            logger.error(f"Ошибка при чтении Excel: {e}")
            return []


    # Дополнительная функция для поиска переводов физлицам
    def search_transfers_to_individuals(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Поиск транзакций, которые относятся к переводам физлицам.
        Категория = "Переводы", в описании есть имя и первая буква фамилии.
        """
        results = []

        for trans in transactions:
            category = str(trans.get("Категория", ""))
            description = str(trans.get("Описание", ""))

            # Проверяем: категория "Переводы" и в описании есть имя с фамилией
            if category == "Переводы":
                # Ищем паттерн: Имя + первая буква фамилии с точкой
                # Например: "Валерий А.", "Сергей З."
                name_pattern = re.compile(r'[А-Я][а-я]+\s+[А-Я]\.')
                if name_pattern.search(description):
                    results.append(trans)

        logger.info(f"Найдено {len(results)} переводов физлицам")
        return results


    # Пример использования
    if __name__ == "__main__":
        # Поиск по телефону
        phone_results = search_by_phone_from_excel()
        print("Транзакции с телефонами:")
        print(json.dumps(phone_results, ensure_ascii=False, indent=2))

        # Поиск переводов физлицам
        df = pd.read_excel("data/operations.xlsx")
        transactions = df.to_dict("records")
        transfer_results = search_transfers_to_individuals(transactions)
        print("\nПереводы физлицам:")
        print(json.dumps(transfer_results, ensure_ascii=False, indent=2))
