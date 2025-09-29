"""
CLEAN CITIZEN VERIFICATION SYSTEM
Government officials verify platform users as legitimate citizens
Simplified for September 2025
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class CitizenVerification:
    """Simple citizen verification by government officials"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent / 'government_directory'
        self.data_path.mkdir(exist_ok=True)
        
        self.verification_file = self.data_path / 'citizen_verifications.json'
        self.verifications = self._load_verifications()
    
    def _load_verifications(self) -> Dict[str, Any]:
        """Load citizen verifications"""
        if self.verification_file.exists():
            with open(self.verification_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'verifications': {},
            'verified_citizens': {},
            'government_verifiers': {},
            'statistics': {
                'total_verifications': 0,
                'verified_citizens': 0,
                'active_verifiers': 0
            },
            'metadata': {
                'created': datetime.now().isoformat(),
                'version': '2.0.0'
            }
        }
    
    def verify_citizen(self, verifier_email: str, citizen_email: str, 
                      citizen_name: str, jurisdiction: str, 
                      verification_type: str = "citizenship") -> Tuple[bool, str]:
        """Government official verifies a citizen"""
        
        verification_id = f"verify_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.verifications['verifications'])}"
        
        verification_record = {
            'verification_id': verification_id,
            'verifier_email': verifier_email,
            'citizen_email': citizen_email,
            'citizen_name': citizen_name,
            'jurisdiction': jurisdiction,
            'verification_type': verification_type,
            'verification_date': datetime.now().isoformat(),
            'status': 'verified',
            'notes': f"Verified by government official in {jurisdiction}"
        }
        
        # Store verification
        self.verifications['verifications'][verification_id] = verification_record
        
        # Add to verified citizens
        if citizen_email not in self.verifications['verified_citizens']:
            self.verifications['verified_citizens'][citizen_email] = []
        
        self.verifications['verified_citizens'][citizen_email].append(verification_record)
        
        # Track government verifier
        if verifier_email not in self.verifications['government_verifiers']:
            self.verifications['government_verifiers'][verifier_email] = {
                'verifications_performed': 0,
                'first_verification': datetime.now().isoformat()
            }
        
        self.verifications['government_verifiers'][verifier_email]['verifications_performed'] += 1
        self.verifications['government_verifiers'][verifier_email]['last_verification'] = datetime.now().isoformat()
        
        # Update statistics
        self.verifications['statistics']['total_verifications'] += 1
        self.verifications['statistics']['verified_citizens'] = len(self.verifications['verified_citizens'])
        self.verifications['statistics']['active_verifiers'] = len(self.verifications['government_verifiers'])
        
        self._save_verifications()
        
        return True, f"Citizen {citizen_name} verified in {jurisdiction}"
    
    def get_citizen_verifications(self, citizen_email: str) -> List[Dict[str, Any]]:
        """Get all verifications for a citizen"""
        return self.verifications['verified_citizens'].get(citizen_email, [])
    
    def is_citizen_verified(self, citizen_email: str, jurisdiction: str = None) -> bool:
        """Check if citizen is verified (optionally in specific jurisdiction)"""
        verifications = self.get_citizen_verifications(citizen_email)
        
        if not jurisdiction:
            return len(verifications) > 0
        
        for verification in verifications:
            if jurisdiction.lower() in verification.get('jurisdiction', '').lower():
                return True
        
        return False
    
    def get_verifier_stats(self, verifier_email: str) -> Dict[str, Any]:
        """Get statistics for a government verifier"""
        return self.verifications['government_verifiers'].get(verifier_email, {})
    
    def search_verifications(self, query: str) -> List[Dict[str, Any]]:
        """Search verifications by citizen name or jurisdiction"""
        results = []
        query_lower = query.lower()
        
        for verification in self.verifications['verifications'].values():
            if (query_lower in verification.get('citizen_name', '').lower() or
                query_lower in verification.get('jurisdiction', '').lower()):
                results.append(verification)
        
        return results
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get verification statistics"""
        return self.verifications.get('statistics', {})
    
    def _save_verifications(self):
        """Save verifications to file"""
        self.verifications['metadata']['last_updated'] = datetime.now().isoformat()
        
        with open(self.verification_file, 'w', encoding='utf-8') as f:
            json.dump(self.verifications, f, indent=2, ensure_ascii=False)


def main():
    """Demo the clean citizen verification system"""
    
    print("👥 CLEAN CITIZEN VERIFICATION SYSTEM")
    print("=" * 50)
    
    verifier = CitizenVerification()
    stats = verifier.get_verification_stats()
    
    print("📊 VERIFICATION STATISTICS:")
    print(f"   Total Verifications: {stats.get('total_verifications', 0)}")
    print(f"   Verified Citizens: {stats.get('verified_citizens', 0)}")
    print(f"   Active Verifiers: {stats.get('active_verifiers', 0)}")
    print()
    
    print("✅ Clean citizen verification system ready!")
    print("🏛️ Government officials can now verify citizens!")


if __name__ == "__main__":
    main()