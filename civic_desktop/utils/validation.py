# Input Validation and Data Sanitization
import re
import validators
from typing import Dict, Any, Tuple, cast


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class DataValidator:
    """Comprehensive data validation for user inputs and system data"""
    
    # Email pattern (more strict than basic regex)
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Name pattern (letters, spaces, hyphens, apostrophes)
    NAME_PATTERN = re.compile(r"^[a-zA-Z\s\-'\.]{1,50}$")
    
    # Password requirements - Government grade security
    PASSWORD_MIN_LENGTH = 12  # Increased for government use
    PASSWORD_MAX_LENGTH = 128
    PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]')
    
    # Common weak passwords to reject
    WEAK_PASSWORDS = {
        'password123', 'admin123', 'welcome123', 'password!', 'qwerty123',
        'abc123456', '123456789', 'password1', 'administrator', 'welcome1'
    }
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format and basic checks"""
        if not email:
            return False, "Email is required"
        
        email = email.strip().lower()
        
        if len(email) > 254:  # RFC 5321 limit
            return False, "Email too long"
        
        if not DataValidator.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        # Additional check using validators library
        if not validators.email(email):
            return False, "Invalid email address"
        
        return True, email
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength with government-grade requirements"""
        if not password:
            return False, "Password is required"
        
        if len(password) < DataValidator.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {DataValidator.PASSWORD_MIN_LENGTH} characters"
        
        if len(password) > DataValidator.PASSWORD_MAX_LENGTH:
            return False, f"Password too long (max {DataValidator.PASSWORD_MAX_LENGTH} characters)"
        
        # Check for common weak passwords
        if password.lower() in DataValidator.WEAK_PASSWORDS:
            return False, "Password is too common and easily guessed"
        
        # Check for required character types
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letters"
        
        if not re.search(r'\d', password):
            return False, "Password must contain numbers"
        
        if not re.search(r'[@$!%*?&]', password):
            return False, "Password must contain special characters (@$!%*?&)"
        
        # Check for patterns that indicate weak passwords
        if re.search(r'(.)\1{3,}', password):  # 4+ repeated characters (more reasonable)
            return False, "Password cannot have 4 or more repeated characters"
        
        # Check for long sequential patterns (4+ digits/letters) - more reasonable than 3
        if re.search(r'(0123|1234|2345|3456|4567|5678|6789|7890)', password):
            return False, "Password cannot contain 4+ sequential numbers"
        
        if re.search(r'(abcd|bcde|cdef|defg|efgh|fghi|ghij|hijk|ijkl|jklm|klmn|lmno|mnop|nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz)', password.lower()):
            return False, "Password cannot contain 4+ sequential letters"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, str]:
        """Validate first/last names"""
        if not name:
            return False, f"{field_name} is required"
        
        name = name.strip()
        
        if len(name) < 1:
            return False, f"{field_name} cannot be empty"
        
        if len(name) > 50:
            return False, f"{field_name} too long (max 50 characters)"
        
        if not DataValidator.NAME_PATTERN.match(name):
            return False, f"{field_name} contains invalid characters"
        
        return True, name
    
    @staticmethod
    def validate_location(location: str, field_name: str = "Location") -> Tuple[bool, str]:
        """Validate city/state/country fields"""
        if not location:
            return False, f"{field_name} is required"
        
        location = location.strip()
        
        if len(location) < 1:
            return False, f"{field_name} cannot be empty"
        
        if len(location) > 100:
            return False, f"{field_name} too long (max 100 characters)"
        
        # Allow letters, spaces, hyphens, periods, and commas for locations
        if not re.match(r"^[a-zA-Z\s\-\.,]{1,100}$", location):
            return False, f"{field_name} contains invalid characters"
        
        return True, location
    
    @staticmethod
    def validate_address(address: str) -> Tuple[bool, str]:
        """Validate street address"""
        if not address:
            return False, "Address is required"
        
        address = address.strip()
        
        if len(address) < 5:
            return False, "Address too short (minimum 5 characters)"
        
        if len(address) > 200:
            return False, "Address too long (max 200 characters)"
        
        # Allow alphanumeric, spaces, periods, commas, hyphens, # symbol
        if not re.match(r"^[a-zA-Z0-9\s\-\.,#]{5,200}$", address):
            return False, "Address contains invalid characters"
        
        return True, address
    
    @staticmethod
    def validate_registration_data(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, str]]:
        """Validate complete registration data"""
        errors: Dict[str, str] = {}
        cleaned_data: Dict[str, str] = {}
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'address', 'city', 'state', 'country', 'email', 'password']
        
        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = f"{field.replace('_', ' ').title()} is required"
        
        if errors:
            return False, "Required fields missing", errors
        
        # Validate each field
        valid, cleaned_email = DataValidator.validate_email(data['email'])
        if valid:
            cleaned_data['email'] = cleaned_email
        else:
            errors['email'] = cleaned_email
        
        valid, result = DataValidator.validate_password(data['password'])
        if valid:
            cleaned_data['password'] = data['password']  # Keep original for hashing
        else:
            errors['password'] = result
        
        valid, cleaned_first = DataValidator.validate_name(data['first_name'], "First name")
        if valid:
            cleaned_data['first_name'] = cleaned_first
        else:
            errors['first_name'] = cleaned_first
        
        valid, cleaned_last = DataValidator.validate_name(data['last_name'], "Last name")
        if valid:
            cleaned_data['last_name'] = cleaned_last
        else:
            errors['last_name'] = cleaned_last
        
        valid, cleaned_address = DataValidator.validate_address(data['address'])
        if valid:
            cleaned_data['address'] = cleaned_address
        else:
            errors['address'] = cleaned_address
        
        valid, cleaned_city = DataValidator.validate_location(data['city'], "City")
        if valid:
            cleaned_data['city'] = cleaned_city
        else:
            errors['city'] = cleaned_city
        
        valid, cleaned_state = DataValidator.validate_location(data['state'], "State")
        if valid:
            cleaned_data['state'] = cleaned_state
        else:
            errors['state'] = cleaned_state
        
        valid, cleaned_country = DataValidator.validate_location(data['country'], "Country")
        if valid:
            cleaned_data['country'] = cleaned_country
        else:
            errors['country'] = cleaned_country
        
        if errors:
            return False, "Validation failed", errors
        
        return True, "Validation successful", cleaned_data
    
    @staticmethod
    def sanitize_blockchain_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data before storing in blockchain"""
        sanitized: Dict[str, Any] = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value.strip())
            elif isinstance(value, list):
                sanitized[key] = [DataValidator.sanitize_blockchain_data(item) if isinstance(item, dict) else str(item).strip() for item in value]  # type: ignore[arg-type]
            elif isinstance(value, dict):
                sanitized[key] = DataValidator.sanitize_blockchain_data(cast(Dict[str, Any], value))
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def validate_file_upload(file_path: str, max_size: int = 10485760) -> Tuple[bool, str]:  # 10MB default
        """Validate file uploads for security (ID documents only)"""
        import os
        import mimetypes
        
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return False, f"File too large (max {max_size // 1024 // 1024}MB)"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Only allow image files and PDFs for ID documents
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf'}
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in allowed_extensions:
            return False, f"File type not allowed. Allowed for ID documents: {', '.join(allowed_extensions)}"
        
        # Verify MIME type matches extension
        mime_type, _ = mimetypes.guess_type(file_path)
        allowed_mimes = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', 
            '.png': 'image/png', '.pdf': 'application/pdf'
        }
        
        expected_mime = allowed_mimes.get(file_ext)
        if expected_mime and mime_type != expected_mime:
            return False, "File content doesn't match extension"
        
        return True, "File is valid"
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize text input to prevent injection attacks"""
        import html
        
        if not isinstance(text, str):
            text = str(text)
        
        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # HTML encode to prevent XSS
        text = html.escape(text, quote=True)
        
        # Remove potential SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\bOR\s+1\s*=\s*1)",
        ]
        
        for pattern in sql_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    @staticmethod
    def validate_session_token(token: str) -> Tuple[bool, str]:
        """Validate session tokens for security"""
        if not token:
            return False, "Token is required"
        
        # Check token format (should be base64 encoded)
        import base64
        try:
            decoded = base64.b64decode(token)
            if len(decoded) < 32:  # Minimum 256 bits
                return False, "Token too short"
        except Exception:
            return False, "Invalid token format"
        
        # Check for suspicious patterns
        if token.count('A') > len(token) * 0.5:  # Too many repeated characters
            return False, "Invalid token pattern"
        
        return True, "Token is valid"
    
    @staticmethod
    def validate_blockchain_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate data before blockchain storage"""
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"
        
        required_fields = ['action', 'timestamp']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate timestamp format - support both 3 and 6 digit microseconds
        timestamp = data.get('timestamp', '')
        if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3,6})?Z?$', timestamp):
            return False, "Invalid timestamp format"
        
        # Check data size (prevent blockchain bloat)
        import json
        data_size = len(json.dumps(data).encode('utf-8'))
        if data_size > 1048576:  # 1MB limit
            return False, "Data too large for blockchain storage"
        
        return True, "Data is valid"