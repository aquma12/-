import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "data/expenses.json"

class ExpenseTracker:
    def __init__(self):
        self.expenses = []
        self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except:
                self.expenses = []

    def save_data(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)

    def add_expense(self, amount: float, category: str, date: str) -> bool:
        if amount <= 0:
            return False
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return False
        expense = {
            "amount": amount,
            "category": category,
            "date": date
        }
        self.expenses.append(expense)
        self.save_data()
        return True

    def get_expenses(self, category: str = None, date_from: str = None, date_to: str = None):
        result = self.expenses
        if category and category != "Все":
            result = [e for e in result if e["category"] == category]
        if date_from:
            try:
                result = [e for e in result if e["date"] >= date_from]
            except:
                pass
        if date_to:
            try:
                result = [e for e in result if e["date"] <= date_to]
            except:
                pass
        return result

    def get_total(self, expenses: list = None):
        if expenses is None:
            expenses = self.expenses
        return sum(e["amount"] for e in expenses)

    def get_categories(self):
        cats = set(e["category"] for e in self.expenses)
        return ["Все"] + sorted(cats)

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("700x600")
        self.tracker = ExpenseTracker()

        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Категория:").grid(row=1, column=0, sticky="w", pady=5)
        self.category_entry = ttk.Entry(input_frame, width=15)
        self.category_entry.grid(row=1, column=1, padx=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=2, column=1, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Button(input_frame, text="Добавить", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=10)

        filter_frame = ttk.LabelFrame(self.root, text="Фильтр", padding=10)
        filter_frame.pack(fill="x", padx=10)

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0)
        self.filter_category = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.filter_category.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="С:").grid(row=0, column=2)
        self.filter_date_from = ttk.Entry(filter_frame, width=12)
        self.filter_date_from.grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="По:").grid(row=0, column=4)
        self.filter_date_to = ttk.Entry(filter_frame, width=12)
        self.filter_date_to.grid(row=0, column=5, padx=5)

        ttk.Button(filter_frame, text="Применить", command=self.apply_filter).grid(row=0, column=6, padx=10)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter).grid(row=0, column=7)

        self.total_label = ttk.Label(self.root, text="Итого: 0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(anchor="w", padx=10, pady=5)

        self.tree = ttk.Treeview(self.root, columns=("date", "category", "amount"), show="headings")
        for col, text in [("date", "Дата"), ("category", "Категория"), ("amount", "Сумма")]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(status_frame, text="Удалить выбранное", command=self.delete_expense).pack(side="left")
        self.status = ttk.Label(status_frame, text="Готов", relief="sunken")
        self.status.pack(side="right")

    def add_expense(self):
        try:
            amount = float(self.amount_entry.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму (число)")
            return

        category = self.category_entry.get().strip()
        if not category:
            messagebox.showerror("Ошибка", "Введите категорию")
            return

        date = self.date_entry.get().strip()

        if self.tracker.add_expense(amount, category, date):
            self.refresh_table()
            self.amount_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
            self.status.config(text="Расход добавлен")
        else:
            messagebox.showerror("Ошибка", "Неверные данные. Сумма должна быть > 0, дата в формате ГГГГ-ММ-ДД")

    def apply_filter(self):
        category = self.filter_category.get()
        date_from = self.filter_date_from.get().strip() or None
        date_to = self.filter_date_to.get().strip() or None

        expenses = self.tracker.get_expenses(category, date_from, date_to)
        self.update_table(expenses)
        total = self.tracker.get_total(expenses)
        self.total_label.config(text=f"Итого: {total:.2f}")
        self.status.config(text=f"Найдено записей: {len(expenses)}")

    def reset_filter(self):
        self.filter_category.set("")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self):
        self.update_table(self.tracker.expenses)
        self.total_label.config(text=f"Итого: {self.tracker.get_total():.2f}")
        categories = self.tracker.get_categories()
        self.filter_category["values"] = categories
        if categories:
            self.filter_category.set("Все")

    def update_table(self, expenses):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for e in expenses:
            self.tree.insert("", "end", values=(e["date"], e["category"], e["amount"]))

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        for i, e in enumerate(self.tracker.expenses):
            if e["date"] == values[0] and e["category"] == values[1] and e["amount"] == values[2]:
                self.tracker.expenses.pop(i)
                self.tracker.save_data()
                break
        self.refresh_table()
        self.status.config(text="Запись удалена")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()