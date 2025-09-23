# Preliminary User Ranks Implementation Plan

## Overview
Implementation of missing preliminary user ranks to create a graduated verification system:
- **Junior Contract Citizen** (Under 18 with parental consent)
- **Prospect Contract Citizen** (Unverified information) 
- **Probation Contract Citizen** (Training incomplete)
- **Contract Citizen** (Full verified status)

## Current System Analysis

### Existing Registration Flow
```python
# users/backend.py line 200+
def register_user():
    # Creates user with immediate "Contract Citizen" role
    # No age verification, information verification, or training requirements
    # Direct access to all citizen features
```

### Implementation Requirements

## 1. Junior Contract Citizen (Under 18)

### Features & Restrictions
- **Age Requirement**: Under 18 years old
- **Parental Consent**: Required guardian approval and verification
- **Permissions**: 
  - ✅ View public debates (read-only)
  - ✅ Access training materials appropriate for age
  - ✅ Participate in youth civic education programs
  - ❌ Vote in elections
  - ❌ Create debate topics
  - ❌ Submit moderation reports
  - ❌ Access adult-oriented content

### Implementation Tasks
1. **Add birth date validation** to registration form
2. **Create parental consent system** with guardian verification
3. **Implement age-appropriate content filtering**
4. **Design youth-specific training curriculum**
5. **Add automatic promotion at 18th birthday**

### Code Changes Required
```python
# utils/validation.py - Add date validation
@staticmethod
def validate_birth_date(birth_date: str) -> Tuple[bool, str, int]:
    """Validate birth date and calculate age"""
    
# users/registration.py - Add birth date field and parental consent
# Add DateEdit widget for birth date selection
# Add parental consent checkbox and verification system

# users/backend.py - Modify registration logic
def determine_initial_rank(user_data):
    age = calculate_age(user_data['birth_date'])
    if age < 18:
        return "Junior Contract Citizen"
    # Continue with other verification checks...
```

## 2. Prospect Contract Citizen (Unverified)

### Features & Restrictions  
- **Status**: Registered but information not verified
- **Verification Required**: Government ID, address confirmation, email verification
- **Permissions**:
  - ✅ View public content
  - ✅ Access basic training materials
  - ✅ Complete identity verification process
  - ❌ Participate in debates
  - ❌ Vote in any elections
  - ❌ Submit content or reports

### Implementation Tasks
1. **Enhanced ID document verification system**
2. **Address verification via mail/digital methods**
3. **Multi-step email verification with confirmation codes**
4. **Integration with identity verification services**
5. **Manual review queue for complex cases**

### Code Changes Required
```python
# users/verification.py - New module for verification processes
class VerificationManager:
    def verify_government_id(self, user_email, id_document_path):
    def verify_address(self, user_email, verification_method):
    def check_verification_status(self, user_email):

# users/backend.py - Add verification status tracking
# Modify user model to include verification fields
# Add promotion logic from Prospect to Probation status
```

## 3. Probation Contract Citizen (Training Incomplete)

### Features & Restrictions
- **Status**: Information verified but civic training incomplete
- **Training Requirement**: Must complete mandatory civic education courses
- **Permissions**:
  - ✅ View all content (read-only mode)
  - ✅ Access full training curriculum  
  - ✅ Take quizzes and track progress
  - ❌ Participate in debates until training complete
  - ❌ Vote until certified
  - ❌ Create any content

### Implementation Tasks
1. **Define mandatory training curriculum for citizenship**
2. **Implement training completion tracking and certification**
3. **Create progress dashboard for users**
4. **Add automatic promotion upon training completion**
5. **Design retraining requirements for role changes**

### Code Changes Required
```python
# training/backend.py - Add mandatory course system
def get_mandatory_courses_for_rank(rank):
    """Return required courses for citizenship level"""

def check_training_completion(user_email, required_rank):
    """Verify user has completed all required training"""

# users/backend.py - Add training requirement checking
def can_promote_to_contract_citizen(user_email):
    return TrainingBackend.check_training_completion(user_email, "Contract Citizen")
```

## 4. Enhanced Validation System

### New Validation Methods
```python
# utils/validation.py - Extensions needed

@staticmethod
def validate_birth_date(birth_date: str) -> Tuple[bool, str, int]:
    """Validate birth date and calculate age"""
    from datetime import datetime
    
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        
        # Basic validation
        if age < 0:
            return False, "Birth date cannot be in the future", 0
        if age > 120:
            return False, "Please enter a valid birth date", 0
        
        return True, f"Age: {age} years", age
    except ValueError:
        return False, "Invalid date format (use YYYY-MM-DD)", 0

@staticmethod
def validate_parental_consent(parent_email: str, parent_name: str, minor_email: str) -> Tuple[bool, str]:
    """Validate parental consent for minors"""
    # Validate parent email format
    valid, result = DataValidator.validate_email(parent_email)
    if not valid:
        return False, f"Invalid parent email: {result}"
    
    # Validate parent name
    valid, result = DataValidator.validate_name(parent_name, "Parent name")
    if not valid:
        return False, f"Invalid parent name: {result}"
    
    # Check that parent and minor emails are different
    if parent_email.lower() == minor_email.lower():
        return False, "Parent and minor cannot use the same email address"
    
    return True, "Parental consent validation passed"

@staticmethod
def validate_government_id(id_number: str, id_type: str) -> Tuple[bool, str]:
    """Validate government ID numbers"""
    if not id_number or not id_type:
        return False, "ID number and type are required"
    
    # Remove spaces and special characters
    clean_id = re.sub(r'[^a-zA-Z0-9]', '', id_number)
    
    if len(clean_id) < 5:
        return False, "ID number too short"
    
    if len(clean_id) > 20:
        return False, "ID number too long"
    
    # Validate based on ID type
    valid_types = ['passport', 'drivers_license', 'state_id', 'military_id']
    if id_type.lower() not in valid_types:
        return False, f"Invalid ID type. Accepted: {', '.join(valid_types)}"
    
    return True, clean_id
```

## 5. User Interface Updates

### Registration Form Enhancement
```python
# users/registration.py - Add new fields

class RegistrationWidget(QWidget):
    def __init__(self):
        # Existing fields...
        
        # Add birth date selection
        self.birth_date_label = QLabel("Birth Date:")
        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.birth_date_edit.setMaximumDate(QDate.currentDate())
        
        # Add government ID fields
        self.id_type_label = QLabel("Government ID Type:")
        self.id_type_combo = QComboBox()
        self.id_type_combo.addItems(["Passport", "Driver's License", "State ID", "Military ID"])
        
        self.id_number_label = QLabel("ID Number:")
        self.id_number_edit = QLineEdit()
        
        # Parental consent section (shown conditionally)
        self.parental_consent_group = QGroupBox("Parental Consent (Required for under 18)")
        self.parent_name_edit = QLineEdit()
        self.parent_email_edit = QLineEdit()
        self.consent_checkbox = QCheckBox("I consent to my minor child's participation")
        
    def on_birth_date_changed(self):
        """Show/hide parental consent based on age"""
        birth_date = self.birth_date_edit.date().toString("yyyy-MM-dd")
        valid, message, age = DataValidator.validate_birth_date(birth_date)
        
        if valid and age < 18:
            self.parental_consent_group.setVisible(True)
        else:
            self.parental_consent_group.setVisible(False)
```

### Dashboard Updates
```python
# users/dashboard.py - Add verification status display

def update_user_status_display(self):
    user = SessionManager.get_current_user()
    role = user.get('role', 'Unknown')
    
    # Add status indicators
    if role == "Junior Contract Citizen":
        self.status_label.setText("👤 Junior Citizen (Under 18)")
        self.add_age_verification_reminder()
    elif role == "Prospect Contract Citizen":
        self.status_label.setText("📋 Prospect Citizen (Verification Pending)")
        self.add_verification_progress()
    elif role == "Probation Contract Citizen":
        self.status_label.setText("🎓 Probation Citizen (Training Required)")
        self.add_training_progress()
    else:
        self.status_label.setText(f"✅ {role}")
```

## 6. Promotion System

### Automatic Rank Progression
```python
# users/rank_manager.py - New module for rank progression

class RankManager:
    @staticmethod
    def check_promotion_eligibility(user_email):
        """Check if user can be promoted to next rank"""
        user = UserBackend.get_user(user_email)
        current_rank = user.get('role', '')
        
        if current_rank == "Junior Contract Citizen":
            # Check if user has reached 18
            birth_date = user.get('birth_date', '')
            valid, message, age = DataValidator.validate_birth_date(birth_date)
            if valid and age >= 18:
                return "Prospect Contract Citizen", "Reached age of majority"
        
        elif current_rank == "Prospect Contract Citizen":
            # Check if verification is complete
            if VerificationManager.is_fully_verified(user_email):
                return "Probation Contract Citizen", "Identity verification complete"
        
        elif current_rank == "Probation Contract Citizen":
            # Check if mandatory training is complete
            if TrainingBackend.check_training_completion(user_email, "Contract Citizen"):
                return "Contract Citizen", "Civic training certification complete"
        
        return None, "No promotion available"
    
    @staticmethod
    def promote_user(user_email, new_rank, reason):
        """Promote user to new rank with blockchain record"""
        # Update user record
        UserBackend.update_user_role(user_email, new_rank)
        
        # Record promotion in blockchain
        from civic_desktop.blockchain.blockchain import Blockchain
        Blockchain.add_page(
            action_type="rank_promotion",
            data={
                'user_email': user_email,
                'old_rank': UserBackend.get_user(user_email).get('role'),
                'new_rank': new_rank,
                'reason': reason,
                'promotion_date': datetime.now().isoformat()
            },
            user_email=user_email
        )
```

## 7. Implementation Priority

### Phase 1: Foundation (Week 1-2)
1. Add birth date validation to utils/validation.py
2. Modify registration form to include birth date
3. Update user backend to support preliminary ranks
4. Implement basic age-based rank assignment

### Phase 2: Verification System (Week 3-4)  
1. Create verification manager module
2. Implement ID document verification
3. Add address verification system
4. Build verification status tracking

### Phase 3: Training Integration (Week 5-6)
1. Define mandatory training curriculum
2. Implement training completion tracking
3. Create automatic promotion system
4. Add training progress dashboard

### Phase 4: UI/UX Enhancements (Week 7-8)
1. Update registration UI with all new fields
2. Enhance dashboard with status indicators
3. Add verification and training progress displays
4. Implement user guidance system

## 8. Testing Requirements

### Test Cases Needed
1. **Age Verification Tests**
   - Under 18 registration with parental consent
   - Automatic promotion at 18th birthday
   - Age calculation edge cases

2. **Verification System Tests**
   - ID document upload and validation
   - Address verification workflows
   - Multi-step verification completion

3. **Training Completion Tests**
   - Mandatory course completion tracking
   - Certification issuance and verification
   - Promotion upon training completion

4. **Permission System Tests**
   - Access control for each rank level
   - Feature restrictions and allowances
   - UI element visibility based on rank

## 9. Security Considerations

### Data Protection
- Birth dates stored securely with encryption
- Parental consent records with audit trails
- ID documents processed with strict security protocols
- Age verification with privacy protection

### Access Control
- Graduated permissions prevent unauthorized access
- Training requirements ensure informed participation
- Verification gates prevent fake accounts
- Blockchain audit trail for all rank changes

## 10. Configuration Updates

### New Constants Required
```python
# users/constants.py - Add preliminary rank constants

PRELIMINARY_RANKS = {
    "Junior Contract Citizen": {
        "age_requirement": "under_18",
        "parental_consent": True,
        "training_required": ["youth_civics_basics"],
        "permissions": ["view_public", "youth_training"],
        "restrictions": ["no_voting", "no_debate_creation", "content_filtered"]
    },
    "Prospect Contract Citizen": {
        "verification_required": ["identity", "address", "email"],
        "permissions": ["view_content", "basic_training"],
        "restrictions": ["no_participation", "no_voting", "read_only"]
    },
    "Probation Contract Citizen": {
        "training_required": ["constitutional_law", "civic_responsibilities", "platform_governance"],
        "permissions": ["view_all", "training_access", "progress_tracking"],
        "restrictions": ["no_participation_until_certified"]
    }
}

MANDATORY_TRAINING_PATHS = {
    "Junior_to_Prospect": ["youth_civics_completion"],
    "Prospect_to_Probation": ["identity_verification_complete"], 
    "Probation_to_Citizen": ["constitutional_law", "civic_responsibilities", "platform_governance"]
}
```

This implementation plan provides a comprehensive graduated verification system that ensures users progress through appropriate stages of civic education and verification before gaining full platform privileges. The system maintains security while providing appropriate access at each level.