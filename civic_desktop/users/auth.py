"""
AUTHENTICATION MODULE - Session management and security
Handles user sessions, authentication state, and security checks
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any
from pathlib import Path

class SessionManager:
    """Manages user sessions and authentication state"""
    
    _current_session = None
    _session_file = None
    
    @classmethod
    def initialize(cls, session_file_path: str = "users/current_session.json"):
        """Initialize session manager with file path"""
        cls._session_file = Path(session_file_path)
        cls._session_file.parent.mkdir(parents=True, exist_ok=True)
        cls._load_session()
    
    @classmethod
    def _load_session(cls):
        """Load current session from file"""
        try:
            if cls._session_file and cls._session_file.exists():
                with open(cls._session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Check if session is still valid
                expires_at = datetime.fromisoformat(session_data.get('expires_at', '1970-01-01'))
                if datetime.now() < expires_at:
                    cls._current_session = session_data
                else:
                    # Session expired, remove file
                    cls._session_file.unlink()
                    cls._current_session = None
        except Exception as e:
            print(f"Error loading session: {e}")
            cls._current_session = None
    
    @classmethod
    def _save_session(cls):
        """Save current session to file"""
        try:
            if cls._session_file:
                if cls._current_session:
                    with open(cls._session_file, 'w', encoding='utf-8') as f:
                        json.dump(cls._current_session, f, indent=2, ensure_ascii=False)
                else:
                    # No session, remove file if it exists
                    if cls._session_file.exists():
                        cls._session_file.unlink()
        except Exception as e:
            print(f"Error saving session: {e}")
    
    @classmethod
    def create_session(cls, user_data: Dict[str, Any], session_id: str, expires_hours: int = 24):
        """Create new user session"""
        cls._current_session = {
            'session_id': session_id,
            'user_id': user_data['user_id'],
            'email': user_data['email'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'role': user_data['role'],
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=expires_hours)).isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        cls._save_session()
        return True
    
    @classmethod
    def get_current_user(cls) -> Optional[Dict[str, Any]]:
        """Get current authenticated user data"""
        if cls._current_session:
            # Update last activity
            cls._current_session['last_activity'] = datetime.now().isoformat()
            cls._save_session()
            return cls._current_session
        return None
    
    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if user is currently authenticated"""
        return cls._current_session is not None
    
    @classmethod
    def get_user_role(cls) -> Optional[str]:
        """Get current user's role"""
        if cls._current_session:
            return cls._current_session.get('role')
        return None
    
    @classmethod
    def has_permission(cls, required_permission: str) -> bool:
        """Check if current user has required permission"""
        if not cls._current_session:
            return False
        
        user_role = cls._current_session.get('role')
        if not user_role:
            return False
        
        # Import here to avoid circular imports
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        from utils.validation import SecurityValidator
        
        is_valid, _ = SecurityValidator.validate_permissions(user_role, required_permission)
        return is_valid
    
    @classmethod
    def logout(cls):
        """Logout current user and clear session"""
        cls._current_session = None
        cls._save_session()
    
    @classmethod
    def extend_session(cls, hours: int = 24):
        """Extend current session expiration"""
        if cls._current_session:
            new_expires = (datetime.now() + timedelta(hours=hours)).isoformat()
            cls._current_session['expires_at'] = new_expires
            cls._save_session()
            return True
        return False

class AuthenticationService:
    """High-level authentication service"""
    
    def __init__(self, backend=None):
        """Initialize authentication service"""
        self.backend = backend
        if not SessionManager._session_file:
            SessionManager.initialize()
    
    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Login user with email and password
        
        Args:
            email: User's email address
            password: User's password
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.backend:
            return False, "Authentication backend not available"
        
        # Authenticate with backend
        success, message, user_record = self.backend.authenticate_user(email, password)
        
        if not success:
            return False, message
        
        # Create backend session
        session_success, session_message, session_id = self.backend.create_session(user_record)
        
        if not session_success:
            return False, f"Session creation failed: {session_message}"
        
        # Create local session
        SessionManager.create_session(user_record, session_id)
        
        return True, f"Welcome back, {user_record['first_name']}!"
    
    def register(self, registration_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Register new user
        
        Args:
            registration_data: User registration information
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.backend:
            return False, "Authentication backend not available"
        
        success, message, user_record = self.backend.register_user(registration_data)
        
        if not success:
            return False, message
        
        # Auto-login after successful registration
        login_success, login_message = self.login(
            registration_data['email'], 
            registration_data['password']
        )
        
        if login_success:
            return True, f"Registration successful! Welcome, {user_record['first_name']}!"
        else:
            return True, f"Registration successful! Please login to continue."
    
    def logout(self) -> Tuple[bool, str]:
        """Logout current user"""
        current_user = SessionManager.get_current_user()
        
        if not current_user:
            return False, "No active session"
        
        # Logout from backend if available
        if self.backend:
            session_id = current_user.get('session_id')
            if session_id:
                self.backend.logout_user(session_id)
        
        # Clear local session
        SessionManager.logout()
        
        return True, "Logged out successfully"
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        return SessionManager.get_current_user()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return SessionManager.is_authenticated()
    
    def require_authentication(self) -> Tuple[bool, str]:
        """Require user to be authenticated"""
        if not self.is_authenticated():
            return False, "Authentication required"
        return True, "User is authenticated"
    
    def require_permission(self, permission: str) -> Tuple[bool, str]:
        """Require user to have specific permission"""
        if not self.is_authenticated():
            return False, "Authentication required"
        
        if not SessionManager.has_permission(permission):
            return False, f"Permission denied: {permission}"
        
        return True, "Permission granted"
    
    def require_role(self, required_role: str) -> Tuple[bool, str]:
        """Require user to have specific role"""
        if not self.is_authenticated():
            return False, "Authentication required"
        
        current_role = SessionManager.get_user_role()
        if current_role != required_role:
            return False, f"Role '{required_role}' required, current role: '{current_role}'"
        
        return True, "Role authorized"

# Role-based access control decorators and utilities
class RoleChecker:
    """Utility class for checking user roles and permissions"""
    
    @staticmethod
    def can_vote() -> bool:
        """Check if user can vote"""
        return SessionManager.has_permission('vote')
    
    @staticmethod
    def can_debate() -> bool:
        """Check if user can participate in debates"""
        return SessionManager.has_permission('debate')
    
    @staticmethod
    def can_moderate() -> bool:
        """Check if user can moderate content"""
        role = SessionManager.get_user_role()
        return role in ['contract_representative', 'contract_senator', 'contract_elder']
    
    @staticmethod
    def can_create_legislation() -> bool:
        """Check if user can create legislation"""
        return SessionManager.has_permission('legislate')
    
    @staticmethod
    def can_veto() -> bool:
        """Check if user can veto legislation"""
        return SessionManager.has_permission('veto')
    
    @staticmethod
    def can_interpret_constitution() -> bool:
        """Check if user can interpret constitutional issues"""
        return SessionManager.get_user_role() == 'contract_elder'
    
    @staticmethod
    def can_manage_elections() -> bool:
        """Check if user can manage elections"""
        role = SessionManager.get_user_role()
        return role in ['contract_elder', 'contract_founder']
    
    @staticmethod
    def can_system_admin() -> bool:
        """Check if user has system administration privileges"""
        return SessionManager.get_user_role() == 'contract_founder'
    
    @staticmethod
    def get_available_actions() -> list:
        """Get list of actions available to current user"""
        if not SessionManager.is_authenticated():
            return []
        
        actions = []
        
        # Basic citizen rights
        if RoleChecker.can_vote():
            actions.extend(['vote', 'petition', 'appeal'])
        
        if RoleChecker.can_debate():
            actions.append('debate')
        
        # Legislative powers
        if RoleChecker.can_create_legislation():
            actions.extend(['create_legislation', 'budget_authority'])
        
        # Moderation powers
        if RoleChecker.can_moderate():
            actions.extend(['moderate_content', 'review_flags'])
        
        # Elder powers
        if RoleChecker.can_veto():
            actions.extend(['veto_legislation', 'constitutional_review'])
        
        # Election management
        if RoleChecker.can_manage_elections():
            actions.extend(['manage_elections', 'assign_roles'])
        
        # System administration
        if RoleChecker.can_system_admin():
            actions.extend(['system_admin', 'emergency_powers', 'modify_constitution'])
        
        return actions

# Initialize session manager
SessionManager.initialize()