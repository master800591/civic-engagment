"""
WORLD CONTRACT ELECTION USER INTERFACE - Global Level Electoral System Management
PyQt5 interface for managing world-level contract governance elections with country electoral participation
Handles Contract Senator/Representative elections for world-level platform governance
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
    from civic_desktop.governance.world_elections import (
        WorldElectionManager, WorldOffice, WorldElectionTrigger, 
        WorldElectionStatus, WorldElectionConfig
    )
    WORLD_ELECTIONS_AVAILABLE = True
except ImportError:
    WORLD_ELECTIONS_AVAILABLE = False

try:
    from civic_desktop.users.session import SessionManager
    SESSION_AVAILABLE = True
except ImportError:
    SESSION_AVAILABLE = False


class WorldPopulationUpdateDialog(QDialog):
    """Dialog for updating world population estimate"""
    
    def __init__(self, current_population: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update World Population")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Current population display
        current_label = QLabel(f"Current World Population: {current_population:,}")
        current_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(current_label)
        
        # Form for population update
        form_layout = QFormLayout()
        
        self.population_input = QSpinBox()
        self.population_input.setRange(1000000, 20000000000)  # 1M to 20 billion
        self.population_input.setValue(current_population)
        self.population_input.setSuffix(" people")
        form_layout.addRow("New Population:", self.population_input)
        
        # Representation calculation display
        self.rep_calculation_label = QLabel()
        self.rep_calculation_label.setStyleSheet("color: blue; font-weight: bold;")
        form_layout.addRow("New Representation:", self.rep_calculation_label)
        
        # Connect population change to update calculation
        self.population_input.valueChanged.connect(self.update_representation_calculation)
        self.update_representation_calculation()
        
        layout.addLayout(form_layout)
        
        # Information section
        info_group = QGroupBox("World Contract Representation Rules")
        info_layout = QVBoxLayout()
        
        info_text = QLabel("""
        🌍 World Contract Governance Rules:
        • Minimum: 2 Contract Representatives + 2 Contract Senators
        • Additional: +1 Contract Representative per 4 million people
        • Elections triggered when 1% of countries have full representation
        • Second trigger at 50% of countries with representation
        • Terms: 1 year, maximum 4 consecutive terms
        • Format: "Contract Senator/Representative for World"
        """)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.update_btn = QPushButton("Update Population")
        self.update_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def update_representation_calculation(self):
        """Update the representation calculation display"""
        population = self.population_input.value()
        base_reps = 2
        additional_reps = population // 4000000  # 1 rep per 4 million
        total_reps = base_reps + additional_reps
        senators = 2
        
        text = f"{total_reps} Contract Representatives ({base_reps} base + {additional_reps} from population), {senators} Contract Senators"
        self.rep_calculation_label.setText(text)
    
    def get_population(self) -> int:
        """Get updated population value"""
        return self.population_input.value()


class WorldCandidateRegistrationDialog(QDialog):
    """Dialog for registering candidates for world contract governance office"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register World Contract Candidate")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Register as Contract Candidate for World")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header_label)
        
        # Form
        form_layout = QFormLayout()
        
        self.office_combo = QComboBox()
        self.office_combo.addItem("Contract World Representative", WorldOffice.WORLD_REPRESENTATIVE.value)
        self.office_combo.addItem("Contract World Senator", WorldOffice.WORLD_SENATOR.value)
        form_layout.addRow("Contract Office:", self.office_combo)
        
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("Enter your country of origin...")
        form_layout.addRow("Country of Origin:", self.country_input)
        
        self.platform_input = QTextEdit()
        self.platform_input.setPlaceholderText("Enter your global platform statement...")
        self.platform_input.setMaximumHeight(120)
        form_layout.addRow("Platform Statement:", self.platform_input)
        
        self.slogan_input = QLineEdit()
        self.slogan_input.setPlaceholderText("Enter campaign slogan...")
        form_layout.addRow("Campaign Slogan:", self.slogan_input)
        
        layout.addLayout(form_layout)
        
        # Eligibility info
        eligibility_group = QGroupBox("Eligibility Requirements")
        eligibility_layout = QVBoxLayout()
        
        eligibility_text = QLabel("""
        📋 To run for World Contract Office, you must:
        • Have served as a Contract Country Representative or Senator
        • Be from a registered country within the platform
        • Not exceed 4 consecutive term limit
        • Be in good standing with platform governance
        • Have a global vision for digital democracy
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
        country = self.country_input.text().strip()
        
        if not platform:
            QMessageBox.warning(self, "Invalid Input", "Please enter a platform statement.")
            return
        
        if not slogan:
            QMessageBox.warning(self, "Invalid Input", "Please enter a campaign slogan.")
            return
            
        if not country:
            QMessageBox.warning(self, "Invalid Input", "Please enter your country of origin.")
            return
        
        self.accept()
    
    def get_candidate_data(self) -> Dict[str, Any]:
        """Get candidate registration data"""
        return {
            'office': WorldOffice(self.office_combo.currentData()),
            'platform_statement': self.platform_input.toPlainText().strip(),
            'campaign_slogan': self.slogan_input.text().strip(),
            'country_of_origin': self.country_input.text().strip()
        }


class WorldElectionTab(QWidget):
    """Main tab for world contract elections management"""
    
    # Signals
    population_updated = pyqtSignal(int)  # new_population
    candidate_registered = pyqtSignal(str)  # candidate_id
    
    def __init__(self):
        super().__init__()
        
        # Initialize election manager
        if WORLD_ELECTIONS_AVAILABLE:
            self.election_manager = WorldElectionManager()
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
        title_label = QLabel("🌍 World Contract Elections")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Action buttons
        self.update_population_btn = QPushButton("📊 Update Population")
        self.update_population_btn.clicked.connect(self.show_population_update)
        header_layout.addWidget(self.update_population_btn)
        
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
        
        # Left panel - World status and representation
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # World representation info
        world_group = QGroupBox("World Representation")
        world_layout = QVBoxLayout()
        
        self.world_info_text = QTextEdit()
        self.world_info_text.setReadOnly(True)
        self.world_info_text.setMaximumHeight(150)
        world_layout.addWidget(self.world_info_text)
        
        world_group.setLayout(world_layout)
        left_layout.addWidget(world_group)
        
        # Active election status
        election_group = QGroupBox("Active World Election")
        election_layout = QVBoxLayout()
        
        self.election_status_text = QTextEdit()
        self.election_status_text.setReadOnly(True)
        self.election_status_text.setMaximumHeight(120)
        election_layout.addWidget(self.election_status_text)
        
        election_group.setLayout(election_layout)
        left_layout.addWidget(election_group)
        
        # Election triggers
        triggers_group = QGroupBox("Election Triggers")
        triggers_layout = QVBoxLayout()
        
        self.trigger_info_text = QTextEdit()
        self.trigger_info_text.setReadOnly(True)
        self.trigger_info_text.setMaximumHeight(100)
        triggers_layout.addWidget(self.trigger_info_text)
        
        self.trigger_election_btn = QPushButton("🚀 Trigger Election")
        self.trigger_election_btn.clicked.connect(self.trigger_election)
        self.trigger_election_btn.setEnabled(False)
        triggers_layout.addWidget(self.trigger_election_btn)
        
        triggers_group.setLayout(triggers_layout)
        left_layout.addWidget(triggers_group)
        
        left_panel.setLayout(left_layout)
        content_splitter.addWidget(left_panel)
        
        # Right panel - Candidates and results
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Candidates list
        candidates_group = QGroupBox("World Candidates")
        candidates_layout = QVBoxLayout()
        
        self.candidates_table = QTableWidget()
        self.candidates_table.setColumnCount(5)
        self.candidates_table.setHorizontalHeaderLabels([
            "Candidate", "Office", "Country", "Platform", "Slogan"
        ])
        self.candidates_table.horizontalHeader().setStretchLastSection(True)
        candidates_layout.addWidget(self.candidates_table)
        
        candidates_group.setLayout(candidates_layout)
        right_layout.addWidget(candidates_group)
        
        # Electoral participation
        participation_group = QGroupBox("Country Electoral Participation")
        participation_layout = QVBoxLayout()
        
        self.participation_table = QTableWidget()
        self.participation_table.setColumnCount(3)
        self.participation_table.setHorizontalHeaderLabels([
            "Country", "Status", "Electoral Votes"
        ])
        self.participation_table.horizontalHeader().setStretchLastSection(True)
        participation_layout.addWidget(self.participation_table)
        
        participation_group.setLayout(participation_layout)
        right_layout.addWidget(participation_group)
        
        # Election results
        results_group = QGroupBox("Election Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(100)
        results_layout.addWidget(self.results_text)
        
        self.view_results_btn = QPushButton("📊 View Detailed Results")
        self.view_results_btn.setEnabled(False)
        results_layout.addWidget(self.view_results_btn)
        
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)
        
        right_panel.setLayout(right_layout)
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([400, 600])
        layout.addWidget(content_splitter)
        
        # Status bar
        self.status_label = QLabel("Ready - World contract governance system active")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Load initial data
        self.refresh_data()
    
    def show_population_update(self):
        """Show population update dialog"""
        
        if not self.election_manager:
            QMessageBox.warning(self, "System Error", "World election system not available.")
            return
        
        # Get current population
        rep_info = self.election_manager.get_world_representation()
        current_pop = rep_info.get('population', 8000000000) if rep_info else 8000000000
        
        dialog = WorldPopulationUpdateDialog(current_pop, self)
        
        if dialog.exec_() == QDialog.Accepted:
            new_population = dialog.get_population()
            
            success, message = self.election_manager.update_world_population(new_population)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.population_updated.emit(new_population)
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Update Failed", message)
    
    def show_candidate_registration(self):
        """Show candidate registration dialog"""
        
        if not self.election_manager:
            QMessageBox.warning(self, "System Error", "World election system not available.")
            return
        
        if not SESSION_AVAILABLE:
            QMessageBox.warning(self, "Authentication Required", "Please log in to register as candidate.")
            return
        
        dialog = WorldCandidateRegistrationDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            candidate_data = dialog.get_candidate_data()
            
            # Get current user email (placeholder)
            user_email = "current_user@example.com"  # Replace with actual session management
            
            success, message = self.election_manager.register_world_candidate(
                user_email=user_email,
                office=candidate_data['office'],
                platform_statement=candidate_data['platform_statement'],
                campaign_slogan=candidate_data['campaign_slogan'],
                country_of_origin=candidate_data['country_of_origin']
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.candidate_registered.emit("")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Registration Failed", message)
    
    def trigger_election(self):
        """Trigger world election"""
        
        if not self.election_manager:
            return
        
        # Check if election can be triggered
        can_trigger, trigger_type, message = self.election_manager.check_election_triggers()
        
        if can_trigger:
            reply = QMessageBox.question(
                self, "Trigger World Election",
                f"Trigger world contract election?\n\nReason: {message}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, msg, election_id = self.election_manager.create_world_election(trigger_type)
                
                if success:
                    QMessageBox.information(self, "Election Created", msg)
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Election Failed", msg)
        else:
            QMessageBox.information(self, "Cannot Trigger Election", message)
    
    def refresh_data(self):
        """Refresh all data displays"""
        
        if not self.election_manager:
            self.status_label.setText("World election system not available")
            return
        
        # Update world representation info
        rep_info = self.election_manager.get_world_representation()
        if rep_info and 'error' not in rep_info:
            world_text = f"""
Population: {rep_info['population']:,}
Total Representatives: {rep_info['total_representatives']}
Total Senators: {rep_info['total_senators']}

Calculation: {rep_info['calculation']}

Base Representatives: {rep_info['base_representatives']}
Additional from Population: {rep_info['additional_representatives']}
            """.strip()
            self.world_info_text.setPlainText(world_text)
        else:
            self.world_info_text.setPlainText("Error loading world representation data.")
        
        # Update election status
        election_info = self.election_manager.get_active_world_election()
        if election_info and 'error' not in election_info:
            if election_info:  # Active election exists
                election_text = f"""
Status: {election_info['status']}
Candidates: {election_info['candidate_count']}
Participating Countries: {election_info['participating_countries']}
Registration Ends: {election_info.get('registration_end', 'N/A')}
Voting Period: {election_info.get('voting_start', 'N/A')} to {election_info.get('voting_end', 'N/A')}
                """.strip()
                self.election_status_text.setPlainText(election_text)
                self.register_candidate_btn.setEnabled(True)
            else:
                self.election_status_text.setPlainText("No active world election")
                self.register_candidate_btn.setEnabled(False)
        else:
            self.election_status_text.setPlainText("Error loading election status.")
        
        # Update trigger status
        can_trigger, trigger_type, message = self.election_manager.check_election_triggers()
        self.trigger_info_text.setPlainText(f"Trigger Status: {message}")
        self.trigger_election_btn.setEnabled(can_trigger)
        
        # Update candidates table (placeholder)
        self.candidates_table.setRowCount(0)
        
        # Update participation table (placeholder)  
        self.participation_table.setRowCount(0)
        
        self.status_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")


# Test the world election UI
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create and show the world election tab
    tab = WorldElectionTab()
    tab.show()
    
    sys.exit(app.exec_())