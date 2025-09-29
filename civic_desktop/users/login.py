"""
LOGIN UI COMPONENT - User-friendly login interface
Provides secure login form with validation and user feedback
"""

import sys
from pathlib import Path
from typing import Optional, Callable

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
        QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox,
        QProgressBar, QFrame, QSpacerItem, QSizePolicy, QGroupBox
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
    from PyQt5.QtGui import QFont, QPalette, QIcon, QPixmap
    PYQT_AVAILABLE = True
except ImportError:
    print("Warning: PyQt5 not available. GUI functionality disabled.")
    PYQT_AVAILABLE = False

# Import authentication modules
sys.path.append(str(Path(__file__).parent.parent))
from users.auth import AuthenticationService
from users.backend import UserBackend
from utils.validation import DataValidator

class LoginWorker(QThread if PYQT_AVAILABLE else object):
    """Worker thread for login operations to prevent UI blocking"""
    
    if PYQT_AVAILABLE:
        login_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, auth_service: AuthenticationService, email: str, password: str):
        if PYQT_AVAILABLE:
            super().__init__()
        self.auth_service = auth_service
        self.email = email
        self.password = password
    
    def run(self):
        """Execute login in background thread"""
        if PYQT_AVAILABLE:
            try:
                success, message = self.auth_service.login(self.email, self.password)
                self.login_completed.emit(success, message)
            except Exception as e:
                self.login_completed.emit(False, f"Login error: {str(e)}")

class LoginUI(QWidget if PYQT_AVAILABLE else object):
    """User-friendly login interface with security features"""
    
    if PYQT_AVAILABLE:
        login_successful = pyqtSignal(dict)  # User data
        show_registration = pyqtSignal()
    
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        
        # Initialize authentication service
        self.backend = UserBackend()
        self.auth_service = AuthenticationService(self.backend)
        
        # UI state
        self.login_attempts = 0
        self.max_attempts = 3
        self.is_logging_in = False
        
        # Setup UI
        self.init_ui()
        self.setup_styles()
        
        # Login worker thread
        self.login_worker = None
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Civic Engagement Platform - Login")
        self.setFixedSize(450, 600)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header section
        header_layout = self.create_header_section()
        main_layout.addLayout(header_layout)
        
        # Login form section
        form_layout = self.create_login_form()
        main_layout.addLayout(form_layout)
        
        # Action buttons section
        buttons_layout = self.create_buttons_section()
        main_layout.addLayout(buttons_layout)
        
        # Footer section
        footer_layout = self.create_footer_section()
        main_layout.addLayout(footer_layout)
        
        # Add stretch to center content
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def create_header_section(self):
        """Create header with platform branding"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Platform title
        title_label = QLabel("🏛️ Civic Engagement Platform")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # Subtitle
        subtitle_label = QLabel("Secure Democratic Participation")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        
        return layout
    
    def create_login_form(self):
        """Create login form with validation"""
        # Group box for form
        form_group = QGroupBox("Sign In to Your Account")
        form_group.setFont(QFont("Arial", 12, QFont.Bold))
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Email field
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        self.email_input.setFont(QFont("Arial", 11))
        self.email_input.textChanged.connect(self.on_input_changed)
        self.email_input.returnPressed.connect(self.on_login_clicked)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setFont(QFont("Arial", 11))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.on_input_changed)
        self.password_input.returnPressed.connect(self.on_login_clicked)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me on this device")
        self.remember_checkbox.setFont(QFont("Arial", 10))
        
        # Show password checkbox
        self.show_password_checkbox = QCheckBox("Show password")
        self.show_password_checkbox.setFont(QFont("Arial", 10))
        self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
        
        # Add fields to form
        form_layout.addRow("📧 Email:", self.email_input)
        form_layout.addRow("🔒 Password:", self.password_input)
        form_layout.addRow("", self.show_password_checkbox)
        form_layout.addRow("", self.remember_checkbox)
        
        form_group.setLayout(form_layout)
        
        # Validation feedback
        self.validation_label = QLabel("")
        self.validation_label.setFont(QFont("Arial", 10))
        self.validation_label.setWordWrap(True)
        self.validation_label.hide()
        
        # Progress bar for login process
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Layout container
        layout = QVBoxLayout()
        layout.addWidget(form_group)
        layout.addWidget(self.validation_label)
        layout.addWidget(self.progress_bar)
        
        return layout
    
    def create_buttons_section(self):
        """Create action buttons"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Login button
        self.login_button = QPushButton("🔐 Sign In")
        self.login_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.login_button.setMinimumHeight(45)
        self.login_button.clicked.connect(self.on_login_clicked)
        self.login_button.setEnabled(False)  # Disabled until valid input
        
        # Forgot password button
        self.forgot_password_button = QPushButton("Forgot Password?")
        self.forgot_password_button.setFont(QFont("Arial", 10))
        self.forgot_password_button.setStyleSheet("QPushButton { border: none; color: #3498db; text-decoration: underline; }")
        self.forgot_password_button.clicked.connect(self.on_forgot_password_clicked)
        
        layout.addWidget(self.login_button)
        layout.addWidget(self.forgot_password_button, alignment=Qt.AlignCenter)
        
        return layout
    
    def create_footer_section(self):
        """Create footer with registration link"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        
        # Registration prompt
        registration_layout = QHBoxLayout()
        
        prompt_label = QLabel("Don't have an account?")
        prompt_label.setFont(QFont("Arial", 10))
        
        register_button = QPushButton("Create Account")
        register_button.setFont(QFont("Arial", 10, QFont.Bold))
        register_button.setStyleSheet("QPushButton { border: none; color: #27ae60; text-decoration: underline; }")
        register_button.clicked.connect(self.on_register_clicked)
        
        registration_layout.addStretch()
        registration_layout.addWidget(prompt_label)
        registration_layout.addWidget(register_button)
        registration_layout.addStretch()
        
        layout.addWidget(separator)
        layout.addLayout(registration_layout)
        
        return layout
    
    def setup_styles(self):
        """Setup consistent styling"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: Arial, sans-serif;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
            }
            
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 12px;
                font-size: 11pt;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #3498db;
            }
            
            QLineEdit:invalid {
                border-color: #e74c3c;
            }
            
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
            }
            
            QPushButton:enabled {
                background-color: #3498db;
                color: white;
            }
            
            QPushButton:hover:enabled {
                background-color: #2980b9;
            }
            
            QPushButton:pressed:enabled {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            
            QCheckBox {
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #ddd;
                border-radius: 3px;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
            
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
    
    def on_input_changed(self):
        """Handle input field changes and enable/disable login button"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # Clear previous validation messages
        self.validation_label.hide()
        
        # Enable login button if both fields have content
        has_input = len(email) > 0 and len(password) > 0
        self.login_button.setEnabled(has_input and not self.is_logging_in)
        
        # Real-time email validation
        if email:
            is_valid, message = DataValidator.validate_email(email)
            if not is_valid:
                self.show_validation_message(message, "error")
                self.email_input.setStyleSheet("border-color: #e74c3c;")
            else:
                self.email_input.setStyleSheet("")
    
    def toggle_password_visibility(self, checked):
        """Toggle password field visibility"""
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def show_validation_message(self, message: str, message_type: str = "info"):
        """Show validation feedback to user"""
        self.validation_label.setText(message)
        
        if message_type == "error":
            self.validation_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        elif message_type == "success":
            self.validation_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.validation_label.setStyleSheet("color: #3498db; font-weight: bold;")
        
        self.validation_label.show()
    
    def on_login_clicked(self):
        """Handle login button click"""
        if self.is_logging_in:
            return
        
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        email_valid, email_msg = DataValidator.validate_email(email)
        if not email_valid:
            self.show_validation_message(email_msg, "error")
            return
        
        if not password:
            self.show_validation_message("Password is required", "error")
            return
        
        # Start login process
        self.start_login(email, password)
    
    def start_login(self, email: str, password: str):
        """Start login process in background thread"""
        self.is_logging_in = True
        
        # Update UI for loading state
        self.login_button.setText("🔄 Signing In...")
        self.login_button.setEnabled(False)
        self.email_input.setEnabled(False)
        self.password_input.setEnabled(False)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        self.show_validation_message("Authenticating...", "info")
        
        # Start login worker thread
        self.login_worker = LoginWorker(self.auth_service, email, password)
        self.login_worker.login_completed.connect(self.on_login_completed)
        self.login_worker.start()
    
    @pyqtSlot(bool, str)
    def on_login_completed(self, success: bool, message: str):
        """Handle login completion"""
        self.is_logging_in = False
        
        # Reset UI state
        self.login_button.setText("🔐 Sign In")
        self.login_button.setEnabled(True)
        self.email_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.show_validation_message(message, "success")
            
            # Get current user data
            user_data = self.auth_service.get_current_user()
            if user_data:
                self.login_successful.emit(user_data)
            
            # Clear form
            if not self.remember_checkbox.isChecked():
                self.email_input.clear()
            self.password_input.clear()
            
            # Reset attempt counter
            self.login_attempts = 0
            
        else:
            self.show_validation_message(message, "error")
            self.login_attempts += 1
            
            # Clear password on failed attempt
            self.password_input.clear()
            
            # Lock out after max attempts
            if self.login_attempts >= self.max_attempts:
                self.lockout_login()
    
    def lockout_login(self):
        """Temporarily lock login after too many failed attempts"""
        self.login_button.setEnabled(False)
        self.email_input.setEnabled(False)
        self.password_input.setEnabled(False)
        
        self.show_validation_message("Too many failed attempts. Please wait 5 minutes before trying again.", "error")
        
        # Re-enable after 5 minutes
        QTimer.singleShot(300000, self.reset_lockout)  # 5 minutes = 300,000 ms
    
    def reset_lockout(self):
        """Reset lockout state"""
        self.login_attempts = 0
        self.login_button.setEnabled(True)
        self.email_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.validation_label.hide()
    
    def on_forgot_password_clicked(self):
        """Handle forgot password click"""
        QMessageBox.information(
            self,
            "Password Recovery",
            "Password recovery functionality will be implemented in a future update.\n\n"
            "For now, please contact a system administrator for password reset assistance."
        )
    
    def on_register_clicked(self):
        """Handle registration button click"""
        self.show_registration.emit()
    
    def clear_form(self):
        """Clear login form"""
        self.email_input.clear()
        self.password_input.clear()
        self.remember_checkbox.setChecked(False)
        self.show_password_checkbox.setChecked(False)
        self.validation_label.hide()
        self.login_attempts = 0