# contracts/contract_ui.py
# Contract User Interface Components
"""
PyQt5 UI components for contract acceptance and viewing.
Implements hierarchical contract system with proper precedence display.
"""

import sys
import os
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QTextEdit, QCheckBox, QFrame, QMessageBox,
    QDialog, QTabWidget, QProgressBar, QSplitter, QGroupBox,
    QListWidget, QListWidgetItem, QTextBrowser, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

# Import contract system
from .contract_terms import (
    ContractManager, PlatformContract, ContractSection, 
    ContractType, ContractStatus, contract_manager
)
from .contract_types import create_default_contracts


class ContractSectionWidget(QFrame):
    """Widget to display a single contract section with acceptance checkbox"""
    
    section_accepted = pyqtSignal(str, bool)  # section_id, accepted
    
    def __init__(self, section: ContractSection, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.section = section
        self.accepted = False
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Setup the UI for contract section display"""
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        
        layout = QVBoxLayout(self)
        
        # Section header
        header_layout = QHBoxLayout()
        
        # Title and precedence
        title_label = QLabel(f"{self.section.title} (Priority: {self.section.precedence})")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Acceptance checkbox
        if self.section.requires_agreement:
            self.accept_checkbox = QCheckBox("I Accept This Section")
            self.accept_checkbox.stateChanged.connect(self.on_acceptance_changed)
            header_layout.addWidget(self.accept_checkbox)
        
        layout.addLayout(header_layout)
        
        # Intent, Reason, Objective
        info_layout = QVBoxLayout()
        
        intent_label = QLabel(f"<b>Intent:</b> {self.section.intent}")
        intent_label.setWordWrap(True)
        info_layout.addWidget(intent_label)
        
        reason_label = QLabel(f"<b>Reason:</b> {self.section.reason}")
        reason_label.setWordWrap(True)
        info_layout.addWidget(reason_label)
        
        objective_label = QLabel(f"<b>Objective:</b> {self.section.objective}")
        objective_label.setWordWrap(True)
        info_layout.addWidget(objective_label)
        
        layout.addLayout(info_layout)
        
        # Content text
        content_browser = QTextBrowser()
        content_browser.setPlainText(self.section.content)
        content_browser.setMaximumHeight(200)
        layout.addWidget(content_browser)
        
        # Effective date
        date_label = QLabel(f"<i>Effective: {self.section.effective_date}</i>")
        layout.addWidget(date_label)
    
    def on_acceptance_changed(self, state: int) -> None:
        """Handle acceptance checkbox state change"""
        self.accepted = state == Qt.Checked
        self.section_accepted.emit(self.section.section_id, self.accepted)
    
    def set_accepted(self, accepted: bool) -> None:
        """Set acceptance state programmatically"""
        self.accepted = accepted
        if hasattr(self, 'accept_checkbox'):
            self.accept_checkbox.setChecked(accepted)


class ContractViewer(QDialog):
    """Dialog to view a complete contract with all sections"""
    
    def __init__(self, contract: PlatformContract, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.contract = contract
        self.setup_ui()
        self.resize(800, 600)
    
    def setup_ui(self) -> None:
        """Setup the contract viewer UI"""
        self.setWindowTitle(f"Contract Viewer - {self.contract.contract_type.value.title()}")
        
        layout = QVBoxLayout(self)
        
        # Contract header
        header_group = QGroupBox("Contract Information")
        header_layout = QVBoxLayout(header_group)
        
        title_label = QLabel(f"<h2>{self.contract.contract_type.value.title()} Contract</h2>")
        header_layout.addWidget(title_label)
        
        info_label = QLabel(f"""
        <b>Jurisdiction:</b> {self.contract.jurisdiction}<br>
        <b>Version:</b> {self.contract.version}<br>
        <b>Status:</b> {self.contract.status.value}<br>
        <b>Precedence Level:</b> {self.contract.precedence_level}<br>
        <b>Created:</b> {self.contract.created_date}<br>
        <b>Effective:</b> {self.contract.effective_date}
        """)
        header_layout.addWidget(info_label)
        
        layout.addWidget(header_group)
        
        # Sections
        sections_group = QGroupBox("Contract Sections")
        sections_layout = QVBoxLayout(sections_group)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        for section in self.contract.get_all_sections():
            section_widget = ContractSectionWidget(section)
            scroll_layout.addWidget(section_widget)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        sections_layout.addWidget(scroll_area)
        
        layout.addWidget(sections_group)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)


class ContractAcceptanceWidget(QWidget):
    """
    Main widget for contract acceptance during user registration
    Handles hierarchical contract system with proper precedence
    """
    
    all_contracts_accepted = pyqtSignal()  # Emitted when all required contracts accepted
    acceptance_changed = pyqtSignal(bool)  # Emitted when acceptance status changes
    
    def __init__(self, user_location: Dict[str, str], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user_location = user_location
        self.contract_manager = contract_manager
        self.applicable_contracts: List[PlatformContract] = []
        self.section_acceptances: Dict[str, bool] = {}
        self.contract_acceptances: Dict[str, bool] = {}
        
        self.setup_ui()
        self.load_applicable_contracts()
    
    def setup_ui(self):
        """Setup the contract acceptance UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("<h2>Contract Acceptance Required</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Explanation
        explanation_label = QLabel("""
        <p>Before participating in the Civic Engagement Platform, you must review and accept 
        the applicable governance contracts for your location. These contracts establish the 
        rules and principles that govern platform participation.</p>
        
        <p><b>Contract Hierarchy:</b> Master (Constitutional) contracts override all others, 
        followed by Country, State, and City contracts in that order.</p>
        """)
        explanation_label.setWordWrap(True)
        layout.addWidget(explanation_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Contract tabs
        self.contract_tabs = QTabWidget()
        layout.addWidget(self.contract_tabs)
        
        # Acceptance summary
        self.summary_group = QGroupBox("Acceptance Summary")
        self.summary_layout = QVBoxLayout(self.summary_group)
        self.summary_label = QLabel("No contracts loaded.")
        self.summary_layout.addWidget(self.summary_label)
        layout.addWidget(self.summary_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.view_hierarchy_btn = QPushButton("View Contract Hierarchy")
        self.view_hierarchy_btn.clicked.connect(self.show_contract_hierarchy)
        button_layout.addWidget(self.view_hierarchy_btn)
        
        button_layout.addStretch()
        
        self.accept_all_btn = QPushButton("Accept All Required Contracts")
        self.accept_all_btn.clicked.connect(self.accept_all_contracts)
        self.accept_all_btn.setEnabled(False)
        button_layout.addWidget(self.accept_all_btn)
        
        layout.addLayout(button_layout)
    
    def load_applicable_contracts(self):
        """Load contracts applicable to user's location"""
        # Initialize default contracts if none exist
        if not self.contract_manager.contracts:
            default_contracts = create_default_contracts()
            for contract in default_contracts.values():
                self.contract_manager.add_contract(contract)
        
        # Get applicable contracts
        self.applicable_contracts = self.contract_manager.get_applicable_contracts(self.user_location)
        
        if not self.applicable_contracts:
            self.summary_label.setText("No applicable contracts found for your location.")
            return
        
        # Create tabs for each contract
        self.contract_tabs.clear()
        for contract in self.applicable_contracts:
            self.create_contract_tab(contract)
        
        self.update_summary()
    
    def create_contract_tab(self, contract: PlatformContract):
        """Create a tab for a single contract"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        
        # Contract info
        info_label = QLabel(f"""
        <h3>{contract.contract_type.value.title()} Contract</h3>
        <b>Jurisdiction:</b> {contract.jurisdiction}<br>
        <b>Precedence Level:</b> {contract.precedence_level} (lower = higher priority)<br>
        <b>Status:</b> {contract.status.value}<br>
        <b>Version:</b> {contract.version}
        """)
        tab_layout.addWidget(info_label)
        
        # Sections
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        contract_accepted = True
        for section in contract.get_all_sections():
            section_widget = ContractSectionWidget(section)
            section_widget.section_accepted.connect(self.on_section_acceptance_changed)
            scroll_layout.addWidget(section_widget)
            
            # Track if all sections are accepted
            if section.requires_agreement:
                contract_accepted = False
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        tab_layout.addWidget(scroll_area)
        
        # Contract acceptance checkbox
        if contract.acceptance_required:
            contract_checkbox = QCheckBox(f"I accept the {contract.contract_type.value.title()} Contract")
            contract_checkbox.stateChanged.connect(
                lambda state, cid=contract.contract_id: self.on_contract_acceptance_changed(cid, state == Qt.Checked)
            )
            tab_layout.addWidget(contract_checkbox)
            
            self.contract_acceptances[contract.contract_id] = False
        
        # Add tab
        tab_name = f"{contract.contract_type.value.title()}"
        if contract.jurisdiction:
            tab_name += f" ({contract.jurisdiction})"
        
        self.contract_tabs.addTab(tab_widget, tab_name)
    
    def on_section_acceptance_changed(self, section_id: str, accepted: bool):
        """Handle section acceptance change"""
        self.section_acceptances[section_id] = accepted
        self.update_summary()
    
    def on_contract_acceptance_changed(self, contract_id: str, accepted: bool):
        """Handle contract acceptance change"""
        self.contract_acceptances[contract_id] = accepted
        self.update_summary()
    
    def update_summary(self):
        """Update acceptance summary and enable/disable buttons"""
        total_contracts = len([c for c in self.applicable_contracts if c.acceptance_required])
        accepted_contracts = sum(1 for accepted in self.contract_acceptances.values() if accepted)
        
        total_sections = sum(len([s for s in c.sections if s.requires_agreement]) for c in self.applicable_contracts)
        accepted_sections = sum(1 for accepted in self.section_acceptances.values() if accepted)
        
        all_accepted = (accepted_contracts == total_contracts and 
                       accepted_sections == total_sections and
                       total_contracts > 0 and total_sections > 0)
        
        summary_text = f"""
        <b>Contract Acceptance Status:</b><br>
        Contracts: {accepted_contracts}/{total_contracts} accepted<br>
        Sections: {accepted_sections}/{total_sections} accepted<br>
        <br>
        """
        
        if all_accepted:
            summary_text += "<b style='color: green;'>✓ All required contracts and sections accepted!</b>"
            self.accept_all_btn.setEnabled(True)
        else:
            summary_text += "<b style='color: red;'>⚠ Please accept all required contracts and sections.</b>"
            self.accept_all_btn.setEnabled(False)
        
        self.summary_label.setText(summary_text)
        self.acceptance_changed.emit(all_accepted)
        
        if all_accepted:
            self.all_contracts_accepted.emit()
    
    def accept_all_contracts(self):
        """Accept all contracts and record in blockchain"""
        if not self.all_requirements_met():
            QMessageBox.warning(self, "Incomplete Acceptance", 
                              "Please accept all required contracts and sections before proceeding.")
            return
        
        # Record acceptances
        user_email = getattr(self, "_user_email", "pending_registration")
        success_count = 0
        for contract in self.applicable_contracts:
            if contract.acceptance_required:
                success = self.contract_manager.record_acceptance(
                    user_email=user_email,
                    contract_id=contract.contract_id,
                    ip_address="",  # Could be added if needed
                    user_agent=""   # Could be added if needed
                )
                if success:
                    success_count += 1
        
        if success_count == len([c for c in self.applicable_contracts if c.acceptance_required]):
            QMessageBox.information(self, "Contracts Accepted", 
                                  f"Successfully accepted {success_count} contracts. "
                                  "You may now complete your registration.")
            self.all_contracts_accepted.emit()
        else:
            QMessageBox.warning(self, "Acceptance Error", 
                              "Some contracts could not be recorded. Please try again.")
    
    def all_requirements_met(self) -> bool:
        """Check if all contract requirements are met"""
        # Check contract acceptances
        for contract in self.applicable_contracts:
            if contract.acceptance_required and not self.contract_acceptances.get(contract.contract_id, False):
                return False
        
        # Check section acceptances
        for contract in self.applicable_contracts:
            for section in contract.sections:
                if section.requires_agreement and not self.section_acceptances.get(section.section_id, False):
                    return False
        
        return True
    
    def show_contract_hierarchy(self):
        """Show dialog explaining contract hierarchy"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Contract Hierarchy Explanation")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        explanation = QTextBrowser()
        explanation.setHtml("""
        <h2>Contract Hierarchy and Precedence</h2>
        
        <h3>Hierarchy Order (Highest to Lowest Precedence):</h3>
        <ol>
        <li><b>Master Contract (Constitutional)</b> - Overrides all other contracts and governance documents</li>
        <li><b>Country Contracts</b> - National-level governance, subject to Constitutional constraints</li>
        <li><b>State Contracts</b> - Regional governance, subject to Constitutional and Country constraints</li>
        <li><b>City Contracts</b> - Local governance, subject to all higher-level constraints</li>
        </ol>
        
        <h3>Conflict Resolution:</h3>
        <ul>
        <li>Higher precedence contracts always override lower precedence contracts</li>
        <li>Constitutional rights cannot be diminished by any lower-level contract</li>
        <li>Emergency powers are subject to constitutional review and citizen oversight</li>
        <li>Contract amendments require supermajority approval and constitutional compliance review</li>
        </ul>
        
        <h3>Why This Hierarchy Matters:</h3>
        <ul>
        <li><b>Prevents Tyranny:</b> Master contract protects fundamental rights that cannot be voted away</li>
        <li><b>Clear Authority:</b> Eliminates confusion about which rules apply in case of conflicts</li>
        <li><b>Democratic Legitimacy:</b> Ensures power flows from constitutional principles through democratic representation</li>
        <li><b>Local Flexibility:</b> Allows local variation within constitutional constraints</li>
        </ul>
        """)
        layout.addWidget(explanation)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.close)
        layout.addWidget(button_box)
        
        dialog.exec_()
    
    def get_user_location(self) -> Dict[str, str]:
        """Get current user location for contract determination"""
        return self.user_location
    
    def set_user_location(self, location: Dict[str, str]):
        """Update user location and reload applicable contracts"""
        self.user_location = location
        self.load_applicable_contracts()


class ContractManagementWidget(QWidget):
    """Widget for managing contracts (admin interface)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.contract_manager = contract_manager
        self.setup_ui()
        self.load_contracts()
    
    def setup_ui(self):
        """Setup the contract management UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("<h2>Contract Management</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Splitter for list and viewer
        splitter = QSplitter(Qt.Horizontal)
        
        # Contract list
        list_group = QGroupBox("Contracts")
        list_layout = QVBoxLayout(list_group)
        
        self.contract_list = QListWidget()
        self.contract_list.itemClicked.connect(self.on_contract_selected)
        list_layout.addWidget(self.contract_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.view_btn = QPushButton("View Contract")
        self.view_btn.clicked.connect(self.view_selected_contract)
        self.view_btn.setEnabled(False)
        button_layout.addWidget(self.view_btn)
        
        self.create_btn = QPushButton("Create New Contract")
        self.create_btn.clicked.connect(self.create_new_contract)
        button_layout.addWidget(self.create_btn)
        
        list_layout.addLayout(button_layout)
        splitter.addWidget(list_group)
        
        # Contract details
        details_group = QGroupBox("Contract Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_browser = QTextBrowser()
        details_layout.addWidget(self.details_browser)
        
        splitter.addWidget(details_group)
        
        layout.addWidget(splitter)
    
    def load_contracts(self):
        """Load contracts into the list"""
        self.contract_list.clear()
        
        for contract in self.contract_manager.get_active_contracts():
            item_text = f"{contract.contract_type.value.title()} - {contract.jurisdiction} (v{contract.version})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, contract.contract_id)
            self.contract_list.addItem(item)
    
    def on_contract_selected(self, item: QListWidgetItem):
        """Handle contract selection"""
        contract_id = item.data(Qt.UserRole)
        contract = self.contract_manager.get_contract(contract_id)
        
        if contract:
            self.view_btn.setEnabled(True)
            self.show_contract_details(contract)
        else:
            self.view_btn.setEnabled(False)
            self.details_browser.clear()
    
    def show_contract_details(self, contract: PlatformContract):
        """Show contract details in the browser"""
        html = f"""
        <h3>{contract.contract_type.value.title()} Contract</h3>
        <p><b>Jurisdiction:</b> {contract.jurisdiction}</p>
        <p><b>Version:</b> {contract.version}</p>
        <p><b>Status:</b> {contract.status.value}</p>
        <p><b>Precedence Level:</b> {contract.precedence_level}</p>
        <p><b>Created:</b> {contract.created_date}</p>
        <p><b>Effective:</b> {contract.effective_date}</p>
        
        <h4>Sections ({len(contract.sections)}):</h4>
        <ul>
        """
        
        for section in contract.get_all_sections():
            html += f"<li><b>{section.title}</b> (Priority: {section.precedence})"
            if section.requires_agreement:
                html += " - <i>Requires Agreement</i>"
            html += "</li>"
        
        html += "</ul>"
        
        self.details_browser.setHtml(html)
    
    def view_selected_contract(self):
        """View the selected contract in detail"""
        current_item = self.contract_list.currentItem()
        if not current_item:
            return
        
        contract_id = current_item.data(Qt.UserRole)
        contract = self.contract_manager.get_contract(contract_id)
        
        if contract:
            viewer = ContractViewer(contract, self)
            viewer.exec_()
    
    def create_new_contract(self):
        """Create a new contract (placeholder)"""
        QMessageBox.information(self, "Create Contract", 
                              "Contract creation interface would be implemented here.")


# Convenience function for easy integration
def show_contract_acceptance_dialog(user_location: Dict[str, str], parent=None, user_email: str = "") -> bool:
    """
    Show contract acceptance dialog and return True if all contracts accepted
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle("Contract Acceptance Required")
    dialog.resize(900, 700)
    
    layout = QVBoxLayout(dialog)
    
    acceptance_widget = ContractAcceptanceWidget(user_location)
    # Store provided email on the widget for use during recording
    setattr(acceptance_widget, "_user_email", user_email or "pending_registration")
    layout.addWidget(acceptance_widget)
    
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    layout.addWidget(button_box)
    
    # Enable OK button only when all contracts accepted
    button_box.button(QDialogButtonBox.Ok).setEnabled(False)
    acceptance_widget.acceptance_changed.connect(
        lambda accepted: button_box.button(QDialogButtonBox.Ok).setEnabled(accepted)
    )
    
    def _on_accept():
        try:
            if acceptance_widget.all_requirements_met():
                acceptance_widget.accept_all_contracts()
        finally:
            dialog.accept()

    button_box.accepted.connect(_on_accept)
    button_box.rejected.connect(dialog.reject)
    
    result = dialog.exec_()
    return result == QDialog.Accepted and acceptance_widget.all_requirements_met()