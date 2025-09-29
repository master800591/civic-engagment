# Utils Module - Validation Framework & Utility Functions

## Purpose
Comprehensive input validation, data sanitization, security utilities, and helper functions used across all platform modules.

## Module Structure
```
utils/
├── validation.py         # Input validation framework
└── README.md            # Utility documentation
```

## AI Implementation Instructions

### 1. Comprehensive Data Validation Framework
```python
# Universal Input Validation System
import re
import validators
from typing import Tuple, Any, Dict, List
from datetime import datetime, timedelta

class DataValidator:
    """Comprehensive validation framework for all platform inputs"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email address format and legitimacy"""
        if not email or not isinstance(email, str):
            return False, "Email must be a non-empty string"
        
        # Basic format validation
        if not validators.email(email):
            return False, "Invalid email format"
        
        # Length constraints
        if len(email) > 254:  # RFC 5321 limit
            return False, "Email address too long (max 254 characters)"
        
        # Domain validation
        domain = email.split('@')[1] if '@' in email else ''
        if len(domain) > 253:
            return False, "Email domain too long"
        
        # Prevent common attack patterns
        dangerous_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
        email_lower = email.lower()
        for pattern in dangerous_patterns:
            if pattern in email_lower:
                return False, "Email contains potentially dangerous content"
        
        return True, "Valid email address"
    
    @staticmethod
    def validate_password(password: str, min_length: int = 8, 
                         require_special: bool = True, 
                         require_numbers: bool = True,
                         require_uppercase: bool = True) -> Tuple[bool, str]:
        """Comprehensive password strength validation"""
        
        if not password or not isinstance(password, str):
            return False, "Password must be a non-empty string"
        
        # Length validation
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        
        if len(password) > 128:  # Prevent DoS via extremely long passwords
            return False, "Password too long (max 128 characters)"
        
        # Character requirements
        validation_errors = []
        
        if require_uppercase and not re.search(r'[A-Z]', password):
            validation_errors.append("at least one uppercase letter")
        
        if require_numbers and not re.search(r'[0-9]', password):
            validation_errors.append("at least one number")
        
        if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            validation_errors.append("at least one special character")
        
        if validation_errors:
            return False, f"Password must contain {', '.join(validation_errors)}"
        
        # Common password checks
        common_passwords = [
            'password', '123456', 'password123', 'admin', 'qwerty',
            'letmein', 'welcome', 'monkey', '1234567890', 'password1'
        ]
        
        if password.lower() in common_passwords:
            return False, "Password is too common and easily guessable"
        
        # Sequential character check
        if DataValidator._has_sequential_chars(password):
            return False, "Password contains too many sequential characters"
        
        return True, "Password meets security requirements"
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, str]:
        """Validate personal names with cultural sensitivity"""
        
        if not name or not isinstance(name, str):
            return False, f"{field_name} must be a non-empty string"
        
        # Length constraints
        if len(name.strip()) < 1:
            return False, f"{field_name} cannot be empty"
        
        if len(name) > 100:
            return False, f"{field_name} too long (max 100 characters)"
        
        # Character validation (allow international characters)
        if not re.match(r'^[\w\s\-\'\.]+$', name, re.UNICODE):
            return False, f"{field_name} contains invalid characters"
        
        # Prevent injection attacks
        dangerous_patterns = ['<', '>', '{', '}', '[', ']', '(', ')', ';', '=']
        for pattern in dangerous_patterns:
            if pattern in name:
                return False, f"{field_name} contains potentially dangerous characters"
        
        # Reasonable name validation
        words = name.strip().split()
        if len(words) > 10:  # Reasonable limit for compound names
            return False, f"{field_name} has too many words (max 10)"
        
        return True, f"Valid {field_name.lower()}"
    
    @staticmethod
    def validate_civic_content(content: str, content_type: str = "content") -> Tuple[bool, str]:
        """Validate civic debate content, arguments, and proposals"""
        
        if not content or not isinstance(content, str):
            return False, f"{content_type} must be a non-empty string"
        
        # Length constraints based on content type
        LENGTH_LIMITS = {
            'argument': {'min': 50, 'max': 5000},
            'topic_title': {'min': 10, 'max': 200},
            'topic_description': {'min': 100, 'max': 2000},
            'comment': {'min': 10, 'max': 1000},
            'proposal': {'min': 200, 'max': 10000},
            'content': {'min': 1, 'max': 5000}  # Default
        }
        
        limits = LENGTH_LIMITS.get(content_type, LENGTH_LIMITS['content'])
        content_length = len(content.strip())
        
        if content_length < limits['min']:
            return False, f"{content_type} too short (minimum {limits['min']} characters)"
        
        if content_length > limits['max']:
            return False, f"{content_type} too long (maximum {limits['max']} characters)"
        
        # Content quality checks
        quality_issues = DataValidator._check_content_quality(content, content_type)
        if quality_issues:
            return False, f"Content quality issues: {', '.join(quality_issues)}"
        
        # Prohibited content detection
        prohibited_check = DataValidator._check_prohibited_content(content)
        if not prohibited_check[0]:
            return False, prohibited_check[1]
        
        return True, f"Valid {content_type}"
    
    @staticmethod
    def validate_jurisdiction(city: str, state: str, country: str) -> Tuple[bool, str]:
        """Validate geographic jurisdiction information"""
        
        # Validate each component
        city_valid, city_msg = DataValidator.validate_name(city, "City")
        if not city_valid:
            return False, city_msg
        
        state_valid, state_msg = DataValidator.validate_name(state, "State")
        if not state_valid:
            return False, state_msg
        
        country_valid, country_msg = DataValidator.validate_name(country, "Country")
        if not country_valid:
            return False, country_msg
        
        # Additional jurisdiction-specific validation
        if len(city) > 50 or len(state) > 50 or len(country) > 50:
            return False, "Location names must be 50 characters or less"
        
        # Basic format validation
        jurisdiction_pattern = r'^[a-zA-Z\s\-\.\']+$'
        for location, name in [(city, "City"), (state, "State"), (country, "Country")]:
            if not re.match(jurisdiction_pattern, location):
                return False, f"{name} contains invalid characters"
        
        return True, "Valid jurisdiction information"
    
    @staticmethod
    def validate_datetime(datetime_str: str, future_only: bool = False) -> Tuple[bool, str]:
        """Validate datetime strings and constraints"""
        
        if not datetime_str or not isinstance(datetime_str, str):
            return False, "Date and time must be provided"
        
        try:
            # Parse ISO format datetime
            parsed_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except ValueError:
            return False, "Invalid date/time format (use ISO format: YYYY-MM-DDTHH:MM:SS)"
        
        # Future date validation
        if future_only and parsed_datetime <= datetime.now():
            return False, "Date and time must be in the future"
        
        # Reasonable date range validation
        min_date = datetime(1900, 1, 1)
        max_date = datetime(2100, 12, 31)
        
        if parsed_datetime < min_date or parsed_datetime > max_date:
            return False, "Date must be between 1900 and 2100"
        
        return True, "Valid date and time"
    
    @staticmethod
    def validate_token_amount(amount: Any) -> Tuple[bool, str]:
        """Validate CivicCoin (CVC) transaction amounts"""
        
        # Type validation
        if not isinstance(amount, (int, float)):
            try:
                amount = float(amount)
            except (ValueError, TypeError):
                return False, "Token amount must be a number"
        
        # Convert to integer (tokens are whole numbers)
        if isinstance(amount, float):
            if amount != int(amount):
                return False, "Token amounts must be whole numbers"
            amount = int(amount)
        
        # Range validation
        if amount < 0:
            return False, "Token amount cannot be negative"
        
        if amount == 0:
            return False, "Token amount must be greater than zero"
        
        if amount > 1000000:  # 1 million token limit per transaction
            return False, "Token amount too large (maximum 1,000,000 per transaction)"
        
        return True, f"Valid token amount: {amount}"
    
    @staticmethod
    def sanitize_input(input_str: str, max_length: int = None) -> str:
        """Sanitize user input for safe processing"""
        
        if not isinstance(input_str, str):
            input_str = str(input_str)
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in input_str if ord(char) >= 32 or char in '\n\r\t')
        
        # Strip leading/trailing whitespace
        sanitized = sanitized.strip()
        
        # Truncate if necessary
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length].strip()
        
        # HTML entity encoding for safety
        html_escape_table = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;'
        }
        
        for char, escape in html_escape_table.items():
            sanitized = sanitized.replace(char, escape)
        
        return sanitized
    
    @staticmethod
    def _has_sequential_chars(password: str, max_sequential: int = 3) -> bool:
        """Check for excessive sequential characters in password"""
        
        sequential_count = 1
        for i in range(1, len(password)):
            if ord(password[i]) == ord(password[i-1]) + 1:
                sequential_count += 1
                if sequential_count >= max_sequential:
                    return True
            else:
                sequential_count = 1
        
        return False
    
    @staticmethod
    def _check_content_quality(content: str, content_type: str) -> List[str]:
        """Check content quality and provide improvement suggestions"""
        
        issues = []
        
        # Basic quality checks
        if len(content.split()) < 5:
            issues.append("content too brief, needs more detail")
        
        # Repetition check
        words = content.lower().split()
        if len(set(words)) < len(words) * 0.6:  # 60% unique words minimum
            issues.append("excessive word repetition")
        
        # All caps check
        if content.isupper() and len(content) > 20:
            issues.append("excessive use of capital letters")
        
        # Profanity and inappropriate content (basic check)
        inappropriate_words = ['spam', 'scam', 'fake', 'lie', 'stupid', 'idiot']
        content_lower = content.lower()
        for word in inappropriate_words:
            if word in content_lower:
                issues.append(f"potentially inappropriate language: '{word}'")
                break
        
        return issues
    
    @staticmethod
    def _check_prohibited_content(content: str) -> Tuple[bool, str]:
        """Check for prohibited content types"""
        
        content_lower = content.lower()
        
        # Prohibited content categories
        PROHIBITED_PATTERNS = {
            'personal_attacks': ['you are', 'you\'re stupid', 'shut up', 'idiot'],
            'spam_indicators': ['click here', 'buy now', 'limited time', 'act fast'],
            'security_threats': ['password', 'login', 'hack', 'exploit'],
            'hate_speech': ['hate', 'racist', 'discrimination'],  # Basic detection
            'misinformation': ['fake news', 'conspiracy', 'hoax']  # Basic detection
        }
        
        for category, patterns in PROHIBITED_PATTERNS.items():
            for pattern in patterns:
                if pattern in content_lower:
                    return False, f"Content may contain {category.replace('_', ' ')}"
        
        # XSS and injection attack patterns
        dangerous_patterns = [
            '<script', 'javascript:', 'data:text/html', 'vbscript:',
            'onload=', 'onclick=', 'onerror=', 'eval(', 'exec('
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                return False, "Content contains potentially dangerous code"
        
        return True, "Content passes security checks"

# Validation decorators for function parameters
def validate_email_param(func):
    """Decorator to validate email parameters"""
    def wrapper(*args, **kwargs):
        # Check for email parameter
        if 'email' in kwargs:
            valid, msg = DataValidator.validate_email(kwargs['email'])
            if not valid:
                raise ValueError(f"Email validation failed: {msg}")
        return func(*args, **kwargs)
    return wrapper

def validate_required_params(*required_params):
    """Decorator to validate required parameters"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for param in required_params:
                if param not in kwargs or not kwargs[param]:
                    raise ValueError(f"Required parameter missing: {param}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Utility functions for common operations
class PlatformUtils:
    """General utility functions for platform operations"""
    
    @staticmethod
    def generate_unique_id(prefix: str = '') -> str:
        """Generate unique identifier with optional prefix"""
        import uuid
        unique_part = str(uuid.uuid4()).replace('-', '')[:16]
        return f"{prefix}{unique_part}" if prefix else unique_part
    
    @staticmethod
    def calculate_age_from_date(birth_date: str) -> int:
        """Calculate age from birth date string"""
        try:
            birth = datetime.fromisoformat(birth_date)
            today = datetime.now()
            age = today.year - birth.year
            if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
                age -= 1
            return age
        except:
            return 0
    
    @staticmethod
    def format_datetime_for_display(datetime_str: str) -> str:
        """Format datetime for user-friendly display"""
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return datetime_str
    
    @staticmethod
    def calculate_time_difference(start_time: str, end_time: str) -> dict:
        """Calculate time difference between two ISO datetime strings"""
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            diff = end - start
            
            return {
                'total_seconds': diff.total_seconds(),
                'days': diff.days,
                'hours': diff.seconds // 3600,
                'minutes': (diff.seconds % 3600) // 60,
                'human_readable': DataValidator._format_time_difference(diff)
            }
        except:
            return {'error': 'Invalid datetime format'}
    
    @staticmethod
    def _format_time_difference(timedelta_obj) -> str:
        """Format timedelta for human reading"""
        days = timedelta_obj.days
        hours, remainder = divmod(timedelta_obj.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if days:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        return ', '.join(parts) if parts else 'Less than a minute'
```

## Integration Patterns

### Standard Validation Usage
```python
# Import validation framework
from civic_desktop.utils.validation import DataValidator, PlatformUtils

# Email validation
valid, message = DataValidator.validate_email(user_input_email)
if not valid:
    show_error_message(message)
    return

# Password validation with custom requirements
valid, message = DataValidator.validate_password(
    password, 
    min_length=12, 
    require_special=True,
    require_numbers=True,
    require_uppercase=True
)

# Content validation for civic debate
valid, message = DataValidator.validate_civic_content(
    argument_text, 
    content_type='argument'
)

# Safe input sanitization
clean_input = DataValidator.sanitize_input(user_input, max_length=1000)
```

### Decorator Usage
```python
from civic_desktop.utils.validation import validate_email_param, validate_required_params

@validate_email_param
@validate_required_params('title', 'description')
def create_debate_topic(title, description, email):
    # Function automatically validates email and required params
    pass
```

## Security Features

### Input Sanitization
- Removes dangerous characters and patterns
- Prevents XSS and injection attacks
- Handles international characters safely
- Truncates excessive input lengths

### Content Quality Assurance
- Validates civic discussion quality
- Detects spam and inappropriate content
- Enforces constructive dialogue standards
- Maintains platform dignity and respect

### Privacy Protection
- Validates personal information carefully
- Respects cultural naming conventions
- Protects against data mining attempts
- Maintains user privacy standards

## Testing Validation Framework

### Unit Tests Required
- Email format validation accuracy
- Password strength enforcement
- Content quality assessment
- Jurisdiction validation completeness
- Token amount validation security
- Input sanitization effectiveness

### Security Tests Required
- XSS prevention verification
- SQL injection prevention
- Content filtering effectiveness
- Rate limiting validation
- Privacy protection verification