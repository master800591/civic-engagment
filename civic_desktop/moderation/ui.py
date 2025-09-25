# Moderation Module - UI Components
from typing import Optional, Any, Dict
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QListWidget, QTextEdit, QLineEdit, QComboBox, QMessageBox,
                            QFrame, QScrollArea, QSplitter, QGroupBox, QFormLayout,
                            QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt
from .backend import ModerationBackend, ModerationAction, ModerationSeverity
from ..users.session import SessionManager
from ..users.backend import UserBackend


class ModerationDashboard(QWidget):
    """Main moderation dashboard for platform moderators"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self) -> None:
        layout = QVBoxLayout()
        # Blockchain status and user role display
        user = SessionManager.get_current_user()
        role = user.get('role', 'Unknown') if user else 'Unknown'
        blockchain_status = QLabel("All moderation actions are <b>recorded on blockchain</b> for audit and transparency.")
        blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
        role_label = QLabel(f"Your Role: <b>{role}</b>")
        role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
        # Add Export Report button
        export_btn = QPushButton("Export Moderation Report")
        export_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 5px; padding: 8px 18px;")
        export_btn.clicked.connect(self.open_reports_tab)
        top_layout = QVBoxLayout()
        top_layout.addWidget(blockchain_status)
        top_layout.addWidget(role_label)
        top_layout.addWidget(export_btn)
        layout.addLayout(top_layout)
        # Check if user has moderation privileges
        if not user or not ModerationBackend.can_moderate(user['email']):
            access_denied = QLabel("Access Denied: You don't have moderation privileges.")
            access_denied.setStyleSheet("color: red; font-size: 16px; font-weight: bold; text-align: center;")
            access_denied.setAlignment(Qt.AlignCenter)
            layout.addWidget(access_denied)
            info_label = QLabel("Moderation access is restricted to elected representatives and platform administrators.")
            info_label.setWordWrap(True)
            info_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(info_label)
            self.setLayout(layout)
            return
        # Moderation tabs
        tabs = QTabWidget()
        flags_tab = self.create_flags_tab()
        tabs.addTab(flags_tab, "Pending Flags")
        stats_tab = self.create_stats_tab()
        tabs.addTab(stats_tab, "Statistics")
        users_tab = self.create_users_tab()
        tabs.addTab(users_tab, "User Management")
        layout.addWidget(tabs)
        self.setLayout(layout)

    def open_reports_tab(self):
        # Signal to main window to switch to Reports tab
        mw = self.parent()
        while mw and not hasattr(mw, 'tabs'):
            mw = mw.parent()
        if mw and hasattr(mw, 'tabs'):
            for i in range(mw.tabs.count()):
                if mw.tabs.tabText(i).lower().startswith("📊 reports") or mw.tabs.tabText(i).lower().startswith("reports"):
                    mw.tabs.setCurrentIndex(i)
                    break
    
    def create_flags_tab(self) -> QWidget:
        """Create the pending flags management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Content Flags Requiring Review")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Flags")
        refresh_btn.clicked.connect(self.refresh_flags)
        layout.addWidget(refresh_btn)
        
        # Flags table
        self.flags_table = QTableWidget()
        self.flags_table.setColumnCount(6)
        self.flags_table.setHorizontalHeaderLabels([
            "ID", "Content Type", "Severity", "Reporter", "Created", "Reason"
        ])
        
        # Make table headers stretch
        header = self.flags_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Make flags table read-only to prevent editing of reports
        self.flags_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.flags_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.flags_table.itemSelectionChanged.connect(self.on_flag_selected)
        layout.addWidget(self.flags_table)
        
        # Flag review section
        review_group = QGroupBox("Review Selected Flag")
        review_layout = QVBoxLayout()
        
        self.flag_details = QLabel("Select a flag to view details")
        self.flag_details.setWordWrap(True)
        review_layout.addWidget(self.flag_details)
        
        review_layout.addWidget(QLabel("Resolution:"))
        self.resolution_input = QTextEdit()
        self.resolution_input.setPlaceholderText("Explain your decision and any actions taken...")
        self.resolution_input.setMaximumHeight(100)
        review_layout.addWidget(self.resolution_input)
        
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("Action Taken:"))
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "No action required",
            "Content removed",
            "User warned",
            "User suspended",
            "Escalated to higher authority"
        ])
        action_layout.addWidget(self.action_combo)
        review_layout.addLayout(action_layout)
        
        self.resolve_btn = QPushButton("Resolve Flag")
        self.resolve_btn.clicked.connect(self.resolve_flag)
        self.resolve_btn.setEnabled(False)
        review_layout.addWidget(self.resolve_btn)
        
        review_group.setLayout(review_layout)
        layout.addWidget(review_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_stats_tab(self):
        """Create the moderation statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Moderation Statistics")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Stats display
        self.stats_display = QFormLayout()
        stats_group = QGroupBox("Platform Statistics")
        stats_group.setLayout(self.stats_display)
        layout.addWidget(stats_group)
        
        # Personal stats
        user = SessionManager.get_current_user()
        if user:
            personal_stats = QFormLayout()
            personal_group = QGroupBox(f"Your Moderation Activity ({user['email']})")
            personal_group.setLayout(personal_stats)
            self.personal_stats = personal_stats
            layout.addWidget(personal_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_users_tab(self):
        """Create the user management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("User Management")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # User actions
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("User Email:"))
        self.target_user_input = QLineEdit()
        self.target_user_input.setPlaceholderText("Enter user email address")
        action_layout.addWidget(self.target_user_input)
        layout.addLayout(action_layout)
        
        # Warning section
        warn_group = QGroupBox("Issue Warning")
        warn_layout = QVBoxLayout()
        
        warn_layout.addWidget(QLabel("Warning Reason:"))
        self.warning_reason = QTextEdit()
        
        blockchain_status = QLabel("All moderation actions are <b>recorded on blockchain</b> for audit and transparency.")
        blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
        blockchain_status.setAccessibleName("Blockchain Status")
        blockchain_status.setToolTip("All moderation actions are securely recorded for audit and transparency.")
        role_label = QLabel(f"Your Role: <b>{role}</b>")
        role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
        role_label.setAccessibleName("User Role")
        role_label.setToolTip("Your current platform role.")
        export_btn = QPushButton("Export Moderation Report")
        export_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        export_btn.setAccessibleName("Export Moderation Report Button")
        export_btn.setToolTip("View and export blockchain-based moderation reports.")
        export_btn.setMinimumHeight(40)
        export_btn.setMinimumWidth(180)
        export_btn.clicked.connect(self.open_reports_tab)
        warn_group.setLayout(warn_layout)
        layout.addWidget(warn_group)
        
        # Flag content section
        flag_group = QGroupBox("Flag Content")
        flag_layout = QVBoxLayout()
        
        flag_info_layout = QHBoxLayout()
        flag_info_layout.addWidget(QLabel("Content Type:"))
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems(["topic", "argument", "user"])
        flag_info_layout.addWidget(self.content_type_combo)
        
        flag_info_layout.addWidget(QLabel("Content ID:"))
        self.content_id_input = QLineEdit()
        self.content_id_input.setPlaceholderText("Enter content ID")
        flag_info_layout.addWidget(self.content_id_input)
        
        flag_info_layout.addWidget(QLabel("Severity:"))
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["low", "medium", "high", "critical"])
        flag_info_layout.addWidget(self.severity_combo)
        
        flag_layout.addLayout(flag_info_layout)
        
        flag_layout.addWidget(QLabel("Flag Reason:"))
        self.flag_reason = QTextEdit()
        self.flag_reason.setPlaceholderText("Explain why this content should be flagged...")
        self.flag_reason.setMaximumHeight(100)
        flag_layout.addWidget(self.flag_reason)
        
        self.flag_btn = QPushButton("Flag Content")
        self.flag_btn.clicked.connect(self.flag_content)
        flag_layout.addWidget(self.flag_btn)
        
        flag_group.setLayout(flag_layout)
        layout.addWidget(flag_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def refresh_data(self):
        """Refresh all moderation data"""
        try:
            if hasattr(self, 'flags_table') and self.flags_table is not None:
                self.refresh_flags()
                self.refresh_stats()
        except Exception as e:
            print(f"Error refreshing moderation data: {e}")
    
    def refresh_flags(self):
        """Refresh the pending flags list"""
        user = SessionManager.get_current_user()
        if not user or not hasattr(self, 'flags_table') or self.flags_table is None:
            return
        
        pending_flags = ModerationBackend.get_pending_flags(user['email'])
        
        self.flags_table.setRowCount(len(pending_flags))
        
        for i, flag in enumerate(pending_flags):
            self.flags_table.setItem(i, 0, QTableWidgetItem(flag['id'][:8] + '...'))
            self.flags_table.setItem(i, 1, QTableWidgetItem(flag['content_type']))
            self.flags_table.setItem(i, 2, QTableWidgetItem(flag['severity']))
            
            # Display reporter name instead of email
            reporter_display = UserBackend.get_user_display_name(flag['reporter_email'])
            self.flags_table.setItem(i, 3, QTableWidgetItem(reporter_display))
            
            self.flags_table.setItem(i, 4, QTableWidgetItem(flag['created_at'][:19]))
            self.flags_table.setItem(i, 5, QTableWidgetItem(flag['reason'][:50] + '...'))
            
            # Store full flag data in the first item
            self.flags_table.item(i, 0).setData(Qt.UserRole, flag)
    
    def refresh_stats(self):
        """Refresh moderation statistics"""
        user = SessionManager.get_current_user()
        if not user:
            return
        
        stats = ModerationBackend.get_moderation_stats(user['email'])
        
        # Clear existing stats
        for i in reversed(range(self.stats_display.count())):
            self.stats_display.removeRow(i)
        
        # Add general stats
        self.stats_display.addRow("Total Flags:", QLabel(str(stats['total_flags'])))
        self.stats_display.addRow("Pending Flags:", QLabel(str(stats['pending_flags'])))
        self.stats_display.addRow("Reviewed Flags:", QLabel(str(stats['reviewed_flags'])))
        
        # Add severity breakdown
        severity_stats = stats['flags_by_severity']
        self.stats_display.addRow("Critical Flags:", QLabel(str(severity_stats['critical'])))
        self.stats_display.addRow("High Priority:", QLabel(str(severity_stats['high'])))
        self.stats_display.addRow("Medium Priority:", QLabel(str(severity_stats['medium'])))
        self.stats_display.addRow("Low Priority:", QLabel(str(severity_stats['low'])))
        
        # Add personal stats if available
        if hasattr(self, 'personal_stats') and 'reviewed_by_moderator' in stats:
            for i in reversed(range(self.personal_stats.count())):
                self.personal_stats.removeRow(i)
            self.personal_stats.addRow("Flags Reviewed by You:", QLabel(str(stats['reviewed_by_moderator'])))
    
    def on_flag_selected(self):
        """Handle flag selection in the table"""
        current_row = self.flags_table.currentRow()
        if current_row >= 0:
            flag_item = self.flags_table.item(current_row, 0)
            if flag_item:
                flag = flag_item.data(Qt.UserRole)
                if flag:
                    # Get reporter display name
                    reporter_display = UserBackend.get_user_display_name(flag['reporter_email'])
                    
                    details = f"Flag ID: {flag['id']}\n"
                    details += f"Content Type: {flag['content_type']}\n"
                    details += f"Content ID: {flag['content_id']}\n"
                    details += f"Reporter: {reporter_display}\n"
                    details += f"Severity: {flag['severity']}\n"
                    details += f"Created: {flag['created_at']}\n\n"
                    details += f"Reason:\n{flag['reason']}"
                    
                    self.flag_details.setText(details)
                    self.resolve_btn.setEnabled(True)
                    self.current_flag = flag
    
    def resolve_flag(self):
        """Resolve the selected flag"""
        if not hasattr(self, 'current_flag'):
            QMessageBox.warning(self, "No Flag Selected", "Please select a flag to resolve")
            return
        
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Required", "Please log in")
            return
        
        resolution = self.resolution_input.toPlainText().strip()
        if not resolution:
            QMessageBox.warning(self, "Missing Resolution", "Please provide a resolution explanation")
            return
        
        action_taken = self.action_combo.currentText()
        
        success, message = ModerationBackend.review_flag(
            self.current_flag['id'], user['email'], resolution, action_taken
        )
        
        if success:
            QMessageBox.information(self, "Flag Resolved", message)
            self.resolution_input.clear()
            self.resolve_btn.setEnabled(False)
            self.flag_details.setText("Select a flag to view details")
            self.refresh_flags()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def warn_user(self):
        """Issue a warning to a user"""
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Required", "Please log in")
            return
        
        target_email = self.target_user_input.text().strip()
        reason = self.warning_reason.toPlainText().strip()
        
        if not target_email or not reason:
            QMessageBox.warning(self, "Missing Information", "Please provide both user email and reason")
            return
        
        success, message = ModerationBackend.warn_user(target_email, user['email'], reason)
        
        if success:
            QMessageBox.information(self, "Warning Issued", message)
            self.target_user_input.clear()
            self.warning_reason.clear()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def flag_content(self):
        """Flag content for review"""
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Required", "Please log in")
            return
        
        content_type = self.content_type_combo.currentText()
        content_id = self.content_id_input.text().strip()
        severity = self.severity_combo.currentText()
        reason = self.flag_reason.toPlainText().strip()
        
        if not content_id or not reason:
            QMessageBox.warning(self, "Missing Information", "Please provide content ID and reason")
            return
        
        success, message = ModerationBackend.flag_content(
            content_type, content_id, reason, user['email'], severity
        )
        
        if success:
            QMessageBox.information(self, "Content Flagged", message)
            self.content_id_input.clear()
            self.flag_reason.clear()
            self.refresh_flags()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def refresh_ui(self):
        """Refresh the UI to reflect current authentication state"""
        # Clear existing content and rebuild
        layout = self.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        # Rebuild the UI with current authentication state
        self.init_ui()
        self.refresh_data()