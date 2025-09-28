"""
CONTRACT ROLES SYSTEM - Constitutional governance roles and permissions management
Defines and manages the contract-based governance hierarchy with checks and balances
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum

class ContractRole(Enum):
    """Constitutional contract roles with hierarchical authority"""
    
    # Members - Base democratic participation
    CONTRACT_MEMBER = "contract_member"
    
    # Legislative Branch - People's Representatives
    CONTRACT_REPRESENTATIVE = "contract_representative"  # House of People
    CONTRACT_SENATOR = "contract_senator"              # Deliberative Upper House
    
    # City/Town Local Government - Municipal Representatives
    CITY_REPRESENTATIVE = "city_representative"        # Local city representatives
    CITY_SENATOR = "city_senator"                     # Local city senators
    TOWN_REPRESENTATIVE = "town_representative"        # Local town representatives  
    TOWN_SENATOR = "town_senator"                     # Local town senators
    
    # Judicial/Advisory Branch - Constitutional Guardians  
    CONTRACT_ELDER = "contract_elder"                  # Wisdom Council with veto power
    
    # Executive Authority - Genesis Leadership
    CONTRACT_FOUNDER = "contract_founder"              # Constitutional architects

class ContractPermissions:
    """Defines permissions and limitations for each contract role"""
    
    # Contract Member Permissions (Base democratic rights)
    MEMBER_PERMISSIONS = {
        'electoral_rights': [
            'vote_in_elections',
            'run_for_representative', 
            'run_for_senator',
            'participate_referendums'
        ],
        'participation_rights': [
            'create_debate_topics',
            'submit_arguments',
            'vote_on_arguments', 
            'flag_content',
            'appeal_moderation'
        ],
        'civic_rights': [
            'access_blockchain_records',
            'petition_for_amendments',
            'recall_officials',
            'access_public_documents'
        ],
        'constitutional_protections': [
            'due_process_rights',
            'equal_participation',
            'free_expression',
            'privacy_protection'
        ]
    }
    
    # Contract Representative Permissions (Legislative initiative)
    REPRESENTATIVE_PERMISSIONS = {
        **MEMBER_PERMISSIONS,
        'legislative_powers': [
            'propose_legislation',
            'budget_authority',
            'impeachment_power',
            'platform_oversight',
            'committee_creation'
        ],
        'blockchain_authority': [
            'validator_eligibility',
            'block_signing_rights',
            'consensus_participation'
        ],
        'term_info': {
            'term_length': '2_years',
            'term_limit': 'unlimited',
            'election_cycle': 'biennial'
        }
    }
    
    # Contract Senator Permissions (Deliberative review)
    SENATOR_PERMISSIONS = {
        **MEMBER_PERMISSIONS,
        'legislative_powers': [
            'review_representative_proposals',
            'deliberative_delay_authority',
            'confirmation_power',
            'elder_veto_override',  # Requires 67% supermajority
            'treaty_ratification'
        ],
        'blockchain_authority': [
            'validator_eligibility',
            'block_signing_rights', 
            'consensus_participation'
        ],
        'checks_powers': [
            'override_elder_veto',  # 67% supermajority required
            'judicial_appointment_confirmation',
            'emergency_protocol_review'
        ],
        'term_info': {
            'term_length': '6_years',
            'term_limit': '2_consecutive_terms',
            'election_cycle': 'staggered_thirds'
        }
    }
    
    # Contract Elder Permissions (Constitutional guardians)
    ELDER_PERMISSIONS = {
        **MEMBER_PERMISSIONS,
        'constitutional_powers': [
            'constitutional_veto',      # 60% Elder consensus required
            'judicial_review',
            'contract_interpretation',
            'elder_veto_authority',     # 75% Elder consensus for major decisions
            'appointment_authority'
        ],
        'oversight_powers': [
            'monitor_constitutional_compliance',
            'resolve_branch_disputes',
            'emergency_mediation',
            'precedent_establishment'
        ],
        'limitations': [
            'cannot_initiate_legislation',
            'cannot_directly_govern',
            'subject_to_citizen_recall',  # 55% turnout + 60% approval
            'cannot_override_founder_emergency'
        ],
        'term_info': {
            'term_length': '4_years',
            'term_limit': '3_consecutive_terms',
            'selection_method': 'elected_by_representatives_and_senators'
        }
    }
    
    # City Representative Permissions (Municipal legislative)
    CITY_REPRESENTATIVE_PERMISSIONS = {
        **MEMBER_PERMISSIONS,
        'municipal_powers': [
            'propose_city_ordinances',
            'city_budget_authority',
            'local_zoning_decisions',
            'municipal_service_oversight',
            'local_economic_development'
        ],
        'blockchain_authority': [
            'city_validator_eligibility',
            'municipal_block_signing',
            'local_consensus_participation'
        ],
        'term_info': {
            'term_length': '1_year',
            'term_limit': '4_total_terms',
            'consecutive_restriction': True,  # Cannot serve consecutive terms
            'election_trigger': 'population_threshold',  # 1% initial, 50% expansion
            'jurisdiction': 'city_level'
        }
    }
    
    # City Senator Permissions (Municipal deliberative)
    CITY_SENATOR_PERMISSIONS = {
        **MEMBER_PERMISSIONS,
        'municipal_powers': [
            'review_city_representative_proposals',
            'municipal_deliberative_authority',
            'city_appointment_confirmations',
            'local_constitutional_oversight',
            'inter_city_coordination'
        ],
        'blockchain_authority': [
            'city_validator_eligibility',
            'municipal_block_signing',
            'local_consensus_participation'
        ],
        'term_info': {
            'term_length': '1_year',
            'term_limit': '4_total_terms',
            'consecutive_restriction': True,  # Cannot serve consecutive terms
            'election_trigger': 'population_threshold',  # 1% initial, 50% expansion
            'jurisdiction': 'city_level'
        }
    }
    
    # Town Representative/Senator Permissions (Same as city but for towns)
    TOWN_REPRESENTATIVE_PERMISSIONS = CITY_REPRESENTATIVE_PERMISSIONS.copy()
    TOWN_SENATOR_PERMISSIONS = CITY_SENATOR_PERMISSIONS.copy()
    
    # Contract Founder Permissions (Genesis authority)
    FOUNDER_PERMISSIONS = {
        **MEMBER_PERMISSIONS,
        'constitutional_authority': [
            'modify_core_governance_contracts',  # 75%+ Founder consensus
            'emergency_protocol_override',
            'initial_elder_appointment',        # Transition power only
            'platform_architecture_changes'
        ],
        'emergency_powers': [
            'constitutional_emergency_declaration',
            'platform_threat_response',
            'critical_system_override'
        ],
        'limitations': [
            'cannot_directly_govern_operations',
            'cannot_override_elected_decisions',  # Except emergencies
            'subject_to_elder_senator_removal',   # 2/3 combined vote
            'supermajority_consensus_required'    # 75%+ for major actions
        ],
        'term_info': {
            'term_length': 'lifetime',
            'term_limit': 'max_7_founders',
            'removal_process': 'elder_senator_consensus'
        }
    }

class ContractRoleManager:
    """Manages contract role assignments, permissions, and governance workflows"""
    
    def __init__(self, config_path: str = None):
        """Initialize contract role manager"""
        if config_path:
            self.config = self._load_config(config_path)
            self.roles_db_path = Path(self.config.get('contract_roles_db', 'contracts/contract_roles.json'))
            self.elections_db_path = Path(self.config.get('elections_db', 'contracts/elections.json'))
        else:
            self.roles_db_path = Path('contracts/contract_roles.json')
            self.elections_db_path = Path('contracts/elections.json')
            
        # Ensure directories exist
        self.roles_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.elections_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize databases
        self._init_role_database()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _init_role_database(self):
        """Initialize contract roles database"""
        if not self.roles_db_path.exists():
            initial_data = {
                'contract_roles': {
                    'members': {},
                    'representatives': {},
                    'senators': {},
                    'city_representatives': {},
                    'city_senators': {},
                    'town_representatives': {},
                    'town_senators': {},
                    'elders': {},
                    'founders': {}
                },
                'role_assignments': [],
                'permission_matrix': {
                    'contract_member': ContractPermissions.MEMBER_PERMISSIONS,
                    'contract_representative': ContractPermissions.REPRESENTATIVE_PERMISSIONS,
                    'contract_senator': ContractPermissions.SENATOR_PERMISSIONS,
                    'contract_elder': ContractPermissions.ELDER_PERMISSIONS,
                    'contract_founder': ContractPermissions.FOUNDER_PERMISSIONS
                },
                'governance_structure': {
                    'max_founders': 7,
                    'representative_terms': '2_years',
                    'senator_terms': '6_years',
                    'elder_terms': '4_years',
                    'founder_terms': 'lifetime'
                },
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.roles_db_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2)
    
    def assign_contract_role(self, user_email: str, new_role: ContractRole, 
                           assignment_method: str = 'appointment', 
                           assigned_by: str = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Assign a contract role to a user with proper authorization checks
        
        Args:
            user_email: Email of user to assign role
            new_role: ContractRole enum value
            assignment_method: 'election', 'appointment', 'founder_key', 'promotion'
            assigned_by: Email of user making assignment (for authorization)
        
        Returns:
            Tuple of (success: bool, message: str, role_info: Optional[Dict])
        """
        try:
            # Load current role data
            with open(self.roles_db_path, 'r', encoding='utf-8') as f:
                roles_data = json.load(f)
            
            # Validate assignment authority
            if not self._validate_role_assignment_authority(new_role, assignment_method, assigned_by):
                return False, f"Insufficient authority to assign {new_role.value}", None
            
            # Check role-specific constraints
            if new_role == ContractRole.CONTRACT_FOUNDER:
                # Check Founder limits
                founder_count = len(roles_data['contract_roles']['founders'])
                if founder_count >= 7:
                    return False, "Maximum of 7 Founders allowed per constitutional framework", None
            
            # Create role assignment record
            role_assignment = {
                'user_email': user_email,
                'role': new_role.value,
                'assignment_method': assignment_method,
                'assigned_by': assigned_by,
                'assigned_at': datetime.now().isoformat(),
                'term_start': datetime.now().isoformat(),
                'term_end': self._calculate_term_end(new_role),
                'active': True,
                'assignment_id': f"{new_role.value}_{datetime.now().timestamp()}"
            }
            
            # Add to appropriate role category
            role_category = self._get_role_category(new_role)
            roles_data['contract_roles'][role_category][user_email] = role_assignment
            
            # Add to assignment history
            roles_data['role_assignments'].append(role_assignment)
            
            # Update metadata
            roles_data['last_updated'] = datetime.now().isoformat()
            
            # Save updated data
            with open(self.roles_db_path, 'w', encoding='utf-8') as f:
                json.dump(roles_data, f, indent=2)
            
            return True, f"Role {new_role.value} assigned to {user_email}", role_assignment
        
        except Exception as e:
            return False, f"Error assigning role: {str(e)}", None
    
    def get_user_role(self, user_email: str) -> Tuple[bool, str, Optional[ContractRole]]:
        """
        Get the current contract role for a user
        
        Args:
            user_email: Email of user to check
        
        Returns:
            Tuple of (success: bool, message: str, role: Optional[ContractRole])
        """
        try:
            with open(self.roles_db_path, 'r', encoding='utf-8') as f:
                roles_data = json.load(f)
            
            # Check each role category
            for category, users in roles_data['contract_roles'].items():
                if user_email in users:
                    role_info = users[user_email]
                    if role_info.get('active', False):
                        role_enum = ContractRole(role_info['role'])
                        return True, f"User role: {role_enum.value}", role_enum
            
            # Default to Contract Member if no specific role assigned
            return True, "Default role: contract_member", ContractRole.CONTRACT_MEMBER
            
        except Exception as e:
            return False, f"Error retrieving user role: {str(e)}", None
    
    def check_user_permission(self, user_email: str, permission: str) -> Tuple[bool, str, bool]:
        """
        Check if a user has a specific permission based on their contract role
        
        Args:
            user_email: Email of user to check
            permission: Permission string to validate
        
        Returns:
            Tuple of (success: bool, message: str, has_permission: bool)
        """
        try:
            # Get user's role
            success, message, user_role = self.get_user_role(user_email)
            if not success:
                return False, message, False
            
            # Load permissions
            with open(self.roles_db_path, 'r', encoding='utf-8') as f:
                roles_data = json.load(f)
            
            # Get role permissions
            role_permissions = roles_data['permission_matrix'].get(user_role.value, {})
            
            # Check permission in all categories
            for category, permissions in role_permissions.items():
                if isinstance(permissions, list) and permission in permissions:
                    return True, f"Permission granted: {permission}", True
                elif isinstance(permissions, dict):
                    for subcategory, subperms in permissions.items():
                        if isinstance(subperms, list) and permission in subperms:
                            return True, f"Permission granted: {permission}", True
            
            return True, f"Permission denied: {permission}", False
        
        except Exception as e:
            return False, f"Error checking permission: {str(e)}", False
    
    def get_role_permissions(self, role: ContractRole) -> Dict[str, Any]:
        """Get all permissions for a specific contract role"""
        permission_map = {
            ContractRole.CONTRACT_MEMBER: ContractPermissions.MEMBER_PERMISSIONS,
            ContractRole.CONTRACT_REPRESENTATIVE: ContractPermissions.REPRESENTATIVE_PERMISSIONS,
            ContractRole.CONTRACT_SENATOR: ContractPermissions.SENATOR_PERMISSIONS,
            ContractRole.CONTRACT_ELDER: ContractPermissions.ELDER_PERMISSIONS,
            ContractRole.CONTRACT_FOUNDER: ContractPermissions.FOUNDER_PERMISSIONS
        }
        return permission_map.get(role, ContractPermissions.MEMBER_PERMISSIONS)
    
    def _validate_role_assignment_authority(self, new_role: ContractRole, 
                                          assignment_method: str, 
                                          assigned_by: str) -> bool:
        """Validate if the assigner has authority to assign the specified role"""
        if assignment_method == 'founder_key':
            # Founder key validation handled by FounderKeyManager
            return True
        
        if assignment_method == 'initial_setup':
            # Allow during platform initialization
            return True
        
        if not assigned_by:
            return False
        
        # Get assigner's role
        success, _, assigner_role = self.get_user_role(assigned_by)
        if not success:
            return False
        
        # Role assignment rules
        if new_role == ContractRole.CONTRACT_FOUNDER:
            # Only Founders can assign Founder role (or founder_key method)
            return assigner_role == ContractRole.CONTRACT_FOUNDER
        
        elif new_role == ContractRole.CONTRACT_ELDER:
            # Representatives and Senators can elect Elders
            return assigner_role in [ContractRole.CONTRACT_REPRESENTATIVE, 
                                   ContractRole.CONTRACT_SENATOR, 
                                   ContractRole.CONTRACT_FOUNDER]
        
        elif new_role in [ContractRole.CONTRACT_REPRESENTATIVE, ContractRole.CONTRACT_SENATOR]:
            # Elected positions - election process validation
            return assignment_method == 'election'
        
        return True  # Contract Citizens can be assigned by any higher role
    
    def _get_role_category(self, role: ContractRole) -> str:
        """Get the database category for a role"""
        role_categories = {
            ContractRole.CONTRACT_MEMBER: 'members',
            ContractRole.CONTRACT_REPRESENTATIVE: 'representatives',
            ContractRole.CONTRACT_SENATOR: 'senators', 
            ContractRole.CONTRACT_ELDER: 'elders',
            ContractRole.CONTRACT_FOUNDER: 'founders'
        }
        return role_categories.get(role, 'members')
    
    def _calculate_term_end(self, role: ContractRole) -> Optional[str]:
        """Calculate term end date based on role"""
        if role == ContractRole.CONTRACT_FOUNDER:
            return None  # Lifetime appointment
        
        term_lengths = {
            ContractRole.CONTRACT_REPRESENTATIVE: timedelta(days=730),  # 2 years
            ContractRole.CONTRACT_SENATOR: timedelta(days=2190),       # 6 years  
            ContractRole.CONTRACT_ELDER: timedelta(days=1460),         # 4 years
            ContractRole.CONTRACT_MEMBER: None  # No term limit
        }
        
        term_length = term_lengths.get(role)
        if term_length:
            end_date = datetime.now() + term_length
            return end_date.isoformat()
        
        return None
    
    def list_users_by_role(self, role: ContractRole) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        List all users with a specific contract role
        
        Args:
            role: ContractRole to list users for
        
        Returns:
            Tuple of (success: bool, message: str, users: List[Dict])
        """
        try:
            with open(self.roles_db_path, 'r', encoding='utf-8') as f:
                roles_data = json.load(f)
            
            category = self._get_role_category(role)
            role_users = roles_data['contract_roles'].get(category, {})
            
            # Filter active users
            active_users = [
                user_info for user_info in role_users.values() 
                if user_info.get('active', False)
            ]
            
            return True, f"Found {len(active_users)} active {role.value}s", active_users
        
        except Exception as e:
            return False, f"Error listing users by role: {str(e)}", []
    
    def get_governance_stats(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Get statistics about current governance structure"""
        try:
            with open(self.roles_db_path, 'r', encoding='utf-8') as f:
                roles_data = json.load(f)
            
            stats = {
                'total_citizens': len(roles_data['contract_roles']['citizens']),
                'total_representatives': len(roles_data['contract_roles']['representatives']),
                'total_senators': len(roles_data['contract_roles']['senators']),
                'total_elders': len(roles_data['contract_roles']['elders']),
                'total_founders': len(roles_data['contract_roles']['founders']),
                'max_founders_allowed': 7,
                'governance_structure': roles_data['governance_structure'],
                'last_updated': roles_data['last_updated']
            }
            
            return True, "Governance statistics retrieved", stats
        
        except Exception as e:
            return False, f"Error retrieving governance stats: {str(e)}", None