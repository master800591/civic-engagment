"""
HARDCODED FOUNDER KEYS - Single-Use Promotion Keys
Generated: 2025-09-28T14:18:20.409653
Total Keys: 10

SECURITY NOTE: These keys are hardcoded for distribution and can only be used once each.
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class HardcodedFounderKeys:
    """Manages hardcoded founder keys for single-use promotion"""
    
    # Hardcoded founder keys (hashes only for security)
    FOUNDER_KEYS = [{'id': 'FOUNDER_01', 'key_hash': 'fb772d44deb7bdc6901e11845a120804517b36a159f3bf54dbe90092817ce7e5', 'fingerprint': '54a118ad82a17789a54a4c721db644f88d0f698cc9f6c99eb689f3fba0ef3338', 'blockchain_address': 'civic_54a118ad82a17789a54a', 'used': False}, {'id': 'FOUNDER_02', 'key_hash': '41805f6051b63bd61d6be3d9a706b12345b61a0dac169dab3ad64cce59931d4d', 'fingerprint': 'd3cd60c07b0de90be01c39a18929cd484b67540bc12a00002734a688e95611d9', 'blockchain_address': 'civic_d3cd60c07b0de90be01c', 'used': False}, {'id': 'FOUNDER_03', 'key_hash': 'dd6348e7944d7909b046157279fcc053d9a336f6d1dd857e7a9ccad92c1b47e5', 'fingerprint': '7aa0201be99f0724b702e4dc79ba631f54d1ed9c7c2f7eb44078f906206cce87', 'blockchain_address': 'civic_7aa0201be99f0724b702', 'used': False}, {'id': 'FOUNDER_04', 'key_hash': 'b9fb5f5552f0377ca087a41b7f975ccd3e5c72f862968d9604593e89568f3340', 'fingerprint': 'd74f9d992824016178022b5478366a9f3a0c9a2edb787be06a78a5c51cce5aca', 'blockchain_address': 'civic_d74f9d99282401617802', 'used': False}, {'id': 'FOUNDER_05', 'key_hash': '9e37874f9331b1f9dc5329e7fee9aff3f839aba5cb2150bf0e1cc58d1e7d6a13', 'fingerprint': 'a1fd339f20324edecdff030442ccc285d216957e603887505a0ab09a12f12549', 'blockchain_address': 'civic_a1fd339f20324edecdff', 'used': False}, {'id': 'FOUNDER_06', 'key_hash': '05f7abd41e82dba304760999d4ea093b882123b14c110adf047dcca52b531e83', 'fingerprint': '6612ef9627b2410054987ebde5851202c5eafed5d93d9895e240be54b8ac90ff', 'blockchain_address': 'civic_6612ef9627b241005498', 'used': False}, {'id': 'FOUNDER_07', 'key_hash': '3e5c1c9c4e7d36a5fb4dd0c734d5a4866785a3126c61dc4faaba99c7960427f0', 'fingerprint': '0e91efee8b98311f6875fe6c2ca11989edbf822ec31dc7bce09d42b7a798ada9', 'blockchain_address': 'civic_0e91efee8b98311f6875', 'used': False}, {'id': 'FOUNDER_08', 'key_hash': 'f44ffe69cc9a063d4e4a7aff163dd81a620c3bff8b1f0515569a9352e8733159', 'fingerprint': '889910051f47334a4b15b9ea22849a11b8a1811e4a39bfc38e5b7a5cd2f1d8a7', 'blockchain_address': 'civic_889910051f47334a4b15', 'used': False}, {'id': 'FOUNDER_09', 'key_hash': 'd3a6d6f7476e72afbef4f94049507078d78235e2f615dcaa3c3b6d69dbdbd220', 'fingerprint': 'a7b9ee44f4948650bb8f05d76cefd1edd74163b9c6d90ddbd4a7b3e6614d6005', 'blockchain_address': 'civic_a7b9ee44f4948650bb8f', 'used': False}, {'id': 'FOUNDER_10', 'key_hash': 'f8d06cd41f354f2514507685489c5cd64e8e917940d4d6d05fb188060981e5f1', 'fingerprint': 'a3a9870ef86c195f02c72cff75d18491f45114414b54f134a075c8943845d485', 'blockchain_address': 'civic_a3a9870ef86c195f02c7', 'used': False}]
    
    # Track used keys (will be persisted)
    _used_keys_file = "users/used_founder_keys.json"
    
    @classmethod
    def validate_founder_key(cls, private_key_pem: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate a founder private key and mark as used if valid
        Returns: (is_valid, message, founder_info)
        """
        import json
        from pathlib import Path
        
        # Calculate hash of provided key
        key_hash = hashlib.sha256(private_key_pem.encode()).hexdigest()
        
        # Load used keys
        used_keys = cls._load_used_keys()
        
        # Check if key has already been used
        if key_hash in used_keys:
            return False, "This founder key has already been used", None
        
        # Find matching hardcoded key
        matching_key = None
        for key_data in cls.FOUNDER_KEYS:
            if key_data['key_hash'] == key_hash:
                matching_key = key_data
                break
        
        if not matching_key:
            return False, "Invalid founder key - not recognized", None
        
        # Mark key as used
        used_keys[key_hash] = {
            'founder_id': matching_key['id'],
            'used_at': datetime.now().isoformat(),
            'fingerprint': matching_key['fingerprint'],
            'blockchain_address': matching_key['blockchain_address']
        }
        
        # Save used keys
        cls._save_used_keys(used_keys)
        
        return True, "Founder key validated and marked as used", {
            'founder_id': matching_key['id'],
            'key_fingerprint': matching_key['fingerprint'],
            'blockchain_address': matching_key['blockchain_address'],
            'is_founder_key': True,
            'single_use': True,
            'used_at': used_keys[key_hash]['used_at']
        }
    
    @classmethod
    def _load_used_keys(cls) -> Dict:
        """Load used keys from file"""
        import json
        from pathlib import Path
        
        used_keys_path = Path(cls._used_keys_file)
        if used_keys_path.exists():
            try:
                with open(used_keys_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    @classmethod
    def _save_used_keys(cls, used_keys: Dict):
        """Save used keys to file"""
        import json
        from pathlib import Path
        
        used_keys_path = Path(cls._used_keys_file)
        used_keys_path.parent.mkdir(exist_ok=True)
        
        with open(used_keys_path, 'w') as f:
            json.dump(used_keys, f, indent=2)
    
    @classmethod
    def get_key_status(cls) -> Dict:
        """Get status of all founder keys"""
        used_keys = cls._load_used_keys()
        
        total_keys = len(cls.FOUNDER_KEYS)
        used_count = len(used_keys)
        available_count = total_keys - used_count
        
        return {
            'total_keys': total_keys,
            'used_keys': used_count,
            'available_keys': available_count,
            'used_key_details': used_keys
        }
    
    @classmethod
    def is_key_available(cls, key_hash: str) -> bool:
        """Check if a key is still available for use"""
        used_keys = cls._load_used_keys()
        return key_hash not in used_keys
