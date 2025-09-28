"""
COUNTRY CONTRACT ELECTION USER INTERFACE - National Level Electoral System Management
PyQt5 interface for managing country-level contract governance elections with state electoral participation
Handles Contract Senator/Representative elections for country-level platform governance
"""

import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QTabWidget,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox, QMessageBox,
    QHeaderView, QProgressBar, QCheckBox, QScrollArea, QFrame,
    QSplitter, QTreeWidget, QTreeWidgetItem, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

try:
    from civic_desktop.governance.country_elections import (
        CountryElectionManager, CountryOffice, CountryElectionTrigger, 
        CountryElectionStatus, CountryElectionConfig
    )
    COUNTRY_ELECTIONS_AVAILABLE = True
except ImportError:
    COUNTRY_ELECTIONS_AVAILABLE = False

try:
    from civic_desktop.users.session import SessionManager
    SESSION_AVAILABLE = True
except ImportError:
    SESSION_AVAILABLE = False


class CountryRegistrationDialog(QDialog):
    """Dialog for registering new countries in the contract governance electoral system"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Country Contract Elections Registration")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Form for country registration
        form_layout = QFormLayout()
        
        self.country_name_input = QLineEdit()
        self.country_name_input.setPlaceholderText("Enter country name...")
        form_layout.addRow("Country Name:", self.country_name_input)
        
        self.population_input = QSpinBox()
        self.population_input.setRange(1000, 2000000000)  # 1K to 2 billion
        self.population_input.setValue(1000000)
        self.population_input.setSuffix(" people")
        form_layout.addRow("Total Population:", self.population_input)
        
        # Representation calculation display
        self.rep_calculation_label = QLabel()
        self.rep_calculation_label.setStyleSheet("color: blue; font-weight: bold;")
        form_layout.addRow("Representation:", self.rep_calculation_label)
        
        # Connect population change to update calculation
        self.population_input.valueChanged.connect(self.update_representation_calculation)
        self.update_representation_calculation()
        
        layout.addLayout(form_layout)
        
        # Information section
        info_group = QGroupBox("Country Contract Representation Rules")
        info_layout = QVBoxLayout()
        
        info_text = QLabel("""
        🏛️ Country Contract Governance Rules:
        • Minimum: 2 Contract Representatives + 2 Contract Senators
        • Additional: +1 Contract Representative per 1 million people
        • Elections triggered when 1% of states have full representation
        • Second trigger at 50% of states with representation
        • Terms: 1 year, maximum 4 consecutive terms
        """)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.register_btn = QPushButton("Register Country")
        self.register_btn.clicked.connect(self.register_country)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.register_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def update_representation_calculation(self):
        """Update the representation calculation display"""
        population = self.population_input.value()
        base_reps = 2
        additional_reps = population // 1000000  # 1 rep per million
        total_reps = base_reps + additional_reps
        senators = 2
        
        text = f"{total_reps} Contract Representatives ({base_reps} base + {additional_reps} from population), {senators} Contract Senators"
        self.rep_calculation_label.setText(text)
    
    def register_country(self):
        """Register the country"""
        country_name = self.country_name_input.text().strip()
        
        if not country_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a country name.")
            return
        
        self.accept()
    
    def get_country_data(self) -> Dict[str, Any]:
        """Get country registration data from form"""
        return {
            'country_name': self.country_name_input.text().strip(),
            'total_population_estimate': self.population_input.value()
        }


class CountryCandidateRegistrationDialog(QDialog):
    """Dialog for registering candidates for country contract governance office"""
    
    def __init__(self, country_id: str, country_name: str, parent=None):
        super().__init__(parent)
        self.country_id = country_id
        self.country_name = country_name
        
        self.setWindowTitle(f"Register Country Contract Candidate - {country_name}")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(f"Register as Contract Candidate - {country_name}")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header_label)
        
        # Form
        form_layout = QFormLayout()
        
        self.office_combo = QComboBox()
        self.office_combo.addItem("Contract Country Representative", CountryOffice.COUNTRY_REPRESENTATIVE.value)
        self.office_combo.addItem("Contract Country Senator", CountryOffice.COUNTRY_SENATOR.value)
        form_layout.addRow("Contract Office:", self.office_combo)
        
        self.platform_input = QTextEdit()
        self.platform_input.setPlaceholderText("Enter your platform statement...")
        self.platform_input.setMaximumHeight(100)
        form_layout.addRow("Platform Statement:", self.platform_input)
        
        self.slogan_input = QLineEdit()
        self.slogan_input.setPlaceholderText("Enter campaign slogan...")
        form_layout.addRow("Campaign Slogan:", self.slogan_input)
        
        layout.addLayout(form_layout)
        
        # Eligibility info
        eligibility_group = QGroupBox("Eligibility Requirements")
        eligibility_layout = QVBoxLayout()
        
        eligibility_text = QLabel("""
        📋 To run for Country Contract Office, you must:
        • Have served as a Contract State Representative or Senator
        • Be from a state within this country
        • Not exceed 4 consecutive term limit
        • Be in good standing with platform governance
        """)
        eligibility_text.setWordWrap(True)
        eligibility_layout.addWidget(eligibility_text)
        eligibility_group.setLayout(eligibility_layout)
        layout.addWidget(eligibility_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.register_btn = QPushButton("Register as Candidate")
        self.register_btn.clicked.connect(self.register_candidate)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.register_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def register_candidate(self):
        """Register as candidate"""
        platform = self.platform_input.toPlainText().strip()
        slogan = self.slogan_input.text().strip()
        
        if not platform:
            QMessageBox.warning(self, "Invalid Input", "Please enter a platform statement.")
            return
        
        if not slogan:
            QMessageBox.warning(self, "Invalid Input", "Please enter a campaign slogan.")
            return
        
        self.accept()
    
    def get_candidate_data(self) -> Dict[str, Any]:
        """Get candidate registration data"""
        return {
            'office': CountryOffice(self.office_combo.currentData()),
            'platform_statement': self.platform_input.toPlainText().strip(),
            'campaign_slogan': self.slogan_input.text().strip()
        }


class CountryElectionTab(QWidget):
    """Main tab for country contract elections management"""
    
    # Signals
    country_registered = pyqtSignal(str, str)  # country_id, country_name
    candidate_registered = pyqtSignal(str, str)  # candidate_id, country_id
    
    def __init__(self):
        super().__init__()
        
        # Initialize election manager
        if COUNTRY_ELECTIONS_AVAILABLE:
            self.election_manager = CountryElectionManager()
        else:
            self.election_manager = None
        
        self.init_ui()
        
        # Set up refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the user interface"""
        
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("🏛️ Country Contract Elections")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Action buttons
        self.register_country_btn = QPushButton("📝 Register Country")
        self.register_country_btn.clicked.connect(self.show_country_registration)
        header_layout.addWidget(self.register_country_btn)
        
        self.register_candidate_btn = QPushButton("🗳️ Register as Candidate")
        self.register_candidate_btn.clicked.connect(self.show_candidate_registration)
        self.register_candidate_btn.setEnabled(False)
        header_layout.addWidget(self.register_candidate_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Main content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Countries and elections
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Countries list
        countries_group = QGroupBox("Registered Countries")
        countries_layout = QVBoxLayout()
        
        self.countries_table = QTableWidget()
        self.countries_table.setColumnCount(5)
        self.countries_table.setHorizontalHeaderLabels([
            "Country", "Population", "Representatives", "Senators", "Status"
        ])
        self.countries_table.horizontalHeader().setStretchLastSection(True)
        self.countries_table.selectionBehavior = QTableWidget.SelectRows
        self.countries_table.itemSelectionChanged.connect(self.on_country_selected)
        countries_layout.addWidget(self.countries_table)
        
        countries_group.setLayout(countries_layout)
        left_layout.addWidget(countries_group)
        
        # Active elections
        elections_group = QGroupBox("Active Elections")
        elections_layout = QVBoxLayout()
        
        self.elections_table = QTableWidget()
        self.elections_table.setColumnCount(4)
        self.elections_table.setHorizontalHeaderLabels([
            "Country", "Status", "Candidates", "Voting Period"
        ])
        self.elections_table.horizontalHeader().setStretchLastSection(True)
        elections_layout.addWidget(self.elections_table)
        
        elections_group.setLayout(elections_layout)
        left_layout.addWidget(elections_group)
        
        left_panel.setLayout(left_layout)
        content_splitter.addWidget(left_panel)
        
        # Right panel - Details and actions
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Election details
        details_group = QGroupBox("Country Details")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Candidates list
        candidates_group = QGroupBox("Current Candidates")
        candidates_layout = QVBoxLayout()
        
        self.candidates_table = QTableWidget()
        self.candidates_table.setColumnCount(4)
        self.candidates_table.setHorizontalHeaderLabels([
            "Candidate", "Office", "Platform", "Slogan"
        ])
        self.candidates_table.horizontalHeader().setStretchLastSection(True)
        candidates_layout.addWidget(self.candidates_table)
        
        candidates_group.setLayout(candidates_layout)
        right_layout.addWidget(candidates_group)
        
        # Election actions
        actions_group = QGroupBox("Election Actions")
        actions_layout = QVBoxLayout()
        
        self.trigger_election_btn = QPushButton("🚀 Trigger Election")
        self.trigger_election_btn.clicked.connect(self.trigger_election)
        self.trigger_election_btn.setEnabled(False)
        actions_layout.addWidget(self.trigger_election_btn)
        
        self.view_results_btn = QPushButton("📊 View Results")
        self.view_results_btn.setEnabled(False)
        actions_layout.addWidget(self.view_results_btn)
        
        actions_group.setLayout(actions_layout)
        right_layout.addWidget(actions_group)
        
        right_panel.setLayout(right_layout)
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([600, 400])
        layout.addWidget(content_splitter)
        
        # Status bar
        self.status_label = QLabel("Ready - No countries registered")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Load initial data
        self.refresh_data()
    
    def show_country_registration(self):
        """Show country registration dialog"""
        
        if not self.election_manager:
            QMessageBox.warning(self, "System Error", "Country election system not available.")
            return
        
        dialog = CountryRegistrationDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            country_data = dialog.get_country_data()
            
            success, message, country_id = self.election_manager.register_country(
                country_name=country_data['country_name'],
                total_population_estimate=country_data['total_population_estimate']
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.country_registered.emit(country_id, country_data['country_name'])
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Registration Failed", message)
    
    def show_candidate_registration(self):
        """Show candidate registration dialog"""
        
        if not self.election_manager:
            QMessageBox.warning(self, "System Error", "Country election system not available.")
            return
        
        # Get selected country
        current_row = self.countries_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a country first.")
            return
        
        country_id = self.countries_table.item(current_row, 0).data(Qt.UserRole)
        country_name = self.countries_table.item(current_row, 0).text()
        
        if not SESSION_AVAILABLE:
            QMessageBox.warning(self, "Authentication Required", "Please log in to register as candidate.")
            return
        
        dialog = CountryCandidateRegistrationDialog(country_id, country_name, self)
        
        if dialog.exec_() == QDialog.Accepted:
            candidate_data = dialog.get_candidate_data()
            
            # Get current user email (placeholder)
            user_email = "current_user@example.com"  # Replace with actual session management
            
            success, message = self.election_manager.register_country_candidate(
                country_id=country_id,
                user_email=user_email,
                office=candidate_data['office'],
                platform_statement=candidate_data['platform_statement'],
                campaign_slogan=candidate_data['campaign_slogan']
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.candidate_registered.emit("", country_id)
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Registration Failed", message)
    
    def trigger_election(self):
        """Trigger country election for selected country"""
        
        if not self.election_manager:
            return
        
        current_row = self.countries_table.currentRow()
        if current_row < 0:
            return
        
        country_id = self.countries_table.item(current_row, 0).data(Qt.UserRole)
        
        # Check if election can be triggered
        can_trigger, trigger_type, message = self.election_manager.check_election_triggers(country_id)
        
        if can_trigger:
            reply = QMessageBox.question(
                self, "Trigger Election",
                f"Trigger country contract election?\n\nReason: {message}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, msg, election_id = self.election_manager.create_country_election(country_id, trigger_type)
                
                if success:
                    QMessageBox.information(self, "Election Created", msg)
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Election Failed", msg)
        else:
            QMessageBox.information(self, "Cannot Trigger Election", message)
    
    def on_country_selected(self):
        """Handle country selection change"""
        
        current_row = self.countries_table.currentRow()
        if current_row < 0:
            self.details_text.clear()
            self.candidates_table.setRowCount(0)
            self.register_candidate_btn.setEnabled(False)
            self.trigger_election_btn.setEnabled(False)
            return
        
        country_id = self.countries_table.item(current_row, 0).data(Qt.UserRole)
        self.update_country_details(country_id)
        self.register_candidate_btn.setEnabled(True)
        
        # Check if election can be triggered
        if self.election_manager:
            can_trigger, _, _ = self.election_manager.check_election_triggers(country_id)
            self.trigger_election_btn.setEnabled(can_trigger)
    
    def update_country_details(self, country_id: str):
        """Update country details display"""
        
        if not self.election_manager:
            return
        
        rep_info = self.election_manager.get_country_representation(country_id)
        
        if rep_info and 'error' not in rep_info:
            details = f"""
Country: {rep_info['country_name']}
Population: {rep_info['population']:,}
Total Representatives: {rep_info['total_representatives']}
Total Senators: {rep_info['total_senators']}

Calculation: {rep_info['rep_calculation']}

Additional Representatives from Population: {rep_info['additional_reps_from_population']}
            """.strip()
            
            self.details_text.setPlainText(details)
        else:
            self.details_text.setPlainText("Error loading country details.")
    
    def refresh_data(self):
        """Refresh all data displays"""
        
        if not self.election_manager:
            self.status_label.setText("Country election system not available")
            return
        
        # Update countries table (placeholder)
        self.countries_table.setRowCount(0)
        
        # Update elections table (placeholder)  
        self.elections_table.setRowCount(0)
        
        # Update candidates table (placeholder)
        self.candidates_table.setRowCount(0)
        
        self.status_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")


# Test the country election UI
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create and show the country election tab
    tab = CountryElectionTab()
    tab.show()
    
    sys.exit(app.exec_())