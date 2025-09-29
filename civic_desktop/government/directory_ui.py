"""
GOVERNMENT DIRECTORY USER INTERFACE
PyQt5 interface for managing comprehensive government officials directory
Contact tracking, verification chain, and outreach management
"""

import sys
import csv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QTableWidget, QTableWidgetItem, QLabel, QPushButton,
                           QComboBox, QLineEdit, QTextEdit, QGroupBox,
                           QFormLayout, QDialog, QDialogButtonBox, QMessageBox,
                           QHeaderView, QCheckBox, QDateEdit, QSpacerItem,
                           QSizePolicy, QScrollArea, QFrame, QProgressBar,
                           QFileDialog, QSplitter)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple

# Import the government directory system
try:
    from .government_directory import (GovernmentDirectoryManager, GovernmentOfficialType, 
                                     VerificationStatus, VerificationAuthority)
    DIRECTORY_SYSTEM_AVAILABLE = True
except ImportError:
    print("Warning: Government directory system not available")
    DIRECTORY_SYSTEM_AVAILABLE = False


class ContactOfficialDialog(QDialog):
    """Dialog for recording contact with government officials"""
    
    def __init__(self, official_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.official_data = official_data
        self.setWindowTitle(f"Contact {official_data.get('name', 'Official')}")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the contact dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"Contact Record: {self.official_data.get('name', 'Unknown')}")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Official information
        info_group = QGroupBox("Official Information")
        info_layout = QFormLayout()
        
        info_layout.addRow("Name:", QLabel(self.official_data.get('name', 'N/A')))
        info_layout.addRow("Title:", QLabel(self.official_data.get('title', 'N/A')))
        info_layout.addRow("Email:", QLabel(self.official_data.get('email', 'N/A')))
        info_layout.addRow("Phone:", QLabel(self.official_data.get('phone', 'N/A')))
        info_layout.addRow("Current Status:", QLabel(self.official_data.get('verification_status', 'N/A')))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Contact form
        contact_group = QGroupBox("Contact Record")
        contact_layout = QFormLayout()
        
        # Contact method
        self.contact_method = QComboBox()
        self.contact_method.addItems(['email', 'phone', 'letter', 'social_media', 'in_person', 'other'])
        contact_layout.addRow("Contact Method:", self.contact_method)
        
        # Response received
        self.response_received = QCheckBox("Response Received")
        contact_layout.addRow("", self.response_received)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter contact notes, response details, next steps...")
        self.notes_input.setMaximumHeight(100)
        contact_layout.addRow("Notes:", self.notes_input)
        
        contact_group.setLayout(contact_layout)
        layout.addWidget(contact_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.button_box = button_box
    
    def setup_connections(self):
        """Setup signal connections"""
        self.button_box.accepted.connect(self.accept_contact)
        self.button_box.rejected.connect(self.reject)
    
    def accept_contact(self):
        """Process the contact record"""
        self.contact_data = {
            'contact_method': self.contact_method.currentText(),
            'response_received': self.response_received.isChecked(),
            'notes': self.notes_input.toPlainText().strip()
        }
        self.accept()


class VerifyOfficialDialog(QDialog):
    """Dialog for verifying government officials"""
    
    def __init__(self, official_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.official_data = official_data
        self.setWindowTitle(f"Verify {official_data.get('name', 'Official')}")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the verification dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"Verify Government Official: {self.official_data.get('name', 'Unknown')}")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Official details
        details_group = QGroupBox("Official Details")
        details_layout = QFormLayout()
        
        details_layout.addRow("Name:", QLabel(self.official_data.get('name', 'N/A')))
        details_layout.addRow("Title:", QLabel(self.official_data.get('title', 'N/A')))
        details_layout.addRow("Jurisdiction:", QLabel(self.official_data.get('jurisdiction', 'N/A')))
        details_layout.addRow("Level:", QLabel(self.official_data.get('jurisdiction_level', 'N/A').title()))
        details_layout.addRow("Email:", QLabel(self.official_data.get('email', 'N/A')))
        details_layout.addRow("Phone:", QLabel(self.official_data.get('phone', 'N/A')))
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Verification form
        verification_group = QGroupBox("Verification Information")
        verification_layout = QFormLayout()
        
        # Verifier email
        self.verifier_email = QLineEdit()
        self.verifier_email.setPlaceholderText("Enter your email address")
        verification_layout.addRow("Verifier Email:", self.verifier_email)
        
        # Verification authority
        self.verification_authority = QComboBox()
        if DIRECTORY_SYSTEM_AVAILABLE:
            for authority in VerificationAuthority:
                self.verification_authority.addItem(authority.value.replace('_', ' ').title(), authority)
        verification_layout.addRow("Verification Authority:", self.verification_authority)
        
        # Verification notes
        self.verification_notes = QTextEdit()
        self.verification_notes.setPlaceholderText("Enter verification details, sources, confirmation method...")
        self.verification_notes.setMaximumHeight(120)
        verification_layout.addRow("Verification Notes:", self.verification_notes)
        
        verification_group.setLayout(verification_layout)
        layout.addWidget(verification_group)
        
        # Hierarchy explanation
        hierarchy_info = QLabel(
            "Verification Hierarchy:\n"
            "• Founders verify Country Leaders\n"
            "• Country Leaders verify State Leaders\n"
            "• State Leaders verify City Leaders\n"
            "• Government officials are SEPARATE from contract roles"
        )
        hierarchy_info.setStyleSheet("background-color: #e3f2fd; padding: 8px; border-radius: 4px;")
        hierarchy_info.setWordWrap(True)
        layout.addWidget(hierarchy_info)
        
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
        """Process the verification"""
        verifier_email = self.verifier_email.text().strip()
        if not verifier_email or '@' not in verifier_email:
            QMessageBox.warning(self, "Validation Error", "Valid verifier email is required")
            return
        
        notes = self.verification_notes.toPlainText().strip()
        if not notes:
            QMessageBox.warning(self, "Validation Error", "Verification notes are required")
            return
        
        self.verification_data = {
            'verifier_email': verifier_email,
            'verification_authority': self.verification_authority.currentData(),
            'verification_notes': notes
        }
        self.accept()


class GovernmentDirectoryTab(QWidget):
    """Main tab for government officials directory management"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.manager = GovernmentDirectoryManager() if DIRECTORY_SYSTEM_AVAILABLE else None
        
        self.setup_ui()
        self.setup_connections()
        self.load_data()
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(60000)  # Refresh every minute
    
    def setup_ui(self):
        """Setup the main user interface"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🏛️ Government Officials Directory")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Action buttons
        self.export_csv_btn = QPushButton("📄 Export CSV")
        self.export_csv_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; }")
        header_layout.addWidget(self.export_csv_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 8px 16px; border: none; border-radius: 4px; }")
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Statistics tab
        self.stats_tab = self.create_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "📊 Statistics")
        
        # Directory tab
        self.directory_tab = self.create_directory_tab()
        self.tab_widget.addTab(self.directory_tab, "🌍 World Directory")
        
        # Contact tracking tab
        self.contacts_tab = self.create_contacts_tab()
        self.tab_widget.addTab(self.contacts_tab, "📞 Contact Tracking")
        
        # Verification chain tab
        self.verification_tab = self.create_verification_tab()
        self.tab_widget.addTab(self.verification_tab, "✅ Verification Chain")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Government directory system ready")
        self.status_label.setStyleSheet("color: #666; padding: 8px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def create_stats_tab(self) -> QWidget:
        """Create the statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Stats overview cards
        stats_layout = QHBoxLayout()
        
        self.total_officials_card = self.create_stat_card("Total Officials", "0", "#2196F3")
        self.country_leaders_card = self.create_stat_card("Country Leaders", "0", "#4CAF50")
        self.state_leaders_card = self.create_stat_card("State Leaders", "0", "#FF9800")
        self.city_leaders_card = self.create_stat_card("City Leaders", "0", "#9C27B0")
        
        stats_layout.addWidget(self.total_officials_card)
        stats_layout.addWidget(self.country_leaders_card)
        stats_layout.addWidget(self.state_leaders_card)
        stats_layout.addWidget(self.city_leaders_card)
        
        layout.addLayout(stats_layout)
        
        # Contact stats
        contact_stats_layout = QHBoxLayout()
        
        self.contacted_card = self.create_stat_card("Contacted", "0", "#8BC34A")
        self.responded_card = self.create_stat_card("Responded", "0", "#03A9F4")
        self.verified_card = self.create_stat_card("Verified", "0", "#FFC107")
        self.response_rate_card = self.create_stat_card("Response Rate", "0%", "#E91E63")
        
        contact_stats_layout.addWidget(self.contacted_card)
        contact_stats_layout.addWidget(self.responded_card)
        contact_stats_layout.addWidget(self.verified_card)
        contact_stats_layout.addWidget(self.response_rate_card)
        
        layout.addLayout(contact_stats_layout)
        
        # Detailed breakdown
        breakdown_group = QGroupBox("Detailed Breakdown")
        breakdown_layout = QVBoxLayout()
        
        self.stats_details = QLabel("Loading detailed statistics...")
        self.stats_details.setWordWrap(True)
        self.stats_details.setStyleSheet("padding: 16px; background-color: #f5f5f5; border-radius: 4px;")
        breakdown_layout.addWidget(self.stats_details)
        
        breakdown_group.setLayout(breakdown_layout)
        layout.addWidget(breakdown_group)
        
        layout.addStretch()
        
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
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        frame.setLayout(layout)
        frame.value_label = value_label
        
        return frame
    
    def create_directory_tab(self) -> QWidget:
        """Create the directory tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Search and filter controls
        filter_layout = QHBoxLayout()
        
        # Search
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, title, or jurisdiction...")
        filter_layout.addWidget(self.search_input)
        
        # Country filter
        filter_layout.addWidget(QLabel("Country:"))
        self.country_filter = QComboBox()
        self.country_filter.addItem("All Countries", "")
        filter_layout.addWidget(self.country_filter)
        
        # Level filter
        filter_layout.addWidget(QLabel("Level:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(["All Levels", "Country", "State", "City"])
        filter_layout.addWidget(self.level_filter)
        
        # Status filter
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses", "")
        if DIRECTORY_SYSTEM_AVAILABLE:
            for status in VerificationStatus:
                self.status_filter.addItem(status.value.replace('_', ' ').title(), status.value)
        
        filter_layout.addWidget(self.status_filter)
        
        layout.addLayout(filter_layout)
        
        # Officials table
        self.officials_table = QTableWidget()
        self.officials_table.setColumnCount(10)
        self.officials_table.setHorizontalHeaderLabels([
            "Name", "Title", "Level", "Jurisdiction", "Country", 
            "Email", "Phone", "Status", "Contacts", "Actions"
        ])
        self.officials_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.officials_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_contacts_tab(self) -> QWidget:
        """Create the contact tracking tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Contact summary
        summary_group = QGroupBox("Contact Summary")
        summary_layout = QHBoxLayout()
        
        self.contact_progress = QProgressBar()
        self.contact_progress.setFormat("Contact Progress: %p%")
        summary_layout.addWidget(self.contact_progress)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Contact history table
        history_label = QLabel("Recent Contact History")
        history_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(history_label)
        
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(6)
        self.contacts_table.setHorizontalHeaderLabels([
            "Official", "Method", "Date", "Response", "Notes", "Follow-up"
        ])
        self.contacts_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.contacts_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_verification_tab(self) -> QWidget:
        """Create the verification chain tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Hierarchy explanation
        hierarchy_info = QLabel("""
🏛️ HIERARCHICAL VERIFICATION SYSTEM

Government officials are verified through a strict hierarchy:
• Platform FOUNDERS verify COUNTRY leaders (Presidents, Prime Ministers, etc.)
• Verified COUNTRY leaders verify STATE/PROVINCIAL leaders (Governors, Premiers, etc.) 
• Verified STATE leaders verify CITY/MUNICIPAL leaders (Mayors, City Managers, etc.)

✨ IMPORTANT: Government officials are SEPARATE from contract governance system.
   They do NOT receive contract roles and cannot run for contract positions.
   This maintains separation between real government and platform governance.
        """)
        hierarchy_info.setStyleSheet("background-color: #e8f5e8; padding: 12px; border-radius: 6px; border-left: 4px solid #4CAF50;")
        hierarchy_info.setWordWrap(True)
        layout.addWidget(hierarchy_info)
        
        # Verification statistics
        verification_stats_group = QGroupBox("Verification Chain Status")
        verification_stats_layout = QVBoxLayout()
        
        self.verification_chain_label = QLabel("Loading verification chain statistics...")
        verification_stats_layout.addWidget(self.verification_chain_label)
        
        verification_stats_group.setLayout(verification_stats_layout)
        layout.addWidget(verification_stats_group)
        
        # Pending verifications
        pending_label = QLabel("Officials Awaiting Verification")
        pending_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(pending_label)
        
        self.verification_table = QTableWidget()
        self.verification_table.setColumnCount(6)
        self.verification_table.setHorizontalHeaderLabels([
            "Official", "Title", "Level", "Jurisdiction", "Status", "Actions"
        ])
        self.verification_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.verification_table)
        
        widget.setLayout(layout)
        return widget
    
    def setup_connections(self):
        """Setup signal connections"""
        self.export_csv_btn.clicked.connect(self.export_officials_csv)
        self.refresh_btn.clicked.connect(self.load_data)
        
        # Search and filter connections
        self.search_input.textChanged.connect(self.filter_officials)
        self.country_filter.currentTextChanged.connect(self.filter_officials)
        self.level_filter.currentTextChanged.connect(self.filter_officials)
        self.status_filter.currentTextChanged.connect(self.filter_officials)
        
        # Table connections
        self.officials_table.cellDoubleClicked.connect(self.on_official_double_click)
    
    def load_data(self):
        """Load and display government directory data"""
        if not DIRECTORY_SYSTEM_AVAILABLE or not self.manager:
            self.status_label.setText("Government directory system not available")
            return
        
        try:
            # Load statistics
            stats = self.manager.get_directory_statistics()
            self.update_statistics(stats)
            
            # Load officials directory
            all_officials = self.manager.search_officials()
            self.update_officials_table(all_officials)
            self.populate_filter_options(all_officials)
            
            # Load contact history
            self.update_contacts_table()
            
            # Load verification chain
            self.update_verification_chain()
            
            self.status_label.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            self.status_label.setText(f"Error loading data: {str(e)}")
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Update statistics display"""
        try:
            # Update main stat cards
            total = stats.get('total_officials', 0)
            self.total_officials_card.value_label.setText(str(total))
            
            officials_by_level = stats.get('officials_by_level', {})
            self.country_leaders_card.value_label.setText(str(officials_by_level.get('country', 0)))
            self.state_leaders_card.value_label.setText(str(officials_by_level.get('state', 0)))
            self.city_leaders_card.value_label.setText(str(officials_by_level.get('city', 0)))
            
            # Update contact stats
            contacted = total - stats.get('uncontacted_officials', 0)
            responded = stats.get('officials_responded', 0)
            verified = stats.get('verified_officials', 0)
            response_rate = stats.get('response_rate', 0)
            
            self.contacted_card.value_label.setText(str(contacted))
            self.responded_card.value_label.setText(str(responded))
            self.verified_card.value_label.setText(str(verified))
            self.response_rate_card.value_label.setText(f"{response_rate:.1f}%")
            
            # Update contact progress
            if total > 0:
                contact_progress = (contacted / total) * 100
                self.contact_progress.setValue(int(contact_progress))
            
            # Update detailed breakdown
            details_text = f"""
📊 COMPREHENSIVE DIRECTORY STATISTICS

Officials by Government Level:
• Country Leaders: {officials_by_level.get('country', 0)}
• State/Provincial Leaders: {officials_by_level.get('state', 0)}
• City/Municipal Leaders: {officials_by_level.get('city', 0)}

Officials by Status:
"""
            officials_by_status = stats.get('officials_by_status', {})
            for status, count in officials_by_status.items():
                details_text += f"• {status.replace('_', ' ').title()}: {count}\n"
            
            details_text += f"""
Geographic Distribution:
"""
            officials_by_country = stats.get('officials_by_country', {})
            for country, count in sorted(officials_by_country.items()):
                details_text += f"• {country}: {count}\n"
            
            details_text += f"""
Contact & Outreach Summary:
• Total Contact Attempts: {stats.get('total_contact_attempts', 0)}
• Response Rate: {response_rate:.1f}%
• Officials Verified: {verified}
• Remaining to Contact: {stats.get('uncontacted_officials', 0)}
"""
            
            self.stats_details.setText(details_text.strip())
            
        except Exception as e:
            self.stats_details.setText(f"Error displaying statistics: {str(e)}")
    
    def populate_filter_options(self, officials: List[Dict[str, Any]]):
        """Populate filter dropdown options based on data"""
        try:
            # Get unique countries
            countries = sorted(set(o.get('country', '') for o in officials if o.get('country')))
            
            self.country_filter.clear()
            self.country_filter.addItem("All Countries", "")
            for country in countries:
                self.country_filter.addItem(country, country)
                
        except Exception as e:
            print(f"Error populating filter options: {e}")
    
    def update_officials_table(self, officials: List[Dict[str, Any]]):
        """Update the officials directory table"""
        try:
            self.officials_table.setRowCount(len(officials))
            
            for row, official in enumerate(officials):
                self.officials_table.setItem(row, 0, QTableWidgetItem(official.get('name', '')))
                self.officials_table.setItem(row, 1, QTableWidgetItem(official.get('title', '')))
                self.officials_table.setItem(row, 2, QTableWidgetItem(official.get('jurisdiction_level', '').title()))
                self.officials_table.setItem(row, 3, QTableWidgetItem(official.get('jurisdiction', '')))
                self.officials_table.setItem(row, 4, QTableWidgetItem(official.get('country', '')))
                self.officials_table.setItem(row, 5, QTableWidgetItem(official.get('email', '')))
                self.officials_table.setItem(row, 6, QTableWidgetItem(official.get('phone', '')))
                
                # Status with icon
                status = official.get('verification_status', 'uncontacted')
                status_icons = {
                    'uncontacted': '⚪',
                    'contacted': '🔵', 
                    'interested': '🟢',
                    'pending': '🟡',
                    'verified': '✅',
                    'rejected': '❌'
                }
                status_text = f"{status_icons.get(status, '?')} {status.replace('_', ' ').title()}"
                self.officials_table.setItem(row, 7, QTableWidgetItem(status_text))
                
                # Contact attempts
                contact_attempts = official.get('contact_attempts', 0)
                self.officials_table.setItem(row, 8, QTableWidgetItem(str(contact_attempts)))
                
                # Actions (simplified - buttons would be added in real implementation)
                actions = "Contact | Verify"
                self.officials_table.setItem(row, 9, QTableWidgetItem(actions))
            
            self.officials_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error updating officials table: {e}")
    
    def update_contacts_table(self):
        """Update the contact history table"""
        # This would load contact history from the manager
        # Simplified for demonstration
        pass
    
    def update_verification_chain(self):
        """Update the verification chain display"""
        try:
            if not self.manager:
                return
            
            # Get verification statistics
            stats = self.manager.get_directory_statistics()
            verified_count = stats.get('verified_officials', 0)
            total_count = stats.get('total_officials', 0)
            
            chain_text = f"""
🏛️ VERIFICATION CHAIN STATUS

Total Officials in Directory: {total_count}
Verified Officials: {verified_count}
Pending Verification: {total_count - verified_count}

Verification Hierarchy Progress:
• Platform Founders → Country Leaders: Active
• Country Leaders → State Leaders: Ready when country leaders verified  
• State Leaders → City Leaders: Ready when state leaders verified

Government officials remain SEPARATE from contract governance system.
No contract roles assigned to government officials.
            """
            
            self.verification_chain_label.setText(chain_text)
            
        except Exception as e:
            print(f"Error updating verification chain: {e}")
    
    def filter_officials(self):
        """Filter officials table based on search criteria"""
        try:
            search_text = self.search_input.text().lower()
            country_filter = self.country_filter.currentData() or ""
            level_filter = self.level_filter.currentText().lower()
            status_filter = self.status_filter.currentData() or ""
            
            for row in range(self.officials_table.rowCount()):
                show_row = True
                
                # Apply search filter
                if search_text:
                    row_text = ""
                    for col in range(3):  # Name, title, jurisdiction
                        item = self.officials_table.item(row, col)
                        if item:
                            row_text += item.text().lower() + " "
                    
                    if search_text not in row_text:
                        show_row = False
                
                # Apply country filter
                if country_filter and show_row:
                    country_item = self.officials_table.item(row, 4)
                    if not country_item or country_item.text() != country_filter:
                        show_row = False
                
                # Apply level filter
                if level_filter != "all levels" and show_row:
                    level_item = self.officials_table.item(row, 2)
                    if not level_item or level_filter not in level_item.text().lower():
                        show_row = False
                
                # Apply status filter  
                if status_filter and show_row:
                    status_item = self.officials_table.item(row, 7)
                    if not status_item or status_filter not in status_item.text().lower():
                        show_row = False
                
                self.officials_table.setRowHidden(row, not show_row)
                
        except Exception as e:
            print(f"Error filtering officials: {e}")
    
    def on_official_double_click(self, row: int, column: int):
        """Handle double-click on official table row"""
        try:
            if not self.manager:
                return
            
            # Get official data from the row
            name_item = self.officials_table.item(row, 0)
            if not name_item:
                return
            
            # Find the official in the data
            all_officials = self.manager.search_officials()
            official_name = name_item.text()
            
            official_data = None
            for official in all_officials:
                if official.get('name') == official_name:
                    official_data = official
                    break
            
            if not official_data:
                return
            
            # Show context menu or action dialog
            self.show_official_actions(official_data)
            
        except Exception as e:
            print(f"Error handling official double-click: {e}")
    
    def show_official_actions(self, official_data: Dict[str, Any]):
        """Show actions dialog for official"""
        
        reply = QMessageBox.question(
            self, 
            f"Actions for {official_data.get('name', 'Official')}",
            f"What would you like to do with {official_data.get('name', 'this official')}?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        
        # Customize button text
        msg_box = QMessageBox()
        msg_box.setWindowTitle(f"Actions for {official_data.get('name', 'Official')}")
        msg_box.setText(f"Choose action for {official_data.get('name')}:")
        
        contact_btn = msg_box.addButton("📞 Record Contact", QMessageBox.YesRole)
        verify_btn = msg_box.addButton("✅ Verify Official", QMessageBox.NoRole) 
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)
        
        msg_box.exec_()
        
        clicked_button = msg_box.clickedButton()
        
        if clicked_button == contact_btn:
            self.record_contact_with_official(official_data)
        elif clicked_button == verify_btn:
            self.verify_official(official_data)
    
    def record_contact_with_official(self, official_data: Dict[str, Any]):
        """Record contact attempt with official"""
        
        dialog = ContactOfficialDialog(official_data, self)
        if dialog.exec_() == QDialog.Accepted:
            if not self.manager:
                return
            
            contact_data = dialog.contact_data
            
            success, message = self.manager.record_contact_attempt(
                official_id=official_data['official_id'],
                contact_method=contact_data['contact_method'],
                response_received=contact_data['response_received'],
                notes=contact_data['notes']
            )
            
            if success:
                QMessageBox.information(self, "Success", f"Contact recorded: {message}")
                self.load_data()  # Refresh data
            else:
                QMessageBox.warning(self, "Error", f"Failed to record contact: {message}")
    
    def verify_official(self, official_data: Dict[str, Any]):
        """Verify government official"""
        
        dialog = VerifyOfficialDialog(official_data, self)
        if dialog.exec_() == QDialog.Accepted:
            if not self.manager:
                return
            
            verification_data = dialog.verification_data
            
            success, message = self.manager.verify_government_official(
                official_id=official_data['official_id'],
                verified_by=verification_data['verifier_email'],
                verification_authority=verification_data['verification_authority'],
                verification_notes=verification_data['verification_notes']
            )
            
            if success:
                QMessageBox.information(self, "Success", f"Official verified: {message}")
                self.load_data()  # Refresh data
            else:
                QMessageBox.warning(self, "Error", f"Verification failed: {message}")
    
    def export_officials_csv(self):
        """Export officials directory to CSV"""
        try:
            if not self.manager:
                QMessageBox.warning(self, "Error", "Directory system not available")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Officials Directory", 
                f"government_officials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                success, message = self.manager.export_officials_csv(filename)
                
                if success:
                    QMessageBox.information(self, "Success", f"Directory exported: {message}")
                else:
                    QMessageBox.warning(self, "Error", f"Export failed: {message}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


# Demo function
def demo_government_directory_ui():
    """Demonstrate the government directory UI"""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create and show the directory tab
    tab = GovernmentDirectoryTab()
    tab.show()
    
    # Run the application
    sys.exit(app.exec_())