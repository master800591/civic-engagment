"""
CONTRACT TYPES - Hierarchical governance contracts system
Implements 4-level constitutional framework with validation and compliance checking
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# Import blockchain for recording
import sys
sys.path.append(str(Path(__file__).parent.parent))

try:
    from blockchain.blockchain import CivicBlockchain
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    print("Warning: Blockchain module not available for contracts")
    BLOCKCHAIN_AVAILABLE = False

try:
    from users.backend import UserBackend
    from users.contract_roles import ContractRole
    USER_BACKEND_AVAILABLE = True
except ImportError:
    print("Warning: User backend not available for contracts")
    USER_BACKEND_AVAILABLE = False


class ContractLevel(Enum):
    """Four-level hierarchical contract structure"""
    MASTER = 0      # Constitutional foundation
    COUNTRY = 1     # National governance
    STATE = 2       # State/regional governance
    CITY = 3        # Local/municipal governance


class ContractStatus(Enum):
    """Contract lifecycle status"""
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


# Contract hierarchy configuration
CONTRACT_HIERARCHY = {
    'Master Contract': {
        'level': ContractLevel.MASTER,
        'description': 'Constitutional foundation and fundamental rights',
        'authority': 'Contract Founders + Supermajority citizen ratification',
        'amendment_threshold': '75% Founders + 60% citizen approval',
        'immutable_sections': ['fundamental_rights', 'amendment_process', 'emergency_protocols'],
        'parent': None
    },
    'Country Contract': {
        'level': ContractLevel.COUNTRY,
        'description': 'National governance structure and federal authority',
        'authority': 'Contract Representatives + Contract Senators + Contract Elder review',
        'amendment_threshold': '60% bicameral + Elder approval + 55% citizen ratification',
        'parent': 'Master Contract'
    },
    'State Contract': {
        'level': ContractLevel.STATE,
        'description': 'State-level governance and regional authority',
        'authority': 'State Representatives + State Senators + Elder review',
        'amendment_threshold': '60% state bicameral + Elder approval',
        'parent': 'Country Contract'
    },
    'City Contract': {
        'level': ContractLevel.CITY,
        'description': 'Local governance and municipal authority',
        'authority': 'Local Representatives + citizen participation',
        'amendment_threshold': '55% local representatives + 50% local citizen approval',
        'parent': 'State Contract'
    }
}


class ContractManager:
    """Manages hierarchical governance contracts with validation and compliance"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize contract manager"""
        self.config_path = config_path or "config/dev_config.json"
        self.config = self._load_config()
        
        # Database paths
        self.contracts_db_path = Path(self.config.get('contracts_db_path', 'contracts/contracts_db.json'))
        
        # Ensure directories exist
        self.contracts_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize databases
        self._init_database()
        
        # Initialize blockchain if available
        if BLOCKCHAIN_AVAILABLE:
            self.blockchain = CivicBlockchain(config_path)
        else:
            self.blockchain = None
            
        # Initialize user backend if available
        if USER_BACKEND_AVAILABLE:
            self.user_backend = UserBackend(config_path)
        else:
            self.user_backend = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _init_database(self):
        """Initialize contracts database"""
        if not self.contracts_db_path.exists():
            initial_data = {
                'contracts': [],
                'contract_hierarchy': CONTRACT_HIERARCHY,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.contracts_db_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2)
    
    def _load_contracts_db(self) -> Dict[str, Any]:
        """Load contracts database"""
        try:
            with open(self.contracts_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_database()
            return self._load_contracts_db()
    
    def _save_contracts_db(self, data: Dict[str, Any]) -> bool:
        """Save contracts database"""
        try:
            data['last_updated'] = datetime.now().isoformat()
            with open(self.contracts_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving contracts database: {e}")
            return False
    
    def has_contract_creation_authority(self, user: Dict[str, Any], level: ContractLevel) -> bool:
        """Check if user has authority to create contract at specified level"""
        user_role = user.get('role', '')
        
        # Contract Founders can create any level
        if user_role == 'contract_founder':
            return True
        
        # Master and Country level require Founders or Elders
        if level in [ContractLevel.MASTER, ContractLevel.COUNTRY]:
            return user_role in ['contract_founder', 'contract_elder']
        
        # State level requires Representatives, Senators, or Elders
        if level == ContractLevel.STATE:
            return user_role in ['contract_representative', 'contract_senator', 'contract_elder']
        
        # City level requires local representatives or higher
        if level == ContractLevel.CITY:
            return user_role in ['city_representative', 'city_senator', 
                               'contract_representative', 'contract_senator', 'contract_elder']
        
        return False
    
    def get_parent_contract(self, level: ContractLevel, jurisdiction: str) -> Optional[Dict[str, Any]]:
        """Get parent contract for hierarchical validation"""
        if level == ContractLevel.MASTER:
            return None  # Master has no parent
        
        # Find hierarchy info
        hierarchy_name = self._get_hierarchy_name(level)
        parent_name = CONTRACT_HIERARCHY.get(hierarchy_name, {}).get('parent')
        
        if not parent_name:
            return None
        
        # Load contracts and find parent
        db = self._load_contracts_db()
        contracts = db.get('contracts', [])
        
        parent_level = CONTRACT_HIERARCHY[parent_name]['level']
        
        # Find active parent contract for jurisdiction
        for contract in contracts:
            if (contract.get('level') == parent_level.value and 
                contract.get('status') == ContractStatus.ACTIVE.value and
                self._is_parent_jurisdiction(contract.get('jurisdiction'), jurisdiction)):
                return contract
        
        return None
    
    def _get_hierarchy_name(self, level: ContractLevel) -> str:
        """Get hierarchy name from level"""
        for name, config in CONTRACT_HIERARCHY.items():
            if config['level'] == level:
                return name
        return ""
    
    def _is_parent_jurisdiction(self, parent_jurisdiction: str, child_jurisdiction: str) -> bool:
        """Check if parent_jurisdiction is parent of child_jurisdiction"""
        # Simple hierarchical check - can be enhanced
        if not parent_jurisdiction or not child_jurisdiction:
            return False
        
        # Parent of all
        if parent_jurisdiction == "global":
            return True
        
        # Check if child starts with parent (e.g., "USA" is parent of "USA/California")
        return child_jurisdiction.startswith(parent_jurisdiction)
    
    def validate_hierarchical_compliance(self, content: Dict[str, Any], 
                                        parent_contract: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that contract complies with parent contract"""
        if not parent_contract:
            return {'compliant': True, 'conflicts': []}
        
        conflicts = []
        
        # Check for conflicts with parent immutable sections
        parent_content = parent_contract.get('content', {})
        parent_immutable = parent_contract.get('immutable_sections', [])
        
        # Check each immutable section
        for section in parent_immutable:
            if section in content:
                if content[section] != parent_content.get(section):
                    conflicts.append(f"Cannot modify immutable section '{section}' from parent contract")
        
        # Check for authority conflicts
        if 'authority_limits' in parent_content:
            if 'authority_claims' in content:
                parent_limits = parent_content['authority_limits']
                child_claims = content['authority_claims']
                
                for claim in child_claims:
                    if claim in parent_limits:
                        conflicts.append(f"Authority claim '{claim}' conflicts with parent limits")
        
        return {
            'compliant': len(conflicts) == 0,
            'conflicts': conflicts,
            'parent_contract_id': parent_contract.get('id'),
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def request_elder_constitutional_review(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Request Elder constitutional review for high-level contracts"""
        # This creates a review request that Elders must approve
        # For now, return a pending status - actual review happens through UI
        
        review_id = str(uuid.uuid4())
        
        return {
            'review_id': review_id,
            'status': 'pending_elder_review',
            'approved': False,  # Will be updated when Elder reviews
            'reason': 'Awaiting Elder constitutional review',
            'requested_at': datetime.now().isoformat()
        }
    
    def create_contract(self, level: ContractLevel, title: str, content: Dict[str, Any],
                       jurisdiction: str, creator_email: str) -> Tuple[bool, str]:
        """Create new governance contract with hierarchical validation"""
        
        # Validate Creator Authority
        if self.user_backend:
            user = self.user_backend.get_user(creator_email)
            if not user:
                return False, "User not found"
            
            if not self.has_contract_creation_authority(user, level):
                return False, "Insufficient authority to create contract at this level"
        
        # Hierarchical Compliance Check
        parent_contract = self.get_parent_contract(level, jurisdiction)
        compliance_check = self.validate_hierarchical_compliance(content, parent_contract)
        
        if not compliance_check['compliant']:
            conflicts = ', '.join(compliance_check['conflicts'])
            return False, f"Conflicts with parent contract: {conflicts}"
        
        # Constitutional Review for Higher Levels
        elder_review = None
        if level in [ContractLevel.MASTER, ContractLevel.COUNTRY]:
            elder_review = self.request_elder_constitutional_review(content)
            # For Master/Country, require Elder approval before activation
            status = ContractStatus.PENDING_APPROVAL
        else:
            status = ContractStatus.PENDING_APPROVAL
        
        # Create Contract Record
        contract_id = str(uuid.uuid4())
        contract_data = {
            'id': contract_id,
            'level': level.value,
            'title': title,
            'content': content,
            'jurisdiction': jurisdiction,
            'creator_email': creator_email,
            'status': status.value,
            'created_at': datetime.now().isoformat(),
            'amendment_history': [],
            'hierarchical_compliance': compliance_check,
            'constitutional_review': elder_review,
            'parent_contract_id': parent_contract.get('id') if parent_contract else None
        }
        
        # Save to database
        db = self._load_contracts_db()
        db['contracts'].append(contract_data)
        self._save_contracts_db(db)
        
        # Blockchain Recording
        if self.blockchain:
            try:
                self.blockchain.add_page(
                    action_type="contract_created",
                    data=contract_data,
                    user_email=creator_email
                )
            except Exception as e:
                print(f"Warning: Failed to record contract creation on blockchain: {e}")
        
        return True, contract_id
    
    def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract by ID"""
        db = self._load_contracts_db()
        contracts = db.get('contracts', [])
        
        for contract in contracts:
            if contract.get('id') == contract_id:
                return contract
        
        return None
    
    def list_contracts(self, level: Optional[ContractLevel] = None, 
                      jurisdiction: Optional[str] = None,
                      status: Optional[ContractStatus] = None) -> List[Dict[str, Any]]:
        """List contracts with optional filters"""
        db = self._load_contracts_db()
        contracts = db.get('contracts', [])
        
        filtered = []
        for contract in contracts:
            # Apply filters
            if level is not None and contract.get('level') != level.value:
                continue
            if jurisdiction is not None and contract.get('jurisdiction') != jurisdiction:
                continue
            if status is not None and contract.get('status') != status.value:
                continue
            
            filtered.append(contract)
        
        return filtered
    
    def approve_contract(self, contract_id: str, approver_email: str) -> Tuple[bool, str]:
        """Approve pending contract (Elder or appropriate authority)"""
        contract = self.get_contract(contract_id)
        if not contract:
            return False, "Contract not found"
        
        if contract['status'] != ContractStatus.PENDING_APPROVAL.value:
            return False, f"Contract is not pending approval (current status: {contract['status']})"
        
        # Validate approver authority
        if self.user_backend:
            user = self.user_backend.get_user(approver_email)
            if not user:
                return False, "Approver not found"
            
            # Require Elder approval for Master/Country level
            if contract['level'] in [ContractLevel.MASTER.value, ContractLevel.COUNTRY.value]:
                if user.get('role') != 'contract_elder':
                    return False, "Only Contract Elders can approve Master/Country level contracts"
        
        # Update contract status
        db = self._load_contracts_db()
        contracts = db.get('contracts', [])
        
        for i, c in enumerate(contracts):
            if c.get('id') == contract_id:
                contracts[i]['status'] = ContractStatus.ACTIVE.value
                contracts[i]['approved_at'] = datetime.now().isoformat()
                contracts[i]['approved_by'] = approver_email
                
                if contracts[i].get('constitutional_review'):
                    contracts[i]['constitutional_review']['approved'] = True
                    contracts[i]['constitutional_review']['approved_at'] = datetime.now().isoformat()
                    contracts[i]['constitutional_review']['approved_by'] = approver_email
                
                self._save_contracts_db(db)
                
                # Blockchain recording
                if self.blockchain:
                    try:
                        self.blockchain.add_page(
                            action_type="contract_approved",
                            data={
                                'contract_id': contract_id,
                                'approver_email': approver_email,
                                'approved_at': datetime.now().isoformat()
                            },
                            user_email=approver_email
                        )
                    except Exception as e:
                        print(f"Warning: Failed to record contract approval on blockchain: {e}")
                
                return True, "Contract approved and activated"
        
        return False, "Contract not found in database"


# Export key classes
__all__ = ['ContractManager', 'ContractLevel', 'ContractStatus', 'CONTRACT_HIERARCHY']
