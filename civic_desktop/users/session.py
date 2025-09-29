"""
SESSION MANAGEMENT - Simple session tracking for user authentication
Provides basic session management functionality for the civic platform
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class SessionManager:
    """Simple session management for user authentication"""
    
    current_session = None
    
    @classmethod
    def get_current_user(cls) -> Optional[Dict]:
        """Get current authenticated user"""
        if cls.current_session:
            return cls.current_session.get('user', None)
        return None
    
    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if user is currently authenticated"""
        return cls.current_session is not None and 'user' in cls.current_session
    
    @classmethod
    def create_session(cls, user: Dict) -> None:
        """Create new user session"""
        cls.current_session = {
            'user': user,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
    
    @classmethod
    def end_session(cls) -> None:
        """End current user session"""
        cls.current_session = None
    
    @classmethod
    def update_activity(cls) -> None:
        """Update last activity timestamp"""
        if cls.current_session:
            cls.current_session['last_activity'] = datetime.now().isoformat()

# Export the main class
__all__ = ['SessionManager']