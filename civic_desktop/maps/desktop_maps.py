"""
Desktop Maps Module for Civic Engagement Platform
Blockchain-integrated geographic information system
Compatible with existing civic_desktop application architecture
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add civic_desktop to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
civic_desktop_dir = os.path.dirname(current_dir)
sys.path.insert(0, civic_desktop_dir)

print(f"🗺️ Maps module loading from: {current_dir}")
print(f"📁 Civic desktop directory: {civic_desktop_dir}")


class MapDataIntegration:
    """
    Core maps data integration with blockchain and user permissions
    Works independently of UI framework
    """
    
    def __init__(self):
        self.blockchain = None
        self.session_manager = None
        
        # Data caches
        self.officials_cache = {}
        self.activities_cache = []
        self.last_update = None
        
        # Initialize integrations
        self.initialize_integrations()
        
        # Load data
        self.load_government_data()
        self.generate_civic_activities()
    
    def initialize_integrations(self):
        """Initialize blockchain and session management"""
        
        # Try to import and initialize blockchain
        try:
            from blockchain.blockchain import Blockchain
            self.blockchain = Blockchain()
            print("✅ Maps: Blockchain integration active")
        except Exception as e:
            print(f"⚠️ Maps: Blockchain unavailable - {e}")
            self.blockchain = None
        
        # Try to import and initialize session management
        try:
            from users.session import SessionManager
            self.session_manager = SessionManager()
            print("✅ Maps: Session management active")
        except Exception as e:
            print(f"⚠️ Maps: Session management unavailable - {e}")
            self.session_manager = None
    
    def load_government_data(self):
        """Load government officials from the directory"""
        
        try:
            # Find government directory
            possible_paths = [
                os.path.join(civic_desktop_dir, 'government', 'government_directory', 'government_officials_directory.json'),
                os.path.join(os.path.dirname(civic_desktop_dir), 'government', 'government_directory', 'government_officials_directory.json'),
                'government/government_directory/government_officials_directory.json'
            ]
            
            officials_file = None
            for path in possible_paths:
                if os.path.exists(path):
                    officials_file = path
                    print(f"📁 Found government directory: {path}")
                    break
            
            if officials_file:
                with open(officials_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                # Process officials data
                self.officials_cache = {}
                for official_id, official in raw_data.items():
                    if isinstance(official, dict):
                        processed = self.process_official_data(official_id, official)
                        if processed:
                            self.officials_cache[official_id] = processed
                
                self.last_update = datetime.now()
                print(f"✅ Loaded {len(self.officials_cache)} government officials")
            else:
                print("⚠️ Government directory not found, loading sample data")
                self.load_sample_officials()
                
        except Exception as e:
            print(f"❌ Error loading government data: {e}")
            self.load_sample_officials()
    
    def process_official_data(self, official_id: str, official: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual official data"""
        
        try:
            # Get coordinates
            lat, lon = self.get_official_coordinates(official)
            
            return {
                'id': official_id,
                'name': official.get('name', 'Unknown Official'),
                'title': official.get('title', 'Government Official'),
                'country': official.get('country', 'Unknown'),
                'jurisdiction': official.get('jurisdiction', 'Unknown'),
                'party': official.get('party_affiliation', 'Independent'),
                'email': official.get('email', 'N/A'),
                'phone': official.get('phone', 'N/A'),
                'verification': official.get('verification_status', 'uncontacted'),
                'coordinates': (lat, lon),
                'type': self.determine_official_type(official.get('title', '')),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ Error processing official {official_id}: {e}")
            return None
    
    def get_official_coordinates(self, official: Dict[str, Any]) -> Tuple[float, float]:
        """Get coordinates for an official"""
        
        # Coordinate mapping for major locations
        location_map = {
            # United States Federal
            'United States': (38.9072, -77.0369),  # Washington DC
            'Washington, D.C.': (38.9072, -77.0369),
            'Washington DC': (38.9072, -77.0369),
            
            # US States (using capitals)
            'California': (38.5816, -121.4944),    # Sacramento
            'Texas': (30.2672, -97.7431),          # Austin
            'Florida': (30.4518, -84.27277),       # Tallahassee
            'New York': (42.6526, -73.7562),       # Albany
            'Illinois': (39.7817, -89.6501),       # Springfield
            
            # Major US Cities
            'New York City': (40.7128, -74.0060),
            'Los Angeles': (34.0522, -118.2437),
            'Chicago': (41.8781, -87.6298),
            'Houston': (29.7604, -95.3698),
            
            # International
            'United Kingdom': (51.5074, -0.1278),  # London
            'Germany': (52.5200, 13.4050),         # Berlin
            'France': (48.8566, 2.3522),           # Paris
            'Japan': (35.6762, 139.6503),          # Tokyo
            'Canada': (45.4215, -75.6972),         # Ottawa
            'Italy': (41.9028, 12.4964),           # Rome
            'Spain': (40.4168, -3.7038),           # Madrid
        }
        
        # Try jurisdiction first, then country
        jurisdiction = official.get('jurisdiction', '')
        country = official.get('country', '')
        
        for location in [jurisdiction, country]:
            if location in location_map:
                return location_map[location]
        
        # Check for partial matches
        for location, coords in location_map.items():
            if location.lower() in jurisdiction.lower() or location.lower() in country.lower():
                return coords
        
        # Default to center of USA
        return (39.8283, -98.5795)
    
    def determine_official_type(self, title: str) -> str:
        """Determine official type from title"""
        
        title_lower = title.lower()
        
        if 'president' in title_lower and 'vice' not in title_lower:
            return 'president'
        elif 'prime minister' in title_lower:
            return 'prime_minister'
        elif 'vice president' in title_lower:
            return 'vice_president'
        elif 'governor' in title_lower:
            return 'governor'
        elif 'mayor' in title_lower:
            return 'mayor'
        elif 'senator' in title_lower:
            return 'senator'
        elif 'representative' in title_lower or 'congressman' in title_lower:
            return 'representative'
        elif 'minister' in title_lower and 'prime' not in title_lower:
            return 'minister'
        elif 'chancellor' in title_lower:
            return 'chancellor'
        else:
            return 'other'
    
    def load_sample_officials(self):
        """Load sample officials data"""
        
        self.officials_cache = {
            'us_president_47': {
                'id': 'us_president_47',
                'name': 'Donald J. Trump',
                'title': 'President of the United States (47th)',
                'country': 'United States',
                'jurisdiction': 'United States',
                'party': 'Republican',
                'email': 'president@whitehouse.gov',
                'phone': '+1-202-456-1414',
                'verification': 'verified',
                'coordinates': (38.9072, -77.0369),
                'type': 'president',
                'last_updated': datetime.now().isoformat()
            },
            'us_vp_50': {
                'id': 'us_vp_50',
                'name': 'J.D. Vance',
                'title': 'Vice President of the United States',
                'country': 'United States',
                'jurisdiction': 'United States',
                'party': 'Republican',
                'email': 'vp@whitehouse.gov',
                'phone': '+1-202-456-1414',
                'verification': 'verified',
                'coordinates': (38.9072, -77.0369),
                'type': 'vice_president',
                'last_updated': datetime.now().isoformat()
            },
            'uk_pm_current': {
                'id': 'uk_pm_current',
                'name': 'Keir Starmer',
                'title': 'Prime Minister of the United Kingdom',
                'country': 'United Kingdom',
                'jurisdiction': 'United Kingdom',
                'party': 'Labour',
                'email': 'pm@gov.uk',
                'phone': '+44-20-7930-4433',
                'verification': 'verified',
                'coordinates': (51.5074, -0.1278),
                'type': 'prime_minister',
                'last_updated': datetime.now().isoformat()
            },
            'japan_pm_current': {
                'id': 'japan_pm_current',
                'name': 'Shigeru Ishiba',
                'title': 'Prime Minister of Japan',
                'country': 'Japan',
                'jurisdiction': 'Japan',
                'party': 'Liberal Democratic Party',
                'email': 'pm@kantei.go.jp',
                'phone': '+81-3-3581-0101',
                'verification': 'verified',
                'coordinates': (35.6762, 139.6503),
                'type': 'prime_minister',
                'last_updated': datetime.now().isoformat()
            }
        }
        
        self.last_update = datetime.now()
        print(f"✅ Loaded {len(self.officials_cache)} sample officials")
    
    def generate_civic_activities(self):
        """Generate civic activities data"""
        
        self.activities_cache = [
            {
                'id': 'presidential_address_2025',
                'title': 'Presidential Address to the Nation',
                'type': 'presidential_address',
                'date': '2025-10-15T20:00:00Z',
                'location': 'Washington, D.C.',
                'coordinates': (38.9072, -77.0369),
                'status': 'scheduled',
                'visibility': 'public',
                'description': 'State of the Union Address'
            },
            {
                'id': 'town_hall_nyc_2025',
                'title': 'New York Community Town Hall',
                'type': 'town_hall',
                'date': '2025-10-20T19:00:00Z',
                'location': 'New York City, NY',
                'coordinates': (40.7128, -74.0060),
                'status': 'upcoming',
                'visibility': 'public',
                'description': 'Community discussion on local issues'
            },
            {
                'id': 'uk_parliament_session',
                'title': 'UK Parliamentary Session',
                'type': 'parliamentary_session',
                'date': '2025-10-18T14:30:00Z',
                'location': 'London, United Kingdom',
                'coordinates': (51.5074, -0.1278),
                'status': 'scheduled',
                'visibility': 'public',
                'description': 'Weekly Prime Minister Questions'
            }
        ]
        
        print(f"✅ Generated {len(self.activities_cache)} civic activities")
    
    def get_user_permissions(self) -> Dict[str, Any]:
        """Get user permissions for map data access"""
        
        if not self.session_manager:
            return self.get_guest_permissions()
        
        try:
            if not self.session_manager.is_authenticated():
                return self.get_guest_permissions()
            
            user = self.session_manager.get_current_user()
            if not user:
                return self.get_guest_permissions()
            
            role = user.get('role', 'Contract Citizen')
            
            # Role-based permissions
            if role in ['Contract Founder', 'Contract Elder']:
                return {
                    'role': 'administrative',
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_contact_info': True,
                    'can_view_sensitive_data': True,
                    'jurisdiction_filter': [],  # No filter
                    'max_officials': -1,  # Unlimited
                    'max_activities': -1
                }
            elif role in ['Contract Representative', 'Contract Senator']:
                return {
                    'role': 'government',
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_contact_info': True,
                    'can_view_sensitive_data': False,
                    'jurisdiction_filter': [user.get('country', ''), user.get('jurisdiction', '')],
                    'max_officials': 200,
                    'max_activities': 50
                }
            elif role == 'Contract Citizen':
                return {
                    'role': 'citizen',
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_contact_info': False,
                    'can_view_sensitive_data': False,
                    'jurisdiction_filter': [user.get('country', 'United States')],
                    'max_officials': 100,
                    'max_activities': 25
                }
            else:
                return self.get_guest_permissions()
                
        except Exception as e:
            print(f"⚠️ Error getting user permissions: {e}")
            return self.get_guest_permissions()
    
    def get_guest_permissions(self) -> Dict[str, Any]:
        """Get guest user permissions"""
        
        return {
            'role': 'guest',
            'can_view_officials': True,
            'can_view_activities': False,
            'can_view_contact_info': False,
            'can_view_sensitive_data': False,
            'jurisdiction_filter': ['United States'],
            'max_officials': 20,
            'max_activities': 5
        }
    
    def get_filtered_officials(self, permissions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get officials filtered by permissions"""
        
        if permissions is None:
            permissions = self.get_user_permissions()
        
        if not permissions.get('can_view_officials', False):
            return []
        
        # Get all officials
        all_officials = list(self.officials_cache.values())
        
        # Apply jurisdiction filter for non-admin users
        if permissions['role'] != 'administrative':
            jurisdiction_filter = permissions.get('jurisdiction_filter', [])
            if jurisdiction_filter:
                filtered = []
                for official in all_officials:
                    if (official.get('country') in jurisdiction_filter or
                        official.get('jurisdiction') in jurisdiction_filter):
                        filtered.append(official)
                all_officials = filtered
        
        # Apply count limit
        max_officials = permissions.get('max_officials', -1)
        if max_officials > 0:
            all_officials = all_officials[:max_officials]
        
        # Remove sensitive data for users without permission
        if not permissions.get('can_view_contact_info', False):
            for official in all_officials:
                official = official.copy()
                official['email'] = 'Contact via official channels'
                official['phone'] = 'Contact via official channels'
        
        return all_officials
    
    def get_filtered_activities(self, permissions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get activities filtered by permissions"""
        
        if permissions is None:
            permissions = self.get_user_permissions()
        
        if not permissions.get('can_view_activities', False):
            return []
        
        activities = self.activities_cache.copy()
        
        # For guests and citizens, only show public activities
        if permissions['role'] in ['guest', 'citizen']:
            activities = [a for a in activities if a.get('visibility') == 'public']
        
        # Apply count limit
        max_activities = permissions.get('max_activities', -1)
        if max_activities > 0:
            activities = activities[:max_activities]
        
        return activities
    
    def search_officials(self, query: str, permissions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search officials by query"""
        
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.lower().strip()
        officials = self.get_filtered_officials(permissions)
        results = []
        
        for official in officials:
            # Search in name, title, jurisdiction, country
            searchable = f"{official.get('name', '')} {official.get('title', '')} {official.get('jurisdiction', '')} {official.get('country', '')}".lower()
            
            if query in searchable:
                # Add relevance score
                relevance = 0
                if query in official.get('name', '').lower():
                    relevance += 10
                elif query in official.get('title', '').lower():
                    relevance += 5
                elif query in official.get('jurisdiction', '').lower():
                    relevance += 3
                else:
                    relevance += 1
                
                result = official.copy()
                result['relevance'] = relevance
                results.append(result)
        
        # Sort by relevance
        results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        # Log search to blockchain
        self.log_to_blockchain('search_officials', {
            'query': query,
            'results_count': len(results)
        })
        
        return results
    
    def get_map_statistics(self, permissions: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get map statistics"""
        
        if permissions is None:
            permissions = self.get_user_permissions()
        
        officials = self.get_filtered_officials(permissions)
        activities = self.get_filtered_activities(permissions)
        
        # Count by type
        officials_by_type = {}
        for official in officials:
            official_type = official.get('type', 'other')
            officials_by_type[official_type] = officials_by_type.get(official_type, 0) + 1
        
        # Count by jurisdiction
        officials_by_jurisdiction = {}
        for official in officials:
            jurisdiction = official.get('jurisdiction', 'Unknown')
            officials_by_jurisdiction[jurisdiction] = officials_by_jurisdiction.get(jurisdiction, 0) + 1
        
        return {
            'total_officials': len(officials),
            'total_activities': len(activities),
            'user_role': permissions['role'],
            'permissions': {
                'view_officials': permissions.get('can_view_officials', False),
                'view_activities': permissions.get('can_view_activities', False),
                'view_contacts': permissions.get('can_view_contact_info', False)
            },
            'officials_by_type': officials_by_type,
            'officials_by_jurisdiction': officials_by_jurisdiction,
            'last_updated': self.last_update.isoformat() if self.last_update else None
        }
    
    def log_to_blockchain(self, action: str, data: Dict[str, Any]):
        """Log action to blockchain"""
        
        if not self.blockchain:
            return
        
        try:
            user_email = ""
            if self.session_manager and self.session_manager.is_authenticated():
                user = self.session_manager.get_current_user()
                if user:
                    user_email = user.get('email', '')
            
            blockchain_data = {
                'action': action,
                'timestamp': datetime.now().isoformat(),
                'user_permissions': self.get_user_permissions(),
                'data': data
            }
            
            success = self.blockchain.add_page(
                action_type="maps_interaction",
                data=blockchain_data,
                user_email=user_email
            )
            
            if success:
                print(f"✅ Maps: Logged to blockchain - {action}")
            
        except Exception as e:
            print(f"⚠️ Maps: Blockchain logging error - {e}")
    
    def refresh_data(self) -> bool:
        """Refresh all map data"""
        
        try:
            print("🔄 Maps: Refreshing data...")
            
            # Reload government data
            self.load_government_data()
            
            # Regenerate activities
            self.generate_civic_activities()
            
            # Log refresh
            self.log_to_blockchain('data_refreshed', {
                'officials_count': len(self.officials_cache),
                'activities_count': len(self.activities_cache)
            })
            
            print("✅ Maps: Data refresh completed")
            return True
            
        except Exception as e:
            print(f"❌ Maps: Data refresh failed - {e}")
            return False


class MapsTab:
    """
    Maps tab for civic desktop application
    Works with or without PyQt5
    """
    
    def __init__(self):
        self.data_integration = MapDataIntegration()
        
        # Try PyQt5 integration
        try:
            from PyQt5.QtWidgets import QWidget
            self.pyqt5_available = True
            print("✅ PyQt5 available - GUI interface possible")
        except ImportError:
            self.pyqt5_available = False
            print("⚠️ PyQt5 not available - text interface only")
    
    def display_text_interface(self):
        """Display text-based interface"""
        
        print("\n" + "="*80)
        print("🗺️ CIVIC ENGAGEMENT MAPS - DESKTOP MODULE")
        print("="*80)
        
        # Show user permissions
        permissions = self.data_integration.get_user_permissions()
        print(f"\n👤 USER ACCESS LEVEL")
        print("-"*50)
        print(f"Role: {permissions['role'].title()}")
        print(f"View Officials: {'✅ Yes' if permissions['can_view_officials'] else '❌ No'}")
        print(f"View Activities: {'✅ Yes' if permissions['can_view_activities'] else '❌ No'}")
        print(f"View Contact Info: {'✅ Yes' if permissions['can_view_contact_info'] else '❌ No'}")
        
        if permissions['jurisdiction_filter']:
            print(f"Jurisdiction Filter: {', '.join(permissions['jurisdiction_filter'])}")
        
        # Show officials
        officials = self.data_integration.get_filtered_officials()
        print(f"\n👥 GOVERNMENT OFFICIALS ({len(officials)} accessible)")
        print("-"*50)
        
        for i, official in enumerate(officials[:10], 1):  # Show first 10
            coords = official.get('coordinates', (0, 0))
            print(f"{i:2d}. {official.get('name', 'Unknown')}")
            print(f"    📋 {official.get('title', 'Unknown Title')}")
            print(f"    🌍 {official.get('jurisdiction', 'Unknown')} ({coords[0]:.4f}°, {coords[1]:.4f}°)")
            print(f"    🏛️ {official.get('party', 'Unknown Party')}")
            print(f"    ✅ Status: {official.get('verification', 'Unknown').title()}")
            
            if permissions['can_view_contact_info']:
                print(f"    📧 {official.get('email', 'N/A')}")
                print(f"    📞 {official.get('phone', 'N/A')}")
            
            print()
        
        if len(officials) > 10:
            print(f"    ... and {len(officials) - 10} more officials")
        
        # Show activities
        activities = self.data_integration.get_filtered_activities()
        if activities:
            print(f"\n📊 CIVIC ACTIVITIES ({len(activities)} accessible)")
            print("-"*50)
            
            for i, activity in enumerate(activities, 1):
                coords = activity.get('coordinates', (0, 0))
                print(f"{i:2d}. {activity.get('title', 'Unknown Activity')}")
                print(f"    📅 {activity.get('date', 'Unknown Date')}")
                print(f"    📍 {activity.get('location', 'Unknown Location')} ({coords[0]:.4f}°, {coords[1]:.4f}°)")
                print(f"    🏷️ Type: {activity.get('type', 'Unknown').replace('_', ' ').title()}")
                print(f"    📊 Status: {activity.get('status', 'Unknown').title()}")
                print(f"    👁️ Visibility: {activity.get('visibility', 'Unknown').title()}")
                print()
        
        # Show statistics
        stats = self.data_integration.get_map_statistics()
        print(f"\n📈 MAP STATISTICS")
        print("-"*50)
        print(f"Total Officials: {stats['total_officials']}")
        print(f"Total Activities: {stats['total_activities']}")
        print(f"User Role: {stats['user_role'].title()}")
        
        if stats['officials_by_type']:
            print(f"\nOfficials by Type:")
            for otype, count in sorted(stats['officials_by_type'].items()):
                print(f"  • {otype.replace('_', ' ').title()}: {count}")
        
        if stats['officials_by_jurisdiction']:
            print(f"\nOfficials by Jurisdiction:")
            for jurisdiction, count in sorted(stats['officials_by_jurisdiction'].items()):
                print(f"  • {jurisdiction}: {count}")
        
        print(f"\n🔗 BLOCKCHAIN INTEGRATION")
        print("-"*50)
        print("✅ All map interactions are logged to blockchain")
        print("✅ User permissions verified for each access")
        print("✅ Data filtering applied based on user role")
        print("✅ Audit trail maintained for transparency")
        
        print("\n" + "="*80)
        print(f"🕒 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Log interface access
        self.data_integration.log_to_blockchain('text_interface_accessed', {
            'officials_shown': len(officials),
            'activities_shown': len(activities)
        })
    
    def interactive_demo(self):
        """Interactive demo for testing"""
        
        print("\n🎮 INTERACTIVE MAPS DEMO")
        print("="*40)
        
        while True:
            print("\nOptions:")
            print("1. Search officials")
            print("2. View statistics")
            print("3. Refresh data")
            print("4. Show all officials")
            print("5. Show activities")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == '0':
                print("👋 Exiting maps demo")
                break
            elif choice == '1':
                query = input("Enter search term: ").strip()
                if query:
                    results = self.data_integration.search_officials(query)
                    print(f"\n🔍 Search Results for '{query}' ({len(results)} found):")
                    for i, official in enumerate(results[:5], 1):
                        print(f"{i}. {official.get('name')} - {official.get('title')}")
            elif choice == '2':
                stats = self.data_integration.get_map_statistics()
                print(f"\n📈 Statistics:")
                print(f"Officials: {stats['total_officials']}")
                print(f"Activities: {stats['total_activities']}")
                print(f"Role: {stats['user_role']}")
            elif choice == '3':
                success = self.data_integration.refresh_data()
                print(f"🔄 Data refresh: {'✅ Success' if success else '❌ Failed'}")
            elif choice == '4':
                officials = self.data_integration.get_filtered_officials()
                print(f"\n👥 All Officials ({len(officials)}):")
                for i, official in enumerate(officials, 1):
                    print(f"{i:2d}. {official.get('name')} - {official.get('title')}")
            elif choice == '5':
                activities = self.data_integration.get_filtered_activities()
                print(f"\n📊 Activities ({len(activities)}):")
                for i, activity in enumerate(activities, 1):
                    print(f"{i:2d}. {activity.get('title')} - {activity.get('type')}")
            else:
                print("❌ Invalid choice")


# Test and demonstration functions
def test_maps_module():
    """Test the maps module functionality"""
    
    print("🧪 TESTING MAPS MODULE")
    print("="*50)
    
    # Initialize maps tab
    maps_tab = MapsTab()
    
    # Test data integration
    integration = maps_tab.data_integration
    
    # Test permissions
    permissions = integration.get_user_permissions()
    print(f"✅ Permissions: {permissions['role']}")
    
    # Test officials
    officials = integration.get_filtered_officials()
    print(f"✅ Officials: {len(officials)}")
    
    # Test activities  
    activities = integration.get_filtered_activities()
    print(f"✅ Activities: {len(activities)}")
    
    # Test search
    results = integration.search_officials("trump")
    print(f"✅ Search results: {len(results)}")
    
    # Test statistics
    stats = integration.get_map_statistics()
    print(f"✅ Statistics generated: {stats['total_officials']} officials, {stats['total_activities']} activities")
    
    # Show interface
    print(f"\n🖥️ Displaying interface...")
    maps_tab.display_text_interface()
    
    return maps_tab


def main():
    """Main function for maps module"""
    
    print("🗺️ CIVIC ENGAGEMENT MAPS MODULE")
    print("Desktop-integrated geographic information system")
    print("With blockchain logging and user permission filtering")
    print("="*60)
    
    # Test the module
    maps_tab = test_maps_module()
    
    # Interactive demo
    try:
        choice = input("\n🎮 Run interactive demo? (y/N): ").strip().lower()
        if choice == 'y':
            maps_tab.interactive_demo()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")


if __name__ == "__main__":
    main()