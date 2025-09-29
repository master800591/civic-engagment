"""
VALIDATION FRAMEWORK - Comprehensive input validation for civic engagement platform
Provides security validation, data sanitization, and input checking across all modules
"""

import re
import validators
from typing import Tuple, Any, Dict, List, Optional
from datetime import datetime, timedelta
import os
from pathlib import Path

class DataValidator:
    """Comprehensive validation framework for all platform inputs"""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # Name validation
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 50
    
    # File validation
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_ID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email address format and legitimacy"""
        if not email or not isinstance(email, str):
            return False, "Email must be a non-empty string"
        
        email = email.strip().lower()
        
        # Check length
        if len(email) > 254:
            return False, "Email address is too long"
        
        # Basic format validation
        try:
            if not validators.email(email):
                return False, "Invalid email format"
        except Exception:
            return False, "Invalid email format"
        
        # Additional security checks
        if '..' in email or email.startswith('.') or email.endswith('.'):
            return False, "Email contains invalid characters"
        
        # Check for suspicious patterns
        suspicious_patterns = ['admin@', 'test@', 'example@', 'noreply@']
        if any(pattern in email for pattern in suspicious_patterns):
            return False, "Email appears to be a system or test address"
        
        return True, "Valid email address"
    
    @staticmethod
    def validate_password(password: str, confirm_password: str = None) -> Tuple[bool, str]:
        """Validate password strength and security requirements"""
        if not password or not isinstance(password, str):
            return False, "Password must be a non-empty string"
        
        # Length validation
        if len(password) < DataValidator.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {DataValidator.MIN_PASSWORD_LENGTH} characters"
        
        if len(password) > DataValidator.MAX_PASSWORD_LENGTH:
            return False, f"Password must be no more than {DataValidator.MAX_PASSWORD_LENGTH} characters"
        
        # Complexity requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not has_upper:
            return False, "Password must contain at least one uppercase letter"
        if not has_lower:
            return False, "Password must contain at least one lowercase letter"
        if not has_digit:
            return False, "Password must contain at least one number"
        if not has_special:
            return False, "Password must contain at least one special character"
        
        # Check for common weak patterns
        weak_patterns = ['password', '123456', 'qwerty', 'admin', 'user']
        password_lower = password.lower()
        for pattern in weak_patterns:
            if pattern in password_lower:
                return False, f"Password contains common weak pattern: {pattern}"
        
        # Confirm password match if provided
        if confirm_password is not None:
            if password != confirm_password:
                return False, "Passwords do not match"
        
        return True, "Strong password"
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, str]:
        """Validate first/last name fields"""
        if not name or not isinstance(name, str):
            return False, f"{field_name} must be a non-empty string"
        
        name = name.strip()
        
        # Length validation
        if len(name) < DataValidator.MIN_NAME_LENGTH:
            return False, f"{field_name} must be at least {DataValidator.MIN_NAME_LENGTH} characters"
        
        if len(name) > DataValidator.MAX_NAME_LENGTH:
            return False, f"{field_name} must be no more than {DataValidator.MAX_NAME_LENGTH} characters"
        
        # Character validation (allow letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[A-Za-z\s\-']+$", name):
            return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
        
        # No multiple consecutive spaces
        if '  ' in name:
            return False, f"{field_name} cannot contain multiple consecutive spaces"
        
        return True, f"Valid {field_name.lower()}"
    
    @staticmethod
    def validate_location(city: str, state: str, country: str) -> Tuple[bool, str]:
        """Validate location information for voting jurisdiction"""
        # Validate city
        if not city or not isinstance(city, str) or len(city.strip()) < 2:
            return False, "City must be at least 2 characters"
        
        # Validate state
        if not state or not isinstance(state, str) or len(state.strip()) < 2:
            return False, "State/Province must be at least 2 characters"
        
        # Validate country
        if not country or not isinstance(country, str) or len(country.strip()) < 2:
            return False, "Country must be at least 2 characters"
        
        # Check for valid characters (letters, spaces, hyphens)
        location_pattern = r"^[A-Za-z\s\-'\.]+$"
        
        if not re.match(location_pattern, city.strip()):
            return False, "City contains invalid characters"
        
        if not re.match(location_pattern, state.strip()):
            return False, "State/Province contains invalid characters"
        
        if not re.match(location_pattern, country.strip()):
            return False, "Country contains invalid characters"
        
        return True, "Valid location information"
    
    @staticmethod
    def validate_file_upload(file_path: str, allowed_extensions: set = None) -> Tuple[bool, str]:
        """Validate uploaded ID document files"""
        if not file_path or not isinstance(file_path, str):
            return False, "File path must be provided"
        
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            return False, "File does not exist"
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > DataValidator.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return False, f"File too large: {size_mb:.1f}MB (max {DataValidator.MAX_FILE_SIZE / (1024 * 1024):.0f}MB)"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Check file extension
        extensions = allowed_extensions or DataValidator.ALLOWED_ID_EXTENSIONS
        if file_path.suffix.lower() not in extensions:
            return False, f"Invalid file type. Allowed: {', '.join(extensions)}"
        
        return True, "Valid file upload"
    
    @staticmethod
    def validate_user_role(role: str) -> Tuple[bool, str]:
        """Validate user role assignment"""
        valid_roles = {
            'contract_member': 'Contract Member - Core democratic rights',
            'contract_representative': 'Contract Representative - People\'s voice in legislature',
            'contract_senator': 'Contract Senator - Deliberative upper house',
            'contract_elder': 'Contract Elder - Constitutional guardian',
            'contract_founder': 'Contract Founder - Platform architect'
        }
        
        if not role or role not in valid_roles:
            return False, f"Invalid role. Must be one of: {', '.join(valid_roles.keys())}"
        
        return True, f"Valid role: {valid_roles[role]}"
    
    @staticmethod
    def sanitize_input(input_string: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not input_string or not isinstance(input_string, str):
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';\\]', '', input_string)
        
        # Limit length
        sanitized = sanitized[:max_length]
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized.strip()
    
    @staticmethod
    def validate_session_data(session_data: Dict) -> Tuple[bool, str]:
        """Validate session data integrity"""
        required_fields = ['user_id', 'email', 'role', 'created_at']
        
        if not isinstance(session_data, dict):
            return False, "Session data must be a dictionary"
        
        for field in required_fields:
            if field not in session_data:
                return False, f"Missing required session field: {field}"
        
        # Validate email in session
        email_valid, email_msg = DataValidator.validate_email(session_data['email'])
        if not email_valid:
            return False, f"Invalid email in session: {email_msg}"
        
        # Validate role
        role_valid, role_msg = DataValidator.validate_user_role(session_data['role'])
        if not role_valid:
            return False, f"Invalid role in session: {role_msg}"
        
        return True, "Valid session data"

class SecurityValidator:
    """Security-focused validation for authentication and authorization"""
    
    @staticmethod
    def validate_login_attempt(email: str, max_attempts: int = 5, lockout_duration: int = 300) -> Tuple[bool, str]:
        """Validate login attempt and check for brute force protection"""
        # This would integrate with a login attempt tracking system
        # For now, just validate email format
        return DataValidator.validate_email(email)
    
    @staticmethod
    def validate_blockchain_signature(signature_data: Dict) -> Tuple[bool, str]:
        """Validate blockchain signature data"""
        required_fields = ['signature', 'public_key', 'message', 'timestamp']
        
        if not isinstance(signature_data, dict):
            return False, "Signature data must be a dictionary"
        
        for field in required_fields:
            if field not in signature_data:
                return False, f"Missing required signature field: {field}"
        
        # Additional signature validation would go here
        return True, "Valid signature data"
    
    @staticmethod
    def validate_permissions(user_role: str, required_permission: str) -> Tuple[bool, str]:
        """Validate user permissions for specific actions"""
        # Define role-based permissions
        permissions = {
            'contract_member': {'vote', 'debate', 'petition', 'appeal'},
            'contract_representative': {'vote', 'debate', 'petition', 'appeal', 'legislate', 'budget', 'impeach'},
            'contract_senator': {'vote', 'debate', 'petition', 'appeal', 'legislate', 'confirm', 'review'},
            'contract_elder': {'vote', 'debate', 'veto', 'interpret', 'constitutional_review'},
            'contract_founder': {'vote', 'debate', 'emergency_power', 'constitutional_amend', 'system_modify'}
        }
        
        if user_role not in permissions:
            return False, f"Unknown user role: {user_role}"
        
        if required_permission not in permissions[user_role]:
            return False, f"User role '{user_role}' lacks permission: '{required_permission}'"
        
        return True, f"User has required permission: {required_permission}"