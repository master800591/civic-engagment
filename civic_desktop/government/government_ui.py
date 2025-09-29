"""
Real-World Government Integration User Interface
Provides PyQt5 interface for managing government officials and jurisdictions
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QTableWidget, QTableWidgetItem, QLabel, QPushButton,
                           QComboBox, QLineEdit, QTextEdit, QGroupBox,
                           QFormLayout, QDialog, QDialogButtonBox, QMessageBox,
                           QHeaderView, QCheckBox, QDateEdit, QSpacerItem,
                           QSizePolicy, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple

# Import the real-world government system
try:
    from .real_world_integration import (RealWorldGovernmentManager, RealWorldGovLevel, 
                                       RealWorldPosition, VerificationStatus)
    GOVERNMENT_SYSTEM_AVAILABLE = True
except ImportError:
    print("Warning: Real-world government system not available")
    GOVERNMENT_SYSTEM_AVAILABLE = False

# Import session management
try:
    from civic_desktop.users.session import SessionManager
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    print("Warning: Session manager not available")
    SESSION_MANAGER_AVAILABLE = False


class GovernmentRegistrationDialog(QDialog):
    """Dialog for registering new government jurisdictions"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register Government Jurisdiction")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.manager = RealWorldGovernmentManager() if GOVERNMENT_SYSTEM_AVAILABLE else None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Register Real-World Government Jurisdiction")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Form
        form_group = QGroupBox("Jurisdiction Information")
        form_layout = QFormLayout()
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Springfield, Illinois, United States")
        form_layout.addRow("Name:", self.name_input)
        
        # Government Level
        self.level_combo = QComboBox()
        if GOVERNMENT_SYSTEM_AVAILABLE:
            for level in RealWorldGovLevel:
                self.level_combo.addItem(level.value.title(), level)
        form_layout.addRow("Government Level:", self.level_combo)
        
        # Country
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("e.g., United States")
        form_layout.addRow("Country:", self.country_input)
        
        # State
        self.state_input = QLineEdit()
        self.state_input.setPlaceholderText("e.g., Illinois (optional)")
        form_layout.addRow("State/Province:", self.state_input)
        
        # County
        self.county_input = QLineEdit()
        self.county_input.setPlaceholderText("e.g., Sangamon County (optional)")
        form_layout.addRow("County:", self.county_input)
        
        # Population
        self.population_input = QLineEdit()
        self.population_input.setPlaceholderText("e.g., 200000")
        form_layout.addRow("Population:", self.population_input)
        
        # Website
        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("https://example.gov")
        form_layout.addRow("Official Website:", self.website_input)
        
        # Contact Email
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("contact@example.gov")
        form_layout.addRow("Contact Email:", self.contact_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Store button box for connections
        self.button_box = button_box
    
    def setup_connections(self):
        """Setup signal connections"""
        self.button_box.accepted.connect(self.accept_registration)
        self.button_box.rejected.connect(self.reject)
    
    def accept_registration(self):
        """Process the jurisdiction registration"""
        if not GOVERNMENT_SYSTEM_AVAILABLE or not self.manager:
            QMessageBox.warning(self, "Error", "Government system not available")
            return
        
        # Validate inputs
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Jurisdiction name is required")
            return
        
        country = self.country_input.text().strip()
        if not country:
            QMessageBox.warning(self, "Validation Error", "Country is required")
            return
        
        # Get form data
        level = self.level_combo.currentData()
        state = self.state_input.text().strip() or None
        county = self.county_input.text().strip() or None
        website = self.website_input.text().strip() or None
        contact = self.contact_input.text().strip() or None
        
        # Parse population
        population = None
        population_text = self.population_input.text().strip()
        if population_text:
            try:
                population = int(population_text.replace(',', ''))
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Invalid population number")
                return
        
        # Register jurisdiction
        try:
            success, message, jurisdiction_id = self.manager.register_jurisdiction(
                name=name,
                level=level,
                country=country,
                state=state,
                county=county,
                population=population,
                website=website,
                contact_email=contact
            )
            
            if success:
                QMessageBox.information(self, "Success", f"{message}\nJurisdiction ID: {jurisdiction_id}")
                self.accept()
            else:
                QMessageBox.warning(self, "Registration Failed", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {str(e)}")


class OfficialRegistrationDialog(QDialog):
    """Dialog for registering government officials"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register Government Official")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        self.manager = RealWorldGovernmentManager() if GOVERNMENT_SYSTEM_AVAILABLE else None
        
        self.setup_ui()
        self.setup_connections()
        self.load_jurisdictions()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Register Real-World Government Official")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Form
        form_group = QGroupBox("Official Information")
        form_layout = QFormLayout()
        
        # User Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("official@government.gov")
        form_layout.addRow("User Email:", self.email_input)
        
        # Jurisdiction
        self.jurisdiction_combo = QComboBox()
        self.jurisdiction_combo.setEditable(False)
        form_layout.addRow("Jurisdiction:", self.jurisdiction_combo)
        
        # Position
        self.position_combo = QComboBox()
        if GOVERNMENT_SYSTEM_AVAILABLE:
            for position in RealWorldPosition:
                self.position_combo.addItem(position.value.replace('_', ' ').title(), position)
        form_layout.addRow("Government Position:", self.position_combo)
        
        # Position Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., Mayor of Springfield, Illinois")
        form_layout.addRow("Official Title:", self.title_input)
        
        # Term Start
        self.term_start = QDateEdit()
        self.term_start.setDate(QDate.currentDate())
        self.term_start.setCalendarPopup(True)
        form_layout.addRow("Term Start Date:", self.term_start)
        
        # Term End
        self.term_end = QDateEdit()
        self.term_end.setDate(QDate.currentDate().addYears(4))
        self.term_end.setCalendarPopup(True)
        form_layout.addRow("Term End Date:", self.term_end)
        
        # Verification Documents
        self.documents_input = QTextEdit()
        self.documents_input.setPlaceholderText("List verification documents (one per line):\n- Oath of Office\n- Election Certificate\n- Government ID")
        self.documents_input.setMaximumHeight(80)
        form_layout.addRow("Verification Documents:", self.documents_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Instructions
        instructions = QLabel("Note: Registration will be submitted for verification by system administrators.")
        instructions.setStyleSheet("color: #666; font-style: italic;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Store button box for connections
        self.button_box = button_box
    
    def setup_connections(self):
        """Setup signal connections"""
        self.button_box.accepted.connect(self.accept_registration)
        self.button_box.rejected.connect(self.reject)
    
    def load_jurisdictions(self):
        """Load available jurisdictions"""
        if not GOVERNMENT_SYSTEM_AVAILABLE or not self.manager:
            return
        
        try:
            jurisdictions = self.manager.search_jurisdictions()
            
            self.jurisdiction_combo.clear()
            self.jurisdiction_combo.addItem("Select Jurisdiction...", None)
            
            for jurisdiction in jurisdictions:
                display_name = f"{jurisdiction['name']} ({jurisdiction['level'].title()})"
                self.jurisdiction_combo.addItem(display_name, jurisdiction['jurisdiction_id'])
                
        except Exception as e:
            print(f"Error loading jurisdictions: {e}")
    
    def accept_registration(self):
        """Process the official registration"""
        if not GOVERNMENT_SYSTEM_AVAILABLE or not self.manager:
            QMessageBox.warning(self, "Error", "Government system not available")
            return
        
        # Validate inputs
        email = self.email_input.text().strip()
        if not email or '@' not in email:
            QMessageBox.warning(self, "Validation Error", "Valid email is required")
            return
        
        jurisdiction_id = self.jurisdiction_combo.currentData()
        if not jurisdiction_id:
            QMessageBox.warning(self, "Validation Error", "Please select a jurisdiction")
            return
        
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Official title is required")
            return
        
        # Get form data
        position = self.position_combo.currentData()
        term_start = self.term_start.date().toString("yyyy-MM-dd")
        term_end = self.term_end.date().toString("yyyy-MM-dd")
        
        # Parse verification documents
        documents_text = self.documents_input.toPlainText().strip()
        documents = []
        if documents_text:
            documents = [line.strip() for line in documents_text.split('\n') if line.strip()]
        
        # Register official
        try:
            success, message, official_id = self.manager.register_government_official(
                user_email=email,
                jurisdiction_id=jurisdiction_id,
                position=position,
                position_title=title,
                term_start=term_start,
                term_end=term_end,
                verification_documents=documents
            )
            
            if success:
                QMessageBox.information(self, "Success", f"{message}\nOfficial ID: {official_id}")
                self.accept()
            else:
                QMessageBox.warning(self, "Registration Failed", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {str(e)}")


class RealWorldGovernmentTab(QWidget):
    """Main tab for real-world government integration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.manager = RealWorldGovernmentManager() if GOVERNMENT_SYSTEM_AVAILABLE else None
        
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
        
        title = QLabel("🏛️ Real-World Government Integration")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Add buttons
        self.register_jurisdiction_btn = QPushButton("Register Jurisdiction")
        self.register_jurisdiction_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; }")
        header_layout.addWidget(self.register_jurisdiction_btn)
        
        self.register_official_btn = QPushButton("Register Official")
        self.register_official_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px 16px; border: none; border-radius: 4px; }")
        header_layout.addWidget(self.register_official_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 8px 16px; border: none; border-radius: 4px; }")
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Statistics tab
        self.stats_tab = self.create_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "📊 Statistics")
        
        # Jurisdictions tab
        self.jurisdictions_tab = self.create_jurisdictions_tab()
        self.tab_widget.addTab(self.jurisdictions_tab, "📍 Jurisdictions")
        
        # Officials tab
        self.officials_tab = self.create_officials_tab()
        self.tab_widget.addTab(self.officials_tab, "👥 Government Officials")
        
        # Verifications tab
        self.verifications_tab = self.create_verifications_tab()
        self.tab_widget.addTab(self.verifications_tab, "⏳ Pending Verifications")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Government integration system ready")
        self.status_label.setStyleSheet("color: #666; padding: 8px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def create_stats_tab(self) -> QWidget:
        """Create the statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        # Create stats cards
        self.total_jurisdictions_card = self.create_stat_card("Total Jurisdictions", "0", "#4CAF50")
        self.total_officials_card = self.create_stat_card("Total Officials", "0", "#2196F3")
        self.verified_officials_card = self.create_stat_card("Verified Officials", "0", "#FF9800")
        self.pending_verifications_card = self.create_stat_card("Pending Verifications", "0", "#F44336")
        
        stats_layout.addWidget(self.total_jurisdictions_card)
        stats_layout.addWidget(self.total_officials_card)
        stats_layout.addWidget(self.verified_officials_card)
        stats_layout.addWidget(self.pending_verifications_card)
        
        layout.addLayout(stats_layout)
        
        # Detailed statistics
        details_group = QGroupBox("Detailed Statistics")
        details_layout = QVBoxLayout()
        
        self.stats_details = QLabel("Loading statistics...")
        self.stats_details.setWordWrap(True)
        self.stats_details.setStyleSheet("padding: 16px; background-color: #f5f5f5; border-radius: 4px;")
        details_layout.addWidget(self.stats_details)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
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
                padding: 16px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        frame.setLayout(layout)
        
        # Store value label for updates
        frame.value_label = value_label
        
        return frame
    
    def create_jurisdictions_tab(self) -> QWidget:
        """Create the jurisdictions tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.jurisdiction_search = QLineEdit()
        self.jurisdiction_search.setPlaceholderText("Search jurisdictions...")
        search_layout.addWidget(self.jurisdiction_search)
        
        layout.addLayout(search_layout)
        
        # Jurisdictions table
        self.jurisdictions_table = QTableWidget()
        self.jurisdictions_table.setColumnCount(6)
        self.jurisdictions_table.setHorizontalHeaderLabels([
            "Name", "Level", "Country", "State", "Population", "Status"
        ])
        self.jurisdictions_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.jurisdictions_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_officials_tab(self) -> QWidget:
        """Create the officials tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Search and filter bar
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Search:"))
        self.official_search = QLineEdit()
        self.official_search.setPlaceholderText("Search officials...")
        filter_layout.addWidget(self.official_search)
        
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses", None)
        if GOVERNMENT_SYSTEM_AVAILABLE:
            for status in VerificationStatus:
                self.status_filter.addItem(status.value.title(), status.value)
        
        filter_layout.addWidget(self.status_filter)
        
        layout.addLayout(filter_layout)
        
        # Officials table
        self.officials_table = QTableWidget()
        self.officials_table.setColumnCount(7)
        self.officials_table.setHorizontalHeaderLabels([
            "Email", "Position", "Title", "Jurisdiction", "Term Start", "Status", "Actions"
        ])
        self.officials_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.officials_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_verifications_tab(self) -> QWidget:
        """Create the pending verifications tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Review and verify government officials. Only verified officials will receive contract roles."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 8px; background-color: #e3f2fd; border-radius: 4px;")
        layout.addWidget(instructions)
        
        # Pending verifications table
        self.verifications_table = QTableWidget()
        self.verifications_table.setColumnCount(6)
        self.verifications_table.setHorizontalHeaderLabels([
            "Official", "Position", "Jurisdiction", "Documents", "Registered", "Actions"
        ])
        self.verifications_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.verifications_table)
        
        widget.setLayout(layout)
        return widget
    
    def setup_connections(self):
        """Setup signal connections"""
        self.register_jurisdiction_btn.clicked.connect(self.show_jurisdiction_dialog)
        self.register_official_btn.clicked.connect(self.show_official_dialog)
        self.refresh_btn.clicked.connect(self.load_data)
        
        # Search functionality
        self.jurisdiction_search.textChanged.connect(self.filter_jurisdictions)
        self.official_search.textChanged.connect(self.filter_officials)
        self.status_filter.currentTextChanged.connect(self.filter_officials)
    
    def show_jurisdiction_dialog(self):
        """Show the jurisdiction registration dialog"""
        dialog = GovernmentRegistrationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()
    
    def show_official_dialog(self):
        """Show the official registration dialog"""
        dialog = OfficialRegistrationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()
    
    def load_data(self):
        """Load and display government data"""
        if not GOVERNMENT_SYSTEM_AVAILABLE or not self.manager:
            self.status_label.setText("Government system not available")
            return
        
        try:
            # Load statistics
            stats = self.manager.get_government_integration_stats()
            self.update_statistics(stats)
            
            # Load jurisdictions
            jurisdictions = self.manager.search_jurisdictions()
            self.update_jurisdictions_table(jurisdictions)
            
            # Load officials
            officials_data = self.manager._load_json(self.manager.officials_db)
            officials = list(officials_data.get('officials', {}).values())
            self.update_officials_table(officials)
            
            # Load pending verifications
            pending = self.manager.get_pending_verifications()
            self.update_verifications_table(pending)
            
            self.status_label.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            self.status_label.setText(f"Error loading data: {str(e)}")
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Update the statistics display"""
        try:
            # Update stat cards
            self.total_jurisdictions_card.value_label.setText(str(stats.get('total_jurisdictions', 0)))
            self.total_officials_card.value_label.setText(str(stats.get('total_officials_registered', 0)))
            
            officials_by_status = stats.get('officials_by_status', {})
            self.verified_officials_card.value_label.setText(str(officials_by_status.get('verified', 0)))
            self.pending_verifications_card.value_label.setText(str(stats.get('pending_verifications', 0)))
            
            # Update detailed statistics
            details_text = f"""
Government Integration Statistics:

Jurisdictions by Level:
"""
            jurisdictions_by_level = stats.get('jurisdictions_by_level', {})
            for level, count in jurisdictions_by_level.items():
                details_text += f"• {level.title()}: {count}\n"
            
            details_text += f"""
Officials by Status:
"""
            for status, count in officials_by_status.items():
                details_text += f"• {status.title()}: {count}\n"
            
            details_text += f"""
Officials by Position:
"""
            officials_by_position = stats.get('officials_by_position', {})
            for position, count in officials_by_position.items():
                details_text += f"• {position.replace('_', ' ').title()}: {count}\n"
            
            self.stats_details.setText(details_text.strip())
            
        except Exception as e:
            self.stats_details.setText(f"Error displaying statistics: {str(e)}")
    
    def update_jurisdictions_table(self, jurisdictions: List[Dict[str, Any]]):
        """Update the jurisdictions table"""
        try:
            self.jurisdictions_table.setRowCount(len(jurisdictions))
            
            for row, jurisdiction in enumerate(jurisdictions):
                self.jurisdictions_table.setItem(row, 0, QTableWidgetItem(jurisdiction.get('name', '')))
                self.jurisdictions_table.setItem(row, 1, QTableWidgetItem(jurisdiction.get('level', '').title()))
                self.jurisdictions_table.setItem(row, 2, QTableWidgetItem(jurisdiction.get('country', '')))
                self.jurisdictions_table.setItem(row, 3, QTableWidgetItem(jurisdiction.get('state', '')))
                
                population = jurisdiction.get('population')
                pop_text = f"{population:,}" if population else ""
                self.jurisdictions_table.setItem(row, 4, QTableWidgetItem(pop_text))
                
                status = "✅ Verified" if jurisdiction.get('verified') else "⏳ Pending"
                self.jurisdictions_table.setItem(row, 5, QTableWidgetItem(status))
            
            self.jurisdictions_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error updating jurisdictions table: {e}")
    
    def update_officials_table(self, officials: List[Dict[str, Any]]):
        """Update the officials table"""
        try:
            self.officials_table.setRowCount(len(officials))
            
            for row, official in enumerate(officials):
                self.officials_table.setItem(row, 0, QTableWidgetItem(official.get('user_email', '')))
                self.officials_table.setItem(row, 1, QTableWidgetItem(official.get('position', '').replace('_', ' ').title()))
                self.officials_table.setItem(row, 2, QTableWidgetItem(official.get('position_title', '')))
                self.officials_table.setItem(row, 3, QTableWidgetItem(official.get('jurisdiction_id', '')))
                self.officials_table.setItem(row, 4, QTableWidgetItem(official.get('term_start', '')))
                
                status = official.get('verification_status', 'pending')
                status_icons = {
                    'pending': '⏳',
                    'verified': '✅',
                    'rejected': '❌',
                    'expired': '⌛'
                }
                status_text = f"{status_icons.get(status, '?')} {status.title()}"
                self.officials_table.setItem(row, 5, QTableWidgetItem(status_text))
                
                # Actions column (placeholder for now)
                self.officials_table.setItem(row, 6, QTableWidgetItem("View Details"))
            
            self.officials_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error updating officials table: {e}")
    
    def update_verifications_table(self, verifications: List[Dict[str, Any]]):
        """Update the pending verifications table"""
        try:
            self.verifications_table.setRowCount(len(verifications))
            
            for row, verification in enumerate(verifications):
                self.verifications_table.setItem(row, 0, QTableWidgetItem(verification.get('user_email', '')))
                self.verifications_table.setItem(row, 1, QTableWidgetItem(verification.get('position', '').replace('_', ' ').title()))
                self.verifications_table.setItem(row, 2, QTableWidgetItem(verification.get('jurisdiction_id', '')))
                
                docs_count = len(verification.get('verification_documents', []))
                self.verifications_table.setItem(row, 3, QTableWidgetItem(f"{docs_count} documents"))
                
                # Parse registration date
                created_date = verification.get('created_date', '')
                if created_date:
                    try:
                        date_obj = datetime.fromisoformat(created_date.replace('Z', ''))
                        date_text = date_obj.strftime('%Y-%m-%d')
                    except:
                        date_text = created_date
                else:
                    date_text = "Unknown"
                self.verifications_table.setItem(row, 4, QTableWidgetItem(date_text))
                
                # Actions (simplified for now)
                action_text = "Verify | Reject"
                self.verifications_table.setItem(row, 5, QTableWidgetItem(action_text))
            
            self.verifications_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error updating verifications table: {e}")
    
    def filter_jurisdictions(self):
        """Filter jurisdictions based on search text"""
        search_text = self.jurisdiction_search.text().lower()
        
        for row in range(self.jurisdictions_table.rowCount()):
            show_row = False
            for col in range(self.jurisdictions_table.columnCount()):
                item = self.jurisdictions_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            
            self.jurisdictions_table.setRowHidden(row, not show_row)
    
    def filter_officials(self):
        """Filter officials based on search text and status"""
        search_text = self.official_search.text().lower()
        status_filter = self.status_filter.currentData()
        
        for row in range(self.officials_table.rowCount()):
            show_row = True
            
            # Apply search filter
            if search_text:
                search_match = False
                for col in range(self.officials_table.columnCount()):
                    item = self.officials_table.item(row, col)
                    if item and search_text in item.text().lower():
                        search_match = True
                        break
                if not search_match:
                    show_row = False
            
            # Apply status filter
            if status_filter and show_row:
                status_item = self.officials_table.item(row, 5)
                if status_item and status_filter not in status_item.text().lower():
                    show_row = False
            
            self.officials_table.setRowHidden(row, not show_row)


# Demo function for testing
def demo_government_ui():
    """Demonstrate the government integration UI"""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create and show the main tab
    tab = RealWorldGovernmentTab()
    tab.show()
    
    # Run the application
    sys.exit(app.exec_())