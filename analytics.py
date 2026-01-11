import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont, QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis, QPieSeries


class AnalyticsWindow(QWidget):
    def __init__(self, store_id=None):
        super().__init__()
        self.store_id = store_id
        self.setWindowTitle("Analytics")
        self.setGeometry(500, 200, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: #f0f4f7;")
        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- Add Back Button ---
        header_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        back_btn.setFixedWidth(100)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        title = QLabel("Financial Analytics")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Pie chart section
        self.pie_chart_view = QChartView()
        self.pie_chart_view.setRenderHint(QPainter.Antialiasing)
        self.pie_chart_view.setMinimumHeight(300)
        layout.addWidget(self.pie_chart_view)

        # Bar chart section
        self.bar_chart_view = QChartView()
        self.bar_chart_view.setRenderHint(QPainter.Antialiasing)
        self.bar_chart_view.setMinimumHeight(300)
        layout.addWidget(self.bar_chart_view)

        # Refresh Button
        refresh_btn = QPushButton("Refresh Analytics")
        refresh_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.load_analytics)
        layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)

        self.load_analytics()

    def go_back(self):
        self.close()

    def load_analytics(self):
        if not self.store_id:
            QMessageBox.warning(self, "Error", "No store selected.")
            return

        try:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()

            # Pie Chart Data: Summary of totals
            c.execute("SELECT SUM(amount) FROM income WHERE store_id=?", (self.store_id,))
            income = c.fetchone()[0] or 0
            c.execute("SELECT SUM(amount) FROM expenses WHERE store_id=?", (self.store_id,))
            expenses = c.fetchone()[0] or 0
            c.execute("SELECT SUM(value) FROM assets WHERE store_id=?", (self.store_id,))
            assets = c.fetchone()[0] or 0
            c.execute("SELECT SUM(amount) FROM liabilities WHERE store_id=?", (self.store_id,))
            liabilities = c.fetchone()[0] or 0

            pie_series = QPieSeries()
            if income > 0:
                pie_series.append("Income", income)
            if expenses > 0:
                pie_series.append("Expenses", expenses)
            if assets > 0:
                pie_series.append("Assets", assets)
            if liabilities > 0:
                pie_series.append("Liabilities", liabilities)

            pie_chart = QChart()
            pie_chart.addSeries(pie_series)
            pie_chart.setTitle("Financial Summary")
            pie_chart.legend().setAlignment(Qt.AlignBottom)
            self.pie_chart_view.setChart(pie_chart)

            # Bar Chart: Monthly income and expenses for past 6 months
            import datetime
            from dateutil.relativedelta import relativedelta
            today = datetime.date.today()
            categories = []
            income_set = QBarSet("Income")
            expenses_set = QBarSet("Expenses")

            for i in range(5, -1, -1):
                month = today - relativedelta(months=i)
                categories.append(month.strftime("%b %Y"))
                month_start = month.replace(day=1).strftime("%Y-%m-%d")
                next_month = month + relativedelta(months=1)
                month_end = next_month.replace(day=1).strftime("%Y-%m-%d")

                c.execute("SELECT SUM(amount) FROM income WHERE store_id=? AND date >= ? AND date < ?",
                          (self.store_id, month_start, month_end))
                monthly_income = c.fetchone()[0] or 0
                income_set.append(monthly_income)

                c.execute("SELECT SUM(amount) FROM expenses WHERE store_id=? AND date >= ? AND date < ?",
                          (self.store_id, month_start, month_end))
                monthly_expenses = c.fetchone()[0] or 0
                expenses_set.append(monthly_expenses)

            bar_series = QBarSeries()
            bar_series.append(income_set)
            bar_series.append(expenses_set)

            bar_chart = QChart()
            bar_chart.addSeries(bar_series)
            bar_chart.setTitle("Monthly Income vs Expenses (Last 6 Months)")
            bar_chart.setAnimationOptions(QChart.SeriesAnimations)

            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            bar_chart.addAxis(axis_x, Qt.AlignBottom)
            bar_series.attachAxis(axis_x)

            axis_y = QValueAxis()
            axis_y.setRange(0, max(max(income_set), max(expenses_set), 1000))
            bar_chart.addAxis(axis_y, Qt.AlignLeft)
            bar_series.attachAxis(axis_y)

            bar_chart.legend().setVisible(True)
            bar_chart.legend().setAlignment(Qt.AlignBottom)

            self.bar_chart_view.setChart(bar_chart)
            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed loading analytics: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AnalyticsWindow(store_id=1)
    window.show()
    sys.exit(app.exec_())
