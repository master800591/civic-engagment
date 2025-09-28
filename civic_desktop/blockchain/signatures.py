"""
BLOCKCHAIN SIGNATURES - Cryptographic validation for blockchain integrity
Handles RSA signatures, validation, and consensus mechanisms
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import base64

try:
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    print("Warning: cryptography library not available for blockchain signatures")
    CRYPTO_AVAILABLE = False

class BlockchainSigner:
    """Handles cryptographic signatures for blockchain validation"""
    
    def __init__(self):
        """Initialize signature manager"""
        self.crypto_available = CRYPTO_AVAILABLE
    
    def sign_block_hash(self, private_key_pem: str, block_hash: str) -> Tuple[bool, str, Optional[str]]:
        """Sign a block hash with private key"""
        
        if not self.crypto_available:
            return False, "Cryptography not available", None
        
        try:
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode(),
                password=None,
                backend=default_backend()
            )
            
            # Sign the hash
            signature = private_key.sign(
                block_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Encode signature as base64
            signature_b64 = base64.b64encode(signature).decode()
            
            return True, "Block signed successfully", signature_b64
            
        except Exception as e:
            return False, f"Signing failed: {str(e)}", None
    
    def verify_block_signature(self, public_key_pem: str, block_hash: str, signature_b64: str) -> Tuple[bool, str]:
        """Verify a block signature"""
        
        if not self.crypto_available:
            return False, "Cryptography not available"
        
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=default_backend()
            )
            
            # Decode signature
            signature = base64.b64decode(signature_b64)
            
            # Verify signature
            public_key.verify(
                signature,
                block_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True, "Signature valid"
            
        except Exception as e:
            return False, f"Signature verification failed: {str(e)}"
    
    def create_validator_signature(self, validator_data: Dict[str, Any], private_key_pem: str) -> Dict[str, str]:
        """Create validator signature for consensus"""
        
        # Create signature payload
        payload = {
            'validator_id': validator_data.get('validator_id'),
            'block_hash': validator_data.get('block_hash'),
            'timestamp': datetime.now().isoformat(),
            'consensus_round': validator_data.get('consensus_round', 1)
        }
        
        # Sign payload
        payload_str = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        
        success, message, signature = self.sign_block_hash(private_key_pem, payload_hash)
        
        if success:
            return {
                'validator_id': payload['validator_id'],
                'signature': signature,
                'timestamp': payload['timestamp'],
                'payload_hash': payload_hash
            }
        else:
            return {
                'validator_id': payload['validator_id'],
                'signature': None,
                'timestamp': payload['timestamp'],
                'error': message
            }

class ConsensusManager:
    """Manages Proof of Authority consensus for blockchain"""
    
    def __init__(self, min_validators: int = 3, consensus_threshold: float = 0.67):
        """Initialize consensus manager"""
        self.min_validators = min_validators
        self.consensus_threshold = consensus_threshold
        self.signer = BlockchainSigner()
    
    def validate_consensus(self, signatures: List[Dict[str, str]], 
                          validators: List[Dict[str, Any]], 
                          block_hash: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate consensus from validator signatures"""
        
        if len(validators) < self.min_validators:
            return False, "Insufficient validators for consensus", {}
        
        valid_signatures = 0
        total_validators = len(validators)
        validation_details = {
            'total_validators': total_validators,
            'required_signatures': int(total_validators * self.consensus_threshold),
            'received_signatures': len(signatures),
            'valid_signatures': 0,
            'invalid_signatures': 0,
            'validator_results': []
        }
        
        # Verify each signature
        for signature_data in signatures:
            validator_id = signature_data.get('validator_id')
            signature = signature_data.get('signature')
            
            # Find validator
            validator = next(
                (v for v in validators if v.get('validator_id') == validator_id), 
                None
            )
            
            if not validator:
                validation_details['validator_results'].append({
                    'validator_id': validator_id,
                    'status': 'unknown_validator',
                    'valid': False
                })
                validation_details['invalid_signatures'] += 1
                continue
            
            # Verify signature
            if signature and validator.get('public_key'):
                is_valid, verify_message = self.signer.verify_block_signature(
                    validator['public_key'],
                    block_hash,
                    signature
                )
                
                if is_valid:
                    valid_signatures += 1
                    validation_details['valid_signatures'] += 1
                    validation_details['validator_results'].append({
                        'validator_id': validator_id,
                        'validator_email': validator.get('user_email'),
                        'status': 'signature_valid',
                        'valid': True
                    })
                else:
                    validation_details['invalid_signatures'] += 1
                    validation_details['validator_results'].append({
                        'validator_id': validator_id,
                        'validator_email': validator.get('user_email'),
                        'status': f'signature_invalid: {verify_message}',
                        'valid': False
                    })
            else:
                validation_details['invalid_signatures'] += 1
                validation_details['validator_results'].append({
                    'validator_id': validator_id,
                    'status': 'missing_signature_or_key',
                    'valid': False
                })
        
        # Check if consensus reached
        required_signatures = int(total_validators * self.consensus_threshold)
        consensus_reached = valid_signatures >= required_signatures
        
        if consensus_reached:
            return True, f"Consensus reached with {valid_signatures}/{total_validators} validators", validation_details
        else:
            return False, f"Consensus failed: {valid_signatures}/{required_signatures} required signatures", validation_details
    
    def create_consensus_round(self, block_hash: str, validators: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new consensus round for block validation"""
        
        consensus_round = {
            'round_id': hashlib.sha256(f"{block_hash}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            'block_hash': block_hash,
            'started_at': datetime.now().isoformat(),
            'validators': [v.get('validator_id') for v in validators],
            'signatures_required': int(len(validators) * self.consensus_threshold),
            'status': 'active',
            'signatures': []
        }
        
        return consensus_round
    
    def add_validator_signature(self, consensus_round: Dict[str, Any], 
                               signature_data: Dict[str, str]) -> Dict[str, Any]:
        """Add validator signature to consensus round"""
        
        # Check if validator already signed
        validator_id = signature_data.get('validator_id')
        existing_signature = next(
            (s for s in consensus_round['signatures'] if s.get('validator_id') == validator_id),
            None
        )
        
        if existing_signature:
            return consensus_round  # Already signed
        
        # Add signature
        consensus_round['signatures'].append(signature_data)
        
        # Check if consensus reached
        if len(consensus_round['signatures']) >= consensus_round['signatures_required']:
            consensus_round['status'] = 'consensus_reached'
            consensus_round['completed_at'] = datetime.now().isoformat()
        
        return consensus_round

class BlockchainValidator:
    """Validates blockchain integrity and consensus"""
    
    def __init__(self):
        """Initialize validator"""
        self.signer = BlockchainSigner()
        self.consensus = ConsensusManager()
    
    def validate_page_chain(self, pages: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Validate a chain of pages for integrity"""
        
        errors = []
        
        if not pages:
            return True, []  # Empty chain is valid
        
        previous_hash = None
        
        for i, page in enumerate(pages):
            # Check required fields
            required_fields = ['page_id', 'timestamp', 'action_type', 'user_email', 'block_hash']
            for field in required_fields:
                if field not in page:
                    errors.append(f"Page {i}: Missing required field '{field}'")
            
            # Validate hash chain
            if i > 0:
                expected_previous = previous_hash
                actual_previous = page.get('previous_hash')
                
                if actual_previous != expected_previous:
                    errors.append(f"Page {i}: Hash chain broken. Expected {expected_previous}, got {actual_previous}")
            
            # Validate page hash
            if 'block_hash' in page:
                # Reconstruct page for hash calculation
                from blockchain import BlockchainPage  # Import here to avoid circular imports
                
                try:
                    page_obj = BlockchainPage(
                        page_id=page['page_id'],
                        timestamp=page['timestamp'],
                        action_type=page['action_type'],
                        user_email=page['user_email'],
                        data=page.get('data', {}),
                        signature=page.get('signature'),
                        validator=page.get('validator'),
                        block_hash=page.get('block_hash'),
                        previous_hash=page.get('previous_hash')
                    )
                    
                    calculated_hash = page_obj.calculate_hash()
                    
                    if calculated_hash != page.get('block_hash'):
                        errors.append(f"Page {i}: Hash mismatch. Calculated {calculated_hash}, stored {page.get('block_hash')}")
                        
                except Exception as e:
                    errors.append(f"Page {i}: Hash validation error: {str(e)}")
            
            previous_hash = page.get('block_hash')
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_chapter_integrity(self, chapter: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate chapter integrity including page chain"""
        
        errors = []
        
        # Check required chapter fields
        required_fields = ['chapter_id', 'start_time', 'end_time', 'pages', 'chapter_hash']
        for field in required_fields:
            if field not in chapter:
                errors.append(f"Chapter: Missing required field '{field}'")
        
        # Validate pages within chapter
        if 'pages' in chapter:
            page_valid, page_errors = self.validate_page_chain(chapter['pages'])
            if not page_valid:
                errors.extend([f"Chapter pages: {error}" for error in page_errors])
        
        # Validate chapter hash
        if 'chapter_id' in chapter and 'start_time' in chapter and 'end_time' in chapter:
            try:
                page_count = len(chapter.get('pages', []))
                chapter_content = f"{chapter['chapter_id']}{chapter['start_time']}{chapter['end_time']}{page_count}"
                calculated_hash = hashlib.sha256(chapter_content.encode()).hexdigest()
                
                if calculated_hash != chapter.get('chapter_hash'):
                    errors.append(f"Chapter: Hash mismatch. Calculated {calculated_hash}, stored {chapter.get('chapter_hash')}")
            
            except Exception as e:
                errors.append(f"Chapter: Hash calculation error: {str(e)}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_validator_eligibility(self, user_email: str, user_role: str) -> Tuple[bool, str]:
        """Validate if user is eligible to be a validator"""
        
        eligible_roles = [
            'contract_representative',
            'contract_senator', 
            'contract_elder',
            'contract_founder'
        ]
        
        if user_role not in eligible_roles:
            return False, f"Role '{user_role}' not eligible for validator status. Must be elected representative."
        
        # Additional checks could be added here:
        # - Verify election status
        # - Check term limits
        # - Verify good standing
        
        return True, "User eligible for validator status"

# Utility functions
def sign_user_action(user_id: str, action_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
    """Sign user action for blockchain - integration point"""
    
    try:
        from users.keys import RSAKeyManager
        key_manager = RSAKeyManager()
        
        # Create action hash
        action_str = json.dumps(action_data, sort_keys=True)
        action_hash = hashlib.sha256(action_str.encode()).hexdigest()
        
        # Sign with user's private key
        return key_manager.sign_message(user_id, action_hash)
        
    except Exception as e:
        return False, f"Signing failed: {str(e)}", None

def verify_user_signature(user_public_key: str, action_data: Dict[str, Any], signature: str) -> Tuple[bool, str]:
    """Verify user signature on action data"""
    
    signer = BlockchainSigner()
    
    # Recreate action hash
    action_str = json.dumps(action_data, sort_keys=True)
    action_hash = hashlib.sha256(action_str.encode()).hexdigest()
    
    # Verify signature
    return signer.verify_block_signature(user_public_key, action_hash, signature)

if __name__ == "__main__":
    # Test signature functionality
    print("🔐 Testing Blockchain Signatures")
    
    signer = BlockchainSigner()
    consensus = ConsensusManager()
    validator = BlockchainValidator()
    
    print(f"✅ Signature modules initialized (Crypto available: {CRYPTO_AVAILABLE})")
    
    # Test validation
    test_pages = [
        {
            'page_id': 'test_001',
            'timestamp': '2025-09-28T10:00:00',
            'action_type': 'user_registration',
            'user_email': 'test@civic.platform',
            'data': {'test': 'data'},
            'block_hash': 'fake_hash_001',
            'previous_hash': None
        }
    ]
    
    is_valid, errors = validator.validate_page_chain(test_pages)
    
    if is_valid:
        print("✅ Test page chain validation passed")
    else:
        print(f"❌ Validation errors: {errors}")
    
    print("🔐 Blockchain signature system ready")