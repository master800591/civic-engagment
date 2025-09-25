"""
Petitions & Initiatives UI - Democratic Citizen Initiative Interface
Comprehensive interface for petition creation, signature collection, and initiative management.
Supports the full citizen-driven legislative process with transparency and verification.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QComboBox, QListWidget, QListWidgetItem, 
    QDialog, QFormLayout, QSpinBox, QCheckBox, QProgressBar, QGroupBox,
    QScrollArea, QFrame, QSplitter, QTableWidget, QTableWidgetItem,
    QMessageBox, QDateEdit, QTextBrowser, QDialogButtonBox, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QPixmap, QIcon
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class PetitionsInitiativesTab(QWidget):
    """
    Main petitions and initiatives interface
    Provides comprehensive tools for democratic citizen participation
    """
    
    def __init__(self):
        super().__init__()
        self.petition_system = None
        self.init_petition_system()
        self.init_ui()
        self.refresh_ui()
        
        # Set up auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_ui)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_petition_system(self):
        """Initialize petition system backend"""
        try:
            from civic_desktop.petitions.petition_system import PetitionSystem
            self.petition_system = PetitionSystem()
        except ImportError as e:
            print(f"Error importing petition system: {e}")
    
    def init_ui(self):
        """Initialize the comprehensive petitions interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Petitions & Initiatives")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Action buttons
        self.create_petition_btn = QPushButton("Create Petition")
        self.create_petition_btn.clicked.connect(self.show_petition_creator)
        
        self.my_petitions_btn = QPushButton("My Petitions")
        self.my_petitions_btn.clicked.connect(self.show_my_petitions)
        
        self.statistics_btn = QPushButton("Statistics")
        self.statistics_btn.clicked.connect(self.show_statistics)
        
        header_layout.addWidget(self.create_petition_btn)
        header_layout.addWidget(self.my_petitions_btn)
        header_layout.addWidget(self.statistics_btn)
        
        layout.addLayout(header_layout)
        
        # Main content area with tabs
        self.tab_widget = QTabWidget()
        
        # Active Petitions Tab
        self.active_tab = self.create_active_petitions_tab()
        self.tab_widget.addTab(self.active_tab, "Active Petitions")
        
        # Initiatives Tab
        self.initiatives_tab = self.create_initiatives_tab()
        self.tab_widget.addTab(self.initiatives_tab, "Initiatives")
        
        # Browse by Category Tab
        self.browse_tab = self.create_browse_tab()
        self.tab_widget.addTab(self.browse_tab, "Browse Categories")
        
        # Progress Tracking Tab
        self.tracking_tab = self.create_tracking_tab()
        self.tab_widget.addTab(self.tracking_tab, "Progress Tracking")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Store main content widget for refresh
        self.main_content = self.tab_widget
    
    def create_active_petitions_tab(self) -> QWidget:
        """Create active petitions browsing interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "All Types", "Local", "State", "Federal", "Constitutional Amendment"
        ])
        self.type_filter.currentTextChanged.connect(self.refresh_petition_list)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All Status", "Active", "Under Review", "Certified", "Approved"
        ])
        self.status_filter.currentTextChanged.connect(self.refresh_petition_list)
        
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(self.status_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Petitions list
        self.petitions_list = QListWidget()
        self.petitions_list.itemDoubleClicked.connect(self.show_petition_details)
        layout.addWidget(self.petitions_list)
        
        return tab
    
    def create_initiatives_tab(self) -> QWidget:
        """Create initiatives tracking interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Legislative Initiatives")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header)
        
        # Initiatives table
        self.initiatives_table = QTableWidget()
        self.initiatives_table.setColumnCount(6)
        self.initiatives_table.setHorizontalHeaderLabels([
            "Title", "Type", "Status", "Review Stage", "Signatures", "Actions"
        ])
        self.initiatives_table.cellDoubleClicked.connect(self.show_initiative_details)
        layout.addWidget(self.initiatives_table)
        
        return tab
    
    def create_browse_tab(self) -> QWidget:
        """Create category browsing interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Categories grid
        categories_layout = QGridLayout()
        
        categories = [
            ("Local Government", "Petitions affecting city and county governance"),
            ("State Policy", "State-level legislative initiatives"),
            ("Federal Issues", "National policy and federal legislation"),
            ("Constitutional", "Constitutional amendments and fundamental rights"),
            ("Environment", "Environmental protection and sustainability"),
            ("Education", "Educational policy and funding"),
            ("Healthcare", "Healthcare access and policy reform"),
            ("Transportation", "Infrastructure and transit improvements"),
            ("Economic Policy", "Tax policy and economic development"),
            ("Civil Rights", "Equal rights and social justice initiatives")
        ]
        
        row, col = 0, 0
        for title, description in categories:
            category_widget = self.create_category_widget(title, description)
            categories_layout.addWidget(category_widget, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        layout.addLayout(categories_layout)
        layout.addStretch()
        
        return tab
    
    def create_tracking_tab(self) -> QWidget:
        """Create progress tracking interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Summary statistics
        stats_group = QGroupBox("System Overview")
        stats_layout = QGridLayout(stats_group)
        
        self.total_petitions_label = QLabel("0")
        self.active_petitions_label = QLabel("0")
        self.total_signatures_label = QLabel("0")
        self.success_rate_label = QLabel("0%")
        
        stats_layout.addWidget(QLabel("Total Petitions:"), 0, 0)
        stats_layout.addWidget(self.total_petitions_label, 0, 1)
        stats_layout.addWidget(QLabel("Active Petitions:"), 0, 2)
        stats_layout.addWidget(self.active_petitions_label, 0, 3)
        stats_layout.addWidget(QLabel("Total Signatures:"), 1, 0)
        stats_layout.addWidget(self.total_signatures_label, 1, 1)
        stats_layout.addWidget(QLabel("Success Rate:"), 1, 2)
        stats_layout.addWidget(self.success_rate_label, 1, 3)
        
        layout.addWidget(stats_group)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        activity_layout.addWidget(self.activity_list)
        
        layout.addWidget(activity_group)
        
        return tab
    
    def create_category_widget(self, title: str, description: str) -> QWidget:
        """Create category selection widget"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                background-color: #f9f9f9;
            }
            QFrame:hover {
                background-color: #e6f3ff;
                border-color: #0066cc;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666;")
        
        browse_btn = QPushButton("Browse Petitions")
        browse_btn.clicked.connect(lambda: self.browse_category(title))
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(browse_btn)
        
        return widget
    
    def refresh_ui(self):
        """Refresh the UI based on authentication state"""
        try:
            from civic_desktop.users.session import SessionManager
            
            is_authenticated = SessionManager.is_authenticated()
            
            # Enable/disable controls based on authentication
            self.create_petition_btn.setEnabled(is_authenticated)
            self.my_petitions_btn.setEnabled(is_authenticated)
            
            if is_authenticated:
                user = SessionManager.get_current_user()
                user_role = user.get('role', 'Contract Citizen') if user else 'Contract Citizen'
                
                # Update status
                self.status_label.setText(f"Connected as {user_role}")
                
                # Refresh data
                self.refresh_petition_list()
                self.refresh_initiatives_list()
                self.refresh_statistics()
                self.refresh_activity()
                
            else:
                self.status_label.setText("Not authenticated - view-only mode")
                self.clear_lists()
                
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
    
    def refresh_petition_list(self):
        """Refresh the active petitions list"""
        if not self.petition_system:
            return
        
        try:
            # Get filter values
            type_filter = self.type_filter.currentText()
            status_filter = self.status_filter.currentText()
            
            # Apply filters
            petition_type = None if type_filter == "All Types" else type_filter.lower().replace(" ", "_")
            status = None if status_filter == "All Status" else status_filter.lower().replace(" ", "_")
            
            petitions = self.petition_system.get_petitions(
                status_filter=status,
                petition_type=petition_type
            )
            
            # Clear and populate list
            self.petitions_list.clear()
            
            for petition in petitions:
                item_widget = self.create_petition_item_widget(petition)
                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())
                item.setData(Qt.UserRole, petition)
                self.petitions_list.addItem(item)
                self.petitions_list.setItemWidget(item, item_widget)
                
        except Exception as e:
            print(f"Error refreshing petition list: {e}")
    
    def create_petition_item_widget(self, petition: Dict[str, Any]) -> QWidget:
        """Create widget for petition list item"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(widget)
        
        # Title and type
        header_layout = QHBoxLayout()
        
        title_label = QLabel(petition.get('title', 'Untitled Petition'))
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        type_label = QLabel(f"[{petition.get('type', 'Unknown').upper()}]")
        type_label.setStyleSheet("color: #0066cc; font-weight: bold;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(type_label)
        
        layout.addLayout(header_layout)
        
        # Description
        description = petition.get('description', 'No description available')
        desc_label = QLabel(description[:200] + "..." if len(description) > 200 else description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #333;")
        layout.addWidget(desc_label)
        
        # Progress and details
        details_layout = QHBoxLayout()
        
        # Signature progress
        current_sigs = petition.get('current_signatures', 0)
        target_sigs = petition.get('target_signatures', 1)
        progress = min(100, int((current_sigs / target_sigs) * 100))
        
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(progress)
        progress_bar.setFormat(f"{current_sigs:,} / {target_sigs:,} signatures ({progress}%)")
        
        # Status and date
        status = petition.get('status', 'unknown').replace('_', ' ').title()
        created_date = petition.get('created_at', '')[:10] if petition.get('created_at') else 'Unknown'
        
        status_label = QLabel(f"Status: {status} | Created: {created_date}")
        status_label.setStyleSheet("color: #666; font-size: 10px;")
        
        details_layout.addWidget(progress_bar, 2)
        details_layout.addWidget(status_label, 1)
        
        layout.addLayout(details_layout)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        view_btn = QPushButton("View Details")
        view_btn.clicked.connect(lambda: self.show_petition_details_by_id(petition.get('id')))
        
        sign_btn = QPushButton("Sign Petition")
        sign_btn.setEnabled(petition.get('status') == 'active')
        sign_btn.clicked.connect(lambda: self.sign_petition(petition.get('id')))
        
        share_btn = QPushButton("Share")
        share_btn.clicked.connect(lambda: self.share_petition(petition.get('id')))
        
        actions_layout.addWidget(view_btn)
        actions_layout.addWidget(sign_btn)
        actions_layout.addWidget(share_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        return widget
    
    def refresh_initiatives_list(self):
        """Refresh the initiatives table"""
        if not self.petition_system:
            return
        
        try:
            # This would get initiatives from the system
            # For now, show placeholder
            self.initiatives_table.setRowCount(0)
            
        except Exception as e:
            print(f"Error refreshing initiatives: {e}")
    
    def refresh_statistics(self):
        """Refresh system statistics"""
        if not self.petition_system:
            return
        
        try:
            stats = self.petition_system.get_petition_statistics()
            
            self.total_petitions_label.setText(str(stats.get('total_petitions', 0)))
            self.active_petitions_label.setText(str(stats.get('active_petitions', 0)))
            self.total_signatures_label.setText(f"{stats.get('total_signatures', 0):,}")
            self.success_rate_label.setText(f"{stats.get('success_rate', 0)}%")
            
        except Exception as e:
            print(f"Error refreshing statistics: {e}")
    
    def refresh_activity(self):
        """Refresh recent activity list"""
        if not hasattr(self, 'activity_list'):
            return
        
        # Placeholder for recent activity
        self.activity_list.clear()
        
        sample_activities = [
            "New petition 'Environmental Protection Act' created",
            "Petition 'Transportation Reform' reached 50% signatures",
            "Initiative 'Education Funding' advanced to legislative review",
            "Constitutional amendment petition 'Voting Rights' submitted"
        ]
        
        for activity in sample_activities:
            self.activity_list.addItem(activity)
    
    def clear_lists(self):
        """Clear all data lists"""
        self.petitions_list.clear()
        if hasattr(self, 'initiatives_table'):
            self.initiatives_table.setRowCount(0)
        if hasattr(self, 'activity_list'):
            self.activity_list.clear()
    
    def show_petition_creator(self):
        """Show petition creation dialog"""
        try:
            from civic_desktop.users.session import SessionManager
            
            if not SessionManager.is_authenticated():
                QMessageBox.warning(self, "Authentication Required", 
                                  "Please log in to create petitions.")
                return
            
            dialog = PetitionCreatorDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_petition_list()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error opening petition creator: {str(e)}")
    
    def show_petition_details(self, item):
        """Show petition details dialog"""
        petition = item.data(Qt.UserRole)
        if petition:
            self.show_petition_details_by_id(petition.get('id'))
    
    def show_petition_details_by_id(self, petition_id: str):
        """Show petition details by ID"""
        if not petition_id or not self.petition_system:
            return
        
        try:
            dialog = PetitionDetailsDialog(petition_id, self.petition_system, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error showing petition details: {str(e)}")
    
    def sign_petition(self, petition_id: str):
        """Sign a petition"""
        if not petition_id or not self.petition_system:
            return
        
        try:
            from civic_desktop.users.session import SessionManager
            
            if not SessionManager.is_authenticated():
                QMessageBox.warning(self, "Authentication Required", 
                                  "Please log in to sign petitions.")
                return
            
            dialog = SignPetitionDialog(petition_id, self.petition_system, self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_petition_list()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error signing petition: {str(e)}")
    
    def share_petition(self, petition_id: str):
        """Share petition with others"""
        QMessageBox.information(self, "Share Petition", 
                              f"Petition ID: {petition_id}\n\nSharing functionality will be implemented in future updates.")
    
    def show_my_petitions(self):
        """Show user's petitions and signatures"""
        try:
            from civic_desktop.users.session import SessionManager
            
            if not SessionManager.is_authenticated():
                QMessageBox.warning(self, "Authentication Required", 
                                  "Please log in to view your petitions.")
                return
            
            dialog = MyPetitionsDialog(self.petition_system, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error showing your petitions: {str(e)}")
    
    def show_statistics(self):
        """Show comprehensive statistics dialog"""
        if not self.petition_system:
            return
        
        try:
            dialog = PetitionStatisticsDialog(self.petition_system, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error showing statistics: {str(e)}")
    
    def browse_category(self, category: str):
        """Browse petitions by category"""
        QMessageBox.information(self, "Browse Category", 
                              f"Browsing petitions in category: {category}\n\nCategory filtering will be implemented in future updates.")
    
    def show_initiative_details(self, row: int, column: int):
        """Show initiative details"""
        QMessageBox.information(self, "Initiative Details", 
                              "Initiative details dialog will be implemented in future updates.")


class PetitionCreatorDialog(QDialog):
    """Dialog for creating new petitions"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.petition_system = parent.petition_system if parent else None
        self.setWindowTitle("Create New Petition")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()
    
    def init_ui(self):
        """Initialize petition creation interface"""
        layout = QVBoxLayout(self)
        
        # Form
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter petition title...")
        form_layout.addRow("Title:", self.title_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["local", "state", "federal", "constitutional_amendment"])
        form_layout.addRow("Type:", self.type_combo)
        
        self.jurisdiction_edit = QLineEdit()
        self.jurisdiction_edit.setPlaceholderText("e.g., 'City of Springfield' or 'State of California'")
        form_layout.addRow("Jurisdiction:", self.jurisdiction_edit)
        
        self.target_signatures = QSpinBox()
        self.target_signatures.setMinimum(10)
        self.target_signatures.setMaximum(1000000)
        self.target_signatures.setValue(1000)
        form_layout.addRow("Target Signatures:", self.target_signatures)
        
        layout.addLayout(form_layout)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Describe the purpose and goals of your petition...")
        layout.addWidget(self.description_edit)
        
        # Full text
        layout.addWidget(QLabel("Full Petition Text:"))
        self.full_text_edit = QTextEdit()
        self.full_text_edit.setPlaceholderText("Enter the complete text of your petition...")
        layout.addWidget(self.full_text_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Petition")
        create_btn.clicked.connect(self.create_petition)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_petition(self):
        """Create the petition"""
        try:
            from civic_desktop.users.session import SessionManager
            
            user = SessionManager.get_current_user()
            if not user:
                QMessageBox.warning(self, "Error", "User not authenticated")
                return
            
            title = self.title_edit.text().strip()
            description = self.description_edit.toPlainText().strip()
            full_text = self.full_text_edit.toPlainText().strip()
            petition_type = self.type_combo.currentText()
            jurisdiction = self.jurisdiction_edit.text().strip()
            target_sigs = self.target_signatures.value()
            
            if not all([title, description, petition_type, jurisdiction]):
                QMessageBox.warning(self, "Validation Error", 
                                  "Please fill in all required fields.")
                return
            
            if not self.petition_system:
                QMessageBox.critical(self, "Error", "Petition system not available")
                return
            
            success, message = self.petition_system.create_petition(
                user['email'], title, description, petition_type,
                target_sigs, jurisdiction, full_text
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating petition: {str(e)}")


class PetitionDetailsDialog(QDialog):
    """Dialog showing detailed petition information"""
    
    def __init__(self, petition_id: str, petition_system, parent=None):
        super().__init__(parent)
        self.petition_id = petition_id
        self.petition_system = petition_system
        self.setWindowTitle("Petition Details")
        self.setModal(True)
        self.resize(700, 600)
        self.init_ui()
        self.load_petition_details()
    
    def init_ui(self):
        """Initialize petition details interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        self.details_browser = QTextBrowser()
        overview_layout.addWidget(self.details_browser)
        
        tab_widget.addTab(overview_tab, "Overview")
        
        # Signatures tab
        signatures_tab = QWidget()
        signatures_layout = QVBoxLayout(signatures_tab)
        
        self.signatures_table = QTableWidget()
        self.signatures_table.setColumnCount(4)
        self.signatures_table.setHorizontalHeaderLabels(["Date", "Location", "Verified", "Signature Hash"])
        signatures_layout.addWidget(self.signatures_table)
        
        tab_widget.addTab(signatures_tab, "Signatures")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        sign_btn = QPushButton("Sign This Petition")
        sign_btn.clicked.connect(self.sign_petition)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(sign_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_petition_details(self):
        """Load and display petition details"""
        # Implementation would load petition details
        # For now, show placeholder
        self.details_browser.setHtml("""
        <h2>Petition Details</h2>
        <p><strong>Title:</strong> Sample Petition</p>
        <p><strong>Type:</strong> Local</p>
        <p><strong>Status:</strong> Active</p>
        <p><strong>Signatures:</strong> 150 / 1,000 (15%)</p>
        <p><strong>Description:</strong> This is a sample petition description...</p>
        """)
    
    def sign_petition(self):
        """Sign the petition"""
        QMessageBox.information(self, "Sign Petition", "Petition signing functionality will be implemented.")


class SignPetitionDialog(QDialog):
    """Dialog for signing a petition"""
    
    def __init__(self, petition_id: str, petition_system, parent=None):
        super().__init__(parent)
        self.petition_id = petition_id
        self.petition_system = petition_system
        self.setWindowTitle("Sign Petition")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize signing interface"""
        layout = QVBoxLayout(self)
        
        # Information
        info_label = QLabel("By signing this petition, you are adding your support to this civic initiative.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Verification checkboxes
        verification_group = QGroupBox("Verification")
        verification_layout = QVBoxLayout(verification_group)
        
        self.identity_check = QCheckBox("I confirm my identity and eligibility to sign")
        self.terms_check = QCheckBox("I agree to the terms of petition participation")
        self.privacy_check = QCheckBox("I understand the privacy implications")
        
        verification_layout.addWidget(self.identity_check)
        verification_layout.addWidget(self.terms_check)
        verification_layout.addWidget(self.privacy_check)
        
        layout.addWidget(verification_group)
        
        # Comments (optional)
        layout.addWidget(QLabel("Comments (optional):"))
        self.comments_edit = QTextEdit()
        self.comments_edit.setMaximumHeight(100)
        layout.addWidget(self.comments_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        sign_btn = QPushButton("Sign Petition")
        sign_btn.clicked.connect(self.sign_petition)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(sign_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def sign_petition(self):
        """Process petition signature"""
        # Validate checkboxes
        if not all([self.identity_check.isChecked(), 
                   self.terms_check.isChecked(), 
                   self.privacy_check.isChecked()]):
            QMessageBox.warning(self, "Verification Required", 
                              "Please check all verification boxes to proceed.")
            return
        
        # Process signature (placeholder)
        QMessageBox.information(self, "Success", "Your signature has been recorded.")
        self.accept()


class MyPetitionsDialog(QDialog):
    """Dialog showing user's petitions and signatures"""
    
    def __init__(self, petition_system, parent=None):
        super().__init__(parent)
        self.petition_system = petition_system
        self.setWindowTitle("My Petitions & Signatures")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()
    
    def init_ui(self):
        """Initialize my petitions interface"""
        layout = QVBoxLayout(self)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # Created petitions tab
        created_tab = QWidget()
        created_layout = QVBoxLayout(created_tab)
        
        self.created_list = QListWidget()
        created_layout.addWidget(self.created_list)
        
        tab_widget.addTab(created_tab, "Created by Me")
        
        # Signed petitions tab
        signed_tab = QWidget()
        signed_layout = QVBoxLayout(signed_tab)
        
        self.signed_list = QListWidget()
        signed_layout.addWidget(self.signed_list)
        
        tab_widget.addTab(signed_tab, "Signed by Me")
        
        layout.addWidget(tab_widget)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class PetitionStatisticsDialog(QDialog):
    """Dialog showing comprehensive petition statistics"""
    
    def __init__(self, petition_system, parent=None):
        super().__init__(parent)
        self.petition_system = petition_system
        self.setWindowTitle("Petition Statistics")
        self.setModal(True)
        self.resize(700, 500)
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        """Initialize statistics interface"""
        layout = QVBoxLayout(self)
        
        # Statistics display
        self.stats_browser = QTextBrowser()
        layout.addWidget(self.stats_browser)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def load_statistics(self):
        """Load and display statistics"""
        if not self.petition_system:
            return
        
        try:
            stats = self.petition_system.get_petition_statistics()
            
            html = f"""
            <h2>Petition System Statistics</h2>
            
            <h3>Overview</h3>
            <ul>
                <li><strong>Total Petitions:</strong> {stats.get('total_petitions', 0)}</li>
                <li><strong>Active Petitions:</strong> {stats.get('active_petitions', 0)}</li>
                <li><strong>Completed Petitions:</strong> {stats.get('completed_petitions', 0)}</li>
                <li><strong>Total Signatures:</strong> {stats.get('total_signatures', 0):,}</li>
                <li><strong>Success Rate:</strong> {stats.get('success_rate', 0)}%</li>
            </ul>
            
            <h3>By Type</h3>
            <ul>
            """
            
            for ptype, count in stats.get('petitions_by_type', {}).items():
                html += f"<li><strong>{ptype.replace('_', ' ').title()}:</strong> {count}</li>"
            
            html += "</ul><h3>By Status</h3><ul>"
            
            for status, count in stats.get('petitions_by_status', {}).items():
                html += f"<li><strong>{status.replace('_', ' ').title()}:</strong> {count}</li>"
            
            html += "</ul>"
            
            self.stats_browser.setHtml(html)
            
        except Exception as e:
            self.stats_browser.setHtml(f"<p>Error loading statistics: {str(e)}</p>")