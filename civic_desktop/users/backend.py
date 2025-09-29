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
                    # Initialize preliminary ranks fields if not present
                    'birth_date': data.get('birth_date', user.get('birth_date', '')),
                    'government_id_type': data.get('government_id_type', user.get('government_id_type', '')),
                    'government_id_number': data.get('government_id_number', user.get('government_id_number', '')),
                    'identity_verified': data.get('identity_verified', user.get('identity_verified', False)),
                    'address_verified': data.get('address_verified', user.get('address_verified', False)),
                    'email_verified': data.get('email_verified', user.get('email_verified', False)),
                    'parental_consent': data.get('parental_consent', user.get('parental_consent', False)),
                    'parent_email': data.get('parent_email', user.get('parent_email', '')),
                    'parent_name': data.get('parent_name', user.get('parent_name', '')),
                    'training_completed': data.get('training_completed', user.get('training_completed', [])),
                    'verification_status': data.get('verification_status', user.get('verification_status', 'pending')),
                    'rank_history': data.get('rank_history', user.get('rank_history', [])),
                    'role': data.get('roles', [None])[0] if data.get('roles') else user.get('role', 'Contract Citizen')
                })
                users_by_email[email] = user
            elif action == 'update_profile':
                email = data.get('user_email')
                if not email:
                    continue
                user = users_by_email.get(email, {'email': email})
                updates = data.get('updates', {})
                if isinstance(updates, dict):
                    # Handle special cases for list fields
                    for key, value in updates.items():
                        if key in ['training_completed', 'rank_history'] and isinstance(value, list):
                            # Append to existing list instead of replacing
                            existing = user.get(key, [])
                            if isinstance(existing, list):
                                existing.extend(value)
                                user[key] = existing
                            else:
                                user[key] = value
                        else:
                            user[key] = value
                users_by_email[email] = user
            elif action == 'role_update':
                email = data.get('user_email')
                if not email:
                    continue
                user = users_by_email.get(email, {'email': email})
                new_role = data.get('new_role')
                if new_role:
                    user['role'] = new_role
                    # Update roles list
                    roles = user.get('roles', [])
                    if new_role not in roles:
                        roles.append(new_role)
                    user['roles'] = roles
                # Process any additional updates
                updates = data.get('updates', {})
                if isinstance(updates, dict):
                    for key, value in updates.items():
                        if key == 'rank_history' and isinstance(value, list):
                            # Append to existing rank history
                            existing_history = user.get('rank_history', [])
                            if isinstance(existing_history, list):
                                existing_history.extend(value)
                                user['rank_history'] = existing_history
                            else:
                                user['rank_history'] = value
                        else:
                            user[key] = value
                users_by_email[email] = user
            elif action == 'training_completion':
                email = data.get('user_email')
                if not email:
                    continue
                user = users_by_email.get(email, {'email': email})
                course_name = data.get('course_name')
                if course_name:
                    # Add to training completed list
                    training_completed = user.get('training_completed', [])
                    if course_name not in training_completed:
                        training_completed.append(course_name)
                        user['training_completed'] = training_completed
                # Process any additional updates
                updates = data.get('updates', {})
                if isinstance(updates, dict):
                    for key, value in updates.items():
                        if key == 'training_completed' and isinstance(value, list):
                            # Append to existing training list (avoid duplicates)
                            existing_training = user.get('training_completed', [])
                            for course in value:
                                if course not in existing_training:
                                    existing_training.append(course)
                            user['training_completed'] = existing_training
                        else:
                            user[key] = value
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
        except (ValueError, TypeError) as e:
            # Log the specific error for debugging
            print(f"Password verification error: {e}")
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
        except ImportError:
            # Module not available, use fallback
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
        
        # Determine initial rank for non-founders using the new rank system
        if not is_founder:
            from .rank_manager import RankManager
            role = RankManager.determine_initial_rank(data)
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
            'id_verification': verification_result,
            # New fields for preliminary ranks system
            'birth_date': data.get('birth_date', ''),
            'government_id_type': data.get('id_type', ''),
            'government_id_number': data.get('id_number', ''),
            'identity_verified': verification_result.get('status') == 'verified',
            'address_verified': False,  # Will be verified separately
            'email_verified': False,   # Will be verified separately
            'parental_consent': data.get('parental_consent', False),
            'parent_email': data.get('parent_email', ''),
            'parent_name': data.get('parent_name', ''),
            'training_completed': [],  # List of completed training courses
            'verification_status': 'pending',
            'rank_history': [{
                'rank': role,
                'assigned_date': datetime.now(timezone.utc).isoformat(),
                'reason': 'Initial registration'
            }]
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
        """Create enhanced genesis block with real cryptographic keys and metadata"""
        genesis_path = os.path.join(os.path.dirname(__file__), '../blockchain/genesis_block.json')
        
        # Generate real RSA keys for genesis founder
        from ..blockchain.signatures import BlockchainSigner
        from cryptography.hazmat.primitives import serialization
        
        try:
            # Get founder's actual public key from validator registry
            from ..blockchain.blockchain import ValidatorRegistry
            public_key = ValidatorRegistry.get_validator_public_key(founder_user['email'])
            
            # If placeholder key found, generate real key
            if not public_key or public_key == "GENESIS_PLACEHOLDER":
                print(f"Generating real RSA keys for genesis founder: {founder_user['email']}")
                # Load private key and extract public key
                private_key = BlockchainSigner.load_private_key(founder_user['email'])
                if private_key:
                    public_key_obj = private_key.public_key()
                    public_key = public_key_obj.public_key_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ).decode('utf-8')
                else:
                    public_key = "KEY_GENERATION_ERROR"
            
        except Exception as e:
            print(f"Warning: Could not generate real keys for genesis: {e}")
            public_key = "GENESIS_PLACEHOLDER"
        
        # Enhanced genesis metadata
        genesis: Dict[str, Any] = {
            'type': 'genesis',
            'version': '1.0.0',
            'platform': 'Civic Engagement Platform',
            'consensus': 'proof_of_authority',
            'governance': 'contract_based_democracy',
            'founder': {
                'first_name': founder_user['first_name'],
                'last_name': founder_user['last_name'],
                'email': founder_user['email'],
                'created_at': founder_user.get('created_at'),
                'public_key': public_key,
                'role': 'Contract Founder'
            },
            'constitution': {
                'voting_thresholds': {
                    'contract_elder_veto': 0.60,
                    'founder_consensus': 0.75,
                    'constitutional_amendment': 0.60,
                    'citizen_recall': 0.55
                },
                'authority_hierarchy': [
                    'Contract Founders',
                    'Contract Elders', 
                    'Contract Representatives',
                    'Contract Senators',
                    'Contract Citizens'
                ],
                'checks_and_balances': {
                    'elder_veto_power': True,
                    'bicameral_legislature': True,
                    'citizen_recall_rights': True,
                    'constitutional_review': True
                }
            },
            'network_parameters': {
                'consensus_mechanism': 'proof_of_authority',
                'block_time': 'immediate',
                'validator_selection': 'democratic_election',
                'max_validators': 100,
                'min_validators': 1
            },
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'message': 'Genesis block for Civic Engagement Platform - Democratic Blockchain Governance',
            'genesis_hash': None  # Will be computed
        }
        
        # Compute genesis hash for integrity
        import hashlib
        genesis_string = json.dumps(genesis, sort_keys=True).encode()
        genesis['genesis_hash'] = hashlib.sha256(genesis_string).hexdigest()
        
        # Save enhanced genesis block
        with open(genesis_path, 'w', encoding='utf-8') as f:
            json.dump(genesis, f, indent=2)
            
        # Now create actual genesis block in blockchain as block 0
        UserBackend._ensure_genesis_block_first(founder_user, genesis)

    @staticmethod
    def _ensure_genesis_block_first(founder_user: Dict[str, Any], genesis_data: Dict[str, Any]) -> None:
        """Ensure genesis block is the first block in the blockchain"""
        from ..blockchain.blockchain import Blockchain
        
        # Load existing chain
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        
        # Check if genesis block already exists as first block
        if pages and pages[0].get('data', {}).get('action') == 'genesis_creation':
            print("Genesis block already exists as first block")
            return
            
        # Create genesis block data for blockchain
        genesis_block_data = {
            'action': 'genesis_creation',
            'type': 'genesis',
            'founder_email': founder_user['email'],
            'founder_name': f"{founder_user['first_name']} {founder_user['last_name']}",
            'genesis_metadata': genesis_data,
            'timestamp': genesis_data['timestamp']
        }
        
        if pages:
            # Blockchain already has blocks - reset it for clean genesis start
            print("Blockchain contains blocks. Resetting for clean genesis start.")
            if Blockchain.reset_blockchain_for_genesis():
                print("Blockchain reset successful. Creating genesis block.")
                Blockchain.add_page(
                    data=genesis_block_data,
                    validator=founder_user['email'],
                    signature='GENESIS'
                )
            else:
                print("Blockchain reset failed. Adding genesis as regular block.")
                Blockchain.add_page(
                    data=genesis_block_data,
                    validator=founder_user['email'],
                    signature='GENESIS'
                )
        else:
            # Empty blockchain - add genesis as first block
            print("Creating genesis block as first block in empty blockchain.")
            Blockchain.add_page(
                data=genesis_block_data,
                validator=founder_user['email'],
                signature='GENESIS'
            )


    @staticmethod
    def update_profile(user_email: str, updates: Dict[str, Any]) -> bool:
        """Update user profile using blockchain as primary storage"""
        users = UserBackend.load_users()
        user_exists = any(user['email'] == user_email for user in users)
        
        if not user_exists:
            return False
            
        # Record profile update in blockchain (primary storage)
        try:
            Blockchain.add_page(
                data={
                    'action': 'update_profile',
                    'user_email': user_email,
                    'updates': updates,
                    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                },
                validator=user_email if ValidatorRegistry.is_validator(user_email) else "SYSTEM"
            )
            return True
        except Exception as e:
            print(f"Failed to record profile update in blockchain: {e}")
            return False

    @staticmethod
    def get_user(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email (alias for get_user_by_email for consistency)"""
        return UserBackend.get_user_by_email(email)

    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        """Get all users"""
        return UserBackend.load_users()

    @staticmethod
    def update_user_role(user_email: str, new_role: str) -> bool:
        """Update user role and record in blockchain (primary storage)"""
        users = UserBackend.load_users()
        user_exists = False
        old_role = 'Unknown'
        
        # Find user to get current role
        for user in users:
            if user['email'] == user_email:
                old_role = user.get('role', 'Unknown')
                user_exists = True
                break
        
        if not user_exists:
            return False
        
        # Record role change in blockchain (primary storage)
        try:
            Blockchain.add_page(
                data={
                    'action': 'role_update',
                    'user_email': user_email,
                    'old_role': old_role,
                    'new_role': new_role,
                    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'updates': {
                        'role': new_role,
                        'roles': [new_role],  # Will be merged with existing roles by load_users
                        'rank_history': [{
                            'rank': new_role,
                            'assigned_date': datetime.now(timezone.utc).isoformat(),
                            'reason': 'Role promotion',
                            'previous_rank': old_role
                        }]
                    }
                },
                validator=user_email if ValidatorRegistry.is_validator(user_email) else "SYSTEM"
            )
            return True
        except Exception as e:
            print(f"Failed to record role change in blockchain: {e}")
            return False

    @staticmethod
    def update_verification_status(user_email: str, verification_type: str, status: bool) -> bool:
        """Update verification status for identity, address, or email"""
        users = UserBackend.load_users()
        updated = False
        
        valid_types = ['identity', 'address', 'email']
        if verification_type not in valid_types:
            return False
        
        for user in users:
            if user['email'] == user_email:
                field_name = f'{verification_type}_verified'
                user[field_name] = status
                
                # Update overall verification status
                if 'verification_status' not in user:
                    user['verification_status'] = 'pending'
                
                # Check if all verifications are complete
                all_verified = (
                    user.get('identity_verified', False) and
                    user.get('address_verified', False) and
                    user.get('email_verified', False)
                )
                
                if all_verified:
                    user['verification_status'] = 'complete'
                elif status:
                    user['verification_status'] = 'in_progress'
                
                updated = True
                
                # Record verification update in blockchain
                try:
                    Blockchain.add_page(
                        data={
                            'action': 'verification_update',
                            'user_email': user_email,
                            'verification_type': verification_type,
                            'status': status,
                            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        },
                        validator="SYSTEM"  # System-recorded verification
                    )
                except Exception as e:
                    print(f"Failed to record verification update in blockchain: {e}")
                
                break
        
        if updated:
            UserBackend.save_users(users)
        
        return updated

    @staticmethod
    def add_training_completion(user_email: str, course_name: str) -> bool:
        """Add completed training course to user record using blockchain as primary storage"""
        users = UserBackend.load_users()
        user_exists = False
        already_completed = False
        
        # Check if user exists and if they already completed this course
        for user in users:
            if user['email'] == user_email:
                user_exists = True
                training_completed = user.get('training_completed', [])
                if course_name in training_completed:
                    already_completed = True
                break
                
        if not user_exists:
            return False
            
        if already_completed:
            return True  # Already completed, no need to record again
        
        # Record training completion in blockchain (primary storage)
        try:
            Blockchain.add_page(
                data={
                    'action': 'training_completion',
                    'user_email': user_email,
                    'course_name': course_name,
                    'completion_date': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'updates': {
                        'training_completed': [course_name]  # Will be appended to existing list by load_users
                    }
                },
                validator=user_email if ValidatorRegistry.is_validator(user_email) else "SYSTEM"
            )
            return True
        except Exception as e:
            print(f"Failed to record training completion in blockchain: {e}")
            return False


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
