# tests/test_views.py

import pytest
import pandas as pd
from src.views import main_page, get_greeting, get_card_info, get_top_transactions


def test_get_greeting():
    greeting = get_greeting()
    assert greeting in ["Good morning", "Good afternoon", "Good evening", "Good night"]


def test_get_card_info():
    test_data = pd.DataFrame({
        "Номер карты": [1234567890123456, 1234567890123456, 9876543210987654],
        "Сумма платежа": [-100.0, -200.0, -50.0],
        "Категория": ["Food", "Transport", "Food"]
    })
    result = get_card_info(test_data)
    assert isinstance(result, list)
    assert len(result) == 2
    assert "last_digits" in result[0]
    assert "total_spent" in result[0]
    assert "cashback" in result[0]


def test_get_top_transactions():
    test_data = pd.DataFrame({
        "Дата операции": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "Сумма платежа": [1000.0, 500.0, 300.0, 200.0, 100.0],
        "Категория": ["Food", "Transport", "Food", "Transport", "Food"],
        "Описание": ["Shop", "Taxi", "Cafe", "Metro", "Supermarket"]
    })
    result = get_top_transactions(test_data, limit=3)
    assert len(result) == 3
    assert result[0]["amount"] == 1000.0


def test_main_page():
    result = main_page("2024-01-15 14:30:00")
    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result


def test_main_page_invalid_date():
    result = main_page("invalid-date")
    assert "error" in result
    assert "greeting" in result


if __name__ == "__main__":
    pytest.main(["-v"])
