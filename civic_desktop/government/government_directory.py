"""
CLEAN GOVERNMENT DIRECTORY SYSTEM
Simple government official management with hierarchical verification
Updated for September 2025
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class GovernmentDirectory:
    """Simple government directory management"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent / 'government_directory'
        self.data_path.mkdir(exist_ok=True)
        
        self.database_file = self.data_path / 'accurate_world_government_database.json'
        self.directory_file = self.data_path / 'government_officials_directory.json'
        
        self.database = self._load_database()
        self.directory = self._load_directory()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load main government database"""
        if self.database_file.exists():
            with open(self.database_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'officials': {}, 'countries': {}}
    
    def _load_directory(self) -> Dict[str, Any]:
        """Load or create directory structure"""
        if self.directory_file.exists():
            with open(self.directory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'verified_officials': {},
            'verification_chains': {
                'founders': [],
                'country_leaders': {},
                'state_leaders': {},
                'city_leaders': {}
            },
            'contact_log': {},
            'metadata': {
                'created': datetime.now().isoformat(),
                'version': '2.0.0'
            }
        }
    
    def verify_official(self, verifier_email: str, official_id: str, 
                       verification_notes: str = "") -> bool:
        """Verify an official (simplified process)"""
        
        if official_id not in self.database.get('officials', {}):
            return False
        
        official_data = self.database['officials'][official_id]
        
        # Create verification record
        verification = {
            'verified_by': verifier_email,
            'verification_date': datetime.now().isoformat(),
            'verification_notes': verification_notes,
            'official_data': official_data,
            'status': 'verified'
        }
        
        # Store verification
        self.directory['verified_officials'][official_id] = verification
        
        # Update verification chain based on level
        level = official_data.get('jurisdiction_level', 'unknown')
        if level == 'country':
            self.directory['verification_chains']['country_leaders'][official_id] = verification
        elif level == 'state':
            self.directory['verification_chains']['state_leaders'][official_id] = verification
        elif level == 'city':
            self.directory['verification_chains']['city_leaders'][official_id] = verification
        
        self._save_directory()
        return True
    
    def get_verified_officials(self) -> Dict[str, Any]:
        """Get all verified officials"""
        return self.directory.get('verified_officials', {})
    
    def get_officials_by_country(self, country: str) -> List[Dict[str, Any]]:
        """Get officials from specific country"""
        officials = []
        for official in self.database.get('officials', {}).values():
            if official.get('country', '').lower() == country.lower():
                officials.append(official)
        return officials
    
    def search_officials(self, query: str) -> List[Dict[str, Any]]:
        """Search officials by name or title"""
        results = []
        query_lower = query.lower()
        
        for official in self.database.get('officials', {}).values():
            if (query_lower in official.get('name', '').lower() or
                query_lower in official.get('title', '').lower()):
                results.append(official)
        
        return results
    
    def record_contact(self, official_id: str, contact_method: str, 
                      contact_notes: str, success: bool = False):
        """Record contact attempt with official"""
        
        contact_record = {
            'contact_date': datetime.now().isoformat(),
            'contact_method': contact_method,
            'contact_notes': contact_notes,
            'success': success
        }
        
        if official_id not in self.directory['contact_log']:
            self.directory['contact_log'][official_id] = []
        
        self.directory['contact_log'][official_id].append(contact_record)
        self._save_directory()
    
    def get_directory_stats(self) -> Dict[str, Any]:
        """Get directory statistics"""
        
        total_officials = len(self.database.get('officials', {}))
        verified_officials = len(self.directory.get('verified_officials', {}))
        contacted_officials = len(self.directory.get('contact_log', {}))
        
        return {
            'total_officials': total_officials,
            'verified_officials': verified_officials,
            'contacted_officials': contacted_officials,
            'verification_rate': (verified_officials / total_officials * 100) if total_officials > 0 else 0,
            'contact_rate': (contacted_officials / total_officials * 100) if total_officials > 0 else 0
        }
    
    def _save_directory(self):
        """Save directory to file"""
        self.directory['metadata']['last_updated'] = datetime.now().isoformat()
        
        with open(self.directory_file, 'w', encoding='utf-8') as f:
            json.dump(self.directory, f, indent=2, ensure_ascii=False)


def main():
    """Demo the clean government directory"""
    
    print("🏛️  CLEAN GOVERNMENT DIRECTORY SYSTEM")
    print("=" * 50)
    
    directory = GovernmentDirectory()
    stats = directory.get_directory_stats()
    
    print("📊 DIRECTORY STATISTICS:")
    print(f"   Total Officials: {stats['total_officials']}")
    print(f"   Verified Officials: {stats['verified_officials']}")
    print(f"   Contacted Officials: {stats['contacted_officials']}")
    print(f"   Verification Rate: {stats['verification_rate']:.1f}%")
    print(f"   Contact Rate: {stats['contact_rate']:.1f}%")
    print()
    
    print("✅ Clean government directory ready!")


if __name__ == "__main__":
    main()