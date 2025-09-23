import json
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from .auth import AuthManager

LAST_LOGIN_FILE = os.path.join(os.path.dirname(__file__), 'last_login.json')

class LoginForm(QWidget):
    def __init__(self, on_login=None, parent=None):
        super().__init__(parent)
        self.on_login = on_login
        self.setWindowTitle("User Login")
        self.layout = QVBoxLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(QLabel("Email:"))
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(QLabel("Password:"))
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.setLayout(self.layout)

        self.load_last_email()

    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Missing Field", "Email and password are required.")
            return
        success, user_or_msg = AuthManager.authenticate(email, password)
        if success:
            self.save_last_email(email)
            QMessageBox.information(self, "Login Success", f"Welcome, {user_or_msg.get('first_name', email)}!")
            if self.on_login:
                self.on_login(user_or_msg)
        else:
            # Custom error for private key issues
            if 'private key' in str(user_or_msg).lower():
                QMessageBox.critical(self, "Private Key Error", f"Login failed: {user_or_msg}\n\nPlease ensure your private key file is present and matches your blockchain public key.")
            else:
                QMessageBox.warning(self, "Login Failed", user_or_msg)

    def save_last_email(self, email: str):
        """Saves the last successfully used email to a file."""
        try:
            with open(LAST_LOGIN_FILE, 'w', encoding='utf-8') as f:
                json.dump({'last_email': email}, f)
        except IOError as e:
            print(f"Warning: Could not save last login email: {e}")

    def load_last_email(self):
        """Loads the last email from the file and pre-fills the input."""
        if not os.path.exists(LAST_LOGIN_FILE):
            return
        try:
            with open(LAST_LOGIN_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                last_email = data.get('last_email')
                if last_email:
                    self.email_input.setText(last_email)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load last login email: {e}")
