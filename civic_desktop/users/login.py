from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from .auth import AuthManager

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

    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Missing Field", "Email and password are required.")
            return
        success, user_or_msg = AuthManager.authenticate(email, password)
        if success:
            QMessageBox.information(self, "Login Success", f"Welcome, {user_or_msg.get('first_name', email)}!")
            if self.on_login:
                self.on_login(user_or_msg)
        else:
            # Custom error for private key issues
            if 'private key' in str(user_or_msg).lower():
                QMessageBox.critical(self, "Private Key Error", f"Login failed: {user_or_msg}\n\nPlease ensure your private key file is present and matches your blockchain public key.")
            else:
                QMessageBox.warning(self, "Login Failed", user_or_msg)
