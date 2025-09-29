"""
Blockchain-integrated Maps Backend
Core mapping data management without web dependencies
Integrated with civic engagement platform blockchain and user permissions
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

# Add parent directories for imports  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MapDataManager:
    """
    Manages map data with blockchain integration and user permissions
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self.get_default_config_path()
        self.blockchain = None
        self.session_manager = None
        
        # Initialize blockchain and session management
        self.initialize_integrations()
        
        # Data caches
        self.officials_cache = {}
        self.activities_cache = {}
        self.last_update = None
        
        # Load initial data
        self.load_government_data()
    
    def get_default_config_path(self) -> str:
        """Get default configuration path"""
        try:
            # Try to find the civic_desktop directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            civic_desktop_dir = None
            
            # Walk up the directory tree to find civic_desktop
            check_dir = current_dir
            while check_dir != os.path.dirname(check_dir):  # Not at root
                if os.path.basename(check_dir) == 'civic_desktop':
                    civic_desktop_dir = check_dir
                    break
                check_dir = os.path.dirname(check_dir)
            
            if civic_desktop_dir:
                return os.path.join(civic_desktop_dir, 'config', 'prod_config.json')
            else:
                return 'config/prod_config.json'
                
        except Exception as e:
            print(f"⚠️ Error finding config path: {e}")
            return 'config/prod_config.json'
    
    def initialize_integrations(self):
        """Initialize blockchain and session management integrations"""
        
        try:
            # Import blockchain
            from blockchain.blockchain import Blockchain
            self.blockchain = Blockchain()
            print("✅ Blockchain integration initialized")
        except ImportError as e:
            print(f"⚠️ Blockchain import error: {e}")
            self.blockchain = None
        except Exception as e:
            print(f"⚠️ Blockchain initialization error: {e}")
            self.blockchain = None
        
        try:
            # Import session manager
            from users.session import SessionManager
            self.session_manager = SessionManager()
            print("✅ Session manager integration initialized")
        except ImportError as e:
            print(f"⚠️ Session manager import error: {e}")
            self.session_manager = None
        except Exception as e:
            print(f"⚠️ Session manager initialization error: {e}")
            self.session_manager = None
    
    def load_government_data(self):
        """Load government officials data from the directory"""
        
        try:
            # Find government directory
            government_dir = self.find_government_directory()
            if not government_dir:
                print("⚠️ Government directory not found, using sample data")
                self.load_sample_data()
                return
            
            # Load officials from government directory
            officials_file = os.path.join(government_dir, 'government_officials_directory.json')
            
            if os.path.exists(officials_file):
                with open(officials_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.officials_cache = self.process_officials_data(data)
                self.last_update = datetime.now()
                
                print(f"✅ Loaded {len(self.officials_cache)} officials from government directory")
            else:
                print(f"⚠️ Government officials file not found: {officials_file}")
                self.load_sample_data()
                
        except Exception as e:
            print(f"❌ Error loading government data: {e}")
            self.load_sample_data()
    
    def find_government_directory(self) -> Optional[str]:
        """Find the government directory"""
        
        # Try multiple possible paths
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'government', 'government_directory'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'government', 'government_directory'),
            'government/government_directory',
            '../government/government_directory',
            'civic_desktop/government/government_directory'
        ]
        
        for path in possible_paths:
            full_path = os.path.abspath(path)
            if os.path.exists(full_path):
                return full_path
        
        return None
    
    def process_officials_data(self, raw_data: Dict) -> Dict[str, Dict]:
        """Process raw officials data into map format"""
        
        processed_officials = {}
        
        for official_id, official_data in raw_data.items():
            if not isinstance(official_data, dict):
                continue
            
            # Get coordinates for the official
            lat, lon = self.get_coordinates_for_official(official_data)
            
            # Process official data
            processed_official = {
                'id': official_id,
                'name': official_data.get('name', 'Unknown Official'),
                'title': official_data.get('title', 'Government Official'),
                'country': official_data.get('country', 'Unknown'),
                'jurisdiction': official_data.get('jurisdiction', 'Unknown'),
                'party_affiliation': official_data.get('party_affiliation', 'Independent'),
                'email': official_data.get('email', ''),
                'phone': official_data.get('phone', ''),
                'verification_status': official_data.get('verification_status', 'uncontacted'),
                'lat': lat,
                'lon': lon,
                'type': self.determine_official_type(official_data.get('title', '')),
                'last_updated': datetime.now().isoformat()
            }
            
            processed_officials[official_id] = processed_official
        
        return processed_officials
    
    def get_coordinates_for_official(self, official_data: Dict) -> Tuple[float, float]:
        """Get geographic coordinates for an official based on their location"""
        
        # Coordinate mapping for major government centers
        location_coords = {
            # United States - Federal
            "United States": (38.9072, -77.0369),  # Washington DC
            "Washington, D.C.": (38.9072, -77.0369),
            
            # US States (capitals)
            "California": (38.5816, -121.4944),    # Sacramento
            "Texas": (30.2672, -97.7431),          # Austin
            "Florida": (30.4518, -84.27277),       # Tallahassee
            "New York": (42.6526, -73.7562),       # Albany
            "Illinois": (39.7817, -89.6501),       # Springfield
            "Pennsylvania": (40.2732, -76.8839),   # Harrisburg
            
            # Major US Cities
            "New York City": (40.7128, -74.0060),
            "Los Angeles": (34.0522, -118.2437),
            "Chicago": (41.8781, -87.6298),
            "Houston": (29.7604, -95.3698),
            "Phoenix": (33.4484, -112.0740),
            "Philadelphia": (39.9526, -75.1652),
            
            # International Capitals
            "United Kingdom": (51.5074, -0.1278),  # London
            "Germany": (52.5200, 13.4050),         # Berlin
            "France": (48.8566, 2.3522),           # Paris
            "Japan": (35.6762, 139.6503),          # Tokyo
            "Canada": (45.4215, -75.6972),         # Ottawa
            "Italy": (41.9028, 12.4964),           # Rome
            "Spain": (40.4168, -3.7038),           # Madrid
            "Australia": (-35.2809, 149.1300),     # Canberra
            "India": (28.6139, 77.2090),           # New Delhi
            "China": (39.9042, 116.4074),          # Beijing
        }
        
        # Try to match by jurisdiction, country, or title
        jurisdiction = official_data.get('jurisdiction', '')
        country = official_data.get('country', '')
        title = official_data.get('title', '')
        
        # Check jurisdiction first
        if jurisdiction in location_coords:
            return location_coords[jurisdiction]
        
        # Check country
        if country in location_coords:
            return location_coords[country]
        
        # Check for city names in title or jurisdiction
        for location, coords in location_coords.items():
            if location.lower() in jurisdiction.lower() or location.lower() in title.lower():
                return coords
        
        # Default to center of USA if no match found
        return (39.8283, -98.5795)
    
    def determine_official_type(self, title: str) -> str:
        """Determine the type of official based on their title"""
        
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
        elif 'representative' in title_lower or 'congressman' in title_lower or 'congresswoman' in title_lower:
            return 'representative'
        elif 'minister' in title_lower:
            return 'minister'
        elif 'chancellor' in title_lower:
            return 'chancellor'
        else:
            return 'other'
    
    def load_sample_data(self):
        """Load sample officials data for testing"""
        
        sample_officials = {
            'us_president': {
                'name': 'Donald J. Trump',
                'title': 'President of the United States (47th)',
                'country': 'United States',
                'jurisdiction': 'United States',
                'party_affiliation': 'Republican',
                'lat': 38.9072,
                'lon': -77.0369,
                'type': 'president',
                'verification_status': 'verified'
            },
            'us_vp': {
                'name': 'J.D. Vance',
                'title': 'Vice President of the United States',
                'country': 'United States',
                'jurisdiction': 'United States',
                'party_affiliation': 'Republican',
                'lat': 38.9072,
                'lon': -77.0369,
                'type': 'vice_president',
                'verification_status': 'verified'
            },
            'uk_pm': {
                'name': 'Keir Starmer',
                'title': 'Prime Minister of the United Kingdom',
                'country': 'United Kingdom',
                'jurisdiction': 'United Kingdom',
                'party_affiliation': 'Labour',
                'lat': 51.5074,
                'lon': -0.1278,
                'type': 'prime_minister',
                'verification_status': 'verified'
            }
        }
        
        self.officials_cache = sample_officials
        print("✅ Loaded sample officials data")
    
    def get_user_permissions(self) -> Dict[str, Any]:
        """Get current user's permissions for map data access"""
        
        if not self.session_manager or not self.session_manager.is_authenticated():
            return self.get_guest_permissions()
        
        try:
            user = self.session_manager.get_current_user()
            if not user:
                return self.get_guest_permissions()
            
            user_role = user.get('role', 'Contract Citizen')
            
            # Role-based permissions
            if user_role in ['Contract Founder', 'Contract Elder']:
                return {
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_location_data': True,
                    'can_view_sensitive_data': True,
                    'jurisdiction_filter': [],
                    'role_level': 'administrative',
                    'max_officials': -1  # Unlimited
                }
            elif user_role in ['Contract Representative', 'Contract Senator']:
                return {
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_location_data': True,
                    'can_view_sensitive_data': False,
                    'jurisdiction_filter': [user.get('jurisdiction', ''), user.get('country', '')],
                    'role_level': 'government',
                    'max_officials': 100
                }
            elif user_role == 'Contract Citizen':
                return {
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_location_data': False,
                    'can_view_sensitive_data': False,
                    'jurisdiction_filter': [user.get('country', 'United States')],
                    'role_level': 'citizen',
                    'max_officials': 50
                }
            else:
                return self.get_guest_permissions()
                
        except Exception as e:
            print(f"❌ Error getting user permissions: {e}")
            return self.get_guest_permissions()
    
    def get_guest_permissions(self) -> Dict[str, Any]:
        """Get permissions for guest users"""
        
        return {
            'can_view_officials': True,
            'can_view_activities': False,
            'can_view_location_data': False,
            'can_view_sensitive_data': False,
            'jurisdiction_filter': ['United States'],
            'role_level': 'guest',
            'max_officials': 20
        }
    
    def get_filtered_officials(self, permissions: Dict[str, Any] = None) -> List[Dict]:
        """Get officials list filtered by user permissions"""
        
        if permissions is None:
            permissions = self.get_user_permissions()
        
        if not permissions.get('can_view_officials', False):
            return []
        
        # Get all officials
        all_officials = list(self.officials_cache.values())
        
        # Apply jurisdiction filter for non-admin users
        if permissions.get('role_level') != 'administrative':
            jurisdiction_filter = permissions.get('jurisdiction_filter', [])
            if jurisdiction_filter:
                filtered_officials = []
                for official in all_officials:
                    if (official.get('country') in jurisdiction_filter or
                        official.get('jurisdiction') in jurisdiction_filter):
                        filtered_officials.append(official)
                all_officials = filtered_officials
        
        # Apply count limit
        max_officials = permissions.get('max_officials', -1)
        if max_officials > 0:
            all_officials = all_officials[:max_officials]
        
        # Remove sensitive data for non-privileged users
        if not permissions.get('can_view_sensitive_data', False):
            for official in all_officials:
                official['phone'] = 'Restricted'
                if official.get('email') and '@' in official['email']:
                    # Partially mask email
                    email_parts = official['email'].split('@')
                    if len(email_parts[0]) > 2:
                        masked_email = email_parts[0][:2] + '*' * (len(email_parts[0]) - 2) + '@' + email_parts[1]
                        official['email'] = masked_email
        
        return all_officials
    
    def get_civic_activities(self, permissions: Dict[str, Any] = None) -> List[Dict]:
        """Get civic activities based on user permissions"""
        
        if permissions is None:
            permissions = self.get_user_permissions()
        
        if not permissions.get('can_view_activities', False):
            return []
        
        # Generate sample activities (in production, integrate with Events module)
        activities = [
            {
                'id': 'presidential_address_2025',
                'title': 'Presidential Address to Nation',
                'type': 'address',
                'lat': 38.9072,
                'lon': -77.0369,
                'date': '2025-10-15T20:00:00Z',
                'status': 'scheduled',
                'visibility': 'public',
                'description': 'Annual State of the Union Address'
            },
            {
                'id': 'local_town_hall_nyc',
                'title': 'NYC Town Hall Meeting',
                'type': 'town_hall',
                'lat': 40.7128,
                'lon': -74.0060,
                'date': '2025-10-20T19:00:00Z',
                'status': 'upcoming',
                'visibility': 'public',
                'description': 'Community discussion on local issues'
            }
        ]
        
        # Filter activities based on visibility and role
        role_level = permissions.get('role_level', 'guest')
        
        if role_level == 'guest':
            # Guests can only see public activities
            activities = [a for a in activities if a.get('visibility') == 'public']
        
        return activities
    
    def log_map_access(self, action: str, data: Dict[str, Any]) -> bool:
        """Log map access activity to blockchain"""
        
        if not self.blockchain:
            return False
        
        try:
            # Get current user
            user_email = ""
            if self.session_manager and self.session_manager.is_authenticated():
                user = self.session_manager.get_current_user()
                if user:
                    user_email = user.get('email', '')
            
            # Prepare blockchain data
            blockchain_data = {
                'action_type': 'map_access',
                'user_action': action,
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'user_permissions': self.get_user_permissions()
            }
            
            # Add to blockchain
            success = self.blockchain.add_page(
                action_type="map_interaction",
                data=blockchain_data,
                user_email=user_email
            )
            
            if success:
                print(f"✅ Map access logged to blockchain: {action}")
                return True
            else:
                print(f"⚠️ Failed to log map access to blockchain: {action}")
                return False
                
        except Exception as e:
            print(f"❌ Error logging map access to blockchain: {e}")
            return False
    
    def search_officials(self, query: str, permissions: Dict[str, Any] = None) -> List[Dict]:
        """Search officials based on query and user permissions"""
        
        if not query or len(query.strip()) < 2:
            return []
        
        query_lower = query.lower().strip()
        
        # Get filtered officials list
        officials = self.get_filtered_officials(permissions)
        
        # Search through officials
        matching_officials = []
        
        for official in officials:
            # Search in name, title, jurisdiction, country
            searchable_text = " ".join([
                official.get('name', ''),
                official.get('title', ''),
                official.get('jurisdiction', ''),
                official.get('country', ''),
                official.get('party_affiliation', '')
            ]).lower()
            
            if query_lower in searchable_text:
                # Add relevance score
                relevance = 0
                if query_lower in official.get('name', '').lower():
                    relevance += 10
                if query_lower in official.get('title', '').lower():
                    relevance += 5
                if query_lower in official.get('jurisdiction', '').lower():
                    relevance += 3
                
                official_copy = official.copy()
                official_copy['relevance'] = relevance
                matching_officials.append(official_copy)
        
        # Sort by relevance
        matching_officials.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        # Log search to blockchain
        self.log_map_access('search_performed', {
            'query': query,
            'results_count': len(matching_officials)
        })
        
        return matching_officials
    
    def get_official_details(self, official_id: str, permissions: Dict[str, Any] = None) -> Optional[Dict]:
        """Get detailed information about a specific official"""
        
        if official_id not in self.officials_cache:
            return None
        
        if permissions is None:
            permissions = self.get_user_permissions()
        
        if not permissions.get('can_view_officials', False):
            return None
        
        official = self.officials_cache[official_id].copy()
        
        # Apply permission-based filtering
        jurisdiction_filter = permissions.get('jurisdiction_filter', [])
        if (permissions.get('role_level') != 'administrative' and 
            jurisdiction_filter and 
            official.get('country') not in jurisdiction_filter and
            official.get('jurisdiction') not in jurisdiction_filter):
            return None
        
        # Remove sensitive data if user doesn't have permission
        if not permissions.get('can_view_sensitive_data', False):
            official['phone'] = 'Restricted'
            if official.get('email') and '@' in official['email']:
                email_parts = official['email'].split('@')
                if len(email_parts[0]) > 2:
                    masked_email = email_parts[0][:2] + '*' * (len(email_parts[0]) - 2) + '@' + email_parts[1]
                    official['email'] = masked_email
        
        # Log access to blockchain
        self.log_map_access('official_accessed', {
            'official_id': official_id,
            'official_name': official.get('name', 'Unknown')
        })
        
        return official
    
    def get_map_statistics(self) -> Dict[str, Any]:
        """Get statistics about map data"""
        
        permissions = self.get_user_permissions()
        
        officials = self.get_filtered_officials(permissions)
        activities = self.get_civic_activities(permissions)
        
        stats = {
            'total_officials': len(officials),
            'total_activities': len(activities),
            'user_role': permissions.get('role_level', 'guest'),
            'can_view_officials': permissions.get('can_view_officials', False),
            'can_view_activities': permissions.get('can_view_activities', False),
            'jurisdiction_filter': permissions.get('jurisdiction_filter', []),
            'last_updated': self.last_update.isoformat() if self.last_update else None
        }
        
        # Count officials by type
        official_types = {}
        for official in officials:
            official_type = official.get('type', 'other')
            official_types[official_type] = official_types.get(official_type, 0) + 1
        
        stats['officials_by_type'] = official_types
        
        # Count by jurisdiction
        jurisdictions = {}
        for official in officials:
            jurisdiction = official.get('jurisdiction', 'Unknown')
            jurisdictions[jurisdiction] = jurisdictions.get(jurisdiction, 0) + 1
        
        stats['officials_by_jurisdiction'] = jurisdictions
        
        return stats
    
    def refresh_data(self) -> bool:
        """Refresh all map data from sources"""
        
        try:
            print("🔄 Refreshing map data...")
            
            # Reload government data
            self.load_government_data()
            
            # Log refresh to blockchain
            self.log_map_access('data_refreshed', {
                'officials_count': len(self.officials_cache),
                'refresh_time': datetime.now().isoformat()
            })
            
            print("✅ Map data refreshed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error refreshing map data: {e}")
            return False


# Test function
def test_map_data_manager():
    """Test the map data manager"""
    
    print("🗺️ Testing Map Data Manager...")
    
    # Initialize manager
    manager = MapDataManager()
    
    # Test permissions
    permissions = manager.get_user_permissions()
    print(f"📋 User Permissions: {permissions}")
    
    # Test getting officials
    officials = manager.get_filtered_officials()
    print(f"👥 Officials Available: {len(officials)}")
    
    for official in officials[:3]:  # Show first 3
        print(f"   • {official.get('name')} - {official.get('title')}")
    
    # Test activities
    activities = manager.get_civic_activities()
    print(f"📊 Activities Available: {len(activities)}")
    
    # Test search
    search_results = manager.search_officials("president")
    print(f"🔍 Search Results for 'president': {len(search_results)}")
    
    # Test statistics
    stats = manager.get_map_statistics()
    print(f"📈 Map Statistics: {stats}")
    
    print("✅ Map Data Manager test completed")


if __name__ == "__main__":
    test_map_data_manager()