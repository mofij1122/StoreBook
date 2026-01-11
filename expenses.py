import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QDateEdit, QComboBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QDate

class ExpensesWindow(QWidget):
    def __init__(self, store_id=None):
        super().__init__()
        self.store_id = store_id
        self.setWindowTitle("Expenses Module")
        self.setGeometry(500, 200, 500, 400)
        self.setup_ui()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                amount REAL,
                category TEXT,
                store_id INTEGER,
                FOREIGN KEY(store_id) REFERENCES stores(id)
            )
        """)
        conn.commit()
        conn.close()

    def setup_ui(self):
        self.setStyleSheet("background-color: #f0f4f7;")

        # Back button
        self.back_button = QPushButton("Back", self)
        self.back_button.setFont(QFont("Segoe UI", 10))
        self.back_button.setStyleSheet("background-color: #3498db; color: white; border-radius: 3px; padding: 2px 8px;")
        self.back_button.move(10, 10)
        self.back_button.resize(70, 30)
        self.back_button.clicked.connect(self.go_back)

        self.title_label = QLabel("Add Expense Entry", self)
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.title_label.move(170, 20)

        self.date_label = QLabel("Date:", self)
        self.date_label.setFont(QFont("Segoe UI", 12))
        self.date_label.move(70, 80)

        self.date_input = QDateEdit(self)
        self.date_input.setFont(QFont("Segoe UI", 12))
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        self.date_input.move(180, 80)
        self.date_input.resize(220, 30)

        self.amount_label = QLabel("Amount:", self)
        self.amount_label.setFont(QFont("Segoe UI", 12))
        self.amount_label.move(70, 130)

        self.amount_input = QLineEdit(self)
        self.amount_input.setFont(QFont("Segoe UI", 12))
        self.amount_input.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        self.amount_input.move(180, 130)
        self.amount_input.resize(220, 30)

        self.category_label = QLabel("Category:", self)
        self.category_label.setFont(QFont("Segoe UI", 12))
        self.category_label.move(70, 180)

        self.category_dropdown = QComboBox(self)
        self.category_dropdown.setFont(QFont("Segoe UI", 12))
        self.category_dropdown.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        self.category_dropdown.move(180, 180)
        self.category_dropdown.resize(220, 30)
        categories = ["Rent", "Electricity", "Purchase", "Salary", "Other"]
        self.category_dropdown.addItems(categories)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        self.submit_button.move(200, 240)
        self.submit_button.resize(100, 35)
        self.submit_button.clicked.connect(self.save_data)

    def go_back(self):
        self.close()  # Close the current window, returning to Dashboard

    def save_data(self):
        date = self.date_input.date().toString("yyyy-MM-dd")
        amount = self.amount_input.text()
        category = self.category_dropdown.currentText()

        if not amount:
            QMessageBox.warning(self, "Incomplete", "Please enter amount.")
            return
        try:
            amount = float(amount)
            if amount < 0:
                raise ValueError("Amount cannot be negative")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid positive number for amount.")
            return

        if not self.store_id:
            QMessageBox.warning(self, "Error", "No store selected.")
            return

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")
            c.execute("INSERT INTO expenses (date, amount, category, store_id) VALUES (?, ?, ?, ?)",
                      (date, amount, category, self.store_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Expense entry saved successfully!")
            self.date_input.setDate(QDate.currentDate())
            self.amount_input.clear()
            self.category_dropdown.setCurrentIndex(0)
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to save entry: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExpensesWindow(store_id=1)
    window.show()
    sys.exit(app.exec_())