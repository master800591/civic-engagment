"""
FOUNDER KEY SYSTEM - Cryptographic authentication for Founder role assignment
Manages the master Founder private/public key pair and validates Founder credentials during registration
"""

import json
import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
import base64
import hashlib

try:
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    print("Warning: cryptography library not available. Founder key functionality disabled.")
    CRYPTO_AVAILABLE = False

class FounderKeyManager:
    """Manages the master Founder key system for role authentication"""
    
    def __init__(self, config_path: str = None):
        """Initialize Founder key manager"""
        if config_path:
            self.config = self._load_config(config_path)
            self.founder_keys_dir = Path(self.config.get('founder_keys_dir', 'users/founder_keys'))
        else:
            self.founder_keys_dir = Path('users/founder_keys')
            
        self.founder_keys_dir.mkdir(parents=True, exist_ok=True)
        self.master_key_file = self.founder_keys_dir / 'founder_master.json'
        self.founder_registry_file = self.founder_keys_dir / 'founder_registry.json'
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def generate_founder_master_key(self, founder_count: int = 7) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Generate the master Founder key pair and derive individual Founder keys
        
        Args:
            founder_count: Number of Founder keys to generate (max 7 per constitution)
        
        Returns:
            Tuple of (success: bool, message: str, founder_info: Optional[Dict])
        """
        if not CRYPTO_AVAILABLE:
            return False, "Cryptography library not available", None
        
        if self.master_key_file.exists():
            return False, "Founder master key already exists. Use load_founder_keys() to access.", None
        
        try:
            print(f"🔐 Generating Founder Master Key System...")
            
            # Generate master private key (4096-bit for maximum security)
            master_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            
            # Get master public key
            master_public_key = master_private_key.public_key()
            
            # Serialize master keys
            master_private_pem = master_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
            
            master_public_pem = master_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
            
            # Generate master key fingerprint
            master_fingerprint = self._generate_key_fingerprint(master_public_pem)
            
            # Generate individual Founder keys derived from master
            founder_keys = {}
            founder_public_keys = []
            
            for i in range(founder_count):
                # Create unique seed for each Founder
                founder_seed = f"FOUNDER_{i+1:02d}_{master_fingerprint[:16]}"
                
                # Generate individual Founder key pair
                founder_private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                    backend=default_backend()
                )
                
                founder_public_key = founder_private_key.public_key()
                
                # Serialize Founder keys
                founder_private_pem = founder_private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ).decode('utf-8')
                
                founder_public_pem = founder_public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')
                
                founder_fingerprint = self._generate_key_fingerprint(founder_public_pem)
                
                # Store Founder key information
                founder_id = f"FOUNDER_{i+1:02d}"
                founder_keys[founder_id] = {
                    'founder_id': founder_id,
                    'private_key_pem': founder_private_pem,
                    'public_key_pem': founder_public_pem,
                    'key_fingerprint': founder_fingerprint,
                    'seed': founder_seed,
                    'created_at': datetime.now().isoformat(),
                    'assigned_to': None,  # Will be set when user claims this key
                    'active': True
                }
                
                founder_public_keys.append({
                    'founder_id': founder_id,
                    'public_key_pem': founder_public_pem,
                    'key_fingerprint': founder_fingerprint
                })
            
            # Save master key system
            master_key_data = {
                'master_private_key': master_private_pem,
                'master_public_key': master_public_pem,
                'master_fingerprint': master_fingerprint,
                'founder_count': founder_count,
                'founder_keys': founder_keys,
                'founder_public_keys': founder_public_keys,
                'created_at': datetime.now().isoformat(),
                'constitutional_authority': 'Genesis Founders - Maximum 7 per constitutional framework',
                'emergency_protocols': {
                    'master_key_rotation': 'Requires 75% Founder consensus + citizen ratification',
                    'founder_key_revocation': 'Requires 67% remaining Founder consensus',
                    'constitutional_override': 'Platform-threatening emergencies only'
                }
            }
            
            # Save to secure file
            with open(self.master_key_file, 'w', encoding='utf-8') as f:
                json.dump(master_key_data, f, indent=2)
            
            # Create Founder registry for tracking assignments
            founder_registry = {
                'master_fingerprint': master_fingerprint,
                'total_founders': founder_count,
                'assigned_founders': 0,
                'active_founders': [],
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.founder_registry_file, 'w', encoding='utf-8') as f:
                json.dump(founder_registry, f, indent=2)
            
            print(f"✅ Founder Master Key System generated successfully!")
            print(f"   Master Fingerprint: {master_fingerprint}")
            print(f"   Founder Keys: {founder_count}")
            print(f"   Security Level: RSA-4096 (Master) / RSA-2048 (Individual)")
            
            return True, "Founder key system created successfully", master_key_data
        
        except Exception as e:
            return False, f"Failed to generate Founder keys: {str(e)}", None
    
    def validate_founder_key(self, provided_private_key: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validate a provided private key against the Founder key system
        
        Args:
            provided_private_key: PEM-formatted private key string
        
        Returns:
            Tuple of (is_valid: bool, message: str, founder_info: Optional[Dict])
        """
        if not CRYPTO_AVAILABLE:
            return False, "Cryptography library not available", None
        
        if not self.master_key_file.exists():
            return False, "Founder key system not initialized", None
        
        try:
            # Load master key data
            with open(self.master_key_file, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
            
            # Parse provided private key
            try:
                provided_key = serialization.load_pem_private_key(
                    provided_private_key.encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
                
                # Get public key from provided private key
                provided_public = provided_key.public_key()
                provided_public_pem = provided_public.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')
                
            except Exception as e:
                return False, f"Invalid private key format: {str(e)}", None
            
            # Check against all Founder keys
            for founder_id, founder_data in master_data['founder_keys'].items():
                stored_private_key = serialization.load_pem_private_key(
                    founder_data['private_key_pem'].encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
                
                stored_public_key = stored_private_key.public_key()
                stored_public_pem = stored_public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')
                
                # Compare public keys
                if provided_public_pem == stored_public_pem:
                    # Valid Founder key found!
                    return True, f"Valid Founder key: {founder_id}", {
                        'founder_id': founder_id,
                        'key_fingerprint': founder_data['key_fingerprint'],
                        'created_at': founder_data['created_at'],
                        'assigned_to': founder_data.get('assigned_to'),
                        'active': founder_data.get('active', True)
                    }
            
            return False, "Private key does not match any Founder key", None
        
        except Exception as e:
            return False, f"Error validating Founder key: {str(e)}", None
    
    def assign_founder_key(self, founder_id: str, user_email: str) -> Tuple[bool, str]:
        """
        Assign a Founder key to a specific user
        
        Args:
            founder_id: Founder key identifier (e.g., 'FOUNDER_01')
            user_email: Email of user being assigned Founder status
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Load master key data
            with open(self.master_key_file, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
            
            # Check if Founder key exists and is available
            if founder_id not in master_data['founder_keys']:
                return False, f"Founder key {founder_id} does not exist"
            
            founder_key = master_data['founder_keys'][founder_id]
            if founder_key.get('assigned_to') is not None:
                return False, f"Founder key {founder_id} already assigned to {founder_key['assigned_to']}"
            
            # Assign the key
            master_data['founder_keys'][founder_id]['assigned_to'] = user_email
            master_data['founder_keys'][founder_id]['assigned_at'] = datetime.now().isoformat()
            
            # Save updated master data
            with open(self.master_key_file, 'w', encoding='utf-8') as f:
                json.dump(master_data, f, indent=2)
            
            # Update registry
            if self.founder_registry_file.exists():
                with open(self.founder_registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                
                registry['assigned_founders'] += 1
                registry['active_founders'].append({
                    'founder_id': founder_id,
                    'user_email': user_email,
                    'assigned_at': datetime.now().isoformat()
                })
                registry['last_updated'] = datetime.now().isoformat()
                
                with open(self.founder_registry_file, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, indent=2)
            
            return True, f"Founder key {founder_id} assigned to {user_email}"
        
        except Exception as e:
            return False, f"Error assigning Founder key: {str(e)}"
    
    def get_founder_keys_info(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Get information about the Founder key system
        
        Returns:
            Tuple of (success: bool, message: str, info: Optional[Dict])
        """
        try:
            if not self.master_key_file.exists():
                return False, "Founder key system not initialized", None
            
            with open(self.master_key_file, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
            
            # Get registry info
            registry_info = {}
            if self.founder_registry_file.exists():
                with open(self.founder_registry_file, 'r', encoding='utf-8') as f:
                    registry_info = json.load(f)
            
            # Compile public information (no private keys)
            founder_info = {
                'master_fingerprint': master_data['master_fingerprint'],
                'founder_count': master_data['founder_count'],
                'created_at': master_data['created_at'],
                'assigned_founders': registry_info.get('assigned_founders', 0),
                'active_founders': registry_info.get('active_founders', []),
                'public_keys': master_data['founder_public_keys']
            }
            
            return True, "Founder key information retrieved", founder_info
        
        except Exception as e:
            return False, f"Error retrieving Founder key info: {str(e)}", None
    
    def _generate_key_fingerprint(self, public_key_pem: str) -> str:
        """Generate a unique fingerprint for a public key"""
        return hashlib.sha256(public_key_pem.encode('utf-8')).hexdigest()[:32]
    
    def export_founder_keys_for_distribution(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Export Founder private keys for secure distribution to genesis Founders
        WARNING: This should only be called during initial setup!
        
        Returns:
            Tuple of (success: bool, message: str, keys_for_distribution: Optional[Dict])
        """
        try:
            if not self.master_key_file.exists():
                return False, "Founder key system not initialized", None
            
            with open(self.master_key_file, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
            
            # Create secure export format
            distribution_keys = {}
            for founder_id, founder_data in master_data['founder_keys'].items():
                distribution_keys[founder_id] = {
                    'founder_id': founder_id,
                    'private_key_pem': founder_data['private_key_pem'],
                    'public_key_pem': founder_data['public_key_pem'],
                    'key_fingerprint': founder_data['key_fingerprint'],
                    'instructions': {
                        'usage': f'This is {founder_id} private key for Civic Engagement Platform',
                        'security': 'Keep this key absolutely secure - it grants Founder authority',
                        'registration': 'Provide this private key during account registration to claim Founder role',
                        'backup': 'Create secure offline backups - loss of key means loss of Founder status'
                    }
                }
            
            export_data = {
                'platform': 'Civic Engagement Platform - Constitutional Democracy',
                'export_type': 'Genesis Founder Keys',
                'master_fingerprint': master_data['master_fingerprint'],
                'export_timestamp': datetime.now().isoformat(),
                'security_warning': 'These keys grant maximum platform authority - distribute securely!',
                'founder_keys': distribution_keys,
                'constitutional_framework': {
                    'max_founders': 7,
                    'founder_powers': [
                        'Constitutional amendment authority',
                        'Emergency protocol override',
                        'Platform governance modification',
                        'Elder appointment authority',
                        'System integrity protection'
                    ],
                    'founder_limitations': [
                        'Cannot override citizen constitutional rights',
                        'Subject to supermajority consensus requirements',
                        'Cannot directly govern day-to-day operations',
                        'Subject to recall by Elder + Senator consensus'
                    ]
                }
            }
            
            return True, "Founder keys exported for distribution", export_data
        
        except Exception as e:
            return False, f"Error exporting Founder keys: {str(e)}", None
    
    def generate_individual_founder_key(self, founder_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Generate an individual founder key for distribution
        
        Args:
            founder_id: Unique identifier for the founder (e.g., "FOUNDER_01")
            
        Returns:
            Tuple of (success: bool, message: str, key_data: Optional[Dict])
        """
        try:
            if not CRYPTO_AVAILABLE:
                return False, "Cryptography library not available", None
            
            # Generate individual RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
            
            # Generate key fingerprint
            public_der = public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            key_fingerprint = hashlib.sha256(public_der).hexdigest()
            
            # Generate blockchain address
            blockchain_address = f"civic_{key_fingerprint[:20]}"
            
            key_data = {
                'founder_id': founder_id,
                'private_key_pem': private_pem,
                'public_key_pem': public_pem,
                'key_fingerprint': key_fingerprint,
                'blockchain_address': blockchain_address,
                'created_at': datetime.now().isoformat(),
                'key_size': 2048,
                'key_type': 'founder_authority',
                'single_use': True
            }
            
            return True, f"Individual founder key generated for {founder_id}", key_data
            
        except Exception as e:
            return False, f"Error generating individual founder key: {str(e)}", None