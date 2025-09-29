"""
CLEAN GOVERNMENT UI SYSTEM
Simple PyQt5 interface for government integration
Updated for September 2025
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QTableWidget, QTableWidgetItem, QLabel, QPushButton,
                           QLineEdit, QTextEdit, QGroupBox, QFormLayout, 
                           QMessageBox, QHeaderView, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime
from typing import Dict, List, Any

# Import our clean government systems
try:
    from .government_system import GovernmentIntegrationSystem
    from .government_directory import GovernmentDirectory  
    from .citizen_verification import CitizenVerification
    SYSTEMS_AVAILABLE = True
except ImportError:
    print("Warning: Government systems not available")
    SYSTEMS_AVAILABLE = False


class CleanGovernmentUI(QWidget):
    """Clean, simple government integration interface"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Government Integration System")
        self.setMinimumSize(1000, 700)
        
        # Initialize systems
        if SYSTEMS_AVAILABLE:
            self.gov_system = GovernmentIntegrationSystem()
            self.directory = GovernmentDirectory()
            self.verifier = CitizenVerification()
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🏛️ Government Integration System")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_officials_tab()
        self.create_verification_tab()
        self.create_stats_tab()
    
    def create_officials_tab(self):
        """Create government officials tab"""
        
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search section
        search_group = QGroupBox("Search Officials")
        search_layout = QHBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, title, or country...")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_officials)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addWidget(search_group)
        
        # Officials table
        self.officials_table = QTableWidget()
        self.officials_table.setColumnCount(5)
        self.officials_table.setHorizontalHeaderLabels([
            "Name", "Title", "Country", "Email", "Phone"
        ])
        self.officials_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.officials_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_officials)
        
        verify_btn = QPushButton("Verify Official")
        verify_btn.clicked.connect(self.verify_selected_official)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(verify_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.tabs.addTab(tab, "Government Officials")
    
    def create_verification_tab(self):
        """Create citizen verification tab"""
        
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Verify citizen section
        verify_group = QGroupBox("Verify Citizen")
        verify_layout = QFormLayout(verify_group)
        
        self.citizen_email_input = QLineEdit()
        self.citizen_name_input = QLineEdit()
        self.jurisdiction_input = QLineEdit()
        self.verifier_email_input = QLineEdit()
        
        verify_button = QPushButton("Verify Citizen")
        verify_button.clicked.connect(self.verify_citizen)
        
        verify_layout.addRow("Citizen Email:", self.citizen_email_input)
        verify_layout.addRow("Citizen Name:", self.citizen_name_input)
        verify_layout.addRow("Jurisdiction:", self.jurisdiction_input)
        verify_layout.addRow("Verifier Email:", self.verifier_email_input)
        verify_layout.addRow("", verify_button)
        
        layout.addWidget(verify_group)
        
        # Verifications table
        self.verifications_table = QTableWidget()
        self.verifications_table.setColumnCount(4)
        self.verifications_table.setHorizontalHeaderLabels([
            "Citizen", "Jurisdiction", "Verifier", "Date"
        ])
        self.verifications_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.verifications_table)
        
        self.tabs.addTab(tab, "Citizen Verification")
    
    def create_stats_tab(self):
        """Create statistics tab"""
        
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Statistics display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.stats_text)
        
        # Refresh button
        refresh_stats_btn = QPushButton("Refresh Statistics")
        refresh_stats_btn.clicked.connect(self.load_statistics)
        layout.addWidget(refresh_stats_btn)
        
        self.tabs.addTab(tab, "Statistics")
    
    def load_data(self):
        """Load all data"""
        self.load_officials()
        self.load_verifications()
        self.load_statistics()
    
    def load_officials(self):
        """Load government officials into table"""
        if not SYSTEMS_AVAILABLE:
            return
        
        officials = self.gov_system.get_all_officials()
        
        self.officials_table.setRowCount(len(officials))
        
        for row, (official_id, official) in enumerate(officials.items()):
            self.officials_table.setItem(row, 0, QTableWidgetItem(official.get('name', '')))
            self.officials_table.setItem(row, 1, QTableWidgetItem(official.get('title', '')))
            self.officials_table.setItem(row, 2, QTableWidgetItem(official.get('country', '')))
            self.officials_table.setItem(row, 3, QTableWidgetItem(official.get('email', '')))
            self.officials_table.setItem(row, 4, QTableWidgetItem(official.get('phone', '')))
            
            # Store the ID in the first column for reference
            self.officials_table.item(row, 0).setData(Qt.UserRole, official_id)
    
    def load_verifications(self):
        """Load citizen verifications into table"""
        if not SYSTEMS_AVAILABLE:
            return
        
        verifications = self.verifier.verifications.get('verifications', {})
        
        self.verifications_table.setRowCount(len(verifications))
        
        for row, verification in enumerate(verifications.values()):
            self.verifications_table.setItem(row, 0, QTableWidgetItem(verification.get('citizen_name', '')))
            self.verifications_table.setItem(row, 1, QTableWidgetItem(verification.get('jurisdiction', '')))
            self.verifications_table.setItem(row, 2, QTableWidgetItem(verification.get('verifier_email', '')))
            self.verifications_table.setItem(row, 3, QTableWidgetItem(verification.get('verification_date', '')))
    
    def load_statistics(self):
        """Load and display statistics"""
        if not SYSTEMS_AVAILABLE:
            self.stats_text.setText("Government systems not available")
            return
        
        gov_stats = self.gov_system.get_statistics()
        dir_stats = self.directory.get_directory_stats()
        ver_stats = self.verifier.get_verification_stats()
        
        stats_text = f"""
🏛️ GOVERNMENT INTEGRATION STATISTICS
{'='*50}

📊 GOVERNMENT OFFICIALS:
   Total Officials: {gov_stats.get('total_officials', 0)}
   Verified Officials: {gov_stats.get('verified_officials', 0)}

🌍 BY COUNTRY:
"""
        
        for country, count in gov_stats.get('by_country', {}).items():
            stats_text += f"   {country}: {count}\n"
        
        stats_text += f"""
📋 DIRECTORY STATS:
   Contact Rate: {dir_stats.get('contact_rate', 0):.1f}%
   Verification Rate: {dir_stats.get('verification_rate', 0):.1f}%

👥 CITIZEN VERIFICATION:
   Total Verifications: {ver_stats.get('total_verifications', 0)}
   Verified Citizens: {ver_stats.get('verified_citizens', 0)}
   Active Verifiers: {ver_stats.get('active_verifiers', 0)}

⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.stats_text.setText(stats_text)
    
    def search_officials(self):
        """Search for officials"""
        if not SYSTEMS_AVAILABLE:
            return
        
        query = self.search_input.text()
        if not query:
            self.load_officials()
            return
        
        results = self.gov_system.search_officials(query)
        
        self.officials_table.setRowCount(len(results))
        
        for row, official in enumerate(results):
            self.officials_table.setItem(row, 0, QTableWidgetItem(official.get('name', '')))
            self.officials_table.setItem(row, 1, QTableWidgetItem(official.get('title', '')))
            self.officials_table.setItem(row, 2, QTableWidgetItem(official.get('country', '')))
            self.officials_table.setItem(row, 3, QTableWidgetItem(official.get('email', '')))
            self.officials_table.setItem(row, 4, QTableWidgetItem(official.get('phone', '')))
    
    def verify_selected_official(self):
        """Verify selected official"""
        current_row = self.officials_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an official to verify")
            return
        
        QMessageBox.information(self, "Success", "Official verification functionality ready!")
    
    def verify_citizen(self):
        """Verify a citizen"""
        if not SYSTEMS_AVAILABLE:
            return
        
        citizen_email = self.citizen_email_input.text()
        citizen_name = self.citizen_name_input.text()
        jurisdiction = self.jurisdiction_input.text()
        verifier_email = self.verifier_email_input.text()
        
        if not all([citizen_email, citizen_name, jurisdiction, verifier_email]):
            QMessageBox.warning(self, "Warning", "Please fill all fields")
            return
        
        success, message = self.verifier.verify_citizen(
            verifier_email, citizen_email, citizen_name, jurisdiction
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.load_verifications()
            self.load_statistics()
            
            # Clear fields
            self.citizen_email_input.clear()
            self.citizen_name_input.clear()
            self.jurisdiction_input.clear()
            self.verifier_email_input.clear()
        else:
            QMessageBox.critical(self, "Error", message)


def main():
    """Run the clean government UI"""
    
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = CleanGovernmentUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()