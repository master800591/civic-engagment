"""
BLOCKCHAIN TERM LIMIT VERIFICATION SYSTEM
Provides blockchain-based verification of term limits for all governance levels
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Import blockchain for term limit storage and verification
try:
    from civic_desktop.blockchain.blockchain import CivicBlockchain
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    print("Warning: Blockchain not available for term limit verification")
    BLOCKCHAIN_AVAILABLE = False

# Import user backend for role verification
try:
    from civic_desktop.users.backend import UserBackend
    USER_BACKEND_AVAILABLE = True
except ImportError:
    print("Warning: User backend not available for term limit verification")
    USER_BACKEND_AVAILABLE = False


class TermLimitLevel(Enum):
    """Governance levels with term limits"""
    CITY = "city"
    STATE = "state"
    COUNTRY = "country"
    WORLD = "world"


class TermLimitOffice(Enum):
    """Offices with term limit restrictions"""
    REPRESENTATIVE = "representative"
    SENATOR = "senator"
    ELDER = "elder"


@dataclass
class TermRecord:
    """Individual term service record"""
    term_id: str
    user_email: str
    level: TermLimitLevel
    office: TermLimitOffice
    jurisdiction: str  # city_id, state_id, country_id, or "world"
    start_date: str
    end_date: str
    term_length_days: int
    election_type: str  # "regular", "special", "recall"
    blockchain_page_id: str  # Reference to blockchain record
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'term_id': self.term_id,
            'user_email': self.user_email,
            'level': self.level.value,
            'office': self.office.value,
            'jurisdiction': self.jurisdiction,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'term_length_days': self.term_length_days,
            'election_type': self.election_type,
            'blockchain_page_id': self.blockchain_page_id
        }


@dataclass
class TermLimitVerification:
    """Term limit eligibility verification result"""
    eligible: bool
    reason: str
    total_terms_served: int
    max_terms_allowed: int
    consecutive_violation: bool
    last_term_end_date: Optional[str]
    days_since_last_term: Optional[int]
    min_break_required_days: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'eligible': self.eligible,
            'reason': self.reason,
            'total_terms_served': self.total_terms_served,
            'max_terms_allowed': self.max_terms_allowed,
            'consecutive_violation': self.consecutive_violation,
            'last_term_end_date': self.last_term_end_date,
            'days_since_last_term': self.days_since_last_term,
            'min_break_required_days': self.min_break_required_days
        }


class BlockchainTermLimitManager:
    """Blockchain-based term limit verification and enforcement system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize blockchain term limit manager"""
        
        self.config_path = config_path
        self.blockchain = CivicBlockchain() if BLOCKCHAIN_AVAILABLE else None
        self.user_backend = UserBackend() if USER_BACKEND_AVAILABLE else None
        
        # Term limit constants (matching corrected rules)
        self.MAX_TOTAL_TERMS = 4
        self.TERM_LENGTH_DAYS = 365  # 1 year
        self.MIN_BREAK_DAYS = 365    # 1 year mandatory break
        
        print("🔐 Blockchain Term Limit Manager initialized")
    
    def record_term_start(self, user_email: str, level: TermLimitLevel, office: TermLimitOffice,
                         jurisdiction: str, election_type: str = "regular") -> Tuple[bool, str, Optional[str]]:
        """Record the start of a new term on blockchain"""
        
        if not self.blockchain:
            return False, "Blockchain not available", None
        
        # Verify eligibility before recording
        verification = self.verify_term_eligibility(user_email, level, office, jurisdiction)
        if not verification.eligible:
            return False, f"Term limit violation: {verification.reason}", None
        
        # Generate term record
        term_id = f"{level.value}_{office.value}_{jurisdiction}_{user_email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() + timedelta(days=self.TERM_LENGTH_DAYS)).isoformat()
        
        term_data = {
            'action_type': 'term_start',
            'term_record': {
                'term_id': term_id,
                'user_email': user_email,
                'level': level.value,
                'office': office.value,
                'jurisdiction': jurisdiction,
                'start_date': start_date,
                'end_date': end_date,
                'term_length_days': self.TERM_LENGTH_DAYS,
                'election_type': election_type
            },
            'verification': verification.to_dict(),
            'governance_compliance': {
                'max_terms_rule': f'Maximum {self.MAX_TOTAL_TERMS} terms total',
                'consecutive_restriction': 'Terms cannot be consecutive',
                'break_requirement': f'Minimum {self.MIN_BREAK_DAYS} day break required',
                'constitutional_authority': 'Contract-based governance system'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Record on blockchain
        success, message, page_id = self.blockchain.add_page(
            action_type="governance_term_start",
            user_email=user_email,
            data=term_data
        )
        
        if success:
            print(f"✅ Term start recorded: {user_email} - {level.value} {office.value} in {jurisdiction}")
            return True, f"Term started and recorded on blockchain", page_id
        else:
            return False, f"Failed to record term start: {message}", None
    
    def record_term_end(self, user_email: str, level: TermLimitLevel, office: TermLimitOffice,
                       jurisdiction: str, reason: str = "term_completed") -> Tuple[bool, str, Optional[str]]:
        """Record the end of a term on blockchain"""
        
        if not self.blockchain:
            return False, "Blockchain not available", None
        
        end_date = datetime.now().isoformat()
        
        term_data = {
            'action_type': 'term_end',
            'term_record': {
                'user_email': user_email,
                'level': level.value,
                'office': office.value,
                'jurisdiction': jurisdiction,
                'end_date': end_date,
                'end_reason': reason
            },
            'governance_compliance': {
                'next_eligibility': (datetime.now() + timedelta(days=self.MIN_BREAK_DAYS)).isoformat(),
                'consecutive_restriction_note': 'Must wait 1 year before running again',
                'constitutional_authority': 'Contract-based governance system'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Record on blockchain
        success, message, page_id = self.blockchain.add_page(
            action_type="governance_term_end",
            user_email=user_email,
            data=term_data
        )
        
        if success:
            print(f"✅ Term end recorded: {user_email} - {level.value} {office.value} in {jurisdiction}")
            return True, f"Term end recorded on blockchain", page_id
        else:
            return False, f"Failed to record term end: {message}", None
    
    def verify_term_eligibility(self, user_email: str, level: TermLimitLevel, 
                               office: TermLimitOffice, jurisdiction: str) -> TermLimitVerification:
        """Verify if user is eligible to serve another term"""
        
        try:
            # Get all previous terms from blockchain
            previous_terms = self._get_blockchain_term_history(user_email, level, office, jurisdiction)
            
            # Check maximum total terms
            if len(previous_terms) >= self.MAX_TOTAL_TERMS:
                return TermLimitVerification(
                    eligible=False,
                    reason=f"Maximum {self.MAX_TOTAL_TERMS} terms reached for {level.value} {office.value}",
                    total_terms_served=len(previous_terms),
                    max_terms_allowed=self.MAX_TOTAL_TERMS,
                    consecutive_violation=False,
                    last_term_end_date=None,
                    days_since_last_term=None,
                    min_break_required_days=self.MIN_BREAK_DAYS
                )
            
            # Check consecutive terms restriction
            if previous_terms:
                # Sort terms by end date (most recent first)
                sorted_terms = sorted(previous_terms, key=lambda x: x.get('end_date', ''), reverse=True)
                
                for term in sorted_terms:
                    try:
                        term_end = datetime.fromisoformat(term['end_date'])
                        days_since = (datetime.now() - term_end).days
                        
                        # If any term ended less than required break period, violation
                        if days_since < self.MIN_BREAK_DAYS:
                            return TermLimitVerification(
                                eligible=False,
                                reason=f"Must wait {self.MIN_BREAK_DAYS - days_since} more days before serving again",
                                total_terms_served=len(previous_terms),
                                max_terms_allowed=self.MAX_TOTAL_TERMS,
                                consecutive_violation=True,
                                last_term_end_date=term['end_date'],
                                days_since_last_term=days_since,
                                min_break_required_days=self.MIN_BREAK_DAYS
                            )
                    except (ValueError, KeyError) as e:
                        print(f"Error parsing term date: {e}")
                        continue
            
            # Eligible to serve
            last_end = previous_terms[-1]['end_date'] if previous_terms else None
            days_since = (datetime.now() - datetime.fromisoformat(last_end)).days if last_end else None
            
            return TermLimitVerification(
                eligible=True,
                reason="Eligible to serve new term",
                total_terms_served=len(previous_terms),
                max_terms_allowed=self.MAX_TOTAL_TERMS,
                consecutive_violation=False,
                last_term_end_date=last_end,
                days_since_last_term=days_since,
                min_break_required_days=self.MIN_BREAK_DAYS
            )
            
        except Exception as e:
            print(f"Error verifying term eligibility: {e}")
            # Err on side of caution
            return TermLimitVerification(
                eligible=False,
                reason=f"Unable to verify term history: {str(e)}",
                total_terms_served=0,
                max_terms_allowed=self.MAX_TOTAL_TERMS,
                consecutive_violation=False,
                last_term_end_date=None,
                days_since_last_term=None,
                min_break_required_days=self.MIN_BREAK_DAYS
            )
    
    def _get_blockchain_term_history(self, user_email: str, level: TermLimitLevel, 
                                   office: TermLimitOffice, jurisdiction: str) -> List[Dict[str, Any]]:
        """Get term history from blockchain records"""
        
        if not self.blockchain:
            return []
        
        try:
            # Get blockchain data
            blockchain_data = self.blockchain._load_blockchain_data()
            pages_data = self.blockchain._load_pages_data()
            
            term_records = []
            
            # Search active pages for term records
            for page in pages_data.get('active_pages', []):
                if (page.get('action_type') in ['governance_term_start', 'governance_term_end'] and
                    page.get('user_email') == user_email):
                    
                    page_data = page.get('data', {})
                    term_record = page_data.get('term_record', {})
                    
                    # Check if this matches our criteria
                    if (term_record.get('level') == level.value and
                        term_record.get('office') == office.value and
                        term_record.get('jurisdiction') == jurisdiction):
                        
                        term_records.append(term_record)
            
            # Filter for completed terms (have end_date)
            completed_terms = [record for record in term_records if record.get('end_date')]
            
            return completed_terms
            
        except Exception as e:
            print(f"Error getting blockchain term history: {e}")
            return []
    
    def get_user_term_summary(self, user_email: str) -> Dict[str, Any]:
        """Get comprehensive term summary for user across all levels"""
        
        summary = {
            'user_email': user_email,
            'term_limit_status': {},
            'total_terms_all_levels': 0,
            'current_terms': [],
            'eligibility_status': {},
            'blockchain_verified': self.blockchain is not None
        }
        
        # Check each level and office combination
        for level in TermLimitLevel:
            summary['term_limit_status'][level.value] = {}
            
            for office in TermLimitOffice:
                office_key = f"{level.value}_{office.value}"
                
                # For jurisdiction, we'd need to check all possible jurisdictions
                # For now, use a placeholder jurisdiction check
                jurisdiction = "placeholder"  # Would need actual jurisdiction lookup
                
                verification = self.verify_term_eligibility(user_email, level, office, jurisdiction)
                
                summary['term_limit_status'][level.value][office.value] = {
                    'eligible': verification.eligible,
                    'terms_served': verification.total_terms_served,
                    'max_terms': verification.max_terms_allowed,
                    'consecutive_violation': verification.consecutive_violation,
                    'days_since_last_term': verification.days_since_last_term
                }
                
                summary['total_terms_all_levels'] += verification.total_terms_served
        
        return summary
    
    def audit_all_term_limits(self) -> Dict[str, Any]:
        """Audit all term limit compliance across the system"""
        
        if not self.blockchain:
            return {'error': 'Blockchain not available for audit'}
        
        audit_results = {
            'audit_timestamp': datetime.now().isoformat(),
            'total_users_checked': 0,
            'violations_found': [],
            'compliance_rate': 0.0,
            'recommendations': [],
            'blockchain_integrity': True
        }
        
        try:
            # Get all users from blockchain term records
            blockchain_data = self.blockchain._load_blockchain_data()
            pages_data = self.blockchain._load_pages_data()
            
            users_with_terms = set()
            
            # Collect all users with term records
            for page in pages_data.get('active_pages', []):
                if page.get('action_type') in ['governance_term_start', 'governance_term_end']:
                    users_with_terms.add(page.get('user_email'))
            
            audit_results['total_users_checked'] = len(users_with_terms)
            
            # Check each user for violations
            for user_email in users_with_terms:
                user_summary = self.get_user_term_summary(user_email)
                
                # Check for any violations
                has_violation = False
                for level_data in user_summary['term_limit_status'].values():
                    for office_data in level_data.values():
                        if office_data['consecutive_violation'] or office_data['terms_served'] > self.MAX_TOTAL_TERMS:
                            has_violation = True
                            audit_results['violations_found'].append({
                                'user_email': user_email,
                                'violation_type': 'consecutive' if office_data['consecutive_violation'] else 'max_terms',
                                'details': office_data
                            })
            
            # Calculate compliance rate
            total_violations = len(audit_results['violations_found'])
            audit_results['compliance_rate'] = 1.0 - (total_violations / max(1, audit_results['total_users_checked']))
            
            # Add recommendations
            if total_violations > 0:
                audit_results['recommendations'].append("Review and enforce term limit violations")
                audit_results['recommendations'].append("Implement automated term limit checking in election system")
            
            audit_results['recommendations'].append("Continue blockchain-based term limit tracking")
            
        except Exception as e:
            audit_results['error'] = f"Audit failed: {str(e)}"
            audit_results['blockchain_integrity'] = False
        
        return audit_results


# Example usage and testing functions
def example_term_limit_workflow():
    """Example of how to use the blockchain term limit system"""
    
    print("\n🔐 BLOCKCHAIN TERM LIMIT VERIFICATION EXAMPLE")
    print("=" * 60)
    
    # Initialize manager
    manager = BlockchainTermLimitManager()
    
    # Example user
    user_email = "john.doe@democracy.gov"
    
    # Check initial eligibility
    print("\n1. Initial Eligibility Check:")
    verification = manager.verify_term_eligibility(
        user_email, 
        TermLimitLevel.CITY, 
        TermLimitOffice.REPRESENTATIVE,
        "springfield_il"
    )
    print(f"   Eligible: {verification.eligible}")
    print(f"   Reason: {verification.reason}")
    print(f"   Terms served: {verification.total_terms_served}/{verification.max_terms_allowed}")
    
    # Record term start
    print("\n2. Recording Term Start:")
    success, message, page_id = manager.record_term_start(
        user_email,
        TermLimitLevel.CITY,
        TermLimitOffice.REPRESENTATIVE,
        "springfield_il"
    )
    print(f"   Success: {success}")
    print(f"   Message: {message}")
    if page_id:
        print(f"   Blockchain Page ID: {page_id}")
    
    # Get user summary
    print("\n3. User Term Summary:")
    summary = manager.get_user_term_summary(user_email)
    print(f"   Total terms all levels: {summary['total_terms_all_levels']}")
    print(f"   Blockchain verified: {summary['blockchain_verified']}")
    
    # Run system audit
    print("\n4. System-wide Term Limit Audit:")
    audit = manager.audit_all_term_limits()
    print(f"   Users checked: {audit.get('total_users_checked', 0)}")
    print(f"   Violations found: {len(audit.get('violations_found', []))}")
    print(f"   Compliance rate: {audit.get('compliance_rate', 0.0):.1%}")
    
    print("\n✅ Blockchain term limit verification example complete!")


if __name__ == "__main__":
    example_term_limit_workflow()