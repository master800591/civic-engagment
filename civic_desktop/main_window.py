from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
import json
from civic_desktop.users.registration import RegistrationForm
from civic_desktop.users.login import LoginForm
from civic_desktop.users.dashboard import UserDashboard
from civic_desktop.users.session import SessionManager
from civic_desktop.github_integration.update_notifier import setup_update_notifications
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Civic Engagement Platform")
        self.setGeometry(100, 100, 1000, 700)
        self.init_ui()
        
        # Start blockchain periodic timer
        from civic_desktop.blockchain.blockchain_timer import BlockchainTimer
        self.blockchain_timer = BlockchainTimer(self)
        
        # Initialize P2P networking
        self._init_p2p_networking()
        
        # Start session monitoring timer
        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self.check_session_status)
        self.session_timer.start(30000)  # Check every 30 seconds
        
        # Setup GitHub update notifications
        self.update_notifier = setup_update_notifications(self)
        
        # Document: All backend modules use environment-aware paths from ENV_CONFIG
        # To switch environments, reload config and refresh UI

    def _init_p2p_networking(self):
        """Initialize P2P networking system"""
        try:
            from civic_desktop.main import ENV_CONFIG
            from civic_desktop.blockchain.p2p_manager import initialize_p2p, start_p2p
            
            # Initialize P2P with configuration
            if initialize_p2p(ENV_CONFIG):
                start_p2p()
                print("✅ P2P networking initialized successfully")
            else:
                print("⚠️ P2P networking disabled or failed to initialize")
                
        except Exception as e:
            print(f"❌ P2P initialization error: {e}")

    def reload_config(self, config_path: str = None) -> None:
        """Reload ENV_CONFIG and update all backend modules and UI."""
        import civic_desktop.main as main_mod
        import importlib
        if config_path is not None:
            main_mod.CONFIG_PATH = config_path
        with open(str(main_mod.CONFIG_PATH), 'r', encoding='utf-8') as f:
            main_mod.ENV_CONFIG = json.load(f)
        # Refresh all tabs to use new config
        self.refresh_users_tab()
        # Optionally refresh other tabs if needed

    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self.users_tab(), "Log In")
        if not SessionManager.is_authenticated():
            self.tabs.addTab(self.registration_tab(), "Register")
        self.tabs.addTab(self.debates_tab(), "Debates")
        self.tabs.addTab(self.moderation_tab(), "Moderation")
        self.tabs.addTab(self.contracts_tab(), "Contracts")
        from civic_desktop.blockchain.blockchain_tab import BlockchainTab
        self.tabs.addTab(BlockchainTab(), "Blockchain")
        from civic_desktop.system_guide.guide_tab import SystemGuideTab
        self.tabs.addTab(SystemGuideTab(), "📖 System Guide")
        from civic_desktop.training.ui import TrainingTab
        self.training_tab = TrainingTab()
        self.tabs.addTab(self.training_tab, "🎓 Training")
        from civic_desktop.github_integration.github_tab import GitHubIntegrationTab
        self.github_tab = GitHubIntegrationTab()
        self.tabs.addTab(self.github_tab, "🐙 GitHub")
        from civic_desktop.blockchain.p2p_tab import P2PNetworkTab
        self.p2p_tab = P2PNetworkTab()
        self.tabs.addTab(self.p2p_tab, "📡 P2P Network")
        # Add Open Maps tab
        self.tabs.addTab(self.maps_tab(), "🗺️ Open Maps")
        # Add Reports tab for blockchain network reports
        self.tabs.addTab(self.reports_tab(), "📊 Reports")
        self.setCentralWidget(self.tabs)
    def reports_tab(self):
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QHeaderView
        from civic_desktop.blockchain.reports import NetworkReports
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(18)
        title = QLabel("<b>Blockchain Network Reports</b>")
        layout.addWidget(title)

        reports = NetworkReports()
        # Credit Ratio Report
        credit_ratio = reports.credit_ratio_report()
        layout.addWidget(QLabel(f"Credits per User: <b>{credit_ratio['credits_per_user']:.2f}</b> (Target: {credit_ratio['target_ratio']})"))
        layout.addWidget(QLabel(f"Inflation Status: <b>{credit_ratio['inflation_status']}</b>"))

        # Network Pool Report
        pool = reports.network_pool_report()
        layout.addWidget(QLabel(f"Network Pool: <b>{pool['total_pool']:.2f}</b> credits"))
        if pool['last_payout']:
            payout_info = pool['last_payout']
            layout.addWidget(QLabel(f"Last Payout: <b>{payout_info.get('amount', 'N/A')}</b> credits on <b>{payout_info.get('timestamp', 'N/A')}</b>"))

        # User Balances Table
        balances_report = reports.user_balances_report()
        balances = balances_report.get('users', [])
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["User", "Credits", "Role"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setRowCount(len(balances))
        for i, user in enumerate(balances):
            email = user.get('email', '')
            credits = str(user.get('credits', 0))
            # Try to get role if present, else blank
            role = user.get('role', '') if 'role' in user else ''
            table.setItem(i, 0, QTableWidgetItem(email))
            table.setItem(i, 1, QTableWidgetItem(credits))
            table.setItem(i, 2, QTableWidgetItem(role))
        layout.addWidget(QLabel("<b>User Balances</b>"))
        layout.addWidget(table)
        widget.setLayout(layout)
        return widget
    def registration_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        register_label = QLabel("<b>Register a new account</b>")
        register_form = RegistrationForm()
        layout.addWidget(register_label)
        layout.addWidget(register_form)
        widget.setLayout(layout)
        return widget

    def users_tab(self):
        # All backend operations use config-driven paths
        from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QFrame
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        # Only show dashboard if logged in
        if SessionManager.is_authenticated():
            self.dashboard = UserDashboard()
            layout.addWidget(self.dashboard)
            self.logout_button = QPushButton("Logout")
            self.logout_button.setStyleSheet("QPushButton { background: #d9534f; color: white; font-weight: bold; border-radius: 5px; padding: 6px 18px; } QPushButton:hover { background: #c9302c; }")
            self.logout_button.clicked.connect(self.handle_logout)
            self.logout_button.setFixedWidth(120)
            layout.addWidget(self.logout_button)
        else:
            # Center login box and add spacing
            from PyQt5.QtWidgets import QGroupBox, QSpacerItem, QSizePolicy
            layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
            login_group = QGroupBox()
            login_group.setTitle("Login to your account")
            login_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; border: 1px solid #bbb; border-radius: 10px; background: #f8f8ff; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
            login_layout = QVBoxLayout()
            login_layout.setSpacing(16)
            login_layout.setContentsMargins(30, 20, 30, 20)
            self.login_form = LoginForm(on_login=self.handle_login)
            login_layout.addWidget(self.login_form)
            login_group.setLayout(login_layout)
            layout.addWidget(login_group)
            layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        widget.setLayout(layout)
        self.users_tab_widget = widget
        self.users_tab_layout = layout
        return widget

    def debates_tab(self):
        # All backend operations use config-driven paths
        """Create the debates tab with full functionality"""
        from civic_desktop.debates.ui import DebateViewer
        return DebateViewer()
    
    def moderation_tab(self):
        # All backend operations use config-driven paths
        """Create the moderation tab with full functionality"""
        from civic_desktop.moderation.ui import ModerationDashboard
        return ModerationDashboard()

    def contracts_tab(self):
        """Create the contracts tab with contract management functionality"""
        # All backend operations use config-driven paths
        from civic_desktop.contracts.contract_ui import ContractManagementWidget
        return ContractManagementWidget()

    def maps_tab(self):
        from civic_desktop.maps.map_view import MapView
        from PyQt5.QtWidgets import QLineEdit, QPushButton, QLabel, QHBoxLayout
        widget = QWidget()
        layout = QVBoxLayout()
        # Address input
        address_layout = QHBoxLayout()
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter address or city...")
        self.geocode_button = QPushButton("Find on Map")
        self.save_button = QPushButton("Save Location")
        address_layout.addWidget(QLabel("Address:"))
        address_layout.addWidget(self.address_input)
        address_layout.addWidget(self.geocode_button)
        address_layout.addWidget(self.save_button)
        layout.addLayout(address_layout)
        # Map widget
        self.map_widget = MapView()
        layout.addWidget(self.map_widget)
        widget.setLayout(layout)
        # Connect buttons
        self.geocode_button.clicked.connect(self.handle_geocode)
        self.save_button.clicked.connect(self.handle_save_location)
        return widget

    def handle_geocode(self):
        import osmnx as ox
        address = self.address_input.text().strip()
        if address:
            try:
                loc = ox.geocode(address)
                lat, lon = loc[0], loc[1]
                self.map_widget.set_location(lat, lon, zoom_start=14)
                self.last_location = {'address': address, 'lat': lat, 'lon': lon}
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Geocoding Error", f"Could not find location: {e}")

    def handle_save_location(self):
        from PyQt5.QtWidgets import QMessageBox
        # Save to user profile (or contract, extend as needed)
        location = getattr(self, 'last_location', None)
        if location:
            # Example: Save to user session profile
            from civic_desktop.users.session import SessionManager
            user = SessionManager.get_current_user()
            if user:
                user['saved_location'] = location
                SessionManager.save_user(user)
                QMessageBox.information(self, "Location Saved", f"Location saved to your profile: {location['address']}")
            else:
                QMessageBox.warning(self, "Save Error", "No authenticated user to save location.")
        else:
            QMessageBox.warning(self, "Save Error", "No location selected to save.")

    def handle_login(self, user: dict) -> None:
        SessionManager.login(user)
        # Dashboard may not exist yet; refresh tabs to build it if authenticated
        self.refresh_users_tab()
        self.refresh_training_tab()

    def handle_logout(self) -> None:
        SessionManager.logout()
        # Dashboard may not exist if user wasn't on Users tab; just refresh tabs
        self.refresh_users_tab()
        self.refresh_training_tab()
    
    def check_session_status(self) -> None:
        """Check session status and handle timeouts"""
        if SessionManager.is_authenticated():
            session_info = SessionManager.get_session_info()
            
            # Warning when session is about to expire (5 minutes left)
            if session_info.get('session_expires_in_minutes', 0) <= 5:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self, 
                    "Session Expiring", 
                    f"Your session will expire in {session_info.get('session_expires_in_minutes', 0):.1f} minutes."
                )
            
            # Warning when inactive timeout is near (2 minutes left)
            if session_info.get('inactive_expires_in_minutes', 0) <= 2:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self, 
                    "Inactivity Warning", 
                    f"You will be logged out due to inactivity in {session_info.get('inactive_expires_in_minutes', 0):.1f} minutes."
                )
        
        # Cleanup expired sessions (this will logout if session is invalid)
        SessionManager.cleanup_expired_sessions()
        
        # If session was cleaned up, refresh the UI
        if not SessionManager.is_authenticated() and hasattr(self, 'dashboard'):
            self.refresh_users_tab()

    def refresh_users_tab(self) -> None:
        # Replace the Users tab and Registration tab with fresh ones reflecting login/logout state
        tabs = self.tabs
        users_index = 0  # Users tab is always first
        tabs.removeTab(users_index)
        tabs.insertTab(users_index, self.users_tab(), "Users")
        tabs.setCurrentIndex(users_index)
        # Registration tab is always second if not authenticated
        if not SessionManager.is_authenticated():
            if tabs.count() < 2 or tabs.tabText(1) != "Register":
                tabs.insertTab(1, self.registration_tab(), "Register")
        else:
            # Remove registration tab if present
            for i in range(tabs.count()):
                if tabs.tabText(i) == "Register":
                    tabs.removeTab(i)
                    break

    def refresh_training_tab(self) -> None:
        """Refresh the training tab to reflect current authentication status"""
        if hasattr(self, 'training_tab'):
            self.training_tab.refresh_ui()

    def make_tab(self, name: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"{name} module coming soon..."))
        widget.setLayout(layout)
        return widget


def run_gui():
    from PyQt5.QtCore import Qt, QCoreApplication
    from PyQt5.QtWebEngineWidgets import QWebEngineView  # Import early to fix initialization
    
    # Set Qt attributes before creating QApplication
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
