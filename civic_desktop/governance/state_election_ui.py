"""
STATE CONTRACT ELECTION USER INTERFACE - Electoral College System Management
PyQt5 interface for managing state-level contract governance elections with city electoral college
Handles Contract Senator/Representative elections for state-level platform governance
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
    from civic_desktop.governance.state_elections import (
        StateElectionManager, StateOffice, StateElectionTrigger, 
        StateElectionStatus, StateElectionConfig
    )
    STATE_ELECTIONS_AVAILABLE = True
except ImportError:
    STATE_ELECTIONS_AVAILABLE = False

try:
    from civic_desktop.users.session import SessionManager
    SESSION_AVAILABLE = True
except ImportError:
    SESSION_AVAILABLE = False


class StateRegistrationDialog(QDialog):
    """Dialog for registering new states in the contract governance electoral system"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("State Contract Elections")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Form for state registration
        form_layout = QFormLayout()
        
        self.state_name_input = QLineEdit()
        self.state_name_input.setPlaceholderText("Enter state name...")
        form_layout.addRow("State Name:", self.state_name_input)
        
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("Enter country...")
        form_layout.addRow("Country:", self.country_input)
        
        self.population_input = QSpinBox()
        self.population_input.setRange(1000, 100000000)
        self.population_input.setValue(1000000)
        self.population_input.setSuffix(" people")
        form_layout.addRow("Total Population:", self.population_input)
        
        # Electoral thresholds
        threshold_group = QGroupBox("Election Thresholds")
        threshold_layout = QFormLayout(threshold_group)
        
        self.initial_threshold_input = QDoubleSpinBox()
        self.initial_threshold_input.setRange(0.01, 1.0)
        self.initial_threshold_input.setValue(0.01)
        self.initial_threshold_input.setSuffix("%")
        self.initial_threshold_input.setDecimals(2)
        threshold_layout.addRow("Initial Election (% of cities):", self.initial_threshold_input)
        
        self.expansion_threshold_input = QDoubleSpinBox()
        self.expansion_threshold_input.setRange(0.01, 1.0)
        self.expansion_threshold_input.setValue(0.50)
        self.expansion_threshold_input.setSuffix("%")
        self.expansion_threshold_input.setDecimals(2)
        threshold_layout.addRow("Expansion Election (% of cities):", self.expansion_threshold_input)
        
        layout.addLayout(form_layout)
        layout.addWidget(threshold_group)
        
        # Info display
        info_label = QLabel(
            "• Representatives: 2 minimum + 1 per 500,000 population\\n"
            "• Senators: Always 2 per state\\n"
            "• Terms: 1 year, maximum 4 terms, non-consecutive\\n"
            "• Candidates must be current/former city officials"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10pt; background: #f0f0f0; padding: 8px; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_state_data(self) -> Dict[str, Any]:
        """Get state registration data from form"""
        return {
            'state_name': self.state_name_input.text().strip(),
            'country': self.country_input.text().strip(),
            'total_population_estimate': self.population_input.value(),
            'initial_threshold_percent': self.initial_threshold_input.value() / 100,
            'expansion_threshold_percent': self.expansion_threshold_input.value() / 100
        }


class StateCandidateRegistrationDialog(QDialog):
    """Dialog for registering candidates for state contract governance office"""
    
    def __init__(self, state_id: str, state_name: str, parent=None):
        super().__init__(parent)
        self.state_id = state_id
        self.state_name = state_name
        
        self.setWindowTitle(f"Register State Candidate - {state_name}")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(f"Register as Candidate - {state_name}")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header_label)
        
        # Form
        form_layout = QFormLayout()
        
        self.office_combo = QComboBox()
        self.office_combo.addItem("Contract State Representative", StateOffice.STATE_REPRESENTATIVE.value)
        self.office_combo.addItem("Contract State Senator", StateOffice.STATE_SENATOR.value)
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
        eligibility_layout = QVBoxLayout(eligibility_group)
        
        eligibility_text = QLabel(
            "✓ Must be or have been a city representative or senator in this state\\n"
            "✓ Cannot exceed 4 total terms for this office\\n"
            "✓ Cannot serve consecutive terms\\n"
            "✓ Electoral college voting by cities determines winners"
        )
        eligibility_text.setWordWrap(True)
        eligibility_layout.addWidget(eligibility_text)
        
        layout.addWidget(eligibility_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_candidate_data(self) -> Dict[str, Any]:
        """Get candidate registration data from form"""
        return {
            'office': StateOffice(self.office_combo.currentData()),
            'platform_statement': self.platform_input.toPlainText().strip(),
            'campaign_slogan': self.slogan_input.text().strip()
        }


class StateElectionWidget(QWidget):
    """Main widget for state election management"""
    
    def __init__(self):
        super().__init__()
        self.manager = None
        self.current_user = None
        
        if STATE_ELECTIONS_AVAILABLE:
            self.manager = StateElectionManager()
        
        if SESSION_AVAILABLE:
            self.current_user = SessionManager.get_current_user()
        
        self.setup_ui()
        self.setup_refresh_timer()
        self.refresh_data()
    
    def setup_ui(self):
        """Set up the user interface"""
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🏛️ STATE ELECTIONS - Electoral College System")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Action buttons
        self.register_state_btn = QPushButton("📍 Register State")
        self.register_state_btn.clicked.connect(self.register_new_state)
        header_layout.addWidget(self.register_state_btn)
        
        self.register_candidate_btn = QPushButton("🏛️ Register as Candidate")
        self.register_candidate_btn.clicked.connect(self.register_as_candidate)
        header_layout.addWidget(self.register_candidate_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Main content with tabs
        self.tab_widget = QTabWidget()
        
        # States overview tab
        self.states_tab = self.create_states_tab()
        self.tab_widget.addTab(self.states_tab, "🗺️ States")
        
        # Elections tab
        self.elections_tab = self.create_elections_tab()
        self.tab_widget.addTab(self.elections_tab, "🗳️ Elections")
        
        # Candidates tab
        self.candidates_tab = self.create_candidates_tab()
        self.tab_widget.addTab(self.candidates_tab, "👥 Candidates")
        
        # Electoral college tab
        self.electoral_tab = self.create_electoral_tab()
        self.tab_widget.addTab(self.electoral_tab, "🏛️ Electoral College")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready - State electoral system initialized")
        self.status_label.setStyleSheet("padding: 4px; background: #f0f0f0; border-radius: 2px;")
        layout.addWidget(self.status_label)
    
    def create_states_tab(self) -> QWidget:
        """Create states overview tab"""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # States table
        self.states_table = QTableWidget()
        self.states_table.setColumnCount(6)
        self.states_table.setHorizontalHeaderLabels([
            "State Name", "Population", "Representatives", "Senators", 
            "Cities w/ Representation", "Election Status"
        ])
        self.states_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(QLabel("Registered States:"))
        layout.addWidget(self.states_table)
        
        return widget
    
    def create_elections_tab(self) -> QWidget:
        """Create elections management tab"""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Elections table
        self.elections_table = QTableWidget()
        self.elections_table.setColumnCount(7)
        self.elections_table.setHorizontalHeaderLabels([
            "State", "Election Type", "Offices", "Status", 
            "Campaign Period", "Voting Period", "Electoral Votes"
        ])
        self.elections_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(QLabel("State Elections:"))
        layout.addWidget(self.elections_table)
        
        return widget
    
    def create_candidates_tab(self) -> QWidget:
        """Create candidates management tab"""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Candidates table
        self.candidates_table = QTableWidget()
        self.candidates_table.setColumnCount(6)
        self.candidates_table.setHorizontalHeaderLabels([
            "Name", "State", "Office", "City Experience", 
            "Electoral Votes", "Status"
        ])
        self.candidates_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(QLabel("State Candidates:"))
        layout.addWidget(self.candidates_table)
        
        return widget
    
    def create_electoral_tab(self) -> QWidget:
        """Create electoral college tab"""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Electoral college composition
        self.electoral_tree = QTreeWidget()
        self.electoral_tree.setHeaderLabels(["State/City", "Electoral Votes", "Representation Status"])
        
        layout.addWidget(QLabel("Electoral College Composition:"))
        layout.addWidget(self.electoral_tree)
        
        return widget
    
    def setup_refresh_timer(self):
        """Set up automatic refresh timer"""
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def refresh_data(self):
        """Refresh all data displays"""
        
        if not self.manager:
            return
        
        try:
            self.refresh_states_table()
            self.refresh_elections_table()
            self.refresh_candidates_table()
            self.refresh_electoral_tree()
            
            self.status_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_label.setText(f"Error refreshing data: {e}")
    
    def refresh_states_table(self):
        """Refresh states table"""
        
        try:
            # This would load actual state data from the manager
            states_data = []  # Placeholder
            
            self.states_table.setRowCount(len(states_data))
            
            for row, state in enumerate(states_data):
                self.states_table.setItem(row, 0, QTableWidgetItem(state.get('state_name', '')))
                self.states_table.setItem(row, 1, QTableWidgetItem(f"{state.get('population', 0):,}"))
                self.states_table.setItem(row, 2, QTableWidgetItem(str(state.get('representatives', 0))))
                self.states_table.setItem(row, 3, QTableWidgetItem(str(state.get('senators', 0))))
                self.states_table.setItem(row, 4, QTableWidgetItem(str(state.get('cities_with_rep', 0))))
                self.states_table.setItem(row, 5, QTableWidgetItem(state.get('election_status', 'No elections')))
            
        except Exception as e:
            print(f"Error refreshing states table: {e}")
    
    def refresh_elections_table(self):
        """Refresh elections table"""
        
        try:
            # This would load actual election data from the manager
            elections_data = []  # Placeholder
            
            self.elections_table.setRowCount(len(elections_data))
            
        except Exception as e:
            print(f"Error refreshing elections table: {e}")
    
    def refresh_candidates_table(self):
        """Refresh candidates table"""
        
        try:
            # This would load actual candidate data from the manager
            candidates_data = []  # Placeholder
            
            self.candidates_table.setRowCount(len(candidates_data))
            
        except Exception as e:
            print(f"Error refreshing candidates table: {e}")
    
    def refresh_electoral_tree(self):
        """Refresh electoral college tree"""
        
        try:
            self.electoral_tree.clear()
            
            # This would build the actual electoral college tree
            # For now, show placeholder structure
            root = QTreeWidgetItem(self.electoral_tree)
            root.setText(0, "Electoral College System")
            root.setText(1, "Active")
            root.setText(2, "State-level elections via city representation")
            
        except Exception as e:
            print(f"Error refreshing electoral tree: {e}")
    
    def register_new_state(self):
        """Open state registration dialog"""
        
        if not self.manager:
            QMessageBox.warning(self, "Error", "State election manager not available")
            return
        
        dialog = StateRegistrationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            state_data = dialog.get_state_data()
            
            if not state_data['state_name'] or not state_data['country']:
                QMessageBox.warning(self, "Error", "State name and country are required")
                return
            
            success, message, state_id = self.manager.register_state(**state_data)
            
            if success:
                QMessageBox.information(self, "Success", f"State registered successfully!\\n{message}")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Registration Failed", message)
    
    def register_as_candidate(self):
        """Open candidate registration dialog"""
        
        if not self.manager:
            QMessageBox.warning(self, "Error", "State election manager not available")
            return
        
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please log in to register as candidate")
            return
        
        # For demo, use a placeholder state
        # In real implementation, user would select from available states
        state_id = "demo_state"
        state_name = "Demo State"
        
        dialog = StateCandidateRegistrationDialog(state_id, state_name, self)
        if dialog.exec_() == QDialog.Accepted:
            candidate_data = dialog.get_candidate_data()
            
            success, message, candidate_id = self.manager.register_state_candidate(
                candidate_email=self.current_user['email'],
                state_id=state_id,
                **candidate_data
            )
            
            if success:
                QMessageBox.information(self, "Success", f"Candidate registration successful!\\n{message}")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Registration Failed", message)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    widget = StateElectionWidget()
    widget.show()
    sys.exit(app.exec_())