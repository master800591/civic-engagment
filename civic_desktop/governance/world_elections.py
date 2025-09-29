"""
WORLD CONTRACT ELECTION SYSTEM - Global Level Governance Elections
Handles world-level contract governance elections with country electoral participation
Format: "Contract Senator/Representative for World"
"""

import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from uuid import uuid4

# Optional imports with fallback handling
try:
    from civic_desktop.blockchain.blockchain import CivicBlockchain
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False

try:
    from civic_desktop.users.backend import UserBackend
    USER_BACKEND_AVAILABLE = True
except ImportError:
    USER_BACKEND_AVAILABLE = False

try:
    from civic_desktop.tasks.task_manager import TaskManager
    TASKS_AVAILABLE = True
except ImportError:
    TASKS_AVAILABLE = False

try:
    from civic_desktop.governance.country_elections import CountryElectionManager
    COUNTRY_ELECTIONS_AVAILABLE = True
except ImportError:
    COUNTRY_ELECTIONS_AVAILABLE = False


class WorldOffice(Enum):
    """Contract-based world governance offices"""
    WORLD_REPRESENTATIVE = "contract_world_representative"
    WORLD_SENATOR = "contract_world_senator"


class WorldElectionTrigger(Enum):
    """Triggers for world contract elections"""
    INITIAL_THRESHOLD = "initial_threshold"      # 1% of countries have full representation
    EXPANSION_THRESHOLD = "expansion_threshold"  # 50% of countries have full representation
    SCHEDULED_ELECTION = "scheduled_election"    # Regular scheduled election
    SPECIAL_ELECTION = "special_election"        # Special circumstances


class WorldElectionStatus(Enum):
    """Status of world contract elections"""
    NOT_TRIGGERED = "not_triggered"              # Thresholds not met
    REGISTRATION_OPEN = "registration_open"      # Candidate registration period
    CAMPAIGN_PERIOD = "campaign_period"          # Active campaigning
    VOTING_OPEN = "voting_open"                  # Country electoral voting period
    VOTING_CLOSED = "voting_closed"              # Voting ended, counting in progress
    RESULTS_CERTIFIED = "results_certified"      # Official results published
    ELECTION_COMPLETED = "election_completed"    # Winners installed, election archived


@dataclass
class WorldElectionConfig:
    """Configuration for world elections"""
    world_id: str = "world_global"
    world_name: str = "World"
    total_population_estimate: int = 8000000000  # 8 billion people
    
    # Election thresholds (based on countries with full representation)
    initial_threshold_percent: float = 0.01    # 1% of countries to trigger first election
    expansion_threshold_percent: float = 0.50  # 50% of countries to trigger ongoing elections
    
    # Representation rules
    base_senators: int = 2                     # Minimum senators for world
    base_representatives: int = 2              # Minimum representatives for world
    rep_per_four_million: int = 1              # Additional reps per 4 million people
    
    # Term settings
    term_length_years: int = 1                 # Term length in years
    max_total_terms: int = 4                   # Max 4 terms total (not consecutive)
    consecutive_term_restriction: bool = True   # Cannot be consecutive
    
    # Election timing
    registration_period_days: int = 30         # Candidate registration period
    campaign_period_days: int = 60             # Campaign period length
    voting_period_days: int = 7                # Voting window for countries


@dataclass
class WorldCandidate:
    """Candidate for contract-based world governance office"""
    candidate_id: str
    user_email: str
    world_id: str
    office: WorldOffice
    platform_statement: str
    campaign_slogan: str
    endorsements: List[str]
    previous_terms: int
    country_of_origin: str
    registered_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_formatted_title(self) -> str:
        """Get properly formatted contract role title"""
        if self.office == WorldOffice.WORLD_REPRESENTATIVE:
            return "Contract Representative for World"
        elif self.office == WorldOffice.WORLD_SENATOR:
            return "Contract Senator for World"
        else:
            return f"Contract {self.office.value.replace('contract_world_', '').replace('_', ' ').title()} for World"


@dataclass
class WorldElection:
    """World contract election instance with country electoral participation"""
    election_id: str
    world_id: str
    world_name: str
    trigger_type: WorldElectionTrigger
    status: WorldElectionStatus
    
    # Election timeline
    registration_start: datetime
    registration_end: datetime
    campaign_start: datetime
    campaign_end: datetime
    voting_start: datetime
    voting_end: datetime
    
    # Candidates and results
    candidates: Dict[str, WorldCandidate]
    participating_countries: List[str]
    country_votes: Dict[str, Dict[str, int]]  # country_id -> {candidate_id: votes}
    electoral_votes: Dict[str, int]           # candidate_id -> total electoral votes
    winners: Dict[WorldOffice, str]           # office -> candidate_id
    
    # Metadata
    created_at: datetime
    completed_at: Optional[datetime] = None


class WorldElectionManager:
    """Manager for world-level contract governance elections with country electoral participation"""
    
    def __init__(self, config_path: str = None):
        """Initialize world election manager"""
        
        # Set up data paths
        if config_path:
            base_path = os.path.dirname(config_path)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        self.world_db_path = os.path.join(base_path, 'world_db.json')
        self.world_elections_db_path = os.path.join(base_path, 'world_elections_db.json')
        self.world_candidates_db_path = os.path.join(base_path, 'world_candidates_db.json')
        
        # Initialize external dependencies
        self.blockchain = CivicBlockchain() if BLOCKCHAIN_AVAILABLE else None
        self.user_backend = UserBackend() if USER_BACKEND_AVAILABLE else None
        self.task_manager = TaskManager() if TASKS_AVAILABLE else None
        self.country_election_manager = CountryElectionManager() if COUNTRY_ELECTIONS_AVAILABLE else None
        
        # Initialize databases
        self._initialize_databases()
    
    def _initialize_databases(self):
        """Initialize world election databases"""
        
        # World database
        if not os.path.exists(self.world_db_path):
            initial_world = {
                "world": {
                    "world_global": {
                        "config": asdict(WorldElectionConfig()),
                        "registered_at": datetime.now().isoformat(),
                        "status": "active"
                    }
                },
                "last_updated": datetime.now().isoformat()
            }
            self._save_json(self.world_db_path, initial_world)
        
        # World elections database
        if not os.path.exists(self.world_elections_db_path):
            initial_elections = {
                "elections": {},
                "active_elections": {},
                "election_history": [],
                "last_updated": datetime.now().isoformat()
            }
            self._save_json(self.world_elections_db_path, initial_elections)
        
        # World candidates database
        if not os.path.exists(self.world_candidates_db_path):
            initial_candidates = {
                "candidates": {},
                "candidate_history": [],
                "endorsements": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_json(self.world_candidates_db_path, initial_candidates)
    
    def get_world_configuration(self) -> WorldElectionConfig:
        """Get world election configuration"""
        
        try:
            world_data = self._load_json(self.world_db_path)
            config_data = world_data["world"]["world_global"]["config"]
            return WorldElectionConfig(**config_data)
        except Exception:
            return WorldElectionConfig()
    
    def update_world_population(self, new_population: int) -> Tuple[bool, str]:
        """Update world population estimate"""
        
        try:
            world_data = self._load_json(self.world_db_path)
            
            config = self.get_world_configuration()
            config.total_population_estimate = new_population
            
            world_data["world"]["world_global"]["config"] = asdict(config)
            world_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.world_db_path, world_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="world_population_updated",
                    data={
                        "new_population": new_population,
                        "representation_calculation": self._calculate_world_representation(new_population)
                    },
                    user_email="system"
                )
            
            return True, f"World population updated to {new_population:,}"
            
        except Exception as e:
            return False, f"Failed to update population: {str(e)}"
    
    def _calculate_world_representation(self, population: int) -> Dict[str, int]:
        """Calculate world representation based on population"""
        
        config = self.get_world_configuration()
        
        # Calculate representatives: base + 1 per 4 million people
        additional_reps = population // 4000000  # 1 rep per 4 million
        total_reps = config.base_representatives + additional_reps
        
        return {
            "total_representatives": total_reps,
            "base_representatives": config.base_representatives,
            "additional_representatives": additional_reps,
            "total_senators": config.base_senators,
            "population": population,
            "calculation": f"{config.base_representatives} base + {additional_reps} from population = {total_reps} total"
        }
    
    def check_election_triggers(self) -> Tuple[bool, WorldElectionTrigger, str]:
        """Check if world contract elections should be triggered"""
        
        try:
            if not self.country_election_manager:
                return False, None, "Country election system not available"
            
            # Get countries with full representation
            countries_with_representation = self._get_countries_with_full_representation()
            total_countries = self._get_total_countries()
            
            if total_countries == 0:
                return False, None, "No countries registered"
            
            representation_percentage = len(countries_with_representation) / total_countries
            
            # Check for election triggers
            config = self.get_world_configuration()
            
            if representation_percentage >= config.initial_threshold_percent:
                elections_data = self._load_json(self.world_elections_db_path)
                
                if "world_global" not in elections_data["active_elections"]:
                    if representation_percentage >= config.expansion_threshold_percent:
                        return True, WorldElectionTrigger.EXPANSION_THRESHOLD, f"50% threshold reached ({representation_percentage:.1%})"
                    else:
                        return True, WorldElectionTrigger.INITIAL_THRESHOLD, f"Initial threshold reached ({representation_percentage:.1%})"
            
            return False, None, f"Threshold not met ({representation_percentage:.1%})"
            
        except Exception as e:
            return False, None, f"Error checking triggers: {str(e)}"
    
    def create_world_election(self, trigger_type: WorldElectionTrigger) -> Tuple[bool, str, str]:
        """Create a new world contract election"""
        
        try:
            config = self.get_world_configuration()
            
            # Generate election ID
            election_id = f"world_election_{str(uuid4())[:8]}"
            
            # Calculate election timeline
            now = datetime.now()
            registration_start = now
            registration_end = now + timedelta(days=config.registration_period_days)
            campaign_start = registration_end
            campaign_end = campaign_start + timedelta(days=config.campaign_period_days)
            voting_start = campaign_end
            voting_end = voting_start + timedelta(days=config.voting_period_days)
            
            # Create election instance
            election = WorldElection(
                election_id=election_id,
                world_id=config.world_id,
                world_name=config.world_name,
                trigger_type=trigger_type,
                status=WorldElectionStatus.REGISTRATION_OPEN,
                registration_start=registration_start,
                registration_end=registration_end,
                campaign_start=campaign_start,
                campaign_end=campaign_end,
                voting_start=voting_start,
                voting_end=voting_end,
                candidates={},
                participating_countries=self._get_countries_with_full_representation(),
                country_votes={},
                electoral_votes={},
                winners={},
                created_at=now
            )
            
            # Store election
            elections_data = self._load_json(self.world_elections_db_path)
            elections_data["elections"][election_id] = asdict(election)
            elections_data["active_elections"]["world_global"] = election_id
            elections_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.world_elections_db_path, elections_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="world_election_created",
                    data={
                        "election_id": election_id,
                        "trigger_type": trigger_type.value,
                        "participating_countries": len(election.participating_countries),
                        "representation": self._calculate_world_representation(config.total_population_estimate)
                    },
                    user_email="system"
                )
            
            # Create task notification
            if self.task_manager:
                self.task_manager.create_task(
                    task_type="world_contract_election",
                    title="World Contract Election",
                    description="Global contract governance election is now open for candidate registration.",
                    priority="critical",
                    data={"election_id": election_id}
                )
            
            return True, f"World contract election created", election_id
            
        except Exception as e:
            return False, f"Failed to create world election: {str(e)}", ""
    
    def register_world_candidate(self, user_email: str, office: WorldOffice, 
                                platform_statement: str, campaign_slogan: str, 
                                country_of_origin: str) -> Tuple[bool, str]:
        """Register a candidate for world contract office"""
        
        try:
            # Verify eligibility - must have been a country representative or senator
            if not self._verify_country_experience(user_email, country_of_origin):
                return False, "Candidate must have served as a country contract representative or senator"
            
            # Check term limits
            if not self._check_world_term_limits(user_email, office):
                return False, "Candidate has reached maximum consecutive term limits"
            
            elections_data = self._load_json(self.world_elections_db_path)
            
            # Find active world election
            if "world_global" not in elections_data["active_elections"]:
                return False, "No active world election found"
            
            election_id = elections_data["active_elections"]["world_global"]
            election = WorldElection(**elections_data["elections"][election_id])
            
            # Check if registration is open
            if election.status != WorldElectionStatus.REGISTRATION_OPEN:
                return False, "Candidate registration is not currently open"
            
            if datetime.now() > election.registration_end:
                return False, "Registration period has ended"
            
            # Check if user already registered
            existing_candidate = None
            for candidate in election.candidates.values():
                if candidate["user_email"] == user_email:
                    existing_candidate = candidate
                    break
            
            if existing_candidate:
                return False, "User already registered as candidate in this election"
            
            # Generate candidate ID
            candidate_id = f"world_candidate_{str(uuid4())[:8]}"
            
            # Create candidate
            candidate = WorldCandidate(
                candidate_id=candidate_id,
                user_email=user_email,
                world_id="world_global",
                office=office,
                platform_statement=platform_statement,
                campaign_slogan=campaign_slogan,
                endorsements=[],
                previous_terms=self._get_previous_world_terms(user_email, office),
                country_of_origin=country_of_origin,
                registered_at=datetime.now()
            )
            
            # Store candidate
            election.candidates[candidate_id] = candidate
            elections_data["elections"][election_id] = asdict(election)
            elections_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.world_elections_db_path, elections_data)
            
            # Store in candidates database
            candidates_data = self._load_json(self.world_candidates_db_path)
            candidates_data["candidates"][candidate_id] = asdict(candidate)
            candidates_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.world_candidates_db_path, candidates_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="world_candidate_registered",
                    data={
                        "candidate_id": candidate_id,
                        "user_email": user_email,
                        "office": office.value,
                        "country_of_origin": country_of_origin,
                        "election_id": election_id
                    },
                    user_email=user_email
                )
            
            return True, f"Successfully registered as candidate for {office.value}"
            
        except Exception as e:
            return False, f"Failed to register candidate: {str(e)}"
    
    def _verify_country_experience(self, user_email: str, country_of_origin: str) -> bool:
        """Verify candidate has country-level experience"""
        
        if not self.country_election_manager:
            return True  # Allow if country system not available
        
        try:
            # Check country election history for this user
            # Implementation would verify user served as country rep/senator
            return True  # Placeholder - implement actual verification
            
        except Exception:
            return True  # Allow if verification fails
    
    def _check_world_term_limits(self, user_email: str, office: WorldOffice) -> bool:
        """Check if candidate has reached term limits"""
        
        try:
            # Get candidate's world election history
            # Get all previous terms for this office
            previous_terms = self._get_all_world_terms(user_email, office)
            
            # Check maximum total terms (4)
            if len(previous_terms) >= 4:
                return False  # Maximum 4 terms total reached
            
            # Check consecutive terms restriction (1-year break required)
            if previous_terms and self._has_consecutive_world_terms_issue(previous_terms):
                return False  # Cannot serve consecutive terms
            
            return True  # Eligible to run
            
        except Exception:
            return True  # Allow if check fails
    
    def _get_previous_world_terms(self, user_email: str, office: WorldOffice) -> int:
        """Get number of previous terms served in world office"""
        # Implementation would count previous terms from election history
        return 0  # Placeholder
    
    def _get_consecutive_world_terms(self, user_email: str, office: WorldOffice) -> int:
        """Get number of consecutive terms currently served"""
        # Implementation would count consecutive terms from election history
        return 0  # Placeholder
    
    def _get_countries_with_full_representation(self) -> List[str]:
        """Get list of country IDs that have full representation"""
        
        if not self.country_election_manager:
            return []
        
        try:
            # Implementation would check country election manager for countries with elected representatives
            return []  # Placeholder
            
        except Exception:
            return []
    
    def _get_total_countries(self) -> int:
        """Get total number of countries registered"""
        
        if not self.country_election_manager:
            return 0
        
        try:
            # Implementation would count registered countries
            return 1  # Placeholder
            
        except Exception:
            return 0
    
    def get_world_representation(self) -> Dict[str, Any]:
        """Get current world representation information"""
        
        try:
            config = self.get_world_configuration()
            return self._calculate_world_representation(config.total_population_estimate)
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_active_world_election(self) -> Dict[str, Any]:
        """Get active world contract election"""
        
        try:
            elections_data = self._load_json(self.world_elections_db_path)
            
            if "world_global" not in elections_data["active_elections"]:
                return {}
            
            election_id = elections_data["active_elections"]["world_global"]
            if election_id in elections_data["elections"]:
                election_data = elections_data["elections"][election_id]
                return {
                    "election_id": election_id,
                    "status": election_data["status"],
                    "candidate_count": len(election_data["candidates"]),
                    "participating_countries": len(election_data["participating_countries"]),
                    "registration_end": election_data["registration_end"],
                    "voting_start": election_data["voting_start"],
                    "voting_end": election_data["voting_end"]
                }
            
            return {}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, file_path: str, data: Dict[str, Any]):
        """Save JSON data to file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)


# Main execution for testing
if __name__ == "__main__":
    print("🌍 World Contract Election System")
    print("=" * 50)
    
    manager = WorldElectionManager()
    
    # Show world representation calculation
    rep_info = manager.get_world_representation()
    if rep_info and 'error' not in rep_info:
        print(f"World Representation:")
        print(f"- Population: {rep_info['population']:,}")
        print(f"- Total Representatives: {rep_info['total_representatives']}")
        print(f"- Total Senators: {rep_info['total_senators']}")
        print(f"- Calculation: {rep_info['calculation']}")
    
    # Test population update
    success, msg = manager.update_world_population(8500000000)  # 8.5 billion
    if success:
        print(f"\n✅ {msg}")
        
        # Show updated representation
        rep_info = manager.get_world_representation()
        if rep_info and 'error' not in rep_info:
            print(f"Updated Calculation: {rep_info['calculation']}")
    else:
        print(f"❌ {msg}")