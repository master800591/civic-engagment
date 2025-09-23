"""
GitHub Update Notifier - System for automatic update checking and notification
Integrates with the main application to show update notifications
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QMessageBox, QDialog, QDialogButtonBox,
                            QTextEdit, QCheckBox, QGroupBox)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QDesktopServices

from .github_manager import GitHubIntegrationManager, check_for_platform_updates


class UpdateNotificationDialog(QDialog):
    """Dialog for showing update notifications"""
    
    def __init__(self, update_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.setWindowTitle("Platform Update Available")
        self.setModal(True)
        self.resize(600, 500)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        icon_label = QLabel("🆕")
        icon_font = QFont()
        icon_font.setPointSize(24)
        icon_label.setFont(icon_font)
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("Platform Update Available!")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Version info
        version_group = QGroupBox("Version Information")
        version_layout = QVBoxLayout()
        
        current_version = self.update_info.get('current_version', 'Unknown')
        latest_version = self.update_info.get('latest_version', 'Unknown')
        
        version_text = f"""
Current Version: {current_version}
Latest Version: {latest_version}
Release Date: {self.update_info.get('release_date', 'Unknown')}
        """
        
        version_label = QLabel(version_text)
        version_layout.addWidget(version_label)
        
        version_group.setLayout(version_layout)
        layout.addWidget(version_group)
        
        # Release notes
        if self.update_info.get('description'):
            notes_group = QGroupBox("What's New")
            notes_layout = QVBoxLayout()
            
            notes_text = QTextEdit()
            notes_text.setPlainText(self.update_info['description'])
            notes_text.setReadOnly(True)
            notes_text.setMaximumHeight(200)
            notes_layout.addWidget(notes_text)
            
            notes_group.setLayout(notes_layout)
            layout.addWidget(notes_group)
        
        # Reminder checkbox
        self.reminder_checkbox = QCheckBox("Remind me later (check again in 24 hours)")
        self.reminder_checkbox.setChecked(True)
        layout.addWidget(self.reminder_checkbox)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        download_btn = QPushButton("📥 Download Update")
        download_btn.setStyleSheet("QPushButton { background: #5cb85c; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px; }")
        download_btn.clicked.connect(self.download_update)
        button_layout.addWidget(download_btn)
        
        view_btn = QPushButton("🌐 View on GitHub")
        view_btn.clicked.connect(self.view_on_github)
        button_layout.addWidget(view_btn)
        
        skip_btn = QPushButton("Skip This Version")
        skip_btn.clicked.connect(self.skip_version)
        button_layout.addWidget(skip_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def download_update(self):
        """Open download page"""
        update_url = self.update_info.get('update_url')
        if update_url:
            QDesktopServices.openUrl(QUrl(update_url))
            self.accept()
    
    def view_on_github(self):
        """View release on GitHub"""
        update_url = self.update_info.get('update_url')
        if update_url:
            QDesktopServices.openUrl(QUrl(update_url))
    
    def skip_version(self):
        """Skip this version"""
        # Record skipped version
        GitHubUpdateNotifier.skip_version(self.update_info.get('latest_version'))
        self.accept()
    
    def should_remind_later(self) -> bool:
        """Check if user wants to be reminded later"""
        return self.reminder_checkbox.isChecked()


class UpdateCheckWorker(QThread):
    """Background worker for checking updates"""
    update_checked = pyqtSignal(dict)  # update_info
    
    def run(self):
        try:
            update_info = check_for_platform_updates()
            self.update_checked.emit(update_info)
        except Exception as e:
            self.update_checked.emit({'error': str(e)})


class GitHubUpdateNotifier:
    """System for automatic update checking and notification"""
    
    CONFIG_FILE = "github_update_config.json"
    
    def __init__(self, parent_window=None):
        self.parent_window = parent_window
        self.config = self.load_config()
        
        # Background worker
        self.update_worker = None
        self.setup_timer()
    
    @classmethod
    def get_config_path(cls) -> str:
        """Get path to config file"""
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, cls.CONFIG_FILE)
    
    def load_config(self) -> Dict[str, Any]:
        """Load notification configuration"""
        config_path = self.get_config_path()
        
        default_config = {
            'auto_check_enabled': True,
            'check_interval_hours': 24,
            'last_check': None,
            'last_notification': None,
            'skipped_versions': [],
            'notify_prereleases': False
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                return default_config
        except Exception as e:
            print(f"Error loading update config: {e}")
            return default_config
    
    def save_config(self):
        """Save notification configuration"""
        try:
            config_path = self.get_config_path()
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving update config: {e}")
    
    def setup_timer(self):
        """Setup automatic update checking timer"""
        if not self.config.get('auto_check_enabled'):
            return
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_updates)
        
        # Check every hour, but only notify based on interval
        self.timer.start(3600000)  # 1 hour in milliseconds
        
        # Check immediately if it's been long enough
        self.check_for_updates()
    
    def check_for_updates(self):
        """Check for updates in background"""
        if not self.should_check_now():
            return
        
        if self.update_worker and self.update_worker.isRunning():
            return
        
        self.update_worker = UpdateCheckWorker()
        self.update_worker.update_checked.connect(self.handle_update_result)
        self.update_worker.start()
        
        # Update last check time
        self.config['last_check'] = datetime.now().isoformat()
        self.save_config()
    
    def should_check_now(self) -> bool:
        """Check if we should check for updates now"""
        if not self.config.get('auto_check_enabled'):
            return False
        
        last_check = self.config.get('last_check')
        if not last_check:
            return True
        
        try:
            last_check_time = datetime.fromisoformat(last_check)
            interval_hours = self.config.get('check_interval_hours', 24)
            
            return datetime.now() > last_check_time + timedelta(hours=interval_hours)
        except:
            return True
    
    def handle_update_result(self, update_info: Dict[str, Any]):
        """Handle update check result"""
        if update_info.get('error'):
            print(f"Update check error: {update_info['error']}")
            return
        
        if not update_info.get('has_updates'):
            return
        
        latest_version = update_info.get('latest_version')
        
        # Check if this version was skipped
        if latest_version in self.config.get('skipped_versions', []):
            return
        
        # Check if this is a prerelease and we don't want those
        if update_info.get('is_prerelease') and not self.config.get('notify_prereleases'):
            return
        
        # Show notification
        self.show_update_notification(update_info)
    
    def show_update_notification(self, update_info: Dict[str, Any]):
        """Show update notification dialog"""
        try:
            dialog = UpdateNotificationDialog(update_info, self.parent_window)
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                # Update last notification time
                self.config['last_notification'] = datetime.now().isoformat()
                
                # If user wants to be reminded later, don't change reminder time
                if not dialog.should_remind_later():
                    # User took action, reset reminder
                    pass
                
                self.save_config()
        except Exception as e:
            print(f"Error showing update notification: {e}")
    
    def force_check(self):
        """Force an immediate update check"""
        self.config['last_check'] = None
        self.check_for_updates()
    
    def enable_auto_check(self, enabled: bool):
        """Enable or disable automatic checking"""
        self.config['auto_check_enabled'] = enabled
        self.save_config()
        
        if enabled:
            self.setup_timer()
        elif hasattr(self, 'timer'):
            self.timer.stop()
    
    def set_check_interval(self, hours: int):
        """Set check interval in hours"""
        self.config['check_interval_hours'] = hours
        self.save_config()
    
    def enable_prerelease_notifications(self, enabled: bool):
        """Enable or disable prerelease notifications"""
        self.config['notify_prereleases'] = enabled
        self.save_config()
    
    @classmethod
    def skip_version(cls, version: str):
        """Skip a specific version"""
        notifier = cls()
        if version not in notifier.config.get('skipped_versions', []):
            notifier.config.setdefault('skipped_versions', []).append(version)
            notifier.save_config()
    
    @classmethod
    def clear_skipped_versions(cls):
        """Clear all skipped versions"""
        notifier = cls()
        notifier.config['skipped_versions'] = []
        notifier.save_config()


# Convenience function for main application
def setup_update_notifications(main_window) -> GitHubUpdateNotifier:
    """Setup update notifications for the main application"""
    return GitHubUpdateNotifier(main_window)