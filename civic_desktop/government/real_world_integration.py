"""
REAL-WORLD GOVERNMENT INTEGRATION SYSTEM
Allows real government officials to register and manage their jurisdictions
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Import existing systems
try:
    from civic_desktop.users.backend import UserBackend
    from civic_desktop.blockchain.blockchain import CivicBlockchain
    from civic_desktop.blockchain.term_limit_verification import BlockchainTermLimitManager
    USER_BACKEND_AVAILABLE = True
except ImportError:
    print("Warning: Backend systems not available for government integration")
    USER_BACKEND_AVAILABLE = False


class RealWorldGovLevel(Enum):
    """Real-world government levels"""
    MUNICIPAL = "municipal"          # Mayor, City Council, etc.
    COUNTY = "county"               # County Commissioner, Sheriff, etc.
    STATE = "state"                 # Governor, State Legislature, etc.
    FEDERAL = "federal"             # Congress, Senate, President, etc.
    INTERNATIONAL = "international"  # UN, EU, etc.


class RealWorldPosition(Enum):
    """Real-world government positions"""
    # Municipal
    MAYOR = "mayor"
    CITY_COUNCIL_MEMBER = "city_council_member"
    CITY_MANAGER = "city_manager"
    
    # County
    COUNTY_COMMISSIONER = "county_commissioner"
    SHERIFF = "sheriff"
    COUNTY_CLERK = "county_clerk"
    
    # State
    GOVERNOR = "governor"
    LT_GOVERNOR = "lt_governor"
    STATE_REPRESENTATIVE = "state_representative"
    STATE_SENATOR = "state_senator"
    ATTORNEY_GENERAL = "attorney_general"
    SECRETARY_OF_STATE = "secretary_of_state"
    
    # Federal
    US_REPRESENTATIVE = "us_representative"
    US_SENATOR = "us_senator"
    PRESIDENT = "president"
    VICE_PRESIDENT = "vice_president"
    CABINET_MEMBER = "cabinet_member"
    FEDERAL_JUDGE = "federal_judge"
    
    # Administrative
    DEPARTMENT_HEAD = "department_head"
    AGENCY_DIRECTOR = "agency_director"
    CIVIL_SERVANT = "civil_servant"


class VerificationStatus(Enum):
    """Government official verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class GovernmentJurisdiction:
    """Real-world government jurisdiction"""
    jurisdiction_id: str
    name: str
    level: RealWorldGovLevel
    parent_jurisdiction: Optional[str]  # State for city, country for state, etc.
    country: str
    state: Optional[str] = None
    county: Optional[str] = None
    population: Optional[int] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    verified: bool = False
    created_date: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'jurisdiction_id': self.jurisdiction_id,
            'name': self.name,
            'level': self.level.value,
            'parent_jurisdiction': self.parent_jurisdiction,
            'country': self.country,
            'state': self.state,
            'county': self.county,
            'population': self.population,
            'website': self.website,
            'contact_email': self.contact_email,
            'verified': self.verified,
            'created_date': self.created_date
        }


@dataclass
class GovernmentOfficial:
    """Real-world government official registration"""
    official_id: str
    user_email: str
    jurisdiction_id: str
    position: RealWorldPosition
    position_title: str  # Official title as it appears
    term_start: str
    term_end: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_documents: List[str] = None
    verification_date: Optional[str] = None
    verified_by: Optional[str] = None
    contract_role_assigned: Optional[str] = None  # Corresponding contract role
    notes: str = ""
    
    def __post_init__(self):
        if self.verification_documents is None:
            self.verification_documents = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'official_id': self.official_id,
            'user_email': self.user_email,
            'jurisdiction_id': self.jurisdiction_id,
            'position': self.position.value,
            'position_title': self.position_title,
            'term_start': self.term_start,
            'term_end': self.term_end,
            'verification_status': self.verification_status.value,
            'verification_documents': self.verification_documents,
            'verification_date': self.verification_date,
            'verified_by': self.verified_by,
            'contract_role_assigned': self.contract_role_assigned,
            'notes': self.notes
        }


class RealWorldGovernmentManager:
    """Manages real-world government officials and jurisdictions"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the government integration manager"""
        
        self.config_path = config_path
        self.base_path = Path(config_path) if config_path else Path(__file__).parent
        self.data_path = self.base_path / 'government_data'
        self.data_path.mkdir(exist_ok=True)
        
        # Database files
        self.jurisdictions_db = self.data_path / 'jurisdictions.json'
        self.officials_db = self.data_path / 'government_officials.json'
        self.verifications_db = self.data_path / 'verifications.json'
        self.mappings_db = self.data_path / 'contract_mappings.json'
        
        # Initialize backend systems
        self.blockchain = CivicBlockchain() if USER_BACKEND_AVAILABLE else None
        self.user_backend = UserBackend() if USER_BACKEND_AVAILABLE else None
        self.term_limit_manager = BlockchainTermLimitManager() if USER_BACKEND_AVAILABLE else None
        
        # Initialize databases
        self._initialize_databases()
        
        print("🏛️ Real-World Government Integration Manager initialized")
    
    def _initialize_databases(self):
        """Initialize government databases"""
        
        if not self.jurisdictions_db.exists():
            initial_jurisdictions = {
                'jurisdictions': {},
                'last_updated': datetime.now().isoformat(),
                'total_jurisdictions': 0
            }
            self._save_json(self.jurisdictions_db, initial_jurisdictions)
        
        if not self.officials_db.exists():
            initial_officials = {
                'officials': {},
                'pending_verifications': {},
                'verification_queue': [],
                'last_updated': datetime.now().isoformat()
            }
            self._save_json(self.officials_db, initial_officials)
        
        if not self.verifications_db.exists():
            initial_verifications = {
                'verification_logs': [],
                'verification_criteria': {
                    'required_documents': {
                        'mayor': ['oath_of_office', 'election_certificate'],
                        'state_representative': ['oath_of_office', 'election_certificate', 'state_id'],
                        'us_senator': ['oath_of_office', 'senate_credentials', 'federal_id'],
                        'governor': ['oath_of_office', 'election_certificate', 'state_seal']
                    },
                    'verification_authorities': [
                        'contract_founder',
                        'contract_elder',
                        'verified_government_liaison'
                    ]
                },
                'last_updated': datetime.now().isoformat()
            }
            self._save_json(self.verifications_db, initial_verifications)
        
        if not self.mappings_db.exists():
            initial_mappings = {
                'position_to_contract_role': {
                    # Municipal mappings
                    'mayor': 'contract_representative',
                    'city_council_member': 'contract_representative',
                    'city_manager': 'contract_representative',
                    
                    # County mappings
                    'county_commissioner': 'contract_representative',
                    'sheriff': 'contract_representative',
                    
                    # State mappings
                    'governor': 'contract_senator',
                    'lt_governor': 'contract_senator',
                    'state_representative': 'contract_representative',
                    'state_senator': 'contract_senator',
                    'attorney_general': 'contract_senator',
                    
                    # Federal mappings
                    'us_representative': 'contract_representative',
                    'us_senator': 'contract_senator',
                    'president': 'contract_elder',
                    'vice_president': 'contract_elder',
                    'cabinet_member': 'contract_senator',
                    'federal_judge': 'contract_elder'
                },
                'special_permissions': {
                    'mayor': ['municipal_authority', 'local_emergency_powers'],
                    'governor': ['state_authority', 'state_emergency_powers'],
                    'president': ['federal_authority', 'national_emergency_powers'],
                    'federal_judge': ['judicial_authority', 'constitutional_interpretation']
                },
                'last_updated': datetime.now().isoformat()
            }
            self._save_json(self.mappings_db, initial_mappings)
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Save JSON data to file"""
        data['last_updated'] = datetime.now().isoformat()
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_jurisdiction(self, name: str, level: RealWorldGovLevel, country: str,
                            state: Optional[str] = None, county: Optional[str] = None,
                            population: Optional[int] = None, parent_jurisdiction: Optional[str] = None,
                            website: Optional[str] = None, contact_email: Optional[str] = None) -> Tuple[bool, str, str]:
        """Register a real-world government jurisdiction"""
        
        try:
            # Generate jurisdiction ID
            jurisdiction_id = f"{level.value}_{country.lower().replace(' ', '_')}"
            if state:
                jurisdiction_id += f"_{state.lower().replace(' ', '_')}"
            if county:
                jurisdiction_id += f"_{county.lower().replace(' ', '_')}"
            jurisdiction_id += f"_{name.lower().replace(' ', '_')}"
            
            # Create jurisdiction object
            jurisdiction = GovernmentJurisdiction(
                jurisdiction_id=jurisdiction_id,
                name=name,
                level=level,
                parent_jurisdiction=parent_jurisdiction,
                country=country,
                state=state,
                county=county,
                population=population,
                website=website,
                contact_email=contact_email,
                created_date=datetime.now().isoformat()
            )
            
            # Save to database
            jurisdictions_data = self._load_json(self.jurisdictions_db)
            jurisdictions_data['jurisdictions'][jurisdiction_id] = jurisdiction.to_dict()
            jurisdictions_data['total_jurisdictions'] = len(jurisdictions_data['jurisdictions'])
            self._save_json(self.jurisdictions_db, jurisdictions_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="government_jurisdiction_registered",
                    user_email="system@government_integration",
                    data={
                        'jurisdiction': jurisdiction.to_dict(),
                        'integration_type': 'real_world_government',
                        'registration_timestamp': datetime.now().isoformat()
                    }
                )
            
            return True, f"Jurisdiction '{name}' registered successfully", jurisdiction_id
            
        except Exception as e:
            return False, f"Failed to register jurisdiction: {str(e)}", ""
    
    def register_government_official(self, user_email: str, jurisdiction_id: str, 
                                   position: RealWorldPosition, position_title: str,
                                   term_start: str, term_end: Optional[str] = None,
                                   verification_documents: List[str] = None) -> Tuple[bool, str, str]:
        """Register a real-world government official"""
        
        try:
            # Validate jurisdiction exists
            jurisdictions_data = self._load_json(self.jurisdictions_db)
            if jurisdiction_id not in jurisdictions_data.get('jurisdictions', {}):
                return False, f"Jurisdiction '{jurisdiction_id}' not found", ""
            
            # Generate official ID
            official_id = f"{jurisdiction_id}_{position.value}_{user_email.replace('@', '_').replace('.', '_')}"
            
            # Create official object
            official = GovernmentOfficial(
                official_id=official_id,
                user_email=user_email,
                jurisdiction_id=jurisdiction_id,
                position=position,
                position_title=position_title,
                term_start=term_start,
                term_end=term_end,
                verification_documents=verification_documents or [],
                verification_status=VerificationStatus.PENDING
            )
            
            # Save to database
            officials_data = self._load_json(self.officials_db)
            officials_data['officials'][official_id] = official.to_dict()
            officials_data['pending_verifications'][official_id] = official.to_dict()
            if official_id not in officials_data.get('verification_queue', []):
                officials_data.setdefault('verification_queue', []).append(official_id)
            
            self._save_json(self.officials_db, officials_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="government_official_registered",
                    user_email=user_email,
                    data={
                        'official': official.to_dict(),
                        'jurisdiction': jurisdiction_id,
                        'integration_type': 'real_world_government_official',
                        'registration_timestamp': datetime.now().isoformat(),
                        'awaiting_verification': True
                    }
                )
            
            return True, f"Government official registration submitted for verification", official_id
            
        except Exception as e:
            return False, f"Failed to register official: {str(e)}", ""
    
    def verify_government_official(self, official_id: str, verified_by: str,
                                 verification_notes: str = "") -> Tuple[bool, str]:
        """Verify a government official and assign contract role"""
        
        try:
            # Load official data
            officials_data = self._load_json(self.officials_db)
            
            if official_id not in officials_data.get('officials', {}):
                return False, f"Official '{official_id}' not found"
            
            official_data = officials_data['officials'][official_id]
            
            # Update verification status
            officials_data['officials'][official_id].update({
                'verification_status': VerificationStatus.VERIFIED.value,
                'verification_date': datetime.now().isoformat(),
                'verified_by': verified_by,
                'notes': verification_notes
            })
            
            # Remove from pending queue
            if official_id in officials_data.get('pending_verifications', {}):
                del officials_data['pending_verifications'][official_id]
            
            if official_id in officials_data.get('verification_queue', []):
                officials_data['verification_queue'].remove(official_id)
            
            # Determine contract role mapping
            mappings_data = self._load_json(self.mappings_db)
            position = official_data['position']
            contract_role = mappings_data.get('position_to_contract_role', {}).get(position, 'contract_member')
            
            # Assign contract role to user
            if self.user_backend:
                role_success, role_message = self._assign_contract_role(
                    official_data['user_email'], 
                    contract_role,
                    f"Real-world {position} in {official_data['jurisdiction_id']}"
                )
                
                if role_success:
                    officials_data['officials'][official_id]['contract_role_assigned'] = contract_role
            
            self._save_json(self.officials_db, officials_data)
            
            # Log verification
            verification_log = {
                'official_id': official_id,
                'user_email': official_data['user_email'],
                'position': position,
                'jurisdiction_id': official_data['jurisdiction_id'],
                'verified_by': verified_by,
                'verification_date': datetime.now().isoformat(),
                'contract_role_assigned': contract_role,
                'notes': verification_notes
            }
            
            verifications_data = self._load_json(self.verifications_db)
            verifications_data.setdefault('verification_logs', []).append(verification_log)
            self._save_json(self.verifications_db, verifications_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="government_official_verified",
                    user_email=official_data['user_email'],
                    data={
                        'official_id': official_id,
                        'verification': verification_log,
                        'contract_role_granted': contract_role,
                        'government_integration_complete': True,
                        'verification_timestamp': datetime.now().isoformat()
                    }
                )
            
            return True, f"Official verified and assigned contract role: {contract_role}"
            
        except Exception as e:
            return False, f"Failed to verify official: {str(e)}"
    
    def _assign_contract_role(self, user_email: str, contract_role: str, reason: str) -> Tuple[bool, str]:
        """Assign contract role to verified government official"""
        
        try:
            if not self.user_backend:
                return False, "User backend not available"
            
            # Get user data
            user_data = self.user_backend.get_user(user_email)
            if not user_data:
                return False, f"User {user_email} not found"
            
            # Update user role
            success, message = self.user_backend.update_user_role(user_email, contract_role)
            
            if success:
                # Record role assignment
                if self.blockchain:
                    self.blockchain.add_page(
                        action_type="government_official_role_assigned",
                        user_email=user_email,
                        data={
                            'new_role': contract_role,
                            'assignment_reason': reason,
                            'assignment_type': 'real_world_government_verification',
                            'assignment_timestamp': datetime.now().isoformat(),
                            'authority': 'government_integration_system'
                        }
                    )
                
                return True, f"Contract role {contract_role} assigned successfully"
            else:
                return False, f"Failed to assign role: {message}"
                
        except Exception as e:
            return False, f"Role assignment failed: {str(e)}"
    
    def get_pending_verifications(self) -> List[Dict[str, Any]]:
        """Get list of pending government official verifications"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            return list(officials_data.get('pending_verifications', {}).values())
            
        except Exception as e:
            print(f"Error getting pending verifications: {e}")
            return []
    
    def search_jurisdictions(self, query: str = "", level: Optional[RealWorldGovLevel] = None,
                           country: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search government jurisdictions"""
        
        try:
            jurisdictions_data = self._load_json(self.jurisdictions_db)
            jurisdictions = list(jurisdictions_data.get('jurisdictions', {}).values())
            
            # Apply filters
            if query:
                jurisdictions = [j for j in jurisdictions if query.lower() in j['name'].lower()]
            
            if level:
                jurisdictions = [j for j in jurisdictions if j['level'] == level.value]
            
            if country:
                jurisdictions = [j for j in jurisdictions if j['country'].lower() == country.lower()]
            
            return jurisdictions
            
        except Exception as e:
            print(f"Error searching jurisdictions: {e}")
            return []
    
    def get_government_officials_by_jurisdiction(self, jurisdiction_id: str) -> List[Dict[str, Any]]:
        """Get all government officials in a jurisdiction"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            officials = list(officials_data.get('officials', {}).values())
            
            return [o for o in officials if o['jurisdiction_id'] == jurisdiction_id]
            
        except Exception as e:
            print(f"Error getting officials for jurisdiction: {e}")
            return []
    
    def get_user_government_positions(self, user_email: str) -> List[Dict[str, Any]]:
        """Get all government positions held by a user"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            officials = list(officials_data.get('officials', {}).values())
            
            return [o for o in officials if o['user_email'] == user_email]
            
        except Exception as e:
            print(f"Error getting user government positions: {e}")
            return []
    
    def get_government_integration_stats(self) -> Dict[str, Any]:
        """Get statistics about government integration"""
        
        try:
            jurisdictions_data = self._load_json(self.jurisdictions_db)
            officials_data = self._load_json(self.officials_db)
            
            # Count jurisdictions by level
            jurisdiction_counts = {}
            for jurisdiction in jurisdictions_data.get('jurisdictions', {}).values():
                level = jurisdiction['level']
                jurisdiction_counts[level] = jurisdiction_counts.get(level, 0) + 1
            
            # Count officials by status
            official_counts = {status.value: 0 for status in VerificationStatus}
            for official in officials_data.get('officials', {}).values():
                status = official['verification_status']
                official_counts[status] += 1
            
            # Count by position type
            position_counts = {}
            for official in officials_data.get('officials', {}).values():
                position = official['position']
                position_counts[position] = position_counts.get(position, 0) + 1
            
            return {
                'total_jurisdictions': jurisdictions_data.get('total_jurisdictions', 0),
                'jurisdictions_by_level': jurisdiction_counts,
                'total_officials_registered': len(officials_data.get('officials', {})),
                'officials_by_status': official_counts,
                'officials_by_position': position_counts,
                'pending_verifications': len(officials_data.get('verification_queue', [])),
                'integration_active': True,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get stats: {str(e)}",
                'integration_active': False
            }


# Example usage and demo functions
def demo_government_integration():
    """Demonstrate the government integration system"""
    
    print("\n🏛️ REAL-WORLD GOVERNMENT INTEGRATION DEMONSTRATION")
    print("=" * 70)
    
    # Initialize manager
    manager = RealWorldGovernmentManager()
    
    # Demo 1: Register jurisdictions
    print("\n📍 DEMO 1: Registering Government Jurisdictions")
    print("-" * 50)
    
    jurisdictions = [
        {
            'name': 'Springfield',
            'level': RealWorldGovLevel.MUNICIPAL,
            'country': 'United States',
            'state': 'Illinois',
            'population': 200000,
            'website': 'https://springfield.il.gov'
        },
        {
            'name': 'Illinois',
            'level': RealWorldGovLevel.STATE,
            'country': 'United States',
            'population': 12600000,
            'website': 'https://illinois.gov'
        },
        {
            'name': 'United States',
            'level': RealWorldGovLevel.FEDERAL,
            'country': 'United States',
            'population': 330000000,
            'website': 'https://usa.gov'
        }
    ]
    
    jurisdiction_ids = {}
    for jurisdiction in jurisdictions:
        success, message, jurisdiction_id = manager.register_jurisdiction(**jurisdiction)
        jurisdiction_ids[jurisdiction['name']] = jurisdiction_id
        print(f"   {'✅' if success else '❌'} {jurisdiction['name']}: {message}")
    
    # Demo 2: Register government officials
    print("\n👥 DEMO 2: Registering Government Officials")
    print("-" * 50)
    
    officials = [
        {
            'user_email': 'mayor.johnson@springfield.gov',
            'jurisdiction_id': jurisdiction_ids.get('Springfield', ''),
            'position': RealWorldPosition.MAYOR,
            'position_title': 'Mayor of Springfield, Illinois',
            'term_start': '2023-01-01',
            'term_end': '2027-01-01'
        },
        {
            'user_email': 'governor.smith@illinois.gov',
            'jurisdiction_id': jurisdiction_ids.get('Illinois', ''),
            'position': RealWorldPosition.GOVERNOR,
            'position_title': 'Governor of Illinois',
            'term_start': '2023-01-09',
            'term_end': '2027-01-09'
        },
        {
            'user_email': 'senator.davis@senate.gov',
            'jurisdiction_id': jurisdiction_ids.get('United States', ''),
            'position': RealWorldPosition.US_SENATOR,
            'position_title': 'United States Senator from Illinois',
            'term_start': '2021-01-03',
            'term_end': '2027-01-03'
        }
    ]
    
    official_ids = []
    for official in officials:
        success, message, official_id = manager.register_government_official(**official)
        official_ids.append(official_id)
        print(f"   {'✅' if success else '❌'} {official['position_title']}: {message}")
    
    # Demo 3: Show pending verifications
    print("\n⏳ DEMO 3: Pending Verifications")
    print("-" * 50)
    
    pending = manager.get_pending_verifications()
    print(f"   Pending verifications: {len(pending)}")
    for verification in pending:
        print(f"   - {verification['position_title']} ({verification['user_email']})")
    
    # Demo 4: Verify officials
    print("\n✅ DEMO 4: Verifying Government Officials")
    print("-" * 50)
    
    for official_id in official_ids:
        if official_id:
            success, message = manager.verify_government_official(
                official_id, 
                "contract_founder@system", 
                "Verified through official government channels"
            )
            print(f"   {'✅' if success else '❌'} {official_id}: {message}")
    
    # Demo 5: Show integration statistics
    print("\n📊 DEMO 5: Government Integration Statistics")
    print("-" * 50)
    
    stats = manager.get_government_integration_stats()
    print(f"   Total jurisdictions: {stats.get('total_jurisdictions', 0)}")
    print(f"   Total officials registered: {stats.get('total_officials_registered', 0)}")
    print(f"   Verified officials: {stats.get('officials_by_status', {}).get('verified', 0)}")
    print(f"   Pending verifications: {stats.get('pending_verifications', 0)}")
    
    print("\n🎉 Government integration demonstration complete!")


if __name__ == "__main__":
    demo_government_integration()