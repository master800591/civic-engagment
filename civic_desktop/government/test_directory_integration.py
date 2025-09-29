#!/usr/bin/env python3
"""
GOVERNMENT DIRECTORY INTEGRATION TEST
Comprehensive test for the government officials directory system
Tests directory management, contact tracking, verification chain, and CSV export
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the government directory system
try:
    from civic_desktop.government.government_directory import (
        GovernmentDirectoryManager, GovernmentOfficialType, 
        VerificationStatus, VerificationAuthority
    )
    DIRECTORY_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Government directory system not available: {e}")
    DIRECTORY_SYSTEM_AVAILABLE = False

def test_directory_initialization():
    """Test government directory initialization"""
    print("\n🏛️ GOVERNMENT DIRECTORY INITIALIZATION TEST")
    print("=" * 60)
    
    if not DIRECTORY_SYSTEM_AVAILABLE:
        print("❌ Directory system not available")
        return False
    
    try:
        # Initialize directory manager
        manager = GovernmentDirectoryManager()
        
        # Get statistics
        stats = manager.get_directory_statistics()
        
        print(f"✅ Directory initialized successfully")
        print(f"📊 Total Officials: {stats.get('total_officials', 0)}")
        print(f"🌍 Countries: {len(stats.get('officials_by_country', {}))}")
        print(f"🏛️ Country Leaders: {stats.get('officials_by_level', {}).get('country', 0)}")
        print(f"🏢 State Leaders: {stats.get('officials_by_level', {}).get('state', 0)}")
        print(f"🏘️ City Leaders: {stats.get('officials_by_level', {}).get('city', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Directory initialization failed: {e}")
        return False

def test_official_search():
    """Test searching government officials"""
    print("\n🔍 OFFICIAL SEARCH TEST")
    print("=" * 40)
    
    if not DIRECTORY_SYSTEM_AVAILABLE:
        print("❌ Directory system not available")
        return False
    
    try:
        manager = GovernmentDirectoryManager()
        
        # Search for US officials
        us_officials = manager.search_officials(country="United States")
        print(f"🇺🇸 US Officials Found: {len(us_officials)}")
        
        # Search for country leaders
        country_leaders = manager.search_officials(jurisdiction_level="country")
        print(f"🌍 Country Leaders Found: {len(country_leaders)}")
        
        # Search for specific officials
        biden_results = manager.search_officials(name_query="Biden")
        print(f"🔎 'Biden' Search Results: {len(biden_results)}")
        
        # Display some results
        if biden_results:
            for official in biden_results[:2]:
                print(f"   • {official.get('name')} - {official.get('title')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Official search failed: {e}")
        return False

def test_contact_tracking():
    """Test contact tracking functionality"""
    print("\n📞 CONTACT TRACKING TEST")
    print("=" * 40)
    
    if not DIRECTORY_SYSTEM_AVAILABLE:
        print("❌ Directory system not available")
        return False
    
    try:
        manager = GovernmentDirectoryManager()
        
        # Find an official to contact
        all_officials = manager.search_officials()
        if not all_officials:
            print("❌ No officials found for testing")
            return False
        
        test_official = all_officials[0]
        official_id = test_official['official_id']
        
        print(f"📧 Testing contact with: {test_official.get('name')}")
        
        # Record contact attempt
        success, message = manager.record_contact_attempt(
            official_id=official_id,
            contact_method="email",
            response_received=False,
            notes="Test outreach email sent for platform invitation"
        )
        
        if success:
            print(f"✅ Contact recorded: {message}")
        else:
            print(f"❌ Contact recording failed: {message}")
        
        # Record response
        success2, message2 = manager.record_contact_attempt(
            official_id=official_id,
            contact_method="email",
            response_received=True,
            notes="Positive response received - interested in platform participation"
        )
        
        if success2:
            print(f"✅ Response recorded: {message2}")
        
        return success and success2
        
    except Exception as e:
        print(f"❌ Contact tracking failed: {e}")
        return False

def test_verification_chain():
    """Test hierarchical verification system"""
    print("\n✅ VERIFICATION CHAIN TEST")
    print("=" * 40)
    
    if not DIRECTORY_SYSTEM_AVAILABLE:
        print("❌ Directory system not available")
        return False
    
    try:
        manager = GovernmentDirectoryManager()
        
        # Find a country leader to verify
        country_leaders = manager.search_officials(jurisdiction_level="country")
        if not country_leaders:
            print("❌ No country leaders found for testing")
            return False
        
        test_leader = country_leaders[0]
        print(f"🏛️ Testing verification of: {test_leader.get('name')} ({test_leader.get('title')})")
        
        # Simulate founder verification of country leader
        success, message = manager.verify_government_official(
            official_id=test_leader['official_id'],
            verified_by="founder@civicplatform.org",
            verification_authority=VerificationAuthority.PLATFORM_FOUNDER,
            verification_notes="Verified through official government channels and direct contact"
        )
        
        if success:
            print(f"✅ Country leader verified: {message}")
            
            # Now test state leader verification by country leader
            state_leaders = manager.search_officials(
                jurisdiction_level="state",
                country=test_leader.get('country')
            )
            
            if state_leaders:
                test_state_leader = state_leaders[0]
                print(f"🏢 Testing state leader verification: {test_state_leader.get('name')}")
                
                success2, message2 = manager.verify_government_official(
                    official_id=test_state_leader['official_id'],
                    verified_by="country.leader@government.org",
                    verification_authority=VerificationAuthority.COUNTRY_LEADER,
                    verification_notes="Verified by verified country leader as legitimate state official"
                )
                
                if success2:
                    print(f"✅ State leader verified: {message2}")
        
        return success
        
    except Exception as e:
        print(f"❌ Verification chain test failed: {e}")
        return False

def test_csv_export():
    """Test CSV export functionality"""
    print("\n📄 CSV EXPORT TEST")
    print("=" * 30)
    
    if not DIRECTORY_SYSTEM_AVAILABLE:
        print("❌ Directory system not available")
        return False
    
    try:
        manager = GovernmentDirectoryManager()
        
        # Export to test CSV file
        test_filename = f"test_government_directory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        success, message = manager.export_officials_csv(test_filename)
        
        if success:
            print(f"✅ CSV export successful: {message}")
            
            # Check if file was created
            if os.path.exists(test_filename):
                file_size = os.path.getsize(test_filename)
                print(f"📁 File created: {test_filename} ({file_size} bytes)")
                
                # Clean up test file
                os.remove(test_filename)
                print(f"🗑️ Test file cleaned up")
                
            return True
        else:
            print(f"❌ CSV export failed: {message}")
            return False
        
    except Exception as e:
        print(f"❌ CSV export test failed: {e}")
        return False

def test_outreach_campaign():
    """Test outreach campaign functionality"""
    print("\n📢 OUTREACH CAMPAIGN TEST")
    print("=" * 40)
    
    if not DIRECTORY_SYSTEM_AVAILABLE:
        print("❌ Directory system not available")
        return False
    
    try:
        manager = GovernmentDirectoryManager()
        
        # Start outreach campaign
        campaign_id, message = manager.start_outreach_campaign(
            target_level="country",
            campaign_name="World Leaders Platform Invitation",
            email_template="invitation"
        )
        
        if campaign_id:
            print(f"✅ Outreach campaign started: {message}")
            print(f"📧 Campaign ID: {campaign_id}")
            
            # Get campaign status  
            campaign_data = manager.get_outreach_campaign_status(campaign_id)
            if campaign_data:
                print(f"📊 Campaign Status:")
                print(f"   • Target Officials: {campaign_data.get('target_count', 0)}")
                print(f"   • Contacted: {campaign_data.get('contacted_count', 0)}")
                print(f"   • Responses: {campaign_data.get('response_count', 0)}")
            
            return True
        else:
            print(f"❌ Outreach campaign failed: {message}")
            return False
        
    except Exception as e:
        print(f"❌ Outreach campaign test failed: {e}")
        return False

def display_directory_summary():
    """Display comprehensive directory summary"""
    print("\n📊 GOVERNMENT DIRECTORY SUMMARY")
    print("=" * 50)
    
    if not DIRECTORY_SYSTEM_AVAILABLE:
        print("❌ Directory system not available")
        return
    
    try:
        manager = GovernmentDirectoryManager()
        stats = manager.get_directory_statistics()
        
        print("🌍 WORLD LEADERS DATABASE")
        print(f"Total Officials: {stats.get('total_officials', 0)}")
        
        print("\n📈 By Government Level:")
        officials_by_level = stats.get('officials_by_level', {})
        for level, count in officials_by_level.items():
            print(f"   {level.title()}: {count}")
        
        print("\n🌎 By Country:")
        officials_by_country = stats.get('officials_by_country', {})
        for country, count in sorted(officials_by_country.items()):
            print(f"   {country}: {count}")
        
        print("\n📞 Contact Status:")
        officials_by_status = stats.get('officials_by_status', {})
        for status, count in officials_by_status.items():
            print(f"   {status.replace('_', ' ').title()}: {count}")
        
        print("\n✅ Verification Chain:")
        verified_count = stats.get('verified_officials', 0)
        total_count = stats.get('total_officials', 0)
        verification_rate = (verified_count / total_count * 100) if total_count > 0 else 0
        print(f"   Verified: {verified_count} ({verification_rate:.1f}%)")
        print(f"   Pending: {total_count - verified_count}")
        
        print("\n🎯 Response Metrics:")
        response_rate = stats.get('response_rate', 0)
        print(f"   Response Rate: {response_rate:.1f}%")
        print(f"   Total Contact Attempts: {stats.get('total_contact_attempts', 0)}")
        
    except Exception as e:
        print(f"❌ Summary display failed: {e}")

def main():
    """Run comprehensive government directory tests"""
    print("🏛️ GOVERNMENT OFFICIALS DIRECTORY SYSTEM TEST")
    print("=" * 60)
    print("Testing comprehensive government contact and verification system")
    print("Hierarchical verification: Founders → Countries → States → Cities")
    print("Government officials separate from contract governance system")
    print("=" * 60)
    
    # Track test results
    test_results = []
    
    # Run all tests
    test_results.append(("Directory Initialization", test_directory_initialization()))
    test_results.append(("Official Search", test_official_search()))
    test_results.append(("Contact Tracking", test_contact_tracking()))
    test_results.append(("Verification Chain", test_verification_chain()))
    test_results.append(("CSV Export", test_csv_export()))
    test_results.append(("Outreach Campaign", test_outreach_campaign()))
    
    # Display directory summary
    display_directory_summary()
    
    # Test results summary
    print("\n" + "=" * 60)
    print("🧪 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Government directory system fully operational!")
        print("\n🚀 NEXT STEPS:")
        print("1. Begin systematic outreach to world leaders using contact database")
        print("2. Implement verification chain: founders verify country leaders")
        print("3. Country leaders verify their state/provincial leaders")
        print("4. State leaders verify their city/municipal leaders")
        print("5. Government officials remain separate from contract governance")
    else:
        print("⚠️ Some tests failed - please review system configuration")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)