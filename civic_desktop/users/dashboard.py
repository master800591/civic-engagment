"""
USER DASHBOARD - Role-based user interface and civic participation hub
Displays user information, available actions, and civic engagement tools
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
        QLabel, QPushButton, QGroupBox, QFrame, QScrollArea,
        QProgressBar, QListWidget, QListWidgetItem, QTabWidget,
        QMessageBox, QTextEdit, QSpacerItem, QSizePolicy
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
    from PyQt5.QtGui import QFont, QPalette, QPixmap, QIcon
    PYQT_AVAILABLE = True
except ImportError:
    print("Warning: PyQt5 not available. GUI functionality disabled.")
    PYQT_AVAILABLE = False

# Import modules
sys.path.append(str(Path(__file__).parent.parent))
from users.auth import SessionManager, RoleChecker, AuthenticationService
from users.crypto_integration import UserCryptoIntegration

class UserDashboard(QWidget if PYQT_AVAILABLE else object):
    """Main user dashboard with role-based interface"""
    
    if PYQT_AVAILABLE:
        logout_requested = pyqtSignal()
        action_requested = pyqtSignal(str, dict)  # action_name, parameters
    
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        
        # Initialize services
        self.auth_service = AuthenticationService()
        self.crypto_service = UserCryptoIntegration()
        
        # UI state
        self.current_user = None
        
        # Setup UI
        self.init_ui()
        self.setup_styles()
        
        # Update timer for dynamic content
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_dashboard)
        self.update_timer.start(30000)  # Update every 30 seconds
        
        # Initial load
        self.refresh_dashboard()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Civic Engagement Dashboard")
        self.setMinimumSize(800, 600)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        header_layout = self.create_header_section()
        main_layout.addLayout(header_layout)
        
        # Content area with tabs
        self.content_tabs = QTabWidget()
        self.setup_content_tabs()
        main_layout.addWidget(self.content_tabs)
        
        self.setLayout(main_layout)
    
    def create_header_section(self):
        """Create dashboard header with user info and logout"""
        layout = QHBoxLayout()
        
        # User info section
        user_info_layout = QVBoxLayout()
        
        self.welcome_label = QLabel("Welcome to Civic Engagement Platform")
        self.welcome_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.welcome_label.setStyleSheet("color: #2c3e50;")
        
        self.user_info_label = QLabel("Loading user information...")
        self.user_info_label.setFont(QFont("Arial", 11))
        self.user_info_label.setStyleSheet("color: #7f8c8d;")
        
        user_info_layout.addWidget(self.welcome_label)
        user_info_layout.addWidget(self.user_info_label)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setMinimumHeight(35)
        self.refresh_button.clicked.connect(self.refresh_dashboard)
        
        self.logout_button = QPushButton("🚪 Logout")
        self.logout_button.setMinimumHeight(35)
        self.logout_button.clicked.connect(self.on_logout_clicked)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.logout_button)
        
        layout.addLayout(user_info_layout, 3)
        layout.addLayout(buttons_layout, 1)
        
        return layout
    
    def setup_content_tabs(self):
        """Setup main content tabs"""
        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.content_tabs.addTab(self.overview_tab, "🏠 Overview")
        
        # Actions tab
        self.actions_tab = self.create_actions_tab()
        self.content_tabs.addTab(self.actions_tab, "⚡ Actions")
        
        # Profile tab
        self.profile_tab = self.create_profile_tab()
        self.content_tabs.addTab(self.profile_tab, "👤 Profile")
        
        # Activity tab
        self.activity_tab = self.create_activity_tab()
        self.content_tabs.addTab(self.activity_tab, "📊 Activity")
        
        # Crypto tab
        self.crypto_tab = self.create_crypto_tab()
        self.content_tabs.addTab(self.crypto_tab, "💰 Crypto")
    
    def create_overview_tab(self):
        """Create overview tab with role information and quick stats"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Role information group
        role_group = QGroupBox("🏛️ Your Role in Civic Governance")
        role_layout = QVBoxLayout()
        
        self.role_description_label = QLabel("Loading role information...")
        self.role_description_label.setWordWrap(True)
        self.role_description_label.setFont(QFont("Arial", 11))
        
        self.permissions_list = QListWidget()
        self.permissions_list.setMaximumHeight(150)
        
        role_layout.addWidget(self.role_description_label)
        role_layout.addWidget(QLabel("Available Permissions:"))
        role_layout.addWidget(self.permissions_list)
        role_group.setLayout(role_layout)
        
        # Quick stats group
        stats_group = QGroupBox("📊 Platform Participation")
        stats_layout = QGridLayout()
        
        self.participation_stats = {}
        stat_labels = [
            ("Votes Cast", "votes_cast"),
            ("Debates Joined", "debates_joined"),
            ("Proposals Made", "proposals_made"),
            ("Community Score", "community_score")
        ]
        
        for i, (label, key) in enumerate(stat_labels):
            row = i // 2
            col = (i % 2) * 2
            
            stat_label = QLabel(label)
            stat_label.setFont(QFont("Arial", 10, QFont.Bold))
            
            stat_value = QLabel("--")
            stat_value.setFont(QFont("Arial", 14, QFont.Bold))
            stat_value.setStyleSheet("color: #3498db;")
            stat_value.setAlignment(Qt.AlignCenter)
            
            stats_layout.addWidget(stat_label, row, col)
            stats_layout.addWidget(stat_value, row, col + 1)
            
            self.participation_stats[key] = stat_value
        
        stats_group.setLayout(stats_layout)
        
        # Recent activity group
        activity_group = QGroupBox("🕒 Recent Activity")
        activity_layout = QVBoxLayout()
        
        self.recent_activity_list = QListWidget()
        self.recent_activity_list.setMaximumHeight(200)
        
        activity_layout.addWidget(self.recent_activity_list)
        activity_group.setLayout(activity_layout)
        
        layout.addWidget(role_group)
        layout.addWidget(stats_group)
        layout.addWidget(activity_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_actions_tab(self):
        """Create actions tab with available civic actions"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Actions grid
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout()
        
        self.action_buttons = {}
        
        # Define all possible actions with descriptions
        all_actions = {
            'vote': {
                'title': '🗳️ Vote',
                'description': 'Participate in elections and referendums',
                'permission': 'vote'
            },
            'debate': {
                'title': '💬 Join Debates',
                'description': 'Engage in civic discussions and policy debates',
                'permission': 'debate'
            },
            'petition': {
                'title': '📝 Create Petition',
                'description': 'Start citizen initiatives and petitions',
                'permission': 'petition'
            },
            'appeal': {
                'title': '⚖️ File Appeal',
                'description': 'Appeal moderation decisions and governance actions',
                'permission': 'appeal'
            },
            'legislate': {
                'title': '🏛️ Create Legislation',
                'description': 'Propose new laws and policy changes',
                'permission': 'legislate'
            },
            'budget': {
                'title': '💰 Budget Authority',
                'description': 'Review and approve budget allocations',
                'permission': 'budget'
            },
            'moderate': {
                'title': '🛡️ Moderate Content',
                'description': 'Review flagged content and community standards',
                'permission': 'moderate'
            },
            'veto': {
                'title': '🚫 Constitutional Veto',
                'description': 'Review legislation for constitutional compliance',
                'permission': 'veto'
            },
            'interpret': {
                'title': '📖 Constitutional Interpretation',
                'description': 'Provide constitutional guidance and interpretation',
                'permission': 'interpret'
            },
            'emergency': {
                'title': '🚨 Emergency Powers',
                'description': 'Exercise emergency governance authority',
                'permission': 'emergency_power'
            }
        }
        
        # Create action buttons in grid
        row, col = 0, 0
        for action_key, action_info in all_actions.items():
            action_button = self.create_action_button(action_key, action_info)
            scroll_layout.addWidget(action_button, row, col)
            
            col += 1
            if col >= 3:  # 3 columns
                col = 0
                row += 1
        
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab
    
    def create_action_button(self, action_key: str, action_info: Dict[str, str]) -> QWidget:
        """Create an action button widget"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setMinimumHeight(120)
        widget.setMaximumWidth(200)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(action_info['title'])
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        # Description
        desc_label = QLabel(action_info['description'])
        desc_label.setFont(QFont("Arial", 9))
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #7f8c8d;")
        
        # Action button
        button = QPushButton("Open")
        button.clicked.connect(lambda: self.on_action_clicked(action_key))
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(button)
        
        widget.setLayout(layout)
        
        # Store references
        self.action_buttons[action_key] = {
            'widget': widget,
            'button': button,
            'permission': action_info['permission']
        }
        
        return widget
    
    def create_profile_tab(self):
        """Create profile tab with user information"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Profile information group
        profile_group = QGroupBox("👤 Profile Information")
        profile_layout = QFormLayout()
        
        self.profile_labels = {}
        profile_fields = [
            ("Full Name", "full_name"),
            ("Email", "email"),
            ("Role", "role"),
            ("Location", "location"),
            ("Member Since", "member_since"),
            ("Last Login", "last_login"),
            ("Verification Status", "verification_status")
        ]
        
        for label_text, key in profile_fields:
            value_label = QLabel("--")
            value_label.setFont(QFont("Arial", 11))
            profile_layout.addRow(f"{label_text}:", value_label)
            self.profile_labels[key] = value_label
        
        profile_group.setLayout(profile_layout)
        
        # Security information group
        security_group = QGroupBox("🔐 Security & Keys")
        security_layout = QFormLayout()
        
        self.security_labels = {}
        security_fields = [
            ("RSA Key Status", "rsa_key_status"),
            ("Blockchain Address", "blockchain_address"),
            ("Key Fingerprint", "key_fingerprint"),
            ("Account Security", "account_security")
        ]
        
        for label_text, key in security_fields:
            value_label = QLabel("--")
            value_label.setFont(QFont("Arial", 11))
            security_layout.addRow(f"{label_text}:", value_label)
            self.security_labels[key] = value_label
        
        security_group.setLayout(security_layout)
        
        # Profile actions
        actions_group = QGroupBox("⚙️ Account Actions")
        actions_layout = QHBoxLayout()
        
        change_password_button = QPushButton("Change Password")
        change_password_button.clicked.connect(self.on_change_password_clicked)
        
        update_profile_button = QPushButton("Update Profile")
        update_profile_button.clicked.connect(self.on_update_profile_clicked)
        
        backup_keys_button = QPushButton("Backup Keys")
        backup_keys_button.clicked.connect(self.on_backup_keys_clicked)
        
        actions_layout.addWidget(change_password_button)
        actions_layout.addWidget(update_profile_button)
        actions_layout.addWidget(backup_keys_button)
        actions_layout.addStretch()
        
        actions_group.setLayout(actions_layout)
        
        layout.addWidget(profile_group)
        layout.addWidget(security_group)
        layout.addWidget(actions_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_activity_tab(self):
        """Create activity tab with user's civic engagement history"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Activity summary
        summary_group = QGroupBox("📈 Activity Summary")
        summary_layout = QGridLayout()
        
        self.activity_stats = {}
        activity_metrics = [
            ("This Week", "week_activity"),
            ("This Month", "month_activity"),
            ("This Year", "year_activity"),
            ("All Time", "total_activity")
        ]
        
        for i, (period, key) in enumerate(activity_metrics):
            period_label = QLabel(period)
            period_label.setFont(QFont("Arial", 10, QFont.Bold))
            
            count_label = QLabel("0")
            count_label.setFont(QFont("Arial", 14, QFont.Bold))
            count_label.setStyleSheet("color: #27ae60;")
            count_label.setAlignment(Qt.AlignCenter)
            
            summary_layout.addWidget(period_label, 0, i)
            summary_layout.addWidget(count_label, 1, i)
            
            self.activity_stats[key] = count_label
        
        summary_group.setLayout(summary_layout)
        
        # Activity history
        history_group = QGroupBox("📜 Recent Activity History")
        history_layout = QVBoxLayout()
        
        self.activity_history_list = QListWidget()
        history_layout.addWidget(self.activity_history_list)
        
        history_group.setLayout(history_layout)
        
        layout.addWidget(summary_group)
        layout.addWidget(history_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_crypto_tab(self):
        """Create crypto portfolio tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Wallet overview group
        wallet_group = QGroupBox("💳 CivicCoin Wallet")
        wallet_layout = QVBoxLayout()
        
        # Balance display
        self.balance_label = QLabel("Loading balance...")
        self.balance_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.balance_label.setStyleSheet("color: #27ae60; font-size: 18px;")
        
        # Address display
        self.address_label = QLabel("Wallet Address: Loading...")
        self.address_label.setFont(QFont("Courier", 9))
        self.address_label.setStyleSheet("color: #7f8c8d; background-color: #ecf0f1; padding: 5px; border-radius: 3px;")
        self.address_label.setWordWrap(True)
        
        wallet_layout.addWidget(self.balance_label)
        wallet_layout.addWidget(self.address_label)
        wallet_group.setLayout(wallet_layout)
        
        # Portfolio group
        portfolio_group = QGroupBox("📊 Portfolio Overview")
        portfolio_layout = QVBoxLayout()
        
        # Portfolio stats
        self.portfolio_stats_layout = QGridLayout()
        
        # Transaction history group
        history_group = QGroupBox("📋 Recent Transactions")
        history_layout = QVBoxLayout()
        
        self.transaction_history_list = QListWidget()
        self.transaction_history_list.setMaximumHeight(200)
        history_layout.addWidget(self.transaction_history_list)
        
        history_group.setLayout(history_layout)
        
        # Quick actions group
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_layout = QHBoxLayout()
        
        self.send_tokens_button = QPushButton("📤 Send Tokens")
        self.send_tokens_button.setMinimumHeight(40)
        self.send_tokens_button.clicked.connect(self.on_send_tokens_clicked)
        
        self.exchange_button = QPushButton("🔄 Exchange")
        self.exchange_button.setMinimumHeight(40)
        self.exchange_button.clicked.connect(self.on_exchange_clicked)
        
        self.pool_button = QPushButton("🏊 Pool & Earn")
        self.pool_button.setMinimumHeight(40)
        self.pool_button.clicked.connect(self.on_pool_clicked)
        
        self.rewards_button = QPushButton("🎁 Claim Rewards")
        self.rewards_button.setMinimumHeight(40)
        self.rewards_button.clicked.connect(self.on_rewards_clicked)
        
        actions_layout.addWidget(self.send_tokens_button)
        actions_layout.addWidget(self.exchange_button)
        actions_layout.addWidget(self.pool_button)
        actions_layout.addWidget(self.rewards_button)
        
        actions_group.setLayout(actions_layout)
        
        portfolio_layout.addLayout(self.portfolio_stats_layout)
        portfolio_group.setLayout(portfolio_layout)
        
        layout.addWidget(wallet_group)
        layout.addWidget(portfolio_group)
        layout.addWidget(history_group)
        layout.addWidget(actions_group)
        
        tab.setLayout(layout)
        return tab
    
    def setup_styles(self):
        """Setup consistent styling"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: Arial, sans-serif;
            }
            
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #ecf0f1;
                border: 1px solid #ddd;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
            }
            
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                background-color: #3498db;
                color: white;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            
            QFrame {
                border-radius: 5px;
                background-color: white;
                padding: 10px;
            }
            
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
        """)
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        self.current_user = SessionManager.get_current_user()
        
        if not self.current_user:
            self.logout_requested.emit()
            return
        
        # Update header
        self.update_header()
        
        # Update role information
        self.update_role_info()
        
        # Update available actions
        self.update_available_actions()
        
        # Update profile information
        self.update_profile_info()
        
        # Update activity data
        self.update_activity_info()
        
        # Update crypto data
        self.update_crypto_info()
    
    def update_header(self):
        """Update header with current user info"""
        if self.current_user:
            first_name = self.current_user.get('first_name', 'User')
            role = self.current_user.get('role', 'contract_member')
            self.welcome_label.setText(f"Welcome back, {first_name}!")
            
            role_display = role.replace('contract_', '').replace('_', ' ').title()
            last_login = self.current_user.get('last_activity', 'Unknown')
            
            self.user_info_label.setText(f"Role: {role_display} | Last Activity: {last_login}")
    
    def update_role_info(self):
        """Update role information and permissions"""
        if not self.current_user:
            return
        
        role = self.current_user.get('role', 'contract_member')
        
        # Role descriptions
        role_descriptions = {
            'contract_member': 'Contract Member - You have fundamental democratic rights including voting, debating, petitioning, and appealing decisions.',
            'contract_representative': 'Contract Representative - You represent citizens in the legislature with powers to create legislation, control budgets, and impeach officials.',
            'contract_senator': 'Contract Senator - You serve in the deliberative upper house with authority to review legislation, confirm appointments, and override Elder vetoes.',
            'contract_elder': 'Contract Elder - You are a constitutional guardian with veto power over unconstitutional legislation and authority to interpret governance contracts.',
            'contract_founder': 'Contract Founder - You have emergency powers and constitutional amendment authority as a platform architect.'
        }
        
        description = role_descriptions.get(role, 'Unknown role')
        self.role_description_label.setText(description)
        
        # Update permissions list
        self.permissions_list.clear()
        available_actions = RoleChecker.get_available_actions()
        
        for action in available_actions:
            item = QListWidgetItem(f"✅ {action.replace('_', ' ').title()}")
            self.permissions_list.addItem(item)
    
    def update_available_actions(self):
        """Update which actions are available to the user"""
        for action_key, action_data in self.action_buttons.items():
            permission = action_data['permission']
            has_permission = SessionManager.has_permission(permission)
            
            # Enable/disable action
            action_data['button'].setEnabled(has_permission)
            action_data['widget'].setEnabled(has_permission)
            
            # Visual feedback
            if has_permission:
                action_data['widget'].setStyleSheet("QFrame { background-color: white; }")
            else:
                action_data['widget'].setStyleSheet("QFrame { background-color: #f5f5f5; color: #999; }")
    
    def update_profile_info(self):
        """Update profile information"""
        if not self.current_user:
            return
        
        # Update profile fields
        self.profile_labels['full_name'].setText(f"{self.current_user.get('first_name', '')} {self.current_user.get('last_name', '')}")
        self.profile_labels['email'].setText(self.current_user.get('email', '--'))
        self.profile_labels['role'].setText(self.current_user.get('role', '--').replace('contract_', '').replace('_', ' ').title())
        
        location = f"{self.current_user.get('city', '')}, {self.current_user.get('state', '')}, {self.current_user.get('country', '')}"
        self.profile_labels['location'].setText(location)
        
        created_at = self.current_user.get('created_at', '')
        if created_at:
            try:
                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                self.profile_labels['member_since'].setText(date_obj.strftime('%B %d, %Y'))
            except:
                self.profile_labels['member_since'].setText(created_at)
        
        last_login = self.current_user.get('last_login', '--')
        self.profile_labels['last_login'].setText(last_login)
        
        verification_status = self.current_user.get('verification_status', 'Unknown')
        self.profile_labels['verification_status'].setText(verification_status.title())
        
        # Update security fields
        self.security_labels['rsa_key_status'].setText("Generated" if self.current_user.get('rsa_public_key') else "Not Generated")
        self.security_labels['blockchain_address'].setText(self.current_user.get('blockchain_address', '--'))
        
        # Placeholder values - would come from key manager in real implementation
        self.security_labels['key_fingerprint'].setText("abc123...")
        self.security_labels['account_security'].setText("Secure")
    
    def update_activity_info(self):
        """Update activity statistics and history"""
        # Placeholder data - would come from blockchain/activity tracking in real implementation
        self.participation_stats['votes_cast'].setText("12")
        self.participation_stats['debates_joined'].setText("5") 
        self.participation_stats['proposals_made'].setText("2")
        self.participation_stats['community_score'].setText("87")
        
        # Activity stats
        self.activity_stats['week_activity'].setText("8")
        self.activity_stats['month_activity'].setText("23")
        self.activity_stats['year_activity'].setText("156")
        self.activity_stats['total_activity'].setText("203")
        
        # Recent activity
        self.recent_activity_list.clear()
        recent_activities = [
            "Voted on City Budget Proposal - 2 hours ago",
            "Joined Climate Policy Debate - 1 day ago", 
            "Created Petition for Park Improvement - 3 days ago",
            "Voted in Representative Election - 1 week ago"
        ]
        
        for activity in recent_activities:
            self.recent_activity_list.addItem(activity)
        
        # Activity history
        self.activity_history_list.clear()
        for activity in recent_activities:
            self.activity_history_list.addItem(activity)
    
    def on_action_clicked(self, action_key: str):
        """Handle action button clicks"""
        if not SessionManager.has_permission(self.action_buttons[action_key]['permission']):
            QMessageBox.warning(self, "Permission Denied", f"You don't have permission to perform this action: {action_key}")
            return
        
        self.action_requested.emit(action_key, {'user': self.current_user})
    
    def on_logout_clicked(self):
        """Handle logout button click"""
        reply = QMessageBox.question(
            self,
            "Logout Confirmation",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()
    
    def on_change_password_clicked(self):
        """Handle change password action"""
        QMessageBox.information(self, "Change Password", "Password change functionality will be implemented in a future update.")
    
    def on_update_profile_clicked(self):
        """Handle update profile action"""
        QMessageBox.information(self, "Update Profile", "Profile update functionality will be implemented in a future update.")
    
    def on_backup_keys_clicked(self):
        """Handle backup keys action"""
        QMessageBox.information(self, "Backup Keys", "Key backup functionality will be implemented in a future update.")
    
    def update_crypto_info(self):
        """Update crypto tab with latest portfolio information"""
        if not self.current_user:
            return
        
        try:
            # Get crypto dashboard data
            crypto_data = self.crypto_service.get_user_crypto_dashboard(self.current_user['email'])
            
            if crypto_data:
                # Update balance
                balance = crypto_data.get('balance', 0)
                self.balance_label.setText(f"Balance: {balance:.6f} CVC")
                
                # Update wallet address
                address = crypto_data.get('address', 'N/A')
                if len(address) > 20:
                    display_address = f"{address[:10]}...{address[-10:]}"
                else:
                    display_address = address
                self.address_label.setText(f"Wallet Address: {display_address}")
                
                # Clear existing portfolio stats
                for i in reversed(range(self.portfolio_stats_layout.count())):
                    self.portfolio_stats_layout.itemAt(i).widget().setParent(None)
                
                # Add portfolio stats
                row = 0
                
                # Total value
                total_value = crypto_data.get('total_value', balance)
                total_label = QLabel("Total Portfolio Value:")
                total_value_label = QLabel(f"{total_value:.6f} CVC")
                total_value_label.setStyleSheet("font-weight: bold; color: #27ae60;")
                self.portfolio_stats_layout.addWidget(total_label, row, 0)
                self.portfolio_stats_layout.addWidget(total_value_label, row, 1)
                row += 1
                
                # Pool positions
                if 'pool_positions' in crypto_data and crypto_data['pool_positions']:
                    pool_label = QLabel("Liquidity Pools:")
                    pool_count = len(crypto_data['pool_positions'])
                    pool_value_label = QLabel(f"{pool_count} pools")
                    self.portfolio_stats_layout.addWidget(pool_label, row, 0)
                    self.portfolio_stats_layout.addWidget(pool_value_label, row, 1)
                    row += 1
                
                # Rewards
                if 'rewards' in crypto_data and crypto_data['rewards']:
                    total_rewards = sum(crypto_data['rewards'].values())
                    rewards_label = QLabel("Pending Rewards:")
                    rewards_value_label = QLabel(f"{total_rewards:.6f} CVC")
                    rewards_value_label.setStyleSheet("color: #f39c12;")
                    self.portfolio_stats_layout.addWidget(rewards_label, row, 0)
                    self.portfolio_stats_layout.addWidget(rewards_value_label, row, 1)
                    row += 1
                
                # Update transaction history
                self.transaction_history_list.clear()
                transactions = crypto_data.get('transactions', [])
                
                if transactions:
                    # Show last 10 transactions
                    for tx in transactions[-10:]:
                        tx_type = tx.get('type', 'transfer')
                        amount = tx.get('amount', 0)
                        timestamp = tx.get('timestamp', 'Unknown')
                        
                        # Format transaction display
                        if tx_type == 'reward':
                            item_text = f"🎁 Reward: +{amount:.6f} CVC ({timestamp})"
                        elif tx_type == 'pool_deposit':
                            item_text = f"🏊 Pool Deposit: -{amount:.6f} CVC ({timestamp})"
                        elif tx_type == 'pool_withdraw':
                            item_text = f"🏊 Pool Withdraw: +{amount:.6f} CVC ({timestamp})"
                        else:
                            item_text = f"💸 Transfer: {amount:+.6f} CVC ({timestamp})"
                        
                        self.transaction_history_list.addItem(item_text)
                else:
                    self.transaction_history_list.addItem("No transactions found")
                    
            else:
                # No crypto data available
                self.balance_label.setText("Balance: Not available")
                self.address_label.setText("Wallet Address: Not created")
                self.transaction_history_list.clear()
                self.transaction_history_list.addItem("Crypto wallet not initialized")
                
        except Exception as e:
            print(f"Error updating crypto info: {e}")
            self.balance_label.setText("Balance: Error loading")
            self.address_label.setText("Wallet Address: Error loading")
    
    # Crypto event handlers
    def on_send_tokens_clicked(self):
        """Handle send tokens action"""
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please login first.")
            return
        
        # Show send tokens dialog (to be implemented)
        QMessageBox.information(self, "Send Tokens", "Send tokens functionality available. Implementation pending.")
    
    def on_exchange_clicked(self):
        """Handle exchange action"""
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please login first.")
            return
        
        # Show exchange dialog (to be implemented)
        QMessageBox.information(self, "Exchange", "Exchange functionality available with full order book and market rates.")
    
    def on_pool_clicked(self):
        """Handle pool action"""
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please login first.")
            return
        
        # Show pool dialog (to be implemented)
        QMessageBox.information(self, "Pool & Earn", "Liquidity pools and yield farming available. Join pools to earn rewards.")
    
    def on_rewards_clicked(self):
        """Handle rewards action"""
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please login first.")
            return
        
        try:
            # Get user rewards
            rewards_info = self.crypto_service.get_user_crypto_dashboard(self.current_user['email'])
            
            # Display rewards info
            if rewards_info and 'rewards' in rewards_info:
                rewards_text = f"Available Rewards:\n\n"
                for reward_type, amount in rewards_info['rewards'].items():
                    rewards_text += f"{reward_type}: {amount:.6f} CVC\n"
                
                QMessageBox.information(self, "Rewards", rewards_text)
            else:
                QMessageBox.information(self, "Rewards", "No rewards currently available.")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load rewards: {str(e)}")