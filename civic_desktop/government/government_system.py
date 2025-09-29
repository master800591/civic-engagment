"""
CLEAN GOVERNMENT INTEGRATION SYSTEM
Simplified, accurate government official database and verification system
Updated for September 2025 with current officials
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class GovernmentIntegrationSystem:
    """Clean, simplified government integration system"""
    
    def __init__(self):
        self.government_path = Path(__file__).parent
        self.data_path = self.government_path / 'government_directory'
        
        # Ensure directory exists
        self.data_path.mkdir(exist_ok=True)
        
        # Database file
        self.database_file = self.data_path / 'accurate_world_government_database.json'
        
        # Load database
        self.database = self._load_database()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load government database"""
        try:
            if self.database_file.exists():
                with open(self.database_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    'officials': {},
                    'countries': {},
                    'statistics': {'total_officials': 0},
                    'metadata': {'last_updated': datetime.now().isoformat()}
                }
        except Exception as e:
            print(f"Error loading database: {e}")
            return {'officials': {}, 'countries': {}, 'statistics': {}, 'metadata': {}}
    
    def get_all_officials(self) -> Dict[str, Any]:
        """Get all government officials"""
        return self.database.get('officials', {})
    
    def get_official_by_id(self, official_id: str) -> Optional[Dict[str, Any]]:
        """Get specific official by ID"""
        return self.database.get('officials', {}).get(official_id)
    
    def get_officials_by_country(self, country: str) -> List[Dict[str, Any]]:
        """Get all officials from a specific country"""
        officials = []
        for official_data in self.database.get('officials', {}).values():
            if official_data.get('country', '').lower() == country.lower():
                officials.append(official_data)
        return officials
    
    def get_officials_by_level(self, level: str) -> List[Dict[str, Any]]:
        """Get officials by jurisdiction level (country, state, city)"""
        officials = []
        for official_data in self.database.get('officials', {}).values():
            if official_data.get('jurisdiction_level', '').lower() == level.lower():
                officials.append(official_data)
        return officials
    
    def verify_government_official(self, email: str, name: str, title: str, 
                                  jurisdiction: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Verify a government official exists in database"""
        
        # Search for official in database
        for official_id, official_data in self.database.get('officials', {}).items():
            if (official_data.get('name', '').lower() == name.lower() and 
                official_data.get('jurisdiction', '').lower() == jurisdiction.lower()):
                
                # Create verified record
                verified_official = {
                    **official_data,
                    'platform_email': email,
                    'verification_date': datetime.now().isoformat(),
                    'verification_status': 'verified',
                    'citizen_verification_authority': True
                }
                
                return True, f"Official verified: {name}", verified_official
        
        return False, f"Official not found in database: {name} - {jurisdiction}", {}
    
    def add_official(self, official_data: Dict[str, Any]) -> bool:
        """Add new official to database"""
        try:
            official_id = official_data.get('official_id')
            if not official_id:
                return False
            
            # Add to database
            self.database['officials'][official_id] = {
                **official_data,
                'last_updated': datetime.now().isoformat()
            }
            
            # Update statistics
            self.database['statistics']['total_officials'] = len(self.database['officials'])
            
            # Save database
            self._save_database()
            
            return True
            
        except Exception as e:
            print(f"Error adding official: {e}")
            return False
    
    def update_official(self, official_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing official"""
        try:
            if official_id in self.database.get('officials', {}):
                self.database['officials'][official_id].update(updates)
                self.database['officials'][official_id]['last_updated'] = datetime.now().isoformat()
                
                self._save_database()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error updating official: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        officials = self.database.get('officials', {})
        
        stats = {
            'total_officials': len(officials),
            'by_country': {},
            'by_level': {},
            'by_priority': {},
            'verified_officials': 0
        }
        
        for official in officials.values():
            # Country statistics
            country = official.get('country', 'Unknown')
            stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
            
            # Level statistics
            level = official.get('jurisdiction_level', 'unknown')
            stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
            
            # Priority statistics
            priority = official.get('priority', 'unknown')
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # Verification status
            if official.get('verification_status') == 'verified':
                stats['verified_officials'] += 1
        
        return stats
    
    def search_officials(self, query: str) -> List[Dict[str, Any]]:
        """Search officials by name, title, or country"""
        results = []
        query_lower = query.lower()
        
        for official in self.database.get('officials', {}).values():
            if (query_lower in official.get('name', '').lower() or
                query_lower in official.get('title', '').lower() or
                query_lower in official.get('country', '').lower() or
                query_lower in official.get('jurisdiction', '').lower()):
                results.append(official)
        
        return results
    
    def _save_database(self):
        """Save database to file"""
        try:
            self.database['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(self.database_file, 'w', encoding='utf-8') as f:
                json.dump(self.database, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving database: {e}")


def main():
    """Main function to demonstrate the clean system"""
    
    print("🏛️  CLEAN GOVERNMENT INTEGRATION SYSTEM")
    print("=" * 50)
    print("Updated for September 2025 with current officials")
    print()
    
    # Initialize system
    gov_system = GovernmentIntegrationSystem()
    
    # Get statistics
    stats = gov_system.get_statistics()
    
    print("📊 DATABASE STATISTICS:")
    print(f"   Total Officials: {stats['total_officials']}")
    print()
    
    print("🌍 BY COUNTRY:")
    for country, count in sorted(stats['by_country'].items()):
        print(f"   {country}: {count}")
    print()
    
    print("🎯 BY PRIORITY:")
    for priority, count in sorted(stats['by_priority'].items()):
        print(f"   {priority.title()}: {count}")
    print()
    
    print("📋 CURRENT WORLD LEADERS:")
    country_officials = gov_system.get_officials_by_level('country')
    for official in sorted(country_officials, key=lambda x: x.get('population_served', 0), reverse=True):
        print(f"   {official.get('name')} - {official.get('title')}")
        print(f"      📧 {official.get('email')}")
        print(f"      👥 Population: {official.get('population_served', 0):,}")
        print()
    
    print("✅ Clean government integration system ready!")


if __name__ == "__main__":
    main()