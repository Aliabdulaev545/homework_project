import pytest

from src.services import search_by_phone, search_transfers_to_individuals, simple_search


def test_simple_search():
    """Тест: простой поиск по подстроке"""
    test_transactions = [
        {"Категория": "Еда", "Описание": "Магазин Пятёрочка"},
        {"Категория": "Транспорт", "Описание": "Такси"},
        {"Категория": "Еда", "Описание": "Кафе"},
    ]

    result = simple_search("Еда", test_transactions)
    assert len(result) == 2
    assert result[0]["Категория"] == "Еда"
    assert result[1]["Категория"] == "Еда"


def test_simple_search_case_insensitive():
    """Тест: поиск нечувствителен к регистру"""
    test_transactions = [
        {"Категория": "еДА", "Описание": "Магазин"},
        {"Категория": "транспорт", "Описание": "Такси"},
    ]

    result = simple_search("еда", test_transactions)
    assert len(result) == 1


def test_simple_search_empty_query():
    """Тест: пустой запрос"""
    test_transactions = [
        {"Категория": "Еда", "Описание": "Магазин"},
        {"Категория": "Транспорт", "Описание": "Такси"},
    ]

    result = simple_search("", test_transactions)
    assert len(result) == 2  # Возвращает все


def test_search_by_phone():
    """Тест: поиск по телефонным номерам"""
    test_transactions = [
        {"Описание": "Оплата +7 921 11-22-33"},
        {"Описание": "Такси"},
        {"Описание": "Перевод +7 995 555-55-55"},
        {"Описание": "Магазин"},
    ]

    result = search_by_phone(test_transactions)
    assert len(result) == 2
    assert "+7 921 11-22-33" in result[0]["Описание"]
    assert "+7 995 555-55-55" in result[1]["Описание"]


def test_search_by_phone_different_formats():
    """Тест: поиск телефонов в разных форматах"""
    test_transactions = [
        {"Описание": "МТС +7 921 11-22-33"},
        {"Описание": "Тинькофф +7 995 555-55-55"},
        {"Описание": "МТС Mobile +7 981 333-44-55"},
        {"Описание": "89001234567"},  # Без +7
        {"Описание": "+7 (900) 000-00-00"},  # Со скобками
    ]

    result = search_by_phone(test_transactions)
    assert len(result) >= 3


def test_search_transfers_to_individuals():
    """Тест: поиск переводов физлицам"""
    test_transactions = [
        {"Категория": "Переводы", "Описание": "Перевод Валерий А."},
        {"Категория": "Переводы", "Описание": "Перевод Сергей З."},
        {"Категория": "Переводы", "Описание": "Перевод в банк"},
        {"Категория": "Еда", "Описание": "Магазин"},
    ]

    result = search_transfers_to_individuals(test_transactions)
    assert len(result) == 2
    assert "Валерий А." in result[0]["Описание"] or "Сергей З." in result[0]["Описание"]


if __name__ == "__main__":
    pytest.main(["-v"])
