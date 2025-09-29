"""
CITY/TOWN CONTRACT ELECTION SYSTEM - Contract-based municipal governance
Handles contract representative and senator elections for platform governance with population-based triggers
Format: "Contract Senator/Representative for [City Name], [State Name]"
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib

# Import blockchain for recording elections
try:
    from civic_desktop.blockchain.blockchain import CivicBlockchain
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    print("Warning: Blockchain not available for city elections")
    BLOCKCHAIN_AVAILABLE = False

# Import blockchain term limit verification
try:
    from civic_desktop.blockchain.term_limit_verification import (
        BlockchainTermLimitManager, TermLimitLevel, TermLimitOffice
    )
    TERM_LIMIT_VERIFICATION_AVAILABLE = True
except ImportError:
    print("Warning: Blockchain term limit verification not available")
    TERM_LIMIT_VERIFICATION_AVAILABLE = False

# Import task system components
try:
    from civic_desktop.tasks.task_types import TaskType
except ImportError:
    TaskType = None

# Import user management
try:
    from users.backend import UserBackend
    USER_BACKEND_AVAILABLE = True
except ImportError:
    print("Warning: User backend not available for city elections")
    USER_BACKEND_AVAILABLE = False

# Import task system for election notifications
try:
    from tasks.task_manager import TaskManager
    from tasks.task_types import TaskType
    TASKS_AVAILABLE = True
except ImportError:
    print("Warning: Task system not available for city elections")
    TASKS_AVAILABLE = False


class CityElectionStatus(Enum):
    """Status of city elections"""
    PENDING_THRESHOLD = "pending_threshold"      # Waiting for 1% population
    ELIGIBLE_FOR_ELECTION = "eligible_for_election"  # 1% reached, can hold election
    ELECTION_SCHEDULED = "election_scheduled"    # Election scheduled
    VOTING_ACTIVE = "voting_active"             # Currently accepting votes
    COUNTING_VOTES = "counting_votes"           # Tabulating results
    ELECTION_COMPLETE = "election_complete"     # Results certified
    AWAITING_EXPANSION = "awaiting_expansion"   # Waiting for 50% trigger


class CityElectionTrigger(Enum):
    """Election trigger conditions"""
    INITIAL_THRESHOLD = "initial_1_percent"     # 1% of city population
    EXPANSION_THRESHOLD = "expansion_50_percent" # 50% of city population
    TERM_EXPIRATION = "term_expiration"         # End of 1-year term
    RECALL_ELECTION = "recall_election"         # Citizen-initiated recall
    VACANCY_ELECTION = "vacancy_election"       # Fill vacant position


class CityOffice(Enum):
    """Contract-based city/town governance offices"""
    CITY_REPRESENTATIVE = "contract_representative"
    CITY_SENATOR = "contract_senator"
    TOWN_REPRESENTATIVE = "contract_representative"  # Same as city but for towns
    TOWN_SENATOR = "contract_senator"


@dataclass
class CityElectionConfig:
    """Configuration for city/town elections"""
    city_id: str
    city_name: str
    state: str
    country: str
    population_estimate: int
    
    # Election thresholds
    initial_threshold_percent: float = 0.01    # 1% to trigger first election
    expansion_threshold_percent: float = 0.50   # 50% to trigger expansion election
    
    # Term limits and rules
    term_length_years: int = 1                 # 1 year terms
    max_total_terms: int = 4                   # Max 4 terms total (not consecutive)
    consecutive_term_restriction: bool = True   # Cannot be consecutive
    
    # Office configuration - New representation structure
    base_representatives: int = 2             # Every city gets 2 representatives
    base_senators: int = 2                   # Every city gets 2 senators
    large_city_threshold: int = 200000       # Population threshold for additional reps
    additional_rep_per_population: int = 100000  # 1 additional rep per 100k above 200k
    
    # Election timing
    campaign_period_days: int = 30            # 30-day campaign period
    voting_period_days: int = 7               # 7-day voting period
    
    def calculate_total_representatives(self) -> int:
        """Calculate total representatives based on population"""
        base_reps = self.base_representatives  # Always 2
        
        if self.population_estimate > self.large_city_threshold:
            # Additional reps for population over 200k
            excess_population = self.population_estimate - self.large_city_threshold
            additional_reps = excess_population // self.additional_rep_per_population
            return base_reps + additional_reps
        
        return base_reps
    
    def calculate_total_senators(self) -> int:
        """Calculate total senators (always 2 for all cities)"""
        return self.base_senators  # Always 2 senators
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CityCandidate:
    """Candidate for city/town office"""
    candidate_id: str
    user_email: str
    office: CityOffice
    city_id: str
    
    # Campaign information
    platform_statement: str
    campaign_slogan: str
    endorsements: List[str]
    
    # Eligibility verification
    residency_verified: bool = False
    term_limit_compliance: bool = False
    previous_terms: List[Dict[str, Any]]
    
    # Campaign metrics
    votes_received: int = 0
    vote_percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_formatted_title(self, city_name: str, state_name: str) -> str:
        """Get properly formatted contract role title"""
        if self.office == CityOffice.CITY_REPRESENTATIVE:
            return f"Contract Representative for {city_name}, {state_name}"
        elif self.office == CityOffice.CITY_SENATOR:
            return f"Contract Senator for {city_name}, {state_name}"
        else:
            return f"Contract {self.office.value.replace('contract_', '').replace('_', ' ').title()} for {city_name}, {state_name}"


@dataclass
class CityElection:
    """City/town election instance"""
    election_id: str
    city_id: str
    election_type: CityElectionTrigger
    offices_contested: List[CityOffice]
    
    # Election timeline
    scheduled_date: str
    campaign_start: str
    voting_start: str
    voting_end: str
    
    # Election details
    eligible_voters: List[str]  # User emails of eligible voters
    candidates: List[CityCandidate]
    status: CityElectionStatus
    
    # Population tracking
    member_population_at_trigger: int
    total_population_estimate: int
    trigger_threshold_met: float
    
    # Results
    results: Dict[str, Any]
    winners: Dict[str, str]  # office -> winner_email
    voter_turnout: float = 0.0
    
    # Blockchain integration
    blockchain_records: List[str]  # Page IDs of blockchain records
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['candidates'] = [c.to_dict() for c in self.candidates]
        return result


class CityElectionManager:
    """Manages city/town elections with population-based triggers"""
    
    def __init__(self, config_path: str = None):
        """Initialize city election manager"""
        
        # Set up paths
        if config_path:
            self.config = self._load_config(config_path)
            self.cities_db_path = Path(self.config.get('cities_db_path', 'governance/cities_db.json'))
            self.elections_db_path = Path(self.config.get('city_elections_db_path', 'governance/city_elections_db.json'))
            self.candidates_db_path = Path(self.config.get('city_candidates_db_path', 'governance/city_candidates_db.json'))
        else:
            self.cities_db_path = Path('governance/cities_db.json')
            self.elections_db_path = Path('governance/city_elections_db.json')
            self.candidates_db_path = Path('governance/city_candidates_db.json')
        
        # Ensure directories exist
        for db_path in [self.cities_db_path, self.elections_db_path, self.candidates_db_path]:
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize systems
        self.blockchain = CivicBlockchain() if BLOCKCHAIN_AVAILABLE else None
        self.user_backend = UserBackend() if USER_BACKEND_AVAILABLE else None
        self.task_manager = TaskManager() if TASKS_AVAILABLE else None
        self.term_limit_manager = BlockchainTermLimitManager() if TERM_LIMIT_VERIFICATION_AVAILABLE else None
        
        # Initialize databases
        self._init_databases()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _init_databases(self):
        """Initialize election databases"""
        
        # Cities database
        if not self.cities_db_path.exists():
            initial_cities = {
                'cities': {},
                'population_tracking': {},
                'election_history': {},
                'created_at': datetime.now().isoformat()
            }
            self._save_json(self.cities_db_path, initial_cities)
        
        # Elections database
        if not self.elections_db_path.exists():
            initial_elections = {
                'active_elections': {},
                'scheduled_elections': {},
                'completed_elections': {},
                'election_statistics': {
                    'total_elections': 0,
                    'average_turnout': 0.0,
                    'cities_with_government': 0
                },
                'created_at': datetime.now().isoformat()
            }
            self._save_json(self.elections_db_path, initial_elections)
        
        # Candidates database
        if not self.candidates_db_path.exists():
            initial_candidates = {
                'candidates': {},
                'candidate_history': {},
                'term_tracking': {},
                'created_at': datetime.now().isoformat()
            }
            self._save_json(self.candidates_db_path, initial_candidates)
    
    def _save_json(self, path: Path, data: Dict[str, Any]):
        """Save data to JSON file"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to {path}: {e}")
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading from {path}: {e}")
            return {}
    
    def register_city(self, city_name: str, state: str, country: str, 
                     population_estimate: int, **kwargs) -> Tuple[bool, str, str]:
        """Register a new city/town for elections"""
        
        try:
            # Generate city ID
            city_id = f"{country}_{state}_{city_name}".lower().replace(' ', '_')
            city_id = hashlib.sha256(city_id.encode()).hexdigest()[:16]
            
            # Create city configuration
            city_config = CityElectionConfig(
                city_id=city_id,
                city_name=city_name,
                state=state,
                country=country,
                population_estimate=population_estimate,
                **kwargs
            )
            
            # Load cities database
            cities_db = self._load_json(self.cities_db_path)
            
            # Check if city already registered
            if city_id in cities_db.get('cities', {}):
                return False, f"City {city_name} already registered", city_id
            
            # Add city to database
            cities_db['cities'][city_id] = city_config.to_dict()
            cities_db['population_tracking'][city_id] = {
                'current_members': 0,
                'member_list': [],
                'population_history': [{
                    'date': datetime.now().isoformat(),
                    'member_count': 0,
                    'estimated_population': population_estimate
                }],
                'threshold_status': {
                    'initial_threshold_met': False,
                    'expansion_threshold_met': False,
                    'last_checked': datetime.now().isoformat()
                }
            }
            
            # Save database
            self._save_json(self.cities_db_path, cities_db)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="city_registered",
                    user_email="system",
                    data={
                        'city_id': city_id,
                        'city_name': city_name,
                        'state': state,
                        'country': country,
                        'population_estimate': population_estimate,
                        'initial_threshold': city_config.initial_threshold_percent,
                        'expansion_threshold': city_config.expansion_threshold_percent,
                        'registration_date': datetime.now().isoformat()
                    }
                )
            
            return True, f"City {city_name} registered successfully", city_id
            
        except Exception as e:
            return False, f"Error registering city: {e}", ""
    
    def add_city_member(self, user_email: str, city_id: str) -> Tuple[bool, str]:
        """Add a member to a city and check election thresholds"""
        
        try:
            # Load databases
            cities_db = self._load_json(self.cities_db_path)
            
            # Verify city exists
            if city_id not in cities_db.get('cities', {}):
                return False, f"City {city_id} not found"
            
            city_config = cities_db['cities'][city_id]
            population_data = cities_db['population_tracking'][city_id]
            
            # Check if user already a member
            if user_email in population_data['member_list']:
                return False, f"User {user_email} already a member of this city"
            
            # Add member
            population_data['member_list'].append(user_email)
            population_data['current_members'] += 1
            
            # Update population history
            population_data['population_history'].append({
                'date': datetime.now().isoformat(),
                'member_count': population_data['current_members'],
                'estimated_population': city_config['population_estimate'],
                'action': 'member_added',
                'user_email': user_email
            })
            
            # Check thresholds
            current_percentage = population_data['current_members'] / city_config['population_estimate']
            threshold_updates = []
            
            # Check 1% threshold (initial election trigger)
            if (not population_data['threshold_status']['initial_threshold_met'] and 
                current_percentage >= city_config['initial_threshold_percent']):
                
                population_data['threshold_status']['initial_threshold_met'] = True
                threshold_updates.append('initial_election_triggered')
                
                # Schedule initial election
                election_scheduled = self._schedule_initial_election(city_id, city_config)
                if election_scheduled:
                    threshold_updates.append('initial_election_scheduled')
            
            # Check 50% threshold (expansion trigger)
            if (not population_data['threshold_status']['expansion_threshold_met'] and 
                current_percentage >= city_config['expansion_threshold_percent']):
                
                population_data['threshold_status']['expansion_threshold_met'] = True
                threshold_updates.append('expansion_election_triggered')
                
                # Schedule expansion election
                election_scheduled = self._schedule_expansion_election(city_id, city_config)
                if election_scheduled:
                    threshold_updates.append('expansion_election_scheduled')
            
            # Update last checked
            population_data['threshold_status']['last_checked'] = datetime.now().isoformat()
            
            # Save database
            self._save_json(self.cities_db_path, cities_db)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="city_member_added",
                    user_email=user_email,
                    data={
                        'city_id': city_id,
                        'city_name': city_config['city_name'],
                        'new_member_count': population_data['current_members'],
                        'population_percentage': current_percentage,
                        'threshold_updates': threshold_updates,
                        'thresholds_met': {
                            'initial': population_data['threshold_status']['initial_threshold_met'],
                            'expansion': population_data['threshold_status']['expansion_threshold_met']
                        }
                    }
                )
            
            # Create tasks for threshold notifications
            if threshold_updates and self.task_manager:
                self._create_threshold_tasks(city_id, city_config, threshold_updates)
            
            message = f"Added member to {city_config['city_name']} ({population_data['current_members']} members, {current_percentage:.2%})"
            if threshold_updates:
                message += f". Triggered: {', '.join(threshold_updates)}"
            
            return True, message
            
        except Exception as e:
            return False, f"Error adding city member: {e}"
    
    def _schedule_initial_election(self, city_id: str, city_config: Dict[str, Any]) -> bool:
        """Schedule initial election for city/town"""
        
        try:
            # Calculate election dates
            now = datetime.now()
            campaign_start = now + timedelta(days=7)  # 7 days to organize
            voting_start = campaign_start + timedelta(days=city_config['campaign_period_days'])
            voting_end = voting_start + timedelta(days=city_config['voting_period_days'])
            
            # Calculate required offices based on new representation structure
            config_obj = CityElectionConfig(**city_config)
            total_representatives = config_obj.calculate_total_representatives()
            total_senators = config_obj.calculate_total_senators()
            
            # Create list of offices to contest (proper list construction)
            offices_contested: List[CityOffice] = []
            # Add all representative positions (2 base + additional based on population)
            for _ in range(total_representatives):
                offices_contested.append(CityOffice.CITY_REPRESENTATIVE)
            # Add all senator positions (always 2)
            for _ in range(total_senators):
                offices_contested.append(CityOffice.CITY_SENATOR)
            
            # Create election
            election = CityElection(
                election_id=str(uuid.uuid4()),
                city_id=city_id,
                election_type=CityElectionTrigger.INITIAL_THRESHOLD,
                offices_contested=offices_contested,
                scheduled_date=voting_start.isoformat(),
                campaign_start=campaign_start.isoformat(),
                voting_start=voting_start.isoformat(),
                voting_end=voting_end.isoformat(),
                eligible_voters=[],  # Will be populated from city members
                candidates=[],
                status=CityElectionStatus.ELECTION_SCHEDULED,
                member_population_at_trigger=0,  # Will be updated
                total_population_estimate=city_config['population_estimate'],
                trigger_threshold_met=city_config['initial_threshold_percent'],
                results={},
                winners={},
                blockchain_records=[]
            )
            
            # Save election
            elections_db = self._load_json(self.elections_db_path)
            elections_db['scheduled_elections'][election.election_id] = election.to_dict()
            elections_db['election_statistics']['total_elections'] += 1
            self._save_json(self.elections_db_path, elections_db)
            
            # Record on blockchain
            if self.blockchain:
                success, message, page_id = self.blockchain.add_page(
                    action_type="city_election_scheduled",
                    user_email="system",
                    data={
                        'election_id': election.election_id,
                        'city_id': city_id,
                        'election_type': 'initial_threshold_election',
                        'offices_contested': [office.value for office in election.offices_contested],
                        'campaign_start': election.campaign_start,
                        'voting_period': f"{election.voting_start} to {election.voting_end}",
                        'trigger_reason': 'reached_1_percent_population_threshold'
                    }
                )
                if success and page_id:
                    election.blockchain_records.append(page_id)
            
            return True
            
        except Exception as e:
            print(f"Error scheduling initial election: {e}")
            return False
    
    def _schedule_expansion_election(self, city_id: str, city_config: Dict[str, Any]) -> bool:
        """Schedule expansion election for population growth (representation update)"""
        
        try:
            # Calculate election dates
            now = datetime.now()
            campaign_start = now + timedelta(days=14)  # 14 days to organize expansion
            voting_start = campaign_start + timedelta(days=city_config['campaign_period_days'])
            voting_end = voting_start + timedelta(days=city_config['voting_period_days'])
            
            # Calculate required representation based on new population
            config_obj = CityElectionConfig(**city_config)
            required_representatives = config_obj.calculate_total_representatives()
            required_senators = config_obj.calculate_total_senators()
            
            # Check current office holders
            current_reps = self._count_current_office_holders(city_id, CityOffice.CITY_REPRESENTATIVE)
            current_sens = self._count_current_office_holders(city_id, CityOffice.CITY_SENATOR)
            
            # Determine additional offices needed
            offices_contested: List[CityOffice] = []
            
            # Add additional representative positions if needed
            if current_reps < required_representatives:
                additional_reps = required_representatives - current_reps
                for _ in range(additional_reps):
                    offices_contested.append(CityOffice.CITY_REPRESENTATIVE)
            
            # Senators should always be 2, but check anyway
            if current_sens < required_senators:
                additional_sens = required_senators - current_sens
                for _ in range(additional_sens):
                    offices_contested.append(CityOffice.CITY_SENATOR)
            
            if not offices_contested:
                return False  # No additional positions needed
            
            # Create expansion election
            election = CityElection(
                election_id=str(uuid.uuid4()),
                city_id=city_id,
                election_type=CityElectionTrigger.EXPANSION_THRESHOLD,
                offices_contested=offices_contested,
                scheduled_date=voting_start.isoformat(),
                campaign_start=campaign_start.isoformat(),
                voting_start=voting_start.isoformat(),
                voting_end=voting_end.isoformat(),
                eligible_voters=[],  # Will be populated from city members
                candidates=[],
                status=CityElectionStatus.ELECTION_SCHEDULED,
                member_population_at_trigger=0,  # Will be updated
                total_population_estimate=city_config['population_estimate'],
                trigger_threshold_met=city_config['expansion_threshold_percent'],
                results={},
                winners={},
                blockchain_records=[]
            )
            
            # Save election
            elections_db = self._load_json(self.elections_db_path)
            elections_db['scheduled_elections'][election.election_id] = election.to_dict()
            self._save_json(self.elections_db_path, elections_db)
            
            # Record on blockchain
            if self.blockchain:
                success, message, page_id = self.blockchain.add_page(
                    action_type="city_contract_expansion_election_scheduled",
                    user_email="system",
                    data={
                        'election_id': election.election_id,
                        'city_id': city_id,
                        'election_type': 'population_based_expansion',
                        'additional_offices': [office.value for office in offices_contested],
                        'total_required_reps': required_representatives,
                        'total_required_sens': required_senators,
                        'campaign_start': election.campaign_start,
                        'voting_period': f"{election.voting_start} to {election.voting_end}",
                        'trigger_reason': 'population_growth_requires_additional_representation'
                    }
                )
                if success and page_id:
                    election.blockchain_records.append(page_id)
            
            return True
            
        except Exception as e:
            print(f"Error scheduling expansion election: {e}")
            return False
    
    def _count_current_office_holders(self, city_id: str, office: CityOffice) -> int:
        """Count current office holders for a specific office"""
        
        try:
            # Load candidates database to check current office holders
            candidates_db = self._load_json(self.candidates_db_path)
            
            # Count active office holders
            count = 0
            for candidate_id, candidate_data in candidates_db.get('candidates', {}).items():
                if (candidate_data.get('city_id') == city_id and 
                    candidate_data.get('office') == office.value and
                    candidate_data.get('currently_serving', False)):
                    count += 1
            
            return count
            
        except Exception as e:
            print(f"Error counting office holders: {e}")
            return 0
    
    def _create_threshold_tasks(self, city_id: str, city_config: Dict[str, Any], 
                              threshold_updates: List[str]):
        """Create tasks to notify users about threshold triggers"""
        
        if not self.task_manager:
            return
        
        try:
            # Get city members for task assignment
            cities_db = self._load_json(self.cities_db_path)
            population_data = cities_db['population_tracking'].get(city_id, {})
            members = population_data.get('member_list', [])
            
            for update in threshold_updates:
                if 'initial_election' in update:
                    # Create tasks for initial election
                    for member_email in members:
                        self.task_manager.create_task(
                            assigned_to=member_email,
                            task_type=TaskType.ELECTION_PARTICIPATION,
                            title=f"Initial Election for {city_config['city_name']}",
                            description=f"Your city {city_config['city_name']} has reached 1% population threshold. "
                                      f"An election will be scheduled for City Representative and City Senator positions. "
                                      f"Consider running for office or participating in the democratic process.",
                            category='voting',
                            priority='high',
                            deadline_hours=168,  # 1 week to prepare
                            metadata={
                                'city_id': city_id,
                                'city_name': city_config['city_name'],
                                'election_type': 'initial_threshold',
                                'threshold_reached': '1_percent'
                            }
                        )
                
                elif 'expansion_election' in update:
                    # Create tasks for expansion election
                    for member_email in members:
                        self.task_manager.create_task(
                            assigned_to=member_email,
                            task_type=TaskType.ELECTION_PARTICIPATION,
                            title=f"Expansion Election for {city_config['city_name']}",
                            description=f"Your city {city_config['city_name']} has reached 50% population threshold. "
                                      f"An expansion election will be scheduled for additional Representative and Senator positions. "
                                      f"This is an opportunity to strengthen your local democratic representation.",
                            category='voting',
                            priority='high',
                            deadline_hours=336,  # 2 weeks to prepare
                            metadata={
                                'city_id': city_id,
                                'city_name': city_config['city_name'],
                                'election_type': 'expansion_threshold',
                                'threshold_reached': '50_percent'
                            }
                        )
        
        except Exception as e:
            print(f"Error creating threshold tasks: {e}")
    
    def register_candidate(self, user_email: str, city_id: str, office: CityOffice,
                          platform_statement: str, campaign_slogan: str = "") -> Tuple[bool, str, str]:
        """Register a candidate for city/town office"""
        
        try:
            # Validate eligibility
            eligible, eligibility_message = self._check_candidate_eligibility(user_email, city_id, office)
            if not eligible:
                return False, eligibility_message, ""
            
            # Create candidate
            candidate = CityCandidate(
                candidate_id=str(uuid.uuid4()),
                user_email=user_email,
                office=office,
                city_id=city_id,
                platform_statement=platform_statement,
                campaign_slogan=campaign_slogan,
                endorsements=[],
                residency_verified=True,  # Verified during eligibility check
                term_limit_compliance=True,  # Verified during eligibility check
                previous_terms=self._get_previous_terms(user_email, city_id, office)
            )
            
            # Save candidate
            candidates_db = self._load_json(self.candidates_db_path)
            candidates_db['candidates'][candidate.candidate_id] = candidate.to_dict()
            self._save_json(self.candidates_db_path, candidates_db)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="city_candidate_registered",
                    user_email=user_email,
                    data={
                        'candidate_id': candidate.candidate_id,
                        'city_id': city_id,
                        'office': office.value,
                        'platform_statement': platform_statement[:200],  # Truncate for blockchain
                        'registration_date': datetime.now().isoformat(),
                        'term_limit_compliance': True
                    }
                )
            
            # Create task for candidate
            if self.task_manager:
                self.task_manager.create_task(
                    assigned_to=user_email,
                    task_type=TaskType.ELECTION_PARTICIPATION,
                    title=f"Campaign for {office.value.replace('_', ' ').title()}",
                    description=f"You are registered as a candidate for {office.value.replace('_', ' ').title()} in your city. "
                              f"Begin your campaign and engage with voters.",
                    category='voting',
                    priority='high',
                    deadline_hours=720,  # 30 days campaign period
                    metadata={
                        'candidate_id': candidate.candidate_id,
                        'city_id': city_id,
                        'office': office.value,
                        'campaign_type': 'city_election'
                    }
                )
            
            return True, f"Successfully registered as candidate for {office.value}", candidate.candidate_id
            
        except Exception as e:
            return False, f"Error registering candidate: {e}", ""
    
    def _check_candidate_eligibility(self, user_email: str, city_id: str, 
                                   office: CityOffice) -> Tuple[bool, str]:
        """Check if user is eligible to be a candidate"""
        
        try:
            # Check if user is a city member
            cities_db = self._load_json(self.cities_db_path)
            population_data = cities_db['population_tracking'].get(city_id, {})
            
            if user_email not in population_data.get('member_list', []):
                return False, "Must be a city member to run for office"
            
            # Check term limits
            previous_terms = self._get_previous_terms(user_email, city_id, office)
            
            # Check if currently serving (cannot run for same office while serving)
            if self._is_currently_serving(user_email, city_id, office):
                return False, "Cannot run for office while currently serving in the same position"
            
            # Check consecutive term restriction
            if len(previous_terms) >= 4:  # Max 4 terms total
                return False, "Maximum term limit of 4 terms reached"
            
            # Check for consecutive terms restriction
            if previous_terms and self._has_consecutive_terms_issue(previous_terms):
                return False, "Cannot serve consecutive terms"
            
            # Check if user is contract member or higher
            if self.user_backend:
                user_data = self.user_backend.get_user(user_email)
                if not user_data:
                    return False, "User not found"
                
                user_role = user_data.get('role', '')
                if user_role not in ['contract_member', 'contract_representative', 'contract_senator', 
                                   'contract_elder', 'contract_founder']:
                    return False, "Must be at least a Contract Member to run for city office"
            
            return True, "Candidate is eligible"
            
        except Exception as e:
            return False, f"Error checking eligibility: {e}"
    
    def _get_previous_terms(self, user_email: str, city_id: str, office: CityOffice) -> List[Dict[str, Any]]:
        """Get previous terms served by user in specific city/office"""
        
        try:
            candidates_db = self._load_json(self.candidates_db_path)
            term_tracking = candidates_db.get('term_tracking', {})
            
            user_terms = term_tracking.get(user_email, {})
            city_terms = user_terms.get(city_id, {})
            office_terms = city_terms.get(office.value, [])
            
            return office_terms
            
        except Exception as e:
            print(f"Error getting previous terms: {e}")
            return []
    
    def _is_currently_serving(self, user_email: str, city_id: str, office: CityOffice) -> bool:
        """Check if user is currently serving in specified office"""
        
        try:
            candidates_db = self._load_json(self.candidates_db_path)
            
            for candidate_id, candidate_data in candidates_db.get('candidates', {}).items():
                if (candidate_data.get('user_email') == user_email and
                    candidate_data.get('city_id') == city_id and
                    candidate_data.get('office') == office.value and
                    candidate_data.get('currently_serving', False)):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking current service: {e}")
            return False
    
    def _has_consecutive_terms_issue(self, previous_terms: List[Dict[str, Any]]) -> bool:
        """Check if user has consecutive terms restriction issue
        
        Rule: Cannot serve consecutive terms - must have 1 year break between ANY terms
        """
        
        try:
            if not previous_terms:
                return False
            
            # Sort terms by end date (most recent first)
            sorted_terms = sorted(previous_terms, key=lambda x: x.get('end_date', ''), reverse=True)
            
            # Check if ANY previous term ended less than 1 year ago
            current_time = datetime.now()
            
            for term in sorted_terms:
                try:
                    term_end = datetime.fromisoformat(term['end_date'])
                    time_since_term_end = current_time - term_end
                    
                    # If any term ended less than 365 days ago, cannot run (consecutive restriction)
                    if time_since_term_end.days < 365:
                        return True
                        
                except (ValueError, KeyError) as date_error:
                    print(f"Error parsing term end date: {date_error}")
                    continue
            
            return False  # No consecutive terms issue found
            
        except Exception as e:
            print(f"Error checking consecutive terms: {e}")
            return True  # Err on side of caution - block if can't verify
    
    def get_city_statistics(self) -> Dict[str, Any]:
        """Get comprehensive city election statistics"""
        
        try:
            cities_db = self._load_json(self.cities_db_path)
            elections_db = self._load_json(self.elections_db_path)
            candidates_db = self._load_json(self.candidates_db_path)
            
            stats = {
                'total_cities_registered': len(cities_db.get('cities', {})),
                'cities_with_elections': 0,
                'cities_at_initial_threshold': 0,
                'cities_at_expansion_threshold': 0,
                'total_elections_held': len(elections_db.get('completed_elections', {})),
                'active_elections': len(elections_db.get('active_elections', {})),
                'scheduled_elections': len(elections_db.get('scheduled_elections', {})),
                'total_candidates': len(candidates_db.get('candidates', {})),
                'currently_serving_officials': 0,
                'average_voter_turnout': 0.0,
                'cities_by_status': {},
                'popular_offices': {},
                'term_completion_rate': 0.0
            }
            
            # Analyze cities
            for city_id, city_data in cities_db.get('cities', {}).items():
                population_data = cities_db['population_tracking'].get(city_id, {})
                threshold_status = population_data.get('threshold_status', {})
                
                if threshold_status.get('initial_threshold_met'):
                    stats['cities_at_initial_threshold'] += 1
                    stats['cities_with_elections'] += 1
                
                if threshold_status.get('expansion_threshold_met'):
                    stats['cities_at_expansion_threshold'] += 1
            
            # Calculate turnout average
            completed_elections = elections_db.get('completed_elections', {})
            if completed_elections:
                total_turnout = sum(election.get('voter_turnout', 0) 
                                  for election in completed_elections.values())
                stats['average_voter_turnout'] = total_turnout / len(completed_elections)
            
            # Count currently serving officials
            for candidate_data in candidates_db.get('candidates', {}).values():
                if candidate_data.get('currently_serving', False):
                    stats['currently_serving_officials'] += 1
                    
                    office = candidate_data.get('office', '')
                    if office in stats['popular_offices']:
                        stats['popular_offices'][office] += 1
                    else:
                        stats['popular_offices'][office] = 1
            
            return stats
            
        except Exception as e:
            print(f"Error generating statistics: {e}")
            return {}
    
    def get_city_info(self, city_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific city"""
        
        try:
            cities_db = self._load_json(self.cities_db_path)
            elections_db = self._load_json(self.elections_db_path)
            candidates_db = self._load_json(self.candidates_db_path)
            
            city_data = cities_db.get('cities', {}).get(city_id, {})
            if not city_data:
                return {}
            
            population_data = cities_db['population_tracking'].get(city_id, {})
            
            # Get elections for this city
            city_elections = []
            for election_db_name in ['active_elections', 'scheduled_elections', 'completed_elections']:
                for election in elections_db.get(election_db_name, {}).values():
                    if election.get('city_id') == city_id:
                        city_elections.append(election)
            
            # Get candidates for this city
            city_candidates = []
            for candidate in candidates_db.get('candidates', {}).values():
                if candidate.get('city_id') == city_id:
                    city_candidates.append(candidate)
            
            # Get current office holders
            current_officials = {}
            for candidate in city_candidates:
                if candidate.get('currently_serving', False):
                    office = candidate.get('office', '')
                    if office not in current_officials:
                        current_officials[office] = []
                    current_officials[office].append(candidate)
            
            return {
                'city_config': city_data,
                'population_data': population_data,
                'elections': city_elections,
                'candidates': city_candidates,
                'current_officials': current_officials,
                'election_eligibility': {
                    'initial_threshold_met': population_data.get('threshold_status', {}).get('initial_threshold_met', False),
                    'expansion_threshold_met': population_data.get('threshold_status', {}).get('expansion_threshold_met', False),
                    'current_percentage': (population_data.get('current_members', 0) / 
                                         city_data.get('population_estimate', 1)) if city_data.get('population_estimate', 0) > 0 else 0
                }
            }
            
        except Exception as e:
            print(f"Error getting city info: {e}")
            return {}


# Usage Example and Testing Functions
def test_city_election_system():
    """Test the city election system"""
    
    print("🏛️ Testing City/Town Election System")
    print("=" * 50)
    
    # Initialize manager
    manager = CityElectionManager()
    
    # Test 1: Register a city
    print("\n📍 Test 1: Registering Democracy City")
    success, message, city_id = manager.register_city(
        city_name="Democracy City",
        state="Liberty State", 
        country="Democratic Republic",
        population_estimate=10000
    )
    print(f"Registration: {'✅' if success else '❌'} {message}")
    if success:
        print(f"City ID: {city_id}")
    
    # Test 2: Add members until 1% threshold
    print(f"\n👥 Test 2: Adding members to reach 1% threshold (100 members)")
    threshold_reached = False
    for i in range(1, 105):  # Add 104 members to exceed 1%
        user_email = f"citizen_{i:03d}@democracycity.gov"
        success, message = manager.add_city_member(user_email, city_id)
        
        if i % 20 == 0:  # Progress update every 20 members
            print(f"   Added {i} members: {message[:80]}...")
        
        if "initial_election_triggered" in message:
            print(f"   🎯 THRESHOLD REACHED at {i} members!")
            threshold_reached = True
    
    # Test 3: Get city statistics
    print(f"\n📊 Test 3: City Statistics")
    stats = manager.get_city_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    # Test 4: Get detailed city info
    print(f"\n🏙️ Test 4: Detailed City Information")
    city_info = manager.get_city_info(city_id)
    if city_info:
        eligibility = city_info['election_eligibility']
        print(f"   Current Members: {city_info['population_data']['current_members']}")
        print(f"   Population Percentage: {eligibility['current_percentage']:.2%}")
        print(f"   Initial Threshold Met: {'✅' if eligibility['initial_threshold_met'] else '❌'}")
        print(f"   Expansion Threshold Met: {'✅' if eligibility['expansion_threshold_met'] else '❌'}")
    
    # Test 5: Register candidates
    print(f"\n🗳️ Test 5: Registering Candidates")
    test_candidates = [
        ("citizen_001@democracycity.gov", CityOffice.CITY_REPRESENTATIVE, "Transparent governance and community development"),
        ("citizen_002@democracycity.gov", CityOffice.CITY_SENATOR, "Deliberative decision-making and constitutional oversight"),
        ("citizen_003@democracycity.gov", CityOffice.CITY_REPRESENTATIVE, "Economic growth and infrastructure investment")
    ]
    
    for email, office, platform in test_candidates:
        success, message, candidate_id = manager.register_candidate(
            user_email=email,
            city_id=city_id,
            office=office,
            platform_statement=platform,
            campaign_slogan="Democracy in Action!"
        )
        print(f"   Candidate Registration: {'✅' if success else '❌'} {message}")
        if success:
            print(f"      Candidate ID: {candidate_id}")
    
    print("\n" + "=" * 50)
    print("🎉 City Election System Test Complete!")
    
    return manager, city_id


if __name__ == "__main__":
    # Run test
    test_city_election_system()