# contracts/contract_terms.py
# Hierarchical Contract Framework for Civic Engagement Platform
"""
Constitutional contract framework implementing Master→Country→State→City hierarchy
where Master contract overrules all others with democratic governance principles.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, asdict


class ContractType(Enum):
    """Hierarchical contract types with precedence order"""
    MASTER = "master"           # Constitutional - overrules all
    COUNTRY = "country"         # National governance
    STATE = "state"             # Regional governance  
    CITY = "city"               # Local governance


class ContractStatus(Enum):
    """Contract lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    REVOKED = "revoked"


@dataclass
class ContractSection:
    """Individual contract section with clear intent and enforceability"""
    
    section_id: str
    title: str
    intent: str              # What this section aims to achieve
    reason: str              # Why this section is necessary
    objective: str           # Specific goal or outcome
    content: str             # Legal text of the section
    effective_date: str      # When this section takes effect
    expiration_date: Optional[str] = None  # When this expires (if applicable)
    precedence: int = 0      # Override priority within contract
    requires_agreement: bool = True  # Must user explicitly agree
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContractSection':
        """Create from dictionary"""
        return cls(**data)


class PlatformContract:
    acceptance_deadline: Optional[str] = None  # ISO date string
    adjudication_triggered: bool = False

    def set_acceptance_deadline(self, deadline_iso: str) -> None:
        self.acceptance_deadline = deadline_iso
        self.adjudication_triggered = False

    def check_acceptance_and_trigger(self, user_emails: List[str]) -> None:
        """
        Checks if all required sections are accepted by all users. If so, triggers payment.
        If deadline has passed and not all accepted, triggers adjudication.
        """
        from datetime import datetime
        now = datetime.now().isoformat()
        all_accepted = True
        for email in user_emails:
            for section in self.sections:
                if section.requires_agreement:
                    # Assume contract_manager.has_accepted_contract checks section acceptance
                    from contracts.contract_terms import contract_manager
                    if not contract_manager.has_accepted_contract(email, self.contract_id):
                        all_accepted = False
                        break
        if all_accepted and not self.payment_completed:
            self.complete_contract_and_pay()
        elif self.acceptance_deadline and now > self.acceptance_deadline and not all_accepted and not self.adjudication_triggered:
            self.trigger_adjudication()

    def trigger_adjudication(self) -> None:
        self.adjudication_triggered = True
        # Record adjudication event in blockchain
        try:
            from civic_desktop.blockchain.blockchain import Blockchain
            Blockchain.add_page({
                'action': 'contract_adjudication',
                'contract_id': self.contract_id,
                'timestamp': datetime.now().isoformat(),
                'reason': 'Acceptance deadline missed'
            }, validator='SYSTEM')
        except Exception as e:
            print(f"Adjudication blockchain record failed: {e}")
    # Payment terms for contract
    payment_amount: float = 0.0
    payment_currency: str = "CIVIC"
    payer_email: Optional[str] = None
    payee_email: Optional[str] = None
    payment_completed: bool = False

    def set_payment_terms(self, amount: float, payer_email: str, payee_email: str, currency: str = "CIVIC") -> None:
        self.payment_amount = amount
        self.payer_email = payer_email
        self.payee_email = payee_email
        self.payment_currency = currency
        self.payment_completed = False

    def complete_contract_and_pay(self) -> bool:
        """Mark contract as completed and trigger payment via TokenLedger"""
        if self.payment_completed or not self.payment_amount or not self.payer_email or not self.payee_email:
            return False
        try:
            from civic_desktop.crypto.ledger import TokenLedger
            ledger = TokenLedger()  # In real app, use shared instance
            success = ledger.send_tokens(self.payer_email, self.payee_email, self.payment_amount, f"Contract {self.contract_id} completion payment")
            if success:
                self.payment_completed = True
            return success
        except Exception as e:
            print(f"Contract payment failed: {e}")
            return False
    """
    Complete contract with hierarchical enforcement
    Master contracts override all others, Country overrides State/City, etc.
    """
    
    def __init__(self, contract_type: ContractType, jurisdiction: str = "") -> None:
        self.contract_type = contract_type
        self.jurisdiction = jurisdiction  # e.g., "USA", "California", "San Francisco"
        self.contract_id = f"{contract_type.value}_{jurisdiction}_{datetime.now().strftime('%Y%m%d')}"
        self.version = "1.0"
        self.status = ContractStatus.DRAFT
        self.sections: List[ContractSection] = []
        self.created_date = datetime.now().isoformat()
        self.effective_date = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
        self.acceptance_required = True
        
        # Hierarchical precedence (lower number = higher precedence)
        self.precedence_level = {
            ContractType.MASTER: 1,
            ContractType.COUNTRY: 2, 
            ContractType.STATE: 3,
            ContractType.CITY: 4
        }[contract_type]
    
    def add_section(self, section: ContractSection) -> None:
        """Add a section to this contract"""
        self.sections.append(section)
        self.last_modified = datetime.now().isoformat()
    
    def get_section(self, section_id: str) -> Optional[ContractSection]:
        """Get specific section by ID"""
        for section in self.sections:
            if section.section_id == section_id:
                return section
        return None
    
    def remove_section(self, section_id: str) -> bool:
        """Remove section by ID"""
        for i, section in enumerate(self.sections):
            if section.section_id == section_id:
                del self.sections[i]
                self.last_modified = datetime.now().isoformat()
                return True
        return False
    
    def update_section(self, section_id: str, updated_section: ContractSection) -> bool:
        """Update existing section"""
        for i, section in enumerate(self.sections):
            if section.section_id == section_id:
                self.sections[i] = updated_section
                self.last_modified = datetime.now().isoformat()
                return True
        return False
    
    def get_all_sections(self) -> List[ContractSection]:
        """Get all sections sorted by precedence"""
        return sorted(self.sections, key=lambda x: x.precedence)
    
    def activate(self) -> None:
        """Activate this contract"""
        self.status = ContractStatus.ACTIVE
        self.effective_date = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
    
    def supersede(self) -> None:
        """Mark contract as superseded by newer version"""
        self.status = ContractStatus.SUPERSEDED
        self.last_modified = datetime.now().isoformat()
    
    def revoke(self) -> None:
        """Revoke this contract"""
        self.status = ContractStatus.REVOKED
        self.last_modified = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary for storage"""
        return {
            'contract_id': self.contract_id,
            'contract_type': self.contract_type.value,
            'jurisdiction': self.jurisdiction,
            'version': self.version,
            'status': self.status.value,
            'created_date': self.created_date,
            'effective_date': self.effective_date,
            'last_modified': self.last_modified,
            'acceptance_required': self.acceptance_required,
            'sections': [section.to_dict() for section in self.sections]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlatformContract':
        """Create contract from dictionary"""
        contract_type = ContractType(data.get('contract_type', ContractType.MASTER.value))
        contract = cls(contract_type, data.get('jurisdiction', ""))
        
        contract.contract_id = data.get('contract_id', f"{contract_type.value}_{datetime.now().strftime('%Y%m%d')}")
        contract.version = data.get('version', "1.0")
        status_str = data.get('status', ContractStatus.ACTIVE.value if data else ContractStatus.ACTIVE.value)
        try:
            contract.status = ContractStatus(status_str)
        except Exception:
            contract.status = ContractStatus.ACTIVE
        contract.created_date = data.get('created_date', datetime.now().isoformat())
        contract.effective_date = data.get('effective_date', datetime.now().isoformat())
        contract.last_modified = data.get('last_modified', datetime.now().isoformat())
        contract.acceptance_required = data.get('acceptance_required', True)
        
        # Load sections
        for section_data in data.get('sections', []):
            try:
                section = ContractSection.from_dict(section_data)
                contract.sections.append(section)
            except Exception:
                continue
        
        return contract


class ContractManager:
    """
    Manages hierarchical contract system with proper precedence enforcement
    Master contracts override all others
    """
    
    def __init__(self, data_dir: str = "contracts_db"):
        # Allow in-memory mode for tests by mapping ':memory:' to a temp dir
        if data_dir == ':memory:':
            import tempfile
            tmp = tempfile.mkdtemp(prefix='contracts_db_')
            self.data_dir = tmp
        else:
            self.data_dir = data_dir
        self.contracts_file = os.path.join(data_dir, "contracts.json")
        self.acceptances_file = os.path.join(data_dir, "acceptances.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.contracts: Dict[str, PlatformContract] = {}
        self.user_acceptances: Dict[str, Dict[str, Any]] = {}
        
        self.load_contracts()
        self.load_acceptances()
    
    def load_contracts(self) -> None:
        """Load all contracts from storage"""
        if os.path.exists(self.contracts_file):
            try:
                with open(self.contracts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for contract_data in data.get('contracts', []):
                    contract = PlatformContract.from_dict(contract_data)
                    self.contracts[contract.contract_id] = contract
                    
            except Exception as e:
                print(f"Error loading contracts: {e}")
    
    def save_contracts(self) -> None:
        """Save all contracts to storage"""
        try:
            data: Dict[str, Any] = {
                'contracts': [contract.to_dict() for contract in self.contracts.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.contracts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving contracts: {e}")
    
    def load_acceptances(self) -> None:
        """Load user contract acceptances"""
        if os.path.exists(self.acceptances_file):
            try:
                with open(self.acceptances_file, 'r', encoding='utf-8') as f:
                    self.user_acceptances = json.load(f)
            except Exception as e:
                print(f"Error loading acceptances: {e}")
    
    def save_acceptances(self) -> None:
        """Save user contract acceptances"""
        try:
            with open(self.acceptances_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_acceptances, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving acceptances: {e}")
    
    def add_contract(self, contract: PlatformContract) -> bool:
        """Add new contract to system"""
        try:
            self.contracts[contract.contract_id] = contract
            self.save_contracts()
            return True
        except Exception as e:
            print(f"Error adding contract: {e}")
            return False
    
    def get_contract(self, contract_id: str) -> Optional[PlatformContract]:
        """Get contract by ID"""
        return self.contracts.get(contract_id)
    
    def get_active_contracts(self) -> List[PlatformContract]:
        """Get all active contracts sorted by precedence"""
        active = [c for c in self.contracts.values() if c.status == ContractStatus.ACTIVE]
        return sorted(active, key=lambda x: x.precedence_level)
    
    def get_contracts_by_type(self, contract_type: ContractType) -> List[PlatformContract]:
        """Get contracts by type"""
        return [c for c in self.contracts.values() if c.contract_type == contract_type]
    
    def get_applicable_contracts(self, user_location: Dict[str, str]) -> List[PlatformContract]:
        """
        Get contracts that apply to user based on their location
        Returns contracts in precedence order (Master first)
        """
        applicable: List[PlatformContract] = []
        
        # Always include master contracts
        master_contracts = self.get_contracts_by_type(ContractType.MASTER)
        applicable.extend([c for c in master_contracts if c.status == ContractStatus.ACTIVE])
        
        # Add country contracts
        if 'country' in user_location:
            country_contracts = [c for c in self.get_contracts_by_type(ContractType.COUNTRY) 
                               if c.jurisdiction == user_location['country'] and c.status == ContractStatus.ACTIVE]
            applicable.extend(country_contracts)
        
        # Add state contracts
        if 'state' in user_location:
            state_contracts = [c for c in self.get_contracts_by_type(ContractType.STATE) 
                             if c.jurisdiction == user_location['state'] and c.status == ContractStatus.ACTIVE]
            applicable.extend(state_contracts)
        
        # Add city contracts
        if 'city' in user_location:
            city_contracts = [c for c in self.get_contracts_by_type(ContractType.CITY) 
                            if c.jurisdiction == user_location['city'] and c.status == ContractStatus.ACTIVE]
            applicable.extend(city_contracts)
        
        return sorted(applicable, key=lambda x: x.precedence_level)
    
    def record_acceptance(self, user_email: str, contract_id: str, ip_address: str = "", user_agent: str = "") -> bool:
        """Record user acceptance of contract with blockchain logging"""
        try:
            if user_email not in self.user_acceptances:
                self.user_acceptances[user_email] = {}
            
            acceptance_data = {
                'contract_id': contract_id,
                'accepted_at': datetime.now().isoformat(),
                'ip_address': ip_address,
                'user_agent': user_agent,
                'contract_version': self.contracts[contract_id].version if contract_id in self.contracts else "unknown"
            }
            
            self.user_acceptances[user_email][contract_id] = acceptance_data
            self.save_acceptances()
            
            # Record in blockchain for immutable audit trail
            try:
                # Import here to avoid circular imports
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                from blockchain.blockchain import Blockchain
                
                blockchain_data = {
                    'action': 'contract_acceptance',
                    'user_email': user_email,
                    'contract_id': contract_id,
                    'contract_type': self.contracts[contract_id].contract_type.value if contract_id in self.contracts else "unknown",
                    'jurisdiction': self.contracts[contract_id].jurisdiction if contract_id in self.contracts else "unknown",
                    'acceptance_timestamp': acceptance_data['accepted_at'],
                    'ip_address': ip_address
                }
                
                Blockchain.add_page(
                    blockchain_data,
                    validator="SYSTEM"
                )
                
            except Exception as e:
                print(f"Warning: Could not record contract acceptance in blockchain: {e}")
            
            return True
            
        except Exception as e:
            print(f"Error recording contract acceptance: {e}")
            return False
    
    def has_accepted_contract(self, user_email: str, contract_id: str) -> bool:
        """Check if user has accepted specific contract"""
        return (user_email in self.user_acceptances and 
                contract_id in self.user_acceptances[user_email])
    
    def get_user_acceptances(self, user_email: str) -> Dict[str, Any]:
        """Get all contract acceptances for user"""
        return self.user_acceptances.get(user_email, {})
    
    def check_all_required_accepted(self, user_email: str, user_location: Dict[str, str]) -> Tuple[bool, List[PlatformContract]]:
        """
        Check if user has accepted all required contracts for their location
        Returns (all_accepted, missing_contracts)
        """
        applicable_contracts = self.get_applicable_contracts(user_location)
        required_contracts = [c for c in applicable_contracts if c.acceptance_required]
        missing_contracts: List[PlatformContract] = []
        for contract in required_contracts:
            if not self.has_accepted_contract(user_email, contract.contract_id):
                missing_contracts.append(contract)
        return len(missing_contracts) == 0, missing_contracts
    
    def resolve_conflicting_sections(self, user_location: Dict[str, str], section_type: str) -> Optional[ContractSection]:
        """
        return len(missing_contracts) == 0, missing_contracts
        Master contracts always override others
        """
        applicable_contracts = self.get_applicable_contracts(user_location)
        
        # Find all sections of the specified type
        matching_sections: List[Tuple[Any, int]] = []
        for contract in applicable_contracts:
            for section in contract.sections:
                if section_type.lower() in section.title.lower() or section_type.lower() in section.section_id.lower():
                    matching_sections.append((section, contract.precedence_level))
        
        if not matching_sections:
            return None
        
        # Return section from highest precedence contract (lowest precedence_level number)
        matching_sections.sort(key=lambda x: x[1])
        return matching_sections[0][0]
    
    def get_effective_rules(self, user_location: Dict[str, str]) -> Dict[str, ContractSection]:
        """
        Get effective rules for user location, resolving conflicts by hierarchy
        Master contract rules always take precedence
        """
        applicable_contracts = self.get_applicable_contracts(user_location)
        effective_rules: Dict[str, ContractSection] = {}
        if not applicable_contracts:
            return effective_rules
        # Process contracts in reverse precedence order (lowest precedence first)
        # This way higher precedence contracts will override lower ones
        for contract in reversed(applicable_contracts):
            if hasattr(contract, 'sections'):
                for section in contract.sections:
                    if hasattr(section, 'title'):
                        effective_rules[section.title] = section
        return effective_rules


# Initialize global contract manager
contract_manager = ContractManager()