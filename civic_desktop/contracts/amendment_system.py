"""
Hierarchical Contract Amendment System
Implements a multi-level governance system for contract modifications with local debate and approval processes.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
import json
import os

class JurisdictionLevel(Enum):
    """Hierarchical levels of governance jurisdiction"""
    CITY = "city"
    STATE = "state" 
    COUNTRY = "country"
    WORLD = "world"

class AmendmentStatus(Enum):
    """Status of contract amendment proposals"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    LOCAL_DEBATE = "local_debate"
    LOCAL_VOTING = "local_voting"
    LOCAL_APPROVED = "local_approved"
    LOCAL_REJECTED = "local_rejected"
    WAITING_ESCALATION = "waiting_escalation"
    ESCALATING = "escalating"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"

class ChangeType(Enum):
    """Types of contract changes"""
    ADDITION = "addition"
    MODIFICATION = "modification"
    REMOVAL = "removal"
    CLARIFICATION = "clarification"

@dataclass
class AmendmentProposal:
    """Represents a proposed amendment to a contract article"""
    id: str
    proposer_email: str
    proposer_name: str
    article_section: str  # e.g., "ARTICLE I.1.A"
    change_type: ChangeType
    current_text: str
    proposed_text: str
    rationale: str
    jurisdiction_level: JurisdictionLevel
    jurisdiction_name: str  # e.g., "Springfield, Illinois"
    status: AmendmentStatus
    created_at: datetime
    votes_for: int = 0
    votes_against: int = 0
    votes_abstain: int = 0
    total_eligible_voters: int = 0
    debate_period_end: Optional[datetime] = None
    voting_period_end: Optional[datetime] = None
    implementation_date: Optional[datetime] = None
    escalation_eligible_date: Optional[datetime] = None
    comments: List[Dict[str, Any]] = field(default_factory=list)
    approval_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return {
            'id': self.id,
            'proposer_email': self.proposer_email,
            'proposer_name': self.proposer_name,
            'article_section': self.article_section,
            'change_type': self.change_type.value,
            'current_text': self.current_text,
            'proposed_text': self.proposed_text,
            'rationale': self.rationale,
            'jurisdiction_level': self.jurisdiction_level.value,
            'jurisdiction_name': self.jurisdiction_name,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'votes_for': self.votes_for,
            'votes_against': self.votes_against,
            'votes_abstain': self.votes_abstain,
            'total_eligible_voters': self.total_eligible_voters,
            'debate_period_end': self.debate_period_end.isoformat() if self.debate_period_end else None,
            'voting_period_end': self.voting_period_end.isoformat() if self.voting_period_end else None,
            'implementation_date': self.implementation_date.isoformat() if self.implementation_date else None,
            'escalation_eligible_date': self.escalation_eligible_date.isoformat() if self.escalation_eligible_date else None,
            'comments': self.comments,
            'approval_history': self.approval_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary (JSON deserialization)"""
        return cls(
            id=data['id'],
            proposer_email=data['proposer_email'],
            proposer_name=data['proposer_name'],
            article_section=data['article_section'],
            change_type=ChangeType(data['change_type']),
            current_text=data['current_text'],
            proposed_text=data['proposed_text'],
            rationale=data['rationale'],
            jurisdiction_level=JurisdictionLevel(data['jurisdiction_level']),
            jurisdiction_name=data['jurisdiction_name'],
            status=AmendmentStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            votes_for=data.get('votes_for', 0),
            votes_against=data.get('votes_against', 0),
            votes_abstain=data.get('votes_abstain', 0),
            total_eligible_voters=data.get('total_eligible_voters', 0),
            debate_period_end=datetime.fromisoformat(data['debate_period_end']) if data.get('debate_period_end') else None,
            voting_period_end=datetime.fromisoformat(data['voting_period_end']) if data.get('voting_period_end') else None,
            implementation_date=datetime.fromisoformat(data['implementation_date']) if data.get('implementation_date') else None,
            escalation_eligible_date=datetime.fromisoformat(data['escalation_eligible_date']) if data.get('escalation_eligible_date') else None,
            comments=data.get('comments', []),
            approval_history=data.get('approval_history', [])
        )

class ContractAmendmentManager:
    """Manages the hierarchical contract amendment process"""
    
    def __init__(self):
        self.amendments_file = os.path.join(os.path.dirname(__file__), 'amendments_db.json')
        self.load_amendments()
        
        # Configuration for timing
        self.DEBATE_PERIOD_DAYS = 30  # 30 days for local debate
        self.VOTING_PERIOD_DAYS = 14  # 14 days for voting
        self.IMPLEMENTATION_WAIT_DAYS = {
            JurisdictionLevel.CITY: 90,    # 3 months before escalation to state
            JurisdictionLevel.STATE: 180,  # 6 months before escalation to country  
            JurisdictionLevel.COUNTRY: 365 # 1 year before escalation to world
        }

    def get_amendment(self, amendment_id: str) -> Optional[AmendmentProposal]:
        """Get a specific amendment by ID"""
        return self.amendments.get(amendment_id)

    def load_amendments(self):
        """Load amendments from JSON file"""
        if os.path.exists(self.amendments_file):
            try:
                with open(self.amendments_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.amendments = {
                        key: AmendmentProposal.from_dict(value) 
                        for key, value in data.items()
                    }
            except Exception as e:
                print(f"Error loading amendments: {e}")
                self.amendments = {}
        else:
            self.amendments = {}

    def save_amendments(self):
        """Save amendments to JSON file"""
        try:
            data = {
                key: amendment.to_dict() 
                for key, amendment in self.amendments.items()
            }
            with open(self.amendments_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving amendments: {e}")

    def generate_amendment_id(self) -> str:
        """Generate unique amendment ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"AMD_{timestamp}_{len(self.amendments):04d}"

    def propose_amendment(self, proposer_email: str, proposer_name: str, 
                         article_section: str, change_type: ChangeType,
                         current_text: str, proposed_text: str, rationale: str,
                         jurisdiction_level: JurisdictionLevel, jurisdiction_name: str) -> str:
        """Submit a new amendment proposal"""
        
        amendment_id = self.generate_amendment_id()
        now = datetime.now(timezone.utc)
        
        amendment = AmendmentProposal(
            id=amendment_id,
            proposer_email=proposer_email,
            proposer_name=proposer_name,
            article_section=article_section,
            change_type=change_type,
            current_text=current_text,
            proposed_text=proposed_text,
            rationale=rationale,
            jurisdiction_level=jurisdiction_level,
            jurisdiction_name=jurisdiction_name,
            status=AmendmentStatus.SUBMITTED,
            created_at=now
        )
        
        self.amendments[amendment_id] = amendment
        self.save_amendments()
        
        # Record on blockchain for transparency
        self._record_amendment_on_blockchain(amendment, "amendment_proposed")
        
        return amendment_id

    def start_local_debate(self, amendment_id: str) -> bool:
        """Start the local debate period for an amendment"""
        if amendment_id not in self.amendments:
            return False
            
        amendment = self.amendments[amendment_id]
        if amendment.status != AmendmentStatus.SUBMITTED:
            return False
            
        now = datetime.now(timezone.utc)
        amendment.status = AmendmentStatus.LOCAL_DEBATE
        amendment.debate_period_end = now + timedelta(days=self.DEBATE_PERIOD_DAYS)
        
        self.save_amendments()
        self._record_amendment_on_blockchain(amendment, "debate_started")
        
        return True

    def add_comment(self, amendment_id: str, commenter_email: str, 
                   commenter_name: str, comment_text: str, 
                   is_support: Optional[bool] = None) -> bool:
        """Add a comment/debate contribution to an amendment"""
        if amendment_id not in self.amendments:
            return False
            
        amendment = self.amendments[amendment_id]
        if amendment.status not in [AmendmentStatus.LOCAL_DEBATE, AmendmentStatus.LOCAL_VOTING]:
            return False
            
        comment = {
            'commenter_email': commenter_email,
            'commenter_name': commenter_name,
            'comment_text': comment_text,
            'is_support': is_support,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        amendment.comments.append(comment)
        self.save_amendments()
        
        return True

    def start_voting_period(self, amendment_id: str) -> bool:
        """Transition amendment from debate to voting period"""
        if amendment_id not in self.amendments:
            return False
            
        amendment = self.amendments[amendment_id]
        if amendment.status != AmendmentStatus.LOCAL_DEBATE:
            return False
            
        now = datetime.now(timezone.utc)
        if amendment.debate_period_end and now < amendment.debate_period_end:
            return False  # Debate period not finished
            
        amendment.status = AmendmentStatus.LOCAL_VOTING
        amendment.voting_period_end = now + timedelta(days=self.VOTING_PERIOD_DAYS)
        
        # Calculate eligible voters in jurisdiction
        amendment.total_eligible_voters = self._get_eligible_voters_count(
            amendment.jurisdiction_level, amendment.jurisdiction_name
        )
        
        self.save_amendments()
        self._record_amendment_on_blockchain(amendment, "voting_started")
        
        return True

    def cast_vote(self, amendment_id: str, voter_email: str, vote: str) -> bool:
        """Cast a vote on an amendment (for/against/abstain)"""
        if amendment_id not in self.amendments:
            return False
            
        amendment = self.amendments[amendment_id]
        if amendment.status != AmendmentStatus.LOCAL_VOTING:
            return False
            
        # Verify voter is eligible in this jurisdiction
        if not self._is_voter_eligible(voter_email, amendment.jurisdiction_level, 
                                      amendment.jurisdiction_name):
            return False
            
        # Record the vote (in a real system, would prevent double-voting)
        if vote.lower() == 'for':
            amendment.votes_for += 1
        elif vote.lower() == 'against':
            amendment.votes_against += 1
        elif vote.lower() == 'abstain':
            amendment.votes_abstain += 1
        else:
            return False
            
        self.save_amendments()
        
        # Check if voting should conclude
        total_votes = amendment.votes_for + amendment.votes_against + amendment.votes_abstain
        if total_votes >= amendment.total_eligible_voters * 0.6:  # 60% participation threshold
            self._conclude_voting(amendment_id)
            
        return True

    def _conclude_voting(self, amendment_id: str):
        """Conclude voting and determine if amendment passes"""
        amendment = self.amendments[amendment_id]
        
        total_decisive_votes = amendment.votes_for + amendment.votes_against
        if total_decisive_votes == 0:
            amendment.status = AmendmentStatus.LOCAL_REJECTED
            return
            
        approval_percentage = amendment.votes_for / total_decisive_votes
        
        if approval_percentage >= 0.5:  # 50% approval required
            amendment.status = AmendmentStatus.LOCAL_APPROVED
            amendment.implementation_date = datetime.now(timezone.utc) + timedelta(days=30)
            
            # Set escalation eligible date
            wait_days = self.IMPLEMENTATION_WAIT_DAYS.get(amendment.jurisdiction_level)
            if wait_days:
                amendment.escalation_eligible_date = amendment.implementation_date + timedelta(days=wait_days)
            
            # Record approval in history
            amendment.approval_history.append({
                'level': amendment.jurisdiction_level.value,
                'jurisdiction': amendment.jurisdiction_name,
                'approved_date': datetime.now(timezone.utc).isoformat(),
                'votes_for': amendment.votes_for,
                'votes_against': amendment.votes_against,
                'approval_percentage': approval_percentage
            })
            
            self._record_amendment_on_blockchain(amendment, "approved_locally")
        else:
            amendment.status = AmendmentStatus.LOCAL_REJECTED
            self._record_amendment_on_blockchain(amendment, "rejected_locally")
            
        self.save_amendments()

    def escalate_amendment(self, amendment_id: str) -> bool:
        """Escalate amendment to next jurisdiction level"""
        if amendment_id not in self.amendments:
            return False
            
        amendment = self.amendments[amendment_id]
        
        # Check if eligible for escalation
        if (amendment.status != AmendmentStatus.LOCAL_APPROVED or
            not amendment.escalation_eligible_date or
            datetime.now(timezone.utc) < amendment.escalation_eligible_date):
            return False
            
        # Determine next level
        current_level = amendment.jurisdiction_level
        if current_level == JurisdictionLevel.CITY:
            next_level = JurisdictionLevel.STATE
            next_jurisdiction = self._get_parent_jurisdiction(amendment.jurisdiction_name, "state")
        elif current_level == JurisdictionLevel.STATE:
            next_level = JurisdictionLevel.COUNTRY
            next_jurisdiction = self._get_parent_jurisdiction(amendment.jurisdiction_name, "country")
        elif current_level == JurisdictionLevel.COUNTRY:
            next_level = JurisdictionLevel.WORLD
            next_jurisdiction = "World"
        else:
            return False  # Already at world level
            
        # Create new amendment at next level
        new_amendment_id = self.generate_amendment_id()
        new_amendment = AmendmentProposal(
            id=new_amendment_id,
            proposer_email=amendment.proposer_email,
            proposer_name=amendment.proposer_name,
            article_section=amendment.article_section,
            change_type=amendment.change_type,
            current_text=amendment.current_text,
            proposed_text=amendment.proposed_text,
            rationale=amendment.rationale,
            jurisdiction_level=next_level,
            jurisdiction_name=next_jurisdiction,
            status=AmendmentStatus.SUBMITTED,
            created_at=datetime.now(timezone.utc),
            approval_history=amendment.approval_history.copy()
        )
        
        self.amendments[new_amendment_id] = new_amendment
        
        # Update original amendment status
        amendment.status = AmendmentStatus.ESCALATING
        
        self.save_amendments()
        self._record_amendment_on_blockchain(new_amendment, "amendment_escalated")
        
        return True

    def get_amendments_by_jurisdiction(self, jurisdiction_level: JurisdictionLevel, 
                                     jurisdiction_name: str) -> List[AmendmentProposal]:
        """Get all amendments for a specific jurisdiction"""
        return [
            amendment for amendment in self.amendments.values()
            if (amendment.jurisdiction_level == jurisdiction_level and 
                amendment.jurisdiction_name == jurisdiction_name)
        ]

    def get_amendments_by_status(self, status: AmendmentStatus) -> List[AmendmentProposal]:
        """Get all amendments with a specific status"""
        return [
            amendment for amendment in self.amendments.values()
            if amendment.status == status
        ]

    def _get_eligible_voters_count(self, jurisdiction_level: JurisdictionLevel, 
                                 jurisdiction_name: str) -> int:
        """Get count of eligible voters in jurisdiction (placeholder)"""
        # This would integrate with the user management system
        # For now, return a placeholder based on jurisdiction level
        if jurisdiction_level == JurisdictionLevel.CITY:
            return 1000  # Placeholder
        elif jurisdiction_level == JurisdictionLevel.STATE:
            return 50000  # Placeholder
        elif jurisdiction_level == JurisdictionLevel.COUNTRY:
            return 100000000  # Placeholder
        else:  # WORLD
            return 1000000000  # Placeholder

    def _is_voter_eligible(self, voter_email: str, jurisdiction_level: JurisdictionLevel, 
                          jurisdiction_name: str) -> bool:
        """Check if voter is eligible in jurisdiction (placeholder)"""
        # This would integrate with the user management system
        # For now, return True as placeholder
        return True

    def _get_parent_jurisdiction(self, current_jurisdiction: str, level: str) -> str:
        """Get parent jurisdiction name (placeholder)"""
        # This would use real geographic/political data
        # For now, return placeholder names
        if level == "state":
            return "Example State"
        elif level == "country":
            return "Example Country"
        return current_jurisdiction

    def _record_amendment_on_blockchain(self, amendment: AmendmentProposal, action: str):
        """Record amendment action on blockchain for transparency"""
        try:
            from civic_desktop.blockchain.blockchain import Blockchain
            from datetime import datetime, timezone
            
            blockchain_data = {
                'action': f'contract_{action}',
                'amendment_id': amendment.id,
                'article_section': amendment.article_section,
                'change_type': amendment.change_type.value,
                'jurisdiction_level': amendment.jurisdiction_level.value,
                'jurisdiction_name': amendment.jurisdiction_name,
                'proposer_email': amendment.proposer_email,
                'status': amendment.status.value,
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'description': f'Contract amendment {action}: {amendment.article_section} in {amendment.jurisdiction_name}'
            }
            
            success = Blockchain.add_page(
                data=blockchain_data,
                validator=amendment.proposer_email
            )
            
            if success:
                print(f"✅ Amendment {action} recorded on blockchain: {amendment.id}")
            else:
                print(f"⚠️ Failed to record amendment {action} on blockchain: {amendment.id}")
                
        except Exception as e:
            print(f"⚠️ Blockchain recording failed for amendment {action}: {str(e)}")