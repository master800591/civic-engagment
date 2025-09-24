"""
GitHub Integration Tab - UI for GitHub integration features
Provides update checking, development status, and issue reporting
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTabWidget, QTextEdit, QLabel, QProgressBar,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QGroupBox, QScrollArea, QFrame, QSplitter,
                            QLineEdit, QComboBox, QMessageBox, QDialog,
                            QDialogButtonBox, QFormLayout, QApplication, QAbstractItemView)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QColor, QPalette, QDesktopServices

from ..github_integration.github_manager import GitHubIntegrationManager
from ..users.session import SessionManager


class GitHubOperationsWorker(QThread):
    """Background worker for GitHub operations"""
    operation_complete = pyqtSignal(str, object)  # operation_type, result
    def __init__(self, operation: str, github_manager: GitHubIntegrationManager, **kwargs: Any):
        super().__init__()
        self.operation = operation
        self.github_manager = github_manager
        self.kwargs = kwargs
    def run(self):
        try:
            if self.operation == 'check_updates':
                result = self.github_manager.check_for_updates()
            elif self.operation == 'get_repo_info':
                result = self.github_manager.get_repository_info()
            elif self.operation == 'get_git_status':
                result = self.github_manager.get_git_status()
            elif self.operation == 'get_commits':
                result = self.github_manager.get_recent_commits(self.kwargs.get('limit', 10))
            elif self.operation == 'get_issues':
                result = self.github_manager.get_issues(
                    self.kwargs.get('state', 'open'), 
                    self.kwargs.get('limit', 10)
                )
            elif self.operation == 'get_pull_requests':
                result = self.github_manager.get_pull_requests(
                    self.kwargs.get('state', 'open'), 
                    self.kwargs.get('limit', 10)
                )
            elif self.operation == 'create_issue':
                result = self.github_manager.create_issue(
                    self.kwargs.get('title', ''),
                    self.kwargs.get('body', ''),
                    self.kwargs.get('labels', [])
                )
            else:
                result = {'error': f'Unknown operation: {self.operation}'}
            
            self.operation_complete.emit(self.operation, result)
            
        except Exception as e:
            error_result = {'error': f"An exception occurred in operation '{self.operation}': {str(e)}"}
            print(f"Worker error: {error_result}")
            self.operation_complete.emit(self.operation, error_result)


class IssueReportDialog(QDialog):
    """Dialog for reporting issues to GitHub"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report Issue to GitHub")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Brief description of the issue")
        form_layout.addRow("Issue Title:", self.title_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Detailed description of the issue, steps to reproduce, expected behavior, etc.")
        form_layout.addRow("Description:", self.description_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(['bug', 'enhancement', 'question', 'documentation', 'performance'])
        form_layout.addRow("Category:", self.category_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_issue_data(self):
        return {
            'title': self.title_edit.text().strip(),
            'body': self.description_edit.toPlainText().strip(),
            'labels': [self.category_combo.currentText()]
        }


class GitHubIntegrationTab(QWidget):
    """Main GitHub integration tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.github_manager = GitHubIntegrationManager()
        self.workers: Dict[str, GitHubOperationsWorker] = {}
        self.current_update_info: Dict[str, Any] = {}
        self.current_repo_info: Dict[str, Any] = {}
        self.current_issues: List[Dict[str, Any]] = []
        self.current_prs: List[Dict[str, Any]] = []
        self.repo_clone_url: Optional[str] = None
        self.repo_html_url: Optional[str] = None
        self.latest_release_url: Optional[str] = None
        self.init_ui()
        self.setup_auto_refresh()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🐙 GitHub Integration Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("🔄 Loading...")
        header_layout.addWidget(self.status_label)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh All")
        refresh_btn.clicked.connect(self.refresh_all_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Create tabbed interface
        self.tab_widget = QTabWidget()
        
        # Tab 1: Updates & Releases
        self.tab_widget.addTab(self.create_updates_tab(), "📦 Updates")
        
        # Tab 2: Repository Status
        self.tab_widget.addTab(self.create_repository_tab(), "📁 Repository")
        
        # Tab 3: Development Activity
        self.tab_widget.addTab(self.create_development_tab(), "💻 Development")
        
        # Tab 4: Issues & Pull Requests
        self.tab_widget.addTab(self.create_issues_tab(), "🐛 Issues & PRs")
        
        # Tab 5: Version Control
        self.tab_widget.addTab(self.create_version_control_tab(), "🔧 Version Control")
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
        
        # Start initial data load
        self.refresh_all_data()

    def update_updates_display(self, update_info: Dict[str, Any]):
        """Update the UI with update information."""
        if update_info.get('error'):
            self.update_status_label.setText(f"❌ Error")
            self.update_status_label.setToolTip(update_info['error'])
            self.update_details_text.setText(f"Could not check for updates.\n\nError: {update_info['error']}")
            self.download_btn.setEnabled(False)
            self.view_release_btn.setEnabled(False)
            return

        if update_info.get('has_updates'):
            self.update_status_label.setText(f"🆕 Update Available: {update_info['latest_version']}")
            self.update_status_label.setStyleSheet("color: green;")
            
            details = f"""
A new version of the platform is available.

Current Version: {update_info['current_version']}
Latest Version: {update_info['latest_version']}

Release Notes:
{update_info.get('release_notes', 'No release notes available.')}
            """
            self.update_details_text.setText(details)
            self.download_btn.setEnabled(True)
            self.view_release_btn.setEnabled(True)
            # Store release URL for the button
            self.latest_release_url = update_info.get('update_url')
        else:
            self.update_status_label.setText(f"✅ Up to date ({update_info['current_version']})")
            self.update_status_label.setStyleSheet("color: black;")
            self.update_details_text.setText("You are running the latest version of the platform.")
            self.download_btn.setEnabled(False)
            self.view_release_btn.setEnabled(False)

    def update_repository_display(self, repo_info: Dict[str, Any]):
        """Update the UI with repository information."""
        if repo_info.get('error'):
            self.repo_info_text.setText(f"Error fetching repository info: {repo_info['error']}")
            return

        self.current_repo_info = repo_info
        info = f"""
Name: {repo_info.get('name', 'N/A')}
Description: {repo_info.get('description', 'N/A')}
Stars: {repo_info.get('stars', 0)}
Forks: {repo_info.get('forks', 0)}
Open Issues: {repo_info.get('issues', 0)}
Language: {repo_info.get('language', 'N/A')}
Last Updated: {repo_info.get('last_updated', 'N/A')}
        """
        self.repo_info_text.setText(info.strip())
        self.repo_clone_url = repo_info.get('clone_url')
        self.repo_html_url = repo_info.get('url')

    def create_updates_tab(self) -> QWidget:
        """Create the updates and releases tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Update status
        update_group = QGroupBox("Update Status")
        update_layout = QVBoxLayout()
        
        self.update_status_label = QLabel("🔄 Checking for updates...")
        update_status_font = QFont()
        update_status_font.setPointSize(12)
        update_status_font.setBold(True)
        self.update_status_label.setFont(update_status_font)
        update_layout.addWidget(self.update_status_label)
        
        # Check for updates button
        check_updates_btn = QPushButton("🔍 Check for Updates")
        check_updates_btn.clicked.connect(self.check_for_updates)
        update_layout.addWidget(check_updates_btn)
        
        update_group.setLayout(update_layout)
        layout.addWidget(update_group)
        
        # Update details
        details_group = QGroupBox("Update Details")
        details_layout = QVBoxLayout()
        
        self.update_details_text = QTextEdit()
        self.update_details_text.setReadOnly(True)
        self.update_details_text.setMaximumHeight(300)
        details_layout.addWidget(self.update_details_text)
        
        # Update actions
        actions_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("📥 Download Update")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.download_update)
        actions_layout.addWidget(self.download_btn)
        
        self.view_release_btn = QPushButton("🌐 View on GitHub")
        self.view_release_btn.setEnabled(False)
        self.view_release_btn.clicked.connect(self.view_release_on_github)
        actions_layout.addWidget(self.view_release_btn)
        
        actions_layout.addStretch()
        details_layout.addLayout(actions_layout)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Version history
        history_group = QGroupBox("Version Information")
        history_layout = QVBoxLayout()
        
        self.version_info_text = QTextEdit()
        self.version_info_text.setReadOnly(True)
        self.version_info_text.setMaximumHeight(200)
        history_layout.addWidget(self.version_info_text)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_repository_tab(self) -> QWidget:
        """Create the repository status tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Repository information
        repo_group = QGroupBox("Repository Information")
        repo_layout = QVBoxLayout()
        
        self.repo_info_text = QTextEdit()
        self.repo_info_text.setReadOnly(True)
        self.repo_info_text.setMaximumHeight(250)
        repo_layout.addWidget(self.repo_info_text)
        
        # Repository actions
        repo_actions_layout = QHBoxLayout()
        
        view_repo_btn = QPushButton("🌐 View Repository")
        view_repo_btn.clicked.connect(self.view_repository_on_github)
        repo_actions_layout.addWidget(view_repo_btn)
        
        clone_btn = QPushButton("📋 Copy Clone URL")
        clone_btn.clicked.connect(self.copy_clone_url)
        repo_actions_layout.addWidget(clone_btn)
        
        repo_actions_layout.addStretch()
        repo_layout.addLayout(repo_actions_layout)
        
        repo_group.setLayout(repo_layout)
        layout.addWidget(repo_group)
        
        # Git status
        git_group = QGroupBox("Local Git Status")
        git_layout = QVBoxLayout()
        
        self.git_status_text = QTextEdit()
        self.git_status_text.setReadOnly(True)
        self.git_status_text.setMaximumHeight(200)
        git_layout.addWidget(self.git_status_text)
        
        # Git actions
        git_actions_layout = QHBoxLayout()
        
        init_git_btn = QPushButton("🔧 Initialize Git Repository")
        init_git_btn.clicked.connect(self.initialize_git_repository)
        git_actions_layout.addWidget(init_git_btn)
        
        refresh_git_btn = QPushButton("🔄 Refresh Git Status")
        refresh_git_btn.clicked.connect(self.refresh_git_status)
        git_actions_layout.addWidget(refresh_git_btn)
        
        git_actions_layout.addStretch()
        git_layout.addLayout(git_actions_layout)
        
        git_group.setLayout(git_layout)
        layout.addWidget(git_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_development_tab(self) -> QWidget:
        """Create the development activity tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Recent commits
        commits_group = QGroupBox("Recent Commits")
        commits_layout = QVBoxLayout()
        
        self.commits_table = QTableWidget()
        self.commits_table.setColumnCount(4)
        self.commits_table.setHorizontalHeaderLabels(['SHA', 'Message', 'Author', 'Date'])
        self.commits_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.commits_table.setMaximumHeight(200)
        # Make commits table read-only to prevent editing of reports
        self.commits_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.commits_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        commits_layout.addWidget(self.commits_table)
        
        refresh_commits_btn = QPushButton("🔄 Refresh Commits")
        refresh_commits_btn.clicked.connect(self.refresh_commits)
        commits_layout.addWidget(refresh_commits_btn)
        
        commits_group.setLayout(commits_layout)
        layout.addWidget(commits_group)
        
        # Development statistics
        stats_group = QGroupBox("Development Statistics")
        stats_layout = QVBoxLayout()
        
        self.dev_stats_text = QTextEdit()
        self.dev_stats_text.setReadOnly(True)
        self.dev_stats_text.setMaximumHeight(150)
        stats_layout.addWidget(self.dev_stats_text)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_issues_tab(self) -> QWidget:
        """Create the issues and pull requests tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Issues section
        issues_group = QGroupBox("Open Issues")
        issues_layout = QVBoxLayout()
        
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(4)
        self.issues_table.setHorizontalHeaderLabels(['#', 'Title', 'Author', 'Labels'])
        self.issues_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.issues_table.setMaximumHeight(200)
        # Make issues table read-only to prevent editing of reports
        self.issues_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.issues_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.issues_table.cellDoubleClicked.connect(self.open_issue_url)
        issues_layout.addWidget(self.issues_table)
        
        # Issue actions
        issue_actions_layout = QHBoxLayout()
        
        report_issue_btn = QPushButton("🐛 Report Issue")
        report_issue_btn.clicked.connect(self.report_issue)
        issue_actions_layout.addWidget(report_issue_btn)
        
        refresh_issues_btn = QPushButton("🔄 Refresh Issues")
        refresh_issues_btn.clicked.connect(self.refresh_issues)
        issue_actions_layout.addWidget(refresh_issues_btn)
        
        view_all_issues_btn = QPushButton("🌐 View All Issues")
        view_all_issues_btn.clicked.connect(self.view_all_issues)
        issue_actions_layout.addWidget(view_all_issues_btn)
        
        issue_actions_layout.addStretch()
        issues_layout.addLayout(issue_actions_layout)
        
        issues_group.setLayout(issues_layout)
        layout.addWidget(issues_group)
        
        # Pull requests section
        prs_group = QGroupBox("Open Pull Requests")
        prs_layout = QVBoxLayout()
        
        self.prs_table = QTableWidget()
        self.prs_table.setColumnCount(4)
        self.prs_table.setHorizontalHeaderLabels(['#', 'Title', 'Author', 'Branch'])
        self.prs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prs_table.setMaximumHeight(200)
        # Make pull requests table read-only to prevent editing of reports
        self.prs_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.prs_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.prs_table.cellDoubleClicked.connect(self.open_pr_url)
        prs_layout.addWidget(self.prs_table)
        
        refresh_prs_btn = QPushButton("🔄 Refresh Pull Requests")
        refresh_prs_btn.clicked.connect(self.refresh_pull_requests)
        prs_layout.addWidget(refresh_prs_btn)
        
        prs_group.setLayout(prs_layout)
        layout.addWidget(prs_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_version_control_tab(self) -> QWidget:
        """Create the version control tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Git configuration
        config_group = QGroupBox("Git Configuration")
        config_layout = QVBoxLayout()
        
        self.git_config_text = QTextEdit()
        self.git_config_text.setReadOnly(True)
        self.git_config_text.setMaximumHeight(150)
        config_layout.addWidget(self.git_config_text)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # GitHub token configuration
        token_group = QGroupBox("GitHub Token Configuration")
        token_layout = QVBoxLayout()
        
        token_info_label = QLabel("""
To access private repositories and create issues, you can configure a GitHub Personal Access Token.
This is optional for public repository access.
        """)
        token_layout.addWidget(token_info_label)
        
        token_form_layout = QHBoxLayout()
        token_form_layout.addWidget(QLabel("GitHub Token:"))
        
        self.token_edit = QLineEdit()
        self.token_edit.setEchoMode(QLineEdit.Password)
        self.token_edit.setPlaceholderText("Enter GitHub Personal Access Token (optional)")
        token_form_layout.addWidget(self.token_edit)
        
        save_token_btn = QPushButton("💾 Save Token")
        save_token_btn.clicked.connect(self.save_github_token)
        token_form_layout.addWidget(save_token_btn)
        
        token_layout.addLayout(token_form_layout)
        
        token_group.setLayout(token_layout)
        layout.addWidget(token_group)
        
        # Repository setup
        setup_group = QGroupBox("Repository Setup")
        setup_layout = QVBoxLayout()
        
        setup_info_text = QTextEdit()
        setup_info_text.setReadOnly(True)
        setup_info_text.setPlainText("""
Repository Setup Instructions:

1. Initialize Git Repository: Click 'Initialize Git Repository' if not already a git repo
2. Configure GitHub Token: Add your GitHub Personal Access Token for full functionality
3. Set Remote Origin: Configure the remote repository URL for synchronization
4. Check for Updates: Use the Updates tab to check for new releases

GitHub Token Permissions Needed:
• repo (for private repositories)
• read:org (for organization repositories) 
• read:user (for user information)

Generate token at: https://github.com/settings/tokens
        """)
        setup_layout.addWidget(setup_info_text)
        
        setup_group.setLayout(setup_layout)
        layout.addWidget(setup_group)
        
        widget.setLayout(layout)
        return widget
    
    def setup_auto_refresh(self):
        """Setup automatic refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_update_status)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes
    
    def start_operation(self, operation: str, **kwargs: Any):
        """Start a background GitHub operation"""
        if operation in self.workers and self.workers[operation].isRunning():
            return
        
        worker = GitHubOperationsWorker(operation, self.github_manager, **kwargs)
        worker.operation_complete.connect(self.handle_operation_result)
        self.workers[operation] = worker
        worker.start()
    
    def handle_operation_result(self, operation: str, result: Any):
        """Handle completed GitHub operation"""
        try:
            # Handle errors first
            if isinstance(result, dict) and result.get('error'):
                self.status_label.setText(f"❌ Error in {operation}")
                print(f"Error in operation '{operation}': {result.get('error')}")
                # Optionally display error in the relevant UI part
                if operation == 'check_updates':
                    self.update_updates_display(result)
                elif operation == 'get_repo_info':
                    self.update_repository_display(result)
                return

            # Handle success
            self.status_label.setText("✅ Ready")
            if operation == 'check_updates':
                self.update_updates_display(result)
            elif operation == 'get_repo_info':
                self.update_repository_display(result)
            elif operation == 'get_git_status':
                self.update_git_status_display(result)
            elif operation == 'get_commits':
                self.update_commits_display(result)
            elif operation == 'get_issues':
                self.update_issues_display(result)
                self.current_issues = result
            elif operation == 'get_pull_requests':
                self.update_prs_display(result)
                self.current_prs = result
            elif operation == 'create_issue':
                self.handle_issue_creation_result(result)

        except Exception as e:
            print(f"Error handling operation result for '{operation}': {e}")
            self.status_label.setText(f"❌ UI Error")

    def update_git_status_display(self, git_status: Dict[str, Any]):
        """Update the UI with git status information."""
        if git_status.get('error'):
            self.git_status_text.setText(f"Error fetching git status: {git_status['error']}")
            return

        status = f"""
Branch: {git_status.get('current_branch', 'unknown')}
Changes: {'Yes' if git_status.get('has_changes') else 'No'}
Remote: {'Connected' if git_status.get('has_remote') else 'Not connected'}
"""
        if git_status.get('ahead') is not None:
            status += f"Ahead: {git_status['ahead']} commits\n"
        if git_status.get('behind') is not None:
            status += f"Behind: {git_status['behind']} commits\n"
        
        self.git_status_text.setText(status.strip())

    def update_commits_display(self, commits: List[Dict[str, Any]]):
        """Update the UI with recent commits."""
        self.commits_table.setRowCount(0)
        if not commits:
            return
        
        self.commits_table.setRowCount(len(commits))
        for row, commit in enumerate(commits):
            self.commits_table.setItem(row, 0, QTableWidgetItem(commit.get('sha', '')))
            self.commits_table.setItem(row, 1, QTableWidgetItem(commit.get('message', '')))
            self.commits_table.setItem(row, 2, QTableWidgetItem(commit.get('author', '')))
            self.commits_table.setItem(row, 3, QTableWidgetItem(commit.get('date', '')))

    def update_issues_display(self, issues: List[Dict[str, Any]]):
        """Update the UI with open issues."""
        self.issues_table.setRowCount(0)
        if not issues:
            return

        self.issues_table.setRowCount(len(issues))
        for row, issue in enumerate(issues):
            self.issues_table.setItem(row, 0, QTableWidgetItem(str(issue.get('number', ''))))
            self.issues_table.setItem(row, 1, QTableWidgetItem(issue.get('title', '')))
            self.issues_table.setItem(row, 2, QTableWidgetItem(issue.get('author', '')))
            self.issues_table.setItem(row, 3, QTableWidgetItem(", ".join(issue.get('labels', []))))

    def update_prs_display(self, prs: List[Dict[str, Any]]):
        """Update the UI with open pull requests."""
        self.prs_table.setRowCount(0)
        if not prs:
            return
            
        self.prs_table.setRowCount(len(prs))
        for row, pr in enumerate(prs):
            self.prs_table.setItem(row, 0, QTableWidgetItem(str(pr.get('number', ''))))
            self.prs_table.setItem(row, 1, QTableWidgetItem(pr.get('title', '')))
            self.prs_table.setItem(row, 2, QTableWidgetItem(pr.get('author', '')))
            self.prs_table.setItem(row, 3, QTableWidgetItem(pr.get('head_branch', '')))

    def handle_issue_creation_result(self, result: Dict[str, Any]):
        """Handle the result of creating an issue."""
        if result.get('error'):
            QMessageBox.critical(self, "Issue Creation Failed", f"Could not create issue: {result['error']}")
        else:
            QMessageBox.information(self, "Issue Created", f"Successfully created issue #{result.get('issue_number')}")
            self.refresh_issues()

    def refresh_all_data(self):
        """Refresh all data from GitHub"""
        self.status_label.setText("🔄 Refreshing...")
        self.start_operation('check_updates')
        self.start_operation('get_repo_info')
        self.start_operation('get_git_status')
        self.start_operation('get_commits', limit=10)
        self.start_operation('get_issues', state='open', limit=10)
        self.start_operation('get_pull_requests', state='open', limit=10)
    
    def check_for_updates(self):
        """Check for updates"""
        self.update_status_label.setText("🔄 Checking for updates...")
        self.start_operation('check_updates')
    
    def refresh_update_status(self):
        """Refresh just the update status"""
        self.start_operation('check_updates')
    
    def refresh_git_status(self):
        """Refresh git status"""
        self.start_operation('get_git_status')
    
    def refresh_commits(self):
        """Refresh commits list"""
        self.start_operation('get_commits', limit=10)
    
    def refresh_issues(self):
        """Refresh issues list"""
        self.start_operation('get_issues', state='open', limit=10)
    
    def refresh_pull_requests(self):
        """Refresh pull requests list"""
        self.start_operation('get_pull_requests', state='open', limit=10)
    
    def view_repository_on_github(self):
        """View the repository on GitHub"""
        if self.repo_html_url:
            QDesktopServices.openUrl(QUrl(self.repo_html_url))

    def copy_clone_url(self):
        if self.repo_clone_url:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(self.repo_clone_url)
                QMessageBox.information(self, "Clone URL Copied", "Repository clone URL copied to clipboard.")

    def initialize_git_repository(self):
        # This is a potentially destructive action, confirm with user
        reply = QMessageBox.question(self, 'Initialize Git Repository',
                                     "Are you sure you want to initialize a new Git repository in the project root?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # For now, we just log this. Implementation would be in GitHubManager
            print("User confirmed Git initialization.")

    def open_issue_url(self, row: int, column: int):
        if self.current_issues and row < len(self.current_issues):
            issue_url = self.current_issues[row].get('url')
            if issue_url:
                QDesktopServices.openUrl(QUrl(issue_url))

    def open_pr_url(self, row: int, column: int):
        if self.current_prs and row < len(self.current_prs):
            pr_url = self.current_prs[row].get('url')
            if pr_url:
                QDesktopServices.openUrl(QUrl(pr_url))

    def view_all_issues(self):
        if self.repo_html_url:
            QDesktopServices.openUrl(QUrl(f"{self.repo_html_url}/issues"))

    def report_issue(self):
        dialog = IssueReportDialog(self)
        if dialog.exec_():
            issue_data: Dict[str, Any] = dialog.get_issue_data()
            if not issue_data['title'] or not issue_data['body']:
                QMessageBox.warning(self, "Incomplete Information", "Please provide a title and description for the issue.")
                return
            
            user = SessionManager.get_current_user()
            issue_data['body'] += f"\n\nReported by: {user['email'] if user else 'N/A'}"
            
            self.start_operation('create_issue', **issue_data)

    def save_github_token(self):
        token = self.token_edit.text().strip()
        if token:
            # In a real app, save this securely. For now, just update the manager instance.
            self.github_manager.github_token = token
            QMessageBox.information(self, "Token Saved", "GitHub token has been saved for this session.")
            self.token_edit.clear()
        else:
            QMessageBox.warning(self, "Empty Token", "Please enter a GitHub token.")

    def download_update(self):
        if not self.current_update_info.get('has_updates'):
            QMessageBox.information(self, "No Updates", "You are already on the latest version.")
            return

        assets = self.current_update_info.get('assets', [])
        if not assets:
            QMessageBox.warning(self, "No Assets", "The latest release has no downloadable assets.")
            return
        
        # For simplicity, assume the first asset is the one we want.
        asset_url = assets[0].get('browser_download_url')
        filename = assets[0].get('name')

        if asset_url and filename:
            # This would trigger a download in the manager. For now, just show info.
            QMessageBox.information(self, "Download Started", f"Downloading '{filename}' from {asset_url}")
            # self.github_manager.download_update(asset_url, filename) -> This would be a threaded operation
        else:
            QMessageBox.warning(self, "Download Error", "Could not find a valid download URL for the update.")

    def view_release_on_github(self):
        if self.latest_release_url:
            QDesktopServices.openUrl(QUrl(self.latest_release_url))