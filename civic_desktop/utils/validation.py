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
        
        return True, f"User has required permission: {required_permission}"