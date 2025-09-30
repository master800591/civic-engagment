"""
Location Services Module - Geographic Civic Engagement & Location Management
Implements location-based civic participation, jurisdictional boundary management,
and event location coordination with privacy protection and blockchain integration.
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import required modules
try:
    from blockchain.blockchain import add_user_action
    from users.backend import UserBackend
    BLOCKCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Import error in location_services: {e}")
    add_user_action = None
    BLOCKCHAIN_AVAILABLE = False
    UserBackend = None


class GeographicCivicEngagementSystem:
    """Location-Based Democratic Participation and Governance"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize geographic services system"""
        if db_path is None:
            db_path = os.path.join(current_dir, 'maps_db.json')
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure the database file exists with proper structure"""
        if not os.path.exists(self.db_path):
            initial_data = {
                'geographic_configurations': [],
                'civic_venues': [],
                'jurisdictional_boundaries': [],
                'event_location_coordination': []
            }
            self.save_database(initial_data)
    
    def load_database(self) -> Dict:
        """Load the geographic database"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ensure_database_exists()
            return self.load_database()
    
    def save_database(self, data: Dict):
        """Save the geographic database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def has_geographic_services_authority(self, admin: Dict) -> bool:
        """Check if user has authority to configure geographic services"""
        if not admin:
            return False
        role = admin.get('role', '').lower()
        return role in ['contract_founder', 'contract_elder', 'contract_senator']
    
    def has_venue_registration_authority(self, registrar: Dict, jurisdiction: str) -> bool:
        """Check if user has authority to register venues"""
        if not registrar:
            return False
        role = registrar.get('role', '').lower()
        # Representatives and higher can register venues
        return role in ['contract_founder', 'contract_elder', 'contract_senator', 'contract_representative']
    
    def initialize_geographic_services(self, admin_email: str, geographic_config: Dict) -> Tuple[bool, str]:
        """Initialize geographic services with privacy-compliant location tracking"""
        
        # Validate Geographic Services Authority
        if UserBackend:
            user_backend = UserBackend()
            admin = user_backend.get_user(admin_email)
            if not self.has_geographic_services_authority(admin):
                return False, "Insufficient authority to configure geographic services"
        
        # Geographic Service Types
        GEOGRAPHIC_SERVICES = {
            'jurisdictional_mapping': {
                'description': 'Official boundary mapping and representation',
                'privacy_level': 'public',
                'accuracy_requirement': 'high',
                'update_frequency': 'quarterly'
            },
            'civic_venue_mapping': {
                'description': 'Public meeting venues and civic spaces',
                'privacy_level': 'public',
                'accuracy_requirement': 'high',
                'update_frequency': 'monthly'
            },
            'demographic_visualization': {
                'description': 'Population and demographic mapping',
                'privacy_level': 'aggregated_only',
                'accuracy_requirement': 'medium',
                'update_frequency': 'annually'
            },
            'participation_analytics': {
                'description': 'Geographic participation pattern analysis',
                'privacy_level': 'anonymized',
                'accuracy_requirement': 'medium',
                'update_frequency': 'monthly'
            },
            'emergency_coordination': {
                'description': 'Emergency response and coordination mapping',
                'privacy_level': 'authorized_only',
                'accuracy_requirement': 'very_high',
                'update_frequency': 'real_time'
            }
        }
        
        # Privacy and Security Configuration
        privacy_framework = {
            'location_data_encryption': True,
            'anonymization_required': True,
            'consent_tracking': True,
            'data_retention_limits': geographic_config.get('retention_days', 365),
            'opt_out_available': True,
            'granularity_controls': {
                'exact_location': 'authorized_only',
                'neighborhood_level': 'opt_in',
                'city_level': 'default',
                'aggregated_only': 'always_available'
            }
        }
        
        # Initialize Map Services
        map_services = {
            'base_map_provider': 'OpenStreetMap',
            'tile_server': geographic_config.get('tile_server', 'https://tile.openstreetmap.org/'),
            'geocoding_service': 'nominatim',
            'reverse_geocoding': True,
            'routing_service': 'osrm',
            'offline_capabilities': geographic_config.get('offline_support', True)
        }
        
        # Create Geographic Configuration
        config_id = str(uuid.uuid4())
        geographic_configuration = {
            'id': config_id,
            'administrator_email': admin_email,
            'service_configuration': {
                'enabled_services': geographic_config.get('enabled_services', list(GEOGRAPHIC_SERVICES.keys())),
                'service_definitions': GEOGRAPHIC_SERVICES,
                'privacy_framework': privacy_framework,
                'map_services': map_services
            },
            'accessibility_features': {
                'screen_reader_support': True,
                'high_contrast_mode': True,
                'keyboard_navigation': True,
                'voice_description': True,
                'alternative_text_maps': True
            },
            'performance_optimization': {
                'tile_caching': True,
                'data_compression': True,
                'progressive_loading': True,
                'mobile_optimization': True
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': None,
            'status': 'active'
        }
        
        # Save Geographic Configuration
        db = self.load_database()
        db['geographic_configurations'].append(geographic_configuration)
        self.save_database(db)
        
        # Record Geographic Services Initialization on Blockchain
        if BLOCKCHAIN_AVAILABLE and add_user_action:
            try:
                add_user_action(
                    action_type="geographic_services_initialized",
                    user_email=admin_email,
                    data={
                        'config_id': config_id,
                        'administrator_email': admin_email,
                        'enabled_services': geographic_config.get('enabled_services', []),
                        'privacy_level': privacy_framework['granularity_controls']
                    }
                )
            except Exception as e:
                print(f"Warning: Could not record to blockchain: {e}")
        
        return True, config_id
    
    def register_civic_venue(self, registrar_email: str, venue_data: Dict) -> Tuple[bool, str]:
        """Register civic venue for public meetings and events"""
        
        # Validate Venue Registration Authority
        if UserBackend:
            user_backend = UserBackend()
            registrar = user_backend.get_user(registrar_email)
            if not self.has_venue_registration_authority(registrar, venue_data.get('jurisdiction', '')):
                return False, "Insufficient authority to register venues in this jurisdiction"
        
        # Civic Venue Categories with requirements
        VENUE_CATEGORIES = {
            'town_hall': {
                'description': 'Primary municipal meeting facility',
                'capacity_requirement': 100,
                'accessibility_required': True,
                'av_equipment_required': True
            },
            'community_center': {
                'description': 'Community meeting and event space',
                'capacity_requirement': 50,
                'accessibility_required': True,
                'av_equipment_required': False
            },
            'school_auditorium': {
                'description': 'Educational facility for civic use',
                'capacity_requirement': 200,
                'accessibility_required': True,
                'av_equipment_required': True
            },
            'outdoor_space': {
                'description': 'Public outdoor gathering space',
                'capacity_requirement': 500,
                'accessibility_required': True,
                'weather_protection': False
            },
            'library_meeting_room': {
                'description': 'Library-based meeting facility',
                'capacity_requirement': 25,
                'accessibility_required': True,
                'av_equipment_required': False
            },
            'emergency_facility': {
                'description': 'Emergency coordination center',
                'capacity_requirement': 50,
                'accessibility_required': True,
                'special_equipment_required': True
            }
        }
        
        venue_category = VENUE_CATEGORIES.get(venue_data.get('category', ''))
        if not venue_category:
            return False, "Invalid venue category"
        
        # Validate required fields
        required_fields = ['name', 'category', 'location', 'capacity', 'accessibility', 'contact']
        missing_fields = [field for field in required_fields if field not in venue_data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Create Venue Record
        venue_id = str(uuid.uuid4())
        venue_record = {
            'id': venue_id,
            'registrar_email': registrar_email,
            'venue_name': venue_data['name'],
            'category': venue_data['category'],
            'description': venue_data.get('description', ''),
            'location': {
                'address': venue_data['location'].get('address', ''),
                'coordinates': {
                    'latitude': venue_data['location'].get('latitude', 0.0),
                    'longitude': venue_data['location'].get('longitude', 0.0)
                },
                'jurisdiction': venue_data.get('jurisdiction', ''),
                'postal_code': venue_data['location'].get('postal_code', ''),
                'accessibility_notes': venue_data['location'].get('accessibility_notes', '')
            },
            'capacity_information': {
                'maximum_capacity': venue_data['capacity'].get('maximum', 0),
                'accessible_seating': venue_data['capacity'].get('accessible_seating', 0),
                'standing_capacity': venue_data['capacity'].get('standing_capacity', 0),
                'parking_availability': venue_data['capacity'].get('parking', False)
            },
            'facilities_equipment': {
                'av_equipment': venue_data.get('equipment', {}).get('av_system', False),
                'sound_system': venue_data.get('equipment', {}).get('sound_system', False),
                'projection_system': venue_data.get('equipment', {}).get('projection', False),
                'wifi_access': venue_data.get('equipment', {}).get('wifi', False),
                'live_streaming_capability': venue_data.get('equipment', {}).get('streaming', False)
            },
            'accessibility_features': {
                'wheelchair_accessible': venue_data['accessibility'].get('wheelchair_access', False),
                'accessible_parking': venue_data['accessibility'].get('accessible_parking', False),
                'hearing_assistance': venue_data['accessibility'].get('hearing_loop', False),
                'visual_accessibility': venue_data['accessibility'].get('visual_aids', False),
                'service_animal_friendly': venue_data['accessibility'].get('service_animals', True)
            },
            'contact_information': {
                'primary_contact': venue_data['contact'].get('primary_contact', ''),
                'phone_number': venue_data['contact'].get('phone', ''),
                'email': venue_data['contact'].get('email', ''),
                'emergency_contact': venue_data['contact'].get('emergency_contact', '')
            },
            'registered_at': datetime.now().isoformat(),
            'verification_status': 'pending_verification',
            'last_inspection_date': venue_data.get('last_inspection'),
            'status': 'active'
        }
        
        # Save Venue Record
        db = self.load_database()
        db['civic_venues'].append(venue_record)
        self.save_database(db)
        
        # Record Venue Registration on Blockchain
        if BLOCKCHAIN_AVAILABLE and add_user_action:
            try:
                add_user_action(
                    action_type="civic_venue_registered",
                    user_email=registrar_email,
                    data={
                        'venue_id': venue_id,
                        'registrar_email': registrar_email,
                        'venue_name': venue_data['name'],
                        'category': venue_data['category'],
                        'jurisdiction': venue_data.get('jurisdiction', ''),
                        'capacity': venue_data['capacity'].get('maximum', 0)
                    }
                )
            except Exception as e:
                print(f"Warning: Could not record to blockchain: {e}")
        
        return True, venue_id


class JurisdictionalBoundaryManager:
    """Comprehensive Jurisdictional Mapping and Boundary Management"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize boundary manager"""
        if db_path is None:
            db_path = os.path.join(current_dir, 'maps_db.json')
        self.db_path = db_path
        self.geographic_system = GeographicCivicEngagementSystem(db_path)
    
    def load_database(self) -> Dict:
        """Load the geographic database"""
        return self.geographic_system.load_database()
    
    def save_database(self, data: Dict):
        """Save the geographic database"""
        self.geographic_system.save_database(data)
    
    def has_boundary_definition_authority(self, authority: Dict, jurisdiction_level: str) -> bool:
        """Check if user has authority to define boundaries at specified level"""
        if not authority:
            return False
        role = authority.get('role', '').lower()
        
        # Authority requirements by jurisdiction level
        authority_map = {
            'federal': ['contract_founder', 'contract_elder'],
            'state': ['contract_founder', 'contract_elder', 'contract_senator'],
            'county': ['contract_founder', 'contract_elder', 'contract_senator', 'contract_representative'],
            'city': ['contract_founder', 'contract_elder', 'contract_senator', 'contract_representative'],
            'district': ['contract_founder', 'contract_elder', 'contract_senator', 'contract_representative']
        }
        
        return role in authority_map.get(jurisdiction_level, [])
    
    def calculate_area(self, coordinates: List) -> float:
        """Calculate area in square kilometers (simplified)"""
        # Simplified area calculation - in production would use proper geodetic calculations
        return len(coordinates) * 10.0  # Placeholder
    
    def calculate_perimeter(self, coordinates: List) -> float:
        """Calculate perimeter in kilometers (simplified)"""
        return len(coordinates) * 5.0  # Placeholder
    
    def calculate_centroid(self, coordinates: List) -> Dict:
        """Calculate centroid of polygon"""
        if not coordinates:
            return {'latitude': 0.0, 'longitude': 0.0}
        # Simplified centroid calculation
        avg_lat = sum(c[0] for c in coordinates) / len(coordinates) if coordinates else 0.0
        avg_lon = sum(c[1] for c in coordinates) / len(coordinates) if coordinates else 0.0
        return {'latitude': avg_lat, 'longitude': avg_lon}
    
    def calculate_bounding_box(self, coordinates: List) -> Dict:
        """Calculate bounding box"""
        if not coordinates:
            return {'min_lat': 0.0, 'max_lat': 0.0, 'min_lon': 0.0, 'max_lon': 0.0}
        
        lats = [c[0] for c in coordinates]
        lons = [c[1] for c in coordinates]
        return {
            'min_lat': min(lats),
            'max_lat': max(lats),
            'min_lon': min(lons),
            'max_lon': max(lons)
        }
    
    def define_jurisdictional_boundaries(self, authority_email: str, boundary_data: Dict) -> Tuple[bool, str]:
        """Define and manage official jurisdictional boundaries"""
        
        # Validate Boundary Definition Authority
        if UserBackend:
            user_backend = UserBackend()
            authority = user_backend.get_user(authority_email)
            if not self.has_boundary_definition_authority(authority, boundary_data.get('jurisdiction_level', '')):
                return False, "Insufficient authority to define jurisdictional boundaries"
        
        # Jurisdiction Levels and Requirements
        JURISDICTION_LEVELS = {
            'federal': {
                'required_authority': 'Contract Elder',
                'boundary_precision': 'high',
                'constitutional_review_required': True,
                'public_comment_period': 90
            },
            'state': {
                'required_authority': 'Contract Senator',
                'boundary_precision': 'high',
                'constitutional_review_required': True,
                'public_comment_period': 60
            },
            'county': {
                'required_authority': 'Contract Representative',
                'boundary_precision': 'high',
                'constitutional_review_required': False,
                'public_comment_period': 30
            },
            'city': {
                'required_authority': 'Contract Representative',
                'boundary_precision': 'medium',
                'constitutional_review_required': False,
                'public_comment_period': 30
            },
            'district': {
                'required_authority': 'Contract Representative',
                'boundary_precision': 'medium',
                'constitutional_review_required': False,
                'public_comment_period': 14
            }
        }
        
        jurisdiction_config = JURISDICTION_LEVELS.get(boundary_data.get('jurisdiction_level', ''))
        if not jurisdiction_config:
            return False, "Invalid jurisdiction level"
        
        # Validate required fields
        required_fields = ['jurisdiction_name', 'jurisdiction_level', 'boundary_coordinates']
        missing_fields = [field for field in required_fields if field not in boundary_data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Create Boundary Record
        boundary_id = str(uuid.uuid4())
        boundary_record = {
            'id': boundary_id,
            'defining_authority_email': authority_email,
            'jurisdiction_name': boundary_data['jurisdiction_name'],
            'jurisdiction_level': boundary_data['jurisdiction_level'],
            'jurisdiction_type': boundary_data.get('jurisdiction_type', 'administrative'),
            'boundary_geometry': {
                'type': 'Polygon',
                'coordinates': boundary_data['boundary_coordinates'],
                'coordinate_system': boundary_data.get('coordinate_system', 'WGS84'),
                'precision_level': jurisdiction_config['boundary_precision']
            },
            'geographic_properties': {
                'total_area_sq_km': self.calculate_area(boundary_data['boundary_coordinates']),
                'perimeter_km': self.calculate_perimeter(boundary_data['boundary_coordinates']),
                'centroid': self.calculate_centroid(boundary_data['boundary_coordinates']),
                'bounding_box': self.calculate_bounding_box(boundary_data['boundary_coordinates'])
            },
            'administrative_details': {
                'parent_jurisdiction': boundary_data.get('parent_jurisdiction'),
                'child_jurisdictions': boundary_data.get('child_jurisdictions', []),
                'population_estimate': boundary_data.get('population'),
                'establishment_date': boundary_data.get('establishment_date'),
                'legal_authority': boundary_data.get('legal_authority')
            },
            'representation_framework': {
                'electoral_districts': boundary_data.get('electoral_districts', []),
                'representative_assignments': boundary_data.get('representatives', []),
                'voting_precincts': boundary_data.get('voting_precincts', [])
            },
            'public_participation': {
                'comment_period_start': datetime.now().isoformat(),
                'comment_period_end': (datetime.now() + timedelta(days=jurisdiction_config['public_comment_period'])).isoformat(),
                'public_comments': [],
                'public_hearing_scheduled': boundary_data.get('public_hearing_required', False)
            },
            'created_at': datetime.now().isoformat(),
            'effective_date': boundary_data.get('effective_date'),
            'review_date': boundary_data.get('review_date'),
            'status': 'pending_public_comment',
            'version': 1.0
        }
        
        # Save Boundary Record
        db = self.load_database()
        db['jurisdictional_boundaries'].append(boundary_record)
        self.save_database(db)
        
        # Record Boundary Definition on Blockchain
        if BLOCKCHAIN_AVAILABLE and add_user_action:
            try:
                add_user_action(
                    action_type="jurisdictional_boundary_defined",
                    user_email=authority_email,
                    data={
                        'boundary_id': boundary_id,
                        'defining_authority': authority_email,
                        'jurisdiction_name': boundary_data['jurisdiction_name'],
                        'jurisdiction_level': boundary_data['jurisdiction_level'],
                        'area_sq_km': boundary_record['geographic_properties']['total_area_sq_km']
                    }
                )
            except Exception as e:
                print(f"Warning: Could not record to blockchain: {e}")
        
        return True, boundary_id


class EventLocationCoordinator:
    """Civic Event Location Management and Coordination"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize event location coordinator"""
        if db_path is None:
            db_path = os.path.join(current_dir, 'maps_db.json')
        self.db_path = db_path
        self.geographic_system = GeographicCivicEngagementSystem(db_path)
    
    def load_database(self) -> Dict:
        """Load the geographic database"""
        return self.geographic_system.load_database()
    
    def save_database(self, data: Dict):
        """Save the geographic database"""
        self.geographic_system.save_database(data)
    
    def has_event_coordination_authority(self, coordinator: Dict, event_type: str) -> bool:
        """Check if user has authority to coordinate event locations"""
        if not coordinator:
            return False
        role = coordinator.get('role', '').lower()
        # Representatives and higher can coordinate events
        return role in ['contract_founder', 'contract_elder', 'contract_senator', 'contract_representative']
    
    def search_suitable_venues(self, search_criteria: Dict) -> List[Dict]:
        """Search for suitable venues based on criteria"""
        db = self.load_database()
        venues = db.get('civic_venues', [])
        
        suitable_venues = []
        for venue in venues:
            # Check if venue meets criteria
            if venue['status'] != 'active':
                continue
            
            # Check jurisdiction match
            if 'jurisdiction' in search_criteria:
                if venue['location']['jurisdiction'] != search_criteria['jurisdiction']:
                    continue
            
            # Check capacity requirement
            if 'capacity_requirement' in search_criteria:
                if venue['capacity_information']['maximum_capacity'] < search_criteria['capacity_requirement']:
                    continue
            
            suitable_venues.append(venue)
        
        return suitable_venues
    
    def select_optimal_venue(self, suitable_venues: List[Dict], event_request: Dict, requirements: Dict) -> Dict:
        """Select the optimal venue from suitable options"""
        if not suitable_venues:
            return {}
        
        # Simple selection: return first suitable venue
        # In production, would rank by multiple factors
        return suitable_venues[0]
    
    def coordinate_event_location(self, coordinator_email: str, event_location_request: Dict) -> Tuple[bool, str]:
        """Coordinate location for civic events with accessibility and capacity management"""
        
        # Validate Event Coordination Authority
        if UserBackend:
            user_backend = UserBackend()
            coordinator = user_backend.get_user(coordinator_email)
            if not self.has_event_coordination_authority(coordinator, event_location_request.get('event_type', '')):
                return False, "Insufficient authority to coordinate event locations"
        
        # Event Location Requirements
        EVENT_LOCATION_REQUIREMENTS = {
            'town_hall_meeting': {
                'minimum_capacity': 100,
                'accessibility_required': True,
                'av_equipment_required': True,
                'parking_required': True,
                'public_transportation_preferred': True
            },
            'public_hearing': {
                'minimum_capacity': 200,
                'accessibility_required': True,
                'av_equipment_required': True,
                'recording_capability_required': True,
                'live_streaming_preferred': True
            },
            'community_meeting': {
                'minimum_capacity': 50,
                'accessibility_required': True,
                'av_equipment_required': False,
                'flexible_seating_preferred': True
            },
            'emergency_briefing': {
                'minimum_capacity': 25,
                'accessibility_required': True,
                'immediate_availability_required': True,
                'communication_equipment_required': True
            },
            'voter_registration_drive': {
                'minimum_capacity': 20,
                'accessibility_required': True,
                'high_visibility_location': True,
                'extended_hours_capability': True
            }
        }
        
        event_requirements = EVENT_LOCATION_REQUIREMENTS.get(event_location_request.get('event_type', ''))
        if not event_requirements:
            return False, "Invalid event type"
        
        # Validate required fields
        required_fields = ['event_name', 'event_type', 'event_date', 'jurisdiction']
        missing_fields = [field for field in required_fields if field not in event_location_request]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Find Suitable Venues
        venue_search_criteria = {
            'jurisdiction': event_location_request['jurisdiction'],
            'capacity_requirement': max(
                event_requirements['minimum_capacity'],
                event_location_request.get('expected_attendance', 0)
            )
        }
        
        suitable_venues = self.search_suitable_venues(venue_search_criteria)
        if not suitable_venues:
            return False, "No suitable venues available for the requested date and requirements"
        
        # Venue Selection and Optimization
        optimal_venue = self.select_optimal_venue(suitable_venues, event_location_request, event_requirements)
        
        # Create Event Location Coordination Record
        coordination_id = str(uuid.uuid4())
        location_coordination = {
            'id': coordination_id,
            'coordinator_email': coordinator_email,
            'event_details': {
                'event_name': event_location_request['event_name'],
                'event_type': event_location_request['event_type'],
                'event_date': event_location_request['event_date'],
                'expected_attendance': event_location_request.get('expected_attendance', 0),
                'duration_hours': event_location_request.get('duration_hours', 2)
            },
            'selected_venue': optimal_venue,
            'location_logistics': {
                'setup_requirements': [],
                'accessibility_accommodations': [],
                'transportation_coordination': {},
                'parking_management': {},
                'security_considerations': []
            },
            'public_notification': {
                'venue_announcement': True,
                'directions_provided': True,
                'accessibility_information': True,
                'alternative_participation_options': []
            },
            'backup_plans': {
                'weather_contingency': {},
                'capacity_overflow': {},
                'technical_failure': {}
            },
            'coordinated_at': datetime.now().isoformat(),
            'confirmation_status': 'pending_venue_confirmation',
            'resource_allocations': {}
        }
        
        # Save Location Coordination
        db = self.load_database()
        db['event_location_coordination'].append(location_coordination)
        self.save_database(db)
        
        # Record Event Location Coordination on Blockchain
        if BLOCKCHAIN_AVAILABLE and add_user_action:
            try:
                add_user_action(
                    action_type="event_location_coordinated",
                    user_email=coordinator_email,
                    data={
                        'coordination_id': coordination_id,
                        'coordinator_email': coordinator_email,
                        'event_name': event_location_request['event_name'],
                        'venue_id': optimal_venue.get('id', ''),
                        'event_date': event_location_request['event_date']
                    }
                )
            except Exception as e:
                print(f"Warning: Could not record to blockchain: {e}")
        
        return True, coordination_id


# Convenience functions for direct access
def initialize_geographic_services(admin_email: str, config: Dict) -> Tuple[bool, str]:
    """Initialize geographic services"""
    system = GeographicCivicEngagementSystem()
    return system.initialize_geographic_services(admin_email, config)


def register_civic_venue(registrar_email: str, venue_data: Dict) -> Tuple[bool, str]:
    """Register a civic venue"""
    system = GeographicCivicEngagementSystem()
    return system.register_civic_venue(registrar_email, venue_data)


def define_jurisdictional_boundaries(authority_email: str, boundary_data: Dict) -> Tuple[bool, str]:
    """Define jurisdictional boundaries"""
    manager = JurisdictionalBoundaryManager()
    return manager.define_jurisdictional_boundaries(authority_email, boundary_data)


def coordinate_event_location(coordinator_email: str, event_request: Dict) -> Tuple[bool, str]:
    """Coordinate event location"""
    coordinator = EventLocationCoordinator()
    return coordinator.coordinate_event_location(coordinator_email, event_request)


if __name__ == '__main__':
    print("Geographic Civic Engagement System - Location Services Module")
    print("=" * 70)
    
    # Test initialization
    system = GeographicCivicEngagementSystem()
    print(f"✓ Database initialized at: {system.db_path}")
    
    # Test database structure
    db = system.load_database()
    print(f"✓ Database loaded with {len(db.get('civic_venues', []))} venues")
    print(f"✓ Database loaded with {len(db.get('jurisdictional_boundaries', []))} boundaries")
    print(f"✓ Database loaded with {len(db.get('event_location_coordination', []))} coordinated events")
    
    print("\nLocation Services Module ready!")
