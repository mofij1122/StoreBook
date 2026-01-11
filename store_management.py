import sys
import sqlite3

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QComboBox, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import traceback

class StoreManagement(QWidget):
    def __init__(self, main_window=None, user_id=None):
        super().__init__()
        self.main_window = main_window if main_window else object()  # Mock object for testing
        self.user_id = user_id if user_id else 1  # Default user_id for testing
        self.setWindowTitle("Store Management")
        self.setGeometry(500, 200, 900, 600)  # Wider window for bigger card
        self.setup_ui()
        self.load_stores()

    def setup_ui(self):
        try:
            self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e0eafc, stop:1 #cfdef3);")
            main_layout = QVBoxLayout(self)
            main_layout.addStretch()

            card = QWidget()
            card.setMinimumHeight(int(self.height() * 0.6))
            card.setMinimumWidth(int(self.width() * 0.6))
            card.setStyleSheet("""
                background: #fff;
                border-radius: 24px;
                padding: 48px 52px;
                box-shadow: 0px 16px 32px rgba(44, 62, 80, 0.13);
            """)
            card_layout = QVBoxLayout(card)

            title = QLabel("Manage Stores")
            title.setFont(QFont("Segoe UI", 28, QFont.Bold))
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: #2980b9;")
            card_layout.addWidget(title)
            card_layout.addSpacing(32)

            label_store = QLabel("Select Store:")
            label_store.setFont(QFont("Segoe UI", 18))
            card_layout.addWidget(label_store)

            self.store_combo = QComboBox()
            self.store_combo.setFont(QFont("Segoe UI", 16))
            self.store_combo.setStyleSheet("""
                border-radius: 10px;
                padding: 16px;
                font-size: 16px;
                background: #f0f4f7;
            """)
            card_layout.addWidget(self.store_combo)
            card_layout.addSpacing(28)

            button_layout = QHBoxLayout()
            select_btn = QPushButton("Select Store")
            select_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
            select_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2980b9;
                    color: white;
                    border-radius: 10px;
                    padding: 18px;
                }
                QPushButton:hover {
                    background-color: #3498db;
                }
            """)
            select_btn.clicked.connect(self.select_store)
            button_layout.addWidget(select_btn)

            new_store_btn = QPushButton("Add New Store")
            new_store_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
            new_store_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border-radius: 10px;
                    padding: 18px;
                }
                QPushButton:hover {
                    background-color: #2ecc71;
                }
            """)
            new_store_btn.clicked.connect(self.add_new_store)
            button_layout.addWidget(new_store_btn)
            card_layout.addLayout(button_layout)

            card_layout.addStretch()
            main_layout.addWidget(card, alignment=Qt.AlignCenter)
            main_layout.addStretch()
        except Exception as e:
            print(f"Error in setup_ui: {traceback.format_exc()}")
            QMessageBox.warning(self, "UI Error", f"Failed to set up Store Management: {e}\nCheck console for details.")

    def load_stores(self):
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("SELECT id, store_name FROM stores WHERE user_id = ?", (self.user_id,))
            stores = c.fetchall()
            self.store_combo.clear()
            if stores:
                for store_id, store_name in stores:
                    self.store_combo.addItem(store_name, store_id)
                print(f"Loaded {len(stores)} stores for user_id {self.user_id}")
            else:
                print(f"No stores found for user_id {self.user_id}")
            conn.close()
        except sqlite3.Error as e:
            print(f"Error in load_stores: {traceback.format_exc()}")
            QMessageBox.warning(self, "Database Error", f"Failed to load stores: {e}\nCheck console for details.")

    def select_store(self):
        try:
            store_id = self.store_combo.currentData()
            if store_id:
                if hasattr(self.main_window, 'store_id'):
                    self.main_window.store_id = store_id
                if hasattr(self.main_window, 'save_session'):
                    self.main_window.save_session()
                if hasattr(self.main_window, 'show_dashboard'):
                    self.main_window.show_dashboard()
                print(f"Selected store_id: {store_id}")
            else:
                QMessageBox.warning(self, "Error", "No store selected.")
        except Exception as e:
            print(f"Error in select_store: {traceback.format_exc()}")
            QMessageBox.warning(self, "Selection Error", f"Failed to select store: {e}")

    def add_new_store(self):
        try:
            if hasattr(self.main_window, 'show_store_form'):
                self.main_window.show_store_form()
            print("Navigated to Add New Store form")
        except Exception as e:
            print(f"Error in add_new_store: {traceback.format_exc()}")
            QMessageBox.warning(self, "Navigation Error", f"Failed to navigate to store form: {e}")


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = StoreManagement()  # Uses default mock main_window and user_id=1 for testing
    window.show()
    sys.exit(app.exec_())
