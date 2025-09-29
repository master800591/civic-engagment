"""
CITIZEN VERIFICATION USER INTERFACE  
PyQt5 interface for citizen verification by government officials
Users request citizenship verification, officials verify citizens
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QTableWidget, QTableWidgetItem, QLabel, QPushButton,
                           QComboBox, QLineEdit, QTextEdit, QGroupBox,
                           QFormLayout, QDialog, QDialogButtonBox, QMessageBox,
                           QHeaderView, QCheckBox, QDateEdit, QSpacerItem,
                           QSizePolicy, QScrollArea, QFrame, QProgressBar,
                           QFileDialog, QSplitter, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple

# Import the citizen verification system
try:
    from .citizen_verification import (CitizenVerificationManager, CitizenshipLevel, 
                                     CitizenshipStatus, VerificationMethod)
    VERIFICATION_SYSTEM_AVAILABLE = True
except ImportError:
    print("Warning: Citizen verification system not available")
    VERIFICATION_SYSTEM_AVAILABLE = False

# Import session management
try:
    from ..users.session import SessionManager
    SESSION_AVAILABLE = True
except ImportError:
    print("Warning: Session management not available")
    SESSION_AVAILABLE = False


class RequestCitizenshipDialog(QDialog):
    """Dialog for requesting citizenship verification"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Request Citizenship Verification")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the request dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🏛️ Request Citizenship Verification")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Information
        info_text = QLabel(
            "Request verification of your citizenship by real-world government officials.\n"
            "Provide required documents and information for verification."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #666; padding: 8px; background-color: #f0f0f0; border-radius: 4px;")
        layout.addWidget(info_text)
        
        # Request form
        form_group = QGroupBox("Citizenship Information")
        form_layout = QFormLayout()
        
        # Citizenship level
        self.citizenship_level = QComboBox()
        if VERIFICATION_SYSTEM_AVAILABLE:
            for level in CitizenshipLevel:
                self.citizenship_level.addItem(level.value.title(), level)
        form_layout.addRow("Citizenship Level:", self.citizenship_level)
        
        # Country
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("Enter country name")
        form_layout.addRow("Country:", self.country_input)
        
        # Jurisdiction (state/city)
        self.jurisdiction_input = QLineEdit()
        self.jurisdiction_input.setPlaceholderText("Enter state, province, or city name")
        form_layout.addRow("State/Province/City:", self.jurisdiction_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Documents section
        docs_group = QGroupBox("Verification Documents")
        docs_layout = QVBoxLayout()
        
        docs_info = QLabel("Select documents you can provide for verification:")
        docs_layout.addWidget(docs_info)
        
        # Document checkboxes
        self.document_checks = {}
        if VERIFICATION_SYSTEM_AVAILABLE:
            for method in VerificationMethod:
                checkbox = QCheckBox(method.value.replace('_', ' ').title())
                self.document_checks[method.value] = checkbox
                docs_layout.addWidget(checkbox)
        
        docs_group.setLayout(docs_layout)
        layout.addWidget(docs_group)
        
        # Additional information
        additional_group = QGroupBox("Additional Information")
        additional_layout = QFormLayout()
        
        self.birth_city = QLineEdit()
        self.birth_city.setPlaceholderText("City where you were born")
        additional_layout.addRow("Birth City:", self.birth_city)
        
        self.residence_years = QLineEdit()
        self.residence_years.setPlaceholderText("Number of years residing")
        additional_layout.addRow("Years of Residence:", self.residence_years)
        
        self.additional_notes = QTextEdit()
        self.additional_notes.setPlaceholderText("Any additional information that may help verification...")
        self.additional_notes.setMaximumHeight(80)
        additional_layout.addRow("Notes:", self.additional_notes)
        
        additional_group.setLayout(additional_layout)
        layout.addWidget(additional_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.button_box = button_box
    
    def setup_connections(self):
        """Setup signal connections"""
        self.button_box.accepted.connect(self.accept_request)
        self.button_box.rejected.connect(self.reject)
    
    def accept_request(self):
        """Process the citizenship verification request"""
        # Validate inputs
        if not self.country_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Country is required")
            return
        
        if not self.jurisdiction_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "State/Province/City is required")
            return
        
        # Check if at least one document is selected
        selected_documents = []
        for doc_type, checkbox in self.document_checks.items():
            if checkbox.isChecked():
                selected_documents.append({
                    "type": doc_type,
                    "available": True,
                    "notes": ""
                })
        
        if not selected_documents:
            QMessageBox.warning(self, "Validation Error", "Please select at least one verification document")
            return
        
        # Compile request data
        self.request_data = {
            "citizenship_level": self.citizenship_level.currentData(),
            "country": self.country_input.text().strip(),
            "jurisdiction": self.jurisdiction_input.text().strip(),
            "documents": selected_documents,
            "additional_info": {
                "birth_city": self.birth_city.text().strip(),
                "residence_years": self.residence_years.text().strip(),
                "notes": self.additional_notes.toPlainText().strip()
            }
        }
        
        self.accept()


class VerifyCitizenDialog(QDialog):
    """Dialog for government officials to verify citizenship"""
    
    def __init__(self, request_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.request_data = request_data
        self.setWindowTitle(f"Verify Citizenship - {request_data.get('user_email', 'User')}")
        self.setModal(True)
        self.setFixedSize(700, 600)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the verification dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"🏛️ Verify Citizenship: {self.request_data.get('user_email', 'User')}")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Request details
        details_group = QGroupBox("Citizenship Request Details")
        details_layout = QFormLayout()
        
        details_layout.addRow("User:", QLabel(self.request_data.get('user_email', 'N/A')))
        details_layout.addRow("Citizenship Level:", QLabel(self.request_data.get('citizenship_level', 'N/A').title()))
        details_layout.addRow("Country:", QLabel(self.request_data.get('country', 'N/A')))
        details_layout.addRow("Jurisdiction:", QLabel(self.request_data.get('jurisdiction', 'N/A')))
        details_layout.addRow("Requested:", QLabel(self.request_data.get('requested_at', 'N/A')))
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Documents provided
        docs_group = QGroupBox("Documents Provided")
        docs_layout = QVBoxLayout()
        
        documents = self.request_data.get('verification_documents', [])
        if documents:
            for doc in documents:
                doc_text = f"• {doc.get('type', 'Unknown').replace('_', ' ').title()}"
                if doc.get('document_id'):
                    doc_text += f" (ID: {doc['document_id']})"
                docs_layout.addWidget(QLabel(doc_text))
        else:
            docs_layout.addWidget(QLabel("No documents listed"))
        
        docs_group.setLayout(docs_layout)
        layout.addWidget(docs_group)
        
        # Additional info
        if self.request_data.get('additional_info'):
            info = self.request_data['additional_info']
            additional_group = QGroupBox("Additional Information")
            additional_layout = QFormLayout()
            
            if info.get('birth_city'):
                additional_layout.addRow("Birth City:", QLabel(info['birth_city']))
            if info.get('residence_years'):
                additional_layout.addRow("Years of Residence:", QLabel(info['residence_years']))
            if info.get('notes'):
                notes_label = QLabel(info['notes'])
                notes_label.setWordWrap(True)
                additional_layout.addRow("Notes:", notes_label)
            
            additional_group.setLayout(additional_layout)
            layout.addWidget(additional_group)
        
        # Verification form
        verification_group = QGroupBox("Verification Decision")
        verification_layout = QFormLayout()
        
        # Verifier information
        self.verifier_email = QLineEdit()
        self.verifier_email.setPlaceholderText("Your government email address")
        verification_layout.addRow("Verifier Email:", self.verifier_email)
        
        self.verifier_title = QLineEdit()
        self.verifier_title.setPlaceholderText("Your official title")
        verification_layout.addRow("Official Title:", self.verifier_title)
        
        self.verifier_jurisdiction = QLineEdit()
        self.verifier_jurisdiction.setPlaceholderText("Your jurisdiction")
        verification_layout.addRow("Your Jurisdiction:", self.verifier_jurisdiction)
        
        # Verification decision
        self.verification_decision = QComboBox()
        if VERIFICATION_SYSTEM_AVAILABLE:
            self.verification_decision.addItem("✅ Verify as Citizen", CitizenshipStatus.VERIFIED)
            self.verification_decision.addItem("❌ Reject Application", CitizenshipStatus.REJECTED)
        verification_layout.addRow("Decision:", self.verification_decision)
        
        # Verification methods used
        methods_label = QLabel("Verification Methods Used:")
        verification_layout.addRow(methods_label)
        
        self.verification_methods = {}
        if VERIFICATION_SYSTEM_AVAILABLE:
            for method in VerificationMethod:
                checkbox = QCheckBox(method.value.replace('_', ' ').title())
                self.verification_methods[method] = checkbox
                verification_layout.addRow("", checkbox)
        
        # Verifier notes
        self.verifier_notes = QTextEdit()
        self.verifier_notes.setPlaceholderText("Enter detailed verification notes, evidence reviewed, confirmation method...")
        self.verifier_notes.setMaximumHeight(100)
        verification_layout.addRow("Verification Notes:", self.verifier_notes)
        
        verification_group.setLayout(verification_layout)
        layout.addWidget(verification_group)
        
        # Authority notice
        authority_info = QLabel(
            "⚖️ VERIFICATION AUTHORITY:\n"
            "As a government official, you have the authority to verify citizenship\n"
            "in your jurisdiction. This verification will be permanently recorded\n"
            "on the blockchain for transparency and accountability."
        )
        authority_info.setStyleSheet("background-color: #fff3cd; padding: 8px; border-radius: 4px; border-left: 4px solid #ffc107;")
        authority_info.setWordWrap(True)
        layout.addWidget(authority_info)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.button_box = button_box
    
    def setup_connections(self):
        """Setup signal connections"""
        self.button_box.accepted.connect(self.accept_verification)
        self.button_box.rejected.connect(self.reject)
    
    def accept_verification(self):
        """Process the verification decision"""
        # Validate verifier information
        verifier_email = self.verifier_email.text().strip()
        if not verifier_email or '@' not in verifier_email:
            QMessageBox.warning(self, "Validation Error", "Valid verifier email is required")
            return
        
        verifier_title = self.verifier_title.text().strip()
        if not verifier_title:
            QMessageBox.warning(self, "Validation Error", "Official title is required")
            return
        
        verifier_jurisdiction = self.verifier_jurisdiction.text().strip()
        if not verifier_jurisdiction:
            QMessageBox.warning(self, "Validation Error", "Verifier jurisdiction is required")
            return
        
        notes = self.verifier_notes.toPlainText().strip()
        if not notes:
            QMessageBox.warning(self, "Validation Error", "Verification notes are required")
            return
        
        # Get selected verification methods
        selected_methods = []
        for method, checkbox in self.verification_methods.items():
            if checkbox.isChecked():
                selected_methods.append(method)
        
        if not selected_methods:
            QMessageBox.warning(self, "Validation Error", "Please select at least one verification method")
            return
        
        # Compile verification data
        self.verification_data = {
            "verifier_email": verifier_email,
            "verifier_title": verifier_title,
            "verifier_jurisdiction": verifier_jurisdiction,
            "decision": self.verification_decision.currentData(),
            "verification_methods": selected_methods,
            "verifier_notes": notes,
            "evidence_reviewed": ["Documents verified", "Identity confirmed", "Jurisdiction validated"]
        }
        
        self.accept()


class CitizenVerificationTab(QWidget):
    """Main tab for citizen verification system"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.manager = CitizenVerificationManager() if VERIFICATION_SYSTEM_AVAILABLE else None
        self.current_user = None
        
        self.setup_ui()
        self.setup_connections()
        self.load_data()
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def setup_ui(self):
        """Setup the main user interface"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🏛️ Citizen Verification System")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Action buttons
        self.request_verification_btn = QPushButton("📝 Request Verification")
        self.request_verification_btn.setStyleSheet("QPushButton { background-color: #007bff; color: white; padding: 8px 16px; border: none; border-radius: 4px; }")
        header_layout.addWidget(self.request_verification_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; padding: 8px 16px; border: none; border-radius: 4px; }")
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # My citizenship tab
        self.citizenship_tab = self.create_citizenship_tab()
        self.tab_widget.addTab(self.citizenship_tab, "🏆 My Citizenship")
        
        # Verification requests tab (for government officials)
        self.requests_tab = self.create_requests_tab()
        self.tab_widget.addTab(self.requests_tab, "📋 Verification Queue")
        
        # Statistics tab
        self.stats_tab = self.create_statistics_tab()
        self.tab_widget.addTab(self.stats_tab, "📊 Statistics")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Citizen verification system ready")
        self.status_label.setStyleSheet("color: #666; padding: 8px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def create_citizenship_tab(self) -> QWidget:
        """Create the user citizenship status tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # User citizenship status
        status_group = QGroupBox("Your Citizenship Status")
        status_layout = QVBoxLayout()
        
        self.citizenship_status_label = QLabel("Loading citizenship status...")
        self.citizenship_status_label.setWordWrap(True)
        status_layout.addWidget(self.citizenship_status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Verified citizenships display
        verified_group = QGroupBox("Verified Citizenships")
        verified_layout = QVBoxLayout()
        
        self.verified_citizenships_list = QListWidget()
        verified_layout.addWidget(self.verified_citizenships_list)
        
        verified_group.setLayout(verified_layout)
        layout.addWidget(verified_group)
        
        # Pending requests display
        pending_group = QGroupBox("Pending Verification Requests")
        pending_layout = QVBoxLayout()
        
        self.pending_requests_list = QListWidget()
        pending_layout.addWidget(self.pending_requests_list)
        
        pending_group.setLayout(pending_layout)
        layout.addWidget(pending_group)
        
        # Benefits of verification
        benefits_group = QGroupBox("Benefits of Citizenship Verification")
        benefits_layout = QVBoxLayout()
        
        benefits_text = QLabel("""
✅ Verified citizenship provides enhanced platform privileges:
• Higher trust score in community interactions
• Eligibility for jurisdiction-specific governance participation  
• Access to local civic engagement features
• Verification badge displayed on your profile
• Enhanced credibility in debates and discussions
• Access to citizen-only features and content
        """)
        benefits_text.setWordWrap(True)
        benefits_text.setStyleSheet("padding: 12px; background-color: #d4edda; border-radius: 4px;")
        benefits_layout.addWidget(benefits_text)
        
        benefits_group.setLayout(benefits_layout)
        layout.addWidget(benefits_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_requests_tab(self) -> QWidget:
        """Create the verification requests management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses", "")
        if VERIFICATION_SYSTEM_AVAILABLE:
            for status in CitizenshipStatus:
                self.status_filter.addItem(status.value.replace('_', ' ').title(), status.value)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addWidget(QLabel("Level:"))
        self.level_filter = QComboBox()
        self.level_filter.addItem("All Levels", "")
        if VERIFICATION_SYSTEM_AVAILABLE:
            for level in CitizenshipLevel:
                self.level_filter.addItem(level.value.title(), level.value)
        filter_layout.addWidget(self.level_filter)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Requests table
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(8)
        self.requests_table.setHorizontalHeaderLabels([
            "User", "Level", "Country", "Jurisdiction", "Status", "Requested", "Verifier", "Actions"
        ])
        self.requests_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.requests_table)
        
        # Government official note
        gov_note = QLabel(
            "🏛️ GOVERNMENT OFFICIALS: You can review and verify citizenship requests in your jurisdiction.\n"
            "Click on a request to assign yourself as verifier and complete the verification process."
        )
        gov_note.setWordWrap(True)
        gov_note.setStyleSheet("background-color: #e2e3e5; padding: 12px; border-radius: 4px; border-left: 4px solid #6c757d;")
        layout.addWidget(gov_note)
        
        widget.setLayout(layout)
        return widget
    
    def create_statistics_tab(self) -> QWidget:
        """Create the statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        
        self.total_requests_card = self.create_stat_card("Total Requests", "0", "#007bff")
        self.verified_citizens_card = self.create_stat_card("Verified Citizens", "0", "#28a745")
        self.pending_requests_card = self.create_stat_card("Pending Requests", "0", "#ffc107")
        self.success_rate_card = self.create_stat_card("Success Rate", "0%", "#17a2b8")
        
        stats_layout.addWidget(self.total_requests_card)
        stats_layout.addWidget(self.verified_citizens_card)
        stats_layout.addWidget(self.pending_requests_card)
        stats_layout.addWidget(self.success_rate_card)
        
        layout.addLayout(stats_layout)
        
        # Detailed statistics
        details_group = QGroupBox("Detailed Statistics")
        details_layout = QVBoxLayout()
        
        self.detailed_stats_label = QLabel("Loading detailed statistics...")
        self.detailed_stats_label.setWordWrap(True)
        details_layout.addWidget(self.detailed_stats_label)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # System information
        system_group = QGroupBox("System Information")
        system_layout = QVBoxLayout()
        
        system_info = QLabel("""
🏛️ CITIZEN VERIFICATION SYSTEM

Purpose: Enable real-world government officials to verify platform users as citizens
Process: Users submit verification requests → Government officials review and verify
Hierarchy: Country → State/Province → City/Town verification levels
Blockchain: All verifications permanently recorded for transparency
Separation: Citizenship verification separate from contract governance roles

Government officials maintain authority over citizenship verification in their jurisdiction.
Verified citizenship provides enhanced platform privileges and trust indicators.
        """)
        system_info.setWordWrap(True)
        system_info.setStyleSheet("padding: 12px; background-color: #f8f9fa; border-radius: 4px;")
        system_layout.addWidget(system_info)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a statistics card"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{ 
                background-color: white; 
                border: 2px solid {color}; 
                border-radius: 8px; 
                padding: 12px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 9))
        title_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        frame.setLayout(layout)
        frame.value_label = value_label
        
        return frame
    
    def setup_connections(self):
        """Setup signal connections"""
        self.request_verification_btn.clicked.connect(self.request_citizenship_verification)
        self.refresh_btn.clicked.connect(self.load_data)
        
        # Filter connections
        self.status_filter.currentTextChanged.connect(self.filter_requests)
        self.level_filter.currentTextChanged.connect(self.filter_requests)
        
        # Table connections
        self.requests_table.cellDoubleClicked.connect(self.on_request_double_click)
    
    def load_data(self):
        """Load and display citizen verification data"""
        if not VERIFICATION_SYSTEM_AVAILABLE or not self.manager:
            self.status_label.setText("Citizen verification system not available")
            return
        
        try:
            # Get current user
            if SESSION_AVAILABLE:
                self.current_user = SessionManager.get_current_user()
            
            # Load user citizenship status
            self.update_citizenship_status()
            
            # Load verification requests
            self.update_requests_table()
            
            # Load statistics
            self.update_statistics()
            
            self.status_label.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            self.status_label.setText(f"Error loading data: {str(e)}")
    
    def update_citizenship_status(self):
        """Update user's citizenship status display"""
        try:
            if not self.current_user:
                self.citizenship_status_label.setText("Please log in to view citizenship status")
                return
            
            user_email = self.current_user.get('email', '')
            status_data = self.manager.get_user_citizenship_status(user_email)
            
            # Update status overview
            verified_count = status_data.get('citizenship_count', 0)
            pending_count = len(status_data.get('pending_requests', []))
            
            status_text = f"""
👤 User: {user_email}
🏆 Verified Citizenships: {verified_count}
⏳ Pending Requests: {pending_count}

Citizenship Status:
"""
            
            if status_data.get('has_country_citizenship'):
                status_text += "✅ Country Citizenship Verified\n"
            else:
                status_text += "❌ Country Citizenship Not Verified\n"
            
            if status_data.get('has_state_citizenship'):
                status_text += "✅ State/Province Citizenship Verified\n"
            else:
                status_text += "❌ State/Province Citizenship Not Verified\n"
            
            if status_data.get('has_city_citizenship'):
                status_text += "✅ City/Town Citizenship Verified\n"
            else:
                status_text += "❌ City/Town Citizenship Not Verified\n"
            
            self.citizenship_status_label.setText(status_text.strip())
            
            # Update verified citizenships list
            self.verified_citizenships_list.clear()
            verified_citizenships = status_data.get('verified_citizenships', {})
            
            for level, citizenship in verified_citizenships.items():
                item_text = f"🏆 {level.title()}: {citizenship['jurisdiction']}, {citizenship['country']}"
                item_text += f"\n   Verified by: {citizenship['verifier_title']}"
                item_text += f"\n   Date: {citizenship['verified_at'][:10]}"
                
                item = QListWidgetItem(item_text)
                self.verified_citizenships_list.addItem(item)
            
            # Update pending requests list
            self.pending_requests_list.clear()
            pending_requests = status_data.get('pending_requests', [])
            
            for request in pending_requests:
                item_text = f"⏳ {request['citizenship_level'].title()}: {request['jurisdiction']}, {request['country']}"
                item_text += f"\n   Status: {request['status'].replace('_', ' ').title()}"
                item_text += f"\n   Requested: {request['requested_at'][:10]}"
                
                item = QListWidgetItem(item_text)
                self.pending_requests_list.addItem(item)
            
        except Exception as e:
            self.citizenship_status_label.setText(f"Error loading citizenship status: {e}")
    
    def update_requests_table(self):
        """Update verification requests table"""
        try:
            # Get all verification requests
            all_requests = self.manager.search_verification_requests()
            
            self.requests_table.setRowCount(len(all_requests))
            
            for row, request in enumerate(all_requests):
                self.requests_table.setItem(row, 0, QTableWidgetItem(request.get('user_email', '')))
                self.requests_table.setItem(row, 1, QTableWidgetItem(request.get('citizenship_level', '').title()))
                self.requests_table.setItem(row, 2, QTableWidgetItem(request.get('country', '')))
                self.requests_table.setItem(row, 3, QTableWidgetItem(request.get('jurisdiction', '')))
                
                # Status with icon
                status = request.get('status', 'unknown')
                status_icons = {
                    'pending': '⏳',
                    'under_review': '👀',
                    'verified': '✅',
                    'rejected': '❌'
                }
                status_text = f"{status_icons.get(status, '?')} {status.replace('_', ' ').title()}"
                self.requests_table.setItem(row, 4, QTableWidgetItem(status_text))
                
                # Request date
                requested_at = request.get('requested_at', '')[:10] if request.get('requested_at') else ''
                self.requests_table.setItem(row, 5, QTableWidgetItem(requested_at))
                
                # Verifier info
                assigned_verifier = request.get('assigned_verifier')
                if assigned_verifier:
                    verifier_text = assigned_verifier.get('verifier_title', 'Unknown')
                else:
                    verifier_text = "Unassigned"
                self.requests_table.setItem(row, 6, QTableWidgetItem(verifier_text))
                
                # Actions
                actions_text = "Review" if status == 'pending' else "View"
                self.requests_table.setItem(row, 7, QTableWidgetItem(actions_text))
            
            self.requests_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error updating requests table: {e}")
    
    def update_statistics(self):
        """Update statistics display"""
        try:
            stats = self.manager.get_verification_statistics()
            
            # Update stat cards
            self.total_requests_card.value_label.setText(str(stats.get('total_requests', 0)))
            self.verified_citizens_card.value_label.setText(str(stats.get('verified_citizens', 0)))
            self.pending_requests_card.value_label.setText(str(stats.get('pending_verifications', 0)))
            
            success_rate = stats.get('system_health', {}).get('verification_success_rate', 0)
            self.success_rate_card.value_label.setText(f"{success_rate:.1f}%")
            
            # Update detailed statistics
            details_text = f"""
📊 CITIZENSHIP VERIFICATION STATISTICS

Verification Requests:
• Total Requests: {stats.get('total_requests', 0)}
• Verified Citizens: {stats.get('verified_citizens', 0)}
• Pending Verifications: {stats.get('pending_verifications', 0)}
• Rejected Applications: {stats.get('rejected_verifications', 0)}

By Citizenship Level:
"""
            
            verifications_by_level = stats.get('verifications_by_level', {})
            for level, count in verifications_by_level.items():
                details_text += f"• {level.title()}: {count}\n"
            
            details_text += f"""
By Country:
"""
            
            verifications_by_country = stats.get('verifications_by_country', {})
            for country, count in sorted(verifications_by_country.items()):
                details_text += f"• {country}: {count}\n"
            
            details_text += f"""
Government Verifiers:
• Total Verifiers: {stats.get('government_verifiers', {}).get('total_verifiers', 0)}
• Active Verifiers: {stats.get('government_verifiers', {}).get('active_verifiers', 0)}
• Verifications Completed: {stats.get('government_verifiers', {}).get('verifications_completed', 0)}

System Health:
• Success Rate: {success_rate:.1f}%
• Database Size: {stats.get('system_health', {}).get('database_size', 0)}
• Pending Queue: {stats.get('system_health', {}).get('pending_queue_size', 0)}
            """
            
            self.detailed_stats_label.setText(details_text.strip())
            
        except Exception as e:
            self.detailed_stats_label.setText(f"Error loading statistics: {e}")
    
    def filter_requests(self):
        """Filter verification requests table"""
        try:
            status_filter = self.status_filter.currentData() or ""
            level_filter = self.level_filter.currentData() or ""
            
            for row in range(self.requests_table.rowCount()):
                show_row = True
                
                # Apply status filter
                if status_filter:
                    status_item = self.requests_table.item(row, 4)
                    if not status_item or status_filter not in status_item.text().lower():
                        show_row = False
                
                # Apply level filter
                if level_filter and show_row:
                    level_item = self.requests_table.item(row, 1)
                    if not level_item or level_filter != level_item.text().lower():
                        show_row = False
                
                self.requests_table.setRowHidden(row, not show_row)
                
        except Exception as e:
            print(f"Error filtering requests: {e}")
    
    def request_citizenship_verification(self):
        """Handle request for citizenship verification"""
        if not self.manager:
            QMessageBox.warning(self, "Error", "Verification system not available")
            return
        
        if not self.current_user:
            QMessageBox.warning(self, "Authentication Required", "Please log in to request citizenship verification")
            return
        
        # Show request dialog
        dialog = RequestCitizenshipDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            request_data = dialog.request_data
            user_email = self.current_user.get('email', '')
            
            success, message = self.manager.request_citizenship_verification(
                user_email=user_email,
                citizenship_level=request_data['citizenship_level'],
                jurisdiction=request_data['jurisdiction'],
                country=request_data['country'],
                verification_documents=request_data['documents'],
                additional_info=request_data['additional_info']
            )
            
            if success:
                QMessageBox.information(self, "Success", f"Verification requested: {message}")
                self.load_data()  # Refresh data
            else:
                QMessageBox.warning(self, "Error", f"Failed to request verification: {message}")
    
    def on_request_double_click(self, row: int, column: int):
        """Handle double-click on verification request"""
        try:
            if not self.manager:
                return
            
            # Get request data from table
            user_email_item = self.requests_table.item(row, 0)
            if not user_email_item:
                return
            
            user_email = user_email_item.text()
            
            # Find the full request data
            all_requests = self.manager.search_verification_requests()
            request_data = None
            
            for request in all_requests:
                if request.get('user_email') == user_email:
                    request_data = request
                    break
            
            if not request_data:
                return
            
            # Check if user can verify (basic check - in real implementation would verify government credentials)
            if not self.current_user:
                QMessageBox.warning(self, "Authentication Required", "Please log in to verify citizenship")
                return
            
            # Show verification dialog
            dialog = VerifyCitizenDialog(request_data, self)
            if dialog.exec_() == QDialog.Accepted:
                verification_data = dialog.verification_data
                
                # First assign verifier
                success1, message1 = self.manager.assign_government_verifier(
                    request_id=request_data['request_id'],
                    verifier_email=verification_data['verifier_email'],
                    verifier_title=verification_data['verifier_title'],
                    verifier_jurisdiction=verification_data['verifier_jurisdiction']
                )
                
                if success1:
                    # Then complete verification
                    success2, message2 = self.manager.complete_citizenship_verification(
                        request_id=request_data['request_id'],
                        verifier_email=verification_data['verifier_email'],
                        verification_decision=verification_data['decision'],
                        verification_methods=verification_data['verification_methods'],
                        verifier_notes=verification_data['verifier_notes'],
                        evidence_reviewed=verification_data['evidence_reviewed']
                    )
                    
                    if success2:
                        QMessageBox.information(self, "Success", f"Verification completed: {message2}")
                        self.load_data()  # Refresh data
                    else:
                        QMessageBox.warning(self, "Error", f"Verification failed: {message2}")
                else:
                    QMessageBox.warning(self, "Error", f"Verifier assignment failed: {message1}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Verification process failed: {str(e)}")


# Demo function
def demo_citizen_verification_ui():
    """Demonstrate the citizen verification UI"""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create and show the verification tab
    tab = CitizenVerificationTab()
    tab.show()
    
    # Run the application
    sys.exit(app.exec_())