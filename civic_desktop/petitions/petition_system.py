"""
Petition System Backend - Democratic Citizen Initiative Management
Handles petition creation, signature collection, and initiative processes for direct democracy.
Supports constitutional petition system and citizen initiative management.
"""

import json
import hashlib
import datetime
import os
import uuid
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class PetitionType(Enum):
    """Types of petitions supported by the system"""
    LOCAL = "local"
    STATE = "state" 
    FEDERAL = "federal"
    CONSTITUTIONAL_AMENDMENT = "constitutional_amendment"

class PetitionStatus(Enum):
    """Petition lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    SIGNATURE_COLLECTION = "signature_collection"
    UNDER_REVIEW = "under_review"
    CERTIFIED = "certified"
    APPROVED = "approved"
    REJECTED = "rejected"
    BALLOT_PLACED = "ballot_placed"
    IMPLEMENTED = "implemented"

@dataclass
class PetitionSignature:
    """Individual petition signature with verification"""
    petition_id: str
    signer_email: str
    signature_hash: str
    timestamp: str
    verified: bool
    geographic_data: Dict[str, str]

class PetitionSystem:
    """
    Comprehensive petition and initiative management system
    Supports citizen-driven legislative processes with cryptographic verification
    """
    
    def __init__(self):
        """Initialize petition system with database and blockchain integration"""
        self.db_path = self._get_db_path()
        self.data = self._load_data()
        
    def _get_db_path(self) -> str:
        """Get environment-specific database path"""
        try:
            from civic_desktop.main import ENV_CONFIG
            return ENV_CONFIG.get('petitions_db_path', 'civic_desktop/petitions/petitions_db.json')
        except:
            return 'civic_desktop/petitions/petitions_db.json'
    
    def _load_data(self) -> Dict[str, Any]:
        """Load petition data from JSON database"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_default_structure()
        except Exception as e:
            print(f"Error loading petitions data: {e}")
            return self._create_default_structure()
    
    def _create_default_structure(self) -> Dict[str, Any]:
        """Create default petition database structure"""
        return {
            "petitions": [],
            "signatures": [],
            "initiatives": [],
            "campaigns": [],
            "settings": {
                "signature_requirements": {
                    "local_petition": 100,
                    "state_petition": 1000,
                    "federal_petition": 10000,
                    "constitutional_amendment": 50000
                },
                "verification_settings": {
                    "require_identity_verification": True,
                    "duplicate_prevention": True,
                    "geographic_validation": True
                },
                "timeline_requirements": {
                    "signature_collection_period_days": 90,
                    "public_comment_period_days": 30,
                    "legislative_review_period_days": 60
                }
            }
        }
    
    def _save_data(self) -> bool:
        """Save petition data to JSON database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving petitions data: {e}")
            return False
    
    def _log_to_blockchain(self, action_type: str, data: Dict[str, Any], user_email: str):
        """Log petition actions to blockchain for transparency"""
        try:
            from civic_desktop.blockchain.blockchain import Blockchain
            Blockchain.add_page(action_type, data, user_email)
        except Exception as e:
            print(f"Blockchain logging error: {e}")
    
    def get_petitions(self, status_filter: Optional[str] = None, 
                     petition_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all petitions with optional filtering"""
        petitions = self.data.get('petitions', [])
        
        if status_filter:
            petitions = [p for p in petitions if p.get('status') == status_filter]
        
        if petition_type:
            petitions = [p for p in petitions if p.get('type') == petition_type]
        
        # Sort by creation date, newest first
        return sorted(petitions, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def create_petition(self, creator_email: str, title: str, description: str,
                       petition_type: str, target_signatures: int,
                       jurisdiction: str, full_text: str = "") -> Tuple[bool, str]:
        """Create new petition with constitutional compliance checking"""
        try:
            # Validate inputs
            if not all([creator_email, title, description, petition_type]):
                return False, "Missing required petition information"
            
            if not self._validate_petition_creator(creator_email):
                return False, "User not authorized to create petitions"
            
            # Check constitutional compliance
            compliance_check = self._check_constitutional_compliance(
                title, description, full_text, petition_type
            )
            
            if not compliance_check[0]:
                return False, f"Constitutional compliance issue: {compliance_check[1]}"
            
            # Calculate signature requirements
            calculated_signatures = self._calculate_signature_requirement(
                petition_type, jurisdiction
            )
            
            if target_signatures < calculated_signatures:
                target_signatures = calculated_signatures
            
            # Create petition
            petition_id = str(uuid.uuid4())
            petition_data = {
                'id': petition_id,
                'title': title,
                'description': description,
                'full_text': full_text,
                'type': petition_type,
                'creator_email': creator_email,
                'jurisdiction': jurisdiction,
                'target_signatures': target_signatures,
                'current_signatures': 0,
                'status': PetitionStatus.ACTIVE.value,
                'created_at': datetime.datetime.now().isoformat(),
                'deadline': self._calculate_deadline(petition_type),
                'legal_review': compliance_check[2],
                'campaign_id': str(uuid.uuid4()),
                'public_comment_period': {
                    'start_date': None,
                    'end_date': None,
                    'comments': []
                }
            }
            
            # Save petition
            self.data['petitions'].append(petition_data)
            self._save_data()
            
            # Log to blockchain
            self._log_to_blockchain(
                "petition_created", 
                petition_data, 
                creator_email
            )
            
            return True, f"Petition created successfully with ID: {petition_id}"
            
        except Exception as e:
            return False, f"Error creating petition: {str(e)}"
    
    def sign_petition(self, petition_id: str, signer_email: str,
                     signer_data: Dict[str, str]) -> Tuple[bool, str]:
        """Add cryptographic signature to petition"""
        try:
            # Find petition
            petition = self._find_petition_by_id(petition_id)
            if not petition:
                return False, "Petition not found"
            
            # Validate petition status
            if petition['status'] != PetitionStatus.ACTIVE.value:
                return False, "Petition is not accepting signatures"
            
            # Check deadline
            if datetime.datetime.now() > datetime.datetime.fromisoformat(petition['deadline']):
                return False, "Petition signature deadline has passed"
            
            # Verify signer eligibility
            eligibility_check = self._verify_signer_eligibility(
                petition_id, signer_email, signer_data
            )
            
            if not eligibility_check[0]:
                return False, f"Signature not eligible: {eligibility_check[1]}"
            
            # Check for duplicate signatures
            if self._has_already_signed(petition_id, signer_email):
                return False, "You have already signed this petition"
            
            # Create cryptographic signature
            signature_hash = self._create_signature_hash(
                petition_id, signer_email, signer_data
            )
            
            # Create signature record
            signature_data = {
                'id': str(uuid.uuid4()),
                'petition_id': petition_id,
                'signer_email': signer_email,
                'signature_hash': signature_hash,
                'timestamp': datetime.datetime.now().isoformat(),
                'verified': True,
                'geographic_data': {
                    'city': signer_data.get('city', ''),
                    'state': signer_data.get('state', ''),
                    'country': signer_data.get('country', '')
                },
                'verification_method': 'cryptographic_hash'
            }
            
            # Add signature
            self.data['signatures'].append(signature_data)
            
            # Update petition signature count
            petition['current_signatures'] += 1
            
            # Check if signature target reached
            if petition['current_signatures'] >= petition['target_signatures']:
                petition['status'] = PetitionStatus.UNDER_REVIEW.value
                self._initiate_review_process(petition_id)
            
            self._save_data()
            
            # Log to blockchain
            self._log_to_blockchain(
                "signature_collected",
                {
                    'petition_id': petition_id,
                    'signature_count': petition['current_signatures'],
                    'signature_hash': signature_hash
                },
                signer_email
            )
            
            return True, "Signature added successfully"
            
        except Exception as e:
            return False, f"Error adding signature: {str(e)}"
    
    def get_petition_signatures(self, petition_id: str) -> List[Dict[str, Any]]:
        """Get all signatures for a petition (anonymized for privacy)"""
        signatures = [
            s for s in self.data.get('signatures', [])
            if s['petition_id'] == petition_id
        ]
        
        # Return anonymized signature data for privacy
        return [
            {
                'id': sig['id'],
                'timestamp': sig['timestamp'],
                'verified': sig['verified'],
                'city': sig['geographic_data'].get('city', 'Unknown'),
                'state': sig['geographic_data'].get('state', 'Unknown'),
                'signature_hash': sig['signature_hash'][:8] + '...'  # Truncated for privacy
            }
            for sig in signatures
        ]
    
    def advance_to_initiative(self, petition_id: str, reviewer_email: str) -> Tuple[bool, str]:
        """Advance successful petition to initiative process"""
        try:
            # Verify reviewer permissions
            if not self._can_advance_initiative(reviewer_email):
                return False, "Insufficient permissions to advance initiatives"
            
            petition = self._find_petition_by_id(petition_id)
            if not petition:
                return False, "Petition not found"
            
            if petition['current_signatures'] < petition['target_signatures']:
                return False, "Petition has not met signature requirements"
            
            # Create initiative from petition
            initiative_data = {
                'id': str(uuid.uuid4()),
                'petition_id': petition_id,
                'title': petition['title'],
                'description': petition['description'],
                'full_text': petition['full_text'],
                'type': petition['type'],
                'status': 'legislative_review',
                'advanced_by': reviewer_email,
                'advanced_at': datetime.datetime.now().isoformat(),
                'legislative_review': {
                    'start_date': datetime.datetime.now().isoformat(),
                    'end_date': self._calculate_review_deadline(),
                    'reviewer_assignments': [],
                    'review_comments': []
                },
                'ballot_certification': {
                    'certified': False,
                    'certification_date': None,
                    'election_scheduled': None
                }
            }
            
            # Update petition status
            petition['status'] = PetitionStatus.CERTIFIED.value
            
            # Add initiative
            self.data['initiatives'].append(initiative_data)
            self._save_data()
            
            # Log to blockchain
            self._log_to_blockchain(
                "initiative_advanced",
                initiative_data,
                reviewer_email
            )
            
            return True, f"Initiative created with ID: {initiative_data['id']}"
            
        except Exception as e:
            return False, f"Error advancing to initiative: {str(e)}"
    
    def get_petition_statistics(self) -> Dict[str, Any]:
        """Get comprehensive petition system statistics"""
        petitions = self.data.get('petitions', [])
        signatures = self.data.get('signatures', [])
        initiatives = self.data.get('initiatives', [])
        
        # Calculate statistics
        stats = {
            'total_petitions': len(petitions),
            'active_petitions': len([p for p in petitions if p['status'] == 'active']),
            'completed_petitions': len([p for p in petitions if p['status'] == 'certified']),
            'total_signatures': len(signatures),
            'total_initiatives': len(initiatives),
            'petitions_by_type': {},
            'petitions_by_status': {},
            'signature_trends': self._calculate_signature_trends(),
            'success_rate': self._calculate_success_rate(),
            'geographic_distribution': self._get_geographic_distribution()
        }
        
        # Group by type
        for petition in petitions:
            petition_type = petition.get('type', 'unknown')
            stats['petitions_by_type'][petition_type] = stats['petitions_by_type'].get(petition_type, 0) + 1
        
        # Group by status  
        for petition in petitions:
            status = petition.get('status', 'unknown')
            stats['petitions_by_status'][status] = stats['petitions_by_status'].get(status, 0) + 1
        
        return stats
    
    def _validate_petition_creator(self, creator_email: str) -> bool:
        """Validate if user can create petitions"""
        try:
            from civic_desktop.users.session import SessionManager
            
            if not SessionManager.is_authenticated():
                return False
            
            user = SessionManager.get_current_user()
            if not user or user.get('email') != creator_email:
                return False
            
            # All Contract Citizens can create petitions
            user_role = user.get('role', 'Contract Citizen')
            return user_role in [
                'Contract Citizen', 'Contract Representative', 
                'Contract Senator', 'Contract Elder', 'Contract Founder'
            ]
            
        except:
            return False
    
    def _check_constitutional_compliance(self, title: str, description: str,
                                      full_text: str, petition_type: str) -> Tuple[bool, str, Dict]:
        """Check petition for constitutional compliance"""
        compliance_report = {
            'reviewed_at': datetime.datetime.now().isoformat(),
            'review_type': 'automated_initial',
            'issues_found': [],
            'constitutional_status': 'pending_elder_review',
            'recommendations': []
        }
        
        # Basic content validation
        if not title or len(title.strip()) < 10:
            compliance_report['issues_found'].append("Title too short or missing")
        
        if not description or len(description.strip()) < 50:
            compliance_report['issues_found'].append("Description too brief")
        
        # Check for prohibited content (basic)
        prohibited_terms = ['violence', 'discrimination', 'illegal', 'unconstitutional']
        content = f"{title} {description} {full_text}".lower()
        
        for term in prohibited_terms:
            if term in content:
                compliance_report['issues_found'].append(f"Potentially problematic content: {term}")
        
        # Constitutional amendment petitions need Elder review
        if petition_type == 'constitutional_amendment':
            compliance_report['recommendations'].append("Requires Contract Elder constitutional review")
        
        is_compliant = len(compliance_report['issues_found']) == 0
        message = "Passes initial compliance check" if is_compliant else "Issues found - review required"
        
        return is_compliant, message, compliance_report
    
    def _calculate_signature_requirement(self, petition_type: str, jurisdiction: str) -> int:
        """Calculate required signatures based on type and jurisdiction"""
        requirements = self.data['settings']['signature_requirements']
        
        base_requirement = requirements.get(petition_type, 1000)
        
        # Adjust for jurisdiction size (simplified)
        jurisdiction_multipliers = {
            'local': 0.1,
            'city': 0.5,
            'state': 1.0,
            'federal': 2.0
        }
        
        multiplier = jurisdiction_multipliers.get(jurisdiction.lower(), 1.0)
        return max(int(base_requirement * multiplier), 10)  # Minimum 10 signatures
    
    def _calculate_deadline(self, petition_type: str) -> str:
        """Calculate petition deadline based on type"""
        days = self.data['settings']['timeline_requirements']['signature_collection_period_days']
        
        # Constitutional amendments get longer periods
        if petition_type == 'constitutional_amendment':
            days = days * 2
        
        deadline = datetime.datetime.now() + datetime.timedelta(days=days)
        return deadline.isoformat()
    
    def _verify_signer_eligibility(self, petition_id: str, signer_email: str,
                                 signer_data: Dict[str, str]) -> Tuple[bool, str]:
        """Verify if user is eligible to sign petition"""
        try:
            from civic_desktop.users.backend import UserBackend
            
            # Check if user exists and is verified
            users = UserBackend().get_users()
            user = next((u for u in users if u.get('email') == signer_email), None)
            
            if not user:
                return False, "User not found in system"
            
            # Check if user has Contract Citizen status or higher
            user_role = user.get('role', 'Contract Citizen')
            if user_role not in ['Contract Citizen', 'Contract Representative', 
                               'Contract Senator', 'Contract Elder', 'Contract Founder']:
                return False, "User must have Contract Citizen status to sign petitions"
            
            # Verify geographic eligibility (simplified)
            petition = self._find_petition_by_id(petition_id)
            if petition and petition.get('jurisdiction'):
                user_state = user.get('state', '')
                petition_jurisdiction = petition.get('jurisdiction', '')
                
                # For state/local petitions, verify geographic eligibility
                if 'state' in petition_jurisdiction.lower() and user_state.lower() not in petition_jurisdiction.lower():
                    return False, "Geographic eligibility requirements not met"
            
            return True, "Eligible to sign petition"
            
        except Exception as e:
            return False, f"Eligibility verification error: {str(e)}"
    
    def _has_already_signed(self, petition_id: str, signer_email: str) -> bool:
        """Check if user has already signed petition"""
        signatures = self.data.get('signatures', [])
        return any(
            sig['petition_id'] == petition_id and sig['signer_email'] == signer_email
            for sig in signatures
        )
    
    def _create_signature_hash(self, petition_id: str, signer_email: str,
                             signer_data: Dict[str, str]) -> str:
        """Create cryptographic hash for signature verification"""
        signature_content = f"{petition_id}:{signer_email}:{datetime.datetime.now().isoformat()}"
        for key in sorted(signer_data.keys()):
            signature_content += f":{key}:{signer_data[key]}"
        
        return hashlib.sha256(signature_content.encode()).hexdigest()
    
    def _find_petition_by_id(self, petition_id: str) -> Optional[Dict[str, Any]]:
        """Find petition by ID"""
        petitions = self.data.get('petitions', [])
        return next((p for p in petitions if p['id'] == petition_id), None)
    
    def _initiate_review_process(self, petition_id: str):
        """Initiate review process for completed petition"""
        petition = self._find_petition_by_id(petition_id)
        if petition:
            # Start public comment period
            petition['public_comment_period']['start_date'] = datetime.datetime.now().isoformat()
            comment_days = self.data['settings']['timeline_requirements']['public_comment_period_days']
            end_date = datetime.datetime.now() + datetime.timedelta(days=comment_days)
            petition['public_comment_period']['end_date'] = end_date.isoformat()
    
    def _can_advance_initiative(self, reviewer_email: str) -> bool:
        """Check if user can advance petitions to initiatives"""
        try:
            from civic_desktop.users.session import SessionManager
            
            user = SessionManager.get_current_user()
            if not user or user.get('email') != reviewer_email:
                return False
            
            # Representatives, Senators, and Elders can advance initiatives
            user_role = user.get('role', 'Contract Citizen')
            return user_role in [
                'Contract Representative', 'Contract Senator', 
                'Contract Elder', 'Contract Founder'
            ]
            
        except:
            return False
    
    def _calculate_review_deadline(self) -> str:
        """Calculate legislative review deadline"""
        days = self.data['settings']['timeline_requirements']['legislative_review_period_days']
        deadline = datetime.datetime.now() + datetime.timedelta(days=days)
        return deadline.isoformat()
    
    def _calculate_signature_trends(self) -> Dict[str, Any]:
        """Calculate signature collection trends"""
        signatures = self.data.get('signatures', [])
        
        # Group signatures by date
        daily_counts = {}
        for sig in signatures:
            try:
                date = datetime.datetime.fromisoformat(sig['timestamp']).date().isoformat()
                daily_counts[date] = daily_counts.get(date, 0) + 1
            except:
                continue
        
        # Calculate trend
        if len(daily_counts) < 2:
            trend = "insufficient_data"
        else:
            recent_avg = sum(list(daily_counts.values())[-7:]) / min(7, len(daily_counts))
            older_avg = sum(list(daily_counts.values())[:-7]) / max(1, len(daily_counts) - 7)
            
            if recent_avg > older_avg * 1.1:
                trend = "increasing"
            elif recent_avg < older_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        
        return {
            'daily_signature_counts': daily_counts,
            'trend': trend,
            'total_signatures_last_30_days': sum(
                count for date, count in daily_counts.items()
                if (datetime.datetime.now().date() - datetime.date.fromisoformat(date)).days <= 30
            )
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate petition success rate"""
        petitions = self.data.get('petitions', [])
        if not petitions:
            return 0.0
        
        successful = len([p for p in petitions if p.get('status') in ['certified', 'approved', 'implemented']])
        return round((successful / len(petitions)) * 100, 2)
    
    def _get_geographic_distribution(self) -> Dict[str, int]:
        """Get geographic distribution of petition signatures"""
        signatures = self.data.get('signatures', [])
        distribution = {}
        
        for sig in signatures:
            state = sig.get('geographic_data', {}).get('state', 'Unknown')
            distribution[state] = distribution.get(state, 0) + 1
        
        return distribution