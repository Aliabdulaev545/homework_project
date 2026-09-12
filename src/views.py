# src/views.py

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_user_settings() -> Dict[str, Any]:
    """Загружает настройки пользователя из user_settings.json"""
    try:
        with open("user_settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Файл user_settings.json не найден")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}


def get_greeting() -> str:
    """Возвращает приветствие в зависимости от времени"""
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 18:
        return "Good afternoon"
    elif 18 <= current_hour < 23:
        return "Good evening"
    else:
        return "Good night"


def get_card_info(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """Возвращает информацию по картам"""
    cards = []
    for card, group in transactions.groupby("Номер карты"):
        last_digits = str(card)[-4:] if card else "0000"
        total_spent = abs(group[group["Сумма платежа"] < 0]["Сумма платежа"].sum())
        cashback = round(total_spent / 100, 2)
        cards.append({"last_digits": last_digits, "total_spent": round(total_spent, 2), "cashback": cashback})
    return cards


def get_top_transactions(transactions: pd.DataFrame, limit: int = 5) -> List[Dict[str, Any]]:
    """Возвращает топ-N транзакций по сумме"""
    sorted_trans = transactions.sort_values("Сумма платежа", ascending=False)
    top = []
    for _, row in sorted_trans.head(limit).iterrows():
        top.append(
            {
                "date": str(row["Дата операции"]),
                "amount": round(row["Сумма платежа"], 2),
                "category": row.get("Категория", "Без категории"),
                "description": row.get("Описание", "Нет описания"),
            }
        )
    return top


def get_stock_prices(param):
    pass


def get_currency_rates(param):
    pass


def main_page(date_str: str) -> Dict[str, Any]:
    logger.info(f"Запрос к главной странице: {date_str}")

    # Проверяем корректность даты
    try:
        datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        logger.error(f"Некорректная дата: {date_str}")
        return {
            "error": f"Некорректная дата: {date_str}",
            "greeting": get_greeting(),
            "cards": [],
            "top_transactions": [],
            "currency_rates": [],
            "stock_prices": [],
        }

    try:
        df = pd.read_excel("data/operations.xlsx", engine="openpyxl")
    except FileNotFoundError:
        logger.error("Файл data/operations.xlsx не найден")
        return {
            "error": "Файл data/operations.xlsx не найден",
            "greeting": get_greeting(),
            "cards": [],
            "top_transactions": [],
            "currency_rates": [],
            "stock_prices": [],
        }
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel: {e}")
        return {
            "error": str(e),
            "greeting": get_greeting(),
            "cards": [],
            "top_transactions": [],
            "currency_rates": [],
            "stock_prices": [],
        }

    return {
        "greeting": get_greeting(),
        "cards": get_card_info(df),
        "top_transactions": get_top_transactions(df, 5),
        "currency_rates": [],
        "stock_prices": [],
    }
