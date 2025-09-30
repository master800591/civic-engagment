"""
Test Geographic Civic Engagement and Jurisdictional Mapping
Tests location services, venue registration, boundary management, and event coordination
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from maps.location_services import (
    GeographicCivicEngagementSystem,
    JurisdictionalBoundaryManager,
    EventLocationCoordinator
)


def test_geographic_services_initialization():
    """Test initializing geographic services"""
    print("\n" + "="*70)
    print("TEST: Geographic Services Initialization")
    print("="*70)
    
    system = GeographicCivicEngagementSystem()
    
    # Test configuration
    config = {
        'enabled_services': ['jurisdictional_mapping', 'civic_venue_mapping'],
        'retention_days': 365,
        'offline_support': True
    }
    
    # Initialize services (without user validation for testing)
    success, config_id = system.initialize_geographic_services(
        'test_admin@civic.org',
        config
    )
    
    if success:
        print(f"✓ Geographic services initialized successfully")
        print(f"  Configuration ID: {config_id}")
        
        # Verify in database
        db = system.load_database()
        configs = db.get('geographic_configurations', [])
        print(f"✓ Configuration saved to database ({len(configs)} total)")
        
        return True
    else:
        print(f"✗ Failed to initialize services: {config_id}")
        return False


def test_civic_venue_registration():
    """Test registering a civic venue"""
    print("\n" + "="*70)
    print("TEST: Civic Venue Registration")
    print("="*70)
    
    system = GeographicCivicEngagementSystem()
    
    # Test venue data
    venue_data = {
        'name': 'City Hall Main Auditorium',
        'category': 'town_hall',
        'description': 'Primary venue for city council meetings and public hearings',
        'jurisdiction': 'San Francisco, CA',
        'location': {
            'address': '1 Dr Carlton B Goodlett Pl',
            'latitude': 37.7793,
            'longitude': -122.4193,
            'postal_code': '94102',
            'accessibility_notes': 'Full wheelchair access, accessible parking available'
        },
        'capacity': {
            'maximum': 250,
            'accessible_seating': 20,
            'standing_capacity': 50,
            'parking': True
        },
        'equipment': {
            'av_system': True,
            'sound_system': True,
            'projection': True,
            'wifi': True,
            'streaming': True
        },
        'accessibility': {
            'wheelchair_access': True,
            'accessible_parking': True,
            'hearing_loop': True,
            'visual_aids': True,
            'service_animals': True
        },
        'contact': {
            'primary_contact': 'City Events Coordinator',
            'phone': '415-555-1234',
            'email': 'events@sf.gov',
            'emergency_contact': '415-555-9999'
        }
    }
    
    # Register venue (without user validation for testing)
    success, venue_id = system.register_civic_venue(
        'venue_manager@civic.org',
        venue_data
    )
    
    if success:
        print(f"✓ Civic venue registered successfully")
        print(f"  Venue ID: {venue_id}")
        print(f"  Name: {venue_data['name']}")
        print(f"  Category: {venue_data['category']}")
        print(f"  Capacity: {venue_data['capacity']['maximum']}")
        
        # Verify in database
        db = system.load_database()
        venues = db.get('civic_venues', [])
        print(f"✓ Venue saved to database ({len(venues)} total)")
        
        # Verify venue details
        saved_venue = next((v for v in venues if v['id'] == venue_id), None)
        if saved_venue:
            print(f"✓ Venue verification:")
            print(f"  - Wheelchair accessible: {saved_venue['accessibility_features']['wheelchair_accessible']}")
            print(f"  - AV equipment: {saved_venue['facilities_equipment']['av_equipment']}")
            print(f"  - Status: {saved_venue['status']}")
        
        return True
    else:
        print(f"✗ Failed to register venue: {venue_id}")
        return False


def test_jurisdictional_boundary_definition():
    """Test defining jurisdictional boundaries"""
    print("\n" + "="*70)
    print("TEST: Jurisdictional Boundary Definition")
    print("="*70)
    
    manager = JurisdictionalBoundaryManager()
    
    # Test boundary data
    boundary_data = {
        'jurisdiction_name': 'Downtown District',
        'jurisdiction_level': 'district',
        'jurisdiction_type': 'electoral',
        'boundary_coordinates': [
            [37.7900, -122.4200],
            [37.7900, -122.4000],
            [37.7700, -122.4000],
            [37.7700, -122.4200],
            [37.7900, -122.4200]  # Close the polygon
        ],
        'coordinate_system': 'WGS84',
        'population': 45000,
        'parent_jurisdiction': 'San Francisco County',
        'establishment_date': '2024-01-01',
        'legal_authority': 'City Charter Section 4.5',
        'electoral_districts': ['District 3', 'District 6'],
        'representatives': [],
        'voting_precincts': ['3A', '3B', '6A', '6B'],
        'effective_date': '2024-01-01',
        'public_hearing_required': False
    }
    
    # Define boundary (without user validation for testing)
    success, boundary_id = manager.define_jurisdictional_boundaries(
        'boundary_admin@civic.org',
        boundary_data
    )
    
    if success:
        print(f"✓ Jurisdictional boundary defined successfully")
        print(f"  Boundary ID: {boundary_id}")
        print(f"  Jurisdiction: {boundary_data['jurisdiction_name']}")
        print(f"  Level: {boundary_data['jurisdiction_level']}")
        
        # Verify in database
        db = manager.load_database()
        boundaries = db.get('jurisdictional_boundaries', [])
        print(f"✓ Boundary saved to database ({len(boundaries)} total)")
        
        # Verify boundary details
        saved_boundary = next((b for b in boundaries if b['id'] == boundary_id), None)
        if saved_boundary:
            print(f"✓ Boundary verification:")
            print(f"  - Area: {saved_boundary['geographic_properties']['total_area_sq_km']:.2f} km²")
            print(f"  - Perimeter: {saved_boundary['geographic_properties']['perimeter_km']:.2f} km")
            print(f"  - Status: {saved_boundary['status']}")
            print(f"  - Comment period: {saved_boundary['public_participation']['comment_period_start'][:10]} to {saved_boundary['public_participation']['comment_period_end'][:10]}")
        
        return True
    else:
        print(f"✗ Failed to define boundary: {boundary_id}")
        return False


def test_event_location_coordination():
    """Test coordinating event location"""
    print("\n" + "="*70)
    print("TEST: Event Location Coordination")
    print("="*70)
    
    # First, register a venue for the event
    system = GeographicCivicEngagementSystem()
    venue_data = {
        'name': 'Community Center Meeting Room',
        'category': 'community_center',
        'description': 'Multi-purpose meeting space',
        'jurisdiction': 'San Francisco, CA',
        'location': {
            'address': '456 Community St',
            'latitude': 37.7750,
            'longitude': -122.4150,
            'postal_code': '94103'
        },
        'capacity': {
            'maximum': 150,
            'accessible_seating': 15,
            'parking': True
        },
        'equipment': {
            'av_system': True,
            'sound_system': True
        },
        'accessibility': {
            'wheelchair_access': True,
            'accessible_parking': True
        },
        'contact': {
            'primary_contact': 'Community Manager',
            'phone': '415-555-5678',
            'email': 'community@sf.gov'
        }
    }
    system.register_civic_venue('venue_manager@civic.org', venue_data)
    
    # Now coordinate an event
    coordinator = EventLocationCoordinator()
    
    # Test event request
    event_request = {
        'event_name': 'Town Hall Meeting on Budget 2024',
        'event_type': 'town_hall_meeting',
        'event_date': (datetime.now() + timedelta(days=30)).isoformat(),
        'jurisdiction': 'San Francisco, CA',
        'expected_attendance': 120,
        'duration_hours': 3
    }
    
    # Coordinate event (without user validation for testing)
    success, coordination_id = coordinator.coordinate_event_location(
        'event_coordinator@civic.org',
        event_request
    )
    
    if success:
        print(f"✓ Event location coordinated successfully")
        print(f"  Coordination ID: {coordination_id}")
        print(f"  Event: {event_request['event_name']}")
        print(f"  Type: {event_request['event_type']}")
        print(f"  Date: {event_request['event_date'][:10]}")
        
        # Verify in database
        db = coordinator.load_database()
        coordinations = db.get('event_location_coordination', [])
        print(f"✓ Coordination saved to database ({len(coordinations)} total)")
        
        # Verify coordination details
        saved_coord = next((c for c in coordinations if c['id'] == coordination_id), None)
        if saved_coord:
            print(f"✓ Coordination verification:")
            print(f"  - Venue: {saved_coord['selected_venue'].get('venue_name', 'N/A')}")
            print(f"  - Expected attendance: {saved_coord['event_details']['expected_attendance']}")
            print(f"  - Status: {saved_coord['confirmation_status']}")
        
        return True
    else:
        print(f"✗ Failed to coordinate event: {coordination_id}")
        return False


def test_database_structure():
    """Test database structure and integrity"""
    print("\n" + "="*70)
    print("TEST: Database Structure and Integrity")
    print("="*70)
    
    system = GeographicCivicEngagementSystem()
    db = system.load_database()
    
    # Check required tables
    required_tables = [
        'geographic_configurations',
        'civic_venues',
        'jurisdictional_boundaries',
        'event_location_coordination'
    ]
    
    all_present = True
    for table in required_tables:
        if table in db:
            print(f"✓ Table '{table}' present with {len(db[table])} records")
        else:
            print(f"✗ Table '{table}' missing!")
            all_present = False
    
    return all_present


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("GEOGRAPHIC CIVIC ENGAGEMENT - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = {
        'Database Structure': test_database_structure(),
        'Geographic Services Init': test_geographic_services_initialization(),
        'Civic Venue Registration': test_civic_venue_registration(),
        'Jurisdictional Boundaries': test_jurisdictional_boundary_definition(),
        'Event Location Coordination': test_event_location_coordination()
    }
    
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*70)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
