# Users Module - Identity & Authentication System + Crypto Integration

## Purpose
Secure user registration, authentication, role-based governance participation, and **integrated cryptocurrency management** with enterprise-grade security and constitutional compliance.

## Module Structure
```
users/
├── backend.py            # User data management, bcrypt hashing, crypto integration
├── auth.py               # Authentication logic and session management
├── login.py              # Login UI component with user-friendly interface
├── registration.py       # Registration UI component (6-step wizard with crypto)
├── dashboard.py          # User dashboard UI with crypto portfolio tab
├── elections.py          # Election backend logic for contract roles
├── election_ui.py        # Election UI components and voting interface
├── session.py            # Session management and state tracking
├── keys.py               # RSA key management and cryptographic operations
├── crypto_integration.py # Complete crypto-user integration bridge (300+ lines)
├── users_db.json         # User database (environment-specific path)
└── private_keys/         # RSA private key storage directory
```

## AI Implementation Instructions

### 1. User Registration Workflow (6-Step Process with Crypto)
```python
# Step 1: Personal Information
def collect_personal_info():
    # Required fields: first_name, last_name, email
    # Validation: DataValidator.validate_email(), name length checks
    # UI: Clear form with real-time validation feedback

# Step 2: Location Details  
def collect_location():
    # Required: city, state, country (for voting jurisdiction)
    # Validation: Non-empty strings, format consistency
    # UI: Dropdown menus for standardized location data

# Step 3: ID Document Upload
def upload_id_document():
    # Required: Government ID for verification
    # Security: File validation, size limits, secure storage
    # UI: Drag-and-drop upload with preview

# Step 4: Password Creation
def create_password():
    # Required: Strong password meeting complexity requirements
    # Security: bcrypt hashing with automatic salt
    # UI: Password strength indicator, confirmation field

# Step 5: Terms Agreement & Key Generation
def generate_keys_and_terms():
    # Automatic: RSA key pair generation for blockchain participation
    # Required: User agreement to platform terms of service
    # Security: Private keys stored locally, never transmitted
    # UI: Terms display with clear explanations

# Step 6: CRYPTO WALLET CREATION (NEW)
def create_crypto_wallet():
    # Automatic: CivicCoin wallet creation using UserCryptoIntegration
    # Role-Based Funding: Contract Founders (1000 CVC), Members (100 CVC)
    # Blockchain Recording: Wallet creation and initial funding recorded
    # UI: Success confirmation with wallet address and initial balance
def finalize_registration():
    # Required: Terms acceptance, automatic RSA key generation
    # Blockchain: Record registration action with full audit trail
    # UI: Clear terms display, key generation progress
```

### 2. Authentication System
```python
# Login Process
def authenticate_user(email, password):
    # Load user from database using ENV_CONFIG path
    # Verify password using bcrypt.checkpw()
    # Create session using SessionManager
    # Record login action to blockchain
    # Return success/failure with appropriate UI feedback

# Session Management
class SessionManager:
    @staticmethod
    def get_current_user():
        # Return current authenticated user data
        
    @staticmethod
    def is_authenticated():
        # Check if user session is active and valid
        
    @staticmethod
    def logout():
        # Clear session, record logout to blockchain
```

### 3. Contract-Based Role System
```python
# Role Hierarchy (Constitutional Democracy)
ROLES = {
    'Contract Citizen': {
        'permissions': ['vote', 'debate', 'petition', 'appeal'],
        'description': 'Core democratic rights'
    },
    'Contract Representative': {
        'permissions': ['legislative_initiative', 'budget_authority', 'impeachment'],
        'description': 'Peoples voice in governance'
    },
    'Contract Senator': {
        'permissions': ['legislative_oversight', 'confirmation_authority', 'veto_override'],
        'description': 'Deliberative review and balance'
    },
    'Contract Elder': {
        'permissions': ['judicial_review', 'constitutional_interpretation', 'veto_power'],
        'description': 'Constitutional guardians'
    },
    'Contract Founder': {
        'permissions': ['emergency_authority', 'constitutional_amendments', 'system_integrity'],
        'description': 'Genesis authority with oversight'
    }
}

# Election System
def conduct_election(position, candidates, voters):
    # Validate voter eligibility based on jurisdiction
    # Implement ranked-choice voting for representatives
    # Apply constitutional safeguards and checks
    # Record all election data to blockchain
    # Update user roles based on results
```

### 4. Security Implementation
```python
# Password Security
import bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

# RSA Key Management  
from cryptography.hazmat.primitives.asymmetric import rsa
def generate_user_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    # Store private key locally, never transmit
    # Return public key for blockchain registration
```

### 5. Database Operations
```python
# Environment-Aware Data Access
from civic_desktop.main import ENV_CONFIG

def load_users():
    db_path = ENV_CONFIG.get('users_db_path', 'users/users_db.json')
    # Load and return user data with error handling

def save_user(user_data):
    # Validate all required fields before saving
    # Record user creation/update to blockchain
    # Update local database file
```

### 6. Blockchain Integration
```python
# Record All User Actions
def record_user_action(action_type, user_data, user_email):
    from civic_desktop.blockchain.blockchain import Blockchain
    
    success = Blockchain.add_page(
        action_type=action_type,  # "user_registration", "user_login", "role_assignment"
        data=user_data,
        user_email=user_email
    )
    return success
```

## UI/UX Requirements

### Registration Interface
- **Progress Indicator**: Clear 5-step progress bar
- **Real-Time Validation**: Immediate feedback on field completion
- **Help Tooltips**: Contextual help for each step
- **Error Handling**: User-friendly error messages
- **Security Explanation**: Clear explanation of key generation

### Login Interface
- **Simple Design**: Email/password with "Remember Me"
- **Password Recovery**: Clear reset process
- **Session Security**: Auto-logout warnings
- **Role Dashboard**: Personalized interface based on user role

### Dashboard Features
- **Role-Specific UI**: Show features based on user permissions
- **Quick Actions**: Easy access to common tasks
- **Notification Center**: Updates and alerts
- **Profile Management**: Account settings and preferences

## Blockchain Data Requirements
ALL user actions must be recorded to blockchain with these action types:
- `user_registration`: Complete user profile, encrypted ID hash
- `user_login`: Login timestamp, session start
- `role_assignment`: Role changes, election results
- `profile_update`: Profile modifications with before/after
- `password_change`: Security event timestamp (not actual password)

## Error Handling & Validation
- Use `utils.validation.DataValidator` for all input validation
- Provide clear, actionable error messages
- Log security events and failed attempts
- Implement rate limiting for login attempts

## Integration Points
- **Session Management**: Used by ALL other modules
- **Role Checking**: Permissions enforced across platform
- **Blockchain Recording**: Audit trail for all actions
- **Configuration**: Environment-aware paths and settings

## Testing Requirements
Create tests for:
- Registration workflow completeness
- Authentication security measures
- Role-based permission enforcement  
- Blockchain integration accuracy
- Session management reliability
- Input validation effectiveness