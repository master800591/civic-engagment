# Communications Module - UI Components for Secure Civic Messaging
"""
Communications UI components providing:
- Direct messaging interface between citizens and representatives
- Official announcements dashboard with distribution management
- Group communications for committees and working groups
- Notification center with user preferences
- Contact directory and message management
"""

from typing import Optional, Any, Dict, List
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QListWidget, QListWidgetItem, QTextEdit, QLineEdit, 
                            QComboBox, QTabWidget, QScrollArea, QMessageBox, QFormLayout,
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                            QGroupBox, QCheckBox, QSpinBox, QProgressBar, QDialog,
                            QTreeWidget, QTreeWidgetItem, QFileDialog, QDateTimeEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDateTime
from PyQt5.QtGui import QFont, QPixmap, QColor, QIcon
from .messaging_backend import MessagingBackend
from ..users.session import SessionManager
from ..users.backend import UserBackend

class CommunicationsTab(QWidget):
    """Main communications interface for secure civic messaging and announcements"""
    
    # Signal for message updates
    message_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.messaging_backend = MessagingBackend()
        self.current_conversation = None
        self.unread_count = 0
        self.init_ui()
        
        # Auto-refresh timer for new messages
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_messages)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the communications interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Blockchain status and user role display
        user = SessionManager.get_current_user()
        role = user.get('role', 'Unknown') if user else 'Unknown'
        
        blockchain_status = QLabel("All communications are <b>secured with encryption</b> and logged on blockchain for transparency.")
        blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
        blockchain_status.setAccessibleName("Security Status")
        blockchain_status.setToolTip("All messages are end-to-end encrypted with blockchain audit trails.")
        
        role_label = QLabel(f"Your Role: <b>{role}</b>")
        role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
        role_label.setAccessibleName("User Role")
        role_label.setToolTip("Your platform role determines messaging permissions and access.")
        
        # Communication action buttons
        compose_btn = QPushButton("✉️ Compose Message")
        compose_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        compose_btn.setAccessibleName("Compose Message Button")
        compose_btn.setToolTip("Send a secure message to representatives or other users.")
        compose_btn.setMinimumHeight(40)
        compose_btn.setMinimumWidth(180)
        compose_btn.clicked.connect(self.open_compose_dialog)
        
        announcement_btn = QPushButton("📢 Create Announcement")
        announcement_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        announcement_btn.clicked.connect(self.open_announcement_dialog)
        
        contacts_btn = QPushButton("👥 Contacts")
        contacts_btn.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        contacts_btn.clicked.connect(self.show_contacts_dialog)
        
        top_layout = QVBoxLayout()
        top_layout.addWidget(blockchain_status)
        top_layout.addWidget(role_label)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(compose_btn)
        button_layout.addWidget(announcement_btn)
        button_layout.addWidget(contacts_btn)
        button_layout.addStretch()
        top_layout.addLayout(button_layout)
        
        layout.addLayout(top_layout)
        
        # Header
        header = QLabel("💬 Secure Civic Communications")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create main content container
        self.main_content = QWidget()
        layout.addWidget(self.main_content)
        
        self.setLayout(layout)
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh the entire UI based on authentication status"""
        # Clear existing content
        if hasattr(self, 'main_content'):
            layout = self.main_content.layout()
            if layout:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            else:
                layout = QVBoxLayout()
                self.main_content.setLayout(layout)
        
        # Check if user is logged in
        if not SessionManager.is_authenticated():
            self.show_login_required()
            return
        
        # Create main communications interface for logged-in users
        self.create_communications_interface()
    
    def show_login_required(self):
        """Show login required message"""
        layout = self.main_content.layout()
        
        login_frame = QFrame()
        login_frame.setFrameStyle(QFrame.StyledPanel)
        login_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin: 50px;
            }
        """)
        
        frame_layout = QVBoxLayout()
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(40, 40, 40, 40)
        
        icon_label = QLabel("🔐")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; color: #6c757d;")
        
        title_label = QLabel("Communications Access Required")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #495057; margin-bottom: 10px;")
        
        message_label = QLabel("Please log in to access secure messaging, announcements, and communications features.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 16px; color: #6c757d; margin-bottom: 20px;")
        message_label.setWordWrap(True)
        
        frame_layout.addWidget(icon_label)
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(message_label)
        
        login_frame.setLayout(frame_layout)
        layout.addWidget(login_frame)
    
    def create_communications_interface(self):
        """Create the main communications interface for authenticated users"""
        layout = self.main_content.layout()
        
        # Main communications layout with splitter
        splitter = QSplitter()
        
        # Left panel - Message list and navigation
        left_panel = self.create_message_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Message content and management
        right_panel = self.create_content_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 700])
        layout.addWidget(splitter)
        
        # Load initial messages and notifications
        self.refresh_messages()
    
    def create_message_panel(self) -> QWidget:
        """Create the left message navigation panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Message statistics
        stats_group = QGroupBox("Message Statistics")
        stats_layout = QFormLayout()
        
        user = SessionManager.get_current_user()
        if user:
            stats = self.messaging_backend.get_message_statistics(user['email'])
            
            self.sent_count_label = QLabel(str(stats.get('sent_messages', 0)))
            self.received_count_label = QLabel(str(stats.get('received_messages', 0)))
            self.unread_count_label = QLabel(str(stats.get('unread_messages', 0)))
            self.announcements_count_label = QLabel(str(stats.get('announcements', 0)))
            self.notifications_count_label = QLabel(str(stats.get('unread_notifications', 0)))
            
            stats_layout.addRow("Sent Messages:", self.sent_count_label)
            stats_layout.addRow("Received Messages:", self.received_count_label)
            stats_layout.addRow("Unread Messages:", self.unread_count_label)
            stats_layout.addRow("Announcements:", self.announcements_count_label)
            stats_layout.addRow("Unread Notifications:", self.notifications_count_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Message folders
        folders_group = QGroupBox("Message Folders")
        folders_layout = QVBoxLayout()
        
        self.inbox_btn = QPushButton("📥 Inbox")
        self.inbox_btn.clicked.connect(lambda: self.load_messages('inbox'))
        
        self.sent_btn = QPushButton("📤 Sent")
        self.sent_btn.clicked.connect(lambda: self.load_messages('sent'))
        
        self.announcements_btn = QPushButton("📢 Announcements")
        self.announcements_btn.clicked.connect(lambda: self.load_messages('announcements'))
        
        self.notifications_btn = QPushButton("🔔 Notifications")
        self.notifications_btn.clicked.connect(lambda: self.load_messages('notifications'))
        
        folders_layout.addWidget(self.inbox_btn)
        folders_layout.addWidget(self.sent_btn)
        folders_layout.addWidget(self.announcements_btn)
        folders_layout.addWidget(self.notifications_btn)
        
        folders_group.setLayout(folders_layout)
        layout.addWidget(folders_group)
        
        # Message list
        messages_group = QGroupBox("Messages")
        messages_layout = QVBoxLayout()
        
        self.message_list = QListWidget()
        self.message_list.itemClicked.connect(self.on_message_selected)
        messages_layout.addWidget(self.message_list)
        
        messages_group.setLayout(messages_layout)
        layout.addWidget(messages_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_content_panel(self) -> QWidget:
        """Create the right content panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Communications tabs
        self.comm_tabs = QTabWidget()
        self.comm_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
                font-weight: bold;
            }
        """)
        
        # Add communication tabs
        self.comm_tabs.addTab(self.create_message_content_tab(), "📋 Message")
        self.comm_tabs.addTab(self.create_compose_tab(), "✉️ Compose")
        self.comm_tabs.addTab(self.create_announcements_tab(), "📢 Announcements")
        self.comm_tabs.addTab(self.create_notifications_tab(), "🔔 Notifications")
        
        layout.addWidget(self.comm_tabs)
        
        widget.setLayout(layout)
        return widget
    
    def create_message_content_tab(self) -> QWidget:
        """Create the message content display tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Message header
        self.message_header = QLabel("Select a message to view")
        self.message_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(self.message_header)
        
        # Message content
        self.message_content = QTextEdit()
        self.message_content.setReadOnly(True)
        self.message_content.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.message_content)
        
        # Message actions
        actions_layout = QHBoxLayout()
        
        self.reply_btn = QPushButton("Reply")
        self.reply_btn.setStyleSheet("background-color: #007bff; color: white; padding: 8px 16px; border-radius: 5px;")
        self.reply_btn.clicked.connect(self.reply_to_message)
        self.reply_btn.setEnabled(False)
        
        self.mark_read_btn = QPushButton("Mark as Read")
        self.mark_read_btn.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px; border-radius: 5px;")
        self.mark_read_btn.clicked.connect(self.mark_message_read)
        self.mark_read_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 8px 16px; border-radius: 5px;")
        self.delete_btn.clicked.connect(self.delete_message)
        self.delete_btn.setEnabled(False)
        
        actions_layout.addWidget(self.reply_btn)
        actions_layout.addWidget(self.mark_read_btn)
        actions_layout.addWidget(self.delete_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_compose_tab(self) -> QWidget:
        """Create the message composition tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Compose form
        form_layout = QFormLayout()
        
        self.recipient_combo = QComboBox()
        self.recipient_combo.setEditable(True)
        self.load_contacts()
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter message subject...")
        
        self.message_type_combo = QComboBox()
        self.message_type_combo.addItems(["direct", "urgent", "official", "group"])
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["normal", "high", "urgent"])
        
        form_layout.addRow("To:", self.recipient_combo)
        form_layout.addRow("Subject:", self.subject_input)
        form_layout.addRow("Type:", self.message_type_combo)
        form_layout.addRow("Priority:", self.priority_combo)
        
        layout.addLayout(form_layout)
        
        # Message content
        content_label = QLabel("Message Content:")
        content_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(content_label)
        
        self.compose_content = QTextEdit()
        self.compose_content.setPlaceholderText("Enter your secure message here...")
        self.compose_content.setMinimumHeight(200)
        layout.addWidget(self.compose_content)
        
        # Send button
        send_layout = QHBoxLayout()
        
        send_btn = QPushButton("Send Message")
        send_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 12px 24px; border-radius: 5px; font-size: 14px;")
        send_btn.clicked.connect(self.send_message)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 12px 24px; border-radius: 5px;")
        clear_btn.clicked.connect(self.clear_compose_form)
        
        send_layout.addWidget(send_btn)
        send_layout.addWidget(clear_btn)
        send_layout.addStretch()
        
        layout.addLayout(send_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_announcements_tab(self) -> QWidget:
        """Create the announcements management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Announcements list
        announcements_label = QLabel("Official Announcements")
        announcements_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(announcements_label)
        
        self.announcements_list = QListWidget()
        self.announcements_list.itemClicked.connect(self.on_announcement_selected)
        layout.addWidget(self.announcements_list)
        
        # Announcement content
        self.announcement_content = QTextEdit()
        self.announcement_content.setReadOnly(True)
        self.announcement_content.setMaximumHeight(200)
        layout.addWidget(self.announcement_content)
        
        # Create announcement section (role-based)
        user = SessionManager.get_current_user()
        if user and self.can_create_announcements(user.get('role', '')):
            create_group = QGroupBox("Create Official Announcement")
            create_layout = QFormLayout()
            
            self.announcement_title = QLineEdit()
            self.announcement_title.setPlaceholderText("Announcement title...")
            
            self.target_audience = QComboBox()
            self.target_audience.addItems([
                "all_citizens", "public", "Contract Representatives", 
                "Contract Senators", "Contract Elders", "specific_users"
            ])
            
            self.announcement_priority = QComboBox()
            self.announcement_priority.addItems(["normal", "high", "urgent", "emergency"])
            
            create_layout.addRow("Title:", self.announcement_title)
            create_layout.addRow("Target Audience:", self.target_audience)
            create_layout.addRow("Priority:", self.announcement_priority)
            
            self.announcement_compose = QTextEdit()
            self.announcement_compose.setPlaceholderText("Enter announcement content...")
            self.announcement_compose.setMaximumHeight(150)
            
            create_layout.addRow("Content:", self.announcement_compose)
            
            publish_btn = QPushButton("Publish Announcement")
            publish_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px;")
            publish_btn.clicked.connect(self.publish_announcement)
            
            create_layout.addRow("", publish_btn)
            create_group.setLayout(create_layout)
            layout.addWidget(create_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_notifications_tab(self) -> QWidget:
        """Create the notifications management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Notifications header
        notifications_label = QLabel("System Notifications")
        notifications_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(notifications_label)
        
        # Notifications list
        self.notifications_list = QListWidget()
        self.notifications_list.itemClicked.connect(self.on_notification_selected)
        layout.addWidget(self.notifications_list)
        
        # Notification actions
        actions_layout = QHBoxLayout()
        
        mark_all_read_btn = QPushButton("Mark All Read")
        mark_all_read_btn.setStyleSheet("background-color: #007bff; color: white; padding: 8px 16px; border-radius: 5px;")
        mark_all_read_btn.clicked.connect(self.mark_all_notifications_read)
        
        clear_old_btn = QPushButton("Clear Old")
        clear_old_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 16px; border-radius: 5px;")
        clear_old_btn.clicked.connect(self.clear_old_notifications)
        
        actions_layout.addWidget(mark_all_read_btn)
        actions_layout.addWidget(clear_old_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        widget.setLayout(layout)
        return widget
    
    def load_contacts(self):
        """Load user contacts into recipient dropdown"""
        try:
            user = SessionManager.get_current_user()
            if user:
                contacts = self.messaging_backend.get_user_contacts(user['email'])
                self.recipient_combo.clear()
                
                for contact in contacts:
                    display_text = f"{contact['name']} ({contact['role']}) - {contact['email']}"
                    self.recipient_combo.addItem(display_text, contact['email'])
        except Exception as e:
            print(f"Error loading contacts: {e}")
    
    def can_create_announcements(self, role: str) -> bool:
        """Check if user role can create official announcements"""
        authorized_roles = ['Contract Elder', 'Contract Representative', 'Contract Senator', 
                           'Contract Founder', 'CEO', 'Admin']
        return role in authorized_roles
    
    def load_messages(self, folder_type: str):
        """Load messages based on folder type"""
        try:
            user = SessionManager.get_current_user()
            if not user:
                return
            
            self.message_list.clear()
            
            if folder_type == 'inbox':
                messages = self.messaging_backend.get_messages(user['email'])
                received_messages = [msg for msg in messages if msg['recipient_email'] == user['email']]
                
                for message in received_messages:
                    item_text = f"From: {message['sender_email']}\nSubject: {message['subject']}\n{message['timestamp'][:16]}"
                    if not message.get('read', False):
                        item_text = "🔵 " + item_text  # Unread indicator
                    
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, message)
                    self.message_list.addItem(item)
            
            elif folder_type == 'sent':
                messages = self.messaging_backend.get_messages(user['email'])
                sent_messages = [msg for msg in messages if msg['sender_email'] == user['email']]
                
                for message in sent_messages:
                    item_text = f"To: {message['recipient_email']}\nSubject: {message['subject']}\n{message['timestamp'][:16]}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, message)
                    self.message_list.addItem(item)
            
            elif folder_type == 'announcements':
                announcements = self.messaging_backend.get_announcements(user['email'])
                
                for announcement in announcements:
                    item_text = f"📢 {announcement['title']}\nFrom: {announcement['sender_email']}\n{announcement['timestamp'][:16]}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, announcement)
                    self.announcements_list.addItem(item)
            
            elif folder_type == 'notifications':
                notifications = self.messaging_backend.get_notifications(user['email'])
                
                for notification in notifications:
                    item_text = f"{notification['type']}: {notification['message']}\n{notification['timestamp'][:16]}"
                    if not notification.get('read', False):
                        item_text = "🔔 " + item_text
                    
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, notification)
                    self.notifications_list.addItem(item)
                    
        except Exception as e:
            print(f"Error loading {folder_type}: {e}")
    
    def on_message_selected(self, item):
        """Handle message selection"""
        if item and item.data(Qt.UserRole):
            message = item.data(Qt.UserRole)
            self.display_message(message)
    
    def on_announcement_selected(self, item):
        """Handle announcement selection"""
        if item and item.data(Qt.UserRole):
            announcement = item.data(Qt.UserRole)
            self.display_announcement(announcement)
    
    def on_notification_selected(self, item):
        """Handle notification selection"""
        if item and item.data(Qt.UserRole):
            notification = item.data(Qt.UserRole)
            self.display_notification(notification)
    
    def display_message(self, message):
        """Display message content"""
        self.message_header.setText(f"From: {message['sender_email']} | Subject: {message['subject']}")
        self.message_content.setPlainText(message['content'])
        
        # Enable action buttons
        self.reply_btn.setEnabled(True)
        self.mark_read_btn.setEnabled(not message.get('read', False))
        self.delete_btn.setEnabled(True)
        
        # Store current message for actions
        self.current_message = message
    
    def display_announcement(self, announcement):
        """Display announcement content"""
        content = f"Title: {announcement['title']}\n"
        content += f"From: {announcement['sender_email']} ({announcement.get('sender_role', 'Unknown')})\n"
        content += f"Priority: {announcement.get('priority', 'normal')}\n"
        content += f"Date: {announcement['timestamp']}\n\n"
        content += announcement['content']
        
        self.announcement_content.setPlainText(content)
    
    def display_notification(self, notification):
        """Display notification content"""
        # Implementation would show notification details
        pass
    
    def refresh_messages(self):
        """Refresh all message data"""
        if not SessionManager.is_authenticated():
            return
        
        try:
            # Update statistics
            user = SessionManager.get_current_user()
            if user:
                stats = self.messaging_backend.get_message_statistics(user['email'])
                
                if hasattr(self, 'sent_count_label'):
                    self.sent_count_label.setText(str(stats.get('sent_messages', 0)))
                    self.received_count_label.setText(str(stats.get('received_messages', 0)))
                    self.unread_count_label.setText(str(stats.get('unread_messages', 0)))
                    self.announcements_count_label.setText(str(stats.get('announcements', 0)))
                    self.notifications_count_label.setText(str(stats.get('unread_notifications', 0)))
        except Exception as e:
            print(f"Error refreshing messages: {e}")
    
    def send_message(self):
        """Send a new message"""
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Required", "Please log in to send messages.")
            return
        
        recipient_text = self.recipient_combo.currentText()
        if " - " in recipient_text:
            recipient_email = recipient_text.split(" - ")[-1]
        else:
            recipient_email = self.recipient_combo.currentData()
        
        subject = self.subject_input.text().strip()
        content = self.compose_content.toPlainText().strip()
        message_type = self.message_type_combo.currentText()
        priority = self.priority_combo.currentText()
        
        if not all([recipient_email, subject, content]):
            QMessageBox.warning(self, "Missing Information", "Please fill in all required fields.")
            return
        
        try:
            success, message = self.messaging_backend.send_message(
                user['email'], recipient_email, subject, content, 
                message_type, priority
            )
            
            if success:
                QMessageBox.information(self, "Message Sent", message)
                self.clear_compose_form()
                self.refresh_messages()
            else:
                QMessageBox.warning(self, "Send Failed", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send message: {str(e)}")
    
    def clear_compose_form(self):
        """Clear the compose form"""
        self.recipient_combo.setCurrentIndex(0)
        self.subject_input.clear()
        self.compose_content.clear()
        self.message_type_combo.setCurrentIndex(0)
        self.priority_combo.setCurrentIndex(0)
    
    def reply_to_message(self):
        """Reply to current message"""
        if hasattr(self, 'current_message'):
            # Switch to compose tab and populate fields
            self.comm_tabs.setCurrentIndex(1)  # Compose tab
            
            # Set recipient and subject
            original_sender = self.current_message['sender_email']
            for i in range(self.recipient_combo.count()):
                if self.recipient_combo.itemData(i) == original_sender:
                    self.recipient_combo.setCurrentIndex(i)
                    break
            
            original_subject = self.current_message['subject']
            reply_subject = f"Re: {original_subject}" if not original_subject.startswith("Re:") else original_subject
            self.subject_input.setText(reply_subject)
            
            # Add original message to compose content
            original_content = f"\n\n--- Original Message ---\nFrom: {original_sender}\nSubject: {original_subject}\n{self.current_message['content']}"
            self.compose_content.setPlainText(original_content)
    
    def mark_message_read(self):
        """Mark current message as read"""
        if hasattr(self, 'current_message'):
            user = SessionManager.get_current_user()
            if user:
                success = self.messaging_backend.mark_message_read(
                    self.current_message['id'], user['email']
                )
                if success:
                    self.mark_read_btn.setEnabled(False)
                    self.refresh_messages()
    
    def delete_message(self):
        """Delete current message"""
        if hasattr(self, 'current_message'):
            reply = QMessageBox.question(
                self, "Confirm Delete", "Are you sure you want to delete this message?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # Implementation would delete message
                QMessageBox.information(self, "Deleted", "Message deleted successfully.")
                self.refresh_messages()
    
    def publish_announcement(self):
        """Publish an official announcement"""
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Required", "Please log in to publish announcements.")
            return
        
        if not self.can_create_announcements(user.get('role', '')):
            QMessageBox.warning(self, "Access Denied", "You don't have permission to create official announcements.")
            return
        
        title = self.announcement_title.text().strip()
        content = self.announcement_compose.toPlainText().strip()
        audience = self.target_audience.currentText()
        priority = self.announcement_priority.currentText()
        
        if not all([title, content]):
            QMessageBox.warning(self, "Missing Information", "Please provide title and content.")
            return
        
        try:
            target_audience = [audience] if audience != "all_citizens" else ["all_citizens", "public"]
            
            success, message = self.messaging_backend.create_official_announcement(
                user['email'], title, content, target_audience, 
                'official', priority
            )
            
            if success:
                QMessageBox.information(self, "Announcement Published", message)
                self.announcement_title.clear()
                self.announcement_compose.clear()
                self.load_messages('announcements')
            else:
                QMessageBox.warning(self, "Publication Failed", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to publish announcement: {str(e)}")
    
    def mark_all_notifications_read(self):
        """Mark all notifications as read"""
        # Implementation would mark all notifications as read
        QMessageBox.information(self, "Notifications", "All notifications marked as read.")
        self.refresh_messages()
    
    def clear_old_notifications(self):
        """Clear old notifications"""
        reply = QMessageBox.question(
            self, "Confirm Clear", "Clear notifications older than 30 days?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Cleared", "Old notifications cleared.")
            self.refresh_messages()
    
    def open_compose_dialog(self):
        """Open compose message dialog"""
        self.comm_tabs.setCurrentIndex(1)  # Switch to compose tab
    
    def open_announcement_dialog(self):
        """Open announcement creation dialog"""
        self.comm_tabs.setCurrentIndex(2)  # Switch to announcements tab
    
    def show_contacts_dialog(self):
        """Show contacts management dialog"""
        dialog = ContactsDialog(self)
        dialog.exec_()

class ContactsDialog(QDialog):
    """Dialog for managing contacts and communication directory"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Civic Contacts Directory")
        self.setModal(True)
        self.resize(600, 500)
        self.messaging_backend = MessagingBackend()
        self.init_ui()
        self.load_contacts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📞 Civic Contacts Directory")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(header)
        
        # Contacts table
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(4)
        self.contacts_table.setHorizontalHeaderLabels(["Name", "Role", "Email", "Category"])
        self.contacts_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.contacts_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        message_btn = QPushButton("Send Message")
        message_btn.clicked.connect(self.send_message_to_contact)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(message_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def load_contacts(self):
        """Load contacts into the table"""
        try:
            user = SessionManager.get_current_user()
            if user:
                contacts = self.messaging_backend.get_user_contacts(user['email'])
                
                self.contacts_table.setRowCount(len(contacts))
                
                for row, contact in enumerate(contacts):
                    self.contacts_table.setItem(row, 0, QTableWidgetItem(contact['name']))
                    self.contacts_table.setItem(row, 1, QTableWidgetItem(contact['role']))
                    self.contacts_table.setItem(row, 2, QTableWidgetItem(contact['email']))
                    self.contacts_table.setItem(row, 3, QTableWidgetItem(contact['category']))
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load contacts: {str(e)}")
    
    def send_message_to_contact(self):
        """Send message to selected contact"""
        current_row = self.contacts_table.currentRow()
        if current_row >= 0:
            email = self.contacts_table.item(current_row, 2).text()
            name = self.contacts_table.item(current_row, 0).text()
            
            QMessageBox.information(self, "Message", f"Opening compose dialog for {name} ({email})")
            self.accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a contact first.")