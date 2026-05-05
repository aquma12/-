import pytest
import os
import sys
import json
sys.path.insert(0, os.path.dirname(__file__))

from app import ExpenseTracker, DATA_FILE

def test_add_expense_positive():
    tracker = ExpenseTracker()
    tracker.expenses = []
    result = tracker.add_expense(100, "Еда", "2026-05-05")
    assert result == True
    assert len(tracker.expenses) == 1

def test_add_expense_negative_amount():
    tracker = ExpenseTracker()
    tracker.expenses = []
    result = tracker.add_expense(-10, "Еда", "2026-05-05")
    assert result == False

def test_add_expense_zero():
    tracker = ExpenseTracker()
    tracker.expenses = []
    result = tracker.add_expense(0, "Еда", "2026-05-05")
    assert result == False

def test_add_expense_invalid_date():
    tracker = ExpenseTracker()
    tracker.expenses = []
    result = tracker.add_expense(100, "Еда", "invalid-date")
    assert result == False

def test_get_total():
    tracker = ExpenseTracker()
    tracker.expenses = [
        {"amount": 100, "category": "Еда", "date": "2026-05-05"},
        {"amount": 200, "category": "Транспорт", "date": "2026-05-06"}
    ]
    total = tracker.get_total()
    assert total == 300

def test_filter_by_category():
    tracker = ExpenseTracker()
    tracker.expenses = [
        {"amount": 100, "category": "Еда", "date": "2026-05-05"},
        {"amount": 200, "category": "Транспорт", "date": "2026-05-06"}
    ]
    filtered = tracker.get_expenses(category="Еда")
    assert len(filtered) == 1
    assert filtered[0]["category"] == "Еда"

def test_filter_by_date():
    tracker = ExpenseTracker()
    tracker.expenses = [
        {"amount": 100, "category": "Еда", "date": "2026-05-01"},
        {"amount": 200, "category": "Еда", "date": "2026-05-10"},
        {"amount": 300, "category": "Еда", "date": "2026-05-20"}
    ]
    filtered = tracker.get_expenses(date_from="2026-05-05", date_to="2026-05-15")
    assert len(filtered) == 1
    assert filtered[0]["amount"] == 200

def test_get_categories():
    tracker = ExpenseTracker()
    tracker.expenses = [
        {"amount": 100, "category": "Еда", "date": "2026-05-05"},
        {"amount": 200, "category": "Транспорт", "date": "2026-05-06"}
    ]
    cats = tracker.get_categories()
    assert "Все" in cats
    assert "Еда" in cats
    assert "Транспорт" in cats