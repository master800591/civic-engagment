"""
HARDCODED FOUNDER KEYS - Single-Use Promotion Keys
Generated: 2025-09-28T14:25:26.264617
Total Keys: 10

SECURITY NOTE: These keys are hardcoded for distribution and can only be used once each.
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class HardcodedFounderKeys:
    """Manages hardcoded founder keys for single-use promotion"""
    
    # Hardcoded founder keys (hashes only for security)
    FOUNDER_KEYS = [{'id': 'FOUNDER_01', 'key_hash': '54dc714bc3ee7f284245d89e4430796f78fb50d326763396be48113e230534f3', 'fingerprint': 'b78393e47b0cc212070bbd1f8c830e7ac144eb9242c928f6340bb5f47614ec3f', 'blockchain_address': 'civic_b78393e47b0cc212070b', 'used': False}, {'id': 'FOUNDER_02', 'key_hash': 'ecdda39d066de9c1ad21c4a50bcdc20f782e04c529d91158417c39cf565e2350', 'fingerprint': '27e61c66111276987cc82e360e4e51b00128e67f6ddf59411a41ec5935cd378c', 'blockchain_address': 'civic_27e61c66111276987cc8', 'used': False}, {'id': 'FOUNDER_03', 'key_hash': '8407507c1cc07824a4fe3230ac958b5ef3d4e47922cf219345f1f506771544b1', 'fingerprint': 'f346c52d77856d07a4308af3fe213dd32a94f868dcbe7cca05f026482558fdac', 'blockchain_address': 'civic_f346c52d77856d07a430', 'used': False}, {'id': 'FOUNDER_04', 'key_hash': 'dd8681859d2b7bd06c0e670e52f8166eaff86a39b43cbc166698114d8c4d4fdb', 'fingerprint': '14290a130d6df96dfeeaf7b6717c4a301dd948ac333cea4a8d9e466ecf753d4f', 'blockchain_address': 'civic_14290a130d6df96dfeea', 'used': False}, {'id': 'FOUNDER_05', 'key_hash': 'b89589739675476ac984dd09166111ea62e8ae5ea3acb37b645520e5429e1d56', 'fingerprint': '034e1f466e05189eb073a0ba13273dedab7905eff783d457e126868c8cf24949', 'blockchain_address': 'civic_034e1f466e05189eb073', 'used': False}, {'id': 'FOUNDER_06', 'key_hash': '7b166d8effcea9f6e59a523c3f44092f5d7ad9f26573fe3866f01a475961fe19', 'fingerprint': 'd393c17afc89464ac3da75abc63d07b2c8b1f985b7caa4ad3bde7208a54a4872', 'blockchain_address': 'civic_d393c17afc89464ac3da', 'used': False}, {'id': 'FOUNDER_07', 'key_hash': '3a0425fb9ae6f3700a37e1fa4a9f47d85b8248749fb31b9c64bb5418e3c8ea0b', 'fingerprint': '32cf36fc9b25dfdf578266666e7b16b8ccfd76936394824cb6f28357c1f54c02', 'blockchain_address': 'civic_32cf36fc9b25dfdf5782', 'used': False}, {'id': 'FOUNDER_08', 'key_hash': '1dfe7f000c34be6fbbe0c6fd1ec4d0dd82864944579c263a02b981c8f7482069', 'fingerprint': '3c424af2fcc2174ba99e92ee37bb3dda7b4b77e3c563c65274cb6bcbf1da89b6', 'blockchain_address': 'civic_3c424af2fcc2174ba99e', 'used': False}, {'id': 'FOUNDER_09', 'key_hash': '1ddcde76e3f6c9b03d8aab6fbb933ef74ecb228fc505a743d3e3cb97188bc34d', 'fingerprint': '26b19996e9c4a9aeaca37aac4dc2f92e81101fb24172c7d44bd15e227c6ea360', 'blockchain_address': 'civic_26b19996e9c4a9aeaca3', 'used': False}, {'id': 'FOUNDER_10', 'key_hash': '50d4035e632608650c2ae26b8444f5cece1a602ec7978654d9579ea3abf638d1', 'fingerprint': '0af92b117fa3450623bf90c11b1850def27dc38c43fcfd3cf5acee5f699c4419', 'blockchain_address': 'civic_0af92b117fa3450623bf', 'used': False}]
    
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
