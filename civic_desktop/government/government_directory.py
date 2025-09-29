"""
COMPREHENSIVE GOVERNMENT OFFICIALS DIRECTORY SYSTEM
Complete database of world government leaders with contact information
Hierarchical verification: Founders → Country → State → City
Government officials SEPARATE from contract governance system
"""

import json
import csv
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Import existing systems
try:
    from civic_desktop.blockchain.blockchain import CivicBlockchain
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    print("Warning: Blockchain system not available for government directory")
    BLOCKCHAIN_AVAILABLE = False


class VerificationAuthority(Enum):
    """Hierarchical verification authority levels"""
    FOUNDER = "founder"                    # Founders verify country leaders
    COUNTRY_LEADER = "country_leader"      # Country leaders verify state leaders  
    STATE_LEADER = "state_leader"          # State leaders verify city leaders
    VERIFIED_OFFICIAL = "verified_official" # Already verified government official


class GovernmentOfficialType(Enum):
    """Types of government officials (separate from contract roles)"""
    # Country Level
    PRESIDENT = "president"
    PRIME_MINISTER = "prime_minister"
    CHANCELLOR = "chancellor"
    MONARCH = "monarch"
    VICE_PRESIDENT = "vice_president"
    DEPUTY_PM = "deputy_prime_minister"
    
    # State/Provincial Level
    GOVERNOR = "governor"
    PREMIER = "premier"
    LT_GOVERNOR = "lt_governor"
    STATE_MINISTER = "state_minister"
    
    # City/Municipal Level
    MAYOR = "mayor"
    DEPUTY_MAYOR = "deputy_mayor"
    CITY_MANAGER = "city_manager"
    LORD_MAYOR = "lord_mayor"


class VerificationStatus(Enum):
    """Government official verification status"""
    UNCONTACTED = "uncontacted"           # Not yet contacted
    CONTACTED = "contacted"               # Initial contact made
    INTERESTED = "interested"             # Expressed interest in joining
    DOCUMENTS_REQUESTED = "docs_requested" # Verification documents requested
    PENDING_VERIFICATION = "pending"      # Awaiting verification
    VERIFIED = "verified"                 # Fully verified government official
    REJECTED = "rejected"                 # Verification rejected
    INACTIVE = "inactive"                 # No longer in office


@dataclass
class GovernmentOfficial:
    """Complete government official information"""
    official_id: str
    name: str
    title: str
    official_type: GovernmentOfficialType
    jurisdiction: str                     # Country, State, or City name
    jurisdiction_level: str               # "country", "state", "city"
    
    # Contact Information
    email: Optional[str] = None
    phone: Optional[str] = None
    office_address: Optional[str] = None
    website: Optional[str] = None
    social_media: Dict[str, str] = None
    
    # Official Details
    party_affiliation: Optional[str] = None
    term_start: Optional[str] = None
    term_end: Optional[str] = None
    predecessor: Optional[str] = None
    
    # Platform Integration
    verification_status: VerificationStatus = VerificationStatus.UNCONTACTED
    platform_account_email: Optional[str] = None
    verified_by: Optional[str] = None
    verification_date: Optional[str] = None
    verification_notes: str = ""
    
    # Contact Tracking
    first_contacted: Optional[str] = None
    last_contact: Optional[str] = None
    contact_attempts: int = 0
    response_received: bool = False
    
    # Geographic Information
    country: str = ""
    state_province: Optional[str] = None
    population_served: Optional[int] = None
    
    def __post_init__(self):
        if self.social_media is None:
            self.social_media = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'official_id': self.official_id,
            'name': self.name,
            'title': self.title,
            'official_type': self.official_type.value,
            'jurisdiction': self.jurisdiction,
            'jurisdiction_level': self.jurisdiction_level,
            'email': self.email,
            'phone': self.phone,
            'office_address': self.office_address,
            'website': self.website,
            'social_media': self.social_media,
            'party_affiliation': self.party_affiliation,
            'term_start': self.term_start,
            'term_end': self.term_end,
            'predecessor': self.predecessor,
            'verification_status': self.verification_status.value,
            'platform_account_email': self.platform_account_email,
            'verified_by': self.verified_by,
            'verification_date': self.verification_date,
            'verification_notes': self.verification_notes,
            'first_contacted': self.first_contacted,
            'last_contact': self.last_contact,
            'contact_attempts': self.contact_attempts,
            'response_received': self.response_received,
            'country': self.country,
            'state_province': self.state_province,
            'population_served': self.population_served
        }


class GovernmentDirectoryManager:
    """Manages comprehensive government officials directory and outreach"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the government directory manager"""
        
        self.config_path = config_path
        self.base_path = Path(config_path) if config_path else Path(__file__).parent
        self.data_path = self.base_path / 'government_directory'
        self.data_path.mkdir(exist_ok=True)
        
        # Database files
        self.officials_db = self.data_path / 'government_officials_directory.json'
        self.contacts_db = self.data_path / 'contact_history.json'
        self.outreach_db = self.data_path / 'outreach_campaigns.json'
        self.verification_chain_db = self.data_path / 'verification_chain.json'
        
        # Initialize blockchain if available
        self.blockchain = CivicBlockchain() if BLOCKCHAIN_AVAILABLE else None
        
        # Initialize databases
        self._initialize_databases()
        
        # Load comprehensive government data
        self._load_world_government_data()
        
        print("🏛️ Government Officials Directory Manager initialized")
        print(f"📊 Loaded {self.get_total_officials()} government officials worldwide")
    
    def _initialize_databases(self):
        """Initialize government directory databases"""
        
        if not self.officials_db.exists():
            initial_officials = {
                'officials': {},
                'countries': {},
                'states': {},
                'cities': {},
                'verification_chain': {
                    'founders': [],
                    'country_verifiers': {},
                    'state_verifiers': {},
                    'city_verifiers': {}
                },
                'last_updated': datetime.now().isoformat(),
                'total_officials': 0
            }
            self._save_json(self.officials_db, initial_officials)
        
        if not self.contacts_db.exists():
            initial_contacts = {
                'contact_history': [],
                'email_templates': {
                    'initial_invitation': {
                        'subject': 'Invitation to Join Revolutionary Civic Engagement Platform',
                        'template': 'Dear {title} {name},\n\nWe invite you to join our innovative civic engagement platform...'
                    },
                    'follow_up': {
                        'subject': 'Follow-up: Civic Engagement Platform Invitation',
                        'template': 'Dear {title} {name},\n\nFollowing up on our invitation...'
                    },
                    'verification_request': {
                        'subject': 'Platform Verification Request',
                        'template': 'Dear {title} {name},\n\nTo complete your verification...'
                    }
                },
                'last_updated': datetime.now().isoformat()
            }
            self._save_json(self.contacts_db, initial_contacts)
        
        if not self.outreach_db.exists():
            initial_outreach = {
                'campaigns': {},
                'statistics': {
                    'total_contacted': 0,
                    'responses_received': 0,
                    'officials_joined': 0,
                    'officials_verified': 0
                },
                'last_updated': datetime.now().isoformat()
            }
            self._save_json(self.outreach_db, initial_outreach)
        
        if not self.verification_chain_db.exists():
            initial_verification = {
                'hierarchy': {
                    'founders': {
                        'emails': [
                            'founder1@civic_platform.org',
                            'founder2@civic_platform.org',
                            'founder3@civic_platform.org'
                        ],
                        'can_verify': ['country_leaders']
                    },
                    'country_leaders': {
                        'verified_officials': {},
                        'can_verify': ['state_leaders']
                    },
                    'state_leaders': {
                        'verified_officials': {},
                        'can_verify': ['city_leaders']
                    },
                    'city_leaders': {
                        'verified_officials': {},
                        'can_verify': []
                    }
                },
                'verification_rules': {
                    'founders_verify_countries': True,
                    'countries_verify_states': True,
                    'states_verify_cities': True,
                    'no_cross_level_verification': True
                },
                'last_updated': datetime.now().isoformat()
            }
            self._save_json(self.verification_chain_db, initial_verification)
    
    def _load_world_government_data(self):
        """Load comprehensive world government officials data"""
        
        # Load existing data
        officials_data = self._load_json(self.officials_db)
        
        # Add comprehensive world leaders if not already present
        if len(officials_data.get('officials', {})) < 100:  # If database is sparse
            print("🌍 Loading comprehensive world government data...")
            
            # Major world leaders with contact information
            world_leaders = self._get_world_leaders_data()
            us_officials = self._get_us_government_data()
            major_cities = self._get_major_cities_data()
            
            # Combine all data
            all_officials = {**world_leaders, **us_officials, **major_cities}
            
            # Update database
            officials_data['officials'].update(all_officials)
            officials_data['total_officials'] = len(officials_data['officials'])
            
            self._save_json(self.officials_db, officials_data)
            
            print(f"✅ Loaded {len(all_officials)} government officials")
    
    def _get_world_leaders_data(self) -> Dict[str, Dict[str, Any]]:
        """Get major world leaders with contact information"""
        
        world_leaders = {
            # United States
            'us_president': {
                'name': 'Joe Biden',
                'title': 'President of the United States',
                'official_type': 'president',
                'jurisdiction': 'United States',
                'jurisdiction_level': 'country',
                'country': 'United States',
                'email': 'president@whitehouse.gov',
                'phone': '+1-202-456-1414',
                'office_address': '1600 Pennsylvania Avenue NW, Washington, DC 20500',
                'website': 'https://whitehouse.gov',
                'party_affiliation': 'Democratic Party',
                'term_start': '2021-01-20',
                'term_end': '2025-01-20',
                'population_served': 331900000
            },
            
            # United Kingdom
            'uk_prime_minister': {
                'name': 'Rishi Sunak',
                'title': 'Prime Minister of the United Kingdom',
                'official_type': 'prime_minister',
                'jurisdiction': 'United Kingdom',
                'jurisdiction_level': 'country',
                'country': 'United Kingdom',
                'email': 'pm@number10.gov.uk',
                'phone': '+44-20-7930-4433',
                'office_address': '10 Downing Street, London SW1A 2AA',
                'website': 'https://gov.uk',
                'party_affiliation': 'Conservative Party',
                'population_served': 67500000
            },
            
            # Germany
            'germany_chancellor': {
                'name': 'Olaf Scholz',
                'title': 'Chancellor of Germany',
                'official_type': 'chancellor',
                'jurisdiction': 'Germany',
                'jurisdiction_level': 'country',
                'country': 'Germany',
                'email': 'bundeskanzler@bundeskanzleramt.de',
                'phone': '+49-30-18400-0',
                'office_address': 'Willy-Brandt-Straße 1, 10557 Berlin',
                'website': 'https://bundeskanzler.de',
                'party_affiliation': 'Social Democratic Party',
                'population_served': 83200000
            },
            
            # France
            'france_president': {
                'name': 'Emmanuel Macron',
                'title': 'President of France',
                'official_type': 'president',
                'jurisdiction': 'France',
                'jurisdiction_level': 'country',
                'country': 'France',
                'email': 'contact@elysee.fr',
                'phone': '+33-1-42-92-81-00',
                'office_address': '55 Rue du Faubourg Saint-Honoré, 75008 Paris',
                'website': 'https://elysee.fr',
                'party_affiliation': 'Renaissance',
                'population_served': 68000000
            },
            
            # Canada
            'canada_prime_minister': {
                'name': 'Justin Trudeau',
                'title': 'Prime Minister of Canada',
                'official_type': 'prime_minister',
                'jurisdiction': 'Canada',
                'jurisdiction_level': 'country',
                'country': 'Canada',
                'email': 'pm@pm.gc.ca',
                'phone': '+1-613-992-4211',
                'office_address': '80 Wellington Street, Ottawa, ON K1A 0A2',
                'website': 'https://pm.gc.ca',
                'party_affiliation': 'Liberal Party',
                'population_served': 38000000
            },
            
            # Japan
            'japan_prime_minister': {
                'name': 'Fumio Kishida',
                'title': 'Prime Minister of Japan',
                'official_type': 'prime_minister',
                'jurisdiction': 'Japan',
                'jurisdiction_level': 'country',
                'country': 'Japan',
                'email': 'info@kantei.go.jp',
                'phone': '+81-3-3581-0101',
                'office_address': '2-3-1 Nagatacho, Chiyoda-ku, Tokyo 100-8968',
                'website': 'https://kantei.go.jp',
                'party_affiliation': 'Liberal Democratic Party',
                'population_served': 125000000
            },
            
            # Australia
            'australia_prime_minister': {
                'name': 'Anthony Albanese',
                'title': 'Prime Minister of Australia',
                'official_type': 'prime_minister',
                'jurisdiction': 'Australia',
                'jurisdiction_level': 'country',
                'country': 'Australia',
                'email': 'pm@pmc.gov.au',
                'phone': '+61-2-6271-5111',
                'office_address': '1 National Circuit, Barton ACT 2600',
                'website': 'https://pm.gov.au',
                'party_affiliation': 'Labor Party',
                'population_served': 26000000
            }
        }
        
        # Convert to proper format with IDs
        formatted_leaders = {}
        for leader_id, data in world_leaders.items():
            official_id = f"country_{data['country'].lower().replace(' ', '_')}_{leader_id}"
            
            # Add required fields with defaults
            formatted_data = {
                'official_id': official_id,
                'verification_status': 'uncontacted',
                'platform_account_email': None,
                'verified_by': None,
                'verification_date': None,
                'verification_notes': '',
                'first_contacted': None,
                'last_contact': None,
                'contact_attempts': 0,
                'response_received': False,
                'state_province': None,
                'social_media': {}
            }
            formatted_data.update(data)
            
            formatted_leaders[official_id] = formatted_data
        
        return formatted_leaders
    
    def _get_us_government_data(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive US government officials data"""
        
        us_officials = {}
        
        # US State Governors
        us_governors = {
            'california': {
                'name': 'Gavin Newsom',
                'title': 'Governor of California',
                'email': 'governor@gov.ca.gov',
                'phone': '+1-916-445-2841',
                'website': 'https://gov.ca.gov'
            },
            'texas': {
                'name': 'Greg Abbott',
                'title': 'Governor of Texas',
                'email': 'governor@gov.texas.gov',
                'phone': '+1-512-463-2000',
                'website': 'https://gov.texas.gov'
            },
            'florida': {
                'name': 'Ron DeSantis',
                'title': 'Governor of Florida',
                'email': 'governor.rick.scott@eog.myflorida.com',
                'phone': '+1-850-717-9337',
                'website': 'https://flgov.com'
            },
            'new_york': {
                'name': 'Kathy Hochul',
                'title': 'Governor of New York',
                'email': 'governor@exec.ny.gov',
                'phone': '+1-518-474-8390',
                'website': 'https://governor.ny.gov'
            },
            'illinois': {
                'name': 'J.B. Pritzker',
                'title': 'Governor of Illinois',
                'email': 'gov.pritzker@illinois.gov',
                'phone': '+1-217-782-0244',
                'website': 'https://gov.illinois.gov'
            }
        }
        
        for state, gov_data in us_governors.items():
            official_id = f"state_united_states_{state}_governor"
            us_officials[official_id] = {
                'official_id': official_id,
                'name': gov_data['name'],
                'title': gov_data['title'],
                'official_type': 'governor',
                'jurisdiction': state.replace('_', ' ').title(),
                'jurisdiction_level': 'state',
                'country': 'United States',
                'state_province': state.replace('_', ' ').title(),
                'email': gov_data['email'],
                'phone': gov_data['phone'],
                'website': gov_data['website'],
                'verification_status': 'uncontacted',
                'contact_attempts': 0,
                'response_received': False
            }
        
        return us_officials
    
    def _get_major_cities_data(self) -> Dict[str, Dict[str, Any]]:
        """Get major world cities mayors data"""
        
        major_cities = {
            'new_york_city': {
                'name': 'Eric Adams',
                'title': 'Mayor of New York City',
                'jurisdiction': 'New York City',
                'state': 'New York',
                'country': 'United States',
                'email': 'mayor@cityhall.nyc.gov',
                'phone': '+1-212-788-3000',
                'population': 8400000
            },
            'los_angeles': {
                'name': 'Karen Bass',
                'title': 'Mayor of Los Angeles',
                'jurisdiction': 'Los Angeles',
                'state': 'California',
                'country': 'United States',
                'email': 'mayor@lacity.org',
                'phone': '+1-213-978-0600',
                'population': 4000000
            },
            'london': {
                'name': 'Sadiq Khan',
                'title': 'Mayor of London',
                'jurisdiction': 'London',
                'country': 'United Kingdom',
                'email': 'mayor@london.gov.uk',
                'phone': '+44-20-7983-4000',
                'population': 9000000
            },
            'tokyo': {
                'name': 'Yuriko Koike',
                'title': 'Governor of Tokyo',
                'jurisdiction': 'Tokyo',
                'country': 'Japan',
                'email': 'info@metro.tokyo.lg.jp',
                'phone': '+81-3-5321-1111',
                'population': 14000000
            },
            'paris': {
                'name': 'Anne Hidalgo',
                'title': 'Mayor of Paris',
                'jurisdiction': 'Paris',
                'country': 'France',
                'email': 'maire@paris.fr',
                'phone': '+33-1-42-76-40-40',
                'population': 2200000
            }
        }
        
        formatted_cities = {}
        for city_id, data in major_cities.items():
            official_id = f"city_{data['country'].lower().replace(' ', '_')}_{city_id}"
            
            formatted_cities[official_id] = {
                'official_id': official_id,
                'name': data['name'],
                'title': data['title'],
                'official_type': 'mayor',
                'jurisdiction': data['jurisdiction'],
                'jurisdiction_level': 'city',
                'country': data['country'],
                'state_province': data.get('state'),
                'email': data['email'],
                'phone': data['phone'],
                'population_served': data['population'],
                'verification_status': 'uncontacted',
                'contact_attempts': 0,
                'response_received': False
            }
        
        return formatted_cities
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Save JSON data to file"""
        data['last_updated'] = datetime.now().isoformat()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_government_official(self, official: GovernmentOfficial) -> Tuple[bool, str]:
        """Add a government official to the directory"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            
            # Check if official already exists
            if official.official_id in officials_data.get('officials', {}):
                return False, f"Official with ID {official.official_id} already exists"
            
            # Add official to database
            officials_data.setdefault('officials', {})[official.official_id] = official.to_dict()
            officials_data['total_officials'] = len(officials_data['officials'])
            
            self._save_json(self.officials_db, officials_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="government_official_added_to_directory",
                    user_email="system@government_directory",
                    data={
                        'official': official.to_dict(),
                        'directory_action': 'add_official',
                        'timestamp': datetime.now().isoformat()
                    }
                )
            
            return True, f"Official {official.name} added to directory successfully"
            
        except Exception as e:
            return False, f"Failed to add official: {str(e)}"
    
    def get_officials_by_level(self, level: str) -> List[Dict[str, Any]]:
        """Get all officials by jurisdiction level (country, state, city)"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            officials = list(officials_data.get('officials', {}).values())
            
            return [o for o in officials if o.get('jurisdiction_level') == level]
            
        except Exception as e:
            print(f"Error getting officials by level: {e}")
            return []
    
    def get_officials_by_country(self, country: str) -> List[Dict[str, Any]]:
        """Get all officials from a specific country"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            officials = list(officials_data.get('officials', {}).values())
            
            return [o for o in officials if o.get('country', '').lower() == country.lower()]
            
        except Exception as e:
            print(f"Error getting officials by country: {e}")
            return []
    
    def get_uncontacted_officials(self) -> List[Dict[str, Any]]:
        """Get all officials who haven't been contacted yet"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            officials = list(officials_data.get('officials', {}).values())
            
            return [o for o in officials if o.get('verification_status') == 'uncontacted']
            
        except Exception as e:
            print(f"Error getting uncontacted officials: {e}")
            return []
    
    def record_contact_attempt(self, official_id: str, contact_method: str, 
                             response_received: bool = False, notes: str = "") -> Tuple[bool, str]:
        """Record a contact attempt with a government official"""
        
        try:
            # Update official record
            officials_data = self._load_json(self.officials_db)
            
            if official_id not in officials_data.get('officials', {}):
                return False, f"Official {official_id} not found"
            
            official = officials_data['officials'][official_id]
            current_time = datetime.now().isoformat()
            
            # Update contact information
            official['contact_attempts'] = official.get('contact_attempts', 0) + 1
            official['last_contact'] = current_time
            if not official.get('first_contacted'):
                official['first_contacted'] = current_time
            
            if response_received:
                official['response_received'] = True
                if official.get('verification_status') == 'uncontacted':
                    official['verification_status'] = 'contacted'
            
            officials_data['officials'][official_id] = official
            self._save_json(self.officials_db, officials_data)
            
            # Record contact history
            contacts_data = self._load_json(self.contacts_db)
            contact_record = {
                'contact_id': f"contact_{official_id}_{len(contacts_data.get('contact_history', []))}",
                'official_id': official_id,
                'official_name': official.get('name', ''),
                'contact_method': contact_method,
                'timestamp': current_time,
                'response_received': response_received,
                'notes': notes
            }
            
            contacts_data.setdefault('contact_history', []).append(contact_record)
            self._save_json(self.contacts_db, contacts_data)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="government_official_contacted",
                    user_email="system@government_directory",
                    data={
                        'contact_record': contact_record,
                        'outreach_activity': True,
                        'timestamp': current_time
                    }
                )
            
            return True, f"Contact attempt recorded for {official.get('name', official_id)}"
            
        except Exception as e:
            return False, f"Failed to record contact: {str(e)}"
    
    def verify_government_official(self, official_id: str, verified_by: str,
                                 verification_authority: VerificationAuthority,
                                 verification_notes: str = "") -> Tuple[bool, str]:
        """Verify government official through hierarchical verification chain"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            
            if official_id not in officials_data.get('officials', {}):
                return False, f"Official {official_id} not found"
            
            official = officials_data['officials'][official_id]
            
            # Check verification authority hierarchy
            can_verify, authority_message = self._check_verification_authority(
                official, verified_by, verification_authority
            )
            
            if not can_verify:
                return False, authority_message
            
            # Update verification status
            official['verification_status'] = 'verified'
            official['verified_by'] = verified_by
            official['verification_date'] = datetime.now().isoformat()
            official['verification_notes'] = verification_notes
            
            officials_data['officials'][official_id] = official
            self._save_json(self.officials_db, officials_data)
            
            # Update verification chain
            self._update_verification_chain(official, verified_by, verification_authority)
            
            # Record on blockchain
            if self.blockchain:
                self.blockchain.add_page(
                    action_type="government_official_verified_directory",
                    user_email=verified_by,
                    data={
                        'official_verified': official,
                        'verification_authority': verification_authority.value,
                        'verification_hierarchy': 'founders->countries->states->cities',
                        'separate_from_contract_system': True,
                        'timestamp': datetime.now().isoformat()
                    }
                )
            
            return True, f"Official {official['name']} verified successfully by {verification_authority.value}"
            
        except Exception as e:
            return False, f"Failed to verify official: {str(e)}"
    
    def _check_verification_authority(self, official: Dict[str, Any], verified_by: str,
                                   verification_authority: VerificationAuthority) -> Tuple[bool, str]:
        """Check if verifier has authority to verify this official"""
        
        verification_data = self._load_json(self.verification_chain_db)
        hierarchy = verification_data.get('hierarchy', {})
        
        official_level = official.get('jurisdiction_level', '')
        
        # Founders can verify country leaders
        if verification_authority == VerificationAuthority.FOUNDER:
            if official_level == 'country':
                founder_emails = hierarchy.get('founders', {}).get('emails', [])
                if verified_by in founder_emails:
                    return True, "Founder authority confirmed"
                else:
                    return False, f"Verifier {verified_by} not in founders list"
            else:
                return False, "Founders can only verify country leaders"
        
        # Country leaders can verify state leaders
        elif verification_authority == VerificationAuthority.COUNTRY_LEADER:
            if official_level == 'state':
                country_verifiers = hierarchy.get('country_leaders', {}).get('verified_officials', {})
                if verified_by in country_verifiers:
                    return True, "Country leader authority confirmed"
                else:
                    return False, f"Verifier {verified_by} not a verified country leader"
            else:
                return False, "Country leaders can only verify state leaders"
        
        # State leaders can verify city leaders
        elif verification_authority == VerificationAuthority.STATE_LEADER:
            if official_level == 'city':
                state_verifiers = hierarchy.get('state_leaders', {}).get('verified_officials', {})
                if verified_by in state_verifiers:
                    return True, "State leader authority confirmed"
                else:
                    return False, f"Verifier {verified_by} not a verified state leader"
            else:
                return False, "State leaders can only verify city leaders"
        
        return False, "Invalid verification authority"
    
    def _update_verification_chain(self, official: Dict[str, Any], verified_by: str,
                                 verification_authority: VerificationAuthority):
        """Update the verification chain with newly verified official"""
        
        verification_data = self._load_json(self.verification_chain_db)
        hierarchy = verification_data.get('hierarchy', {})
        
        official_level = official.get('jurisdiction_level', '')
        
        # Add to appropriate verifier level
        if official_level == 'country':
            hierarchy.setdefault('country_leaders', {}).setdefault('verified_officials', {})[verified_by] = {
                'official_id': official['official_id'],
                'name': official['name'],
                'country': official['country'],
                'verified_date': datetime.now().isoformat()
            }
        elif official_level == 'state':
            hierarchy.setdefault('state_leaders', {}).setdefault('verified_officials', {})[verified_by] = {
                'official_id': official['official_id'],
                'name': official['name'],
                'state': official.get('state_province', ''),
                'verified_date': datetime.now().isoformat()
            }
        elif official_level == 'city':
            hierarchy.setdefault('city_leaders', {}).setdefault('verified_officials', {})[verified_by] = {
                'official_id': official['official_id'],
                'name': official['name'],
                'city': official['jurisdiction'],
                'verified_date': datetime.now().isoformat()
            }
        
        verification_data['hierarchy'] = hierarchy
        self._save_json(self.verification_chain_db, verification_data)
    
    def export_officials_csv(self, filename: Optional[str] = None) -> Tuple[bool, str]:
        """Export all officials to CSV for outreach purposes"""
        
        try:
            if not filename:
                filename = f"government_officials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            filepath = self.data_path / filename
            
            officials_data = self._load_json(self.officials_db)
            officials = list(officials_data.get('officials', {}).values())
            
            if not officials:
                return False, "No officials to export"
            
            # CSV headers
            headers = [
                'Official ID', 'Name', 'Title', 'Official Type', 'Jurisdiction',
                'Level', 'Country', 'State/Province', 'Email', 'Phone',
                'Website', 'Office Address', 'Party Affiliation', 'Term Start',
                'Term End', 'Population Served', 'Verification Status',
                'Contact Attempts', 'Response Received', 'Last Contact'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                
                for official in officials:
                    writer.writerow([
                        official.get('official_id', ''),
                        official.get('name', ''),
                        official.get('title', ''),
                        official.get('official_type', ''),
                        official.get('jurisdiction', ''),
                        official.get('jurisdiction_level', ''),
                        official.get('country', ''),
                        official.get('state_province', ''),
                        official.get('email', ''),
                        official.get('phone', ''),
                        official.get('website', ''),
                        official.get('office_address', ''),
                        official.get('party_affiliation', ''),
                        official.get('term_start', ''),
                        official.get('term_end', ''),
                        official.get('population_served', ''),
                        official.get('verification_status', ''),
                        official.get('contact_attempts', 0),
                        official.get('response_received', False),
                        official.get('last_contact', '')
                    ])
            
            return True, f"Officials exported to {filepath}"
            
        except Exception as e:
            return False, f"Failed to export CSV: {str(e)}"
    
    def get_directory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive directory statistics"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            contacts_data = self._load_json(self.contacts_db)
            
            officials = list(officials_data.get('officials', {}).values())
            
            # Count by level
            level_counts = {}
            for official in officials:
                level = official.get('jurisdiction_level', 'unknown')
                level_counts[level] = level_counts.get(level, 0) + 1
            
            # Count by verification status
            status_counts = {}
            for official in officials:
                status = official.get('verification_status', 'uncontacted')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by country
            country_counts = {}
            for official in officials:
                country = official.get('country', 'Unknown')
                country_counts[country] = country_counts.get(country, 0) + 1
            
            # Contact statistics
            total_contacts = len(contacts_data.get('contact_history', []))
            responded_officials = len([o for o in officials if o.get('response_received', False)])
            
            return {
                'total_officials': len(officials),
                'officials_by_level': level_counts,
                'officials_by_status': status_counts,
                'officials_by_country': country_counts,
                'total_contact_attempts': total_contacts,
                'officials_responded': responded_officials,
                'uncontacted_officials': status_counts.get('uncontacted', 0),
                'verified_officials': status_counts.get('verified', 0),
                'response_rate': (responded_officials / len(officials) * 100) if officials else 0,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get statistics: {str(e)}",
                'total_officials': 0
            }
    
    def get_total_officials(self) -> int:
        """Get total number of officials in directory"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            return len(officials_data.get('officials', {}))
        except:
            return 0
    
    def search_officials(self, query: str = "", country: str = "", level: str = "",
                        status: str = "") -> List[Dict[str, Any]]:
        """Search government officials with filters"""
        
        try:
            officials_data = self._load_json(self.officials_db)
            officials = list(officials_data.get('officials', {}).values())
            
            # Apply filters
            if query:
                officials = [o for o in officials 
                           if query.lower() in o.get('name', '').lower() or 
                              query.lower() in o.get('title', '').lower() or
                              query.lower() in o.get('jurisdiction', '').lower()]
            
            if country:
                officials = [o for o in officials 
                           if o.get('country', '').lower() == country.lower()]
            
            if level:
                officials = [o for o in officials 
                           if o.get('jurisdiction_level', '') == level]
            
            if status:
                officials = [o for o in officials 
                           if o.get('verification_status', '') == status]
            
            return officials
            
        except Exception as e:
            print(f"Error searching officials: {e}")
            return []


# Demo and testing functions
def demonstrate_government_directory():
    """Demonstrate the government directory system"""
    
    print("\n" + "="*80)
    print("🏛️ COMPREHENSIVE GOVERNMENT OFFICIALS DIRECTORY DEMONSTRATION")
    print("="*80)
    
    # Initialize manager
    print("\n🔧 STEP 1: Initialize Government Directory Manager")
    print("-" * 60)
    
    manager = GovernmentDirectoryManager()
    
    # Show loaded officials
    print(f"\n📊 STEP 2: Directory Statistics")
    print("-" * 60)
    
    stats = manager.get_directory_statistics()
    print(f"   Total Officials: {stats.get('total_officials', 0)}")
    print(f"   Countries: {len(stats.get('officials_by_country', {}))}")
    print(f"   Country Leaders: {stats.get('officials_by_level', {}).get('country', 0)}")
    print(f"   State/Provincial Leaders: {stats.get('officials_by_level', {}).get('state', 0)}")
    print(f"   City Leaders: {stats.get('officials_by_level', {}).get('city', 0)}")
    print(f"   Uncontacted: {stats.get('uncontacted_officials', 0)}")
    print(f"   Verified: {stats.get('verified_officials', 0)}")
    
    # Show sample officials by level
    print(f"\n🌍 STEP 3: Sample Country Leaders")
    print("-" * 60)
    
    country_officials = manager.get_officials_by_level('country')
    for official in country_officials[:5]:  # Show first 5
        print(f"   {official['name']} - {official['title']}")
        print(f"   📧 {official.get('email', 'No email')}")
        print(f"   📞 {official.get('phone', 'No phone')}")
        print(f"   🔗 {official.get('website', 'No website')}")
        print(f"   📊 Status: {official['verification_status']}")
        print()
    
    # Show US state officials
    print(f"\n🇺🇸 STEP 4: US State Governors")
    print("-" * 60)
    
    us_officials = manager.get_officials_by_country('United States')
    state_officials = [o for o in us_officials if o.get('jurisdiction_level') == 'state']
    
    for official in state_officials:
        print(f"   {official['name']} - {official['title']}")
        print(f"   📧 {official.get('email', 'No email')}")
        print(f"   📞 {official.get('phone', 'No phone')}")
        print()
    
    # Demonstrate contact tracking
    print(f"\n📞 STEP 5: Contact Outreach Simulation")
    print("-" * 60)
    
    # Simulate contacting officials
    uncontacted = manager.get_uncontacted_officials()[:3]  # Contact first 3
    
    for official in uncontacted:
        official_id = official['official_id']
        print(f"   Contacting: {official['name']}")
        
        # Record contact attempt
        success, message = manager.record_contact_attempt(
            official_id=official_id,
            contact_method="email",
            response_received=True,  # Simulate positive response
            notes="Initial platform invitation sent via official email"
        )
        
        if success:
            print(f"   ✅ Contact recorded: {message}")
        else:
            print(f"   ❌ Contact failed: {message}")
    
    # Demonstrate hierarchical verification
    print(f"\n✅ STEP 6: Hierarchical Verification Simulation")
    print("-" * 60)
    
    # Simulate founder verifying country leader
    country_officials = manager.get_officials_by_level('country')
    if country_officials:
        country_leader = country_officials[0]
        print(f"   Founder verifying: {country_leader['name']} (Country Leader)")
        
        success, message = manager.verify_government_official(
            official_id=country_leader['official_id'],
            verified_by="founder1@civic_platform.org",
            verification_authority=VerificationAuthority.FOUNDER,
            verification_notes="Verified through official government channels and diplomatic contacts"
        )
        
        if success:
            print(f"   ✅ Verification successful: {message}")
        else:
            print(f"   ❌ Verification failed: {message}")
    
    # Export to CSV
    print(f"\n📁 STEP 7: Export Officials Directory")
    print("-" * 60)
    
    success, message = manager.export_officials_csv("government_officials_demo.csv")
    if success:
        print(f"   ✅ Export successful: {message}")
    else:
        print(f"   ❌ Export failed: {message}")
    
    # Final statistics
    print(f"\n📊 STEP 8: Updated Statistics")
    print("-" * 60)
    
    final_stats = manager.get_directory_statistics()
    print(f"   Response Rate: {final_stats.get('response_rate', 0):.1f}%")
    print(f"   Total Contacts Made: {final_stats.get('total_contact_attempts', 0)}")
    print(f"   Officials Responded: {final_stats.get('officials_responded', 0)}")
    print(f"   Officials Verified: {final_stats.get('verified_officials', 0)}")
    
    print(f"\n🎉 Government Directory System Demonstration Complete!")
    
    return True


if __name__ == "__main__":
    demonstrate_government_directory()