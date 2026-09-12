# src/reports.py

import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def report_decorator(filename: Optional[str] = None):
    """
    Декоратор для записи результатов отчетов в файл.

    Args:
        filename: имя файла для сохранения (опционально)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Выполняем функцию
            result = func(*args, **kwargs)

            # Определяем имя файла
            if filename:
                output_filename = filename
            else:
                # Генерируем имя по умолчанию
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"report_{func.__name__}_{timestamp}.json"

            # Сохраняем результат в файл
            try:
                if isinstance(result, pd.DataFrame):
                    # Если результат - DataFrame, конвертируем в JSON
                    with open(output_filename, "w", encoding="utf-8") as f:
                        json.dump(result.to_dict("records"), f, ensure_ascii=False, indent=2)
                elif isinstance(result, dict) or isinstance(result, list):
                    with open(output_filename, "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                else:
                    with open(output_filename, "w", encoding="utf-8") as f:
                        f.write(str(result))

                logger.info(f"Отчет сохранен в файл: {output_filename}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")

            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает средние траты в каждый из дней недели за последние 3 месяца.

    Args:
        transactions: датафрейм с транзакциями
        date: опциональная дата (формат: 'YYYY-MM-DD')

    Returns:
        DataFrame со средними тратами по дням недели
    """
    try:
        # Определяем дату
        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")

        # Начальная дата: 3 месяца назад
        start_date = end_date - timedelta(days=90)

        # Преобразуем дату операции в datetime
        if "Дата операции" in transactions.columns:
            transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"])

            # Фильтруем транзакции за последние 3 месяца
            mask = (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)
            filtered_trans = transactions.loc[mask]

            # Берем только расходы (отрицательные суммы)
            if "Сумма платежа" in filtered_trans.columns:
                expenses = filtered_trans[filtered_trans["Сумма платежа"] < 0]

                if not expenses.empty:
                    # Добавляем день недели
                    expenses["День недели"] = expenses["Дата операции"].dt.day_name(locale="ru_RU")

                    # Группируем по дням недели и считаем среднюю сумму
                    weekday_spending = expenses.groupby("День недели")["Сумма платежа"].mean().abs()

                    # Сортируем по дням недели (понедельник, вторник, ...)
                    weekday_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
                    result = weekday_spending.reindex(weekday_order).reset_index()
                    result.columns = ["День недели", "Средние траты, руб"]

                    return result
                else:
                    logger.warning("Нет расходов за указанный период")
                    return pd.DataFrame(columns=["День недели", "Средние траты, руб"])
            else:
                logger.error("В данных нет столбца 'Сумма платежа'")
        else:
            logger.error("В данных нет столбца 'Дата операции'")

        return pd.DataFrame(columns=["День недели", "Средние траты, руб"])

    except Exception as e:
        logger.error(f"Ошибка в spending_by_weekday: {e}")
        return pd.DataFrame(columns=["День недели", "Средние траты, руб"])


# Дополнительные функции для отчетов


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние 3 месяца.
    """
    try:
        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")

        start_date = end_date - timedelta(days=90)

        if "Дата операции" in transactions.columns:
            transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"])
            mask = (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)
            filtered_trans = transactions.loc[mask]

            if "Категория" in filtered_trans.columns and "Сумма платежа" in filtered_trans.columns:
                category_expenses = filtered_trans[
                    (filtered_trans["Категория"] == category) & (filtered_trans["Сумма платежа"] < 0)
                ]

                if not category_expenses.empty:
                    result = category_expenses[["Дата операции", "Сумма платежа", "Описание"]].copy()
                    result["Сумма платежа"] = result["Сумма платежа"].abs()
                    return result
                else:
                    return pd.DataFrame(columns=["Дата операции", "Сумма платежа", "Описание"])
            else:
                logger.error("Отсутствуют необходимые столбцы")

        return pd.DataFrame(columns=["Дата операции", "Сумма платежа", "Описание"])

    except Exception as e:
        logger.error(f"Ошибка в spending_by_category: {e}")
        return pd.DataFrame(columns=["Дата операции", "Сумма платежа", "Описание"])


@report_decorator()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает средние траты в рабочий и выходной день за последние 3 месяца.
    """
    try:
        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")

        start_date = end_date - timedelta(days=90)

        if "Дата операции" in transactions.columns:
            transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"])
            mask = (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)
            filtered_trans = transactions.loc[mask]

            if "Сумма платежа" in filtered_trans.columns:
                expenses = filtered_trans[filtered_trans["Сумма платежа"] < 0]

                if not expenses.empty:
                    # Определяем рабочие дни (пн-пт) и выходные (сб-вс)
                    expenses["День недели"] = expenses["Дата операции"].dt.weekday
                    expenses["Тип дня"] = expenses["День недели"].apply(lambda x: "Рабочий" if x < 5 else "Выходной")

                    # Считаем средние траты
                    result = expenses.groupby("Тип дня")["Сумма платежа"].mean().abs().reset_index()
                    result.columns = ["Тип дня", "Средние траты, руб"]
                    return result
                else:
                    logger.warning("Нет расходов за указанный период")
                    return pd.DataFrame(columns=["Тип дня", "Средние траты, руб"])
            else:
                logger.error("В данных нет столбца 'Сумма платежа'")
        else:
            logger.error("В данных нет столбца 'Дата операции'")

        return pd.DataFrame(columns=["Тип дня", "Средние траты, руб"])

    except Exception as e:
        logger.error(f"Ошибка в spending_by_workday: {e}")
        return pd.DataFrame(columns=["Тип дня", "Средние траты, руб"])


# Пример использования
if __name__ == "__main__":
    try:
        # Загружаем данные
        df = pd.read_excel("data/operations.xlsx")

        # Отчет по дням недели
        weekday_report = spending_by_weekday(df)
        print("\nТраты по дням недели:")
        print(weekday_report)

        # Отчет по категории
        category_report = spending_by_category(df, "Супермаркеты")
        print("\nТраты по категории 'Супермаркеты':")
        print(category_report)

        # Отчет по рабочим/выходным дням
        workday_report = spending_by_workday(df)
        print("\nТраты в рабочие/выходные дни:")
        print(workday_report)

    except Exception as e:
        logger.error(f"Ошибка: {e}")
