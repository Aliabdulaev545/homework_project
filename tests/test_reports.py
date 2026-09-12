from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.reports import report_decorator, spending_by_category, spending_by_weekday, spending_by_workday


def test_spending_by_weekday():
    """Тест: траты по дням недели"""
    # Создаём тестовые данные за последние 3 месяца
    dates = []
    for i in range(7):
        dates.append((datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"))

    test_data = pd.DataFrame(
        {
            "Дата операции": dates,
            "Сумма платежа": [-100.0, -200.0, -300.0, -400.0, -500.0, -600.0, -700.0],
            "Категория": ["Еда"] * 7,
            "Описание": ["Магазин"] * 7,
        }
    )

    result = spending_by_weekday(test_data)

    # Проверяем структуру
    assert isinstance(result, pd.DataFrame)
    assert "День недели" in result.columns
    assert "Средние траты, руб" in result.columns
    assert len(result) == 7  # Все дни недели


def test_spending_by_weekday_empty():
    """Тест: траты по дням недели с пустыми данными"""
    test_data = pd.DataFrame({"Дата операции": [], "Сумма платежа": [], "Категория": [], "Описание": []})

    result = spending_by_weekday(test_data)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_spending_by_category():
    """Тест: траты по категории"""
    test_data = pd.DataFrame(
        {
            "Дата операции": [datetime.now().strftime("%Y-%m-%d")] * 3,
            "Сумма платежа": [-100.0, -200.0, -50.0],
            "Категория": ["Супермаркеты", "Супермаркеты", "Транспорт"],
            "Описание": ["Магазин", "Магазин", "Такси"],
        }
    )

    result = spending_by_category(test_data, "Супермаркеты")
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2  # Две транзакции в категории
    assert abs(result["Сумма платежа"].sum()) == 300.0


def test_spending_by_workday():
    """Тест: траты в рабочие/выходные дни"""
    test_data = pd.DataFrame(
        {
            "Дата операции": [datetime.now().strftime("%Y-%m-%d")] * 5,
            "Сумма платежа": [-100.0, -200.0, -300.0, -400.0, -500.0],
            "Категория": ["Еда"] * 5,
            "Описание": ["Магазин"] * 5,
        }
    )

    result = spending_by_workday(test_data)

    assert isinstance(result, pd.DataFrame)
    assert "Тип дня" in result.columns
    assert "Средние траты, руб" in result.columns
    # Должен быть либо рабочий, либо выходной день
    assert len(result) == 1 or len(result) == 2


def test_report_decorator():
    """Тест: декоратор для отчётов"""

    @report_decorator("test_report.json")
    def test_func():
        return {"test": "data"}

    result = test_func()
    assert result == {"test": "data"}

    # Проверяем, что файл создался
    import os

    assert os.path.exists("test_report.json")

    # Удаляем тестовый файл
    os.remove("test_report.json")


if __name__ == "__main__":
    pytest.main(["-v"])
