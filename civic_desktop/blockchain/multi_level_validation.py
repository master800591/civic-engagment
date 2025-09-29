"""
MULTI-LEVEL BLOCKCHAIN VALIDATION SYSTEM
Implements geographic and role-based validation for Contract Members and government officials
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
import hashlib

class ValidationType(Enum):
    """Types of validation available for blockchain signing"""
    FOUNDER_VALIDATION = "founder_validation"
    CITY_VALIDATION = "city_validation"
    STATE_VALIDATION = "state_validation"
    COUNTRY_VALIDATION = "country_validation"
    ROLE_VALIDATION = "role_validation"

class ValidationLevel(Enum):
    """Validation security levels"""
    BASIC = "basic"           # Single validator
    STANDARD = "standard"     # Multiple validators
    SECURE = "secure"         # Geographic + role validation
    MAXIMUM = "maximum"       # All validation types required

class MultiLevelValidator:
    """
    Manages multi-level validation system for blockchain operations
    Enables Contract Members and officials to validate blocks through various methods
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize multi-level validation system"""
        self.config_path = config_path
        self.validation_db_path = Path('blockchain/validation_registry.json')
        self.validation_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Validation thresholds by jurisdiction
        self.validation_thresholds = {
            'city': {
                'minimum_validators': 3,
                'percentage_required': 0.33,  # 33% of city members
                'validation_timeout_hours': 24
            },
            'state': {
                'minimum_validators': 5,
                'percentage_required': 0.25,  # 25% of state members
                'validation_timeout_hours': 48
            },
            'country': {
                'minimum_validators': 10,
                'percentage_required': 0.20,  # 20% of country members
                'validation_timeout_hours': 72
            },
            'founder': {
                'minimum_validators': 1,
                'percentage_required': 0.10,  # 10% of founders (minimum 1)
                'validation_timeout_hours': 12
            }
        }
        
        # Initialize validation database
        self._init_validation_database()
    
    def _init_validation_database(self):
        """Initialize validation database with schema"""
        if not self.validation_db_path.exists():
            initial_data = {
                'validation_requests': {},
                'validator_registry': {
                    'members': {},          # Contract Members by location
                    'representatives': {},  # Representatives by jurisdiction
                    'senators': {},         # Senators by jurisdiction
                    'elders': {},          # Elders (constitutional guardians)
                    'founders': {}         # Founders (genesis authority)
                },
                'validation_history': [],
                'geographic_structure': {
                    'cities': {},
                    'states': {},
                    'countries': {}
                },
                'validation_rules': {
                    'member_validation_enabled': True,
                    'geographic_validation_required': True,
                    'minimum_validation_levels': 2,
                    'consensus_threshold': 0.51
                },
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.validation_db_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2)
    
    def register_member_validator(self, user_email: str, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Register a Contract Member as a blockchain validator
        
        Args:
            user_email: Member's email address
            user_data: User information including location and role
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            validation_data = self._load_validation_data()
            
            # Extract user information
            role = user_data.get('role', 'contract_member')
            city = user_data.get('city', '').strip().lower()
            state = user_data.get('state', '').strip().lower()
            country = user_data.get('country', '').strip().lower()
            
            # Validate role eligibility
            if role not in ['contract_member', 'contract_representative', 'contract_senator', 'contract_elder', 'contract_founder']:
                return False, f"Role {role} not eligible for blockchain validation"
            
            # Create validator record
            validator_record = {
                'user_email': user_email,
                'role': role,
                'city': city,
                'state': state,
                'country': country,
                'registered_at': datetime.now().isoformat(),
                'status': 'active',
                'validation_count': 0,
                'last_validation': None,
                'public_key': user_data.get('rsa_public_key', ''),
                'validator_id': hashlib.sha256(f"{user_email}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            }
            
            # Add to appropriate role category
            role_category = self._get_role_category(role)
            validation_data['validator_registry'][role_category][user_email] = validator_record
            
            # Update geographic structure
            self._update_geographic_structure(validation_data, city, state, country, user_email)
            
            # Save updated data
            self._save_validation_data(validation_data)
            
            return True, f"Contract Member registered as validator: {role} in {city}, {state}, {country}"
            
        except Exception as e:
            return False, f"Error registering member validator: {str(e)}"
    
    def _get_role_category(self, role: str) -> str:
        """Get the validator registry category for a role"""
        role_mapping = {
            'contract_member': 'members',
            'contract_representative': 'representatives',
            'contract_senator': 'senators',
            'contract_elder': 'elders',
            'contract_founder': 'founders'
        }
        return role_mapping.get(role, 'members')
    
    def _update_geographic_structure(self, validation_data: Dict[str, Any], city: str, state: str, country: str, user_email: str):
        """Update geographic validation structure"""
        geo_structure = validation_data['geographic_structure']
        
        # Initialize country if not exists
        if country not in geo_structure['countries']:
            geo_structure['countries'][country] = {
                'states': {},
                'total_members': 0,
                'active_validators': []
            }
        
        # Initialize state if not exists
        if state not in geo_structure['countries'][country]['states']:
            geo_structure['countries'][country]['states'][state] = {
                'cities': {},
                'total_members': 0,
                'active_validators': []
            }
        
        # Initialize city if not exists
        if city not in geo_structure['countries'][country]['states'][state]['cities']:
            geo_structure['countries'][country]['states'][state]['cities'][city] = {
                'total_members': 0,
                'active_validators': []
            }
        
        # Add user to appropriate locations
        geo_structure['countries'][country]['active_validators'].append(user_email)
        geo_structure['countries'][country]['states'][state]['active_validators'].append(user_email)
        geo_structure['countries'][country]['states'][state]['cities'][city]['active_validators'].append(user_email)
        
        # Update counts
        geo_structure['countries'][country]['total_members'] += 1
        geo_structure['countries'][country]['states'][state]['total_members'] += 1
        geo_structure['countries'][country]['states'][state]['cities'][city]['total_members'] += 1
    
    def create_validation_request(self, block_hash: str, validation_level: ValidationLevel, 
                                  requester_email: str, block_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new validation request for a blockchain block
        
        Args:
            block_hash: Hash of the block to validate
            validation_level: Required validation level
            requester_email: Email of user requesting validation
            block_data: Block data to validate
            
        Returns:
            Tuple of (success: bool, message: str, request_id: Optional[str])
        """
        try:
            validation_data = self._load_validation_data()
            
            # Generate request ID
            request_id = hashlib.sha256(f"{block_hash}_{requester_email}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            # Determine required validation types based on level
            required_validations = self._get_required_validations(validation_level)
            
            # Create validation request
            validation_request = {
                'request_id': request_id,
                'block_hash': block_hash,
                'requester_email': requester_email,
                'validation_level': validation_level.value,
                'required_validations': required_validations,
                'block_data': block_data,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=48)).isoformat(),
                'status': 'pending',
                'validations_received': {
                    'founder': [],
                    'city': [],
                    'state': [],
                    'country': [],
                    'role': []
                },
                'consensus_reached': False,
                'final_result': None
            }
            
            # Add to validation requests
            validation_data['validation_requests'][request_id] = validation_request
            
            # Save updated data
            self._save_validation_data(validation_data)
            
            return True, f"Validation request created: {request_id}", request_id
            
        except Exception as e:
            return False, f"Error creating validation request: {str(e)}", None
    
    def _get_required_validations(self, validation_level: ValidationLevel) -> List[str]:
        """Get required validation types for a validation level"""
        validation_requirements = {
            ValidationLevel.BASIC: ['city'],
            ValidationLevel.STANDARD: ['city', 'state'],
            ValidationLevel.SECURE: ['city', 'state', 'country'],
            ValidationLevel.MAXIMUM: ['founder', 'city', 'state', 'country', 'role']
        }
        return validation_requirements.get(validation_level, ['city'])
    
    def submit_member_validation(self, request_id: str, validator_email: str, 
                                 validation_type: ValidationType, approve: bool, 
                                 signature: str = None) -> Tuple[bool, str]:
        """
        Submit a validation from a Contract Member or official
        
        Args:
            request_id: ID of the validation request
            validator_email: Email of the validator
            validation_type: Type of validation being submitted
            approve: Whether the validator approves the block
            signature: Cryptographic signature (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            validation_data = self._load_validation_data()
            
            # Check if request exists
            if request_id not in validation_data['validation_requests']:
                return False, "Validation request not found"
            
            request = validation_data['validation_requests'][request_id]
            
            # Check if request is still active
            if request['status'] != 'pending':
                return False, f"Validation request is {request['status']}, cannot accept new validations"
            
            # Check if request has expired
            if datetime.now() > datetime.fromisoformat(request['expires_at']):
                request['status'] = 'expired'
                self._save_validation_data(validation_data)
                return False, "Validation request has expired"
            
            # Verify validator eligibility
            validator_eligible, eligibility_message = self._check_validator_eligibility(
                validation_data, validator_email, validation_type, request
            )
            
            if not validator_eligible:
                return False, eligibility_message
            
            # Create validation record
            validation_record = {
                'validator_email': validator_email,
                'validation_type': validation_type.value,
                'approval': approve,
                'timestamp': datetime.now().isoformat(),
                'signature': signature,
                'validator_location': self._get_validator_location(validation_data, validator_email)
            }
            
            # Add validation to appropriate category
            validation_category = validation_type.value.replace('_validation', '')
            request['validations_received'][validation_category].append(validation_record)
            
            # Update validator statistics
            self._update_validator_stats(validation_data, validator_email)
            
            # Check if consensus reached
            consensus_reached, consensus_result = self._check_consensus(request, validation_data)
            
            if consensus_reached:
                request['status'] = 'completed'
                request['consensus_reached'] = True
                request['final_result'] = consensus_result
                request['completed_at'] = datetime.now().isoformat()
            
            # Save updated data
            self._save_validation_data(validation_data)
            
            return True, f"Validation submitted successfully. Consensus: {'Reached' if consensus_reached else 'Pending'}"
            
        except Exception as e:
            return False, f"Error submitting validation: {str(e)}"
    
    def _check_validator_eligibility(self, validation_data: Dict[str, Any], validator_email: str, 
                                     validation_type: ValidationType, request: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if a validator is eligible to provide a specific type of validation"""
        
        # Find validator in registry
        validator = None
        for category, validators in validation_data['validator_registry'].items():
            if validator_email in validators:
                validator = validators[validator_email]
                break
        
        if not validator:
            return False, "Validator not found in registry"
        
        if validator.get('status') != 'active':
            return False, "Validator is not active"
        
        # Check validation type eligibility
        if validation_type == ValidationType.FOUNDER_VALIDATION:
            if validator.get('role') != 'contract_founder':
                return False, "Only Contract Founders can provide founder validation"
        
        elif validation_type in [ValidationType.CITY_VALIDATION, ValidationType.STATE_VALIDATION, ValidationType.COUNTRY_VALIDATION]:
            # Get requester's location for geographic validation
            requester_location = self._get_validator_location(validation_data, request['requester_email'])
            validator_location = self._get_validator_location(validation_data, validator_email)
            
            if not requester_location or not validator_location:
                return False, "Cannot determine geographic eligibility"
            
            # Check geographic overlap
            if validation_type == ValidationType.CITY_VALIDATION:
                if validator_location['city'] != requester_location['city']:
                    return False, "Validator not in same city as requester"
            elif validation_type == ValidationType.STATE_VALIDATION:
                if validator_location['state'] != requester_location['state']:
                    return False, "Validator not in same state as requester"
            elif validation_type == ValidationType.COUNTRY_VALIDATION:
                if validator_location['country'] != requester_location['country']:
                    return False, "Validator not in same country as requester"
        
        # Check if validator already submitted validation for this request
        validation_category = validation_type.value.replace('_validation', '')
        existing_validations = request['validations_received'].get(validation_category, [])
        
        for existing in existing_validations:
            if existing['validator_email'] == validator_email:
                return False, "Validator has already submitted validation for this request"
        
        return True, "Validator is eligible"
    
    def _get_validator_location(self, validation_data: Dict[str, Any], validator_email: str) -> Optional[Dict[str, str]]:
        """Get validator's geographic location"""
        
        for category, validators in validation_data['validator_registry'].items():
            if validator_email in validators:
                validator = validators[validator_email]
                return {
                    'city': validator.get('city', ''),
                    'state': validator.get('state', ''),
                    'country': validator.get('country', '')
                }
        return None
    
    def _update_validator_stats(self, validation_data: Dict[str, Any], validator_email: str):
        """Update validator statistics after validation submission"""
        
        for category, validators in validation_data['validator_registry'].items():
            if validator_email in validators:
                validators[validator_email]['validation_count'] += 1
                validators[validator_email]['last_validation'] = datetime.now().isoformat()
                break
    
    def _check_consensus(self, request: Dict[str, Any], validation_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check if consensus has been reached for a validation request"""
        
        required_validations = request['required_validations']
        validations_received = request['validations_received']
        
        consensus_reached = True
        approval_count = 0
        total_validations = 0
        
        # Check each required validation type
        for validation_type in required_validations:
            received = validations_received.get(validation_type, [])
            threshold = self.validation_thresholds.get(validation_type, {})
            
            min_validators = threshold.get('minimum_validators', 1)
            
            if len(received) < min_validators:
                consensus_reached = False
                break
            
            # Count approvals
            approvals = sum(1 for v in received if v.get('approval', False))
            total_validations += len(received)
            approval_count += approvals
            
            # Check if minimum approval threshold met
            required_approvals = max(1, int(len(received) * threshold.get('percentage_required', 0.51)))
            
            if approvals < required_approvals:
                consensus_reached = False
                break
        
        if consensus_reached:
            # Determine final result based on overall approval rate
            overall_approval_rate = approval_count / total_validations if total_validations > 0 else 0
            
            if overall_approval_rate >= 0.51:  # Majority approval
                return True, 'approved'
            else:
                return True, 'rejected'
        
        return False, None
    
    def get_validation_status(self, request_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Get the status of a validation request"""
        
        try:
            validation_data = self._load_validation_data()
            
            if request_id not in validation_data['validation_requests']:
                return False, "Validation request not found", None
            
            request = validation_data['validation_requests'][request_id]
            
            # Calculate progress
            progress = self._calculate_validation_progress(request, validation_data)
            
            status_info = {
                'request_id': request_id,
                'status': request['status'],
                'consensus_reached': request.get('consensus_reached', False),
                'final_result': request.get('final_result'),
                'progress': progress,
                'created_at': request['created_at'],
                'expires_at': request['expires_at']
            }
            
            return True, "Validation status retrieved", status_info
            
        except Exception as e:
            return False, f"Error retrieving validation status: {str(e)}", None
    
    def _calculate_validation_progress(self, request: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate validation progress for a request"""
        
        progress = {}
        
        for validation_type in request['required_validations']:
            received = request['validations_received'].get(validation_type, [])
            threshold = self.validation_thresholds.get(validation_type, {})
            
            min_validators = threshold.get('minimum_validators', 1)
            approvals = sum(1 for v in received if v.get('approval', False))
            
            progress[validation_type] = {
                'received': len(received),
                'minimum_required': min_validators,
                'approvals': approvals,
                'rejections': len(received) - approvals,
                'progress_percentage': min(100, (len(received) / min_validators) * 100) if min_validators > 0 else 100
            }
        
        return progress
    
    def _load_validation_data(self) -> Dict[str, Any]:
        """Load validation data from storage"""
        try:
            with open(self.validation_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_validation_database()
            with open(self.validation_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def _save_validation_data(self, data: Dict[str, Any]):
        """Save validation data to storage"""
        data['last_updated'] = datetime.now().isoformat()
        with open(self.validation_db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

# Convenience functions for external use
def register_member_as_validator(user_email: str, user_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Register a Contract Member as blockchain validator"""
    validator = MultiLevelValidator()
    return validator.register_member_validator(user_email, user_data)

def create_block_validation_request(block_hash: str, validation_level: ValidationLevel, 
                                    requester_email: str, block_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
    """Create validation request for blockchain block"""
    validator = MultiLevelValidator()
    return validator.create_validation_request(block_hash, validation_level, requester_email, block_data)

def submit_validation(request_id: str, validator_email: str, validation_type: ValidationType, 
                      approve: bool, signature: str = None) -> Tuple[bool, str]:
    """Submit validation for a block"""
    validator = MultiLevelValidator()
    return validator.submit_member_validation(request_id, validator_email, validation_type, approve, signature)

def get_validation_request_status(request_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Get status of validation request"""
    validator = MultiLevelValidator()
    return validator.get_validation_status(request_id)

if __name__ == "__main__":
    # Test the multi-level validation system
    print("🏛️ Testing Multi-Level Blockchain Validation System")
    
    validator = MultiLevelValidator()
    
    # Test member registration
    test_user_data = {
        'email': 'alice.member@civic.test',
        'role': 'contract_member',
        'city': 'Democracy City',
        'state': 'Freedom State',
        'country': 'United States',
        'rsa_public_key': 'test_public_key_data'
    }
    
    success, message = validator.register_member_validator('alice.member@civic.test', test_user_data)
    print(f"Member Registration: {'✅' if success else '❌'} {message}")
    
    # Test validation request
    test_block_data = {
        'action_type': 'test_governance_action',
        'data': {'description': 'Test constitutional action'}
    }
    
    success, message, request_id = validator.create_validation_request(
        'test_block_hash_123', 
        ValidationLevel.STANDARD,
        'alice.member@civic.test',
        test_block_data
    )
    
    print(f"Validation Request: {'✅' if success else '❌'} {message}")
    if request_id:
        print(f"   Request ID: {request_id}")
    
    print("🏛️ Multi-Level Validation System Initialized Successfully!")