
import hashlib
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from civic_desktop.blockchain.blockchain import Blockchain
from .backend import UserBackend

class AuthManager:
    @staticmethod
    def authenticate(email, password):
        """Authenticate user with email and password"""
        # Load users from the user database (not just blockchain)
        users = UserBackend.load_users()
        if not users:
            return False, 'No users registered.'
        
        # Find all users by email (handle duplicates gracefully)
        matches = [u for u in users if u.get('email', '').lower() == email.lower()]
        if not matches:
            return False, 'Invalid email or password.'
        
        # Prefer entries with bcrypt hashes (start with $2)
        def is_bcrypt_hash(h: str) -> bool:
            return isinstance(h, str) and h.startswith('$2')

        candidates = sorted(matches, key=lambda u: (not is_bcrypt_hash(u.get('password_hash', ''))))

        # Check private key file exists
        privkey_dir = os.path.join(os.path.dirname(__file__), 'private_keys')
        privkey_path = os.path.join(privkey_dir, f"{email.replace('@','_at_')}.pem")
        if not os.path.exists(privkey_path):
            return False, 'Private key file not found. Please restore your private key.'
        
        # Load private key once
        try:
            with open(privkey_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(), password=None, backend=default_backend()
                )
        except Exception as e:
            return False, f'Private key error: {str(e)}'

        password_matched_but_key_failed = False
        for cand in candidates:
            if not UserBackend.verify_password(password, cand.get('password_hash', '')):
                continue
            # Verify private key against this candidate's public key
            try:
                public_key_pem = cand.get('public_key', '').encode('utf-8')
                public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
                test_message = b'civic-auth-test'
                signature = private_key.sign(
                    test_message,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                public_key.verify(
                    signature,
                    test_message,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                return True, cand
            except Exception:
                password_matched_but_key_failed = True
                continue
        
        if password_matched_but_key_failed:
            return False, 'Private key does not match public key.'
        return False, 'Invalid email or password.'
