#!/usr/bin/env python3
"""
GOVERNMENT DIRECTORY DEMONSTRATION
Shows the comprehensive government officials directory system in action
Demonstrates contact management and hierarchical verification chain
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def demo_government_directory():
    """Demonstrate the government directory system capabilities"""
    
    print("🏛️ GOVERNMENT OFFICIALS DIRECTORY SYSTEM DEMO")
    print("=" * 60)
    print("Comprehensive contact database for world government leaders")
    print("Hierarchical verification: Founders → Countries → States → Cities")
    print("Government officials SEPARATE from contract governance system")
    print("=" * 60)
    
    try:
        from civic_desktop.government.government_directory import GovernmentDirectoryManager
        
        # Initialize directory
        print("\n📊 Initializing Government Directory...")
        manager = GovernmentDirectoryManager()
        stats = manager.get_directory_statistics()
        
        print(f"✅ Directory loaded with {stats.get('total_officials', 0)} officials")
        
        # Show world leaders
        print("\n🌍 WORLD LEADERS DATABASE")
        print("-" * 30)
        
        # Display major world leaders
        world_leaders = [
            "Joe Biden", "Emmanuel Macron", "Justin Trudeau", 
            "Fumio Kishida", "Anthony Albanese", "Olaf Scholz"
        ]
        
        for leader_name in world_leaders:
            results = manager.search_officials(name_query=leader_name)
            if results:
                leader = results[0]
                print(f"• {leader.get('name', 'Unknown')} - {leader.get('title', 'Unknown Title')}")
                print(f"  📧 {leader.get('email', 'No email')}")
                print(f"  📞 {leader.get('phone', 'No phone')}")
                print(f"  🏛️ {leader.get('jurisdiction', 'Unknown jurisdiction')}")
                print()
        
        # Show US state governors  
        print("\n🇺🇸 US STATE GOVERNORS")
        print("-" * 25)
        
        us_governors = [
            "Gavin Newsom", "Greg Abbott", "Ron DeSantis", 
            "Kathy Hochul", "J.B. Pritzker"
        ]
        
        for governor_name in us_governors:
            results = manager.search_officials(name_query=governor_name)
            if results:
                governor = results[0]
                print(f"• {governor.get('name', 'Unknown')} - {governor.get('title', 'Governor')}")
                print(f"  🏛️ {governor.get('jurisdiction', 'Unknown state')}")
                print(f"  📧 {governor.get('email', 'No email')}")
        
        print("\n🏘️ MAJOR CITY MAYORS")
        print("-" * 20)
        
        major_mayors = [
            "Eric Adams", "Karen Bass", "Sadiq Khan", 
            "Yuriko Koike", "Anne Hidalgo"
        ]
        
        for mayor_name in major_mayors:
            results = manager.search_officials(name_query=mayor_name)
            if results:
                mayor = results[0]
                print(f"• {mayor.get('name', 'Unknown')} - {mayor.get('title', 'Mayor')}")
                print(f"  🏘️ {mayor.get('jurisdiction', 'Unknown city')}")
                print(f"  📧 {mayor.get('email', 'No email')}")
        
        # Demonstrate verification hierarchy
        print("\n✅ HIERARCHICAL VERIFICATION SYSTEM")
        print("-" * 40)
        print("🔗 VERIFICATION CHAIN:")
        print("   1. Platform FOUNDERS verify COUNTRY leaders")
        print("   2. Country leaders verify STATE/PROVINCIAL leaders")
        print("   3. State leaders verify CITY/MUNICIPAL leaders")
        print()
        print("🚫 SEPARATION PRINCIPLE:")
        print("   • Government officials are SEPARATE from contract roles")
        print("   • They do NOT receive contract governance positions")
        print("   • Cannot run for contract Representative/Senator/Elder roles")
        print("   • Maintains separation between real government and platform")
        
        # Show contact tracking capabilities
        print("\n📞 CONTACT MANAGEMENT SYSTEM")
        print("-" * 35)
        print("📧 EMAIL TEMPLATES:")
        print("   • Platform invitation emails")
        print("   • Follow-up reminders")
        print("   • Verification requests")
        print("   • Platform updates and announcements")
        print()
        print("📊 TRACKING CAPABILITIES:")
        print("   • Contact attempt logging")
        print("   • Response tracking")
        print("   • Interest level monitoring")
        print("   • Verification status updates")
        
        # Statistics overview
        print("\n📈 DIRECTORY STATISTICS")
        print("-" * 25)
        
        officials_by_level = stats.get('officials_by_level', {})
        print(f"Country Leaders: {officials_by_level.get('country', 0)}")
        print(f"State Leaders: {officials_by_level.get('state', 0)}")
        print(f"City Leaders: {officials_by_level.get('city', 0)}")
        
        officials_by_country = stats.get('officials_by_country', {})
        print(f"Countries Represented: {len(officials_by_country)}")
        
        print(f"Verified Officials: {stats.get('verified_officials', 0)}")
        print(f"Response Rate: {stats.get('response_rate', 0):.1f}%")
        
        # CSV export demonstration
        print("\n📄 CSV EXPORT CAPABILITY")
        print("-" * 25)
        print("✅ Export complete official database to CSV")
        print("✅ Filter exports by country, level, or status")
        print("✅ Include contact information for outreach campaigns")
        print("✅ Track verification chain progress")
        
        print("\n🎯 OUTREACH CAMPAIGN READINESS")
        print("-" * 35)
        print("✅ Systematic contact with world leaders")
        print("✅ Verification of government credentials")
        print("✅ Platform invitation and onboarding")
        print("✅ Separation from contract governance maintained")
        print("✅ Complete transparency through blockchain integration")
        
        print("\n" + "=" * 60)
        print("🚀 GOVERNMENT DIRECTORY SYSTEM OPERATIONAL")
        print("Ready for worldwide government leader outreach!")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"❌ Government directory system not available: {e}")
        print("\n📋 SYSTEM REQUIREMENTS:")
        print("• GovernmentDirectoryManager class")
        print("• World leaders database")
        print("• Contact tracking system")
        print("• Hierarchical verification chain")
        return False
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def show_contact_examples():
    """Show examples of government contact information"""
    
    print("\n📇 SAMPLE GOVERNMENT CONTACT DIRECTORY")
    print("=" * 45)
    
    sample_contacts = {
        "🇺🇸 United States": {
            "President": {
                "name": "Joe Biden",
                "email": "president@whitehouse.gov", 
                "phone": "+1-202-456-1414",
                "address": "1600 Pennsylvania Avenue NW, Washington, DC 20500"
            },
            "Governor (CA)": {
                "name": "Gavin Newsom",
                "email": "govpress@gov.ca.gov",
                "phone": "+1-916-445-2841", 
                "address": "1303 10th Street, Sacramento, CA 95814"
            },
            "Mayor (NYC)": {
                "name": "Eric Adams",
                "email": "mayor@cityhall.nyc.gov",
                "phone": "+1-212-788-3000",
                "address": "City Hall, New York, NY 10007"
            }
        },
        "🇫🇷 France": {
            "President": {
                "name": "Emmanuel Macron",
                "email": "contact@elysee.fr",
                "phone": "+33-1-42-92-81-00",
                "address": "Palais de l'Élysée, 75008 Paris"
            },
            "Mayor (Paris)": {
                "name": "Anne Hidalgo", 
                "email": "anne.hidalgo@paris.fr",
                "phone": "+33-1-42-76-40-40",
                "address": "Hôtel de Ville, 75004 Paris"
            }
        },
        "🇬🇧 United Kingdom": {
            "Prime Minister": {
                "name": "Rishi Sunak",
                "email": "pm@number10.gov.uk",
                "phone": "+44-20-7930-4433",
                "address": "10 Downing Street, London SW1A 2AA"
            },
            "Mayor (London)": {
                "name": "Sadiq Khan",
                "email": "mayor@london.gov.uk", 
                "phone": "+44-20-7983-4000",
                "address": "City Hall, London SE1 2AA"
            }
        },
        "🇨🇦 Canada": {
            "Prime Minister": {
                "name": "Justin Trudeau",
                "email": "pm@pm.gc.ca",
                "phone": "+1-613-992-4211",
                "address": "Office of the Prime Minister, Ottawa, ON K1A 0A6"
            }
        },
        "🇯🇵 Japan": {
            "Prime Minister": {
                "name": "Fumio Kishida",
                "email": "pm@kantei.go.jp", 
                "phone": "+81-3-5253-2111",
                "address": "Prime Minister's Office, Tokyo"
            },
            "Governor (Tokyo)": {
                "name": "Yuriko Koike",
                "email": "info@metro.tokyo.lg.jp",
                "phone": "+81-3-5321-1111",
                "address": "Tokyo Metropolitan Government, Tokyo"
            }
        }
    }
    
    for country, officials in sample_contacts.items():
        print(f"\n{country}")
        print("-" * len(country))
        
        for position, contact in officials.items():
            print(f"  {position}: {contact['name']}")
            print(f"    📧 {contact['email']}")
            print(f"    📞 {contact['phone']}")
            print(f"    📍 {contact['address']}")
            print()

def main():
    """Main demonstration function"""
    
    # Run the directory demo
    success = demo_government_directory()
    
    # Show contact examples
    show_contact_examples()
    
    if success:
        print("\n🎉 DEMO COMPLETE - Government directory system ready for deployment!")
        print("\n🔗 BLOCKCHAIN INTEGRATION:")
        print("• All government directory activities recorded on blockchain")
        print("• Contact attempts and responses transparently logged") 
        print("• Verification chain permanently auditable")
        print("• Government official separation from contract roles enforced")
        
        print("\n📋 NEXT ACTIONS:")
        print("1. Begin systematic outreach to world leaders")
        print("2. Implement founder verification of country leaders")
        print("3. Enable country leaders to verify state/provincial officials")
        print("4. Allow state leaders to verify municipal officials")
        print("5. Maintain strict separation from contract governance")
        
    else:
        print("\n⚠️ Demo incomplete - system configuration needed")
    
    return success

if __name__ == "__main__":
    main()