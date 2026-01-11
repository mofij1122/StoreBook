import sys
import sqlite3
import json
import os
import traceback
import re


from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QDateEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate


from form import StoreDetailsForm
from dashboard import Dashboard
from income import IncomeWindow
from expenses import ExpensesWindow
from capital import CapitalWindow
from assets import AssetsWindow
from liabilities import LiabilitiesWindow
from profit_loss import ProfitLossWindow
from SeeAllRecordsWindow import SeeAllRecordsWindow
from store_management import StoreManagement
from analytics import AnalyticsWindow 



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("Initializing MainWindow")
        self.setWindowTitle("StoreBook")
        self.setGeometry(self.screen().availableGeometry().center().x() - 350, self.screen().availableGeometry().center().y() - 300, 700, 600)
        self.user_id = None
        self.store_id = None
        self.session_file = "session.json"
        self.nav_bar = None
        self.create_table_if_not_exists()
        self.load_session()
        if self.user_id:
            print("User ID found, setting up UI")
            self.load_stores()
            self.setup_ui()
        else:
            print("No user ID, showing login")
            self.show_login()
        self.activateWindow()  # Force window activation


    def create_table_if_not_exists(self):
        print("Starting database creation")
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in c.fetchall()]
            if 'birth_date' not in columns:
                print("Adding birth_date column")
                c.execute("ALTER TABLE users ADD COLUMN birth_date TEXT")


            c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                email TEXT,
                birth_date TEXT
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


            c.execute("SELECT COUNT(*) FROM users")
            if c.fetchone()[0] == 0:
                print("Initializing default admin user")
                c.execute("INSERT INTO users (username, password, email, birth_date) VALUES (?, ?, ?, ?)",
                          ("admin", "Pass12!@", "admin@example.com", "1990-01-01"))
                c.execute("INSERT INTO stores (user_id, store_name) VALUES (?, ?)", (1, "Test Store"))


            conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            print("Closing database connection")
            conn.close()


    def setup_ui(self):
        if self.store_id:
            print("Showing dashboard")
            self.show_dashboard()
        else:
            print("Showing store management")
            self.show_store_management()
        self.show()


    def load_session(self):
        print("Loading session")
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    session = json.load(f)
                    self.user_id = session.get('user_id')
                    self.store_id = session.get('store_id')
            except (json.JSONDecodeError, KeyError):
                print("Invalid session file, removing it")
                os.remove(self.session_file)


    def save_session(self):
        session = {'user_id': self.user_id, 'store_id': self.store_id}
        with open(self.session_file, 'w') as f:
            json.dump(session, f)


    def show_login(self):
        print("Showing login screen")
        self.login_widget = QWidget()
        self.setCentralWidget(self.login_widget)


        card = QWidget()
        card.setStyleSheet("""
            background: #ffffff;
            border-radius: 16px;
            padding: 32px 36px;
            box-shadow: 0px 6px 32px rgba(44, 62, 80, 0.15);
        """)


        layout = QVBoxLayout(card)


        title = QLabel("StoreBook Login")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3498db;")
        layout.addWidget(title)


        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("border-radius:7px; padding:12px; font-size:16px; background:#f0f4f7;")
        layout.addWidget(self.username_input)


        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("border-radius:7px; padding:12px; font-size:16px; background:#f0f4f7;")
        layout.addWidget(self.password_input)


        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1,y2:1, stop:0 #2980b9, stop:1 #6dd5fa);
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }
            QPushButton:hover { background: #3498db; }
        """)
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)


        links_layout = QHBoxLayout()
        forget_btn = QPushButton("Forget Password")
        forget_btn.setFont(QFont("Segoe UI", 10))
        forget_btn.setStyleSheet("background: none; color: #e67e22; border:none;")
        forget_btn.clicked.connect(self.forget_password)
        links_layout.addWidget(forget_btn)


        links_layout.addStretch()


        register_btn = QPushButton("Register")
        register_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        register_btn.setStyleSheet("background: none; color: #27ae60; border:none;")
        register_btn.clicked.connect(self.show_register)
        links_layout.addWidget(register_btn)


        layout.addLayout(links_layout)


        outer = QVBoxLayout(self.login_widget)
        outer.addStretch()
        outer.addWidget(card, alignment=Qt.AlignCenter)
        outer.addStretch()


        self.login_widget.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e0eafc, stop:1 #cfdef3);")
        self.show()


    def login(self):
        print("Attempting login")
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()


        if not username or not password:
            QMessageBox.warning(self, "Incomplete", "Please enter username and password.")
            return


        if not re.match(r"^[a-zA-Z0-9]{4,}$", username):
            QMessageBox.warning(self, "Invalid", "Username must be at least 4 alphanumeric characters.")
            return


        if not re.match(r"^(?=.*[A-Z])(?=.*\d.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{5,}$", password):
            QMessageBox.warning(self, "Invalid", "Password must be at least 5 characters with 1 uppercase, 2 numbers, and 1 special character.")
            return


        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")
            c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
            user = c.fetchone()
            if user:
                self.user_id = user[0]
                c.execute("SELECT id FROM stores WHERE user_id = ?", (self.user_id,))
                store = c.fetchone()
                if store:
                    self.store_id = store[0]
                    self.save_session()
                    self.setup_ui()
                else:
                    QMessageBox.warning(self, "Error", "No store associated with this user. Please add a store.")
                    self.show_store_management()
            else:
                QMessageBox.warning(self, "Error", "Invalid username or password.")
            conn.close()
        except sqlite3.Error as e:
            print(f"Login error - Stack trace: {traceback.format_exc()}")
            QMessageBox.warning(self, "Database Error", f"Login failed: {e}\nCheck console for details.")


    def forget_password(self):
        print("Initiating forget password")
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Incomplete", "Please enter your username.")
            return

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")
            c.execute("SELECT email, birth_date FROM users WHERE username = ?", (username,))
            user_data = c.fetchone()
            if user_data:
                email, birth_date = user_data
                self.show_verify_birth_date(username, email, birth_date)
            else:
                QMessageBox.warning(self, "Error", "Username not found.")
            conn.close()
        except sqlite3.Error as e:
            print(f"Password reset error - Stack trace: {traceback.format_exc()}")
            QMessageBox.warning(self, "Database Error", f"Password reset failed: {e}\nCheck console for details.")


    def show_verify_birth_date(self, username, email, stored_birth_date):
        print("Showing verify birth date screen")

        self.verify_widget = QWidget()
        self.setCentralWidget(self.verify_widget)

        # Outer layout with background and centering like login page
        outer = QVBoxLayout(self.verify_widget)
        outer.addStretch()

        card = QWidget()
        card.setStyleSheet("""
            background: #ffffff;
            border-radius: 16px;
            padding: 32px 36px;
            box-shadow: 0px 6px 32px rgba(44, 62, 80, 0.15);
        """)

        layout = QVBoxLayout(card)

        title = QLabel("Verify Birth Date")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3498db;")
        layout.addWidget(title)

        info = QLabel(f"Enter your birth date for {username} (Email: {email})")
        info.setFont(QFont("Segoe UI", 14))
        layout.addWidget(info)

        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDisplayFormat("yyyy-MM-dd")
        self.birth_date_input.setStyleSheet(
            "border-radius:7px; padding:12px; font-size:16px; background:#f0f4f7; color:#3498db;"
        )
        birth_date_label = QLabel("Birth Date:")
        birth_date_label.setFont(QFont("Segoe UI", 16, QFont.Bold))  
        layout.addWidget(birth_date_label)
        layout.addWidget(self.birth_date_input)


        verify_btn = QPushButton("Verify and Reset")
        verify_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        verify_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1,y2:1, stop:0 #2980b9, stop:1 #6dd5fa);
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover { background: #3498db; }
        """)
        verify_btn.clicked.connect(lambda: self.verify_and_reset_password(username, stored_birth_date))
        layout.addWidget(verify_btn)

        back_btn = QPushButton("Back to Login")
        back_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        back_btn.setStyleSheet("""
            QPushButton {
                background: #c0392b;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover { background: #e74c3c; }
        """)
        back_btn.clicked.connect(self.show_login)
        layout.addWidget(back_btn)

        outer.addWidget(card, alignment=Qt.AlignCenter)
        outer.addStretch()

        self.verify_widget.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e0eafc, stop:1 #cfdef3);")
        self.show()


    def verify_and_reset_password(self, username, stored_birth_date):
        print("Verifying birth date and resetting password")
        entered_birth_date = self.birth_date_input.date().toString("yyyy-MM-dd")
        if entered_birth_date != stored_birth_date:
            QMessageBox.warning(self, "Error", "Incorrect birth date. Please try again.")
            return
        self.show_reset_password(username)


    def show_reset_password(self, username):
        print("Showing reset password screen")
        self.reset_widget = QWidget()
        self.setCentralWidget(self.reset_widget)
        layout = QVBoxLayout()
        title = QLabel("Reset Password")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        info = QLabel(f"Enter new password for {username}")
        info.setFont(QFont("Segoe UI", 12))
        layout.addWidget(info)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 14px;")
        layout.addWidget(QLabel("New Password:"))
        layout.addWidget(self.new_password_input)
        reset_btn = QPushButton("Reset Password")
        reset_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        reset_btn.setStyleSheet("background-color: #27ae60; color: white; border-radius: 5px; padding: 8px;")
        reset_btn.clicked.connect(lambda: self.reset_password(username))
        layout.addWidget(reset_btn)
        back_btn = QPushButton("Back to Login")
        back_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        back_btn.setStyleSheet("background-color: #c0392b; color: white; border-radius: 5px; padding: 8px;")
        back_btn.clicked.connect(self.show_login)
        layout.addWidget(back_btn)
        self.reset_widget.setLayout(layout)
        self.reset_widget.setStyleSheet("background-color: #f0f4f7;")
        self.show()


    def reset_password(self, username):
        print("Attempting password reset")
        new_password = self.new_password_input.text().strip()
        if not new_password:
            QMessageBox.warning(self, "Incomplete", "Please enter a new password.")
            return
        if not re.match(r"^(?=.*[A-Z])(?=.*\d.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{5,}$", new_password):
            QMessageBox.warning(self, "Invalid", "Password must be at least 5 characters with 1 uppercase, 2 numbers, and 1 special character.")
            return
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")
            c.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
            if c.rowcount > 0:
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", f"Password reset successfully for {username}. You can now log in.")
                self.show_login()
            else:
                QMessageBox.warning(self, "Error", "Failed to reset password.")
        except sqlite3.Error as e:
            print(f"Password reset error - Stack trace: {traceback.format_exc()}")
            QMessageBox.warning(self, "Database Error", f"Password reset failed: {e}\nCheck console for details.")


    def show_register(self):
        print("Showing registration screen")
        self.register_widget = QWidget()
        self.setCentralWidget(self.register_widget)


        card = QWidget()
        card.setStyleSheet("""
            background: #ffffff;
            border-radius: 18px;
            padding: 32px 36px;
            box-shadow: 0px 9px 32px rgba(44, 62, 80, 0.25);
        """)


        layout = QVBoxLayout(card)


        title = QLabel("Create Your Account")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #27ae60;")
        layout.addWidget(title)


        self.reg_username_input = QLineEdit()
        self.reg_username_input.setPlaceholderText("Choose a Username")
        self.reg_username_input.setStyleSheet("border-radius:7px; padding:12px; font-size:16px; background:#f0f4f7;")
        layout.addWidget(self.reg_username_input)


        self.reg_password_input = QLineEdit()
        self.reg_password_input.setPlaceholderText("Choose a Password")
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_password_input.setStyleSheet("border-radius:7px; padding:12px; font-size:16px; background:#f0f4f7;")
        layout.addWidget(self.reg_password_input)


        self.reg_email_input = QLineEdit()
        self.reg_email_input.setPlaceholderText("Email Address")
        self.reg_email_input.setStyleSheet("border-radius:7px; padding:12px; font-size:16px; background:#f0f4f7;")
        layout.addWidget(self.reg_email_input)


        self.reg_birth_date_input = QDateEdit()
        self.reg_birth_date_input.setCalendarPopup(True)
        self.reg_birth_date_input.setDisplayFormat("yyyy-MM-dd")
        self.reg_birth_date_input.setStyleSheet("border-radius:7px; padding:12px; font-size:16px; background:#f0f4f7; color: #3498db;")
        layout.addWidget(self.reg_birth_date_input)


        register_btn = QPushButton("Register")
        register_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        register_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1,y2:1, stop:0 #27ae60, stop:1 #6dd5fa);
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover { background: #2ecc71; }
        """)
        register_btn.clicked.connect(self.register)
        layout.addWidget(register_btn)


        back_btn = QPushButton("Back to Login")
        back_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        back_btn.setStyleSheet("background: none; color: #c0392b; border:none;")
        back_btn.clicked.connect(self.show_login)
        layout.addWidget(back_btn)


        outer = QVBoxLayout(self.register_widget)
        outer.addStretch()
        outer.addWidget(card, alignment=Qt.AlignCenter)
        outer.addStretch()


        self.register_widget.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e0eafc, stop:1 #cfdef3);")
        self.show()


    def register(self):
        print("Attempting registration")
        username = self.reg_username_input.text().strip()
        password = self.reg_password_input.text().strip()
        email = self.reg_email_input.text().strip()
        birth_date = self.reg_birth_date_input.date().toString("yyyy-MM-dd")


        if not username or not password or not email or not birth_date:
            QMessageBox.warning(self, "Incomplete", "Please fill all fields.")
            return


        if not re.match(r"^[a-zA-Z0-9]{4,}$", username):
            QMessageBox.warning(self, "Invalid", "Username must be at least 4 alphanumeric characters.")
            return


        if not re.match(r"^(?=.*[A-Z])(?=.*\d.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{5,}$", password):
            QMessageBox.warning(self, "Invalid", "Password must be at least 5 characters with 1 uppercase, 2 numbers, and 1 special character.")
            return


        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")
            c.execute("INSERT INTO users (username, password, email, birth_date) VALUES (?, ?, ?, ?)", (username, password, email, birth_date))
            self.user_id = c.lastrowid
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "User registered successfully!")
            self.save_session()
            self.show_store_management()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists.")
        except sqlite3.Error as e:
            print(f"Registration error - Stack trace: {traceback.format_exc()}")
            QMessageBox.warning(self, "Error", f"Database error: {e}\nCheck console for details.")


    def show_store_management(self):
        print("Showing store management")
        self.store_management = StoreManagement(main_window=self, user_id=self.user_id)
        self.setCentralWidget(self.store_management)


    def show_store_form(self, user_id=None):
        self.store_form = StoreDetailsForm(main_window=self, user_id=user_id or self.user_id)
        self.setCentralWidget(self.store_form)


    def show_dashboard(self, store_id=None):
        print("Showing dashboard")
        if store_id:
            self.store_id = store_id
            self.save_session()


        self.dashboard = Dashboard(main_window=self, store_id=self.store_id)
        self.dashboard.data_updated.connect(self.trigger_dashboard_update)
        self.setCentralWidget(self.dashboard)


    def load_stores(self):
        print("Loading stores")
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("SELECT id FROM stores WHERE user_id = ?", (self.user_id,))
            stores = c.fetchall()
            if stores and not self.store_id:
                self.store_id = stores[0][0]
            conn.close()
        except sqlite3.Error as e:
            print(f"Error loading stores: {e}")


    def logout(self):
        print("Logging out")
        self.user_id = None
        self.store_id = None
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
        self.nav_bar = None
        self.setMenuWidget(None)
        self.show_login()


    def show_income(self, store_id=None):
        self.income_window = IncomeWindow(store_id=store_id or self.store_id)
        self.income_window.show()
        self.income_window.destroyed.connect(self.trigger_dashboard_update)


    def show_expenses(self, store_id=None):
        self.expenses_window = ExpensesWindow(store_id=store_id or self.store_id)
        self.expenses_window.show()
        self.expenses_window.destroyed.connect(self.trigger_dashboard_update)


    def show_capital(self, store_id=None):
        self.capital_window = CapitalWindow(store_id=store_id or self.store_id)
        self.capital_window.show()
        self.capital_window.destroyed.connect(self.trigger_dashboard_update)


    def show_assets(self, store_id=None):
        self.assets_window = AssetsWindow(store_id=store_id or self.store_id)
        self.assets_window.show()
        self.assets_window.destroyed.connect(self.trigger_dashboard_update)


    def show_liabilities(self, store_id=None):
        self.liabilities_window = LiabilitiesWindow(store_id=store_id or self.store_id)
        self.liabilities_window.show()
        self.liabilities_window.destroyed.connect(self.trigger_dashboard_update)


    def show_profit_loss(self, store_id=None):
        self.profit_loss_window = ProfitLossWindow(store_id=store_id or self.store_id)
        self.profit_loss_window.show()


    def show_reports(self, store_id=None):
        self.edit_entry_window = SeeAllRecordsWindow(store_id=store_id or self.store_id)
        self.edit_entry_window.show()
        self.edit_entry_window.destroyed.connect(self.trigger_dashboard_update)


    def show_records(self, store_id=None):
        self.records_window = SeeAllRecordsWindow(store_id=store_id or self.store_id)
        self.records_window.show()
        self.records_window.destroyed.connect(self.trigger_dashboard_update)


    def show_analytics(self, store_id=None):
        self.analytics_window = AnalyticsWindow(store_id=store_id or self.store_id)
        self.analytics_window.show()
        self.analytics_window.destroyed.connect(self.trigger_dashboard_update)


    def trigger_dashboard_update(self):
        if hasattr(self, 'dashboard') and self.dashboard:
            self.dashboard.refresh_dashboard()



if __name__ == '__main__':
    print("Starting application")
    app = QApplication(sys.argv)
    window = MainWindow()
    print("Showing main window")
    window.show()
    print("Starting event loop")
    sys.exit(app.exec_())
