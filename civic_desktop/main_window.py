# Main Application Window - Updated with Tasks Tab
# PyQt5-based main interface with comprehensive task management integration

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QMessageBox, QStatusBar,
    QMenuBar, QAction, qApp, QSystemTrayIcon, QMenu
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPixmap

# Import all module tabs
try:
    from users.login import LoginWidget
    from users.dashboard import UserDashboard
    from debates.ui import DebateUI
    from moderation.ui import ModerationDashboard
    from blockchain.blockchain_tab import BlockchainTab
    from contracts.enhanced_contract_tab import EnhancedContractTab
    from training.ui import TrainingUI
    from crypto.wallet_ui import WalletUI
    from github_integration.github_tab import GitHubTab
    from maps.map_view import MapView
    from system_guide.guide_tab import GuideTab
    from analytics.reports_ui import AnalyticsReportsTab
    from events.calendar_ui import EventsCalendarTab
    from communications.communications_ui import CommunicationsTab
    from surveys.polling_ui import SurveysPollingTab
    from petitions.initiatives_ui import PetitionsInitiativesTab
    from documents.archive_ui import DocumentsArchiveTab
    from transparency.oversight_ui import TransparencyOversightTab
    from collaboration.collaboration_ui import CollaborationTab
    
    # Import the new Tasks module
    from tasks.task_ui import TaskDashboard
    
    # Import City/Town Elections module  
    from governance.city_election_ui import CityElectionTab
    
    # Import State Elections module
    from governance.state_election_ui import StateElectionWidget
    
    # Import Country Elections module
    from governance.country_election_ui import CountryElectionTab
    
    # Import World Elections module
    from governance.world_election_ui import WorldElectionTab
    
    # Import Real-World Government Integration module
    from government.government_ui import RealWorldGovernmentTab
    
    # Import Government Directory module
    from government.directory_ui import GovernmentDirectoryTab
    
    # Import Citizen Verification module
    from government.citizen_verification_ui import CitizenVerificationTab

except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    # Create placeholder widgets for missing modules
    
    class PlaceholderWidget(QWidget):
        def __init__(self, module_name):
            super().__init__()
            layout = QVBoxLayout()
            label = QLabel(f"{module_name} Module")
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 16))
            layout.addWidget(label)
            
            info_label = QLabel("This module is being developed")
            info_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(info_label)
            
            self.setLayout(layout)
    
    # Create placeholder for elections if not available
    CityElectionTab = lambda: PlaceholderWidget("City Contract Elections")
    StateElectionWidget = lambda: PlaceholderWidget("State Contract Elections")
    CountryElectionTab = lambda: PlaceholderWidget("Country Contract Elections")
    WorldElectionTab = lambda: PlaceholderWidget("World Contract Elections")
    
    # Create placeholder classes for missing imports
    LoginWidget = lambda: PlaceholderWidget("Login")
    UserDashboard = lambda: PlaceholderWidget("User Dashboard")
    DebateUI = lambda: PlaceholderWidget("Debate")
    ModerationDashboard = lambda: PlaceholderWidget("Moderation")
    BlockchainTab = lambda: PlaceholderWidget("Blockchain")
    EnhancedContractTab = lambda: PlaceholderWidget("Contracts")
    TrainingUI = lambda: PlaceholderWidget("Training")
    WalletUI = lambda: PlaceholderWidget("Crypto Wallet")
    GitHubTab = lambda: PlaceholderWidget("GitHub")
    MapView = lambda: PlaceholderWidget("Maps")
    GuideTab = lambda: PlaceholderWidget("System Guide")
    AnalyticsReportsTab = lambda: PlaceholderWidget("Analytics")
    EventsCalendarTab = lambda: PlaceholderWidget("Events")
    CommunicationsTab = lambda: PlaceholderWidget("Communications")
    SurveysPollingTab = lambda: PlaceholderWidget("Surveys")
    PetitionsInitiativesTab = lambda: PlaceholderWidget("Petitions")
    DocumentsArchiveTab = lambda: PlaceholderWidget("Documents")
    TransparencyOversightTab = lambda: PlaceholderWidget("Transparency")
    CollaborationTab = lambda: PlaceholderWidget("Collaboration")
    TaskDashboard = lambda: PlaceholderWidget("Tasks")

# Session management import
try:
    from users.session import SessionManager
except ImportError:
    class SessionManager:
        @staticmethod
        def is_authenticated():
            return True
        
        @staticmethod
        def get_current_user():
            return {'email': 'test@example.com', 'role': 'contract_member', 'name': 'Test User'}

class MainWindow(QMainWindow):
    """Main application window with comprehensive tab-based interface"""
    
    # Signals for cross-tab communication
    user_authenticated = pyqtSignal(dict)
    user_logged_out = pyqtSignal()
    task_notification = pyqtSignal(str, dict)  # task_type, task_data
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.tabs = {}
        
        # Initialize UI
        self.init_ui()
        
        # Set up auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_tabs)
        self.refresh_timer.start(60000)  # Refresh every minute
        
        # Check authentication status
        self.check_authentication()
    
    def init_ui(self):
        """Initialize the main user interface"""
        
        self.setWindowTitle("🏛️ Civic Engagement Platform")
        self.setMinimumSize(1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header section
        self.create_header(main_layout)
        
        # Tab widget for all modules
        self.tab_widget = QTabWidget()
        self.create_tabs()
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.create_status_bar()
        
        # Menu bar
        self.create_menu_bar()
        
        central_widget.setLayout(main_layout)
        
        # Apply styling
        self.apply_styles()
        
        # Set up system tray (if supported)
        self.setup_system_tray()
    
    def create_header(self, layout):
        """Create application header with user info and quick actions"""
        
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        
        # Application title
        title_label = QLabel("🏛️ Civic Engagement Platform")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # User info and actions
        self.user_info_label = QLabel("Not authenticated")
        header_layout.addWidget(self.user_info_label)
        
        # Quick action buttons
        self.login_logout_btn = QPushButton("Login")
        self.login_logout_btn.clicked.connect(self.toggle_authentication)
        header_layout.addWidget(self.login_logout_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_all_tabs)
        header_layout.addWidget(self.refresh_btn)
        
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)
    
    def create_tabs(self):
        """Create all module tabs"""
        
        # Core Authentication and User Management
        try:
            self.tabs['users'] = LoginWidget()
            self.tab_widget.addTab(self.tabs['users'], "👤 Users")
        except Exception as e:
            print(f"Error creating Users tab: {e}")
        
        # NEW: Tasks Module (Primary Tab)
        try:
            self.tabs['tasks'] = TaskDashboard()
            self.tab_widget.addTab(self.tabs['tasks'], "📋 Tasks")
            
            # Connect task signals
            if hasattr(self.tabs['tasks'], 'task_completed'):
                self.tabs['tasks'].task_completed.connect(self.handle_task_completed)
            if hasattr(self.tabs['tasks'], 'task_deferred'):
                self.tabs['tasks'].task_deferred.connect(self.handle_task_deferred)
                
        except Exception as e:
            print(f"Error creating Tasks tab: {e}")
            self.tabs['tasks'] = PlaceholderWidget("Tasks")
            self.tab_widget.addTab(self.tabs['tasks'], "📋 Tasks")
        
        # Democratic Participation
        try:
            self.tabs['debates'] = DebateUI()
            self.tab_widget.addTab(self.tabs['debates'], "💬 Debates")
        except Exception as e:
            print(f"Error creating Debates tab: {e}")
        
        try:
            self.tabs['moderation'] = ModerationDashboard()
            self.tab_widget.addTab(self.tabs['moderation'], "🛡️ Moderation")
        except Exception as e:
            print(f"Error creating Moderation tab: {e}")
        
        # Governance and Transparency
        try:
            self.tabs['contracts'] = EnhancedContractTab()
            self.tab_widget.addTab(self.tabs['contracts'], "⚖️ Contracts")
        except Exception as e:
            print(f"Error creating Contracts tab: {e}")
        
        try:
            self.tabs['blockchain'] = BlockchainTab()
            self.tab_widget.addTab(self.tabs['blockchain'], "⛓️ Blockchain")
        except Exception as e:
            print(f"Error creating Blockchain tab: {e}")
        
        # Real-World Government Integration
        try:
            self.tabs['government'] = RealWorldGovernmentTab()
            self.tab_widget.addTab(self.tabs['government'], "🏛️ Real Government")
        except Exception as e:
            print(f"Error creating Real Government tab: {e}")
            self.tabs['government'] = PlaceholderWidget("Real Government")
            self.tab_widget.addTab(self.tabs['government'], "🏛️ Real Government")
        
        # Government Officials Directory
        try:
            self.tabs['government_directory'] = GovernmentDirectoryTab()
            self.tab_widget.addTab(self.tabs['government_directory'], "🌍 Government Directory")
        except Exception as e:
            print(f"Error creating Government Directory tab: {e}")
            self.tabs['government_directory'] = PlaceholderWidget("Government Directory")
            self.tab_widget.addTab(self.tabs['government_directory'], "🌍 Government Directory")
        
        # Citizen Verification System
        try:
            self.tabs['citizen_verification'] = CitizenVerificationTab()
            self.tab_widget.addTab(self.tabs['citizen_verification'], "🏆 Citizen Verification")
        except Exception as e:
            print(f"Error creating Citizen Verification tab: {e}")
            self.tabs['citizen_verification'] = PlaceholderWidget("Citizen Verification")
            self.tab_widget.addTab(self.tabs['citizen_verification'], "🏆 Citizen Verification")
        
        # City/Town Elections and Local Governance
        try:
            self.tabs['city_elections'] = CityElectionTab()
            self.tab_widget.addTab(self.tabs['city_elections'], "🏛️ City Contract Elections")
        except Exception as e:
            print(f"Error creating City Contract Elections tab: {e}")
        
        # State Elections and Electoral College
        try:
            self.tabs['state_elections'] = StateElectionWidget()
            self.tab_widget.addTab(self.tabs['state_elections'], "🗳️ State Contract Elections")
        except Exception as e:
            print(f"Error creating State Contract Elections tab: {e}")
        
        # Country Elections and National Governance
        try:
            self.tabs['country_elections'] = CountryElectionTab()
            self.tab_widget.addTab(self.tabs['country_elections'], "🌍 Country Contract Elections")
        except Exception as e:
            print(f"Error creating Country Contract Elections tab: {e}")
        
        # World Elections and Global Governance
        try:
            self.tabs['world_elections'] = WorldElectionTab()
            self.tab_widget.addTab(self.tabs['world_elections'], "🌎 World Contract Elections")
        except Exception as e:
            print(f"Error creating World Contract Elections tab: {e}")
        
        # Civic Services and Education
        try:
            self.tabs['training'] = TrainingUI()
            self.tab_widget.addTab(self.tabs['training'], "📚 Training")
        except Exception as e:
            print(f"Error creating Training tab: {e}")
        
        try:
            self.tabs['crypto'] = WalletUI()
            self.tab_widget.addTab(self.tabs['crypto'], "💰 Crypto/Wallet")
        except Exception as e:
            print(f"Error creating Crypto tab: {e}")
        
        # Community Engagement
        try:
            self.tabs['events'] = EventsCalendarTab()
            self.tab_widget.addTab(self.tabs['events'], "📅 Events")
        except Exception as e:
            print(f"Error creating Events tab: {e}")
        
        try:
            self.tabs['communications'] = CommunicationsTab()
            self.tab_widget.addTab(self.tabs['communications'], "📨 Communications")
        except Exception as e:
            print(f"Error creating Communications tab: {e}")
        
        try:
            self.tabs['surveys'] = SurveysPollingTab()
            self.tab_widget.addTab(self.tabs['surveys'], "📊 Surveys")
        except Exception as e:
            print(f"Error creating Surveys tab: {e}")
        
        try:
            self.tabs['petitions'] = PetitionsInitiativesTab()
            self.tab_widget.addTab(self.tabs['petitions'], "📝 Petitions")
        except Exception as e:
            print(f"Error creating Petitions tab: {e}")
        
        # Administrative and Oversight
        try:
            self.tabs['documents'] = DocumentsArchiveTab()
            self.tab_widget.addTab(self.tabs['documents'], "📂 Documents")
        except Exception as e:
            print(f"Error creating Documents tab: {e}")
        
        try:
            self.tabs['transparency'] = TransparencyOversightTab()
            self.tab_widget.addTab(self.tabs['transparency'], "🔍 Transparency")
        except Exception as e:
            print(f"Error creating Transparency tab: {e}")
        
        try:
            self.tabs['analytics'] = AnalyticsReportsTab()
            self.tab_widget.addTab(self.tabs['analytics'], "📈 Analytics")
        except Exception as e:
            print(f"Error creating Analytics tab: {e}")
        
        # Collaboration and Integration
        try:
            self.tabs['collaboration'] = CollaborationTab()
            self.tab_widget.addTab(self.tabs['collaboration'], "🤝 Collaboration")
        except Exception as e:
            print(f"Error creating Collaboration tab: {e}")
        
        try:
            self.tabs['maps'] = MapView()
            self.tab_widget.addTab(self.tabs['maps'], "🗺️ Maps")
        except Exception as e:
            print(f"Error creating Maps tab: {e}")
        
        # System and Development
        try:
            self.tabs['github'] = GitHubTab()
            self.tab_widget.addTab(self.tabs['github'], "🐙 GitHub")
        except Exception as e:
            print(f"Error creating GitHub tab: {e}")
        
        try:
            self.tabs['guide'] = GuideTab()
            self.tab_widget.addTab(self.tabs['guide'], "❓ System Guide")
        except Exception as e:
            print(f"Error creating Guide tab: {e}")
        
        # Set default tab to Tasks (new primary tab)
        try:
            tasks_index = None
            for i in range(self.tab_widget.count()):
                if "Tasks" in self.tab_widget.tabText(i):
                    tasks_index = i
                    break
            
            if tasks_index is not None:
                self.tab_widget.setCurrentIndex(tasks_index)
        except Exception as e:
            print(f"Error setting default tab: {e}")
    
    def create_status_bar(self):
        """Create status bar with system information"""
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status messages
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Connection status
        self.connection_label = QLabel("🟢 Connected")
        self.status_bar.addPermanentWidget(self.connection_label)
        
        # User status
        self.user_status_label = QLabel("👤 Not authenticated")
        self.status_bar.addPermanentWidget(self.user_status_label)
    
    def create_menu_bar(self):
        """Create application menu bar"""
        
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        refresh_action = QAction('Refresh All', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_all_tabs)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        tasks_action = QAction('Tasks Dashboard', self)
        tasks_action.setShortcut('Ctrl+T')
        tasks_action.triggered.connect(self.show_tasks_tab)
        view_menu.addAction(tasks_action)
        
        debates_action = QAction('Debates', self)
        debates_action.setShortcut('Ctrl+D')
        debates_action.triggered.connect(self.show_debates_tab)
        view_menu.addAction(debates_action)
        
        contracts_action = QAction('Contracts', self)
        contracts_action.setShortcut('Ctrl+C')
        contracts_action.triggered.connect(self.show_contracts_tab)
        view_menu.addAction(contracts_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        blockchain_action = QAction('Blockchain Explorer', self)
        blockchain_action.triggered.connect(self.show_blockchain_tab)
        tools_menu.addAction(blockchain_action)
        
        analytics_action = QAction('Analytics Dashboard', self)
        analytics_action.triggered.connect(self.show_analytics_tab)
        tools_menu.addAction(analytics_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        guide_action = QAction('System Guide', self)
        guide_action.setShortcut('F1')
        guide_action.triggered.connect(self.show_guide_tab)
        help_menu.addAction(guide_action)
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_system_tray(self):
        """Set up system tray icon (if supported)"""
        
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Set tray icon (you would need an actual icon file)
            # self.tray_icon.setIcon(QIcon("icon.png"))
            
            # Tray menu
            tray_menu = QMenu()
            
            show_action = tray_menu.addAction("Show")
            show_action.triggered.connect(self.show)
            
            hide_action = tray_menu.addAction("Hide")
            hide_action.triggered.connect(self.hide)
            
            tray_menu.addSeparator()
            
            quit_action = tray_menu.addAction("Quit")
            quit_action.triggered.connect(qApp.quit)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def check_authentication(self):
        """Check current authentication status"""
        
        try:
            if SessionManager.is_authenticated():
                user = SessionManager.get_current_user()
                self.handle_user_authenticated(user)
            else:
                self.handle_user_logged_out()
        except Exception as e:
            print(f"Error checking authentication: {e}")
            self.handle_user_logged_out()
    
    def handle_user_authenticated(self, user_data):
        """Handle successful user authentication"""
        
        self.current_user = user_data
        
        # Update UI
        user_name = user_data.get('name', user_data.get('email', 'User'))
        user_role = user_data.get('role', 'Member').replace('_', ' ').title()
        
        self.user_info_label.setText(f"👤 {user_name} ({user_role})")
        self.user_status_label.setText(f"👤 {user_name}")
        self.login_logout_btn.setText("Logout")
        
        # Enable tabs based on user role
        self.update_tab_visibility(user_data.get('role', 'contract_member'))
        
        # Emit signal for other components
        self.user_authenticated.emit(user_data)
        
        # Update status
        self.status_label.setText("User authenticated successfully")
        
        # Refresh tasks tab specifically
        if 'tasks' in self.tabs and hasattr(self.tabs['tasks'], 'refresh_tasks'):
            try:
                self.tabs['tasks'].refresh_tasks()
            except Exception as e:
                print(f"Error refreshing tasks: {e}")
    
    def handle_user_logged_out(self):
        """Handle user logout"""
        
        self.current_user = None
        
        # Update UI
        self.user_info_label.setText("Not authenticated")
        self.user_status_label.setText("👤 Not authenticated")
        self.login_logout_btn.setText("Login")
        
        # Show login tab
        if 'users' in self.tabs:
            users_index = None
            for i in range(self.tab_widget.count()):
                if "Users" in self.tab_widget.tabText(i):
                    users_index = i
                    break
            
            if users_index is not None:
                self.tab_widget.setCurrentIndex(users_index)
        
        # Emit signal
        self.user_logged_out.emit()
        
        # Update status
        self.status_label.setText("Please log in to access platform features")
    
    def toggle_authentication(self):
        """Toggle between login and logout"""
        
        if SessionManager.is_authenticated():
            # Logout
            try:
                SessionManager.logout()
                self.handle_user_logged_out()
                QMessageBox.information(self, "Logged Out", "You have been logged out successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Logout Error", f"Error logging out: {e}")
        else:
            # Show login tab
            if 'users' in self.tabs:
                users_index = None
                for i in range(self.tab_widget.count()):
                    if "Users" in self.tab_widget.tabText(i):
                        users_index = i
                        break
                
                if users_index is not None:
                    self.tab_widget.setCurrentIndex(users_index)
    
    def update_tab_visibility(self, user_role):
        """Update tab visibility based on user role"""
        
        # Define role-based tab access
        role_access = {
            'contract_member': ['tasks', 'debates', 'training', 'events', 'communications', 'surveys', 'petitions', 'documents', 'maps', 'guide'],
            'contract_representative': ['tasks', 'debates', 'moderation', 'contracts', 'training', 'crypto', 'events', 'communications', 'surveys', 'petitions', 'documents', 'transparency', 'analytics', 'maps', 'guide'],
            'contract_senator': ['tasks', 'debates', 'moderation', 'contracts', 'blockchain', 'training', 'crypto', 'events', 'communications', 'surveys', 'petitions', 'documents', 'transparency', 'analytics', 'collaboration', 'maps', 'guide'],
            'contract_elder': ['tasks', 'debates', 'moderation', 'contracts', 'blockchain', 'training', 'crypto', 'events', 'communications', 'surveys', 'petitions', 'documents', 'transparency', 'analytics', 'collaboration', 'maps', 'github', 'guide'],
            'contract_founder': ['tasks', 'debates', 'moderation', 'contracts', 'blockchain', 'training', 'crypto', 'events', 'communications', 'surveys', 'petitions', 'documents', 'transparency', 'analytics', 'collaboration', 'maps', 'github', 'guide']
        }
        
        # Get allowed tabs for user role
        allowed_tabs = role_access.get(user_role, role_access['contract_member'])
        
        # Update tab visibility (note: this is a simplified approach)
        # In a full implementation, you would show/hide tabs dynamically
        # For now, all tabs are visible but may show different content based on role
        
        # Update status to show access level
        access_level = len(allowed_tabs)
        self.status_label.setText(f"Access level: {access_level} modules available")
    
    def refresh_all_tabs(self):
        """Refresh all tabs with current data"""
        
        try:
            # Refresh tasks tab (primary focus)
            if 'tasks' in self.tabs and hasattr(self.tabs['tasks'], 'refresh_tasks'):
                self.tabs['tasks'].refresh_tasks()
            
            # Refresh other tabs that have refresh methods
            for tab_name, tab_widget in self.tabs.items():
                if hasattr(tab_widget, 'refresh_data'):
                    try:
                        tab_widget.refresh_data()
                    except Exception as e:
                        print(f"Error refreshing {tab_name} tab: {e}")
                elif hasattr(tab_widget, 'refresh'):
                    try:
                        tab_widget.refresh()
                    except Exception as e:
                        print(f"Error refreshing {tab_name} tab: {e}")
            
            self.status_label.setText("All tabs refreshed successfully")
            
        except Exception as e:
            self.status_label.setText(f"Error refreshing tabs: {e}")
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing data: {e}")
    
    def handle_task_completed(self, task_id):
        """Handle task completion signal from tasks tab"""
        
        self.status_label.setText(f"Task {task_id} completed successfully")
        
        # Refresh related tabs that might be affected
        if 'blockchain' in self.tabs and hasattr(self.tabs['blockchain'], 'refresh_data'):
            self.tabs['blockchain'].refresh_data()
        
        if 'crypto' in self.tabs and hasattr(self.tabs['crypto'], 'refresh_balance'):
            self.tabs['crypto'].refresh_balance()
    
    def handle_task_deferred(self, task_id):
        """Handle task deferral signal from tasks tab"""
        
        self.status_label.setText(f"Task {task_id} deferred")
    
    # Tab navigation methods
    def show_tasks_tab(self):
        """Show tasks tab"""
        self._show_tab_by_name("Tasks")
    
    def show_debates_tab(self):
        """Show debates tab"""
        self._show_tab_by_name("Debates")
    
    def show_contracts_tab(self):
        """Show contracts tab"""
        self._show_tab_by_name("Contracts")
    
    def show_blockchain_tab(self):
        """Show blockchain tab"""
        self._show_tab_by_name("Blockchain")
    
    def show_analytics_tab(self):
        """Show analytics tab"""
        self._show_tab_by_name("Analytics")
    
    def show_guide_tab(self):
        """Show guide tab"""
        self._show_tab_by_name("Guide")
    
    def _show_tab_by_name(self, tab_name):
        """Helper method to show tab by name"""
        
        for i in range(self.tab_widget.count()):
            if tab_name.lower() in self.tab_widget.tabText(i).lower():
                self.tab_widget.setCurrentIndex(i)
                break
    
    def show_about(self):
        """Show about dialog"""
        
        about_text = """
        <h2>🏛️ Civic Engagement Platform</h2>
        <p><b>Version:</b> 2.0.0</p>
        <p><b>Build:</b> Tasks Integration Release</p>
        
        <p>A comprehensive platform for democratic participation and civic engagement.</p>
        
        <h3>New Features:</h3>
        <ul>
            <li>📋 <b>Tasks Module:</b> Centralized task management for all civic duties</li>
            <li>🔍 Multi-level blockchain validation with Contract Member participation</li>
            <li>🗳️ Integrated voting task management</li>
            <li>⚖️ Contract review task assignment</li>
            <li>👥 Jury duty and moderation task coordination</li>
            <li>🔔 Comprehensive notification system</li>
        </ul>
        
        <h3>Core Modules:</h3>
        <ul>
            <li>👤 Users & Authentication</li>
            <li>💬 Debates & Discussion</li>
            <li>🛡️ Content Moderation</li>
            <li>⚖️ Constitutional Contracts</li>
            <li>⛓️ Blockchain Transparency</li>
            <li>📚 Civic Education</li>
            <li>💰 Civic Token Economy</li>
            <li>📅 Events & Calendar</li>
            <li>📨 Communications</li>
            <li>📊 Surveys & Polling</li>
            <li>📝 Petitions & Initiatives</li>
            <li>📂 Document Archive</li>
            <li>🔍 Transparency & Oversight</li>
            <li>📈 Analytics & Reports</li>
            <li>🤝 Inter-jurisdictional Collaboration</li>
        </ul>
        
        <p><b>Developed for:</b> Democratic institutions, civic organizations, and engaged communities</p>
        <p><b>License:</b> Open Source</p>
        """
        
        QMessageBox.about(self, "About Civic Engagement Platform", about_text)
    
    def apply_styles(self):
        """Apply custom styles to the main window"""
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            QTabWidget::pane {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #e9ecef;
                border: 2px solid #dee2e6;
                border-bottom-color: #e9ecef;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 120px;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
                color: #007bff;
            }
            
            QTabBar::tab:hover {
                background-color: #f8f9fa;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004494;
            }
            
            QLabel {
                color: #343a40;
            }
            
            QStatusBar {
                background-color: #e9ecef;
                border-top: 1px solid #dee2e6;
            }
            
            QMenuBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
            
            QMenuBar::item {
                padding: 8px 16px;
            }
            
            QMenuBar::item:selected {
                background-color: #e9ecef;
            }
        """)

def main():
    """Main application entry point"""
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Civic Engagement Platform")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Civic Engagement Foundation")
    
    # Set application icon (if available)
    # app.setWindowIcon(QIcon("icon.png"))
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start application event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

# Export main class for use in other modules
__all__ = ['MainWindow', 'main']