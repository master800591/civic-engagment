"""
AMENDMENT SYSTEM - Multi-stage amendment proposals with constitutional safeguards
Implements amendment proposals, voting, constitutional enforcement, and Elder review
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# Import contract types
import sys
sys.path.append(str(Path(__file__).parent.parent))

from contracts.contract_types import ContractManager, ContractLevel

try:
    from blockchain.blockchain import CivicBlockchain
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    print("Warning: Blockchain module not available for amendments")
    BLOCKCHAIN_AVAILABLE = False

try:
    from users.backend import UserBackend
    USER_BACKEND_AVAILABLE = True
except ImportError:
    print("Warning: User backend not available for amendments")
    USER_BACKEND_AVAILABLE = False


class AmendmentStatus(Enum):
    """Amendment lifecycle status"""
    PROPOSED = "proposed"
    PUBLIC_COMMENT = "public_comment"
    VOTING = "voting"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class VoteOption(Enum):
    """Vote options for amendments"""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


class AmendmentManager:
    """Manages amendment proposals, voting, and implementation"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize amendment manager"""
        self.config_path = config_path or "config/dev_config.json"
        self.config = self._load_config()
        
        # Database paths
        self.amendments_db_path = Path(self.config.get('amendments_db_path', 'contracts/amendments_db.json'))
        
        # Ensure directories exist
        self.amendments_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize databases
        self._init_database()
        
        # Initialize contract manager
        self.contract_manager = ContractManager(config_path)
        
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
        """Initialize amendments database"""
        if not self.amendments_db_path.exists():
            initial_data = {
                'amendments': [],
                'votes': [],
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.amendments_db_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2)
    
    def _load_amendments_db(self) -> Dict[str, Any]:
        """Load amendments database"""
        try:
            with open(self.amendments_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_database()
            return self._load_amendments_db()
    
    def _save_amendments_db(self, data: Dict[str, Any]) -> bool:
        """Save amendments database"""
        try:
            data['last_updated'] = datetime.now().isoformat()
            with open(self.amendments_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving amendments database: {e}")
            return False
    
    def can_propose_amendments(self, user: Dict[str, Any], contract: Dict[str, Any]) -> bool:
        """Check if user can propose amendments to contract"""
        user_role = user.get('role', '')
        contract_level = contract.get('level')
        
        # Contract Founders can propose any amendment
        if user_role == 'contract_founder':
            return True
        
        # Contract Elders can propose any amendment
        if user_role == 'contract_elder':
            return True
        
        # Representatives and Senators can propose to their level and below
        if user_role in ['contract_representative', 'contract_senator']:
            return contract_level >= ContractLevel.COUNTRY.value
        
        # Local representatives can propose local amendments
        if user_role in ['city_representative', 'city_senator']:
            return contract_level == ContractLevel.CITY.value
        
        return False
    
    def analyze_amendment_impact(self, contract: Dict[str, Any], 
                                amendment_text: str) -> Dict[str, Any]:
        """Analyze potential impact of amendment"""
        # Simple impact analysis - can be enhanced with NLP
        impact = {
            'affected_sections': [],
            'jurisdictions_affected': [contract.get('jurisdiction', 'unknown')],
            'estimated_scope': 'local',
            'requires_citizen_ratification': False,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Check if amendment affects fundamental rights or high-level contracts
        if contract.get('level') <= ContractLevel.COUNTRY.value:
            impact['estimated_scope'] = 'national'
            impact['requires_citizen_ratification'] = True
        
        # Check for keywords that indicate broad impact
        broad_keywords = ['fundamental', 'rights', 'constitution', 'authority', 'power']
        if any(keyword in amendment_text.lower() for keyword in broad_keywords):
            impact['estimated_scope'] = 'significant'
            impact['requires_citizen_ratification'] = True
        
        return impact
    
    def validate_constitutional_compliance(self, amendment_text: str, 
                                          contract: Dict[str, Any]) -> Dict[str, Any]:
        """Validate amendment for constitutional compliance"""
        violations = []
        
        # Check immutable sections
        parent_contract = self.contract_manager.get_parent_contract(
            ContractLevel(contract['level']), 
            contract['jurisdiction']
        )
        
        if parent_contract:
            immutable = parent_contract.get('content', {}).get('immutable_sections', [])
            
            # Simple check - can be enhanced
            for section in immutable:
                if section in amendment_text.lower():
                    violations.append(f"Potentially affects immutable section: {section}")
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'review_timestamp': datetime.now().isoformat()
        }
    
    def detect_contract_conflicts(self, amendment_text: str, 
                                 jurisdiction: str) -> Dict[str, Any]:
        """Detect conflicts with other contracts"""
        conflicts = []
        
        # Get all active contracts in jurisdiction hierarchy
        all_contracts = self.contract_manager.list_contracts()
        
        # Simple conflict detection - can be enhanced with NLP
        for contract in all_contracts:
            if contract.get('jurisdiction') == jurisdiction:
                # Check for keyword conflicts
                contract_keywords = str(contract.get('content', {})).lower()
                if 'override' in amendment_text.lower() and contract.get('id'):
                    conflicts.append({
                        'contract_id': contract['id'],
                        'conflict_type': 'potential_override',
                        'severity': 'medium'
                    })
        
        return {
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def calculate_amendment_voting_schedule(self, contract_level: int) -> Dict[str, Any]:
        """Calculate voting schedule based on contract level"""
        now = datetime.now()
        
        # Higher level contracts get longer voting periods
        if contract_level <= ContractLevel.COUNTRY.value:
            voting_period_days = 45
            public_comment_days = 30
        elif contract_level == ContractLevel.STATE.value:
            voting_period_days = 30
            public_comment_days = 21
        else:  # City level
            voting_period_days = 21
            public_comment_days = 14
        
        return {
            'public_comment_start': now.isoformat(),
            'public_comment_end': (now + timedelta(days=public_comment_days)).isoformat(),
            'voting_start': (now + timedelta(days=public_comment_days)).isoformat(),
            'voting_end': (now + timedelta(days=public_comment_days + voting_period_days)).isoformat()
        }
    
    def get_approval_requirements(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Get approval requirements based on contract level"""
        level = contract.get('level')
        
        if level == ContractLevel.MASTER.value:
            return {
                'founder_approval': '75%',
                'citizen_ratification': '60%',
                'elder_review': True,
                'bicameral_approval': False
            }
        elif level == ContractLevel.COUNTRY.value:
            return {
                'representative_approval': '60%',
                'senator_approval': '60%',
                'elder_approval': True,
                'citizen_ratification': '55%'
            }
        elif level == ContractLevel.STATE.value:
            return {
                'representative_approval': '60%',
                'senator_approval': '60%',
                'elder_review': True,
                'citizen_ratification': False
            }
        else:  # City level
            return {
                'representative_approval': '55%',
                'citizen_approval': '50%',
                'elder_review': False
            }
    
    def propose_amendment(self, contract_id: str, amendment_text: str, 
                         proposer_email: str, impact_analysis: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Propose amendment to existing governance contract"""
        
        # Load Target Contract
        contract = self.contract_manager.get_contract(contract_id)
        if not contract:
            return False, "Contract not found"
        
        # Validate Proposer Authority
        if self.user_backend:
            proposer = self.user_backend.get_user(proposer_email)
            if not proposer:
                return False, "Proposer not found"
            
            if not self.can_propose_amendments(proposer, contract):
                return False, "Insufficient authority to propose amendments to this contract"
        
        # Automatic Impact Analysis
        if not impact_analysis:
            impact_analysis = self.analyze_amendment_impact(contract, amendment_text)
        
        # Constitutional Compliance Pre-Check
        constitutional_check = self.validate_constitutional_compliance(amendment_text, contract)
        if not constitutional_check['compliant']:
            violations = ', '.join(constitutional_check['violations'])
            return False, f"Amendment violates constitutional principles: {violations}"
        
        # Conflict Detection with Existing Contracts
        conflict_analysis = self.detect_contract_conflicts(amendment_text, contract['jurisdiction'])
        
        # Amendment Proposal Record
        amendment_id = str(uuid.uuid4())
        amendment_data = {
            'id': amendment_id,
            'contract_id': contract_id,
            'amendment_text': amendment_text,
            'proposer_email': proposer_email,
            'impact_analysis': impact_analysis,
            'constitutional_check': constitutional_check,
            'conflict_analysis': conflict_analysis,
            'status': AmendmentStatus.PROPOSED.value,
            'public_comment_period': {
                'start_date': datetime.now().isoformat(),
                'end_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'comments': []
            },
            'voting_schedule': self.calculate_amendment_voting_schedule(contract['level']),
            'approval_requirements': self.get_approval_requirements(contract),
            'created_at': datetime.now().isoformat(),
            'voting_results': {
                'approve': 0,
                'reject': 0,
                'abstain': 0,
                'total_eligible': 0
            }
        }
        
        # Save to database
        db = self._load_amendments_db()
        db['amendments'].append(amendment_data)
        self._save_amendments_db(db)
        
        # Blockchain Recording
        if self.blockchain:
            try:
                self.blockchain.add_page(
                    action_type="amendment_proposed",
                    data=amendment_data,
                    user_email=proposer_email
                )
            except Exception as e:
                print(f"Warning: Failed to record amendment proposal on blockchain: {e}")
        
        return True, amendment_id
    
    def get_amendment(self, amendment_id: str) -> Optional[Dict[str, Any]]:
        """Get amendment by ID"""
        db = self._load_amendments_db()
        amendments = db.get('amendments', [])
        
        for amendment in amendments:
            if amendment.get('id') == amendment_id:
                return amendment
        
        return None
    
    def eligible_to_vote_on_amendment(self, voter: Dict[str, Any], 
                                     amendment: Dict[str, Any]) -> bool:
        """Check if voter is eligible to vote on amendment"""
        voter_role = voter.get('role', '')
        
        # Get contract to determine voting eligibility
        contract = self.contract_manager.get_contract(amendment['contract_id'])
        if not contract:
            return False
        
        contract_level = contract.get('level')
        
        # Contract Founders can vote on Master level
        if contract_level == ContractLevel.MASTER.value:
            return voter_role == 'contract_founder'
        
        # Representatives and Senators vote on Country/State level
        if contract_level in [ContractLevel.COUNTRY.value, ContractLevel.STATE.value]:
            return voter_role in ['contract_representative', 'contract_senator', 'contract_elder']
        
        # Local representatives vote on City level
        if contract_level == ContractLevel.CITY.value:
            return voter_role in ['city_representative', 'city_senator', 
                                 'contract_representative', 'contract_senator']
        
        return False
    
    def has_voted_on_amendment(self, amendment_id: str, voter_email: str) -> bool:
        """Check if user has already voted on amendment"""
        db = self._load_amendments_db()
        votes = db.get('votes', [])
        
        for vote in votes:
            if vote.get('amendment_id') == amendment_id and vote.get('voter_email') == voter_email:
                return True
        
        return False
    
    def calculate_voting_weight(self, voter_role: str, contract_level: int) -> float:
        """Calculate voting weight based on role and contract level"""
        # Most votes are equal weight
        # Can be enhanced for different voting systems
        return 1.0
    
    def vote_on_amendment(self, amendment_id: str, voter_email: str, 
                         vote: VoteOption, reasoning: Optional[str] = None) -> Tuple[bool, str]:
        """Multi-branch voting on contract amendments"""
        
        # Load Amendment and Validate Voter
        amendment = self.get_amendment(amendment_id)
        if not amendment:
            return False, "Amendment not found"
        
        # Prevent Double Voting (check first, before user backend)
        if self.has_voted_on_amendment(amendment_id, voter_email):
            return False, "You have already voted on this amendment"
        
        if self.user_backend:
            voter = self.user_backend.get_user(voter_email)
            if not voter:
                return False, "Voter not found"
            
            # Voting Eligibility Check
            if not self.eligible_to_vote_on_amendment(voter, amendment):
                return False, "Not eligible to vote on this amendment"
            
            voter_role = voter.get('role', '')
        else:
            voter_role = 'contract_member'
        
        # Role-Based Voting Weight
        contract = self.contract_manager.get_contract(amendment['contract_id'])
        voting_weight = self.calculate_voting_weight(voter_role, contract.get('level', 0))
        
        # Record Vote
        vote_data = {
            'id': str(uuid.uuid4()),
            'amendment_id': amendment_id,
            'voter_email': voter_email,
            'voter_role': voter_role,
            'vote': vote.value if isinstance(vote, VoteOption) else vote,
            'reasoning': reasoning,
            'voting_weight': voting_weight,
            'jurisdiction': voter.get('jurisdiction') if self.user_backend else 'unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        # Save vote
        db = self._load_amendments_db()
        db['votes'].append(vote_data)
        
        # Update Amendment Vote Tally
        amendments = db.get('amendments', [])
        for i, a in enumerate(amendments):
            if a.get('id') == amendment_id:
                vote_type = vote.value if isinstance(vote, VoteOption) else vote
                amendments[i]['voting_results'][vote_type] += voting_weight
                break
        
        self._save_amendments_db(db)
        
        # Blockchain Recording
        if self.blockchain:
            try:
                self.blockchain.add_page(
                    action_type="amendment_voted",
                    data=vote_data,
                    user_email=voter_email
                )
            except Exception as e:
                print(f"Warning: Failed to record vote on blockchain: {e}")
        
        return True, "Vote recorded successfully"
    
    def list_amendments(self, contract_id: Optional[str] = None,
                       status: Optional[AmendmentStatus] = None) -> List[Dict[str, Any]]:
        """List amendments with optional filters"""
        db = self._load_amendments_db()
        amendments = db.get('amendments', [])
        
        filtered = []
        for amendment in amendments:
            if contract_id is not None and amendment.get('contract_id') != contract_id:
                continue
            if status is not None and amendment.get('status') != status.value:
                continue
            
            filtered.append(amendment)
        
        return filtered


class ConstitutionalEnforcement:
    """Elder constitutional review and enforcement"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize constitutional enforcement"""
        self.config_path = config_path or "config/dev_config.json"
        
        self.contract_manager = ContractManager(config_path)
        
        if BLOCKCHAIN_AVAILABLE:
            self.blockchain = CivicBlockchain(config_path)
        else:
            self.blockchain = None
        
        if USER_BACKEND_AVAILABLE:
            self.user_backend = UserBackend(config_path)
        else:
            self.user_backend = None
    
    def check_fundamental_rights_compliance(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Check contract compliance with fundamental rights"""
        issues = []
        
        # Check for fundamental rights keywords
        content_str = str(contract.get('content', {})).lower()
        
        required_protections = ['due process', 'equal treatment', 'participation']
        for protection in required_protections:
            if protection not in content_str:
                issues.append(f"Missing fundamental protection: {protection}")
        
        return {
            'passes': len(issues) == 0,
            'issues': issues
        }
    
    def validate_power_separation(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Validate separation of powers"""
        issues = []
        
        content = contract.get('content', {})
        
        # Check for proper power separation
        if 'authority' in content:
            # Simple check - should not consolidate all powers
            if 'all powers' in str(content['authority']).lower():
                issues.append("Potential power consolidation detected")
        
        return {
            'passes': len(issues) == 0,
            'issues': issues
        }
    
    def verify_checks_and_balances(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Verify checks and balances"""
        issues = []
        
        content = contract.get('content', {})
        
        # Check for oversight mechanisms
        if 'oversight' not in str(content).lower():
            issues.append("No oversight mechanism specified")
        
        return {
            'passes': len(issues) == 0,
            'issues': issues
        }
    
    def assess_minority_protections(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Assess minority protection provisions"""
        issues = []
        
        # Check for minority protection clauses
        content_str = str(contract.get('content', {})).lower()
        
        if 'minority' not in content_str and 'protection' not in content_str:
            issues.append("No explicit minority protection provisions")
        
        return {
            'passes': len(issues) == 0,
            'issues': issues
        }
    
    def validate_due_process_provisions(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Validate due process provisions"""
        issues = []
        
        content_str = str(contract.get('content', {})).lower()
        
        if 'due process' not in content_str:
            issues.append("No due process provisions specified")
        
        return {
            'passes': len(issues) == 0,
            'issues': issues
        }
    
    def analyze_precedent_consistency(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consistency with constitutional precedent"""
        issues = []
        
        # Simple precedent check - can be enhanced with precedent database
        # For now, just flag high-level contracts for manual review
        if contract.get('level') <= ContractLevel.COUNTRY.value:
            issues.append("High-level contract requires detailed precedent review")
        
        return {
            'passes': len(issues) == 0,
            'issues': issues
        }
    
    def review_constitutional_compliance(self, contract_id: str, 
                                        elder_email: str) -> Tuple[bool, Dict[str, Any]]:
        """Elder review for constitutional compliance"""
        
        # Validate Elder Authority
        if self.user_backend:
            elder = self.user_backend.get_user(elder_email)
            if not elder:
                return False, {'error': 'Elder not found'}
            if elder.get('role') != 'contract_elder':
                return False, {'error': 'Only Contract Elders can perform constitutional review'}
        
        # Load Contract/Amendment for Review
        contract = self.contract_manager.get_contract(contract_id)
        if not contract:
            return False, {'error': 'Contract not found'}
        
        # Comprehensive Constitutional Analysis
        analysis = {
            'fundamental_rights_check': self.check_fundamental_rights_compliance(contract),
            'separation_of_powers': self.validate_power_separation(contract),
            'checks_and_balances': self.verify_checks_and_balances(contract),
            'minority_protection': self.assess_minority_protections(contract),
            'due_process': self.validate_due_process_provisions(contract),
            'constitutional_precedent': self.analyze_precedent_consistency(contract)
        }
        
        # Overall Compliance Decision
        compliance_decision = {
            'compliant': all(analysis[key]['passes'] for key in analysis),
            'issues': [issue for key in analysis for issue in analysis[key]['issues']],
            'recommendations': [],
            'constitutional_interpretation': '',
            'precedent_impact': 'To be determined by Elder'
        }
        
        # Elder Review Record
        review_data = {
            'contract_id': contract_id,
            'elder_email': elder_email,
            'analysis': analysis,
            'decision': compliance_decision,
            'elder_reasoning': '',  # To be filled by UI
            'precedent_value': 'high' if contract.get('level', 99) <= ContractLevel.COUNTRY.value else 'medium',
            'timestamp': datetime.now().isoformat()
        }
        
        # Blockchain Recording
        if self.blockchain:
            try:
                self.blockchain.add_page(
                    action_type="constitutional_review",
                    data=review_data,
                    user_email=elder_email
                )
            except Exception as e:
                print(f"Warning: Failed to record constitutional review on blockchain: {e}")
        
        return True, review_data


# Export key classes
__all__ = ['AmendmentManager', 'ConstitutionalEnforcement', 'AmendmentStatus', 'VoteOption']
