"""
RSA KEY MANAGEMENT - Cryptographic key operations for blockchain participation
Handles RSA key generation, storage, and cryptographic operations for users
"""

import os
import json
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
from datetime import datetime
import hashlib
import base64

try:
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    print("Warning: cryptography library not available. RSA functionality disabled.")
    CRYPTO_AVAILABLE = False

class RSAKeyManager:
    """Manages RSA key pairs for users and blockchain operations"""
    
    def __init__(self, keys_directory: str = "users/private_keys"):
        """Initialize RSA key manager"""
        self.keys_dir = Path(keys_directory)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_key_pair(self, user_id: str, key_size: int = 2048) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Generate RSA key pair for user
        
        Args:
            user_id: Unique user identifier
            key_size: RSA key size in bits (default 2048)
        
        Returns:
            Tuple of (success: bool, message: str, key_info: Optional[Dict])
        """
        if not CRYPTO_AVAILABLE:
            return False, "Cryptography library not available", None
        
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize private key (PEM format)
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Serialize public key (PEM format)
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Create key metadata
            key_info = {
                'user_id': user_id,
                'key_size': key_size,
                'created_at': datetime.now().isoformat(),
                'public_key_pem': public_pem.decode('utf-8'),
                'key_fingerprint': self._generate_fingerprint(public_pem),
                'blockchain_address': self._generate_blockchain_address(public_pem)
            }
            
            # Save private key to secure file
            private_key_file = self.keys_dir / f"{user_id}_private.pem"
            with open(private_key_file, 'wb') as f:
                f.write(private_pem)
            
            # Set secure file permissions (Unix-style)
            try:
                os.chmod(private_key_file, 0o600)  # Read/write for owner only
            except (OSError, AttributeError):
                pass  # Windows doesn't support chmod in the same way
            
            # Save key metadata
            metadata_file = self.keys_dir / f"{user_id}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(key_info, f, indent=2, ensure_ascii=False)
            
            return True, "RSA key pair generated successfully", key_info
            
        except Exception as e:
            return False, f"Failed to generate key pair: {str(e)}", None
    
    def load_user_keys(self, user_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Load user's RSA key pair and metadata
        
        Args:
            user_id: User identifier
        
        Returns:
            Tuple of (success: bool, message: str, key_data: Optional[Dict])
        """
        if not CRYPTO_AVAILABLE:
            return False, "Cryptography library not available", None
        
        try:
            # Check if key files exist
            private_key_file = self.keys_dir / f"{user_id}_private.pem"
            metadata_file = self.keys_dir / f"{user_id}_metadata.json"
            
            if not private_key_file.exists():
                return False, "Private key file not found", None
            
            if not metadata_file.exists():
                return False, "Key metadata file not found", None
            
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                key_info = json.load(f)
            
            # Load private key
            with open(private_key_file, 'rb') as f:
                private_key_pem = f.read()
            
            # Verify key can be loaded
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=default_backend()
            )
            
            # Add loaded key objects to info (for immediate use)
            key_info['private_key_object'] = private_key
            key_info['public_key_object'] = private_key.public_key()
            
            return True, "Keys loaded successfully", key_info
            
        except Exception as e:
            return False, f"Failed to load keys: {str(e)}", None
    
    def sign_message(self, user_id: str, message: str) -> Tuple[bool, str, Optional[str]]:
        """
        Sign a message with user's private key
        
        Args:
            user_id: User identifier
            message: Message to sign
        
        Returns:
            Tuple of (success: bool, message: str, signature: Optional[str])
        """
        if not CRYPTO_AVAILABLE:
            return False, "Cryptography library not available", None
        
        try:
            # Load user's private key
            success, load_msg, key_data = self.load_user_keys(user_id)
            if not success:
                return False, load_msg, None
            
            private_key = key_data['private_key_object']
            message_bytes = message.encode('utf-8')
            
            # Sign the message
            signature_bytes = private_key.sign(
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Encode signature as base64 for storage/transmission
            signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
            
            return True, "Message signed successfully", signature_b64
            
        except Exception as e:
            return False, f"Failed to sign message: {str(e)}", None
    
    def verify_signature(self, public_key_pem: str, message: str, signature_b64: str) -> Tuple[bool, str]:
        """
        Verify a signature against a message and public key
        
        Args:
            public_key_pem: Public key in PEM format
            message: Original message
            signature_b64: Base64-encoded signature
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not CRYPTO_AVAILABLE:
            return False, "Cryptography library not available"
        
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            
            # Decode signature
            signature_bytes = base64.b64decode(signature_b64.encode('utf-8'))
            message_bytes = message.encode('utf-8')
            
            # Verify signature
            public_key.verify(
                signature_bytes,
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True, "Signature valid"
            
        except Exception as e:
            return False, f"Signature verification failed: {str(e)}"
    
    def _generate_fingerprint(self, public_key_pem: bytes) -> str:
        """Generate SHA256 fingerprint of public key"""
        return hashlib.sha256(public_key_pem).hexdigest()[:16]  # First 16 chars
    
    def _generate_blockchain_address(self, public_key_pem: bytes) -> str:
        """Generate blockchain address from public key"""
        # Create a deterministic address from the public key hash
        key_hash = hashlib.sha256(public_key_pem).digest()
        address_hash = hashlib.ripemd160(key_hash).hexdigest() if hasattr(hashlib, 'ripemd160') else hashlib.sha256(key_hash).hexdigest()[:40]
        return f"civic_{address_hash[:32]}"
    
    def get_user_public_key(self, user_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Get user's public key PEM
        
        Args:
            user_id: User identifier
        
        Returns:
            Tuple of (success: bool, message: str, public_key_pem: Optional[str])
        """
        try:
            metadata_file = self.keys_dir / f"{user_id}_metadata.json"
            
            if not metadata_file.exists():
                return False, "Key metadata not found", None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                key_info = json.load(f)
            
            return True, "Public key retrieved", key_info.get('public_key_pem')
            
        except Exception as e:
            return False, f"Failed to get public key: {str(e)}", None
    
    def get_blockchain_address(self, user_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Get user's blockchain address
        
        Args:
            user_id: User identifier
        
        Returns:
            Tuple of (success: bool, message: str, address: Optional[str])
        """
        try:
            metadata_file = self.keys_dir / f"{user_id}_metadata.json"
            
            if not metadata_file.exists():
                return False, "Key metadata not found", None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                key_info = json.load(f)
            
            return True, "Blockchain address retrieved", key_info.get('blockchain_address')
            
        except Exception as e:
            return False, f"Failed to get blockchain address: {str(e)}", None
    
    def list_user_keys(self) -> List[Dict[str, Any]]:
        """List all user keys with metadata"""
        keys_list = []
        
        try:
            for metadata_file in self.keys_dir.glob("*_metadata.json"):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        key_info = json.load(f)
                    
                    # Add file status
                    user_id = key_info.get('user_id')
                    private_key_file = self.keys_dir / f"{user_id}_private.pem"
                    key_info['private_key_exists'] = private_key_file.exists()
                    
                    keys_list.append(key_info)
                    
                except Exception as e:
                    print(f"Error reading key metadata {metadata_file}: {e}")
        
        except Exception as e:
            print(f"Error listing keys: {e}")
        
        return keys_list
    
    def delete_user_keys(self, user_id: str) -> Tuple[bool, str]:
        """
        Delete user's key pair (use with caution!)
        
        Args:
            user_id: User identifier
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            private_key_file = self.keys_dir / f"{user_id}_private.pem"
            metadata_file = self.keys_dir / f"{user_id}_metadata.json"
            
            files_deleted = 0
            
            if private_key_file.exists():
                private_key_file.unlink()
                files_deleted += 1
            
            if metadata_file.exists():
                metadata_file.unlink()
                files_deleted += 1
            
            if files_deleted == 0:
                return False, "No key files found for user"
            
            return True, f"Deleted {files_deleted} key files for user {user_id}"
            
        except Exception as e:
            return False, f"Failed to delete keys: {str(e)}"
    
    def backup_keys(self, backup_directory: str) -> Tuple[bool, str]:
        """
        Create backup of all key files
        
        Args:
            backup_directory: Directory to store backup
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            backup_dir = Path(backup_directory)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            files_backed_up = 0
            
            for key_file in self.keys_dir.glob("*"):
                if key_file.is_file():
                    backup_file = backup_dir / key_file.name
                    backup_file.write_bytes(key_file.read_bytes())
                    files_backed_up += 1
            
            backup_info = {
                'backup_date': datetime.now().isoformat(),
                'files_backed_up': files_backed_up,
                'source_directory': str(self.keys_dir),
                'backup_directory': str(backup_dir)
            }
            
            with open(backup_dir / 'backup_info.json', 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            return True, f"Backed up {files_backed_up} key files to {backup_dir}"
            
        except Exception as e:
            return False, f"Backup failed: {str(e)}"