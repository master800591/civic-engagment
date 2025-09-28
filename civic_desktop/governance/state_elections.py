"""
STATE CONTRACT ELECTION SYSTEM - Electoral College Process for Contract Representatives and Senators
Handles state-level contract governance elections with city electoral college and eligibility requirements
Format: "Contract Senator/Representative for [State Name]"
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib

# Import task system components
try:
    from civic_desktop.tasks.task_types import TaskType
except ImportError:
    TaskType = None

# Import blockchain for recording elections
try:
    from civic_desktop.blockchain.blockchain import CivicBlockchain
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False

# Import user backend for verification
try:
    from civic_desktop.users.backend import UserBackend
    USER_BACKEND_AVAILABLE = True
except ImportError:
    USER_BACKEND_AVAILABLE = False

# Import task manager for notifications
try:
    from civic_desktop.tasks.task_manager import TaskManager
    TASKS_AVAILABLE = True
except ImportError:
    TASKS_AVAILABLE = False

# Import city elections for eligibility verification
try:
    from civic_desktop.governance.city_elections import CityElectionManager, CityOffice
    CITY_ELECTIONS_AVAILABLE = True
except ImportError:
    CITY_ELECTIONS_AVAILABLE = False


class StateElectionTrigger(Enum):
    """Triggers that initiate state elections"""
    INITIAL_THRESHOLD = "initial_1_percent"     # 1% of cities have representatives
    EXPANSION_THRESHOLD = "expansion_50_percent" # 50% of cities have representatives
    TERM_EXPIRATION = "term_expiration"         # End of 1-year term
    RECALL_ELECTION = "recall_election"         # Citizen-initiated recall
    VACANCY_ELECTION = "vacancy_election"       # Fill vacant position


class StateOffice(Enum):
    """Contract-based state governance offices"""
    STATE_REPRESENTATIVE = "contract_state_representative"
    STATE_SENATOR = "contract_state_senator"


class StateElectionStatus(Enum):
    """Current status of state election"""
    ELECTION_SCHEDULED = "election_scheduled"   # Election announced, candidates can register
    CAMPAIGN_ACTIVE = "campaign_active"        # Campaign period active
    VOTING_OPEN = "voting_open"                # Electoral college voting period
    VOTING_CLOSED = "voting_closed"            # Voting ended, counting in progress
    RESULTS_CERTIFIED = "results_certified"    # Official results published
    ELECTION_COMPLETED = "election_completed"  # Winners installed, election archived


@dataclass
class StateElectionConfig:
    """Configuration for state elections"""
    state_id: str
    state_name: str
    country: str
    total_population_estimate: int
    
    # Election thresholds (based on cities with full representation)
    initial_threshold_percent: float = 0.01    # 1% of cities to trigger first election
    expansion_threshold_percent: float = 0.50   # 50% of cities to trigger expansion election
    
    # Representation structure
    base_representatives: int = 2               # Minimum 2 representatives per state
    rep_per_population: int = 500000           # 1 additional rep per 500k population
    base_senators: int = 2                     # Always 2 senators per state
    
    # Term limits and rules (same as city level)
    term_length_years: int = 1                 # 1 year terms
    max_consecutive_terms: int = 4             # Max 4 terms
    consecutive_term_restriction: bool = True   # Cannot be consecutive
    
    # Election timing
    campaign_period_days: int = 45             # 45-day campaign period (longer than city)
    voting_period_days: int = 10               # 10-day electoral college voting period
    
    def calculate_total_representatives(self) -> int:
        """Calculate total representatives based on state population"""
        base_reps = self.base_representatives  # Always at least 2
        
        if self.total_population_estimate > 0:
            # Additional reps for population (1 per 500k)
            additional_reps = self.total_population_estimate // self.rep_per_population
            return max(base_reps, base_reps + additional_reps)
        
        return base_reps
    
    def calculate_total_senators(self) -> int:
        """Calculate total senators (always 2 for all states)"""
        return self.base_senators  # Always 2 senators
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StateCandidate:
    """Candidate for contract-based state governance office"""
    candidate_id: str
    user_email: str
    office: StateOffice
    state_id: str
    
    # Eligibility requirements
    current_city_office: Optional[str] = None   # Currently serving city representative/senator
    previous_city_offices: Optional[List[Dict[str, Any]]] = None  # History of city offices held
    eligibility_verified: bool = False
    
    # Campaign information  
    platform_statement: str = ""
    campaign_slogan: str = ""
    endorsements: Optional[List[str]] = None
    
    # Electoral college support
    city_endorsements: Optional[Dict[str, str]] = None    # city_id -> endorsement_type
    electoral_votes_received: int = 0
    vote_percentage: float = 0.0
    
    # Term limit compliance
    term_limit_compliance: bool = False
    previous_terms: Optional[List[Dict[str, Any]]] = None
    currently_serving: bool = False
    
    def __post_init__(self):
        if self.endorsements is None:
            self.endorsements = []
        if self.previous_city_offices is None:
            self.previous_city_offices = []
        if self.city_endorsements is None:
            self.city_endorsements = {}
        if self.previous_terms is None:
            self.previous_terms = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StateElection:
    """State contract election instance with electoral college process"""
    election_id: str
    state_id: str
    election_type: StateElectionTrigger
    offices_contested: List[StateOffice]
    
    # Election timeline
    scheduled_date: str
    campaign_start: str
    voting_start: str
    voting_end: str
    
    # Electoral college details
    eligible_cities: Optional[List[str]] = None           # Cities that can vote in electoral college
    city_electoral_votes: Optional[Dict[str, int]] = None # city_id -> number of electoral votes
    total_electoral_votes: int = 0
    
    # Candidates and results
    candidates: Optional[List[str]] = None                # Candidate IDs
    electoral_results: Optional[Dict[str, Dict[str, int]]] = None  # office -> {candidate_id: electoral_votes}
    winners: Optional[Dict[str, str]] = None              # office -> candidate_id
    
    # Election metadata
    status: StateElectionStatus = StateElectionStatus.ELECTION_SCHEDULED
    cities_with_representation_at_trigger: int = 0
    total_cities_in_state: int = 0
    trigger_threshold_met: float = 0.0
    
    # Audit trail
    blockchain_records: Optional[List[str]] = None        # Page IDs of blockchain records
    
    def __post_init__(self):
        if self.eligible_cities is None:
            self.eligible_cities = []
        if self.city_electoral_votes is None:
            self.city_electoral_votes = {}
        if self.candidates is None:
            self.candidates = []
        if self.electoral_results is None:
            self.electoral_results = {}
        if self.winners is None:
            self.winners = {}
        if self.blockchain_records is None:
            self.blockchain_records = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StateElectionManager:
    """Manager for state-level contract governance elections with electoral college system"""
    
    def __init__(self, config_path: str = None):
        """Initialize state election manager"""
        
        # Set up database paths
        base_path = Path(config_path) if config_path else Path("governance")
        base_path.mkdir(exist_ok=True)
        
        self.states_db_path = base_path / "states_db.json"
        self.state_elections_db_path = base_path / "state_elections_db.json"
        self.state_candidates_db_path = base_path / "state_candidates_db.json"
        
        # Initialize external systems
        self.blockchain = CivicBlockchain() if BLOCKCHAIN_AVAILABLE else None
        self.user_backend = UserBackend() if USER_BACKEND_AVAILABLE else None
        self.task_manager = TaskManager() if TASKS_AVAILABLE else None
        self.city_election_manager = CityElectionManager() if CITY_ELECTIONS_AVAILABLE else None
        
        # Initialize databases
        self._initialize_databases()
    
    def _initialize_databases(self):
        """Create database files if they don't exist"""
        
        # Initialize states database
        if not self.states_db_path.exists():
            initial_states = {
                "states": {},
                "city_tracking": {},  # Track which cities have representation
                "population_tracking": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_json(self.states_db_path, initial_states)
        
        # Initialize elections database
        if not self.state_elections_db_path.exists():
            initial_elections = {
                "scheduled_elections": {},
                "active_elections": {},
                "completed_elections": {},
                "electoral_college_results": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_json(self.state_elections_db_path, initial_elections)
        
        # Initialize candidates database
        if not self.state_candidates_db_path.exists():
            initial_candidates = {
                "candidates": {},
                "eligibility_records": {},
                "endorsement_tracking": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_json(self.state_candidates_db_path, initial_candidates)
    
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
    
    def register_state(self, state_name: str, country: str, 
                      total_population_estimate: int, **kwargs) -> Tuple[bool, str, str]:
        """Register a new state in the electoral system"""
        
        try:
            state_id = str(uuid.uuid4())
            
            # Create state configuration
            state_config = StateElectionConfig(
                state_id=state_id,
                state_name=state_name,
                country=country,
                total_population_estimate=total_population_estimate,
                **kwargs
            )
            
            # Save to database
            states_db = self._load_json(self.states_db_path)
            states_db['states'][state_id] = state_config.to_dict()
            
            # Initialize city tracking
            states_db['city_tracking'][state_id] = {
                "cities_with_full_representation": [],
                "total_cities_registered": 0,
                "last_threshold_check": datetime.now().isoformat()
            }
            
            # Initialize population tracking
            states_db['population_tracking'][state_id] = {
                "total_population": total_population_estimate,
                "last_census_update": datetime.now().isoformat(),
                "population_history": []
            }
            
            self._save_json(self.states_db_path, states_db)
            
            # Record on blockchain
            if self.blockchain:
                success, message, page_id = self.blockchain.add_page(
                    action_type="state_registered",
                    user_email="system",
                    data={
                        'state_id': state_id,
                        'state_name': state_name,
                        'country': country,
                        'total_population': total_population_estimate,
                        'calculated_representatives': state_config.calculate_total_representatives(),
                        'calculated_senators': state_config.calculate_total_senators(),
                        'registration_timestamp': datetime.now().isoformat()
                    }
                )
            
            return True, f"State '{state_name}' registered successfully", state_id
            
        except Exception as e:
            return False, f"Error registering state: {e}", ""
    
    def check_election_triggers(self, state_id: str) -> bool:
        """Check if state election should be triggered based on city representation"""
        
        try:
            states_db = self._load_json(self.states_db_path)
            state_config = states_db['states'].get(state_id, {})
            
            if not state_config:
                return False
            
            # Get current city representation status
            city_tracking = states_db['city_tracking'].get(state_id, {})
            cities_with_representation = len(city_tracking.get('cities_with_full_representation', []))
            total_cities = city_tracking.get('total_cities_registered', 0)
            
            if total_cities == 0:
                return False  # No cities registered yet
            
            representation_percentage = cities_with_representation / total_cities
            
            # Check for initial threshold (1%)
            if representation_percentage >= state_config.get('initial_threshold_percent', 0.01):
                if not self._has_active_or_scheduled_election(state_id):
                    # Check if this is first election or expansion
                    existing_officials = self._count_current_state_officials(state_id)
                    
                    if existing_officials['representatives'] == 0 and existing_officials['senators'] == 0:
                        # Trigger initial election
                        return self._schedule_initial_state_election(state_id, state_config)
                    elif representation_percentage >= state_config.get('expansion_threshold_percent', 0.50):
                        # Trigger expansion election if needed
                        return self._schedule_expansion_state_election(state_id, state_config)
            
            return False
            
        except Exception as e:
            print(f"Error checking election triggers: {e}")
            return False
    
    def _has_active_or_scheduled_election(self, state_id: str) -> bool:
        """Check if state already has an active or scheduled election"""
        
        elections_db = self._load_json(self.state_elections_db_path)
        
        # Check scheduled elections
        for election in elections_db.get('scheduled_elections', {}).values():
            if election.get('state_id') == state_id:
                return True
        
        # Check active elections
        for election in elections_db.get('active_elections', {}).values():
            if election.get('state_id') == state_id:
                return True
        
        return False
    
    def _count_current_state_officials(self, state_id: str) -> Dict[str, int]:
        """Count currently serving state officials"""
        
        candidates_db = self._load_json(self.state_candidates_db_path)
        
        count = {
            'representatives': 0,
            'senators': 0
        }
        
        for candidate in candidates_db.get('candidates', {}).values():
            if (candidate.get('state_id') == state_id and 
                candidate.get('currently_serving', False)):
                
                if candidate.get('office') == StateOffice.STATE_REPRESENTATIVE.value:
                    count['representatives'] += 1
                elif candidate.get('office') == StateOffice.STATE_SENATOR.value:
                    count['senators'] += 1
        
        return count
    
    def _schedule_initial_state_election(self, state_id: str, state_config: Dict[str, Any]) -> bool:
        """Schedule initial state election for all positions"""
        
        try:
            # Calculate election dates
            now = datetime.now()
            campaign_start = now + timedelta(days=21)  # 3 weeks to organize
            voting_start = campaign_start + timedelta(days=state_config['campaign_period_days'])
            voting_end = voting_start + timedelta(days=state_config['voting_period_days'])
            
            # Calculate required offices based on representation structure
            config_obj = StateElectionConfig(**state_config)
            total_representatives = config_obj.calculate_total_representatives()
            total_senators = config_obj.calculate_total_senators()
            
            # Create list of offices to contest (proper list construction)
            offices_contested: List[StateOffice] = []
            # Add all representative positions
            for _ in range(total_representatives):
                offices_contested.append(StateOffice.STATE_REPRESENTATIVE)
            # Add all senator positions (always 2)
            for _ in range(total_senators):
                offices_contested.append(StateOffice.STATE_SENATOR)
            
            # Get electoral college composition
            eligible_cities, city_electoral_votes, total_electoral_votes = self._calculate_electoral_college(state_id)
            
            # Create election
            election = StateElection(
                election_id=str(uuid.uuid4()),
                state_id=state_id,
                election_type=StateElectionTrigger.INITIAL_THRESHOLD,
                offices_contested=offices_contested,
                scheduled_date=voting_start.isoformat(),
                campaign_start=campaign_start.isoformat(),
                voting_start=voting_start.isoformat(),
                voting_end=voting_end.isoformat(),
                eligible_cities=eligible_cities,
                city_electoral_votes=city_electoral_votes,
                total_electoral_votes=total_electoral_votes,
                candidates=[],
                status=StateElectionStatus.ELECTION_SCHEDULED,
                cities_with_representation_at_trigger=len(eligible_cities),
                total_cities_in_state=self._get_total_cities_in_state(state_id),
                trigger_threshold_met=state_config['initial_threshold_percent']
            )
            
            # Save election
            elections_db = self._load_json(self.state_elections_db_path)
            elections_db['scheduled_elections'][election.election_id] = election.to_dict()
            self._save_json(self.state_elections_db_path, elections_db)
            
            # Record on blockchain
            if self.blockchain:
                success, message, page_id = self.blockchain.add_page(
                    action_type="state_initial_election_scheduled",
                    user_email="system",
                    data={
                        'election_id': election.election_id,
                        'state_id': state_id,
                        'election_type': 'initial_threshold_election',
                        'offices_contested': [office.value for office in offices_contested],
                        'total_representatives': total_representatives,
                        'total_senators': total_senators,
                        'eligible_cities': len(eligible_cities),
                        'total_electoral_votes': total_electoral_votes,
                        'campaign_start': election.campaign_start,
                        'voting_period': f"{election.voting_start} to {election.voting_end}",
                        'trigger_reason': 'reached_1_percent_cities_with_representation'
                    }
                )
                if success and page_id:
                    election.blockchain_records.append(page_id)
            
            # Notify eligible city officials about upcoming election
            self._notify_initial_state_election(state_id, state_config, election.election_id, 
                                              campaign_start, voting_start, voting_end)
            
            return True
            
        except Exception as e:
            print(f"Error scheduling initial state election: {e}")
            return False
    
    def _schedule_expansion_state_election(self, state_id: str, state_config: Dict[str, Any]) -> bool:
        """Schedule expansion election for additional positions due to population growth"""
        
        try:
            # Calculate election dates
            now = datetime.now()
            campaign_start = now + timedelta(days=21)  # 3 weeks to organize
            voting_start = campaign_start + timedelta(days=state_config['campaign_period_days'])
            voting_end = voting_start + timedelta(days=state_config['voting_period_days'])
            
            # Calculate required representation based on current population
            config_obj = StateElectionConfig(**state_config)
            required_representatives = config_obj.calculate_total_representatives()
            required_senators = config_obj.calculate_total_senators()
            
            # Check current office holders
            current_officials = self._count_current_state_officials(state_id)
            current_reps = current_officials['representatives']
            current_sens = current_officials['senators']
            
            # Determine additional offices needed
            offices_contested: List[StateOffice] = []
            
            # Add additional representative positions if needed
            if current_reps < required_representatives:
                additional_reps = required_representatives - current_reps
                for _ in range(additional_reps):
                    offices_contested.append(StateOffice.STATE_REPRESENTATIVE)
            
            # Senators should always be 2, but check anyway
            if current_sens < required_senators:
                additional_sens = required_senators - current_sens
                for _ in range(additional_sens):
                    offices_contested.append(StateOffice.STATE_SENATOR)
            
            if not offices_contested:
                return False  # No additional positions needed
            
            # Get electoral college composition
            eligible_cities, city_electoral_votes, total_electoral_votes = self._calculate_electoral_college(state_id)
            
            # Create expansion election
            election = StateElection(
                election_id=str(uuid.uuid4()),
                state_id=state_id,
                election_type=StateElectionTrigger.EXPANSION_THRESHOLD,
                offices_contested=offices_contested,
                scheduled_date=voting_start.isoformat(),
                campaign_start=campaign_start.isoformat(),
                voting_start=voting_start.isoformat(),
                voting_end=voting_end.isoformat(),
                eligible_cities=eligible_cities,
                city_electoral_votes=city_electoral_votes,
                total_electoral_votes=total_electoral_votes,
                candidates=[],
                status=StateElectionStatus.ELECTION_SCHEDULED,
                cities_with_representation_at_trigger=len(eligible_cities),
                total_cities_in_state=self._get_total_cities_in_state(state_id),
                trigger_threshold_met=state_config['expansion_threshold_percent']
            )
            
            # Save election
            elections_db = self._load_json(self.state_elections_db_path)
            elections_db['scheduled_elections'][election.election_id] = election.to_dict()
            self._save_json(self.state_elections_db_path, elections_db)
            
            # Record on blockchain
            if self.blockchain:
                success, message, page_id = self.blockchain.add_page(
                    action_type="state_expansion_election_scheduled",
                    user_email="system",
                    data={
                        'election_id': election.election_id,
                        'state_id': state_id,
                        'election_type': 'population_based_expansion',
                        'additional_offices': [office.value for office in offices_contested],
                        'total_required_reps': required_representatives,
                        'total_required_sens': required_senators,
                        'eligible_cities': len(eligible_cities),
                        'total_electoral_votes': total_electoral_votes,
                        'campaign_start': election.campaign_start,
                        'voting_period': f"{election.voting_start} to {election.voting_end}",
                        'trigger_reason': 'population_growth_requires_additional_representation'
                    }
                )
                if success and page_id:
                    election.blockchain_records.append(page_id)
            
            return True
            
        except Exception as e:
            print(f"Error scheduling expansion state election: {e}")
            return False
    
    def _calculate_electoral_college(self, state_id: str) -> Tuple[List[str], Dict[str, int], int]:
        """Calculate electoral college composition based on cities with representation"""
        
        try:
            states_db = self._load_json(self.states_db_path)
            city_tracking = states_db['city_tracking'].get(state_id, {})
            
            eligible_cities = city_tracking.get('cities_with_full_representation', [])
            city_electoral_votes = {}
            total_electoral_votes = 0
            
            # Each city with full representation gets electoral votes
            # For now, each city gets 1 electoral vote (can be enhanced later based on population)
            for city_id in eligible_cities:
                city_electoral_votes[city_id] = 1
                total_electoral_votes += 1
            
            return eligible_cities, city_electoral_votes, total_electoral_votes
            
        except Exception as e:
            print(f"Error calculating electoral college: {e}")
            return [], {}, 0
    
    def _get_total_cities_in_state(self, state_id: str) -> int:
        """Get total number of cities registered in the state"""
        
        states_db = self._load_json(self.states_db_path)
        city_tracking = states_db['city_tracking'].get(state_id, {})
        return city_tracking.get('total_cities_registered', 0)
    
    def _notify_initial_state_election(self, state_id: str, state_config: Dict[str, Any], 
                                      election_id: str, campaign_start: datetime, 
                                      voting_start: datetime, voting_end: datetime):
        """Notify eligible candidates about initial state election"""
        
        if not self.task_manager or not TaskType:
            return
        
        try:
            # Get all current city officials in the state who are eligible to run
            eligible_candidates = self._get_eligible_state_candidates(state_id)
            
            for candidate_email in eligible_candidates:
                if TaskType:
                    self.task_manager.create_task(
                        task_type=TaskType.ELECTION_PARTICIPATION,
                        assigned_to=candidate_email,
                        task_data={
                            'title': f"State Election Opportunity - {state_config['state_name']}",
                            'description': f"Your state {state_config['state_name']} has reached the threshold for state elections. "
                                        f"As a current or former city official, you are eligible to run for state representative or senator. "
                                        f"Electoral college voting by cities will determine winners.",
                            'election_id': election_id,
                            'state_id': state_id,
                            'election_type': 'initial_threshold',
                            'voting_start': voting_start.isoformat(),
                            'voting_end': voting_end.isoformat(),
                            'due_date': campaign_start.isoformat()
                        }
                    )
        except Exception as e:
            print(f"Error notifying initial state election: {e}")
    
    def _get_eligible_state_candidates(self, state_id: str) -> List[str]:
        """Get list of users eligible to run for state office (current/former city officials)"""
        
        if not self.city_election_manager:
            return []
        
        try:
            eligible_candidates = []
            
            # Get all city officials in the state
            # This would need to be implemented in city_election_manager
            # For now, return empty list as placeholder
            
            return eligible_candidates
            
        except Exception as e:
            print(f"Error getting eligible state candidates: {e}")
            return []
    
    def register_state_candidate(self, candidate_email: str, office: StateOffice, 
                               state_id: str, platform_statement: str = "", 
                               campaign_slogan: str = "") -> Tuple[bool, str, str]:
        """Register candidate for state office with eligibility verification"""
        
        try:
            # Verify user exists and has required city office experience
            if self.user_backend:
                user = self.user_backend.get_user_by_email(candidate_email)
                if not user:
                    return False, "User not found", ""
            
            # Check eligibility (must be or have been city representative/senator)
            is_eligible, eligibility_message = self._verify_state_candidate_eligibility(candidate_email, state_id)
            if not is_eligible:
                return False, f"Eligibility check failed: {eligibility_message}", ""
            
            # Check if already registered for this election
            if self._is_already_registered_for_state_election(candidate_email, state_id, office):
                return False, "Already registered for this election", ""
            
            # Create candidate record
            candidate_id = str(uuid.uuid4())
            
            # Get city office history
            current_city_office, previous_city_offices = self._get_city_office_history(candidate_email, state_id)
            
            candidate = StateCandidate(
                candidate_id=candidate_id,
                user_email=candidate_email,
                office=office,
                state_id=state_id,
                current_city_office=current_city_office,
                previous_city_offices=previous_city_offices,
                eligibility_verified=True,
                platform_statement=platform_statement,
                campaign_slogan=campaign_slogan,
                term_limit_compliance=True  # Will be verified separately
            )
            
            # Save candidate
            candidates_db = self._load_json(self.state_candidates_db_path)
            candidates_db['candidates'][candidate_id] = candidate.to_dict()
            self._save_json(self.state_candidates_db_path, candidates_db)
            
            # Record on blockchain
            if self.blockchain:
                success, message, page_id = self.blockchain.add_page(
                    action_type="state_candidate_registered",
                    user_email=candidate_email,
                    data={
                        'candidate_id': candidate_id,
                        'state_id': state_id,
                        'office': office.value,
                        'platform_statement': platform_statement,
                        'city_office_history': {
                            'current': current_city_office,
                            'previous': previous_city_offices
                        },
                        'registration_timestamp': datetime.now().isoformat()
                    }
                )
                if success and page_id:
                    candidate.blockchain_records.append(page_id)
            
            # Notify candidate of successful registration
            if self.task_manager and TaskType:
                self.task_manager.create_task(
                    task_type=TaskType.ELECTION_PARTICIPATION,
                    assigned_to=candidate_email,
                    task_data={
                        'title': f"State Campaign Registration - {office.value.replace('_', ' ').title()}",
                        'description': f"You are successfully registered as a candidate for {office.value.replace('_', ' ').title()} in your state. "
                                    f"Campaign period is active. Work to gain city endorsements for electoral college votes!",
                        'candidate_id': candidate_id,
                        'state_id': state_id,
                        'office': office.value,
                        'campaign_type': 'electoral_college',
                        'due_date': datetime.now().isoformat()
                    }
                )
            
            return True, f"Successfully registered as candidate for {office.value}", candidate_id
            
        except Exception as e:
            return False, f"Error registering state candidate: {e}", ""
    
    def _verify_state_candidate_eligibility(self, candidate_email: str, state_id: str) -> Tuple[bool, str]:
        """Verify candidate meets eligibility requirements for state office"""
        
        try:
            # Must be or have been a city representative or senator in this state
            current_city_office, previous_city_offices = self._get_city_office_history(candidate_email, state_id)
            
            if current_city_office:
                return True, f"Currently serving as {current_city_office}"
            
            if previous_city_offices:
                office_list = [office['office'] for office in previous_city_offices]
                return True, f"Previously served as: {', '.join(office_list)}"
            
            return False, "Must be or have been a city representative or senator in this state"
            
        except Exception as e:
            return False, f"Error verifying eligibility: {e}"
    
    def _get_city_office_history(self, candidate_email: str, state_id: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Get candidate's city office history in this state"""
        
        # This would integrate with city_election_manager to get actual data
        # For now, return placeholder data
        return None, []
    
    def _is_already_registered_for_state_election(self, candidate_email: str, state_id: str, office: StateOffice) -> bool:
        """Check if candidate is already registered for current state election"""
        
        try:
            candidates_db = self._load_json(self.state_candidates_db_path)
            
            for candidate in candidates_db.get('candidates', {}).values():
                if (candidate.get('user_email') == candidate_email and 
                    candidate.get('state_id') == state_id and
                    candidate.get('office') == office.value and
                    not candidate.get('election_completed', False)):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking registration status: {e}")
            return False
    
    def update_city_representation_status(self, state_id: str, city_id: str, has_full_representation: bool):
        """Update tracking of which cities have full representation for electoral college"""
        
        try:
            states_db = self._load_json(self.states_db_path)
            
            if state_id not in states_db['city_tracking']:
                states_db['city_tracking'][state_id] = {
                    "cities_with_full_representation": [],
                    "total_cities_registered": 0,
                    "last_threshold_check": datetime.now().isoformat()
                }
            
            city_tracking = states_db['city_tracking'][state_id]
            cities_with_rep = city_tracking['cities_with_full_representation']
            
            if has_full_representation and city_id not in cities_with_rep:
                cities_with_rep.append(city_id)
            elif not has_full_representation and city_id in cities_with_rep:
                cities_with_rep.remove(city_id)
            
            # Update total cities count
            city_tracking['total_cities_registered'] = len(set(cities_with_rep + [city_id]))
            city_tracking['last_threshold_check'] = datetime.now().isoformat()
            
            self._save_json(self.states_db_path, states_db)
            
            # Check if this change triggers a state election
            self.check_election_triggers(state_id)
            
        except Exception as e:
            print(f"Error updating city representation status: {e}")