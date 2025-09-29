"""
COUNTRY CONTRACT ELECTION SYSTEM - National Level Governance Elections
Handles country-level contract governance elections with state electoral participation
Format: "Contract Senator/Representative for [Country Name]"
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
    from civic_desktop.governance.state_elections import StateElectionManager
    STATE_ELECTIONS_AVAILABLE = True
except ImportError:
    STATE_ELECTIONS_AVAILABLE = False


class CountryOffice(Enum):
    """Contract-based country governance offices"""
    COUNTRY_REPRESENTATIVE = "contract_country_representative"
    COUNTRY_SENATOR = "contract_country_senator"


class CountryElectionTrigger(Enum):
    """Triggers for country contract elections"""
    INITIAL_THRESHOLD = "initial_threshold"      # 1% of states have full representation
    EXPANSION_THRESHOLD = "expansion_threshold"  # 50% of states have full representation
    SCHEDULED_ELECTION = "scheduled_election"    # Regular scheduled election
    SPECIAL_ELECTION = "special_election"        # Special circumstances


class CountryElectionStatus(Enum):
    """Status of country contract elections"""
    NOT_TRIGGERED = "not_triggered"              # Thresholds not met
    REGISTRATION_OPEN = "registration_open"      # Candidate registration period
    CAMPAIGN_PERIOD = "campaign_period"          # Active campaigning
    VOTING_OPEN = "voting_open"                  # State electoral voting period
    VOTING_CLOSED = "voting_closed"              # Voting ended, counting in progress
    RESULTS_CERTIFIED = "results_certified"      # Official results published
    ELECTION_COMPLETED = "election_completed"    # Winners installed, election archived


@dataclass
class CountryElectionConfig:
    """Configuration for country elections"""
    country_id: str
    country_name: str
    total_population_estimate: int
    
    # Election thresholds (based on states with full representation)
    initial_threshold_percent: float = 0.01    # 1% of states to trigger first election
    expansion_threshold_percent: float = 0.50  # 50% of states to trigger ongoing elections
    
    # Representation rules
    base_senators: int = 2                     # Minimum senators per country
    base_representatives: int = 2              # Minimum representatives per country
    rep_per_million: int = 1                   # Additional reps per 1 million people
    
    # Term settings
    term_length_years: int = 1                 # Term length in years
    max_total_terms: int = 4                   # Max 4 terms total (not consecutive)
    consecutive_term_restriction: bool = True   # Cannot be consecutive
    
    # Election timing
    registration_period_days: int = 30         # Candidate registration period
    campaign_period_days: int = 60             # Campaign period length
    voting_period_days: int = 7                # Voting window for states


@dataclass
class CountryCandidate:
    """Candidate for contract-based country governance office"""
    candidate_id: str
    user_email: str
    country_id: str
    office: CountryOffice
    platform_statement: str
    campaign_slogan: str
    endorsements: List[str]
    previous_terms: int
    registered_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_formatted_title(self, country_name: str) -> str:
        """Get properly formatted contract role title"""
        if self.office == CountryOffice.COUNTRY_REPRESENTATIVE:
            return f"Contract Representative for {country_name}"
        elif self.office == CountryOffice.COUNTRY_SENATOR:
            return f"Contract Senator for {country_name}"
        else:
            return f"Contract {self.office.value.replace('contract_country_', '').replace('_', ' ').title()} for {country_name}"


@dataclass
class CountryElection:
    """Country contract election instance with state electoral participation"""
    election_id: str
    country_id: str
    country_name: str
    trigger_type: CountryElectionTrigger
    status: CountryElectionStatus
    
    # Election timeline
    registration_start: datetime
    registration_end: datetime
    campaign_start: datetime
    campaign_end: datetime
    voting_start: datetime
    voting_end: datetime
    
    # Candidates and results
    candidates: Dict[str, CountryCandidate]
    participating_states: List[str]
    state_votes: Dict[str, Dict[str, int]]  # state_id -> {candidate_id: votes}
    electoral_votes: Dict[str, int]         # candidate_id -> total electoral votes
    winners: Dict[CountryOffice, str]       # office -> candidate_id
    
    # Metadata
    created_at: datetime
    completed_at: Optional[datetime] = None


class CountryElectionManager:
    """Manager for country-level contract governance elections with state electoral participation"""
    
    def __init__(self, config_path: str = None):
        """Initialize country election manager"""
        
        # Set up data paths
        if config_path:
            base_path = os.path.dirname(config_path)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        self.countries_db_path = os.path.join(base_path, 'countries_db.json')
        self.country_elections_db_path = os.path.join(base_path, 'country_elections_db.json')
        self.country_candidates_db_path = os.path.join(base_path, 'country_candidates_db.json')
        
        # Initialize external dependencies
        self.blockchain = CivicBlockchain() if BLOCKCHAIN_AVAILABLE else None
        self.user_backend = UserBackend() if USER_BACKEND_AVAILABLE else None
        self.task_manager = TaskManager() if TASKS_AVAILABLE else None
        self.state_election_manager = StateElectionManager() if STATE_ELECTIONS_AVAILABLE else None
        
        # Initialize databases
        self._initialize_databases()
    
    def _initialize_databases(self):
        """Initialize country election databases"""
        
        # Countries database
        if not os.path.exists(self.countries_db_path):
            initial_countries = {
                "countries": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_json(self.countries_db_path, initial_countries)
        
        # Country elections database
        if not os.path.exists(self.country_elections_db_path):
            initial_elections = {
                "elections": {},
                "active_elections": {},
                "election_history": [],
                "last_updated": datetime.now().isoformat()
            }
            self._save_json(self.country_elections_db_path, initial_elections)
        
        # Country candidates database
        if not os.path.exists(self.country_candidates_db_path):
            initial_candidates = {
                "candidates": {},
                "candidate_history": [],
                "endorsements": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_json(self.country_candidates_db_path, initial_candidates)
    
    def register_country(self, country_name: str, total_population_estimate: int, **kwargs) -> Tuple[bool, str, str]:
        """Register a new country for contract governance elections"""
        
        try:
            countries_data = self._load_json(self.countries_db_path)
            
            # Generate country ID
            country_id = f"country_{country_name.lower().replace(' ', '_').replace('-', '_')}_{str(uuid4())[:8]}"
            
            # Create country configuration
            config = CountryElectionConfig(
                country_id=country_id,
                country_name=country_name,
                total_population_estimate=total_population_estimate,
                **kwargs
            )
            
            # Calculate representation
            total_reps = max(config.base_representatives, 
                           config.base_representatives + (total_population_estimate // 1000000) * config.rep_per_million)
            
            # Store country data
            countries_data["countries"][country_id] = {
                "config": asdict(config),
                "total_representatives": total_reps,
                "total_senators": config.base_senators,
                "registered_at": datetime.now().isoformat(),
                "status": "registered"
            }
            
            countries_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.countries_db_path, countries_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="country_registered",
                    data={
                        "country_id": country_id,
                        "country_name": country_name,
                        "population": total_population_estimate,
                        "representatives": total_reps,
                        "senators": config.base_senators
                    },
                    user_email="system"
                )
            
            return True, f"Country '{country_name}' registered successfully with {total_reps} representatives and {config.base_senators} senators", country_id
            
        except Exception as e:
            return False, f"Failed to register country: {str(e)}", ""
    
    def check_election_triggers(self, country_id: str) -> Tuple[bool, CountryElectionTrigger, str]:
        """Check if country contract elections should be triggered"""
        
        try:
            if not self.state_election_manager:
                return False, None, "State election system not available"
            
            countries_data = self._load_json(self.countries_db_path)
            
            if country_id not in countries_data["countries"]:
                return False, None, "Country not found"
            
            country_config = CountryElectionConfig(**countries_data["countries"][country_id]["config"])
            
            # Get states with full representation in this country
            states_with_representation = self._get_states_with_full_representation(country_config.country_name)
            total_states_in_country = self._get_total_states_in_country(country_config.country_name)
            
            if total_states_in_country == 0:
                return False, None, "No states registered in this country"
            
            representation_percentage = len(states_with_representation) / total_states_in_country
            
            # Check for initial threshold trigger (1% of states)
            if representation_percentage >= country_config.initial_threshold_percent:
                active_elections = self._load_json(self.country_elections_db_path)["active_elections"]
                
                if country_id not in active_elections:
                    if representation_percentage >= country_config.expansion_threshold_percent:
                        return True, CountryElectionTrigger.EXPANSION_THRESHOLD, f"50% threshold reached ({representation_percentage:.1%})"
                    else:
                        return True, CountryElectionTrigger.INITIAL_THRESHOLD, f"Initial threshold reached ({representation_percentage:.1%})"
            
            return False, None, f"Threshold not met ({representation_percentage:.1%})"
            
        except Exception as e:
            return False, None, f"Error checking triggers: {str(e)}"
    
    def create_country_election(self, country_id: str, trigger_type: CountryElectionTrigger) -> Tuple[bool, str, str]:
        """Create a new country contract election"""
        
        try:
            countries_data = self._load_json(self.countries_db_path)
            
            if country_id not in countries_data["countries"]:
                return False, "Country not found", ""
            
            country_config = CountryElectionConfig(**countries_data["countries"][country_id]["config"])
            
            # Generate election ID
            election_id = f"country_election_{country_id}_{str(uuid4())[:8]}"
            
            # Calculate election timeline
            now = datetime.now()
            registration_start = now
            registration_end = now + timedelta(days=country_config.registration_period_days)
            campaign_start = registration_end
            campaign_end = campaign_start + timedelta(days=country_config.campaign_period_days)
            voting_start = campaign_end
            voting_end = voting_start + timedelta(days=country_config.voting_period_days)
            
            # Create election instance
            election = CountryElection(
                election_id=election_id,
                country_id=country_id,
                country_name=country_config.country_name,
                trigger_type=trigger_type,
                status=CountryElectionStatus.REGISTRATION_OPEN,
                registration_start=registration_start,
                registration_end=registration_end,
                campaign_start=campaign_start,
                campaign_end=campaign_end,
                voting_start=voting_start,
                voting_end=voting_end,
                candidates={},
                participating_states=self._get_states_with_full_representation(country_config.country_name),
                state_votes={},
                electoral_votes={},
                winners={},
                created_at=now
            )
            
            # Store election
            elections_data = self._load_json(self.country_elections_db_path)
            elections_data["elections"][election_id] = asdict(election)
            elections_data["active_elections"][country_id] = election_id
            elections_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.country_elections_db_path, elections_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="country_election_created",
                    data={
                        "election_id": election_id,
                        "country_id": country_id,
                        "country_name": country_config.country_name,
                        "trigger_type": trigger_type.value,
                        "participating_states": len(election.participating_states)
                    },
                    user_email="system"
                )
            
            # Create task notification
            if self.task_manager:
                self.task_manager.create_task(
                    task_type="country_contract_election",
                    title=f"Country Contract Election - {country_config.country_name}",
                    description=f"Contract governance election for {country_config.country_name} is now open for candidate registration.",
                    priority="high",
                    data={"election_id": election_id, "country_id": country_id}
                )
            
            return True, f"Country contract election created for {country_config.country_name}", election_id
            
        except Exception as e:
            return False, f"Failed to create country election: {str(e)}", ""
    
    def register_country_candidate(self, country_id: str, user_email: str, office: CountryOffice, 
                                 platform_statement: str, campaign_slogan: str) -> Tuple[bool, str]:
        """Register a candidate for country contract office"""
        
        try:
            # Verify eligibility - must have been a state representative or senator
            if not self._verify_state_experience(user_email, country_id):
                return False, "Candidate must have served as a state contract representative or senator"
            
            # Check term limits
            if not self._check_country_term_limits(user_email, office):
                return False, "Candidate has reached maximum consecutive term limits"
            
            elections_data = self._load_json(self.country_elections_db_path)
            
            # Find active election for country
            if country_id not in elections_data["active_elections"]:
                return False, "No active country election found"
            
            election_id = elections_data["active_elections"][country_id]
            election = CountryElection(**elections_data["elections"][election_id])
            
            # Check if registration is open
            if election.status != CountryElectionStatus.REGISTRATION_OPEN:
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
            candidate_id = f"country_candidate_{str(uuid4())[:8]}"
            
            # Create candidate
            candidate = CountryCandidate(
                candidate_id=candidate_id,
                user_email=user_email,
                country_id=country_id,
                office=office,
                platform_statement=platform_statement,
                campaign_slogan=campaign_slogan,
                endorsements=[],
                previous_terms=self._get_previous_country_terms(user_email, office),
                registered_at=datetime.now()
            )
            
            # Store candidate
            election.candidates[candidate_id] = candidate
            elections_data["elections"][election_id] = asdict(election)
            elections_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.country_elections_db_path, elections_data)
            
            # Store in candidates database
            candidates_data = self._load_json(self.country_candidates_db_path)
            candidates_data["candidates"][candidate_id] = asdict(candidate)
            candidates_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.country_candidates_db_path, candidates_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="country_candidate_registered",
                    data={
                        "candidate_id": candidate_id,
                        "user_email": user_email,
                        "country_id": country_id,
                        "office": office.value,
                        "election_id": election_id
                    },
                    user_email=user_email
                )
            
            return True, f"Successfully registered as candidate for {office.value}"
            
        except Exception as e:
            return False, f"Failed to register candidate: {str(e)}"
    
    def _verify_state_experience(self, user_email: str, country_id: str) -> bool:
        """Verify candidate has state-level experience in the country"""
        
        if not self.state_election_manager:
            return True  # Allow if state system not available
        
        try:
            # Get country name
            countries_data = self._load_json(self.countries_db_path)
            country_name = countries_data["countries"][country_id]["config"]["country_name"]
            
            # Check state election history for this user
            # Implementation would check if user served as state rep/senator in any state within this country
            return True  # Placeholder - implement actual verification
            
        except Exception:
            return True  # Allow if verification fails
    
    def _check_country_term_limits(self, user_email: str, office: CountryOffice) -> bool:
        """Check if candidate has reached term limits
        
        Rule: Max 4 terms total, cannot be consecutive (1-year break required)
        """
        
        try:
            # Get all previous terms for this office
            previous_terms = self._get_all_country_terms(user_email, office)
            
            # Check maximum total terms (4)
            if len(previous_terms) >= 4:
                return False  # Maximum 4 terms total reached
            
            # Check consecutive terms restriction (1-year break required)
            if previous_terms and self._has_consecutive_country_terms_issue(previous_terms):
                return False  # Cannot serve consecutive terms
            
            return True  # Eligible to run
            
        except Exception:
            return False  # Err on side of caution - block if can't verify
    
    def _get_previous_country_terms(self, user_email: str, office: CountryOffice) -> int:
        """Get number of previous terms served in country office"""
        # Implementation would count previous terms from election history
        return 0  # Placeholder
    
    def _get_consecutive_country_terms(self, user_email: str, office: CountryOffice) -> int:
        """Get number of consecutive terms currently served"""
        # Implementation would count consecutive terms from election history
        return 0  # Placeholder
    
    def _get_states_with_full_representation(self, country_name: str) -> List[str]:
        """Get list of state IDs that have full representation in the country"""
        
        if not self.state_election_manager:
            return []
        
        try:
            # Implementation would check state election manager for states with elected representatives
            return []  # Placeholder
            
        except Exception:
            return []
    
    def _get_total_states_in_country(self, country_name: str) -> int:
        """Get total number of states registered in the country"""
        
        if not self.state_election_manager:
            return 0
        
        try:
            # Implementation would count registered states in the country
            return 1  # Placeholder
            
        except Exception:
            return 0
    
    def get_country_representation(self, country_id: str) -> Dict[str, Any]:
        """Get current representation information for country"""
        
        try:
            countries_data = self._load_json(self.countries_db_path)
            
            if country_id not in countries_data["countries"]:
                return {}
            
            country_data = countries_data["countries"][country_id]
            config = CountryElectionConfig(**country_data["config"])
            
            # Calculate current representation
            total_population = config.total_population_estimate
            calculated_reps = max(config.base_representatives, 
                                config.base_representatives + (total_population // 1000000) * config.rep_per_million)
            
            return {
                "country_name": config.country_name,
                "population": total_population,
                "total_representatives": calculated_reps,
                "total_senators": config.base_senators,
                "base_representatives": config.base_representatives,
                "additional_reps_from_population": calculated_reps - config.base_representatives,
                "rep_calculation": f"{config.base_representatives} base + {(total_population // 1000000)} million population units = {calculated_reps} total"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_active_country_elections(self) -> Dict[str, Any]:
        """Get all active country contract elections"""
        
        try:
            elections_data = self._load_json(self.country_elections_db_path)
            active_elections = {}
            
            for country_id, election_id in elections_data["active_elections"].items():
                if election_id in elections_data["elections"]:
                    election_data = elections_data["elections"][election_id]
                    active_elections[country_id] = {
                        "election_id": election_id,
                        "country_name": election_data["country_name"],
                        "status": election_data["status"],
                        "candidate_count": len(election_data["candidates"]),
                        "participating_states": len(election_data["participating_states"]),
                        "registration_end": election_data["registration_end"],
                        "voting_start": election_data["voting_start"],
                        "voting_end": election_data["voting_end"]
                    }
            
            return active_elections
            
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
    print("🏛️ Country Contract Election System")
    print("=" * 50)
    
    manager = CountryElectionManager()
    
    # Test country registration
    success, msg, country_id = manager.register_country(
        country_name="United States",
        total_population_estimate=330000000  # 330 million people
    )
    
    if success:
        print(f"✅ {msg}")
        print(f"Country ID: {country_id}")
        
        # Show representation calculation
        rep_info = manager.get_country_representation(country_id)
        print(f"\nRepresentation Calculation:")
        print(f"- Population: {rep_info['population']:,}")
        print(f"- Total Representatives: {rep_info['total_representatives']}")
        print(f"- Total Senators: {rep_info['total_senators']}")
        print(f"- Calculation: {rep_info['rep_calculation']}")
    else:
        print(f"❌ {msg}")