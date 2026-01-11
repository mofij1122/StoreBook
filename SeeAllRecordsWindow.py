import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit, QPushButton,
    QMessageBox, QHBoxLayout, QLineEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class SeeAllRecordsWindow(QWidget):
    def __init__(self, store_id=None):
        super().__init__()
        self.store_id = store_id
        self.setWindowTitle("View All Records")
        self.setGeometry(500, 200, 700, 600)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: #f0f4f7;")
        main_layout = QVBoxLayout()

        # Back button setup
        self.back_button = QPushButton("Back", self)
        self.back_button.setFont(QFont("Segoe UI", 10))
        self.back_button.setStyleSheet("background-color: #3498db; color: white; border-radius: 3px; padding: 2px 8px;")
        self.back_button.clicked.connect(self.go_back)

        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch()
        main_layout.addLayout(back_layout)

        title_label = QLabel("View All Records")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        main_layout.addWidget(title_label)

        # Module select combobox and search bar layout
        top_layout = QHBoxLayout()

        module_label = QLabel("Select Module:")
        module_label.setFont(QFont("Segoe UI", 12))
        top_layout.addWidget(module_label)

        self.module_combo = QComboBox()
        self.module_combo.addItems(["capital", "income", "expenses", "assets", "liabilities"])
        self.module_combo.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        self.module_combo.setFixedWidth(180)
        self.module_combo.currentIndexChanged.connect(self.on_filters_changed)
        top_layout.addWidget(self.module_combo)

        search_label = QLabel("Search:")
        search_label.setFont(QFont("Segoe UI", 12))
        top_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text")
        self.search_input.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 6px; font-size: 14px;")
        self.search_input.textChanged.connect(self.on_filters_changed)
        top_layout.addWidget(self.search_input)

        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # Records display
        self.records_display = QTextEdit()
        self.records_display.setReadOnly(True)
        self.records_display.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        main_layout.addWidget(QLabel("Records:"))
        main_layout.addWidget(self.records_display)

        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Entry ID:"))
        self.entry_id_input = QLineEdit()
        self.entry_id_input.setPlaceholderText("Enter Entry ID to edit/delete")
        control_layout.addWidget(self.entry_id_input)

        control_layout.addWidget(QLabel("New Amount/Value:"))
        self.amount_input = QLineEdit()
        control_layout.addWidget(self.amount_input)

        control_layout.addWidget(QLabel("New Description/Name/Category:"))
        self.description_input = QLineEdit()
        control_layout.addWidget(self.description_input)

        main_layout.addLayout(control_layout)

        btn_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Save Changes")
        self.edit_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.edit_btn.clicked.connect(self.edit_entry)
        btn_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete Entry")
        self.delete_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.delete_btn.setStyleSheet("""
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
        self.delete_btn.clicked.connect(self.delete_entry)
        btn_layout.addWidget(self.delete_btn)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self.fetch_records()

    def go_back(self):
        self.close()

    def on_filters_changed(self):
        self.fetch_records()

    def fetch_records(self):
        module = self.module_combo.currentText()
        search_text = self.search_input.text().strip()
        if not self.store_id:
            QMessageBox.warning(self, "Error", "No store selected.")
            return
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")

            table_columns = {
                "expenses": ("id, date, amount, category", ["ID", "Date", "Amount", "Category"]),
                "assets": ("id, date, asset_name, value, category", ["ID", "Date", "Asset Name", "Value", "Category"]),
                "liabilities": ("id, date, liability_name, amount, category", ["ID", "Date", "Liability Name", "Amount", "Category"]),
                "capital": ("id, date, amount, description", ["ID", "Date", "Amount", "Description"]),
                "income": ("id, date, amount, description", ["ID", "Date", "Amount", "Description"])
            }
            columns_str, headers = table_columns[module]

            # Build SQL with optional search filter on textual columns
            base_query = f"SELECT {columns_str} FROM {module} WHERE store_id=?"
            params = [self.store_id]

            # Determine which columns are searchable (date is not searched)
            search_columns = []
            if module in ("expenses"):
                search_columns = ["category"]
            elif module in ("assets"):
                search_columns = ["asset_name", "category"]
            elif module in ("liabilities"):
                search_columns = ["liability_name", "category"]
            elif module in ("capital", "income"):
                search_columns = ["description"]
            # If search text is present, construct WHERE search conditions joined by OR
            if search_text:
                search_conditions = " OR ".join([f"{col} LIKE ?" for col in search_columns])
                base_query += f" AND ({search_conditions})"
                params.extend([f"%{search_text}%"] * len(search_columns))

            c.execute(base_query, params)
            results = c.fetchall()
            conn.close()

            if not results:
                self.records_display.setText("No records found for the selected module.")
                return

            display_text = ""
            for row in results:
                for label, item in zip(headers, row):
                    display_text += f"{label}: {item if item else ''}\n"
                display_text += "-" * 30 + "\n"
            self.records_display.setFont(QFont("Segoe UI", 11))
            self.records_display.setText(display_text)

        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to fetch records: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An unexpected error occurred: {e}")

    def edit_entry(self):
        module = self.module_combo.currentText()
        entry_id = self.entry_id_input.text().strip()
        new_amount = self.amount_input.text().strip()
        new_description = self.description_input.text().strip()

        if not entry_id or not new_amount or not new_description:
            QMessageBox.warning(self, "Incomplete", "Please enter Entry ID, new amount/value, and new description/name/category.")
            return

        try:
            entry_id = int(entry_id)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Entry ID must be an integer.")
            return

        try:
            new_amount_f = float(new_amount)
            if new_amount_f < 0:
                raise ValueError("Amount cannot be negative")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid positive number for amount/value.")
            return

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")

            if module == "expenses":
                c.execute("UPDATE expenses SET amount=?, category=? WHERE id=? AND store_id=?", 
                          (new_amount_f, new_description, entry_id, self.store_id))
            elif module == "assets":
                c.execute("UPDATE assets SET value=?, asset_name=?, category=? WHERE id=? AND store_id=?", 
                          (new_amount_f, new_description, new_description, entry_id, self.store_id))
            elif module == "liabilities":
                c.execute("UPDATE liabilities SET amount=?, liability_name=?, category=? WHERE id=? AND store_id=?", 
                          (new_amount_f, new_description, new_description, entry_id, self.store_id))
            else:
                c.execute(f"UPDATE {module} SET amount=?, description=? WHERE id=? AND store_id=?", 
                          (new_amount_f, new_description, entry_id, self.store_id))

            if c.rowcount == 0:
                QMessageBox.warning(self, "Not Found", "Entry ID not found or does not belong to current store.")
            else:
                conn.commit()
                QMessageBox.information(self, "Updated", "Entry updated successfully.")
                self.fetch_records()
            conn.close()

        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to update entry: {e}")

    def delete_entry(self):
        module = self.module_combo.currentText()
        entry_id = self.entry_id_input.text().strip()

        if not entry_id:
            QMessageBox.warning(self, "Select Entry", "Please enter Entry ID to delete.")
            return

        try:
            entry_id = int(entry_id)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Entry ID must be an integer.")
            return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     "Are you sure you want to delete this entry?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute("PRAGMA foreign_keys = ON")

                c.execute(f"DELETE FROM {module} WHERE id=? AND store_id=?", (entry_id, self.store_id))
                if c.rowcount == 0:
                    QMessageBox.warning(self, "Not Found", "Entry ID not found or does not belong to current store.")
                else:
                    conn.commit()
                    QMessageBox.information(self, "Deleted", "Entry deleted successfully.")
                    self.fetch_records()
                conn.close()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"Failed to delete entry: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SeeAllRecordsWindow(store_id=1)
    window.show()
    sys.exit(app.exec_())
