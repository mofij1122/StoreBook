import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QComboBox, QMessageBox, QGroupBox, QFrame
)
from PyQt5.QtGui import QFont, QPainter, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtChart import QChart, QChartView, QPieSeries


class Dashboard(QWidget):
    data_updated = pyqtSignal()

    def __init__(self, main_window=None, store_id=None):
        super().__init__()
        self.main_window = main_window
        self.store_id = store_id if store_id is not None else 0
        self.setWindowTitle("Dashboard")
        self.setGeometry(500, 200, 950, 650)
        self.setup_ui()
        if self.main_window:
            self.data_updated.connect(self.refresh_dashboard)

    def setup_ui(self):
        self.setStyleSheet("background-color: #ecf0f1;")
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Store switcher layout
        store_layout = QHBoxLayout()
        store_label = QLabel("Store:")
        store_label.setFont(QFont("Segoe UI", 12))
        store_layout.addWidget(store_label)

        self.store_combo = QComboBox()
        self.store_combo.setFixedWidth(250)
        self.store_combo.setStyleSheet(
            "border: 1px solid #bdc3c7; border-radius: 5px; padding: 4px; font-size: 12px;"
        )
        store_layout.addWidget(self.store_combo)
        self.store_combo.currentIndexChanged.connect(self.store_changed)

        manage_store_btn = QPushButton("Manage Stores")
        manage_store_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        manage_store_btn.setStyleSheet(
            "background-color: #2980b9; color: white; border-radius: 5px; padding: 6px 12px;"
        )
        manage_store_btn.clicked.connect(self.show_store_management)
        store_layout.addWidget(manage_store_btn)

        store_layout.addStretch()

        logout_btn = QPushButton("Logout")
        logout_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logout_btn.setFixedSize(130, 48)
        logout_btn.setStyleSheet("""
            background-color: #ec7063;
            color: white;
            border-radius: 10px;
            padding: 15px 30px;
            font-size: 18px;
        """)
        logout_btn.clicked.connect(self.main_window.logout if self.main_window else self.logout_placeholder)
        store_layout.addWidget(logout_btn)

        main_layout.addLayout(store_layout)

        # Navigation buttons layout with lighter colors
        nav_layout = QHBoxLayout()
        buttons = [
            ("Capital", self.open_capital, "#82e0aa"),
            ("Income", self.open_income, "#85c1e9"),
            ("Expenses", self.open_expenses, "#f7a39f"),
            ("Assets", self.open_assets, "#aed6f1"),
            ("Liabilities", self.open_liabilities, "#c2a9e9"),
            ("Profit/Loss", self.open_profit_loss, "#a9cce3"),
            ("View All Records", self.open_see_all_records, "#f7d9a6"),
            ("Analytics", self.open_analytics, "#f9e79f"),
        ]
        for text, callback, color in buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: black;
                    border-radius: 6px;
                    padding: 10px 18px;
                    margin-right: 8px;
                }}
                QPushButton:hover {{
                    background-color: {self.lighten_color(color)};
                    color: black;
                }}
            """)
            btn.clicked.connect(callback)
            nav_layout.addWidget(btn)
        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumWidth(480)
        content_layout.addWidget(self.chart_view)

        self.legend_group = QGroupBox("Legend")
        self.legend_group.setFixedWidth(200)
        self.legend_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        self.legend_layout = QVBoxLayout()
        self.legend_group.setLayout(self.legend_layout)
        content_layout.addWidget(self.legend_group)

        content_layout.addSpacing(10)

        right_layout = QVBoxLayout()

        latest_label = QLabel("Latest Entries")
        latest_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        right_layout.addWidget(latest_label)

        self.latest_text = QLabel("No entries found.")
        self.latest_text.setFont(QFont("Segoe UI", 12))
        self.latest_text.setWordWrap(True)
        self.latest_text.setStyleSheet(
            "background-color: white; border: 1px solid #bdc3c7; border-radius: 6px; padding: 12px;"
        )
        self.latest_text.setMinimumWidth(320)
        right_layout.addWidget(self.latest_text)

        self.profit_loss_label = QLabel("")
        self.profit_loss_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.profit_loss_label.setAlignment(Qt.AlignCenter)
        self.profit_loss_label.setFixedHeight(60)
        self.profit_loss_label.setStyleSheet("border-radius: 6px; color: white;")
        right_layout.addWidget(self.profit_loss_label)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        refresh_btn.setStyleSheet("background-color: #2980b9; color: white; border-radius: 6px; padding: 10px;")
        refresh_btn.clicked.connect(self.refresh_dashboard)
        right_layout.addWidget(refresh_btn)

        right_layout.addStretch()
        content_layout.addLayout(right_layout)

        self.load_store_options()
        self.refresh_dashboard()

    def logout_placeholder(self):
        QMessageBox.information(self, "Logout", "Logout clicked but no main window available.")

    def lighten_color(self, hex_color):
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, c + 40) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def load_store_options(self):
        if not self.main_window or not hasattr(self.main_window, "user_id"):
            return
        try:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("SELECT id, store_name FROM stores WHERE user_id=?", (self.main_window.user_id,))
            stores = c.fetchall()
            self.store_combo.clear()
            self.store_combo.addItem("All Stores", 0)
            for sid, sname in stores:
                self.store_combo.addItem(sname, sid)
            if self.store_id == 0:
                self.store_combo.setCurrentIndex(0)
            else:
                for i in range(self.store_combo.count()):
                    if self.store_combo.itemData(i) == self.store_id:
                        self.store_combo.setCurrentIndex(i)
                        break
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to load stores: {e}")

    def update_legend(self, series):
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for slice in series.slices():
            color = slice.color()
            label = slice.label()
            hlayout = QHBoxLayout()
            colorbox = QFrame()
            colorbox.setFixedSize(20, 20)
            colorbox.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            hlayout.addWidget(colorbox)
            labelwidget = QLabel(label)
            labelwidget.setFont(QFont("Segoe UI", 11))
            hlayout.addWidget(labelwidget)
            hlayout.addStretch()
            container = QWidget()
            container.setLayout(hlayout)
            self.legend_layout.addWidget(container)

    def store_changed(self, index):
        sid = self.store_combo.itemData(index)
        if sid != self.store_id:
            self.store_id = sid
            if self.main_window:
                self.main_window.store_id = sid
                self.main_window.save_session()
            self.refresh_dashboard()

    def show_store_management(self):
        if self.main_window and hasattr(self.main_window, "show_store_management"):
            self.main_window.show_store_management()
        else:
            QMessageBox.warning(self, "Error", "Store management not available.")

    def refresh_dashboard(self):
        if self.store_id is None:
            self.latest_text.setText("No store selected.")
            self.chart_view.setChart(QChart())
            self.profit_loss_label.setText("")
            while self.legend_layout.count():
                item = self.legend_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            return

        try:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()

            if self.store_id == 0:
                c.execute("SELECT id FROM stores WHERE user_id=?", (self.main_window.user_id,))
                store_ids = [str(row[0]) for row in c.fetchall()]
                if not store_ids:
                    store_ids = ["-1"]
                store_filter = f"store_id IN ({','.join(store_ids)})"
            else:
                store_filter = "store_id = ?"

            # Fetch store name for chart title
            store_name = "All Stores"
            if self.store_id != 0:
                c.execute("SELECT store_name FROM stores WHERE id=?", (self.store_id,))
                row = c.fetchone()
                if row:
                    store_name = row[0]

            series = QPieSeries()

            if self.store_id == 0:
                c.execute(f"SELECT SUM(amount) FROM income WHERE {store_filter}")
                income_sum = c.fetchone()[0] or 0
                c.execute(f"SELECT SUM(amount) FROM expenses WHERE {store_filter}")
                expense_sum = c.fetchone()[0] or 0
            else:
                c.execute("SELECT SUM(amount) FROM income WHERE store_id=?", (self.store_id,))
                income_sum = c.fetchone()[0] or 0
                c.execute("SELECT SUM(amount) FROM expenses WHERE store_id=?", (self.store_id,))
                expense_sum = c.fetchone()[0] or 0

            # Pie chart colors (unique)
            # Income: Blue; Expenses: Orange; Assets varying blues; Liabilities varying purples
            if income_sum > 0:
                slice = series.append("Income", income_sum)
                slice.setColor(QColor("#2980b9"))  # Blue
            if expense_sum > 0:
                slice = series.append("Expenses", expense_sum)
                slice.setColor(QColor("#f39c12"))  # Orange

            color_palette = [
                "#3498db", "#5dade2", "#85c1e9", "#aed6f1",
                "#af7ac5", "#bb8fce", "#d2b4de", "#e8daef"
            ]
            palette_index = 0

            if self.store_id == 0:
                c.execute(f"SELECT category, SUM(value) FROM assets WHERE {store_filter} GROUP BY category")
            else:
                c.execute("SELECT category, SUM(value) FROM assets WHERE store_id=? GROUP BY category", (self.store_id,))
            rows = c.fetchall()
            for category, value in rows:
                if value > 0:
                    color = QColor(color_palette[palette_index % len(color_palette)])
                    palette_index += 1
                    slice = series.append(f"{category or 'None'}", value)
                    slice.setColor(color)

            if self.store_id == 0:
                c.execute(f"SELECT category, SUM(amount) FROM liabilities WHERE {store_filter} GROUP BY category")
            else:
                c.execute("SELECT category, SUM(amount) FROM liabilities WHERE store_id=? GROUP BY category", (self.store_id,))
            rows = c.fetchall()
            for category, amount in rows:
                if amount > 0:
                    color = QColor(color_palette[palette_index % len(color_palette)])
                    palette_index += 1
                    slice = series.append(f"{category or 'None'}", amount)
                    slice.setColor(color)

            chart = QChart()
            chart.addSeries(series)

            # Set chart title with store name
            chart.setTitle(f"Financial Summary - {store_name}")

            title_font = QFont()
            title_font.setPointSize(20)
            label_font = QFont()
            label_font.setPointSize(12)

            chart.setTitleFont(title_font)
            chart.legend().hide()
            for slice in series.slices():
                slice.setLabelFont(label_font)
                slice.setLabelVisible(True)

            self.chart_view.setChart(chart)
            self.update_legend(series)

            if self.store_id == 0:
                c.execute(f"""
                    SELECT 'Income', date, amount, description FROM income WHERE {store_filter}
                    UNION ALL
                    SELECT 'Expenses', date, amount, category FROM expenses WHERE {store_filter}
                    UNION ALL
                    SELECT 'Capital', date, amount, description FROM capital WHERE {store_filter}
                    UNION ALL
                    SELECT 'Assets', date, value, asset_name FROM assets WHERE {store_filter}
                    UNION ALL
                    SELECT 'Liabilities', date, amount, liability_name FROM liabilities WHERE {store_filter}
                    ORDER BY date DESC
                    LIMIT 3
                """)
            else:
                c.execute("""
                    SELECT 'Income', date, amount, description FROM income WHERE store_id=?
                    UNION ALL
                    SELECT 'Expenses', date, amount, category FROM expenses WHERE store_id=?
                    UNION ALL
                    SELECT 'Capital', date, amount, description FROM capital WHERE store_id=?
                    UNION ALL
                    SELECT 'Assets', date, value, asset_name FROM assets WHERE store_id=?
                    UNION ALL
                    SELECT 'Liabilities', date, amount, liability_name FROM liabilities WHERE store_id=?
                    ORDER BY date DESC
                    LIMIT 3
                """, (self.store_id, self.store_id, self.store_id, self.store_id, self.store_id))
            rows = c.fetchall()

            if rows:
                text = ""
                for module, dt, val, desc in rows:
                    text += f"<b>Entry:</b> {module}<br><b>Date:</b> {dt}<br><b>Amount/Value:</b> ₹{val}<br><b>Description:</b> {desc}<br><hr>"
                self.latest_text.setText(text)
            else:
                self.latest_text.setText("No entries found.")

            if self.store_id == 0:
                c.execute(f"SELECT SUM(amount) FROM income WHERE {store_filter}")
                total_income = c.fetchone()[0] or 0
                c.execute(f"SELECT SUM(amount) FROM expenses WHERE {store_filter}")
                total_expenses = c.fetchone()[0] or 0
            else:
                c.execute("SELECT SUM(amount) FROM income WHERE store_id=?", (self.store_id,))
                total_income = c.fetchone()[0] or 0
                c.execute("SELECT SUM(amount) FROM expenses WHERE store_id=?", (self.store_id,))
                total_expenses = c.fetchone()[0] or 0

            net_profit = total_income - total_expenses

            if net_profit > 0:
                self.profit_loss_label.setText(f"Profit: ₹{net_profit:.2f}")
                self.profit_loss_label.setStyleSheet("background-color: #27ae60; color: white; border-radius: 6px; padding: 10px;")
            elif net_profit < 0:
                self.profit_loss_label.setText(f"Loss: ₹{abs(net_profit):.2f}")
                self.profit_loss_label.setStyleSheet("background-color: #c0392b; color: white; border-radius: 6px; padding: 10px;")
            else:
                self.profit_loss_label.setText("Break-even")
                self.profit_loss_label.setStyleSheet("background-color: gray; color: white; padding: 10px; border-radius: 6px;")

            conn.close()

        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh dashboard: {e}")

    def open_capital(self):
        if self.main_window:
            self.main_window.show_capital(store_id=self.store_id)
        else:
            QMessageBox.information(self, "Info", "Capital module clicked.")

    def open_income(self):
        if self.main_window:
            self.main_window.show_income(store_id=self.store_id)
        else:
            QMessageBox.information(self, "Info", "Income module clicked.")

    def open_expenses(self):
        if self.main_window:
            self.main_window.show_expenses(store_id=self.store_id)
        else:
            QMessageBox.information(self, "Info", "Expenses module clicked.")

    def open_assets(self):
        if self.main_window:
            self.main_window.show_assets(store_id=self.store_id)
        else:
            QMessageBox.information(self, "Info", "Assets module clicked.")

    def open_liabilities(self):
        if self.main_window:
            self.main_window.show_liabilities(store_id=self.store_id)
        else:
            QMessageBox.information(self, "Info", "Liabilities module clicked.")

    def open_profit_loss(self):
        if self.main_window:
            self.main_window.show_profit_loss(store_id=self.store_id)
        else:
            QMessageBox.information(self, "Info", "Profit/Loss module clicked.")

    def open_see_all_records(self):
        if self.main_window:
            self.main_window.show_records(store_id=self.store_id)
        else:
            QMessageBox.information(self, "Info", "View All Records clicked.")

    def open_analytics(self):
        if self.main_window:
            self.main_window.show_analytics(store_id=self.store_id)
        else:
            QMessageBox.information(self, "Info", "Analytics module clicked.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard(store_id=0)
    window.show()
    sys.exit(app.exec_())
