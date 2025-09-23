"""
GitHub Integration Manager
Handles GitHub API interactions, update checking, and version control operations
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import requests
from packaging import version

class GitHubIntegrationManager:
    """Manages GitHub integration for the civic engagement platform"""
    
    def __init__(self, repo_owner: str = "Civic-Engagement", repo_name: str = "civic-engagment"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_base = "https://api.github.com"
        self.repo_url = f"https://github.com/{repo_owner}/{repo_name}"
        self.api_repo_url = f"{self.api_base}/repos/{repo_owner}/{repo_name}"
        
        # Load GitHub token if available (optional for public repos)
        self.github_token = self._load_github_token()
        
        # Current version info
        self.current_version = self._get_current_version()
        
    def _load_github_token(self) -> Optional[str]:
        """Load GitHub token from environment or config file"""
        # Try environment variable first
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            return token
        
        # Try config file
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'github_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('github_token')
        except Exception:
            pass
        
        return None
    
    def _get_current_version(self) -> str:
        """Get current version from CHANGELOG or version file"""
        try:
            # Try to read from CHANGELOG.md
            changelog_path = os.path.join(os.path.dirname(__file__), '..', '..', 'CHANGELOG.md')
            if os.path.exists(changelog_path):
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for version pattern like [Version 1.5.0]
                    import re
                    version_match = re.search(r'\[Version\s+([^\]]+)\]', content)
                    if version_match:
                        return version_match.group(1).strip()
            
            # Fallback to a default version
            return "1.5.0"
        except Exception:
            return "1.0.0"
    
    def _make_api_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated API request to GitHub"""
        url = f"{self.api_base}/{endpoint}"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Civic-Engagement-Platform'
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"GitHub API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            print(f"GitHub API request error: {e}")
            return None
    
    def check_for_updates(self) -> Dict[str, Any]:
        """Check for available updates from GitHub releases"""
        update_info = {
            'has_updates': False,
            'current_version': self.current_version,
            'latest_version': None,
            'latest_release': None,
            'update_url': None,
            'release_notes': None,
            'assets': [],
            'error': None
        }
        
        try:
            # Get latest release
            latest_release = self._make_api_request(f"repos/{self.repo_owner}/{self.repo_name}/releases/latest")
            
            if not latest_release:
                update_info['error'] = "Unable to fetch release information from GitHub"
                return update_info
            
            latest_version = latest_release.get('tag_name', '').lstrip('v')
            update_info['latest_version'] = latest_version
            update_info['latest_release'] = latest_release
            update_info['update_url'] = latest_release.get('html_url')
            update_info['release_notes'] = latest_release.get('body', '')
            update_info['assets'] = latest_release.get('assets', [])
            
            # Compare versions
            try:
                if version.parse(latest_version) > version.parse(self.current_version):
                    update_info['has_updates'] = True
            except Exception as e:
                # Fallback to string comparison if version parsing fails
                if latest_version != self.current_version:
                    update_info['has_updates'] = True
            
            return update_info
            
        except Exception as e:
            update_info['error'] = f"Error checking for updates: {str(e)}"
            return update_info
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get comprehensive repository information"""
        repo_info = self._make_api_request(f"repos/{self.repo_owner}/{self.repo_name}")
        
        if not repo_info:
            return {'error': 'Unable to fetch repository information'}
        
        return {
            'name': repo_info.get('name'),
            'description': repo_info.get('description'),
            'stars': repo_info.get('stargazers_count', 0),
            'forks': repo_info.get('forks_count', 0),
            'issues': repo_info.get('open_issues_count', 0),
            'last_updated': repo_info.get('updated_at'),
            'language': repo_info.get('language'),
            'license': repo_info.get('license', {}).get('name') if repo_info.get('license') else None,
            'url': repo_info.get('html_url'),
            'clone_url': repo_info.get('clone_url'),
            'ssh_url': repo_info.get('ssh_url')
        }
    
    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits from the repository"""
        commits_data = self._make_api_request(f"repos/{self.repo_owner}/{self.repo_name}/commits?per_page={limit}")
        
        if not commits_data:
            return []
        
        commits = []
        for commit in commits_data:
            commits.append({
                'sha': commit.get('sha', '')[:8],  # Short SHA
                'message': commit.get('commit', {}).get('message', '').split('\n')[0],  # First line only
                'author': commit.get('commit', {}).get('author', {}).get('name', 'Unknown'),
                'date': commit.get('commit', {}).get('author', {}).get('date', ''),
                'url': commit.get('html_url', '')
            })
        
        return commits
    
    def get_issues(self, state: str = 'open', limit: int = 10) -> List[Dict[str, Any]]:
        """Get repository issues"""
        issues_data = self._make_api_request(f"repos/{self.repo_owner}/{self.repo_name}/issues?state={state}&per_page={limit}")
        
        if not issues_data:
            return []
        
        issues = []
        for issue in issues_data:
            # Skip pull requests (they appear in issues API)
            if issue.get('pull_request'):
                continue
                
            issues.append({
                'number': issue.get('number'),
                'title': issue.get('title'),
                'state': issue.get('state'),
                'author': issue.get('user', {}).get('login', 'Unknown'),
                'created_at': issue.get('created_at'),
                'updated_at': issue.get('updated_at'),
                'labels': [label.get('name') for label in issue.get('labels', [])],
                'url': issue.get('html_url')
            })
        
        return issues
    
    def get_pull_requests(self, state: str = 'open', limit: int = 10) -> List[Dict[str, Any]]:
        """Get repository pull requests"""
        prs_data = self._make_api_request(f"repos/{self.repo_owner}/{self.repo_name}/pulls?state={state}&per_page={limit}")
        
        if not prs_data:
            return []
        
        prs = []
        for pr in prs_data:
            prs.append({
                'number': pr.get('number'),
                'title': pr.get('title'),
                'state': pr.get('state'),
                'author': pr.get('user', {}).get('login', 'Unknown'),
                'created_at': pr.get('created_at'),
                'updated_at': pr.get('updated_at'),
                'mergeable': pr.get('mergeable'),
                'url': pr.get('html_url'),
                'base_branch': pr.get('base', {}).get('ref', 'main'),
                'head_branch': pr.get('head', {}).get('ref', 'unknown')
            })
        
        return prs
    
    def create_issue(self, title: str, body: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new issue on GitHub"""
        if not self.github_token:
            return {'error': 'GitHub token required to create issues'}
        
        issue_data = {
            'title': title,
            'body': body
        }
        
        if labels:
            issue_data['labels'] = labels
        
        result = self._make_api_request(f"repos/{self.repo_owner}/{self.repo_name}/issues", 'POST', issue_data)
        
        if result:
            return {
                'success': True,
                'issue_number': result.get('number'),
                'url': result.get('html_url')
            }
        else:
            return {'error': 'Failed to create issue'}
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get local git repository status"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            if result.returncode != 0:
                return {'error': 'Not a git repository'}
            
            status_info = {}
            
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            status_info['current_branch'] = result.stdout.strip() if result.returncode == 0 else 'unknown'
            
            # Get status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                status_info['has_changes'] = len(changes) > 0
                status_info['changes'] = changes
            else:
                status_info['has_changes'] = None
                status_info['changes'] = []
            
            # Get last commit
            result = subprocess.run(['git', 'log', '-1', '--pretty=format:%H|%s|%an|%ad'], 
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0 and result.stdout:
                commit_parts = result.stdout.strip().split('|')
                if len(commit_parts) >= 4:
                    status_info['last_commit'] = {
                        'sha': commit_parts[0][:8],
                        'message': commit_parts[1],
                        'author': commit_parts[2],
                        'date': commit_parts[3]
                    }
            
            # Check if remote tracking exists
            result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'], 
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            status_info['has_remote'] = result.returncode == 0
            
            if status_info['has_remote']:
                # Check if we're ahead/behind remote
                result = subprocess.run(['git', 'rev-list', '--left-right', '--count', 'HEAD...@{u}'], 
                                      capture_output=True, text=True, cwd=os.path.dirname(__file__))
                if result.returncode == 0:
                    counts = result.stdout.strip().split('\t')
                    if len(counts) == 2:
                        status_info['ahead'] = int(counts[0])
                        status_info['behind'] = int(counts[1])
            
            return status_info
            
        except Exception as e:
            return {'error': f'Git status error: {str(e)}'}
    
    def initialize_git_repository(self, remote_url: Optional[str] = None) -> Dict[str, Any]:
        """Initialize git repository and set up remote"""
        try:
            repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            # Initialize git repository
            result = subprocess.run(['git', 'init'], capture_output=True, text=True, cwd=repo_dir)
            if result.returncode != 0:
                return {'error': f'Failed to initialize git repository: {result.stderr}'}
            
            # Add remote if provided
            if remote_url:
                result = subprocess.run(['git', 'remote', 'add', 'origin', remote_url], 
                                      capture_output=True, text=True, cwd=repo_dir)
                if result.returncode != 0:
                    return {'error': f'Failed to add remote: {result.stderr}'}
            
            # Create initial commit
            result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True, cwd=repo_dir)
            if result.returncode == 0:
                result = subprocess.run(['git', 'commit', '-m', 'Initial commit'], 
                                      capture_output=True, text=True, cwd=repo_dir)
            
            return {'success': True, 'message': 'Git repository initialized successfully'}
            
        except Exception as e:
            return {'error': f'Git initialization error: {str(e)}'}
    
    def download_update(self, asset_url: str, filename: str) -> Dict[str, Any]:
        """Download update file from GitHub release"""
        try:
            headers = {}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            response = requests.get(asset_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            download_path = os.path.join(os.path.dirname(__file__), '..', '..', 'downloads', filename)
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return {
                'success': True,
                'download_path': download_path,
                'file_size': os.path.getsize(download_path)
            }
            
        except Exception as e:
            return {'error': f'Download failed: {str(e)}'}


class GitHubIntegrationUI:
    """UI components for GitHub integration"""
    
    @staticmethod
    def format_update_notification(update_info: Dict[str, Any]) -> str:
        """Format update notification for display"""
        if update_info.get('error'):
            return f"❌ Error checking for updates: {update_info['error']}"
        
        if not update_info.get('has_updates'):
            return f"✅ You have the latest version ({update_info['current_version']})"
        
        latest = update_info['latest_version']
        current = update_info['current_version']
        
        notification = f"""
🆕 Update Available!
═══════════════════
Current Version: {current}
Latest Version: {latest}

🔗 Download: {update_info.get('update_url', 'N/A')}

📋 Release Notes:
{update_info.get('release_notes', 'No release notes available')[:200]}...
"""
        
        return notification
    
    @staticmethod
    def format_repository_status(repo_info: Dict[str, Any], git_status: Dict[str, Any]) -> str:
        """Format repository status for display"""
        if repo_info.get('error'):
            return f"❌ Repository Error: {repo_info['error']}"
        
        status = f"""
📁 Repository Status
═══════════════════
Name: {repo_info.get('name', 'N/A')}
⭐ Stars: {repo_info.get('stars', 0)}
🍴 Forks: {repo_info.get('forks', 0)}
🐛 Open Issues: {repo_info.get('issues', 0)}
📝 Language: {repo_info.get('language', 'N/A')}
"""
        
        if not git_status.get('error'):
            status += f"""
🔧 Local Git Status
════════════════════
Branch: {git_status.get('current_branch', 'unknown')}
Changes: {'Yes' if git_status.get('has_changes') else 'No'}
Remote: {'Connected' if git_status.get('has_remote') else 'Not connected'}
"""
            
            if git_status.get('ahead') is not None:
                status += f"Ahead: {git_status['ahead']} commits\n"
            if git_status.get('behind') is not None:
                status += f"Behind: {git_status['behind']} commits\n"
        
        return status


# Convenience functions for common operations
def check_for_platform_updates() -> Dict[str, Any]:
    """Quick function to check for platform updates"""
    github_manager = GitHubIntegrationManager()
    return github_manager.check_for_updates()

def get_platform_development_status() -> Dict[str, Any]:
    """Get comprehensive development status"""
    github_manager = GitHubIntegrationManager()
    
    return {
        'repository_info': github_manager.get_repository_info(),
        'git_status': github_manager.get_git_status(),
        'recent_commits': github_manager.get_recent_commits(5),
        'open_issues': github_manager.get_issues('open', 5),
        'pull_requests': github_manager.get_pull_requests('open', 5),
        'update_check': github_manager.check_for_updates()
    }

def report_platform_issue(title: str, description: str, user_email: str = None) -> Dict[str, Any]:
    """Report an issue to the GitHub repository"""
    github_manager = GitHubIntegrationManager()
    
    # Add user context to the issue body
    issue_body = f"""
**Issue Description:**
{description}

**Platform Information:**
- Version: {github_manager.current_version}
- Reported by: {user_email or 'Anonymous'}
- Date: {datetime.now(timezone.utc).isoformat()}

**Environment:**
- Platform: Civic Engagement Platform
- Component: User Report
"""
    
    return github_manager.create_issue(title, issue_body, ['user-report', 'bug'])