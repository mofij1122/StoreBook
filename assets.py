import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QDateEdit, QComboBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QDate


class AssetsWindow(QWidget):
    def __init__(self, store_id=None):
        super().__init__()
        self.store_id = store_id
        self.setWindowTitle("Assets Module")
        self.setGeometry(500, 200, 500, 450)
        self.setup_ui()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                asset_name TEXT,
                value REAL,
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

        self.title_label = QLabel("Add Asset Entry", self)
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

        self.name_label = QLabel("Asset Name:", self)
        self.name_label.setFont(QFont("Segoe UI", 12))
        self.name_label.move(70, 130)

        self.name_input = QLineEdit(self)
        self.name_input.setFont(QFont("Segoe UI", 12))
        self.name_input.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        self.name_input.move(180, 130)
        self.name_input.resize(220, 30)

        self.value_label = QLabel("Value:", self)
        self.value_label.setFont(QFont("Segoe UI", 12))
        self.value_label.move(70, 180)

        self.value_input = QLineEdit(self)
        self.value_input.setFont(QFont("Segoe UI", 12))
        self.value_input.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        self.value_input.move(180, 180)
        self.value_input.resize(220, 30)

        self.category_label = QLabel("Category:", self)
        self.category_label.setFont(QFont("Segoe UI", 12))
        self.category_label.move(70, 230)

        self.category_combo = QComboBox(self)
        self.category_combo.setFont(QFont("Segoe UI", 12))
        self.category_combo.addItems(["Property", "Vehicle", "Machinery", "Investments", "Other"])
        self.category_combo.move(180, 230)
        self.category_combo.resize(220, 30)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.submit_button.move(200, 280)
        self.submit_button.resize(100, 35)
        self.submit_button.clicked.connect(self.save_data)

    def go_back(self):
        self.close()  # Close the current window, returning to Dashboard

    def save_data(self):
        date = self.date_input.date().toString("yyyy-MM-dd")
        asset_name = self.name_input.text()
        value = self.value_input.text()
        category = self.category_combo.currentText()

        if not asset_name or not value:
            QMessageBox.warning(self, "Incomplete", "Please enter all fields.")
            return
        try:
            value = float(value)
            if value < 0:
                raise ValueError("Value cannot be negative")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid positive number for value.")
            return

        if not self.store_id:
            QMessageBox.warning(self, "Error", "No store selected.")
            return

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")
            c.execute("INSERT INTO assets (date, asset_name, value, category, store_id) VALUES (?, ?, ?, ?, ?)",
                      (date, asset_name, value, category, self.store_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Asset entry saved successfully!")
            self.date_input.setDate(QDate.currentDate())
            self.name_input.clear()
            self.value_input.clear()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to save entry: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AssetsWindow(store_id=1)
    window.show()
    sys.exit(app.exec_())
