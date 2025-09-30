# Documents Archive UI - Document Management & Transparency Interface
# PyQt5-based document management, FOIA processing, and legislative tracking

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QProgressBar, QTextEdit, QTabWidget,
    QListWidget, QListWidgetItem, QSplitter, QGroupBox,
    QComboBox, QCheckBox, QSpinBox, QSlider, QMessageBox,
    QDialog, QDialogButtonBox, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
    QFormLayout, QGridLayout, QFileDialog, QTextBrowser
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QDate
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

# Import backend components
try:
    from documents.document_manager import DocumentManager, FOIARequestProcessor
    from users.session import SessionManager
    from blockchain.blockchain import add_user_action
except ImportError as e:
    print(f"Warning: Import error in documents UI: {e}")
    # Fallback for blockchain if import fails
    def add_user_action(action_type, user_email, data):
        print(f"Blockchain recording (fallback): {action_type} by {user_email}")
        return (True, "Recorded", None)


class DocumentUploadDialog(QDialog):
    """Dialog for uploading new documents"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upload Document")
        self.setModal(True)
        self.resize(600, 500)
        self.document_data = {}
        self.selected_file_path = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📄 Upload New Document")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # File selection
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        file_select_layout = QHBoxLayout()
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        self.file_path_display.setPlaceholderText("No file selected...")
        file_select_layout.addWidget(self.file_path_display)
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_select_layout.addWidget(browse_btn)
        
        file_layout.addLayout(file_select_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Document metadata
        metadata_group = QGroupBox("Document Information")
        form = QFormLayout()
        
        self.doc_title = QLineEdit()
        self.doc_title.setPlaceholderText("Enter document title...")
        form.addRow("Title:", self.doc_title)
        
        self.doc_type = QComboBox()
        self.doc_type.addItems([
            "Legislative Bill",
            "Policy Document", 
            "Meeting Minutes",
            "Budget Document",
            "Contract/Agreement",
            "Legal Opinion",
            "Research Report",
            "Public Notice",
            "Correspondence",
            "Administrative Record",
            "Other"
        ])
        form.addRow("Document Type:", self.doc_type)
        
        self.description = QTextEdit()
        self.description.setPlaceholderText("Describe the document content and purpose...")
        self.description.setMaximumHeight(80)
        form.addRow("Description:", self.description)
        
        self.author = QLineEdit()
        self.author.setPlaceholderText("Document author or department...")
        form.addRow("Author:", self.author)
        
        self.classification = QComboBox()
        self.classification.addItems([
            "Public",
            "Internal",
            "Confidential",
            "Restricted"
        ])
        form.addRow("Classification:", self.classification)
        
        self.jurisdiction = QComboBox()
        self.jurisdiction.addItems([
            "City",
            "County", 
            "State",
            "Federal",
            "Multi-Jurisdictional"
        ])
        form.addRow("Jurisdiction:", self.jurisdiction)
        
        self.department = QLineEdit()
        self.department.setPlaceholderText("Originating department...")
        form.addRow("Department:", self.department)
        
        # Tags for searchability
        self.tags = QLineEdit()
        self.tags.setPlaceholderText("Enter tags separated by commas...")
        form.addRow("Tags:", self.tags)
        
        metadata_group.setLayout(form)
        layout.addWidget(metadata_group)
        
        # Visibility and access
        access_group = QGroupBox("Access Control")
        access_layout = QFormLayout()
        
        self.public_access = QCheckBox("Make publicly accessible")
        self.public_access.setChecked(True)
        access_layout.addWidget(self.public_access)
        
        self.searchable = QCheckBox("Include in public search")
        self.searchable.setChecked(True)
        access_layout.addWidget(self.searchable)
        
        self.retention_period = QComboBox()
        self.retention_period.addItems([
            "Permanent",
            "25 years",
            "10 years",
            "7 years",
            "5 years",
            "3 years"
        ])
        access_layout.addRow("Retention Period:", self.retention_period)
        
        access_group.setLayout(access_layout)
        layout.addWidget(access_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def browse_file(self):
        """Browse for file to upload"""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Document to Upload",
            "",
            "All Files (*);;PDF Files (*.pdf);;Word Documents (*.docx);;Text Files (*.txt)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            self.file_path_display.setText(file_path)
            
            # Auto-populate title from filename if empty
            if not self.doc_title.text():
                filename = os.path.basename(file_path)
                title = os.path.splitext(filename)[0].replace('_', ' ').title()
                self.doc_title.setText(title)
    
    def accept(self):
        """Validate and collect document data"""
        
        if not self.selected_file_path:
            QMessageBox.warning(self, "Validation Error", "Please select a file to upload.")
            return
        
        if not self.doc_title.text().strip():
            QMessageBox.warning(self, "Validation Error", "Document title is required.")
            return
        
        if not self.description.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Document description is required.")
            return
        
        self.document_data = {
            'file_path': self.selected_file_path,
            'title': self.doc_title.text().strip(),
            'type': self.doc_type.currentText(),
            'description': self.description.toPlainText().strip(),
            'author': self.author.text().strip(),
            'classification': self.classification.currentText(),
            'jurisdiction': self.jurisdiction.currentText(),
            'department': self.department.text().strip(),
            'tags': [tag.strip() for tag in self.tags.text().split(',') if tag.strip()],
            'public_access': self.public_access.isChecked(),
            'searchable': self.searchable.isChecked(),
            'retention_period': self.retention_period.currentText(),
            'uploaded_by': "current_user"  # Will be populated by parent
        }
        
        super().accept()


class FOIARequestDialog(QDialog):
    """Dialog for submitting FOIA requests"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Submit FOIA Request")
        self.setModal(True)
        self.resize(600, 500)
        self.request_data = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📋 Freedom of Information Act Request")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # FOIA information
        info_text = QLabel(
            "Submit a request to access government documents and records. "
            "All FOIA requests are processed according to applicable laws and regulations."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("QLabel { background-color: #f0f8ff; padding: 10px; border-radius: 5px; }")
        layout.addWidget(info_text)
        
        # Request form
        form = QFormLayout()
        
        # Requester information
        requester_group = QGroupBox("Requester Information")
        requester_layout = QFormLayout()
        
        self.requester_name = QLineEdit()
        self.requester_name.setPlaceholderText("Full name...")
        requester_layout.addRow("Name:", self.requester_name)
        
        self.requester_email = QLineEdit()
        self.requester_email.setPlaceholderText("Email address...")
        requester_layout.addRow("Email:", self.requester_email)
        
        self.requester_phone = QLineEdit()
        self.requester_phone.setPlaceholderText("Phone number (optional)...")
        requester_layout.addRow("Phone:", self.requester_phone)
        
        self.requester_address = QTextEdit()
        self.requester_address.setPlaceholderText("Mailing address...")
        self.requester_address.setMaximumHeight(60)
        requester_layout.addRow("Address:", self.requester_address)
        
        requester_group.setLayout(requester_layout)
        layout.addWidget(requester_group)
        
        # Request details
        request_group = QGroupBox("Request Details")
        request_layout = QFormLayout()
        
        self.request_subject = QLineEdit()
        self.request_subject.setPlaceholderText("Brief subject of your request...")
        request_layout.addRow("Subject:", self.request_subject)
        
        self.request_description = QTextEdit()
        self.request_description.setPlaceholderText(
            "Provide a detailed description of the documents or information you are seeking. "
            "Be as specific as possible to help us locate the requested records."
        )
        self.request_description.setMinimumHeight(100)
        request_layout.addRow("Description:", self.request_description)
        
        self.date_range_start = QDateEdit()
        self.date_range_start.setDate(QDate.currentDate().addYears(-1))
        request_layout.addRow("Date Range Start:", self.date_range_start)
        
        self.date_range_end = QDateEdit()
        self.date_range_end.setDate(QDate.currentDate())
        request_layout.addRow("Date Range End:", self.date_range_end)
        
        self.department = QLineEdit()
        self.department.setPlaceholderText("Specific department or agency...")
        request_layout.addRow("Department:", self.department)
        
        request_group.setLayout(request_layout)
        layout.addWidget(request_group)
        
        # Delivery preferences
        delivery_group = QGroupBox("Delivery Preferences")
        delivery_layout = QFormLayout()
        
        self.delivery_method = QComboBox()
        self.delivery_method.addItems([
            "Electronic (Email)",
            "Physical Mail",
            "In-Person Pickup"
        ])
        delivery_layout.addRow("Delivery Method:", self.delivery_method)
        
        self.format_preference = QComboBox()
        self.format_preference.addItems([
            "Digital Copy (PDF)",
            "Physical Copy",
            "Either Format"
        ])
        delivery_layout.addRow("Format:", self.format_preference)
        
        delivery_group.setLayout(delivery_layout)
        layout.addWidget(delivery_group)
        
        # Fee information
        fee_info = QLabel(
            "Note: Processing fees may apply for extensive requests. "
            "You will be notified of any fees before processing begins."
        )
        fee_info.setWordWrap(True)
        fee_info.setStyleSheet("QLabel { font-style: italic; color: #666; }")
        layout.addWidget(fee_info)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def accept(self):
        """Validate and collect FOIA request data"""
        
        if not self.requester_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "Requester name is required.")
            return
        
        if not self.requester_email.text().strip():
            QMessageBox.warning(self, "Validation Error", "Email address is required.")
            return
        
        if not self.request_subject.text().strip():
            QMessageBox.warning(self, "Validation Error", "Request subject is required.")
            return
        
        if not self.request_description.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Request description is required.")
            return
        
        self.request_data = {
            'requester_name': self.requester_name.text().strip(),
            'requester_email': self.requester_email.text().strip(),
            'requester_phone': self.requester_phone.text().strip(),
            'requester_address': self.requester_address.toPlainText().strip(),
            'subject': self.request_subject.text().strip(),
            'description': self.request_description.toPlainText().strip(),
            'date_range_start': self.date_range_start.date().toString("yyyy-MM-dd"),
            'date_range_end': self.date_range_end.date().toString("yyyy-MM-dd"),
            'department': self.department.text().strip(),
            'delivery_method': self.delivery_method.currentText(),
            'format_preference': self.format_preference.currentText(),
            'submitted_by': "current_user"  # Will be populated by parent
        }
        
        super().accept()


class DocumentViewerDialog(QDialog):
    """Dialog for viewing document details and content"""
    
    def __init__(self, document_data, parent=None):
        super().__init__(parent)
        self.document_data = document_data
        self.setWindowTitle(f"Document: {document_data.get('title', 'Unknown')}")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"📄 {self.document_data.get('title', 'Document')}")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # Document metadata
        metadata_group = QGroupBox("Document Information")
        metadata_layout = QFormLayout()
        
        metadata_fields = [
            ("Type", "type"),
            ("Author", "author"),
            ("Department", "department"),
            ("Classification", "classification"),
            ("Jurisdiction", "jurisdiction"),
            ("Created", "created_at"),
            ("File Size", "file_size"),
            ("Format", "file_format")
        ]
        
        for label, field in metadata_fields:
            value = self.document_data.get(field, "N/A")
            metadata_layout.addRow(f"{label}:", QLabel(str(value)))
        
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)
        
        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()
        
        description = QTextBrowser()
        description.setPlainText(self.document_data.get('description', 'No description available.'))
        description.setMaximumHeight(100)
        desc_layout.addWidget(description)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Tags
        if self.document_data.get('tags'):
            tags_group = QGroupBox("Tags")
            tags_layout = QVBoxLayout()
            
            tags_text = ", ".join(self.document_data['tags'])
            tags_label = QLabel(tags_text)
            tags_label.setWordWrap(True)
            tags_layout.addWidget(tags_label)
            
            tags_group.setLayout(tags_layout)
            layout.addWidget(tags_group)
        
        # Version history
        if self.document_data.get('versions'):
            versions_group = QGroupBox("Version History")
            versions_layout = QVBoxLayout()
            
            versions_table = QTableWidget()
            versions_table.setColumnCount(4)
            versions_table.setHorizontalHeaderLabels(["Version", "Date", "Author", "Changes"])
            
            versions = self.document_data['versions']
            versions_table.setRowCount(len(versions))
            
            for i, version in enumerate(versions):
                versions_table.setItem(i, 0, QTableWidgetItem(version.get('version', 'N/A')))
                versions_table.setItem(i, 1, QTableWidgetItem(version.get('date', 'N/A')))
                versions_table.setItem(i, 2, QTableWidgetItem(version.get('author', 'N/A')))
                versions_table.setItem(i, 3, QTableWidgetItem(version.get('changes', 'N/A')))
            
            versions_table.resizeColumnsToContents()
            versions_layout.addWidget(versions_table)
            
            versions_group.setLayout(versions_layout)
            layout.addWidget(versions_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        download_btn = QPushButton("💾 Download")
        download_btn.clicked.connect(self.download_document)
        button_layout.addWidget(download_btn)
        
        share_btn = QPushButton("🔗 Share")
        share_btn.clicked.connect(self.share_document)
        button_layout.addWidget(share_btn)
        
        version_btn = QPushButton("📝 New Version")
        version_btn.clicked.connect(self.create_new_version)
        button_layout.addWidget(version_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("✖️ Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def download_document(self):
        """Download the document"""
        QMessageBox.information(self, "Download", "Document download would start here.")
    
    def share_document(self):
        """Share the document"""
        QMessageBox.information(self, "Share", "Document sharing options would be displayed here.")
    
    def create_new_version(self):
        """Create a new version of the document"""
        QMessageBox.information(self, "New Version", "New version creation dialog would open here.")


class DocumentsArchiveTab(QWidget):
    """Main Documents & Archive Tab widget"""
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.document_manager = None
        self.foia_processor = None
        self.init_ui()
        self.load_user_session()
    
    def init_ui(self):
        """Initialize the documents archive interface"""
        
        layout = QVBoxLayout()
        
        # Tab header
        header_layout = QHBoxLayout()
        
        title = QLabel("📄 Documents & Archive Management")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Quick action buttons
        upload_btn = QPushButton("📤 Upload Document")
        upload_btn.clicked.connect(self.upload_document)
        header_layout.addWidget(upload_btn)
        
        foia_btn = QPushButton("📋 FOIA Request")
        foia_btn.clicked.connect(self.submit_foia_request)
        header_layout.addWidget(foia_btn)
        
        layout.addLayout(header_layout)
        
        # Main content tabs
        self.content_tabs = QTabWidget()
        
        # Document library tab
        self.library_tab = QWidget()
        self.init_library_tab()
        self.content_tabs.addTab(self.library_tab, "📚 Document Library")
        
        # FOIA requests tab
        self.foia_tab = QWidget()
        self.init_foia_tab()
        self.content_tabs.addTab(self.foia_tab, "📋 FOIA Requests")
        
        # Legislative tracking tab
        self.legislative_tab = QWidget()
        self.init_legislative_tab()
        self.content_tabs.addTab(self.legislative_tab, "🏛️ Legislative Tracking")
        
        # Archives tab
        self.archives_tab = QWidget()
        self.init_archives_tab()
        self.content_tabs.addTab(self.archives_tab, "📦 Archives")
        
        layout.addWidget(self.content_tabs)
        
        self.setLayout(layout)
    
    def init_library_tab(self):
        """Initialize the document library tab"""
        
        layout = QVBoxLayout()
        
        # Search and filters
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search documents by title, content, or tags...")
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self.search_documents)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Filter row
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "All Types", "Legislative Bill", "Policy Document", "Meeting Minutes",
            "Budget Document", "Contract/Agreement", "Legal Opinion", "Research Report"
        ])
        filter_layout.addWidget(self.type_filter)
        
        self.classification_filter = QComboBox()
        self.classification_filter.addItems(["All Classifications", "Public", "Internal", "Confidential"])
        filter_layout.addWidget(self.classification_filter)
        
        self.jurisdiction_filter = QComboBox()
        self.jurisdiction_filter.addItems(["All Jurisdictions", "City", "County", "State", "Federal"])
        filter_layout.addWidget(self.jurisdiction_filter)
        
        filter_btn = QPushButton("Apply Filters")
        filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(filter_btn)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Documents table
        self.documents_table = QTableWidget()
        self.documents_table.setColumnCount(7)
        self.documents_table.setHorizontalHeaderLabels([
            "Title", "Type", "Author", "Department", "Date", "Classification", "Actions"
        ])
        
        # Sample documents
        sample_documents = [
            {
                "title": "City Budget 2024",
                "type": "Budget Document",
                "author": "Finance Department",
                "department": "Finance",
                "date": "2024-01-15",
                "classification": "Public"
            },
            {
                "title": "Transportation Policy Update",
                "type": "Policy Document",
                "author": "Planning Commission",
                "department": "Planning",
                "date": "2024-01-10",
                "classification": "Public"
            },
            {
                "title": "City Council Minutes - January",
                "type": "Meeting Minutes",
                "author": "City Clerk",
                "department": "Administration",
                "date": "2024-01-08",
                "classification": "Public"
            },
            {
                "title": "Infrastructure Assessment Report",
                "type": "Research Report",
                "author": "Engineering Department",
                "department": "Public Works",
                "date": "2024-01-05",
                "classification": "Internal"
            }
        ]
        
        self.documents_table.setRowCount(len(sample_documents))
        
        for i, doc in enumerate(sample_documents):
            self.documents_table.setItem(i, 0, QTableWidgetItem(doc["title"]))
            self.documents_table.setItem(i, 1, QTableWidgetItem(doc["type"]))
            self.documents_table.setItem(i, 2, QTableWidgetItem(doc["author"]))
            self.documents_table.setItem(i, 3, QTableWidgetItem(doc["department"]))
            self.documents_table.setItem(i, 4, QTableWidgetItem(doc["date"]))
            self.documents_table.setItem(i, 5, QTableWidgetItem(doc["classification"]))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QPushButton("👁️ View")
            view_btn.clicked.connect(lambda checked, title=doc["title"]: self.view_document(title))
            actions_layout.addWidget(view_btn)
            
            download_btn = QPushButton("💾 Download")
            download_btn.clicked.connect(lambda checked, title=doc["title"]: self.download_document(title))
            actions_layout.addWidget(download_btn)
            
            actions_widget.setLayout(actions_layout)
            self.documents_table.setCellWidget(i, 6, actions_widget)
        
        self.documents_table.resizeColumnsToContents()
        layout.addWidget(self.documents_table)
        
        self.library_tab.setLayout(layout)
    
    def init_foia_tab(self):
        """Initialize the FOIA requests tab"""
        
        layout = QVBoxLayout()
        
        # FOIA header
        header_layout = QHBoxLayout()
        
        header = QLabel("📋 Freedom of Information Act Requests")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        new_request_btn = QPushButton("➕ New FOIA Request")
        new_request_btn.clicked.connect(self.submit_foia_request)
        header_layout.addWidget(new_request_btn)
        
        layout.addLayout(header_layout)
        
        # FOIA requests table
        self.foia_table = QTableWidget()
        self.foia_table.setColumnCount(7)
        self.foia_table.setHorizontalHeaderLabels([
            "Request ID", "Subject", "Requester", "Date Submitted", "Status", "Due Date", "Actions"
        ])
        
        # Sample FOIA requests
        sample_requests = [
            {
                "id": "FOIA-2024-001",
                "subject": "Budget Planning Documents 2023",
                "requester": "John Citizen",
                "date": "2024-01-15",
                "status": "Under Review",
                "due_date": "2024-02-15"
            },
            {
                "id": "FOIA-2024-002",
                "subject": "Police Department Policies",
                "requester": "News Media Corp",
                "date": "2024-01-12",
                "status": "Processing",
                "due_date": "2024-02-12"
            },
            {
                "id": "FOIA-2024-003",
                "subject": "City Council Email Records",
                "requester": "Transparency Watch",
                "date": "2024-01-10",
                "status": "Completed",
                "due_date": "2024-02-10"
            }
        ]
        
        self.foia_table.setRowCount(len(sample_requests))
        
        for i, request in enumerate(sample_requests):
            self.foia_table.setItem(i, 0, QTableWidgetItem(request["id"]))
            self.foia_table.setItem(i, 1, QTableWidgetItem(request["subject"]))
            self.foia_table.setItem(i, 2, QTableWidgetItem(request["requester"]))
            self.foia_table.setItem(i, 3, QTableWidgetItem(request["date"]))
            self.foia_table.setItem(i, 4, QTableWidgetItem(request["status"]))
            self.foia_table.setItem(i, 5, QTableWidgetItem(request["due_date"]))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QPushButton("👁️ View")
            view_btn.clicked.connect(lambda checked, req_id=request["id"]: self.view_foia_request(req_id))
            actions_layout.addWidget(view_btn)
            
            process_btn = QPushButton("⚙️ Process")
            process_btn.clicked.connect(lambda checked, req_id=request["id"]: self.process_foia_request(req_id))
            actions_layout.addWidget(process_btn)
            
            actions_widget.setLayout(actions_layout)
            self.foia_table.setCellWidget(i, 6, actions_widget)
        
        self.foia_table.resizeColumnsToContents()
        layout.addWidget(self.foia_table)
        
        self.foia_tab.setLayout(layout)
    
    def init_legislative_tab(self):
        """Initialize the legislative tracking tab"""
        
        layout = QVBoxLayout()
        
        # Legislative header
        header = QLabel("🏛️ Legislative Document Tracking")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Bills and legislation table
        self.legislative_table = QTableWidget()
        self.legislative_table.setColumnCount(6)
        self.legislative_table.setHorizontalHeaderLabels([
            "Bill Number", "Title", "Sponsor", "Status", "Last Action", "Actions"
        ])
        
        # Sample legislative items
        sample_bills = [
            {
                "number": "CB-2024-001",
                "title": "Municipal Broadband Infrastructure Act",
                "sponsor": "Councilmember Smith",
                "status": "Committee Review",
                "last_action": "2024-01-15 - Referred to Technology Committee"
            },
            {
                "number": "CB-2024-002", 
                "title": "Green Energy Incentive Program",
                "sponsor": "Councilmember Johnson",
                "status": "First Reading",
                "last_action": "2024-01-12 - Introduced in Council"
            },
            {
                "number": "CB-2024-003",
                "title": "Affordable Housing Development Fund",
                "sponsor": "Councilmember Davis",
                "status": "Passed",
                "last_action": "2024-01-10 - Signed by Mayor"
            }
        ]
        
        self.legislative_table.setRowCount(len(sample_bills))
        
        for i, bill in enumerate(sample_bills):
            self.legislative_table.setItem(i, 0, QTableWidgetItem(bill["number"]))
            self.legislative_table.setItem(i, 1, QTableWidgetItem(bill["title"]))
            self.legislative_table.setItem(i, 2, QTableWidgetItem(bill["sponsor"]))
            self.legislative_table.setItem(i, 3, QTableWidgetItem(bill["status"]))
            self.legislative_table.setItem(i, 4, QTableWidgetItem(bill["last_action"]))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            track_btn = QPushButton("📊 Track")
            track_btn.clicked.connect(lambda checked, num=bill["number"]: self.track_legislation(num))
            actions_layout.addWidget(track_btn)
            
            history_btn = QPushButton("📜 History")
            history_btn.clicked.connect(lambda checked, num=bill["number"]: self.view_legislative_history(num))
            actions_layout.addWidget(history_btn)
            
            actions_widget.setLayout(actions_layout)
            self.legislative_table.setCellWidget(i, 5, actions_widget)
        
        self.legislative_table.resizeColumnsToContents()
        layout.addWidget(self.legislative_table)
        
        self.legislative_tab.setLayout(layout)
    
    def init_archives_tab(self):
        """Initialize the archives tab"""
        
        layout = QVBoxLayout()
        
        # Archives header
        header = QLabel("📦 Document Archives")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Archive statistics
        stats_layout = QGridLayout()
        
        stats = [
            ("Total Documents", "1,247"),
            ("Archive Size", "45.2 GB"),
            ("Retention Policies", "12"),
            ("Public Records", "892"),
            ("Restricted Access", "355"),
            ("Average Age", "3.5 years")
        ]
        
        for i, (label, value) in enumerate(stats):
            card = self.create_stats_card(label, value)
            row = i // 3
            col = i % 3
            stats_layout.addWidget(card, row, col)
        
        layout.addLayout(stats_layout)
        
        # Archive management
        management_group = QGroupBox("Archive Management")
        management_layout = QVBoxLayout()
        
        management_buttons = [
            ("🔍 Search Archives", self.search_archives),
            ("📊 Generate Report", self.generate_archive_report),
            ("🗂️ Manage Retention", self.manage_retention_policies),
            ("💾 Backup Archives", self.backup_archives),
            ("🔧 Maintenance", self.archive_maintenance)
        ]
        
        for button_text, handler in management_buttons:
            btn = QPushButton(button_text)
            btn.clicked.connect(handler)
            management_layout.addWidget(btn)
        
        management_group.setLayout(management_layout)
        layout.addWidget(management_group)
        
        # Recent archive activity
        activity_group = QGroupBox("Recent Archive Activity")
        activity_layout = QVBoxLayout()
        
        activities = [
            "📄 City Budget 2024 archived with 25-year retention",
            "🗂️ Transportation study moved to permanent archive",
            "💾 Monthly backup completed successfully",
            "🔍 FOIA search completed: 47 documents found",
            "📊 Quarterly archive report generated"
        ]
        
        for activity in activities:
            activity_label = QLabel(activity)
            activity_layout.addWidget(activity_label)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        self.archives_tab.setLayout(layout)
    
    def create_stats_card(self, title, value):
        """Create a statistics display card"""
        
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 5px; padding: 10px; }")
        
        layout = QVBoxLayout()
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 16, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        card.setLayout(layout)
        return card
    
    def load_user_session(self):
        """Load current user session"""
        
        try:
            # Mock current user for testing
            self.current_user = {
                'email': 'test@example.com',
                'role': 'Contract Representative',
                'department': 'Administration'
            }
            
            if self.current_user:
                self.init_backend_managers()
        except Exception as e:
            print(f"Error loading user session: {e}")
    
    def init_backend_managers(self):
        """Initialize backend management systems"""
        
        try:
            self.document_manager = DocumentManager()
            self.foia_processor = FOIARequestProcessor()
            print("Document managers initialized successfully")
        except Exception as e:
            print(f"Error initializing document managers: {e}")
            self.document_manager = None
            self.foia_processor = None
    
    def upload_document(self):
        """Upload a new document"""
        
        if not self.current_user:
            QMessageBox.warning(self, "Authentication Required", 
                               "Please log in to upload documents.")
            return
        
        if not self.document_manager:
            QMessageBox.warning(self, "Error", 
                               "Document manager not initialized.")
            return
        
        dialog = DocumentUploadDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            document_data = dialog.document_data
            document_data['uploaded_by'] = self.current_user.get('email')
            file_path = dialog.selected_file_path
            
            if not file_path:
                QMessageBox.warning(self, "Error", "No file selected.")
                return
            
            try:
                success, message = self.document_manager.upload_document(document_data, file_path)
                
                if success:
                    QMessageBox.information(self, "Success", 
                                          f"Document '{document_data['title']}' uploaded successfully!\n\n{message}")
                    # Refresh documents table
                    self.refresh_documents_table()
                else:
                    QMessageBox.warning(self, "Error", message)
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to upload document: {e}")
    
    def submit_foia_request(self):
        """Submit a new FOIA request"""
        
        if not self.foia_processor:
            QMessageBox.warning(self, "Error", 
                               "FOIA processor not initialized.")
            return
        
        dialog = FOIARequestDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            request_data = dialog.request_data
            
            if self.current_user:
                request_data['submitted_by'] = self.current_user.get('email')
            
            try:
                success, message = self.foia_processor.submit_request(request_data)
                
                if success:
                    QMessageBox.information(self, "FOIA Request Submitted", 
                                          f"Your FOIA request has been submitted successfully.\n\n"
                                          f"{message}\n\n"
                                          f"You will receive updates via email.")
                    # Refresh FOIA table
                    self.refresh_foia_table()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to submit FOIA request: {message}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to submit FOIA request: {e}")
    
    def search_documents(self):
        """Search documents based on query"""
        
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.information(self, "Search", "Please enter a search term.")
            return
        
        if not self.document_manager:
            QMessageBox.warning(self, "Error", "Document manager not initialized.")
            return
        
        try:
            # Get filter values
            filters = {
                'type': self.type_filter.currentText() if self.type_filter.currentText() != "All Types" else None,
                'classification': self.classification_filter.currentText() if self.classification_filter.currentText() != "All Classifications" else None,
                'jurisdiction': self.jurisdiction_filter.currentText() if self.jurisdiction_filter.currentText() != "All Jurisdictions" else None
            }
            
            results = self.document_manager.search_documents(query, filters)
            
            if results:
                # Update document table with search results
                self.documents_table.setRowCount(len(results))
                
                for i, doc in enumerate(results):
                    self.documents_table.setItem(i, 0, QTableWidgetItem(doc.get('title', 'N/A')))
                    self.documents_table.setItem(i, 1, QTableWidgetItem(doc.get('type', 'N/A')))
                    self.documents_table.setItem(i, 2, QTableWidgetItem(doc.get('uploaded_by', 'N/A')))
                    self.documents_table.setItem(i, 3, QTableWidgetItem(doc.get('department', 'N/A')))
                    self.documents_table.setItem(i, 4, QTableWidgetItem(doc.get('created_at', 'N/A')[:10]))
                    self.documents_table.setItem(i, 5, QTableWidgetItem(doc.get('classification', 'N/A')))
                    
                    # Action buttons
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout()
                    actions_layout.setContentsMargins(2, 2, 2, 2)
                    
                    view_btn = QPushButton("👁️ View")
                    view_btn.clicked.connect(lambda checked, title=doc['title']: self.view_document(title))
                    actions_layout.addWidget(view_btn)
                    
                    download_btn = QPushButton("💾 Download")
                    download_btn.clicked.connect(lambda checked, title=doc['title']: self.download_document(title))
                    actions_layout.addWidget(download_btn)
                    
                    actions_widget.setLayout(actions_layout)
                    self.documents_table.setCellWidget(i, 6, actions_widget)
                
                self.documents_table.resizeColumnsToContents()
                
                QMessageBox.information(self, "Search Results", 
                                       f"Found {len(results)} document(s) matching '{query}'")
            else:
                QMessageBox.information(self, "Search Results", 
                                       f"No documents found matching '{query}'")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {e}")
    
    def apply_filters(self):
        """Apply filters to document list"""
        
        if not self.document_manager:
            QMessageBox.warning(self, "Error", "Document manager not initialized.")
            return
        
        try:
            # Get all documents and apply filters
            all_documents = self.document_manager.get_public_documents()
            
            # Get filter values
            type_filter = self.type_filter.currentText()
            classification_filter = self.classification_filter.currentText()
            jurisdiction_filter = self.jurisdiction_filter.currentText()
            
            filtered_docs = []
            for doc in all_documents:
                # Apply type filter
                if type_filter != "All Types" and doc.get('type') != type_filter:
                    continue
                
                # Apply classification filter
                if classification_filter != "All Classifications" and doc.get('classification') != classification_filter:
                    continue
                
                # Apply jurisdiction filter
                if jurisdiction_filter != "All Jurisdictions" and doc.get('jurisdiction') != jurisdiction_filter:
                    continue
                
                filtered_docs.append(doc)
            
            # Update table with filtered results
            self.documents_table.setRowCount(len(filtered_docs))
            
            for i, doc in enumerate(filtered_docs):
                self.documents_table.setItem(i, 0, QTableWidgetItem(doc.get('title', 'N/A')))
                self.documents_table.setItem(i, 1, QTableWidgetItem(doc.get('type', 'N/A')))
                self.documents_table.setItem(i, 2, QTableWidgetItem(doc.get('uploaded_by', 'N/A')))
                self.documents_table.setItem(i, 3, QTableWidgetItem(doc.get('department', 'N/A')))
                self.documents_table.setItem(i, 4, QTableWidgetItem(doc.get('created_at', 'N/A')[:10]))
                self.documents_table.setItem(i, 5, QTableWidgetItem(doc.get('classification', 'N/A')))
                
                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(2, 2, 2, 2)
                
                view_btn = QPushButton("👁️ View")
                view_btn.clicked.connect(lambda checked, title=doc['title']: self.view_document(title))
                actions_layout.addWidget(view_btn)
                
                download_btn = QPushButton("💾 Download")
                download_btn.clicked.connect(lambda checked, title=doc['title']: self.download_document(title))
                actions_layout.addWidget(download_btn)
                
                actions_widget.setLayout(actions_layout)
                self.documents_table.setCellWidget(i, 6, actions_widget)
            
            self.documents_table.resizeColumnsToContents()
            
            QMessageBox.information(self, "Filters Applied", 
                                   f"Showing {len(filtered_docs)} document(s) matching selected filters.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply filters: {e}")
    
    def view_document(self, title):
        """View document details"""
        
        if not self.document_manager:
            QMessageBox.warning(self, "Error", "Document manager not initialized.")
            return
        
        try:
            # Find document by title
            data = self.document_manager.load_data()
            document = next((d for d in data['documents'] if d['title'] == title), None)
            
            if not document:
                QMessageBox.warning(self, "Not Found", f"Document '{title}' not found.")
                return
            
            # Get document versions
            versions = self.document_manager.get_document_versions(document['id'])
            
            # Prepare document data for viewer
            document_data = {
                'title': document.get('title', 'N/A'),
                'type': document.get('type', 'N/A'),
                'author': document.get('uploaded_by', 'N/A'),
                'department': document.get('department', 'N/A'),
                'classification': document.get('classification', 'N/A'),
                'jurisdiction': document.get('jurisdiction', 'N/A'),
                'created_at': document.get('created_at', 'N/A')[:10] if document.get('created_at') else 'N/A',
                'file_size': document.get('file_info', {}).get('file_size', 'N/A'),
                'file_format': document.get('file_info', {}).get('mime_type', 'N/A'),
                'description': document.get('description', 'No description available'),
                'tags': document.get('tags', []),
                'versions': [
                    {
                        'version': v.get('version_number', 'N/A'),
                        'date': v.get('created_at', 'N/A')[:10] if v.get('created_at') else 'N/A',
                        'author': v.get('modified_by', 'N/A'),
                        'changes': v.get('changes_description', 'N/A')
                    }
                    for v in versions
                ]
            }
            
            dialog = DocumentViewerDialog(document_data, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view document: {e}")
    
    def download_document(self, title):
        """Download a document"""
        
        if not self.document_manager:
            QMessageBox.warning(self, "Error", "Document manager not initialized.")
            return
        
        try:
            # Find document by title
            data = self.document_manager.load_data()
            document = next((d for d in data['documents'] if d['title'] == title), None)
            
            if not document:
                QMessageBox.warning(self, "Not Found", f"Document '{title}' not found.")
                return
            
            # Get file info
            file_info = document.get('file_info', {})
            stored_path = file_info.get('stored_path')
            original_filename = file_info.get('original_filename', 'document.pdf')
            
            if not stored_path or not os.path.exists(stored_path):
                QMessageBox.warning(self, "Error", "Document file not found on disk.")
                return
            
            # Ask user where to save
            save_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Document", 
                original_filename,
                "All Files (*.*)"
            )
            
            if save_path:
                import shutil
                shutil.copy2(stored_path, save_path)
                
                # Record access on blockchain
                try:
                    if self.current_user:
                        add_user_action(
                            action_type="document_accessed",
                            data={
                                'document_id': document['id'],
                                'title': document['title'],
                                'action': 'download'
                            },
                            user_email=self.current_user.get('email')
                        )
                except Exception as e:
                    print(f"Warning: Failed to record document access on blockchain: {e}")
                
                QMessageBox.information(self, "Success", f"Document downloaded to:\n{save_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download document: {e}")
    
    def view_foia_request(self, request_id):
        """View FOIA request details"""
        
        if not self.foia_processor:
            QMessageBox.warning(self, "Error", "FOIA processor not initialized.")
            return
        
        try:
            foia_request = self.foia_processor.get_foia_request(request_id)
            
            if not foia_request:
                QMessageBox.warning(self, "Not Found", f"FOIA request {request_id} not found.")
                return
            
            # Build detailed view
            details_text = f"Request ID: {request_id}\n"
            details_text += f"Status: {foia_request.get('status', 'N/A')}\n"
            details_text += f"Complexity: {foia_request.get('complexity', 'N/A')}\n\n"
            
            # Requester info
            requester_info = foia_request.get('requester_info', {})
            details_text += "=== Requester Information ===\n"
            details_text += f"Name: {requester_info.get('name', 'N/A')}\n"
            details_text += f"Email: {requester_info.get('email', 'N/A')}\n"
            details_text += f"Phone: {requester_info.get('phone', 'N/A')}\n\n"
            
            # Request details
            details_text += "=== Request Details ===\n"
            details_text += f"Subject: {foia_request.get('subject', 'N/A')}\n"
            details_text += f"Description: {foia_request.get('description', 'N/A')}\n"
            details_text += f"Submitted: {foia_request.get('submitted_at', 'N/A')[:10]}\n"
            
            due_date = foia_request.get('due_date', 'N/A')
            if hasattr(due_date, 'isoformat'):
                due_date = due_date.isoformat()
            details_text += f"Due Date: {str(due_date)[:10] if due_date != 'N/A' else 'N/A'}\n\n"
            
            # Processing info
            if foia_request.get('processing_info'):
                processing = foia_request['processing_info']
                details_text += "=== Processing Information ===\n"
                details_text += f"Assigned To: {processing.get('assigned_to', 'N/A')}\n"
                details_text += f"Estimated Hours: {processing.get('estimated_hours', 'N/A')}\n"
                details_text += f"Cost Estimate: ${processing.get('cost_estimate', 0):.2f}\n"
            
            # Display in scrollable dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"FOIA Request Details - {request_id}")
            dialog.resize(600, 500)
            
            layout = QVBoxLayout()
            text_browser = QTextBrowser()
            text_browser.setPlainText(details_text)
            layout.addWidget(text_browser)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view FOIA request: {e}")
    
    def process_foia_request(self, request_id):
        """Process a FOIA request"""
        
        if not self.foia_processor:
            QMessageBox.warning(self, "Error", "FOIA processor not initialized.")
            return
        
        if not self.current_user:
            QMessageBox.warning(self, "Authentication Required", 
                               "Please log in to process FOIA requests.")
            return
        
        try:
            # Get FOIA request
            foia_request = self.foia_processor.get_foia_request(request_id)
            
            if not foia_request:
                QMessageBox.warning(self, "Not Found", f"FOIA request {request_id} not found.")
                return
            
            # Call backend processor
            success, message = self.foia_processor.process_foia_request(
                request_id, 
                self.current_user.get('email')
            )
            
            if success:
                QMessageBox.information(self, "FOIA Processing", 
                                       f"FOIA request {request_id} processed successfully.\n\n{message}")
                # Refresh FOIA table
                self.refresh_foia_table()
            else:
                QMessageBox.warning(self, "Processing Failed", 
                                   f"Failed to process FOIA request:\n{message}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process FOIA request: {e}")
    
    def track_legislation(self, bill_number):
        """Track legislation progress"""
        
        if not self.document_manager:
            QMessageBox.warning(self, "Error", "Document manager not initialized.")
            return
        
        try:
            history = self.document_manager.get_legislative_history(bill_number)
            
            if history:
                tracking = history['tracking']
                actions_text = "\n".join([f"• {a['date'][:10]}: {a['action']}" for a in tracking.get('actions', [])])
                
                QMessageBox.information(self, "Legislative Tracking", 
                                       f"Bill: {bill_number}\n"
                                       f"Title: {tracking['title']}\n"
                                       f"Sponsor: {tracking['sponsor']}\n"
                                       f"Status: {tracking['status']}\n"
                                       f"Current Stage: {tracking['stage']}\n\n"
                                       f"Recent Actions:\n{actions_text}")
            else:
                QMessageBox.warning(self, "Not Found", 
                                   f"Bill {bill_number} not found in tracking system.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to track legislation: {e}")
    
    def view_legislative_history(self, bill_number):
        """View legislative history"""
        
        if not self.document_manager:
            QMessageBox.warning(self, "Error", "Document manager not initialized.")
            return
        
        try:
            history = self.document_manager.get_legislative_history(bill_number)
            
            if history:
                tracking = history['tracking']
                
                # Build comprehensive history display
                history_text = f"Bill Number: {bill_number}\n"
                history_text += f"Title: {tracking['title']}\n"
                history_text += f"Sponsor: {tracking['sponsor']}\n"
                history_text += f"Status: {tracking['status']}\n"
                history_text += f"Current Stage: {tracking['stage']}\n\n"
                
                # Actions
                if tracking.get('actions'):
                    history_text += "=== Actions ===\n"
                    for action in tracking['actions']:
                        history_text += f"{action['date'][:10]}: {action['action']}\n"
                    history_text += "\n"
                
                # Votes
                if tracking.get('votes'):
                    history_text += "=== Votes ===\n"
                    for vote in tracking['votes']:
                        history_text += f"{vote['date'][:10]} - {vote['stage']}: {vote.get('result', 'N/A')}\n"
                        history_text += f"  For: {vote.get('votes_for', 0)}, Against: {vote.get('votes_against', 0)}, Abstentions: {vote.get('abstentions', 0)}\n"
                    history_text += "\n"
                
                # Amendments
                if tracking.get('amendments'):
                    history_text += "=== Amendments ===\n"
                    for amendment in tracking['amendments']:
                        history_text += f"{amendment['date'][:10]}: {amendment.get('description', 'N/A')} ({amendment.get('status', 'N/A')})\n"
                
                # Display in a dialog with scrollable text
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Legislative History - {bill_number}")
                dialog.resize(600, 500)
                
                layout = QVBoxLayout()
                text_browser = QTextBrowser()
                text_browser.setPlainText(history_text)
                layout.addWidget(text_browser)
                
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                
                dialog.setLayout(layout)
                dialog.exec_()
            else:
                QMessageBox.warning(self, "Not Found", 
                                   f"Bill {bill_number} not found in tracking system.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view legislative history: {e}")
    
    def search_archives(self):
        """Search document archives"""
        
        QMessageBox.information(self, "Archive Search", 
                               "Archive search interface would be displayed here.")
    
    def generate_archive_report(self):
        """Generate archive report"""
        
        QMessageBox.information(self, "Archive Report", 
                               "Archive report generation would start here.")
    
    def manage_retention_policies(self):
        """Manage document retention policies"""
        
        QMessageBox.information(self, "Retention Policies", 
                               "Retention policy management interface would be displayed here.")
    
    def backup_archives(self):
        """Backup document archives"""
        
        QMessageBox.information(self, "Archive Backup", 
                               "Archive backup process would start here.")
    
    def archive_maintenance(self):
        """Perform archive maintenance"""
        
        QMessageBox.information(self, "Archive Maintenance", 
                               "Archive maintenance tasks would be performed here.")
    
    def refresh_documents_table(self):
        """Refresh the documents table from database"""
        
        if not self.document_manager:
            return
        
        try:
            # Get all public documents
            documents = self.document_manager.get_public_documents()
            
            # Clear and repopulate table
            self.documents_table.setRowCount(len(documents))
            
            for i, doc in enumerate(documents):
                self.documents_table.setItem(i, 0, QTableWidgetItem(doc.get('title', 'N/A')))
                self.documents_table.setItem(i, 1, QTableWidgetItem(doc.get('type', 'N/A')))
                self.documents_table.setItem(i, 2, QTableWidgetItem(doc.get('uploaded_by', 'N/A')))
                self.documents_table.setItem(i, 3, QTableWidgetItem(doc.get('department', 'N/A')))
                self.documents_table.setItem(i, 4, QTableWidgetItem(doc.get('created_at', 'N/A')[:10]))
                self.documents_table.setItem(i, 5, QTableWidgetItem(doc.get('classification', 'N/A')))
                
                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(2, 2, 2, 2)
                
                view_btn = QPushButton("👁️ View")
                view_btn.clicked.connect(lambda checked, title=doc['title']: self.view_document(title))
                actions_layout.addWidget(view_btn)
                
                download_btn = QPushButton("💾 Download")
                download_btn.clicked.connect(lambda checked, title=doc['title']: self.download_document(title))
                actions_layout.addWidget(download_btn)
                
                actions_widget.setLayout(actions_layout)
                self.documents_table.setCellWidget(i, 6, actions_widget)
            
            self.documents_table.resizeColumnsToContents()
                
        except Exception as e:
            print(f"Error refreshing documents: {e}")
    
    def refresh_foia_table(self):
        """Refresh the FOIA requests table from database"""
        
        if not self.foia_processor:
            return
        
        try:
            data = self.foia_processor.load_data()
            foia_requests = data.get('foia_requests', [])
            
            # Clear and repopulate table
            self.foia_table.setRowCount(len(foia_requests))
            
            for i, request in enumerate(foia_requests):
                self.foia_table.setItem(i, 0, QTableWidgetItem(request.get('request_id', 'N/A')))
                self.foia_table.setItem(i, 1, QTableWidgetItem(request.get('subject', 'N/A')))
                
                requester_name = request.get('requester_info', {}).get('name', 'N/A')
                self.foia_table.setItem(i, 2, QTableWidgetItem(requester_name))
                
                submitted_date = request.get('submitted_at', 'N/A')
                if submitted_date != 'N/A':
                    submitted_date = submitted_date[:10]
                self.foia_table.setItem(i, 3, QTableWidgetItem(submitted_date))
                
                self.foia_table.setItem(i, 4, QTableWidgetItem(request.get('status', 'N/A')))
                
                due_date = request.get('due_date', 'N/A')
                if due_date != 'N/A' and hasattr(due_date, 'isoformat'):
                    due_date = due_date.isoformat()[:10]
                self.foia_table.setItem(i, 5, QTableWidgetItem(str(due_date)[:10] if due_date != 'N/A' else 'N/A'))
                
                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(2, 2, 2, 2)
                
                view_btn = QPushButton("👁️ View")
                req_id = request.get('request_id')
                view_btn.clicked.connect(lambda checked, r=req_id: self.view_foia_request(r))
                actions_layout.addWidget(view_btn)
                
                process_btn = QPushButton("⚙️ Process")
                process_btn.clicked.connect(lambda checked, r=req_id: self.process_foia_request(r))
                actions_layout.addWidget(process_btn)
                
                actions_widget.setLayout(actions_layout)
                self.foia_table.setCellWidget(i, 6, actions_widget)
            
            self.foia_table.resizeColumnsToContents()
                
        except Exception as e:
            print(f"Error refreshing FOIA requests: {e}")
    
    def refresh_legislative_table(self):
        """Refresh the legislative documents table from database"""
        
        if not self.document_manager:
            return
        
        try:
            legislative_docs = self.document_manager.get_legislative_documents()
            
            # Clear and repopulate table
            self.legislative_table.setRowCount(len(legislative_docs))
            
            for i, doc in enumerate(legislative_docs):
                tracking = doc.get('tracking', {})
                
                self.legislative_table.setItem(i, 0, QTableWidgetItem(tracking.get('bill_number', 'N/A')))
                self.legislative_table.setItem(i, 1, QTableWidgetItem(doc.get('title', 'Untitled')))
                self.legislative_table.setItem(i, 2, QTableWidgetItem(tracking.get('sponsor', 'N/A')))
                self.legislative_table.setItem(i, 3, QTableWidgetItem(tracking.get('status', 'N/A')))
                
                # Last action
                actions = tracking.get('actions', [])
                if actions:
                    last_action = actions[-1]
                    action_text = f"{last_action['date'][:10]} - {last_action['action']}"
                else:
                    action_text = 'No actions'
                self.legislative_table.setItem(i, 4, QTableWidgetItem(action_text))
                
                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(2, 2, 2, 2)
                
                bill_num = tracking.get('bill_number')
                
                track_btn = QPushButton("📊 Track")
                track_btn.clicked.connect(lambda checked, b=bill_num: self.track_legislation(b))
                actions_layout.addWidget(track_btn)
                
                history_btn = QPushButton("📜 History")
                history_btn.clicked.connect(lambda checked, b=bill_num: self.view_legislative_history(b))
                actions_layout.addWidget(history_btn)
                
                actions_widget.setLayout(actions_layout)
                self.legislative_table.setCellWidget(i, 5, actions_widget)
            
            self.legislative_table.resizeColumnsToContents()
                
        except Exception as e:
            print(f"Error refreshing legislative documents: {e}")


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    documents_tab = DocumentsArchiveTab()
    documents_tab.show()
    
    sys.exit(app.exec_())