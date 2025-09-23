# Blockchain Cryptographic Signatures
import os
import json
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


from typing import Any, Dict

class BlockchainSigner:
    """Handles cryptographic signing and verification for blockchain blocks"""
    
    @staticmethod
    def load_private_key(email: str) -> Any:
        """Load private key for a user by email"""
        try:
            privkey_dir = os.path.join(os.path.dirname(__file__), '../users/private_keys')
            privkey_path = os.path.join(privkey_dir, f"{email.replace('@','_at_')}.pem")
            
            if not os.path.exists(privkey_path):
                raise FileNotFoundError(f"Private key not found for {email}")
            
            with open(privkey_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(), password=None, backend=default_backend()
                )
            return private_key
        except Exception as e:
            raise Exception(f"Failed to load private key for {email}: {str(e)}")
    
    @staticmethod
    def load_public_key_from_pem(public_key_pem: str) -> Any:
        """Load public key from PEM string"""
        try:
            return serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'), 
                backend=default_backend()
            )
        except Exception as e:
            raise Exception(f"Failed to load public key: {str(e)}")
    
    @staticmethod
    def sign_block_data(block_data: Dict[str, Any], validator_email: str) -> str:
        """Sign block data with validator's private key"""
        try:
            # Create canonical JSON representation for signing
            canonical_data = json.dumps(block_data, sort_keys=True, separators=(',', ':'))
            data_bytes = canonical_data.encode('utf-8')
            
            # Load validator's private key
            private_key = BlockchainSigner.load_private_key(validator_email)
            
            # Sign the data
            signature = private_key.sign(
                data_bytes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # Return base64 encoded signature
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Failed to sign block: {str(e)}")
    
    @staticmethod
    def verify_block_signature(block_data: Dict[str, Any], signature: str, validator_public_key: str) -> bool:
        """Verify block signature using validator's public key"""
        try:
            # Skip verification for system/genesis blocks
            if signature in ['GENESIS', 'PERIODIC', 'SYSTEM']:
                return True
            
            # Create canonical JSON representation
            canonical_data = json.dumps(block_data, sort_keys=True, separators=(',', ':'))
            data_bytes = canonical_data.encode('utf-8')
            
            # Load public key
            public_key = BlockchainSigner.load_public_key_from_pem(validator_public_key)
            
            # Decode signature
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            
            # Verify signature
            public_key.verify(
                signature_bytes,
                data_bytes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            print(f"Signature verification failed: {str(e)}")
            return False
    
    @staticmethod
    def get_validator_public_key(validator_email: str) -> str:
        """Get public key for a validator from user database"""
        try:
            from ..users.backend import UserBackend
            users = UserBackend.load_users()
            
            for user in users:
                if user.get('email') == validator_email:
                    return user.get('public_key', '')
            
            raise Exception(f"Public key not found for validator {validator_email}")
            
        except Exception as e:
            raise Exception(f"Failed to get public key: {str(e)}")