import sys
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox,
    QVBoxLayout, QComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class StoreDetailsForm(QWidget):
    def __init__(self, main_window=None, user_id=None):
        super().__init__()
        self.main_window = main_window
        self.user_id = user_id
        self.setWindowTitle("Store Details Form")

        # Dynamic sizing and centering
        screen = QApplication.primaryScreen()
        size = screen.availableGeometry()
        width = int(size.width() * 0.45)
        height = int(size.height() * 0.25)
        self.resize(width, height)
        self.move((size.width() - width) // 2, (size.height() - height) // 2)

        self.setup_ui()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("""
        CREATE TABLE IF NOT EXISTS store_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            storename TEXT,
            storetype TEXT,
            ownername TEXT
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            store_name TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        conn.commit()
        conn.close()

    def setup_ui(self):
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e0eafc, stop:1 #cfdef3);")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 50, 30, 50)
        main_layout.setSpacing(20)
        main_layout.addStretch()

        card = QWidget()
        card.setFixedWidth(480)
        card.setStyleSheet("""
            background: #ffffff;
            border-radius: 20px;
            padding: 10px;
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        title = QLabel("Store Details")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #27ae60; margin-bottom: 10px;")
        card_layout.addWidget(title)

        # Input Fields
        self.username_input = self.create_input("Your Name:", card_layout)
        self.storename_input = self.create_input("Store Name:", card_layout)
        self.storetype_input = self.create_dropdown("Store Type:", card_layout, [
            "Grocery", "Electronics", "Clothing", "Pharmacy", "Restaurant", "Bookstore", "Other"
        ])
        self.ownername_input = self.create_input("Owner Name:", card_layout)

        # Submit Button (Top)
        submit_btn = QPushButton("Submit")
        submit_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        submit_btn.setFixedHeight(45)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        submit_btn.clicked.connect(self.submit_form)
        card_layout.addWidget(submit_btn)

        # Back Button (Bottom)
        back_btn = QPushButton("Back")
        back_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        back_btn.setFixedHeight(45)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        card_layout.addWidget(back_btn)

        card_layout.addStretch()
        main_layout.addWidget(card, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    def create_input(self, label_text, layout):
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 14))
        label.setStyleSheet("color: #333333; margin-bottom: 5px;")
        layout.addWidget(label)

        input_field = QLineEdit()
        input_field.setFont(QFont("Segoe UI", 12))
        input_field.setFixedHeight(55)
        input_field.setStyleSheet("""
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #bdc3c7;
            background: #f0f4f7;
        """)
        layout.addWidget(input_field)
        return input_field

    def create_dropdown(self, label_text, layout, items):
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 14))
        label.setStyleSheet("color: #333333; margin-bottom: 5px;")
        layout.addWidget(label)

        dropdown = QComboBox()
        dropdown.setFont(QFont("Segoe UI", 12))
        dropdown.setFixedHeight(45)
        dropdown.setStyleSheet("""
            QComboBox {
                border-radius: 8px;
                padding: 10px;
                border: 1px solid #bdc3c7;
                background: #f0f4f7;
            }
        """)
        dropdown.addItems(items)
        layout.addWidget(dropdown)
        return dropdown

    def go_back(self):
        if self.main_window:
            self.main_window.show_store_management()
        else:
            self.close()

    def submit_form(self):
        username = self.username_input.text()
        storename = self.storename_input.text()
        storetype = self.storetype_input.currentText()
        ownername = self.ownername_input.text()

        if not all([username, storename, storetype, ownername]):
            QMessageBox.warning(self, "Incomplete", "Please fill all fields.")
            return

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")
            c.execute("INSERT INTO store_details (username, storename, storetype, ownername) VALUES (?, ?, ?, ?)",
                      (username, storename, storetype, ownername))
            c.execute("INSERT INTO stores (user_id, store_name) VALUES (?, ?)",
                      (self.user_id or 1, storename))
            store_id = c.lastrowid
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Store details saved successfully!")

            if self.main_window:
                self.main_window.show_dashboard(store_id=store_id)

        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to save store details: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StoreDetailsForm(user_id=1)
    window.show()
    sys.exit(app.exec_())
