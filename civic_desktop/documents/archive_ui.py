"""
Documents & Archive UI - Democratic Document Management Interface
Comprehensive document management with search, access control, and transparency tools.
Supports FOIA requests, public records access, and official document workflows.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QDialog, QFormLayout, QSpinBox, QCheckBox, QGroupBox,
    QScrollArea, QFrame, QSplitter, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QCalendarWidget, QDateEdit, QTimeEdit,
    QMessageBox, QInputDialog, QGridLayout, QSlider,
    QListWidget, QListWidgetItem, QPushButton, QTextBrowser
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QDate, QTime
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QIcon

# Import session management
try:
    from civic_desktop.users.session import SessionManager
    from civic_desktop.documents.document_manager import DocumentManager, DocumentCategory, AccessLevel, DocumentStatus
    from civic_desktop.blockchain.blockchain import Blockchain
except ImportError as e:
    print(f"Import error in documents archive_ui: {e}")
    # Create minimal fallbacks for development
    class SessionManager:
        @staticmethod
        def get_current_user():
            return {"email": "dev@civic.local", "role": "Contract Citizen"}
        
        @staticmethod
        def is_authenticated():
            return True

class DocumentUploadDialog(QDialog):
    """Dialog for uploading new documents with metadata"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.document_manager = DocumentManager()
        self.selected_file = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Upload Document")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout()
        
        # File selection
        file_group = QGroupBox("Document File")
        file_layout = QVBoxLayout()
        
        file_select_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setPlaceholderText("No file selected...")
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_file)
        
        file_select_layout.addWidget(QLabel("File:"))
        file_select_layout.addWidget(self.file_path_edit)
        file_select_layout.addWidget(self.browse_btn)
        
        file_layout.addLayout(file_select_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Document metadata
        metadata_group = QGroupBox("Document Information")
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Official document title...")
        form_layout.addRow("Title:", self.title_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Document description and purpose...")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)
        
        self.category_combo = QComboBox()
        for category in DocumentCategory:
            self.category_combo.addItem(category.value.replace('_', ' ').title(), category.value)
        form_layout.addRow("Category:", self.category_combo)
        
        self.access_combo = QComboBox()
        for access in AccessLevel:
            self.access_combo.addItem(f"{access.name.title()} (Level {access.value})", access.value)
        form_layout.addRow("Access Level:", self.access_combo)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Tags separated by commas...")
        form_layout.addRow("Tags:", self.tags_edit)
        
        # Constitutional compliance
        self.constitutional_check = QCheckBox("Constitutional compliance verified")
        form_layout.addRow("Compliance:", self.constitutional_check)
        
        metadata_group.setLayout(form_layout)
        layout.addWidget(metadata_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton("Upload Document")
        self.upload_btn.clicked.connect(self.upload_document)
        self.upload_btn.setEnabled(False)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.upload_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Connect validation
        self.title_edit.textChanged.connect(self.validate_form)
        self.file_path_edit.textChanged.connect(self.validate_form)
        
    def browse_file(self):
        """Browse for file to upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Document",
            "",
            "All Files (*);;PDF Files (*.pdf);;Word Documents (*.docx *.doc);;Text Files (*.txt);;Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_path_edit.setText(file_path)
            
            # Auto-populate title from filename if empty
            if not self.title_edit.text():
                filename = os.path.splitext(os.path.basename(file_path))[0]
                self.title_edit.setText(filename.replace('_', ' ').replace('-', ' ').title())
                
    def validate_form(self):
        """Validate form completeness"""
        has_file = bool(self.selected_file)
        has_title = bool(self.title_edit.text().strip())
        
        self.upload_btn.setEnabled(has_file and has_title)
        
    def upload_document(self):
        """Upload the document with metadata"""
        if not self.selected_file or not self.title_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please select a file and provide a title.")
            return
            
        try:
            user = SessionManager.get_current_user()
            
            # Prepare metadata
            metadata = {
                'title': self.title_edit.text().strip(),
                'description': self.description_edit.toPlainText().strip(),
                'category': self.category_combo.currentData(),
                'access_level': self.access_combo.currentData(),
                'tags': [tag.strip() for tag in self.tags_edit.text().split(',') if tag.strip()],
                'constitutional_compliance': self.constitutional_check.isChecked()
            }
            
            # Upload document
            success, message = self.document_manager.upload_document(
                file_path=self.selected_file,
                uploader_email=user['email'],
                metadata=metadata
            )
            
            if success:
                QMessageBox.information(self, "Success", "Document uploaded successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Upload Failed", f"Failed to upload document: {message}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload error: {str(e)}")

class FOIARequestDialog(QDialog):
    """Dialog for submitting FOIA requests"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.document_manager = DocumentManager()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Freedom of Information Act (FOIA) Request")
        self.setModal(True)
        self.resize(600, 450)
        
        layout = QVBoxLayout()
        
        # Request information
        request_group = QGroupBox("Request Information")
        form_layout = QFormLayout()
        
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Subject of your FOIA request...")
        form_layout.addRow("Subject:", self.subject_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Detailed description of requested documents or information...")
        self.description_edit.setMinimumHeight(120)
        form_layout.addRow("Description:", self.description_edit)
        
        self.keywords_edit = QLineEdit()
        self.keywords_edit.setPlaceholderText("Keywords to help locate documents...")
        form_layout.addRow("Keywords:", self.keywords_edit)
        
        self.date_range_start = QDateEdit()
        self.date_range_start.setDate(QDate.currentDate().addDays(-365))
        form_layout.addRow("Date Range Start:", self.date_range_start)
        
        self.date_range_end = QDateEdit()
        self.date_range_end.setDate(QDate.currentDate())
        form_layout.addRow("Date Range End:", self.date_range_end)
        
        request_group.setLayout(form_layout)
        layout.addWidget(request_group)
        
        # Requester information
        requester_group = QGroupBox("Requester Information")
        requester_layout = QFormLayout()
        
        user = SessionManager.get_current_user()
        
        self.requester_email = QLineEdit()
        self.requester_email.setText(user.get('email', ''))
        self.requester_email.setReadOnly(True)
        requester_layout.addRow("Email:", self.requester_email)
        
        self.requester_name = QLineEdit()
        self.requester_name.setPlaceholderText("Your full name...")
        requester_layout.addRow("Full Name:", self.requester_name)
        
        self.organization = QLineEdit()
        self.organization.setPlaceholderText("Organization (if applicable)...")
        requester_layout.addRow("Organization:", self.organization)
        
        self.purpose = QComboBox()
        self.purpose.addItems([
            "Personal Use",
            "Academic Research", 
            "News Media",
            "Commercial Use",
            "Legal Proceedings",
            "Public Interest",
            "Other"
        ])
        requester_layout.addRow("Purpose:", self.purpose)
        
        requester_group.setLayout(requester_layout)
        layout.addWidget(requester_group)
        
        # Delivery preferences
        delivery_group = QGroupBox("Delivery Preferences")
        delivery_layout = QFormLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Electronic (PDF)",
            "Electronic (Original Format)",
            "Physical Copies",
            "Either Electronic or Physical"
        ])
        delivery_layout.addRow("Preferred Format:", self.format_combo)
        
        self.fee_limit = QSpinBox()
        self.fee_limit.setRange(0, 10000)
        self.fee_limit.setValue(100)
        self.fee_limit.setSuffix(" civic tokens")
        delivery_layout.addRow("Fee Limit:", self.fee_limit)
        
        delivery_group.setLayout(delivery_layout)
        layout.addWidget(delivery_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.submit_btn = QPushButton("Submit FOIA Request")
        self.submit_btn.clicked.connect(self.submit_request)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.submit_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def submit_request(self):
        """Submit the FOIA request"""
        if not self.subject_edit.text().strip() or not self.description_edit.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Please provide subject and description.")
            return
            
        try:
            user = SessionManager.get_current_user()
            
            # Prepare request data
            request_data = {
                'subject': self.subject_edit.text().strip(),
                'description': self.description_edit.toPlainText().strip(),
                'keywords': self.keywords_edit.text().strip(),
                'date_range_start': self.date_range_start.date().toString('yyyy-MM-dd'),
                'date_range_end': self.date_range_end.date().toString('yyyy-MM-dd'),
                'requester_name': self.requester_name.text().strip(),
                'organization': self.organization.text().strip(),
                'purpose': self.purpose.currentText(),
                'preferred_format': self.format_combo.currentText(),
                'fee_limit': self.fee_limit.value()
            }
            
            # Submit request
            success, message = self.document_manager.submit_foia_request(
                requester_email=user['email'],
                request_data=request_data
            )
            
            if success:
                QMessageBox.information(self, "Success", 
                    "FOIA request submitted successfully! You will receive updates on processing status.")
                self.accept()
            else:
                QMessageBox.warning(self, "Submission Failed", f"Failed to submit request: {message}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Submission error: {str(e)}")

class DocumentsArchiveTab(QWidget):
    """Complete Documents & Archive management interface"""
    
    def __init__(self):
        super().__init__()
        self.document_manager = DocumentManager()
        self.current_documents = []
        self.init_ui()
        self.refresh_ui()
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_ui)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📄 Documents & Archive")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        
        user = SessionManager.get_current_user()
        user_info = QLabel(f"User: {user.get('email', 'Unknown')} | Role: {user.get('role', 'Unknown')}")
        user_info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(user_info)
        
        layout.addLayout(header_layout)
        
        # Main content with tabs
        self.tab_widget = QTabWidget()
        
        # Document Library Tab
        self.library_tab = self.create_library_tab()
        self.tab_widget.addTab(self.library_tab, "📚 Document Library")
        
        # Upload Documents Tab
        self.upload_tab = self.create_upload_tab()
        self.tab_widget.addTab(self.upload_tab, "📤 Upload Documents")
        
        # FOIA Requests Tab
        self.foia_tab = self.create_foia_tab()
        self.tab_widget.addTab(self.foia_tab, "📋 FOIA Requests")
        
        # Public Records Tab
        self.public_tab = self.create_public_tab()
        self.tab_widget.addTab(self.public_tab, "🌐 Public Records")
        
        # Archive Management Tab
        self.archive_tab = self.create_archive_tab()
        self.tab_widget.addTab(self.archive_tab, "🗄️ Archive Management")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    def create_library_tab(self):
        """Create document library interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Search and filter section
        search_group = QGroupBox("Search & Filter Documents")
        search_layout = QVBoxLayout()
        
        # Search bar
        search_bar_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search documents by title, content, tags...")
        self.search_edit.textChanged.connect(self.filter_documents)
        
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.clicked.connect(self.search_documents)
        
        search_bar_layout.addWidget(QLabel("Search:"))
        search_bar_layout.addWidget(self.search_edit)
        search_bar_layout.addWidget(self.search_btn)
        
        search_layout.addLayout(search_bar_layout)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", "")
        for category in DocumentCategory:
            self.category_filter.addItem(category.value.replace('_', ' ').title(), category.value)
        self.category_filter.currentTextChanged.connect(self.filter_documents)
        
        self.access_filter = QComboBox()
        self.access_filter.addItem("All Access Levels", "")
        for access in AccessLevel:
            self.access_filter.addItem(f"{access.name.title()}", access.value)
        self.access_filter.currentTextChanged.connect(self.filter_documents)
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses", "")
        for status in DocumentStatus:
            self.status_filter.addItem(status.value.replace('_', ' ').title(), status.value)
        self.status_filter.currentTextChanged.connect(self.filter_documents)
        
        filter_layout.addWidget(QLabel("Category:"))
        filter_layout.addWidget(self.category_filter)
        filter_layout.addWidget(QLabel("Access:"))
        filter_layout.addWidget(self.access_filter)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addStretch()
        
        search_layout.addLayout(filter_layout)
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Document list
        self.documents_table = QTableWidget()
        self.documents_table.setColumnCount(7)
        self.documents_table.setHorizontalHeaderLabels([
            "Title", "Category", "Access Level", "Status", 
            "Uploaded", "Size", "Actions"
        ])
        
        header = self.documents_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Title column stretches
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.documents_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.documents_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.documents_table)
        
        widget.setLayout(layout)
        return widget
        
    def create_upload_tab(self):
        """Create document upload interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Upload section
        upload_group = QGroupBox("Upload New Document")
        upload_layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("""
        📋 Document Upload Guidelines:
        • Ensure documents comply with transparency requirements
        • Include appropriate metadata and categorization
        • Verify constitutional compliance where applicable
        • Consider appropriate access level classification
        """)
        instructions.setStyleSheet("background: #f8f9fa; padding: 10px; border-radius: 5px; color: #495057;")
        upload_layout.addWidget(instructions)
        
        # Upload button
        upload_btn_layout = QHBoxLayout()
        
        self.upload_document_btn = QPushButton("📤 Upload New Document")
        self.upload_document_btn.clicked.connect(self.upload_document)
        self.upload_document_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        
        upload_btn_layout.addWidget(self.upload_document_btn)
        upload_btn_layout.addStretch()
        
        upload_layout.addLayout(upload_btn_layout)
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        # Recent uploads
        recent_group = QGroupBox("Recent Uploads")
        recent_layout = QVBoxLayout()
        
        self.recent_uploads_list = QListWidget()
        self.recent_uploads_list.setMaximumHeight(200)
        recent_layout.addWidget(self.recent_uploads_list)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        # Upload statistics
        stats_group = QGroupBox("Upload Statistics")
        stats_layout = QGridLayout()
        
        self.total_docs_label = QLabel("Total Documents: 0")
        self.public_docs_label = QLabel("Public Documents: 0")
        self.restricted_docs_label = QLabel("Restricted Documents: 0")
        self.storage_used_label = QLabel("Storage Used: 0 MB")
        
        stats_layout.addWidget(self.total_docs_label, 0, 0)
        stats_layout.addWidget(self.public_docs_label, 0, 1)
        stats_layout.addWidget(self.restricted_docs_label, 1, 0)
        stats_layout.addWidget(self.storage_used_label, 1, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_foia_tab(self):
        """Create FOIA requests interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # FOIA information
        info_group = QGroupBox("Freedom of Information Act (FOIA)")
        info_layout = QVBoxLayout()
        
        foia_info = QLabel("""
        📋 About FOIA Requests:
        The Freedom of Information Act provides citizens with the right to access government records.
        Submit requests for documents that are not readily available in the public records.
        
        ⏱️ Processing Time: Most requests processed within 10-20 business days
        💰 Fees: May apply for large requests or copying costs (paid in civic tokens)
        🔒 Exemptions: Some documents may be exempt from disclosure for security or privacy reasons
        """)
        foia_info.setStyleSheet("background: #e3f2fd; padding: 15px; border-radius: 5px; color: #1565c0;")
        info_layout.addWidget(foia_info)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Submit request
        submit_group = QGroupBox("Submit New FOIA Request")
        submit_layout = QVBoxLayout()
        
        submit_btn_layout = QHBoxLayout()
        
        self.submit_foia_btn = QPushButton("📋 Submit FOIA Request")
        self.submit_foia_btn.clicked.connect(self.submit_foia_request)
        self.submit_foia_btn.setStyleSheet("""
            QPushButton {
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056b3;
            }
        """)
        
        submit_btn_layout.addWidget(self.submit_foia_btn)
        submit_btn_layout.addStretch()
        
        submit_layout.addLayout(submit_btn_layout)
        submit_group.setLayout(submit_layout)
        layout.addWidget(submit_group)
        
        # My requests
        requests_group = QGroupBox("My FOIA Requests")
        requests_layout = QVBoxLayout()
        
        self.foia_requests_table = QTableWidget()
        self.foia_requests_table.setColumnCount(5)
        self.foia_requests_table.setHorizontalHeaderLabels([
            "Subject", "Submitted", "Status", "Response Due", "Actions"
        ])
        
        header = self.foia_requests_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.foia_requests_table.setAlternatingRowColors(True)
        requests_layout.addWidget(self.foia_requests_table)
        
        requests_group.setLayout(requests_layout)
        layout.addWidget(requests_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_public_tab(self):
        """Create public records interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Public records info
        info_group = QGroupBox("Public Records Access")
        info_layout = QVBoxLayout()
        
        public_info = QLabel("""
        🌐 Public Records Information:
        These documents are readily available to all citizens without requiring a formal request.
        Public records include meeting minutes, budgets, ordinances, and other transparency documents.
        
        ✅ Instant Access: Download immediately without waiting
        🆓 Free Access: No fees for standard public records
        📱 Multiple Formats: Available in PDF, original format, or plain text
        """)
        public_info.setStyleSheet("background: #f1f8e9; padding: 15px; border-radius: 5px; color: #33691e;")
        info_layout.addWidget(public_info)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Public documents browser
        browser_group = QGroupBox("Browse Public Documents")
        browser_layout = QVBoxLayout()
        
        # Category browser
        categories_layout = QHBoxLayout()
        
        self.public_category_combo = QComboBox()
        self.public_category_combo.addItem("All Public Categories", "")
        for category in DocumentCategory:
            self.public_category_combo.addItem(category.value.replace('_', ' ').title(), category.value)
        self.public_category_combo.currentTextChanged.connect(self.filter_public_documents)
        
        categories_layout.addWidget(QLabel("Category:"))
        categories_layout.addWidget(self.public_category_combo)
        categories_layout.addStretch()
        
        browser_layout.addLayout(categories_layout)
        
        # Public documents table
        self.public_documents_table = QTableWidget()
        self.public_documents_table.setColumnCount(5)
        self.public_documents_table.setHorizontalHeaderLabels([
            "Title", "Category", "Published", "Size", "Download"
        ])
        
        header = self.public_documents_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.public_documents_table.setAlternatingRowColors(True)
        browser_layout.addWidget(self.public_documents_table)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_archive_tab(self):
        """Create archive management interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Archive information
        info_group = QGroupBox("Archive Management")
        info_layout = QVBoxLayout()
        
        archive_info = QLabel("""
        🗄️ Document Archive System:
        Long-term preservation and management of historical government records.
        Ensures permanent availability of important civic documents for future generations.
        
        📚 Historical Preservation: Maintains government records indefinitely
        🔍 Advanced Search: Full-text search across archived documents
        📊 Version Control: Complete history of document changes and revisions
        """)
        archive_info.setStyleSheet("background: #fff3e0; padding: 15px; border-radius: 5px; color: #e65100;")
        info_layout.addWidget(archive_info)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Archive statistics
        stats_group = QGroupBox("Archive Statistics")
        stats_layout = QGridLayout()
        
        self.archived_count_label = QLabel("Archived Documents: 0")
        self.archive_size_label = QLabel("Archive Size: 0 GB")
        self.oldest_doc_label = QLabel("Oldest Document: N/A")
        self.retention_policy_label = QLabel("Retention Policy: Permanent")
        
        stats_layout.addWidget(self.archived_count_label, 0, 0)
        stats_layout.addWidget(self.archive_size_label, 0, 1)
        stats_layout.addWidget(self.oldest_doc_label, 1, 0)
        stats_layout.addWidget(self.retention_policy_label, 1, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Archive search
        search_group = QGroupBox("Search Archive")
        search_layout = QVBoxLayout()
        
        archive_search_layout = QHBoxLayout()
        
        self.archive_search_edit = QLineEdit()
        self.archive_search_edit.setPlaceholderText("Search historical documents...")
        
        self.archive_search_btn = QPushButton("🔍 Search Archive")
        self.archive_search_btn.clicked.connect(self.search_archive)
        
        archive_search_layout.addWidget(QLabel("Search:"))
        archive_search_layout.addWidget(self.archive_search_edit)
        archive_search_layout.addWidget(self.archive_search_btn)
        
        search_layout.addLayout(archive_search_layout)
        
        # Date range for archive search
        date_range_layout = QHBoxLayout()
        
        self.archive_start_date = QDateEdit()
        self.archive_start_date.setDate(QDate.currentDate().addYears(-10))
        
        self.archive_end_date = QDateEdit()
        self.archive_end_date.setDate(QDate.currentDate())
        
        date_range_layout.addWidget(QLabel("Date Range:"))
        date_range_layout.addWidget(self.archive_start_date)
        date_range_layout.addWidget(QLabel("to"))
        date_range_layout.addWidget(self.archive_end_date)
        date_range_layout.addStretch()
        
        search_layout.addLayout(date_range_layout)
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Archive results
        results_group = QGroupBox("Archive Search Results")
        results_layout = QVBoxLayout()
        
        self.archive_results_table = QTableWidget()
        self.archive_results_table.setColumnCount(6)
        self.archive_results_table.setHorizontalHeaderLabels([
            "Title", "Category", "Date", "Version", "Retention", "Access"
        ])
        
        header = self.archive_results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        self.archive_results_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.archive_results_table)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        widget.setLayout(layout)
        return widget
        
    def upload_document(self):
        """Open document upload dialog"""
        dialog = DocumentUploadDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_ui()
            
    def submit_foia_request(self):
        """Open FOIA request dialog"""
        dialog = FOIARequestDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_ui()
            
    def search_documents(self):
        """Perform document search"""
        search_term = self.search_edit.text().strip()
        if not search_term:
            QMessageBox.information(self, "Search", "Please enter a search term.")
            return
            
        try:
            results = self.document_manager.search_documents(
                query=search_term,
                user_email=SessionManager.get_current_user()['email']
            )
            
            if results:
                QMessageBox.information(self, "Search Results", 
                    f"Found {len(results)} documents matching your search.")
                self.display_documents(results)
            else:
                QMessageBox.information(self, "Search Results", "No documents found matching your search.")
                
        except Exception as e:
            QMessageBox.warning(self, "Search Error", f"Search failed: {str(e)}")
            
    def search_archive(self):
        """Search archived documents"""
        search_term = self.archive_search_edit.text().strip()
        if not search_term:
            QMessageBox.information(self, "Archive Search", "Please enter a search term.")
            return
            
        try:
            start_date = self.archive_start_date.date().toString('yyyy-MM-dd')
            end_date = self.archive_end_date.date().toString('yyyy-MM-dd')
            
            results = self.document_manager.search_archive(
                query=search_term,
                start_date=start_date,
                end_date=end_date,
                user_email=SessionManager.get_current_user()['email']
            )
            
            if results:
                QMessageBox.information(self, "Archive Search Results", 
                    f"Found {len(results)} archived documents matching your search.")
                self.display_archive_results(results)
            else:
                QMessageBox.information(self, "Archive Search Results", 
                    "No archived documents found matching your search.")
                
        except Exception as e:
            QMessageBox.warning(self, "Archive Search Error", f"Archive search failed: {str(e)}")
            
    def filter_documents(self):
        """Filter documents based on current filter settings"""
        try:
            filters = {
                'search': self.search_edit.text().strip(),
                'category': self.category_filter.currentData() or None,
                'access_level': self.access_filter.currentData() if self.access_filter.currentData() != "" else None,
                'status': self.status_filter.currentData() or None
            }
            
            documents = self.document_manager.get_filtered_documents(
                filters=filters,
                user_email=SessionManager.get_current_user()['email']
            )
            
            self.display_documents(documents)
            
        except Exception as e:
            print(f"Error filtering documents: {e}")
            
    def filter_public_documents(self):
        """Filter public documents"""
        try:
            category = self.public_category_combo.currentData() or None
            
            documents = self.document_manager.get_public_documents(category=category)
            self.display_public_documents(documents)
            
        except Exception as e:
            print(f"Error filtering public documents: {e}")
            
    def display_documents(self, documents):
        """Display documents in the library table"""
        self.documents_table.setRowCount(len(documents))
        
        for row, doc in enumerate(documents):
            self.documents_table.setItem(row, 0, QTableWidgetItem(doc.get('title', 'Untitled')))
            self.documents_table.setItem(row, 1, QTableWidgetItem(doc.get('category', 'Unknown')))
            self.documents_table.setItem(row, 2, QTableWidgetItem(f"Level {doc.get('access_level', 0)}"))
            self.documents_table.setItem(row, 3, QTableWidgetItem(doc.get('status', 'Unknown')))
            
            # Format upload date
            upload_date = doc.get('uploaded_at', '')
            if upload_date:
                try:
                    dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d')
                except:
                    formatted_date = upload_date
            else:
                formatted_date = 'Unknown'
            self.documents_table.setItem(row, 4, QTableWidgetItem(formatted_date))
            
            # File size
            file_size = doc.get('file_size', 0)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 0 else "Unknown"
            self.documents_table.setItem(row, 5, QTableWidgetItem(size_str))
            
            # Actions button
            actions_btn = QPushButton("View")
            actions_btn.clicked.connect(lambda checked, doc_id=doc.get('id'): self.view_document(doc_id))
            self.documents_table.setCellWidget(row, 6, actions_btn)
            
    def display_public_documents(self, documents):
        """Display public documents"""
        self.public_documents_table.setRowCount(len(documents))
        
        for row, doc in enumerate(documents):
            self.public_documents_table.setItem(row, 0, QTableWidgetItem(doc.get('title', 'Untitled')))
            self.public_documents_table.setItem(row, 1, QTableWidgetItem(doc.get('category', 'Unknown')))
            
            # Format publish date
            publish_date = doc.get('published_at', '')
            if publish_date:
                try:
                    dt = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d')
                except:
                    formatted_date = publish_date
            else:
                formatted_date = 'Unknown'
            self.public_documents_table.setItem(row, 2, QTableWidgetItem(formatted_date))
            
            # File size
            file_size = doc.get('file_size', 0)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 0 else "Unknown"
            self.public_documents_table.setItem(row, 3, QTableWidgetItem(size_str))
            
            # Download button
            download_btn = QPushButton("📥 Download")
            download_btn.clicked.connect(lambda checked, doc_id=doc.get('id'): self.download_document(doc_id))
            self.public_documents_table.setCellWidget(row, 4, download_btn)
            
    def display_archive_results(self, results):
        """Display archive search results"""
        self.archive_results_table.setRowCount(len(results))
        
        for row, doc in enumerate(results):
            self.archive_results_table.setItem(row, 0, QTableWidgetItem(doc.get('title', 'Untitled')))
            self.archive_results_table.setItem(row, 1, QTableWidgetItem(doc.get('category', 'Unknown')))
            
            # Format date
            doc_date = doc.get('date', '')
            if doc_date:
                try:
                    dt = datetime.fromisoformat(doc_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d')
                except:
                    formatted_date = doc_date
            else:
                formatted_date = 'Unknown'
            self.archive_results_table.setItem(row, 2, QTableWidgetItem(formatted_date))
            
            self.archive_results_table.setItem(row, 3, QTableWidgetItem(f"v{doc.get('version', '1.0')}"))
            self.archive_results_table.setItem(row, 4, QTableWidgetItem(doc.get('retention_policy', 'Permanent')))
            
            # Access button
            access_btn = QPushButton("📖 View")
            access_btn.clicked.connect(lambda checked, doc_id=doc.get('id'): self.view_archived_document(doc_id))
            self.archive_results_table.setCellWidget(row, 5, access_btn)
            
    def view_document(self, document_id):
        """View a document"""
        try:
            user = SessionManager.get_current_user()
            success, result = self.document_manager.access_document(
                document_id=document_id,
                user_email=user['email']
            )
            
            if success:
                QMessageBox.information(self, "Document Access", 
                    f"Document accessed successfully. File path: {result}")
            else:
                QMessageBox.warning(self, "Access Denied", f"Cannot access document: {result}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view document: {str(e)}")
            
    def download_document(self, document_id):
        """Download a public document"""
        try:
            success, file_path = self.document_manager.download_public_document(document_id)
            
            if success:
                # Ask user where to save
                save_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Save Document",
                    os.path.basename(file_path),
                    "All Files (*)"
                )
                
                if save_path:
                    shutil.copy2(file_path, save_path)
                    QMessageBox.information(self, "Download Complete", f"Document saved to: {save_path}")
            else:
                QMessageBox.warning(self, "Download Failed", f"Cannot download document: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download failed: {str(e)}")
            
    def view_archived_document(self, document_id):
        """View an archived document"""
        try:
            user = SessionManager.get_current_user()
            success, result = self.document_manager.access_archived_document(
                document_id=document_id,
                user_email=user['email']
            )
            
            if success:
                QMessageBox.information(self, "Archive Access", 
                    f"Archived document accessed successfully.")
            else:
                QMessageBox.warning(self, "Access Denied", f"Cannot access archived document: {result}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view archived document: {str(e)}")
            
    def refresh_ui(self):
        """Refresh the UI with current data"""
        try:
            # Refresh document library
            self.filter_documents()
            
            # Refresh public documents
            self.filter_public_documents()
            
            # Refresh statistics
            self.update_statistics()
            
            # Refresh recent uploads
            self.update_recent_uploads()
            
            # Refresh FOIA requests
            self.update_foia_requests()
            
        except Exception as e:
            print(f"Error refreshing Documents UI: {e}")
            
    def update_statistics(self):
        """Update document statistics"""
        try:
            stats = self.document_manager.get_document_statistics()
            
            self.total_docs_label.setText(f"Total Documents: {stats.get('total_documents', 0)}")
            self.public_docs_label.setText(f"Public Documents: {stats.get('public_documents', 0)}")
            self.restricted_docs_label.setText(f"Restricted Documents: {stats.get('restricted_documents', 0)}")
            self.storage_used_label.setText(f"Storage Used: {stats.get('storage_used_mb', 0):.1f} MB")
            
            # Archive statistics
            archive_stats = self.document_manager.get_archive_statistics()
            self.archived_count_label.setText(f"Archived Documents: {archive_stats.get('archived_count', 0)}")
            self.archive_size_label.setText(f"Archive Size: {archive_stats.get('archive_size_gb', 0):.2f} GB")
            self.oldest_doc_label.setText(f"Oldest Document: {archive_stats.get('oldest_document_date', 'N/A')}")
            
        except Exception as e:
            print(f"Error updating statistics: {e}")
            
    def update_recent_uploads(self):
        """Update recent uploads list"""
        try:
            user = SessionManager.get_current_user()
            recent_uploads = self.document_manager.get_recent_uploads(user['email'], limit=10)
            
            self.recent_uploads_list.clear()
            
            for upload in recent_uploads:
                item_text = f"{upload.get('title', 'Untitled')} - {upload.get('uploaded_at', 'Unknown date')}"
                item = QListWidgetItem(item_text)
                self.recent_uploads_list.addItem(item)
                
        except Exception as e:
            print(f"Error updating recent uploads: {e}")
            
    def update_foia_requests(self):
        """Update FOIA requests table"""
        try:
            user = SessionManager.get_current_user()
            requests = self.document_manager.get_user_foia_requests(user['email'])
            
            self.foia_requests_table.setRowCount(len(requests))
            
            for row, req in enumerate(requests):
                self.foia_requests_table.setItem(row, 0, QTableWidgetItem(req.get('subject', 'Unknown')))
                self.foia_requests_table.setItem(row, 1, QTableWidgetItem(req.get('submitted_at', 'Unknown')))
                self.foia_requests_table.setItem(row, 2, QTableWidgetItem(req.get('status', 'Unknown')))
                self.foia_requests_table.setItem(row, 3, QTableWidgetItem(req.get('response_due', 'Unknown')))
                
                # Actions
                view_btn = QPushButton("View")
                view_btn.clicked.connect(lambda checked, req_id=req.get('id'): self.view_foia_request(req_id))
                self.foia_requests_table.setCellWidget(row, 4, view_btn)
                
        except Exception as e:
            print(f"Error updating FOIA requests: {e}")
            
    def view_foia_request(self, request_id):
        """View FOIA request details"""
        try:
            request_data = self.document_manager.get_foia_request(request_id)
            
            if request_data:
                # Show request details in a dialog
                QMessageBox.information(self, "FOIA Request Details", 
                    f"Subject: {request_data.get('subject', 'Unknown')}\n"
                    f"Status: {request_data.get('status', 'Unknown')}\n"
                    f"Submitted: {request_data.get('submitted_at', 'Unknown')}\n"
                    f"Description: {request_data.get('description', 'No description')}")
            else:
                QMessageBox.warning(self, "Error", "FOIA request not found.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view FOIA request: {str(e)}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test the documents archive interface
    window = DocumentsArchiveTab()
    window.show()
    
    sys.exit(app.exec_())