"""
GitHub Integration Module
Provides update checking, repository management, and version control features
"""

from .github_manager import GitHubIntegrationManager, GitHubIntegrationUI, check_for_platform_updates
from .github_tab import GitHubIntegrationTab
from .update_notifier import GitHubUpdateNotifier, setup_update_notifications

__all__ = [
    'GitHubIntegrationManager',
    'GitHubIntegrationUI', 
    'GitHubIntegrationTab',
    'GitHubUpdateNotifier',
    'check_for_platform_updates',
    'setup_update_notifications'
]