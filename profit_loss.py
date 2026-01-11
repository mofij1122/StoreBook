import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QFont

class ProfitLossWindow(QWidget):
    def __init__(self, store_id=None):
        super().__init__()
        self.store_id = store_id
        self.setWindowTitle("Profit/Loss")
        self.setGeometry(500, 200, 500, 500)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: #f0f4f7;")

        # Back button
        self.back_button = QPushButton("Back", self)
        self.back_button.setFont(QFont("Segoe UI", 10))
        self.back_button.setStyleSheet("background-color: #3498db; color: white; border-radius: 3px; padding: 2px 8px;")
        self.back_button.move(10, 10)
        self.back_button.resize(70, 30)
        self.back_button.clicked.connect(self.go_back)

        self.title_label = QLabel("Profit/Loss Report", self)
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.title_label.move(170, 20)

        self.result_label = QLabel("", self)
        self.result_label.setFont(QFont("Segoe UI", 10))
        self.result_label.move(50, 80)
        self.result_label.resize(400, 200)

        self.calculate_button = QPushButton("Calculate", self)
        self.calculate_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.calculate_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.calculate_button.move(200, 300)
        self.calculate_button.resize(100, 35)
        self.calculate_button.clicked.connect(self.calculate_profit_loss)

        self.export_button = QPushButton("Export", self)
        self.export_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.export_button.setStyleSheet("""
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
        self.export_button.move(200, 350)
        self.export_button.resize(100, 35)
        self.export_button.clicked.connect(self.export_report)

    def go_back(self):
        self.close()  # Close the current window, returning to Dashboard

    def calculate_profit_loss(self):
        if not self.store_id:
            QMessageBox.warning(self, "Error", "No store selected.")
            return

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")

            c.execute("SELECT SUM(amount) FROM capital WHERE store_id = ?", (self.store_id,))
            total_capital = c.fetchone()[0] or 0

            c.execute("SELECT SUM(amount) FROM income WHERE store_id = ?", (self.store_id,))
            total_income = c.fetchone()[0] or 0

            c.execute("SELECT SUM(amount) FROM expenses WHERE store_id = ?", (self.store_id,))
            total_expenses = c.fetchone()[0] or 0

            c.execute("SELECT SUM(amount) FROM liabilities WHERE store_id = ?", (self.store_id,))
            total_liabilities = c.fetchone()[0] or 0

            c.execute("SELECT SUM(value) FROM assets WHERE store_id = ?", (self.store_id,))
            total_assets = c.fetchone()[0] or 0

            net_balance = total_income - total_expenses

            report_text = f"""
    Total Capital: ₹{total_capital:.2f}
    Total Income: ₹{total_income:.2f}
    Total Expenses: ₹{total_expenses:.2f}
    Total Liabilities: ₹{total_liabilities:.2f}
    Total Assets Value: ₹{total_assets:.2f}
    -----------------------------
    Net Balance (Profit/Loss): ₹{net_balance:.2f}
    """

            self.result_label.setText(report_text)
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to calculate profit/loss: {e}")

    def export_report(self):
        if not self.store_id:
            QMessageBox.warning(self, "Error", "No store selected.")
            return

        try:
            import csv
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")

            c.execute("SELECT date, amount, description FROM capital WHERE store_id = ?", (self.store_id,))
            capital_data = c.fetchall()

            c.execute("SELECT date, amount, description FROM income WHERE store_id = ?", (self.store_id,))
            income_data = c.fetchall()

            c.execute("SELECT date, amount, category FROM expenses WHERE store_id = ?", (self.store_id,))
            expenses_data = c.fetchall()

            c.execute("SELECT date, amount, description FROM liabilities WHERE store_id = ?", (self.store_id,))
            liabilities_data = c.fetchall()

            c.execute("SELECT date, value, description FROM assets WHERE store_id = ?", (self.store_id,))
            assets_data = c.fetchall()

            conn.close()

            with open('financial_report.csv', 'w', newline='') as f:
                writer = csv.writer(f)

                writer.writerow(["Capital"])
                writer.writerow(["Date", "Amount", "Description"])
                writer.writerows(capital_data)
                writer.writerow([])

                writer.writerow(["Income"])
                writer.writerow(["Date", "Amount", "Description"])
                writer.writerows(income_data)
                writer.writerow([])

                writer.writerow(["Expenses"])
                writer.writerow(["Date", "Amount", "Category"])
                writer.writerows(expenses_data)
                writer.writerow([])

                writer.writerow(["Liabilities"])
                writer.writerow(["Date", "Amount", "Description"])
                writer.writerows(liabilities_data)
                writer.writerow([])

                writer.writerow(["Assets"])
                writer.writerow(["Date", "Value", "Description"])
                writer.writerows(assets_data)

            QMessageBox.information(self, "Success", "Report exported as financial_report.csv")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export report: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProfitLossWindow(store_id=1)
    window.show()
    sys.exit(app.exec_())