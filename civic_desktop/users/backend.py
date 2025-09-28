"""
USER BACKEND - Core user data management and authentication
Handles user registration, authentication, role management, and database operations
"""

import json
import bcrypt
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import uuid
import hashlib

# Import validation framework
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.validation import DataValidator, SecurityValidator

# Import Founder key and contract roles
try:
    from users.founder_keys import FounderKeyManager
    from users.contract_roles import ContractRoleManager, ContractRole
    from users.hardcoded_founder_keys import HardcodedFounderKeys
    FOUNDER_SYSTEM_AVAILABLE = True
except ImportError:
    print("Warning: Founder key system not available")
    FOUNDER_SYSTEM_AVAILABLE = False

# Import PDF generator
try:
    from users.pdf_generator import UserPDFGenerator
    PDF_GENERATION_AVAILABLE = True
except ImportError:
    print("Warning: PDF generation not available")
    PDF_GENERATION_AVAILABLE = False

class UserBackend:
    """Core user management backend with security and validation"""
    
    def __init__(self, config_path: str = None):
        """Initialize user backend with environment-specific configuration"""
        self.config_path = config_path or "config/dev_config.json"
        self.config = self._load_config()
        
        # Database paths
        self.users_db_path = Path(self.config.get('users_db_path', 'users/users_db.json'))
        self.sessions_db_path = Path(self.config.get('sessions_db_path', 'users/sessions_db.json'))
        self.private_keys_dir = Path(self.config.get('private_keys_dir', 'users/private_keys'))
        
        # Ensure directories exist
        self.users_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.sessions_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.private_keys_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize databases
        self._init_databases()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_path}: {e}")
        
        # Default configuration
        return {
            'users_db_path': 'users/users_db.json',
            'sessions_db_path': 'users/sessions_db.json',
            'private_keys_dir': 'users/private_keys',
            'session_timeout_hours': 24,
            'max_login_attempts': 5,
            'lockout_duration_minutes': 30
        }
    
    def _init_databases(self):
        """Initialize database files if they don't exist"""
        # Initialize users database
        if not self.users_db_path.exists():
            initial_users_data = {
                'users': [],
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'version': '1.0',
                    'total_users': 0
                }
            }
            self._save_users_db(initial_users_data)
        
        # Initialize sessions database
        if not self.sessions_db_path.exists():
            initial_sessions_data = {
                'active_sessions': {},
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'total_sessions': 0
                }
            }
            self._save_sessions_db(initial_sessions_data)
    
    def _load_users_db(self) -> Dict[str, Any]:
        """Load users database"""
        try:
            with open(self.users_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading users database: {e}")
            return {'users': [], 'metadata': {}}
    
    def _save_users_db(self, data: Dict[str, Any]):
        """Save users database"""
        try:
            with open(self.users_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving users database: {e}")
    
    def _load_sessions_db(self) -> Dict[str, Any]:
        """Load sessions database"""
        try:
            with open(self.sessions_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading sessions database: {e}")
            return {'active_sessions': {}, 'metadata': {}}
    
    def _save_sessions_db(self, data: Dict[str, Any]):
        """Save sessions database"""
        try:
            with open(self.sessions_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving sessions database: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt with automatic salt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against stored hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return str(uuid.uuid4())
    
    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        return hashlib.sha256(f"{uuid.uuid4()}{datetime.now()}".encode()).hexdigest()
    
    def register_user(self, user_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict]]:
        """
        Register new user with comprehensive validation
        
        Args:
            user_data: Dictionary containing user registration information
        
        Returns:
            Tuple of (success: bool, message: str, user_record: Optional[Dict])
        """
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'password', 'city', 'state', 'country']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                return False, f"Missing required field: {field}", None
        
        # Validate individual fields
        validation_checks = [
            DataValidator.validate_name(user_data['first_name'], "First name"),
            DataValidator.validate_name(user_data['last_name'], "Last name"),
            DataValidator.validate_email(user_data['email']),
            DataValidator.validate_password(user_data['password'], user_data.get('confirm_password')),
            DataValidator.validate_location(user_data['city'], user_data['state'], user_data['country'])
        ]
        
        for is_valid, message in validation_checks:
            if not is_valid:
                return False, message, None
        
        # Check if email already exists
        users_data = self._load_users_db()
        existing_user = next((u for u in users_data['users'] if u['email'] == user_data['email']), None)
        if existing_user:
            return False, "Email address already registered", None
        
        # Check for Founder key during registration
        user_role = 'contract_citizen'  # Default role
        founder_info = None
        
        if user_data.get('founder_private_key') and FOUNDER_SYSTEM_AVAILABLE:
            try:
                # Use hardcoded founder keys for single-use promotion
                is_valid_founder, founder_message, founder_data = HardcodedFounderKeys.validate_founder_key(
                    user_data['founder_private_key']
                )
                
                if is_valid_founder:
                    user_role = 'contract_founder'
                    founder_info = founder_data
                    print(f"🏛️ Hardcoded founder key validated: {founder_data['id']}")
                    print(f"🎉 User promoted to Constitutional Founder with single-use key: {founder_data['id']}")
                    
                    # Mark key as used (handled automatically by HardcodedFounderKeys.validate_founder_key)
                    print(f"🔒 Founder key {founder_data['id']} is now permanently used and cannot be reused")
                        
                else:
                    print(f"⚠️ Invalid Founder key provided: {founder_message}")
                    
            except Exception as e:
                print(f"⚠️ Error validating Founder key: {e}")
        
        # Create user record
        user_id = self._generate_user_id()
        password_hash = self._hash_password(user_data['password'])
        
        new_user = {
            'user_id': user_id,
            'first_name': DataValidator.sanitize_input(user_data['first_name']),
            'last_name': DataValidator.sanitize_input(user_data['last_name']),
            'email': user_data['email'].lower().strip(),
            'password_hash': password_hash,
            'city': DataValidator.sanitize_input(user_data['city']),
            'state': DataValidator.sanitize_input(user_data['state']),
            'country': DataValidator.sanitize_input(user_data['country']),
            'role': user_role,  # Founder role if key validated, otherwise contract_citizen
            'verification_status': 'pending',  # ID verification pending
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'login_attempts': 0,
            'locked_until': None,
            'rsa_public_key': None,  # Will be set during key generation
            'blockchain_address': None,  # Generated from public key
            'profile_completed': False,
            'terms_accepted': user_data.get('terms_accepted', False),
            'id_document_path': user_data.get('id_document_path'),
            'metadata': {
                'registration_ip': user_data.get('registration_ip'),
                'user_agent': user_data.get('user_agent'),
                'registration_method': 'web_form',
                'founder_info': founder_info  # Founder key info if applicable
            }
        }
        
        # Add user to database
        users_data['users'].append(new_user)
        users_data['metadata']['total_users'] = len(users_data['users'])
        users_data['metadata']['last_updated'] = datetime.now().isoformat()
        
        self._save_users_db(users_data)
        
        # Register contract role if Founder system available
        if FOUNDER_SYSTEM_AVAILABLE:
            try:
                role_manager = ContractRoleManager(self.config_path)
                contract_role = ContractRole.CONTRACT_FOUNDER if user_role == 'contract_founder' else ContractRole.CONTRACT_CITIZEN
                assignment_method = 'founder_key' if user_role == 'contract_founder' else 'initial_setup'
                
                role_success, role_message, role_info = role_manager.assign_contract_role(
                    user_data['email'].lower().strip(),
                    contract_role,
                    assignment_method,
                    'system'
                )
                
                if role_success:
                    print(f"✅ Contract role assigned: {contract_role.value}")
                else:
                    print(f"⚠️ Contract role assignment failed: {role_message}")
                    
            except Exception as e:
                print(f"⚠️ Error assigning contract role: {e}")
        
        # Generate RSA keys for user
        try:
            from users.keys import RSAKeyManager
            key_manager = RSAKeyManager(self.private_keys_dir)
            
            key_success, key_message, key_info = key_manager.generate_key_pair(user_id)
            
            if key_success:
                # Update user record with key information
                new_user['rsa_public_key'] = key_info['public_key_pem']
                new_user['blockchain_address'] = key_info['blockchain_address']
                new_user['key_fingerprint'] = key_info['key_fingerprint']
                
                print(f"🔑 RSA keys generated: {key_info['key_fingerprint'][:16]}...")
            else:
                print(f"⚠️ Key generation failed: {key_message}")
                key_info = None
        except Exception as e:
            print(f"⚠️ Error generating RSA keys: {e}")
            key_info = None
        
        # Generate user PDF documents
        pdf_paths = {}
        if PDF_GENERATION_AVAILABLE and key_info:
            try:
                pdf_generator = UserPDFGenerator(self.config_path)
                
                pdf_success, pdf_message, pdf_paths = pdf_generator.generate_user_pdfs(
                    new_user, key_info
                )
                
                if pdf_success:
                    print(f"📄 User PDFs generated successfully")
                    print(f"   Public PDF: {pdf_paths.get('public_pdf', 'N/A')}")
                    print(f"   Private PDF: {pdf_paths.get('private_pdf', 'N/A')}")
                    
                    # Add PDF paths to user metadata
                    new_user['metadata']['pdf_documents'] = {
                        'public_pdf_path': pdf_paths.get('public_pdf'),
                        'private_pdf_path': pdf_paths.get('private_pdf'),
                        'public_qr_path': pdf_paths.get('public_qr'),
                        'private_qr_path': pdf_paths.get('private_qr'),
                        'generated_at': datetime.now().isoformat()
                    }
                else:
                    print(f"⚠️ PDF generation failed: {pdf_message}")
                    
            except Exception as e:
                print(f"⚠️ Error generating PDFs: {e}")
        
        # Remove sensitive data from returned record
        safe_user_record = {k: v for k, v in new_user.items() if k != 'password_hash'}
        
        # Add PDF paths to safe record for return
        if pdf_paths:
            safe_user_record['pdf_documents'] = pdf_paths
        
        # Record registration on blockchain for transparency
        try:
            from blockchain.blockchain import add_user_action
            blockchain_data = {
                'user_id': new_user['user_id'],
                'name': f"{new_user['first_name']} {new_user['last_name']}",
                'location': f"{new_user['city']}, {new_user['state']}, {new_user['country']}",
                'role': new_user['role'],
                'registration_method': 'civic_platform_wizard',
                'constitutional_rights': True,
                'blockchain_address': new_user.get('blockchain_address', 'pending'),
                'rsa_key_fingerprint': new_user.get('key_fingerprint', 'generated'),
                'founder_info': {
                    'is_founder': user_role == 'contract_founder',
                    'founder_id': founder_info['founder_id'] if founder_info else None,
                    'key_fingerprint': founder_info['key_fingerprint'] if founder_info else None
                } if founder_info else {'is_founder': False},
                'pdf_documents': {
                    'public_pdf_generated': bool(pdf_paths.get('public_pdf')),
                    'private_pdf_generated': bool(pdf_paths.get('private_pdf')),
                    'qr_codes_generated': bool(pdf_paths.get('public_qr') and pdf_paths.get('private_qr')),
                    'generation_timestamp': datetime.now().isoformat()
                }
            }
            
            blockchain_success, blockchain_message, page_id = add_user_action(
                action_type='user_registration',
                user_email=new_user['email'],
                data=blockchain_data
            )
            
            if blockchain_success:
                print(f"📄 Registration recorded on blockchain: {page_id}")
            else:
                print(f"⚠️ Blockchain recording failed: {blockchain_message}")
                
        except ImportError:
            print("⚠️ Blockchain system not available for registration recording")
        except Exception as e:
            print(f"⚠️ Blockchain recording error: {e}")
        
        return True, "User registered successfully", safe_user_record
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate user login with security checks
        
        Args:
            email: User's email address
            password: User's password
        
        Returns:
            Tuple of (success: bool, message: str, user_record: Optional[Dict])
        """
        
        # Validate input
        email_valid, email_msg = DataValidator.validate_email(email)
        if not email_valid:
            return False, email_msg, None
        
        email = email.lower().strip()
        
        # Load users database
        users_data = self._load_users_db()
        user = next((u for u in users_data['users'] if u['email'] == email), None)
        
        if not user:
            return False, "Invalid email or password", None
        
        # Check if account is locked
        if user.get('locked_until'):
            locked_until = datetime.fromisoformat(user['locked_until'])
            if datetime.now() < locked_until:
                remaining_time = (locked_until - datetime.now()).total_seconds() / 60
                return False, f"Account locked. Try again in {remaining_time:.0f} minutes", None
            else:
                # Unlock account
                user['locked_until'] = None
                user['login_attempts'] = 0
        
        # Verify password
        if not self._verify_password(password, user['password_hash']):
            # Increment failed login attempts
            user['login_attempts'] = user.get('login_attempts', 0) + 1
            max_attempts = self.config.get('max_login_attempts', 5)
            
            if user['login_attempts'] >= max_attempts:
                # Lock account
                lockout_duration = self.config.get('lockout_duration_minutes', 30)
                user['locked_until'] = (datetime.now() + timedelta(minutes=lockout_duration)).isoformat()
                self._save_users_db(users_data)
                return False, f"Too many failed attempts. Account locked for {lockout_duration} minutes", None
            
            self._save_users_db(users_data)
            remaining_attempts = max_attempts - user['login_attempts']
            return False, f"Invalid email or password. {remaining_attempts} attempts remaining", None
        
        # Successful login - reset failed attempts and update last login
        user['login_attempts'] = 0
        user['locked_until'] = None
        user['last_login'] = datetime.now().isoformat()
        self._save_users_db(users_data)
        
        # Remove sensitive data from returned record
        safe_user_record = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return True, "Login successful", safe_user_record
    
    def create_session(self, user_record: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        Create user session after successful authentication
        
        Args:
            user_record: User record from authentication
        
        Returns:
            Tuple of (success: bool, message: str, session_id: Optional[str])
        """
        
        session_id = self._generate_session_id()
        
        session_data = {
            'session_id': session_id,
            'user_id': user_record['user_id'],
            'email': user_record['email'],
            'role': user_record['role'],
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=self.config.get('session_timeout_hours', 24))).isoformat(),
            'last_activity': datetime.now().isoformat(),
            'ip_address': None,  # Would be set by web framework
            'user_agent': None   # Would be set by web framework
        }
        
        # Load sessions database
        sessions_data = self._load_sessions_db()
        sessions_data['active_sessions'][session_id] = session_data
        sessions_data['metadata']['total_sessions'] = len(sessions_data['active_sessions'])
        sessions_data['metadata']['last_updated'] = datetime.now().isoformat()
        
        self._save_sessions_db(sessions_data)
        
        return True, "Session created successfully", session_id
    
    def validate_session(self, session_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate active user session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Tuple of (success: bool, message: str, session_data: Optional[Dict])
        """
        
        if not session_id:
            return False, "No session ID provided", None
        
        sessions_data = self._load_sessions_db()
        session = sessions_data['active_sessions'].get(session_id)
        
        if not session:
            return False, "Invalid session", None
        
        # Check if session has expired
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            # Remove expired session
            del sessions_data['active_sessions'][session_id]
            self._save_sessions_db(sessions_data)
            return False, "Session expired", None
        
        # Update last activity
        session['last_activity'] = datetime.now().isoformat()
        sessions_data['active_sessions'][session_id] = session
        self._save_sessions_db(sessions_data)
        
        return True, "Valid session", session
    
    def logout_user(self, session_id: str) -> Tuple[bool, str]:
        """
        Logout user and invalidate session
        
        Args:
            session_id: Session to invalidate
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        
        sessions_data = self._load_sessions_db()
        
        if session_id in sessions_data['active_sessions']:
            del sessions_data['active_sessions'][session_id]
            self._save_sessions_db(sessions_data)
            return True, "Logged out successfully"
        
        return False, "Session not found"
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user record by email (without password hash)"""
        email_valid, _ = DataValidator.validate_email(email)
        if not email_valid:
            return None
        
        users_data = self._load_users_db()
        user = next((u for u in users_data['users'] if u['email'] == email.lower().strip()), None)
        
        if user:
            # Return copy without password hash
            return {k: v for k, v in user.items() if k != 'password_hash'}
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user record by user ID (without password hash)"""
        if not user_id:
            return None
        
        users_data = self._load_users_db()
        user = next((u for u in users_data['users'] if u['user_id'] == user_id), None)
        
        if user:
            # Return copy without password hash
            return {k: v for k, v in user.items() if k != 'password_hash'}
        
        return None
    
    def update_user_role(self, user_id: str, new_role: str, authorized_by: str) -> Tuple[bool, str]:
        """
        Update user role (requires proper authorization)
        
        Args:
            user_id: User to update
            new_role: New role to assign
            authorized_by: User ID of authorizing user
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        
        # Validate new role
        role_valid, role_msg = DataValidator.validate_user_role(new_role)
        if not role_valid:
            return False, role_msg
        
        # Load users database
        users_data = self._load_users_db()
        user_index = next((i for i, u in enumerate(users_data['users']) if u['user_id'] == user_id), None)
        
        if user_index is None:
            return False, "User not found"
        
        # Update role
        old_role = users_data['users'][user_index]['role']
        users_data['users'][user_index]['role'] = new_role
        users_data['users'][user_index]['role_updated_at'] = datetime.now().isoformat()
        users_data['users'][user_index]['role_updated_by'] = authorized_by
        
        self._save_users_db(users_data)
        
        return True, f"Role updated from {old_role} to {new_role}"
    
    def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Get all users with specific role"""
        role_valid, _ = DataValidator.validate_user_role(role)
        if not role_valid:
            return []
        
        users_data = self._load_users_db()
        users_with_role = [
            {k: v for k, v in user.items() if k != 'password_hash'}
            for user in users_data['users']
            if user['role'] == role
        ]
        
        return users_with_role
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of removed sessions"""
        sessions_data = self._load_sessions_db()
        initial_count = len(sessions_data['active_sessions'])
        
        # Remove expired sessions
        current_time = datetime.now()
        active_sessions = {}
        
        for session_id, session in sessions_data['active_sessions'].items():
            expires_at = datetime.fromisoformat(session['expires_at'])
            if current_time <= expires_at:
                active_sessions[session_id] = session
        
        sessions_data['active_sessions'] = active_sessions
        sessions_data['metadata']['total_sessions'] = len(active_sessions)
        sessions_data['metadata']['last_cleanup'] = datetime.now().isoformat()
        
        self._save_sessions_db(sessions_data)
        
        removed_count = initial_count - len(active_sessions)
        return removed_count