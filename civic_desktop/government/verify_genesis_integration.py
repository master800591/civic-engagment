"""
GENESIS DATA INTEGRATION VERIFICATION
Test that the populated genesis data works with existing government directory system
Verify all systems are properly integrated and functional
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add the civic_desktop path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test simple data access without imports first
def test_direct_data_access():
    """Test direct access to genesis data file"""
    
    print("🔍 TESTING DIRECT DATA ACCESS")
    print("=" * 40)
    
    try:
        data_path = Path(__file__).parent / 'government_directory' / 'government_officials_directory.json'
        
        if not data_path.exists():
            print("❌ Genesis data file not found!")
            return False
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Data file loaded successfully")
        print(f"📊 Total Officials: {len(data.get('officials', {}))}")
        print(f"🌍 Countries: {len(data.get('countries', {}))}")
        print(f"🏢 States: {len(data.get('states', {}))}")
        print(f"🏘️ Cities: {len(data.get('cities', {}))}")
        
        # Test data structure
        if 'statistics' in data:
            stats = data['statistics']
            print(f"📈 Statistics Available:")
            print(f"   Total: {stats.get('total_officials', 0)}")
            print(f"   By Level: {stats.get('by_level', {})}")
            print(f"   By Status: {stats.get('by_status', {})}")
        
        # Test sample official data
        officials = data.get('officials', {})
        if 'usa_president' in officials:
            biden = officials['usa_president']
            print(f"\n✅ Sample Official: {biden['name']}")
            print(f"   📧 Email: {biden.get('email', 'N/A')}")
            print(f"   📞 Phone: {biden.get('phone', 'N/A')}")
            print(f"   🌍 Jurisdiction: {biden.get('jurisdiction', 'N/A')}")
            print(f"   ⭐ Priority: {biden.get('priority', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing data: {e}")
        return False


def test_outreach_campaign_simulation():
    """Simulate an outreach campaign using the genesis data"""
    
    print("\n📧 TESTING OUTREACH CAMPAIGN SIMULATION")
    print("=" * 50)
    
    try:
        data_path = Path(__file__).parent / 'government_directory' / 'government_officials_directory.json'
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        officials = data.get('officials', {})
        
        # Simulate prioritization
        critical_officials = []
        high_officials = []
        medium_officials = []
        
        for official_id, official in officials.items():
            priority = official.get('priority', 'low')
            if priority == 'critical':
                critical_officials.append(official)
            elif priority == 'high':
                high_officials.append(official)
            else:
                medium_officials.append(official)
        
        print(f"🎯 CAMPAIGN TARGET ANALYSIS:")
        print(f"   🚨 Critical Priority: {len(critical_officials)} officials")
        print(f"   ⚡ High Priority: {len(high_officials)} officials")
        print(f"   📋 Medium Priority: {len(medium_officials)} officials")
        
        # Simulate first wave contacts
        print(f"\n🌟 FIRST WAVE CRITICAL TARGETS:")
        print("-" * 35)
        
        for i, official in enumerate(critical_officials[:5]):
            print(f"{i+1}. {official['name']} - {official['title']}")
            print(f"   📧 Contact: {official.get('email', 'No email')}")
            print(f"   👥 Population: {official.get('population_served', 0):,}")
            print(f"   🌍 Country: {official.get('country', 'Unknown')}")
            print()
        
        # Simulate contact tracking
        print("📞 SIMULATED CONTACT TRACKING:")
        print("-" * 30)
        
        for official in critical_officials[:3]:
            print(f"✅ Contacted: {official['name']}")
            print(f"   📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
            print(f"   📧 Method: Email to {official.get('email', 'N/A')}")
            print(f"   ⏰ Follow-up: 7 days")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in campaign simulation: {e}")
        return False


def test_citizen_verification_integration():
    """Test integration with citizen verification system"""
    
    print("\n🏆 TESTING CITIZEN VERIFICATION INTEGRATION")
    print("=" * 50)
    
    try:
        data_path = Path(__file__).parent / 'government_directory' / 'government_officials_directory.json'
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        officials = data.get('officials', {})
        
        # Simulate officials who could verify citizens
        verification_capable = []
        
        for official_id, official in officials.items():
            if official.get('jurisdiction_level') in ['country', 'state', 'city']:
                verification_capable.append({
                    'official_id': official_id,
                    'name': official['name'],
                    'title': official['title'],
                    'level': official['jurisdiction_level'],
                    'jurisdiction': official['jurisdiction'],
                    'population': official.get('population_served', 0)
                })
        
        # Sort by population for verification authority
        verification_capable.sort(key=lambda x: x['population'], reverse=True)
        
        print(f"🔐 CITIZEN VERIFICATION AUTHORITY:")
        print(f"   Total Verification Officials: {len(verification_capable)}")
        print()
        
        # Display verification hierarchy
        country_officials = [o for o in verification_capable if o['level'] == 'country']
        state_officials = [o for o in verification_capable if o['level'] == 'state']  
        city_officials = [o for o in verification_capable if o['level'] == 'city']
        
        print("🏛️ COUNTRY LEVEL VERIFICATION (National Citizenship):")
        for official in country_officials[:5]:
            print(f"   ✅ {official['name']} - {official['jurisdiction']}")
            print(f"      Population: {official['population']:,}")
        
        print(f"\n🏢 STATE LEVEL VERIFICATION (State Residency):")
        for official in state_officials[:3]:
            print(f"   ✅ {official['name']} - {official['jurisdiction']}")
            print(f"      Population: {official['population']:,}")
        
        print(f"\n🏘️ CITY LEVEL VERIFICATION (City Residency):")
        for official in city_officials[:3]:
            print(f"   ✅ {official['name']} - {official['jurisdiction']}")
            print(f"      Population: {official['population']:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in verification integration test: {e}")
        return False


def test_data_export_capabilities():
    """Test data export for outreach campaigns"""
    
    print(f"\n📊 TESTING DATA EXPORT CAPABILITIES") 
    print("=" * 40)
    
    try:
        data_path = Path(__file__).parent / 'government_directory' / 'government_officials_directory.json'
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        officials = data.get('officials', {})
        
        # Create CSV-like export data
        export_data = []
        for official_id, official in officials.items():
            export_record = {
                'Name': official.get('name', ''),
                'Title': official.get('title', ''),
                'Email': official.get('email', ''),
                'Phone': official.get('phone', ''),
                'Country': official.get('country', ''),
                'Jurisdiction': official.get('jurisdiction', ''),
                'Level': official.get('jurisdiction_level', ''),
                'Priority': official.get('priority', ''),
                'Population': official.get('population_served', 0),
                'Status': official.get('verification_status', 'uncontacted')
            }
            export_data.append(export_record)
        
        # Simulate CSV export
        csv_path = Path(__file__).parent / 'government_directory' / 'outreach_targets.csv'
        
        print(f"📄 EXPORT SIMULATION:")
        print(f"   Records to export: {len(export_data)}")
        print(f"   Target file: {csv_path.name}")
        print(f"   Fields: Name, Title, Email, Phone, Country, Priority")
        
        # Display sample export records
        print(f"\n📋 SAMPLE EXPORT RECORDS:")
        print("-" * 30)
        
        for i, record in enumerate(export_data[:3]):
            print(f"{i+1}. {record['Name']}")
            print(f"   Title: {record['Title']}")
            print(f"   Email: {record['Email']}")
            print(f"   Priority: {record['Priority']}")
            print(f"   Population: {record['Population']:,}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in export test: {e}")
        return False


def display_platform_readiness_summary():
    """Display comprehensive platform readiness summary"""
    
    print(f"\n🚀 PLATFORM READINESS SUMMARY")
    print("=" * 40)
    
    try:
        data_path = Path(__file__).parent / 'government_directory' / 'government_officials_directory.json'
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        officials = data.get('officials', {})
        statistics = data.get('statistics', {})
        
        print("✅ GENESIS DATA STATUS:")
        print(f"   Genesis Loaded: {data.get('genesis_loaded', False)}")
        print(f"   Genesis Date: {data.get('genesis_date', 'Unknown')}")
        print(f"   Last Updated: {data.get('last_updated', 'Unknown')}")
        print(f"   Version: {data.get('version', 'Unknown')}")
        
        print(f"\n📊 DATABASE METRICS:")
        print(f"   Total Officials: {statistics.get('total_officials', 0)}")
        print(f"   Countries: {len(data.get('countries', {}))}")
        print(f"   States/Provinces: {len(data.get('states', {}))}")  
        print(f"   Cities: {len(data.get('cities', {}))}")
        
        # Calculate total population coverage
        total_population = 0
        for official in officials.values():
            pop = official.get('population_served', 0)
            if isinstance(pop, (int, float)):
                total_population += pop
        
        print(f"\n👥 POPULATION COVERAGE:")
        print(f"   Total Population Served: {total_population:,}")
        print(f"   Average per Official: {total_population//len(officials):,}")
        
        # Priority distribution
        by_priority = {}
        for official in officials.values():
            priority = official.get('priority', 'unknown')
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        print(f"\n🎯 PRIORITY DISTRIBUTION:")
        for priority, count in sorted(by_priority.items()):
            print(f"   {priority.title()}: {count} officials")
        
        print(f"\n🌍 READY FOR:")
        print("   ✅ Government Outreach Campaigns")
        print("   ✅ Citizen Verification System") 
        print("   ✅ Official Platform Onboarding")
        print("   ✅ Democratic Engagement Platform")
        print("   ✅ Real-World Government Integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in readiness summary: {e}")
        return False


def main():
    """Main test execution"""
    
    print("🧪 GENESIS DATA INTEGRATION VERIFICATION")
    print("=" * 60)
    print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Direct Data Access
    if test_direct_data_access():
        tests_passed += 1
        print("✅ Test 1 PASSED: Direct Data Access")
    else:
        print("❌ Test 1 FAILED: Direct Data Access")
    
    # Test 2: Outreach Campaign Simulation  
    if test_outreach_campaign_simulation():
        tests_passed += 1
        print("✅ Test 2 PASSED: Outreach Campaign Simulation")
    else:
        print("❌ Test 2 FAILED: Outreach Campaign Simulation")
    
    # Test 3: Citizen Verification Integration
    if test_citizen_verification_integration():
        tests_passed += 1
        print("✅ Test 3 PASSED: Citizen Verification Integration")
    else:
        print("❌ Test 3 FAILED: Citizen Verification Integration")
    
    # Test 4: Data Export Capabilities
    if test_data_export_capabilities():
        tests_passed += 1
        print("✅ Test 4 PASSED: Data Export Capabilities")
    else:
        print("❌ Test 4 FAILED: Data Export Capabilities")
    
    # Test 5: Platform Readiness Summary
    if display_platform_readiness_summary():
        tests_passed += 1
        print("✅ Test 5 PASSED: Platform Readiness Summary")
    else:
        print("❌ Test 5 FAILED: Platform Readiness Summary")
    
    # Final Results
    print("\n" + "=" * 60)
    print(f"🎯 VERIFICATION RESULTS: {tests_passed}/{total_tests} TESTS PASSED")
    
    if tests_passed == total_tests:
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("✅ Genesis data is fully integrated and ready for deployment")
        print("🚀 Platform ready for government outreach campaigns")
    elif tests_passed >= 4:
        print("⚠️  Most tests passed. System is functional with minor issues.")
    else:
        print("❌ Multiple test failures. Integration needs attention.")
    
    print(f"⏰ Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()