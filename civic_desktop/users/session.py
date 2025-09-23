import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from ..utils.validation import DataValidator


class SessionManager:
    """Secure session management with timeout and validation"""
    _current_user: Optional[Dict[str, Any]] = None
    _session_token: Optional[str] = None
    _session_start: Optional[datetime] = None
    _last_activity: Optional[datetime] = None
    _session_timeout_minutes: int = 30  # Government security standard
    _inactive_timeout_minutes: int = 15  # Inactivity timeout
    
    @classmethod
    def login(cls, user: Dict[str, Any]) -> bool:
        """Secure login with session token generation"""
        try:
            # Validate user data
            if not user or 'email' not in user:
                return False
            
            # Generate secure session token
            cls._session_token = secrets.token_urlsafe(32)
            cls._current_user = user.copy()
            cls._session_start = datetime.now()
            cls._last_activity = datetime.now()
            
            # Add session metadata
            cls._current_user['session_token'] = cls._session_token
            cls._current_user['session_start'] = cls._session_start.isoformat()
            
            return True
            
        except Exception as e:
            print(f"Login error: {e}")
            cls.logout()
            return False

    @classmethod
    def logout(cls) -> None:
        """Secure logout with complete session cleanup"""
        cls._current_user = None
        cls._session_token = None
        cls._session_start = None
        cls._last_activity = None

    @classmethod
    def get_current_user(cls) -> Optional[Dict[str, Any]]:
        """Get current user with session validation"""
        if not cls._is_session_valid():
            cls.logout()
            return None
        
        # Update last activity
        cls._last_activity = datetime.now()
        return cls._current_user

    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if user is authenticated with valid session"""
        return cls._is_session_valid()
    
    @classmethod
    def validate_session_token(cls, token: str) -> bool:
        """Validate session token format and match"""
        if not DataValidator.validate_session_token(token):
            return False
        return cls._session_token == token
    
    @classmethod
    def extend_session(cls) -> bool:
        """Extend session timeout if within valid period"""
        if not cls._is_session_valid():
            return False
        
        cls._last_activity = datetime.now()
        return True
    
    @classmethod
    def get_session_info(cls) -> Dict[str, Any]:
        """Get session information for monitoring"""
        if not cls._current_user:
            return {'authenticated': False}
        
        now = datetime.now()
        session_duration = (now - cls._session_start).total_seconds() / 60 if cls._session_start else 0
        inactive_duration = (now - cls._last_activity).total_seconds() / 60 if cls._last_activity else 0
        
        return {
            'authenticated': True,
            'user_email': cls._current_user.get('email', 'unknown'),
            'session_duration_minutes': round(session_duration, 1),
            'inactive_duration_minutes': round(inactive_duration, 1),
            'session_expires_in_minutes': max(0, cls._session_timeout_minutes - session_duration),
            'inactive_expires_in_minutes': max(0, cls._inactive_timeout_minutes - inactive_duration)
        }
    
    @classmethod
    def _is_session_valid(cls) -> bool:
        """Check if current session is valid"""
        if not cls._current_user or not cls._session_start or not cls._last_activity:
            return False
        
        now = datetime.now()
        
        # Check session timeout
        session_duration = now - cls._session_start
        if session_duration > timedelta(minutes=cls._session_timeout_minutes):
            return False
        
        # Check inactivity timeout
        inactive_duration = now - cls._last_activity
        if inactive_duration > timedelta(minutes=cls._inactive_timeout_minutes):
            return False
        
        return True
    
    @classmethod
    def cleanup_expired_sessions(cls) -> None:
        """Cleanup expired sessions (called periodically)"""
        if not cls._is_session_valid():
            cls.logout()
