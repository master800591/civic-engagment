"""
GENESIS DATA INTEGRATION TEST
Test and populate the government directory with comprehensive real-world data
Demonstrates the complete government officials database functionality
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add the civic_desktop path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from government.genesis_government_data import GenesisGovernmentDataLoader
    from government.government_directory import GovernmentDirectoryManager
    print("✅ Successfully imported government modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Running without imports - creating data directly")


def test_genesis_data_creation():
    """Test creating and loading genesis government data"""
    
    print("🌍 GENESIS GOVERNMENT DATA INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize the data loader
    try:
        loader = GenesisGovernmentDataLoader()
        print("✅ GenesisGovernmentDataLoader initialized")
        
        # Create comprehensive government data
        print("\n📊 Populating Genesis Government Data...")
        genesis_data = loader.populate_genesis_data()
        
        print(f"\n🎉 Genesis Data Successfully Created!")
        print(f"📈 Total Officials: {genesis_data['statistics']['total_officials']}")
        print(f"🏛️ Country Leaders: {genesis_data['statistics']['by_level']['country']}")
        print(f"🏢 State/Province Leaders: {genesis_data['statistics']['by_level']['state']}")
        print(f"🏘️ City Leaders: {genesis_data['statistics']['by_level']['city']}")
        
        # Display sample data
        print("\n🔍 SAMPLE GOVERNMENT OFFICIALS:")
        print("-" * 40)
        
        sample_officials = list(genesis_data['officials'].items())[:10]
        for official_id, official_data in sample_officials:
            print(f"👤 {official_data['name']} - {official_data['title']}")
            print(f"   📧 {official_data.get('email', 'No email')}")
            print(f"   📞 {official_data.get('phone', 'No phone')}")
            print(f"   🌍 {official_data['jurisdiction']} ({official_data['jurisdiction_level']})")
            print(f"   ✅ Status: {official_data['verification_status']}")
            print()
        
        return True, genesis_data
        
    except Exception as e:
        print(f"❌ Error creating genesis data: {e}")
        return False, None


def test_government_directory_integration():
    """Test integration with the government directory manager"""
    
    print("\n🏛️ GOVERNMENT DIRECTORY INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Initialize the directory manager
        directory_manager = GovernmentDirectoryManager()
        print("✅ GovernmentDirectoryManager initialized")
        
        # Get statistics
        total_officials = directory_manager.get_total_officials()
        print(f"📊 Total Officials in Directory: {total_officials}")
        
        # Test getting officials by level
        country_officials = directory_manager.get_officials_by_level('country')
        state_officials = directory_manager.get_officials_by_level('state') 
        city_officials = directory_manager.get_officials_by_level('city')
        
        print(f"🏛️ Country Level Officials: {len(country_officials)}")
        print(f"🏢 State Level Officials: {len(state_officials)}")
        print(f"🏘️ City Level Officials: {len(city_officials)}")
        
        # Test getting officials by country
        us_officials = directory_manager.get_officials_by_country('United States')
        uk_officials = directory_manager.get_officials_by_country('United Kingdom')
        
        print(f"🇺🇸 US Officials: {len(us_officials)}")
        print(f"🇬🇧 UK Officials: {len(uk_officials)}")
        
        # Test getting uncontacted officials
        uncontacted = directory_manager.get_uncontacted_officials()
        print(f"📞 Uncontacted Officials: {len(uncontacted)}")
        
        # Display key officials
        print("\n🌟 KEY WORLD LEADERS:")
        print("-" * 30)
        
        key_officials = [
            ('usa_president', 'President Biden'),
            ('uk_prime_minister', 'PM Sunak'),
            ('germany_chancellor', 'Chancellor Scholz'),
            ('france_president', 'President Macron'),
            ('japan_prime_minister', 'PM Kishida'),
            ('canada_prime_minister', 'PM Trudeau')
        ]
        
        for official_id, display_name in key_officials:
            official = directory_manager.get_official_by_id(official_id)
            if official:
                print(f"✅ {display_name}: {official.get('email', 'No email')}")
            else:
                print(f"❌ {display_name}: Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing directory integration: {e}")
        return False


def create_demo_outreach_campaign():
    """Create a demonstration outreach campaign"""
    
    print("\n📧 DEMO OUTREACH CAMPAIGN CREATION")
    print("=" * 60)
    
    try:
        directory_manager = GovernmentDirectoryManager()
        
        # Create sample outreach campaign
        campaign_data = {
            'campaign_id': f"genesis_outreach_{datetime.now().strftime('%Y%m%d')}",
            'name': 'Genesis Platform Invitation Campaign',
            'description': 'Initial outreach to world government leaders for civic engagement platform',
            'target_audience': 'world_leaders',
            'priority_levels': ['critical', 'high', 'medium'],
            'start_date': datetime.now().isoformat(),
            'status': 'planned',
            'template_type': 'initial_invitation',
            'follow_up_schedule': '7_14_30_days'
        }
        
        # Get target officials for outreach
        all_officials = directory_manager.get_uncontacted_officials()
        
        # Prioritize by population and significance
        priority_officials = []
        high_priority_officials = []
        medium_priority_officials = []
        
        for official in all_officials:
            population = official.get('population_served', 0)
            priority = official.get('priority', 'low')
            
            if priority == 'critical' or population > 100000000:
                priority_officials.append(official)
            elif priority == 'high' or population > 10000000:
                high_priority_officials.append(official)
            else:
                medium_priority_officials.append(official)
        
        print(f"🎯 OUTREACH CAMPAIGN TARGETS:")
        print(f"   🚨 Critical Priority: {len(priority_officials)} officials")
        print(f"   ⚡ High Priority: {len(high_priority_officials)} officials") 
        print(f"   📋 Medium Priority: {len(medium_priority_officials)} officials")
        print(f"   📊 Total Targets: {len(all_officials)} officials")
        
        # Display first wave targets
        print(f"\n🌟 FIRST WAVE CRITICAL TARGETS:")
        print("-" * 35)
        
        for official in priority_officials[:10]:
            print(f"👤 {official['name']} - {official['title']}")
            print(f"   📧 {official.get('email', 'No email')}")
            print(f"   👥 Population: {official.get('population_served', 'N/A'):,}")
            print()
        
        return True, campaign_data
        
    except Exception as e:
        print(f"❌ Error creating outreach campaign: {e}")
        return False, None


def display_comprehensive_statistics():
    """Display comprehensive statistics about the genesis data"""
    
    print("\n📈 COMPREHENSIVE GENESIS DATA STATISTICS")
    print("=" * 60)
    
    try:
        directory_manager = GovernmentDirectoryManager()
        
        # Get all officials data
        officials_data = directory_manager._load_json(directory_manager.officials_db)
        
        if 'statistics' in officials_data:
            stats = officials_data['statistics']
            
            print("🌍 BY JURISDICTION LEVEL:")
            for level, count in stats['by_level'].items():
                print(f"   {level.title()}: {count:,} officials")
            
            print("\n🌎 BY COUNTRY:")
            sorted_countries = sorted(stats['by_country'].items(), 
                                    key=lambda x: x[1], reverse=True)
            for country, count in sorted_countries[:15]:
                print(f"   {country}: {count:,} officials")
            
            print("\n📞 BY VERIFICATION STATUS:")
            for status, count in stats['by_status'].items():
                print(f"   {status.replace('_', ' ').title()}: {count:,} officials")
            
            print(f"\n📊 TOTAL DATABASE SIZE: {stats['total_officials']:,} government officials")
        
        return True
        
    except Exception as e:
        print(f"❌ Error displaying statistics: {e}")
        return False


def main():
    """Main test execution function"""
    
    print("🚀 GENESIS GOVERNMENT DATA INTEGRATION TEST SUITE")
    print("=" * 70)
    print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Genesis Data Creation
    success, genesis_data = test_genesis_data_creation()
    if success:
        tests_passed += 1
        print("✅ Test 1 PASSED: Genesis Data Creation")
    else:
        print("❌ Test 1 FAILED: Genesis Data Creation")
    
    # Test 2: Directory Integration
    success = test_government_directory_integration()
    if success:
        tests_passed += 1
        print("✅ Test 2 PASSED: Directory Integration")
    else:
        print("❌ Test 2 FAILED: Directory Integration")
    
    # Test 3: Outreach Campaign
    success, campaign_data = create_demo_outreach_campaign()
    if success:
        tests_passed += 1
        print("✅ Test 3 PASSED: Outreach Campaign Creation")
    else:
        print("❌ Test 3 FAILED: Outreach Campaign Creation")
    
    # Test 4: Statistics Display
    success = display_comprehensive_statistics()
    if success:
        tests_passed += 1
        print("✅ Test 4 PASSED: Statistics Display")
    else:
        print("❌ Test 4 FAILED: Statistics Display")
    
    # Test 5: Data Verification
    try:
        data_path = Path(__file__).parent / 'government_directory' / 'government_officials_directory.json'
        if data_path.exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if len(data.get('officials', {})) > 50:
                tests_passed += 1
                print("✅ Test 5 PASSED: Data File Verification")
            else:
                print("❌ Test 5 FAILED: Insufficient data in file")
        else:
            print("❌ Test 5 FAILED: Data file not found")
    except Exception as e:
        print(f"❌ Test 5 FAILED: Data verification error: {e}")
    
    # Final Results
    print("\n" + "=" * 70)
    print(f"🎯 TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Genesis Government Data Successfully Populated!")
    elif tests_passed >= 3:
        print("⚠️  Most tests passed. Genesis data is functional with minor issues.")
    else:
        print("❌ Multiple test failures. Genesis data population needs attention.")
    
    print(f"⏰ Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌍 Ready for government outreach and platform onboarding!")


if __name__ == "__main__":
    main()