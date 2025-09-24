"""
Enhanced Contract Tab Widget with Amendment System
Integrates contract viewing and amendment capabilities
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLabel, QPushButton, QListWidget, QListWidgetItem,
                             QTextBrowser, QGroupBox, QSplitter, QMessageBox)
from PyQt5.QtCore import Qt
from typing import Optional

from .contract_ui import ContractViewer, GenesisContractViewer
from .contract_terms import contract_manager, PlatformContract
from .amendment_ui import ContractAmendmentTab


class EnhancedContractTab(QWidget):
    """Enhanced contract tab with amendment system integration"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.contract_manager = contract_manager
        self.setup_ui()
        self.load_contracts()
    
    def setup_ui(self):
        """Set up the enhanced contract interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("<h1>📜 Contract Management System</h1>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Create tab widget for different functions
        self.tab_widget = QTabWidget()
        
        # Tab 1: Contract Viewer
        viewer_tab = self.create_viewer_tab()
        self.tab_widget.addTab(viewer_tab, "📋 View Contracts")
        
        # Tab 2: Contract Amendments
        amendment_tab = ContractAmendmentTab()
        self.tab_widget.addTab(amendment_tab, "📝 Propose Amendments")
        
        # Tab 3: Contract Management (for admin users)
        management_tab = self.create_management_tab()
        self.tab_widget.addTab(management_tab, "⚙️ Admin Management")
        
        layout.addWidget(self.tab_widget)
    
    def create_viewer_tab(self) -> QWidget:
        """Create the contract viewer tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        description = QLabel(
            "Browse and view all available contracts. "
            "The Genesis Contract establishes the foundational law of our Republic."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-style: italic; color: gray; margin: 10px;")
        layout.addWidget(description)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Contract list side
        list_group = QGroupBox("Available Contracts")
        list_layout = QVBoxLayout(list_group)
        
        self.contract_list = QListWidget()
        self.contract_list.itemClicked.connect(self.on_contract_selected)
        list_layout.addWidget(self.contract_list)
        
        # Buttons for contract list
        button_layout = QHBoxLayout()
        
        self.view_btn = QPushButton("📖 View Full Contract")
        self.view_btn.clicked.connect(self.view_selected_contract)
        self.view_btn.setEnabled(False)
        button_layout.addWidget(self.view_btn)
        
        self.genesis_btn = QPushButton("🏛️ View Genesis Contract")
        self.genesis_btn.clicked.connect(self.view_genesis_contract)
        button_layout.addWidget(self.genesis_btn)
        
        list_layout.addLayout(button_layout)
        splitter.addWidget(list_group)
        
        # Details side
        details_group = QGroupBox("Contract Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_browser = QTextBrowser()
        self.details_browser.setPlaceholderText("Select a contract from the list to view its details.")
        details_layout.addWidget(self.details_browser)
        
        splitter.addWidget(details_group)
        
        # Set splitter proportions
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        return tab
    
    def create_management_tab(self) -> QWidget:
        """Create the contract management tab (admin functions)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Admin notice
        admin_notice = QLabel(
            "⚠️ <b>Administrative Functions</b><br>"
            "These functions are restricted to users with administrative privileges."
        )
        admin_notice.setStyleSheet("color: orange; font-weight: bold; padding: 10px; background-color: #fff8dc; border: 1px solid #ddd; border-radius: 4px;")
        admin_notice.setWordWrap(True)
        layout.addWidget(admin_notice)
        
        # Admin functions
        admin_group = QGroupBox("Administrative Functions")
        admin_layout = QVBoxLayout(admin_group)
        
        create_btn = QPushButton("📝 Create New Contract")
        create_btn.clicked.connect(self.create_new_contract)
        admin_layout.addWidget(create_btn)
        
        import_btn = QPushButton("📤 Import Contract")
        import_btn.clicked.connect(self.import_contract)
        admin_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📥 Export Contract")
        export_btn.clicked.connect(self.export_contract)
        admin_layout.addWidget(export_btn)
        
        admin_layout.addStretch()
        
        layout.addWidget(admin_group)
        layout.addStretch()
        
        return tab
    
    def load_contracts(self):
        """Load contracts into the list"""
        self.contract_list.clear()
        
        # Add Genesis Contract as special item
        genesis_item = QListWidgetItem("🏛️ The Genesis Contract (Constitution)")
        genesis_item.setData(Qt.UserRole, "genesis")
        genesis_item.setToolTip("The foundational constitutional contract of the Republic")
        self.contract_list.addItem(genesis_item)
        
        # Add other contracts
        contracts = self.contract_manager.get_active_contracts()
        for contract in contracts:
            # Handle contract display name
            display_name = getattr(contract, 'title', None) or f"{contract.contract_type.value.title()} Contract"
            item = QListWidgetItem(f"{display_name} (v{contract.version})")
            item.setData(Qt.UserRole, contract.contract_id)
            item.setToolTip(f"Jurisdiction: {contract.jurisdiction}\\nStatus: {contract.status.value}")
            self.contract_list.addItem(item)
        
        if not contracts:
            # Add placeholder item if no contracts
            placeholder_item = QListWidgetItem("📋 No additional contracts available")
            placeholder_item.setData(Qt.UserRole, None)
            placeholder_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
            self.contract_list.addItem(placeholder_item)
    
    def on_contract_selected(self, item: QListWidgetItem):
        """Handle contract selection"""
        contract_id = item.data(Qt.UserRole)
        
        if contract_id == "genesis":
            # Handle Genesis Contract selection
            self.show_genesis_details()
            self.view_btn.setEnabled(True)
        elif contract_id is None:
            # Placeholder item
            self.details_browser.clear()
            self.view_btn.setEnabled(False)
        else:
            # Handle regular contract selection
            contract = self.contract_manager.get_contract(contract_id)
            if contract:
                self.show_contract_details(contract)
                self.view_btn.setEnabled(True)
            else:
                self.details_browser.clear()
                self.view_btn.setEnabled(False)
    
    def show_genesis_details(self):
        """Show Genesis Contract details"""
        html = """
        <h2>🏛️ The Genesis Contract</h2>
        <p><strong>Type:</strong> Constitutional Foundation</p>
        <p><strong>Status:</strong> Active and Immutable</p>
        <p><strong>Jurisdiction:</strong> Republic-wide</p>
        <p><strong>Version:</strong> 1.0</p>
        
        <h3>Description:</h3>
        <p>The Genesis Contract serves as the foundational constitutional document of our Republic. 
        It establishes the framework for governance, defines the relationship between citizens and 
        government, and sets forth the fundamental rights and responsibilities.</p>
        
        <h3>Key Features:</h3>
        <ul>
        <li><strong>18 Articles</strong> covering all aspects of governance</li>
        <li><strong>Separation of Powers</strong> between Legislative, Executive, and Judicial branches</li>
        <li><strong>Bill of Rights</strong> protecting fundamental freedoms</li>
        <li><strong>Amendment Process</strong> for constitutional changes</li>
        <li><strong>Blockchain Recording</strong> for immutable transparency</li>
        </ul>
        
        <h3>Legal Authority:</h3>
        <p>This contract has supreme legal authority within the Republic and serves as the basis 
        for all other laws, regulations, and agreements. All citizens, representatives, and 
        officials are bound by its terms.</p>
        
        <p><em>Click "View Full Contract" to read the complete text.</em></p>
        """
        
        self.details_browser.setHtml(html)
    
    def show_contract_details(self, contract: PlatformContract):
        """Show details for a regular contract"""
        # Get contract display name
        contract_title = getattr(contract, 'title', None) or f"{contract.contract_type.value.title()} Contract"
        
        html = f"""
        <h2>{contract_title}</h2>
        <p><strong>Type:</strong> {contract.contract_type.value.title()}</p>
        <p><strong>Status:</strong> {contract.status.value.title()}</p>
        <p><strong>Jurisdiction:</strong> {contract.jurisdiction}</p>
        <p><strong>Version:</strong> {contract.version}</p>
        <p><strong>Precedence Level:</strong> {contract.precedence_level}</p>
        <p><strong>Created:</strong> {contract.created_date}</p>
        <p><strong>Effective:</strong> {contract.effective_date}</p>
        
        <h3>Sections ({len(contract.sections)}):</h3>
        <ul>
        """
        
        for section in contract.get_all_sections():
            html += f"<li><strong>{section.title}</strong> (Priority: {section.precedence})"
            if section.requires_agreement:
                html += " - <em>Requires Agreement</em>"
            html += "</li>"
        
        html += """
        </ul>
        
        <p><em>Click "View Full Contract" to read the complete text and sections.</em></p>
        """
        
        self.details_browser.setHtml(html)
    
    def view_selected_contract(self):
        """View the selected contract in detail"""
        current_item = self.contract_list.currentItem()
        if not current_item:
            return
        
        contract_id = current_item.data(Qt.UserRole)
        
        if contract_id == "genesis":
            self.view_genesis_contract()
        else:
            contract = self.contract_manager.get_contract(contract_id)
            if contract:
                viewer = ContractViewer(contract, self)
                viewer.exec_()
    
    def view_genesis_contract(self):
        """View the Genesis Contract"""
        viewer = GenesisContractViewer(self)
        viewer.exec_()
    
    def create_new_contract(self):
        """Create a new contract (admin function)"""
        # Check if user has admin privileges (placeholder)
        QMessageBox.information(self, "Create Contract", 
                              "Contract creation interface would be implemented here.\\n\\n"
                              "This function requires administrative privileges and would "
                              "include forms for contract details, sections, and approval workflows.")
    
    def import_contract(self):
        """Import a contract from file (admin function)"""
        QMessageBox.information(self, "Import Contract", 
                              "Contract import interface would be implemented here.\\n\\n"
                              "This would allow importing contracts from JSON or other formats.")
    
    def export_contract(self):
        """Export a contract to file (admin function)"""
        QMessageBox.information(self, "Export Contract", 
                              "Contract export interface would be implemented here.\\n\\n"
                              "This would allow exporting contracts for backup or sharing.")