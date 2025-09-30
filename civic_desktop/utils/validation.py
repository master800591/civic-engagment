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
    
    @staticmethod
    def validate_birth_date(birth_date: str) -> Tuple[bool, str, Optional[int]]:
        """Validate birth date and calculate age
        
        Args:
            birth_date: Birth date in ISO format (YYYY-MM-DD)
            
        Returns:
            Tuple of (is_valid, message, age)
        """
        if not birth_date or not isinstance(birth_date, str):
            return False, "Birth date must be provided", None
        
        try:
            # Parse the birth date
            birth_datetime = datetime.fromisoformat(birth_date.replace('Z', '+00:00').split('T')[0])
        except ValueError:
            return False, "Invalid birth date format (use YYYY-MM-DD)", None
        
        # Check if date is in reasonable range
        min_date = datetime(1900, 1, 1)
        max_date = datetime.now()
        
        if birth_datetime < min_date:
            return False, "Birth date cannot be before 1900", None
        
        if birth_datetime > max_date:
            return False, "Birth date cannot be in the future", None
        
        # Calculate age
        today = datetime.now()
        age = today.year - birth_datetime.year
        
        # Adjust if birthday hasn't occurred this year yet
        if (today.month, today.day) < (birth_datetime.month, birth_datetime.day):
            age -= 1
        
        # Validate age is reasonable (0-150 years)
        if age < 0 or age > 150:
            return False, f"Invalid age calculated: {age}", None
        
        return True, f"Valid birth date (age: {age})", age
    
    @staticmethod
    def validate_required_string(value: str, field_name: str = "Field", 
                                 min_length: int = 1, max_length: int = 1000) -> Tuple[bool, str]:
        """Validate required string field with length constraints
        
        Args:
            value: String value to validate
            field_name: Name of the field for error messages
            min_length: Minimum required length
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (is_valid, message)
        """
        if value is None or not isinstance(value, str):
            return False, f"{field_name} must be a string"
        
        value = value.strip()
        
        if len(value) < min_length:
            return False, f"{field_name} must be at least {min_length} character{'s' if min_length > 1 else ''}"
        
        if len(value) > max_length:
            return False, f"{field_name} must be no more than {max_length} characters"
        
        # Check for dangerous content
        dangerous_patterns = ['<script', 'javascript:', 'data:', 'vbscript:', 'onload=', 'onerror=']
        value_lower = value.lower()
        for pattern in dangerous_patterns:
            if pattern in value_lower:
                return False, f"{field_name} contains potentially dangerous content"
        
        return True, f"Valid {field_name.lower()}"
    
    @staticmethod
    def validate_id_document(document_data: Any) -> Tuple[bool, str]:
        """Validate ID document data
        
        Args:
            document_data: Document data (can be file path string or dict with metadata)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not document_data:
            return False, "ID document is required"
        
        # If it's a string, treat as file path
        if isinstance(document_data, str):
            return DataValidator.validate_file_upload(document_data)
        
        # If it's a dict, validate metadata
        if isinstance(document_data, dict):
            required_fields = ['document_type', 'document_number']
            
            for field in required_fields:
                if field not in document_data:
                    return False, f"Missing required ID document field: {field}"
            
            # Validate document type
            valid_types = ['passport', 'drivers_license', 'national_id', 'state_id', 'military_id']
            doc_type = document_data.get('document_type', '').lower()
            
            if doc_type not in valid_types:
                return False, f"Invalid document type. Must be one of: {', '.join(valid_types)}"
            
            # Validate document number
            doc_number = document_data.get('document_number', '').strip()
            if len(doc_number) < 5:
                return False, "Document number must be at least 5 characters"
            
            if len(doc_number) > 50:
                return False, "Document number is too long"
            
            # Check for valid characters (alphanumeric, hyphens, spaces)
            if not re.match(r'^[A-Za-z0-9\s\-]+$', doc_number):
                return False, "Document number contains invalid characters"
            
            return True, "Valid ID document"
        
        return False, "ID document must be a file path or document metadata"
    
    @staticmethod
    def validate_civic_content(content: str, content_type: str = "content") -> Tuple[bool, str]:
        """Validate civic debate content, arguments, and proposals
        
        Args:
            content: The content to validate
            content_type: Type of content (argument, topic_title, etc.)
            
        Returns:
            Tuple of (is_valid, message)
        """
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
    def _check_content_quality(content: str, content_type: str) -> List[str]:
        """Check content quality and provide improvement suggestions
        
        Args:
            content: Content to check
            content_type: Type of content
            
        Returns:
            List of quality issues found
        """
        issues = []
        
        # Basic quality checks
        words = content.split()
        if len(words) < 5:
            issues.append("content too brief, needs more detail")
        
        # Repetition check
        if len(words) > 10:
            unique_words = set(word.lower() for word in words)
            if len(unique_words) < len(words) * 0.5:  # 50% unique words minimum
                issues.append("excessive word repetition")
        
        # All caps check
        if content.isupper() and len(content) > 20:
            issues.append("excessive use of capital letters")
        
        # Excessive punctuation
        punctuation_count = sum(1 for char in content if char in '!?.')
        if punctuation_count > len(words) * 0.5:
            issues.append("excessive punctuation")
        
        # Check for constructive language in debates/arguments
        if content_type in ['argument', 'proposal']:
            # Ensure content has some substance beyond just negatives
            negative_words = ['no', 'not', 'never', 'wrong', 'bad', 'terrible', 'awful']
            negative_count = sum(1 for word in words if word.lower() in negative_words)
            
            if negative_count > len(words) * 0.3:  # More than 30% negative words
                issues.append("content appears overly negative, consider constructive framing")
        
        return issues
    
    @staticmethod
    def _check_prohibited_content(content: str) -> Tuple[bool, str]:
        """Check for prohibited content types
        
        Args:
            content: Content to check
            
        Returns:
            Tuple of (is_allowed, message)
        """
        content_lower = content.lower()
        
        # Prohibited content categories with patterns
        PROHIBITED_PATTERNS = {
            'personal_attacks': ['you are stupid', 'you\'re an idiot', 'shut up', 'you suck'],
            'spam_indicators': ['click here now', 'buy now', 'limited time offer', 'act fast', 'visit my website'],
            'security_threats': ['send me your password', 'give me your login', 'share your credentials'],
            'explicit_content': ['(blocked)', '(censored)'],  # Placeholder for actual patterns
        }
        
        for category, patterns in PROHIBITED_PATTERNS.items():
            for pattern in patterns:
                if pattern in content_lower:
                    return False, f"Content may contain {category.replace('_', ' ')}"
        
        # XSS and injection attack patterns
        dangerous_patterns = [
            '<script', 'javascript:', 'data:text/html', 'vbscript:',
            'onload=', 'onclick=', 'onerror=', 'eval(', 'exec(',
            '<iframe', '<object', '<embed'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                return False, "Content contains potentially dangerous code"
        
        # SQL injection patterns
        sql_patterns = ["'; drop table", "' or '1'='1", "'; delete from", "union select"]
        for pattern in sql_patterns:
            if pattern in content_lower:
                return False, "Content contains potentially dangerous SQL patterns"
        
        return True, "Content passes security checks"

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


class AdvancedValidator:
    """Advanced validation for complex civic engagement platform features"""
    
    @staticmethod
    def validate_document_metadata(metadata: Dict) -> Tuple[bool, str]:
        """Validate document metadata for the documents module"""
        required_fields = ['title', 'document_type', 'classification', 'author', 'created_date']
        
        if not isinstance(metadata, dict):
            return False, "Metadata must be a dictionary"
        
        for field in required_fields:
            if field not in metadata:
                return False, f"Missing required metadata field: {field}"
        
        # Validate document type
        valid_doc_types = [
            'legislative_bill', 'constitutional_amendment', 'policy_document',
            'meeting_minutes', 'court_decision', 'administrative_order',
            'public_notice', 'budget_document', 'audit_report'
        ]
        
        if metadata['document_type'] not in valid_doc_types:
            return False, f"Invalid document type. Must be one of: {', '.join(valid_doc_types)}"
        
        # Validate classification
        valid_classifications = ['public', 'restricted', 'confidential', 'classified']
        if metadata['classification'] not in valid_classifications:
            return False, f"Invalid classification. Must be one of: {', '.join(valid_classifications)}"
        
        # Validate title length
        title = metadata['title']
        if not isinstance(title, str) or len(title.strip()) < 5:
            return False, "Document title must be at least 5 characters"
        
        if len(title) > 200:
            return False, "Document title cannot exceed 200 characters"
        
        return True, "Valid document metadata"
    
    @staticmethod
    def validate_collaboration_agreement(agreement: Dict) -> Tuple[bool, str]:
        """Validate inter-jurisdictional collaboration agreement data"""
        required_fields = [
            'title', 'participating_jurisdictions', 'project_type', 
            'governance_model', 'resource_commitments', 'duration'
        ]
        
        if not isinstance(agreement, dict):
            return False, "Agreement must be a dictionary"
        
        for field in required_fields:
            if field not in agreement:
                return False, f"Missing required agreement field: {field}"
        
        # Validate participating jurisdictions
        jurisdictions = agreement['participating_jurisdictions']
        if not isinstance(jurisdictions, list) or len(jurisdictions) < 2:
            return False, "Must have at least 2 participating jurisdictions"
        
        # Validate project type
        valid_project_types = [
            'resource_sharing', 'policy_coordination', 'infrastructure_development',
            'emergency_response', 'research_collaboration', 'service_provision'
        ]
        
        if agreement['project_type'] not in valid_project_types:
            return False, f"Invalid project type. Must be one of: {', '.join(valid_project_types)}"
        
        # Validate governance model
        valid_governance_models = ['consensus', 'majority', 'weighted', 'lead_authority']
        if agreement['governance_model'] not in valid_governance_models:
            return False, f"Invalid governance model. Must be one of: {', '.join(valid_governance_models)}"
        
        return True, "Valid collaboration agreement"
    
    @staticmethod
    def validate_task_assignment(task_data: Dict) -> Tuple[bool, str]:
        """Validate task assignment data for the tasks module"""
        required_fields = ['task_type', 'assigned_to', 'title', 'deadline', 'priority']
        
        if not isinstance(task_data, dict):
            return False, "Task data must be a dictionary"
        
        for field in required_fields:
            if field not in task_data:
                return False, f"Missing required task field: {field}"
        
        # Validate task type
        valid_task_types = [
            'blockchain_validation', 'voting_opportunity', 'contract_review',
            'jury_duty', 'community_service', 'emergency_response',
            'training_completion', 'research_assignment', 'outreach_activity',
            'mediation_service', 'audit_participation', 'platform_testing'
        ]
        
        if task_data['task_type'] not in valid_task_types:
            return False, f"Invalid task type. Must be one of: {', '.join(valid_task_types)}"
        
        # Validate priority
        valid_priorities = ['urgent', 'high', 'normal', 'low']
        if task_data['priority'] not in valid_priorities:
            return False, f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
        
        # Validate deadline format
        try:
            if isinstance(task_data['deadline'], str):
                datetime.fromisoformat(task_data['deadline'])
            elif not isinstance(task_data['deadline'], datetime):
                return False, "Deadline must be a datetime object or ISO format string"
        except ValueError:
            return False, "Invalid deadline format"
        
        # Validate assigned_to email
        email_valid, email_msg = DataValidator.validate_email(task_data['assigned_to'])
        if not email_valid:
            return False, f"Invalid assignee email: {email_msg}"
        
        return True, "Valid task assignment"
    
    @staticmethod
    def validate_onboarding_progress(progress_data: Dict) -> Tuple[bool, str]:
        """Validate user onboarding progress data"""
        required_fields = ['user_email', 'pathway', 'current_module', 'completion_percentage']
        
        if not isinstance(progress_data, dict):
            return False, "Progress data must be a dictionary"
        
        for field in required_fields:
            if field not in progress_data:
                return False, f"Missing required progress field: {field}"
        
        # Validate email
        email_valid, email_msg = DataValidator.validate_email(progress_data['user_email'])
        if not email_valid:
            return False, f"Invalid user email: {email_msg}"
        
        # Validate completion percentage
        completion = progress_data['completion_percentage']
        try:
            completion = float(completion)
            if completion < 0 or completion > 100:
                return False, "Completion percentage must be between 0 and 100"
        except (ValueError, TypeError):
            return False, "Completion percentage must be a number"
        
        # Validate pathway
        valid_pathways = [
            'contract_member', 'contract_representative', 'contract_senator',
            'contract_elder', 'contract_founder'
        ]
        
        if progress_data['pathway'] not in valid_pathways:
            return False, f"Invalid pathway. Must be one of: {', '.join(valid_pathways)}"
        
        return True, "Valid onboarding progress"
    
    @staticmethod
    def validate_geographic_data(geo_data: Dict) -> Tuple[bool, str]:
        """Validate geographic/maps data"""
        required_fields = ['jurisdiction', 'coordinates', 'boundary_type']
        
        if not isinstance(geo_data, dict):
            return False, "Geographic data must be a dictionary"
        
        for field in required_fields:
            if field not in geo_data:
                return False, f"Missing required geographic field: {field}"
        
        # Validate coordinates
        coordinates = geo_data['coordinates']
        if not isinstance(coordinates, dict):
            return False, "Coordinates must be a dictionary"
        
        if 'latitude' not in coordinates or 'longitude' not in coordinates:
            return False, "Coordinates must include latitude and longitude"
        
        try:
            lat = float(coordinates['latitude'])
            lon = float(coordinates['longitude'])
            
            if lat < -90 or lat > 90:
                return False, "Latitude must be between -90 and 90"
            
            if lon < -180 or lon > 180:
                return False, "Longitude must be between -180 and 180"
        except (ValueError, TypeError):
            return False, "Latitude and longitude must be numbers"
        
        # Validate boundary type
        valid_boundary_types = ['city', 'county', 'state', 'federal', 'district', 'ward']
        if geo_data['boundary_type'] not in valid_boundary_types:
            return False, f"Invalid boundary type. Must be one of: {', '.join(valid_boundary_types)}"
        
        return True, "Valid geographic data"


class ComprehensiveValidator:
    """Comprehensive validation framework combining all validators"""
    
    @staticmethod
    def validate_complete_user_registration(registration_data: Dict) -> Tuple[bool, List[str], Dict[str, bool]]:
        """Comprehensive validation for complete user registration"""
        results = {}
        errors = []
        
        # Basic user data validation
        basic_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in basic_fields:
            if field not in registration_data:
                errors.append(f"Missing required field: {field}")
                results[field] = False
                continue
        
        # Email validation
        if 'email' in registration_data:
            email_valid, email_msg = DataValidator.validate_email(registration_data['email'])
            results['email'] = email_valid
            if not email_valid:
                errors.append(f"Email: {email_msg}")
        
        # Password validation
        if 'password' in registration_data:
            pass_valid, pass_msg = DataValidator.validate_password(registration_data['password'])
            results['password'] = pass_valid
            if not pass_valid:
                errors.append(f"Password: {pass_msg}")
        
        # Name validation
        for name_field in ['first_name', 'last_name']:
            if name_field in registration_data:
                name_valid, name_msg = DataValidator.validate_name(registration_data[name_field])
                results[name_field] = name_valid
                if not name_valid:
                    errors.append(f"{name_field.replace('_', ' ').title()}: {name_msg}")
        
        # Role validation
        if 'role' in registration_data:
            role_valid, role_msg = DataValidator.validate_user_role(registration_data['role'])
            results['role'] = role_valid
            if not role_valid:
                errors.append(f"Role: {role_msg}")
        
        # Location validation
        if 'jurisdiction' in registration_data:
            jurisdiction_valid, jurisdiction_msg = DataValidator.validate_required_string(
                registration_data['jurisdiction'], 'jurisdiction', min_length=2, max_length=100
            )
            results['jurisdiction'] = jurisdiction_valid
            if not jurisdiction_valid:
                errors.append(f"Jurisdiction: {jurisdiction_msg}")
        
        # Document validation
        if 'id_document' in registration_data:
            doc_valid, doc_msg = DataValidator.validate_id_document(registration_data['id_document'])
            results['id_document'] = doc_valid
            if not doc_valid:
                errors.append(f"ID Document: {doc_msg}")
        
        overall_valid = len(errors) == 0
        return overall_valid, errors, results
    
    @staticmethod
    def create_validation_summary(validation_results: Dict[str, bool]) -> Dict[str, Any]:
        """Create summary of validation results"""
        total_fields = len(validation_results)
        valid_fields = sum(1 for valid in validation_results.values() if valid)
        
        return {
            'total_fields': total_fields,
            'valid_fields': valid_fields,
            'invalid_fields': total_fields - valid_fields,
            'success_rate': round((valid_fields / total_fields * 100) if total_fields > 0 else 0, 1),
            'overall_status': 'passed' if valid_fields == total_fields else 'failed'
        }


# Validation decorators for function parameters
def validate_email_param(func):
    """Decorator to validate email parameters in function calls
    
    Usage:
        @validate_email_param
        def my_function(email, other_param):
            # email will be validated automatically
            pass
    """
    def wrapper(*args, **kwargs):
        # Check for email parameter
        if 'email' in kwargs:
            valid, msg = DataValidator.validate_email(kwargs['email'])
            if not valid:
                raise ValueError(f"Email validation failed: {msg}")
        return func(*args, **kwargs)
    return wrapper


def validate_required_params(*required_params):
    """Decorator to validate required parameters are present
    
    Usage:
        @validate_required_params('email', 'name', 'password')
        def my_function(email, name, password, optional_param=None):
            # All required params will be validated automatically
            pass
    """
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
        """Generate unique identifier with optional prefix
        
        Args:
            prefix: Optional prefix for the ID
            
        Returns:
            Unique identifier string
        """
        import uuid
        unique_part = str(uuid.uuid4()).replace('-', '')[:16]
        return f"{prefix}{unique_part}" if prefix else unique_part
    
    @staticmethod
    def calculate_age_from_date(birth_date: str) -> Optional[int]:
        """Calculate age from birth date string
        
        Args:
            birth_date: Birth date in ISO format (YYYY-MM-DD)
            
        Returns:
            Age in years or None if invalid date
        """
        try:
            birth = datetime.fromisoformat(birth_date.split('T')[0])
            today = datetime.now()
            age = today.year - birth.year
            
            # Adjust if birthday hasn't occurred this year yet
            if (today.month, today.day) < (birth.month, birth.day):
                age -= 1
            
            return age if 0 <= age <= 150 else None
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def format_date_for_display(date_str: str, format_type: str = 'short') -> str:
        """Format date string for user-friendly display
        
        Args:
            date_str: Date in ISO format
            format_type: 'short', 'long', or 'relative'
            
        Returns:
            Formatted date string
        """
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            if format_type == 'short':
                return date_obj.strftime('%Y-%m-%d')
            elif format_type == 'long':
                return date_obj.strftime('%B %d, %Y at %I:%M %p')
            elif format_type == 'relative':
                delta = datetime.now() - date_obj.replace(tzinfo=None)
                
                if delta.days == 0:
                    if delta.seconds < 3600:
                        return f"{delta.seconds // 60} minutes ago"
                    else:
                        return f"{delta.seconds // 3600} hours ago"
                elif delta.days == 1:
                    return "yesterday"
                elif delta.days < 7:
                    return f"{delta.days} days ago"
                elif delta.days < 30:
                    return f"{delta.days // 7} weeks ago"
                else:
                    return date_obj.strftime('%B %d, %Y')
            
            return date_str
        except (ValueError, AttributeError):
            return date_str
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system storage
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename safe for file system
        """
        # Remove potentially dangerous characters
        safe_filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)
        
        # Replace spaces with underscores
        safe_filename = safe_filename.replace(' ', '_')
        
        # Limit length
        if len(safe_filename) > 255:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:255 - len(ext)] + ext
        
        return safe_filename or 'unnamed_file'
    
    @staticmethod
    def hash_sensitive_data(data: str, algorithm: str = 'sha256') -> str:
        """Hash sensitive data for secure storage
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm to use (sha256, sha512, md5)
            
        Returns:
            Hexadecimal hash string
        """
        import hashlib
        
        if algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data.encode()).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        else:
            return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
        """Truncate text to specified length with suffix
        
        Args:
            text: Text to truncate
            max_length: Maximum length including suffix
            suffix: Suffix to append to truncated text
            
        Returns:
            Truncated text
        """
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)].strip() + suffix
        
        return True, f"User has required permission: {required_permission}"