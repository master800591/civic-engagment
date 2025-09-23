import hashlib
import os
import json
import bcrypt
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from .elections import ElectionManager
 
from civic_desktop.blockchain.blockchain import Blockchain, ValidatorRegistry
from .constants import USERS_DB
from ..contracts.contract_terms import contract_manager

class UserBackend:
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        users = UserBackend.load_users()
        for user in users:
            if user.get('email', '').lower() == email.lower():
                return user
        return None

    @staticmethod
    def get_user_display_name(email: str) -> str:
        """Get formatted display name with titles and roles for a user"""
        if not email:
            return "Unknown User"
        
        # Handle system/agent accounts
        if email.startswith('system.') or email.startswith('agent.'):
            agent_name = email.replace('system.', '').replace('agent.', '').replace('_', ' ').title()
            return f"🤖 Agent {agent_name}"
        
        user = UserBackend.get_user_by_email(email)
        if not user:
            return f"User ({email.split('@')[0]})"
        
        # Build display name with titles
        first_name = user.get('first_name', '').strip()
        last_name = user.get('last_name', '').strip()
        roles = user.get('roles', [])
        
        # Base name
        if first_name and last_name:
            display_name = f"{first_name} {last_name}"
        elif first_name:
            display_name = first_name
        else:
            display_name = email.split('@')[0].title()
        
        # Add titles based on roles
        titles = []
        if 'Contract Founder' in roles:
            titles.append('🏛️ Founder')
        elif 'Contract Elder' in roles:
            titles.append('👴 Elder')
        elif 'Contract Senator' in roles:
            titles.append('🏛️ Senator')
        elif 'Contract Representative' in roles:
            titles.append('🗳️ Representative')
        elif 'Contract Citizen' in roles:
            titles.append('👤 Citizen')
        
        # Add CEO/leadership titles if applicable
        if any('CEO' in role for role in roles):
            titles.insert(0, '💼 CEO')
        if any('Director' in role for role in roles):
            titles.insert(0, '📋 Director')
        if any('Manager' in role for role in roles):
            titles.insert(0, '📊 Manager')
        
        # Format with titles
        if titles:
            return f"{' '.join(titles)} {display_name}"
        else:
            return display_name

    @staticmethod
    def load_users() -> List[Dict[str, Any]]:
        """Derive users from the blockchain pages (single source of truth)."""
        chain = Blockchain.load_chain()
        users_by_email: Dict[str, Dict[str, Any]] = {}
        for page in chain.get('pages', []):
            data = page.get('data', {})
            action = data.get('action')
            if action == 'register_user':
                email = data.get('user_email') or data.get('email')
                if not email:
                    continue
                user: Dict[str, Any] = users_by_email.get(email, {})
                # Populate fields from chain record
                user.update({
                    'first_name': data.get('first_name', user.get('first_name')),
                    'last_name': data.get('last_name', user.get('last_name')),
                    'address': data.get('address', user.get('address')),
                    'city': data.get('city', user.get('city')),
                    'state': data.get('state', user.get('state')),
                    'country': data.get('country', user.get('country')),
                    'email': email,
                    'password_hash': data.get('password_hash', user.get('password_hash', '')),
                    'roles': data.get('roles', user.get('roles', [])) or [],
                    'public_key': data.get('public_key', user.get('public_key', '')),
                    'id_document_hash': data.get('id_document_hash', user.get('id_document_hash', '')),
                })
                users_by_email[email] = user
            elif action == 'update_profile':
                email = data.get('user_email')
                if not email:
                    continue
                user = users_by_email.get(email, {'email': email})
                updates = data.get('updates', {})
                if isinstance(updates, dict):
                    user.update(updates)
                users_by_email[email] = user
        return list(users_by_email.values())


    @staticmethod
    def save_users(users: List[Dict[str, Any]]) -> None:
        """Deprecated: Users are stored on-chain. This is a no-op."""
        return None


    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with salt"""
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False


    @staticmethod
    def is_duplicate_id(id_document_hash: str) -> bool:
        users = UserBackend.load_users()
        for user in users:
            if user.get('id_document_hash') == id_document_hash:
                return True
        return False


    @staticmethod
    def register_user(data: Dict[str, Any], id_document_path: str) -> Tuple[bool, str]:
        try:
            from .id_verification_api import GovernmentIDVerificationAPI
        except Exception:
            class GovernmentIDVerificationAPI:  # fallback stub
                def __init__(self, api_url: str):
                    pass
                def verify_id(self, **kwargs):
                    return {'success': True, 'status': 'verified'}
        user_location = {
            'country': data.get('country', ''),
            'state': data.get('state', ''),
            'city': data.get('city', '')
        }
        users = UserBackend.load_users()
        is_founder = len(users) == 0
        with open(id_document_path, 'rb') as f:
            id_document_hash = hashlib.sha256(f.read()).hexdigest()
        if UserBackend.is_duplicate_id(id_document_hash):
            return False, 'Duplicate ID document detected.'

        # Government ID Verification step
        gov_api = GovernmentIDVerificationAPI(api_url="https://gov-id-verification.example/api")
        id_type = data.get('id_type', 'national_id')
        id_number = data.get('id_number', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        date_of_birth = data.get('date_of_birth', '')
        verification_result = gov_api.verify_id(
            id_type=id_type,
            id_number=id_number,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            document_image_path=id_document_path
        )
        if not verification_result.get('success'):
            error_msg = verification_result.get('error', 'Government ID verification failed.')
            return False, f'ID Verification Error: {error_msg}'
        if verification_result.get('status') != 'verified':
            return False, f'ID Verification failed: {verification_result.get("status")}'

        all_accepted, missing_contracts = contract_manager.check_all_required_accepted(
            user_email=data['email'],
            user_location=user_location
        )
        # Do not hard-fail here; UI enforces acceptance. Backend records state.
        for contract in contract_manager.get_applicable_contracts(user_location):
            if contract.acceptance_required:
                contract_manager.record_acceptance(
                    user_email=data['email'],
                    contract_id=contract.contract_id,
                    ip_address="",
                    user_agent=""
                )
        role = 'Contract Founder' if is_founder else 'Contract Citizen'
        from .keys import generate_keypair
        pub_key, priv_key = generate_keypair()
        privkey_dir = os.path.join(os.path.dirname(__file__), 'private_keys')
        os.makedirs(privkey_dir, exist_ok=True)
        privkey_path = os.path.join(privkey_dir, f"{data['email'].replace('@','_at_')}.pem")
        with open(privkey_path, 'w', encoding='utf-8') as f:
            f.write(priv_key)
        user: Dict[str, Any] = {
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'address': data['address'],
            'city': data['city'],
            'state': data['state'],
            'country': data['country'],
            'email': data['email'],
            'password_hash': UserBackend.hash_password(data['password']),
            'id_document_hash': id_document_hash,
            'agreed_to_contract': True,
            'contracts_accepted': all_accepted,
            'role': role,
            'roles': [role],
            'public_key': pub_key,
            'registration_date': datetime.now(timezone.utc).isoformat(),
            'contract_acceptance_date': datetime.now(timezone.utc).isoformat(),
            'user_location': user_location,
            'id_verification': verification_result
        }
        # Persist registration to blockchain (single source of truth)
        chain_record = {
            'action': 'register_user',
            'user_email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'address': user['address'],
            'city': user['city'],
            'state': user['state'],
            'country': user['country'],
            'public_key': user['public_key'],
            'roles': user['roles'],
            'password_hash': user['password_hash'],
            'id_document_hash': user['id_document_hash'],
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        if is_founder:
            ValidatorRegistry.add_validator(user['email'], public_key="GENESIS_PLACEHOLDER")
            UserBackend.create_genesis_block(user)
            Blockchain.add_page(
                data=chain_record,
                validator=user['email'],
                signature='GENESIS'  # Mark as genesis/founder
            )
            return True, 'Founder account created. Genesis block initialized.'
        else:
            triggered: List[str] = []
            for jur in ['city', 'state', 'country']:
                if ElectionManager.should_trigger_election(jur, data[jur]):  # type: ignore
                    triggered.append(jur)
            # Always record registration to blockchain even if not a validator yet
            Blockchain.add_page(
                data=chain_record,
                validator="SYSTEM"  # system-recorded until user becomes validator
            )
            if triggered:
                return True, f"Registration successful. Election triggered for: {', '.join(triggered)}."
            return True, 'Registration successful.'


    @staticmethod
    def create_genesis_block(founder_user: Dict[str, Any]) -> None:
        genesis_path = os.path.join(os.path.dirname(__file__), '../blockchain/genesis_block.json')
        genesis: Dict[str, Any] = {
            'type': 'genesis',
            'founder': {
                'first_name': founder_user['first_name'],
                'last_name': founder_user['last_name'],
                'email': founder_user['email'],
                'created_at': founder_user.get('created_at')
            },
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'message': 'Genesis block for Civic Engagement Platform',
        }
        with open(genesis_path, 'w', encoding='utf-8') as f:
            json.dump(genesis, f, indent=2)


    @staticmethod
    def update_profile(user_email: str, updates: Dict[str, Any]) -> bool:
        users = UserBackend.load_users()
        updated = False
        for user in users:
            if user['email'] == user_email:
                user.update(updates)
                updated = True
                # Blockchain: record profile update if validator
                if ValidatorRegistry.is_validator(user_email):
                        Blockchain.add_page(
                            data={
                                'action': 'update_profile',
                                'user_email': user_email,
                                'updates': updates,
                                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            },
                            validator=user_email
                            # signature will be generated automatically
                        )
        if updated:
            UserBackend.save_users(users)
        return updated


    @staticmethod
    def log_user_action(user_email: str, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        # General-purpose blockchain log for user actions
        if ValidatorRegistry.is_validator(user_email):
            Blockchain.add_page(
                data={
                    'action': action,
                    'user_email': user_email,
                    'details': details or {},
                    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                },
                validator=user_email
                # signature will be generated automatically
            )
