"""
Integration Test for Maps Module
Tests that map_view.py properly integrates with location_services.py
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_imports():
    """Test that all imports work correctly"""
    print("\n" + "="*70)
    print("TEST: Module Imports")
    print("="*70)
    
    try:
        from maps.location_services import (
            GeographicCivicEngagementSystem,
            JurisdictionalBoundaryManager,
            EventLocationCoordinator
        )
        print("✓ location_services imports successful")
        
        # Test instantiation
        geo_system = GeographicCivicEngagementSystem()
        boundary_mgr = JurisdictionalBoundaryManager()
        event_coord = EventLocationCoordinator()
        print("✓ All classes instantiate successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def test_map_view_imports():
    """Test that map_view.py imports work"""
    print("\n" + "="*70)
    print("TEST: MapView Module Imports")
    print("="*70)
    
    try:
        # This will test if the file compiles and imports work
        import maps.map_view
        print("✓ map_view.py imports successfully")
        return True
    except Exception as e:
        print(f"✗ Map view import error: {e}")
        return False


def test_database_compatibility():
    """Test that database operations work correctly"""
    print("\n" + "="*70)
    print("TEST: Database Compatibility")
    print("="*70)
    
    try:
        from maps.location_services import GeographicCivicEngagementSystem
        
        system = GeographicCivicEngagementSystem()
        db = system.load_database()
        
        # Check structure
        required_keys = [
            'geographic_configurations',
            'civic_venues',
            'jurisdictional_boundaries',
            'event_location_coordination'
        ]
        
        for key in required_keys:
            if key not in db:
                print(f"✗ Missing database key: {key}")
                return False
        
        print("✓ Database structure is correct")
        print(f"✓ Database path: {system.db_path}")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_api_functions():
    """Test convenience API functions"""
    print("\n" + "="*70)
    print("TEST: API Functions")
    print("="*70)
    
    try:
        from maps.location_services import (
            initialize_geographic_services,
            register_civic_venue,
            define_jurisdictional_boundaries,
            coordinate_event_location
        )
        print("✓ All API functions importable")
        print("  - initialize_geographic_services")
        print("  - register_civic_venue")
        print("  - define_jurisdictional_boundaries")
        print("  - coordinate_event_location")
        
        return True
    except Exception as e:
        print(f"✗ API function error: {e}")
        return False


def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("MAPS MODULE - INTEGRATION TEST SUITE")
    print("="*70)
    
    results = {
        'Module Imports': test_imports(),
        'MapView Imports': test_map_view_imports(),
        'Database Compatibility': test_database_compatibility(),
        'API Functions': test_api_functions()
    }
    
    print("\n" + "="*70)
    print("INTEGRATION TEST RESULTS")
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
    success = run_integration_tests()
    sys.exit(0 if success else 1)
