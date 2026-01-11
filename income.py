import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QDateEdit, QComboBox, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QDate, Qt


class IncomeWindow(QWidget):
    def __init__(self, store_id=None):
        super().__init__()
        self.store_id = store_id
        self.setWindowTitle("Income Module")
        self.setGeometry(500, 200, 500, 400)
        self.setup_ui()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("""
            CREATE TABLE IF NOT EXISTS income (
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

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        header_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setFont(QFont("Segoe UI", 10))
        back_btn.setStyleSheet("background-color: #3498db; color: white; border-radius: 3px; padding: 2px 8px;")
        back_btn.clicked.connect(self.go_back)
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setFixedHeight(40)
        main_layout.addWidget(header_widget)

        self.title_label = QLabel("Add Income Entry", self)
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        self.date_label = QLabel("Date:", self)
        self.date_label.setFont(QFont("Segoe UI", 12))
        main_layout.addWidget(self.date_label)
        self.date_input = QDateEdit(self)
        self.date_input.setFont(QFont("Segoe UI", 12))
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        self.date_input.setMinimumSize(220, 30)
        main_layout.addWidget(self.date_input)

        self.amount_label = QLabel("Amount:", self)
        self.amount_label.setFont(QFont("Segoe UI", 12))
        main_layout.addWidget(self.amount_label)
        self.amount_input = QLineEdit(self)
        self.amount_input.setFont(QFont("Segoe UI", 12))
        self.amount_input.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        self.amount_input.setMinimumSize(220, 30)
        main_layout.addWidget(self.amount_input)

        self.category_label = QLabel("Category:", self)
        self.category_label.setFont(QFont("Segoe UI", 12))
        main_layout.addWidget(self.category_label)
        self.category_dropdown = QComboBox(self)
        self.category_dropdown.setFont(QFont("Segoe UI", 12))
        self.category_dropdown.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        self.category_dropdown.setMinimumSize(220, 30)
        categories = ["Sales", "Services", "Commission", "Rent Received", "Other"]
        self.category_dropdown.addItems(categories)
        main_layout.addWidget(self.category_dropdown)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.submit_button.setMinimumSize(100, 35)
        main_layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)
        self.submit_button.clicked.connect(self.save_data)

        main_layout.addStretch()

    def go_back(self):
        self.close()

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
            c.execute("INSERT INTO income (date, amount, category, store_id) VALUES (?, ?, ?, ?)",
                      (date, amount, category, self.store_id))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Income entry saved successfully!")
            self.amount_input.clear()
            self.category_dropdown.setCurrentIndex(0)
            self.date_input.setDate(QDate.currentDate())
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to save entry: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = IncomeWindow(store_id=1)
    window.show()
    sys.exit(app.exec_())
