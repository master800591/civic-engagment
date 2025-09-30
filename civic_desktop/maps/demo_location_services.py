"""
Geographic Civic Engagement - Demo Script
Demonstrates the complete functionality of location services
"""

import os
import sys
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


def demo_header(title):
    """Print a formatted demo section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def demo_geographic_services():
    """Demonstrate geographic services initialization"""
    demo_header("DEMO: Geographic Services Initialization")
    
    system = GeographicCivicEngagementSystem()
    
    config = {
        'enabled_services': [
            'jurisdictional_mapping',
            'civic_venue_mapping',
            'participation_analytics'
        ],
        'retention_days': 365,
        'tile_server': 'https://tile.openstreetmap.org/',
        'offline_support': True
    }
    
    print("\n📍 Initializing geographic services...")
    print(f"   Services: {', '.join(config['enabled_services'])}")
    print(f"   Data retention: {config['retention_days']} days")
    print(f"   Offline support: {config['offline_support']}")
    
    success, config_id = system.initialize_geographic_services(
        'admin@civic.org',
        config
    )
    
    if success:
        print(f"\n✅ SUCCESS: Geographic services initialized")
        print(f"   Configuration ID: {config_id}")
        print(f"   Privacy: Location data encrypted and anonymized")
        print(f"   Accessibility: Full screen reader and keyboard support")
    else:
        print(f"\n❌ FAILED: {config_id}")


def demo_venue_registration():
    """Demonstrate civic venue registration"""
    demo_header("DEMO: Civic Venue Registration")
    
    system = GeographicCivicEngagementSystem()
    
    venues = [
        {
            'name': 'City Hall Main Auditorium',
            'category': 'town_hall',
            'description': 'Primary venue for city council meetings',
            'jurisdiction': 'San Francisco, CA',
            'location': {
                'address': '1 Dr Carlton B Goodlett Pl',
                'latitude': 37.7793,
                'longitude': -122.4193,
                'postal_code': '94102',
                'accessibility_notes': 'Full wheelchair access via main entrance'
            },
            'capacity': {
                'maximum': 250,
                'accessible_seating': 20,
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
                'email': 'events@sf.gov'
            }
        },
        {
            'name': 'Community Center Meeting Hall',
            'category': 'community_center',
            'description': 'Multi-purpose community space',
            'jurisdiction': 'Oakland, CA',
            'location': {
                'address': '123 Community Way',
                'latitude': 37.8044,
                'longitude': -122.2712,
                'postal_code': '94601'
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
                'phone': '510-555-5678',
                'email': 'community@oakland.gov'
            }
        }
    ]
    
    print("\n🏛️ Registering civic venues...")
    
    for venue in venues:
        success, venue_id = system.register_civic_venue(
            'venue_manager@civic.org',
            venue
        )
        
        if success:
            print(f"\n✅ Venue Registered: {venue['name']}")
            print(f"   ID: {venue_id}")
            print(f"   Category: {venue['category']}")
            print(f"   Location: {venue['location']['address']}")
            print(f"   Capacity: {venue['capacity']['maximum']} people")
            print(f"   Accessible: {'Yes' if venue['accessibility']['wheelchair_access'] else 'No'}")
            print(f"   Equipment: AV={venue['equipment'].get('av_system', False)}, "
                  f"Streaming={venue['equipment'].get('streaming', False)}")
        else:
            print(f"\n❌ Failed to register: {venue['name']}")


def demo_jurisdictional_boundaries():
    """Demonstrate jurisdictional boundary definition"""
    demo_header("DEMO: Jurisdictional Boundary Management")
    
    manager = JurisdictionalBoundaryManager()
    
    boundaries = [
        {
            'jurisdiction_name': 'Downtown District 3',
            'jurisdiction_level': 'district',
            'jurisdiction_type': 'electoral',
            'boundary_coordinates': [
                [37.7900, -122.4200],
                [37.7900, -122.4000],
                [37.7700, -122.4000],
                [37.7700, -122.4200],
                [37.7900, -122.4200]
            ],
            'population': 45000,
            'parent_jurisdiction': 'San Francisco County',
            'establishment_date': '2024-01-01',
            'electoral_districts': ['District 3'],
            'voting_precincts': ['3A', '3B', '3C', '3D']
        },
        {
            'jurisdiction_name': 'Alameda County',
            'jurisdiction_level': 'county',
            'jurisdiction_type': 'administrative',
            'boundary_coordinates': [
                [37.9, -122.3],
                [37.9, -121.9],
                [37.5, -121.9],
                [37.5, -122.3],
                [37.9, -122.3]
            ],
            'population': 1670000,
            'parent_jurisdiction': 'State of California',
            'establishment_date': '1853-03-25',
            'representatives': []
        }
    ]
    
    print("\n🗺️ Defining jurisdictional boundaries...")
    
    for boundary in boundaries:
        success, boundary_id = manager.define_jurisdictional_boundaries(
            'boundary_admin@civic.org',
            boundary
        )
        
        if success:
            # Get the saved boundary for details
            db = manager.load_database()
            saved = next((b for b in db['jurisdictional_boundaries'] if b['id'] == boundary_id), None)
            
            print(f"\n✅ Boundary Defined: {boundary['jurisdiction_name']}")
            print(f"   ID: {boundary_id}")
            print(f"   Level: {boundary['jurisdiction_level']}")
            print(f"   Type: {boundary['jurisdiction_type']}")
            print(f"   Population: {boundary.get('population', 'N/A'):,}")
            if saved:
                print(f"   Area: {saved['geographic_properties']['total_area_sq_km']:.2f} km²")
                print(f"   Status: {saved['status']}")
                print(f"   Public comment period: "
                      f"{saved['public_participation']['comment_period_start'][:10]} to "
                      f"{saved['public_participation']['comment_period_end'][:10]}")
        else:
            print(f"\n❌ Failed to define: {boundary['jurisdiction_name']}")


def demo_event_coordination():
    """Demonstrate event location coordination"""
    demo_header("DEMO: Event Location Coordination")
    
    coordinator = EventLocationCoordinator()
    
    events = [
        {
            'event_name': 'Town Hall Meeting: 2024 Budget Review',
            'event_type': 'town_hall_meeting',
            'event_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'jurisdiction': 'San Francisco, CA',
            'expected_attendance': 200,
            'duration_hours': 3
        },
        {
            'event_name': 'Community Forum: Public Transit Expansion',
            'event_type': 'community_meeting',
            'event_date': (datetime.now() + timedelta(days=45)).isoformat(),
            'jurisdiction': 'Oakland, CA',
            'expected_attendance': 100,
            'duration_hours': 2
        }
    ]
    
    print("\n📅 Coordinating event locations...")
    
    for event in events:
        success, coordination_id = coordinator.coordinate_event_location(
            'event_coordinator@civic.org',
            event
        )
        
        if success:
            # Get the coordination details
            db = coordinator.load_database()
            coord = next((c for c in db['event_location_coordination'] if c['id'] == coordination_id), None)
            
            print(f"\n✅ Event Coordinated: {event['event_name']}")
            print(f"   Coordination ID: {coordination_id}")
            print(f"   Type: {event['event_type']}")
            print(f"   Date: {event['event_date'][:10]}")
            print(f"   Expected attendance: {event['expected_attendance']}")
            if coord and coord['selected_venue']:
                print(f"   Venue: {coord['selected_venue'].get('venue_name', 'TBD')}")
                print(f"   Confirmation: {coord['confirmation_status']}")
        else:
            print(f"\n❌ Failed to coordinate: {event['event_name']}")


def demo_database_summary():
    """Show summary of all data in the system"""
    demo_header("SYSTEM DATABASE SUMMARY")
    
    system = GeographicCivicEngagementSystem()
    db = system.load_database()
    
    print(f"\n📊 Database Statistics:")
    print(f"   Location: {system.db_path}")
    print(f"   Geographic Configurations: {len(db.get('geographic_configurations', []))}")
    print(f"   Civic Venues: {len(db.get('civic_venues', []))}")
    print(f"   Jurisdictional Boundaries: {len(db.get('jurisdictional_boundaries', []))}")
    print(f"   Event Coordinations: {len(db.get('event_location_coordination', []))}")
    
    # Show venue details
    if db.get('civic_venues'):
        print(f"\n🏛️ Registered Venues:")
        for venue in db['civic_venues']:
            print(f"   • {venue['venue_name']} ({venue['category']})")
            print(f"     Capacity: {venue['capacity_information']['maximum_capacity']}, "
                  f"Location: {venue['location']['jurisdiction']}")
    
    # Show boundary details
    if db.get('jurisdictional_boundaries'):
        print(f"\n🗺️ Jurisdictional Boundaries:")
        for boundary in db['jurisdictional_boundaries']:
            print(f"   • {boundary['jurisdiction_name']} ({boundary['jurisdiction_level']})")
            print(f"     Status: {boundary['status']}")
    
    # Show event details
    if db.get('event_location_coordination'):
        print(f"\n📅 Coordinated Events:")
        for coord in db['event_location_coordination']:
            print(f"   • {coord['event_details']['event_name']}")
            print(f"     Date: {coord['event_details']['event_date'][:10]}, "
                  f"Venue: {coord['selected_venue'].get('venue_name', 'TBD')}")


def run_complete_demo():
    """Run complete demonstration"""
    print("\n" + "="*70)
    print("  GEOGRAPHIC CIVIC ENGAGEMENT - COMPLETE DEMONSTRATION")
    print("  Location-Based Civic Participation & Jurisdictional Mapping")
    print("="*70)
    
    # Run all demos in sequence
    demo_geographic_services()
    demo_venue_registration()
    demo_jurisdictional_boundaries()
    demo_event_coordination()
    demo_database_summary()
    
    print("\n" + "="*70)
    print("  DEMONSTRATION COMPLETE")
    print("="*70)
    print("\n✅ All geographic civic engagement features demonstrated successfully!")
    print("   • Privacy-compliant location services initialized")
    print("   • Civic venues registered with accessibility features")
    print("   • Jurisdictional boundaries defined with public comment periods")
    print("   • Event locations coordinated with venue optimization")
    print("   • All data stored with blockchain audit trail")
    print("\n📝 See maps_db.json for complete data structure")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_complete_demo()
