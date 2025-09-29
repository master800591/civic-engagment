# Moderation Module - Backend Logic
import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from ..blockchain.blockchain import Blockchain
from ..blockchain.integration_manager import BlockchainIntegrationManager, record_moderation_action
from ..users.backend import UserBackend


def get_moderation_db_path() -> str:
    try:
        from civic_desktop.main import ENV_CONFIG
        return ENV_CONFIG.get('moderation_db_path', os.path.join(os.path.dirname(__file__), 'moderation_db.json'))
    except ImportError:
        # ENV_CONFIG not available, use default path
        return os.path.join(os.path.dirname(__file__), 'moderation_db.json')


class ModerationAction:
    """Constants for moderation actions"""
    FLAG_CONTENT = "flag_content"
    APPROVE_TOPIC = "approve_topic"
    REJECT_TOPIC = "reject_topic"
    WARN_USER = "warn_user"
    SUSPEND_USER = "suspend_user"
    DELETE_CONTENT = "delete_content"


class ModerationSeverity:
    """Constants for moderation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ModerationBackend:
    """Backend logic for content moderation and platform governance"""

    @staticmethod
    def _build_logs_from_chain() -> List[Dict[str, Any]]:
        chain = Blockchain.load_chain()
        logs: List[Dict[str, Any]] = []
        for page in chain.get('pages', []):
            data = page.get('data', {})
            action = data.get('action')
            if action in {ModerationAction.FLAG_CONTENT, 'review_flag', 'warn_user'}:
                logs.append(data)
        return logs

    @staticmethod
    def load_moderation_logs() -> List[Dict[str, Any]]:
        """Load moderation action logs from blockchain"""
        return ModerationBackend._build_logs_from_chain()

    @staticmethod
    def save_moderation_logs(logs: List[Dict[str, Any]]) -> None:
        """Deprecated: logs are stored on-chain. This is a no-op."""
        return None
    
    @staticmethod
    def can_moderate(user_email: str, jurisdiction: Optional[str] = None, location: Optional[str] = None) -> bool:
        """Check if user has moderation privileges"""
        users = UserBackend.load_users()
        user = next((u for u in users if u['email'] == user_email), None)
        
        if not user:
            return False
        
        roles = user.get('roles', [])
        
        # Founders and CEOs can moderate anywhere
        if 'founder' in roles or 'ceo' in roles:
            return True
        
        # Check jurisdiction-specific moderation rights
        if jurisdiction and location:
            if jurisdiction == 'city':
                return ('city_rep' in roles or 'city_senator' in roles) and user.get('city', '').lower() == location.lower()
            elif jurisdiction == 'state':
                return ('state_rep' in roles or 'state_senator' in roles) and user.get('state', '').lower() == location.lower()
            elif jurisdiction == 'country':
                return ('country_rep' in roles or 'country_senator' in roles) and user.get('country', '').lower() == location.lower()
        
        # General moderation privileges for any representative role
        return any(role.endswith('_rep') or role.endswith('_senator') for role in roles)
    
    @staticmethod
    def flag_content(content_type: str, content_id: str, reason: str, reporter_email: str, severity: str = ModerationSeverity.LOW) -> Tuple[bool, str]:
        """Flag content for moderation review"""
        if not reason or len(reason.strip()) < 10:
            return False, "Reason must be at least 10 characters"
        
        if severity not in [ModerationSeverity.LOW, ModerationSeverity.MEDIUM, 
                           ModerationSeverity.HIGH, ModerationSeverity.CRITICAL]:
            return False, "Invalid severity level"
        
        logs: List[Dict[str, Any]] = ModerationBackend.load_moderation_logs()

        flag_entry: Dict[str, Any] = {
            'id': str(uuid.uuid4()),
            'action': ModerationAction.FLAG_CONTENT,
            'content_type': content_type,  # 'topic', 'argument', 'user'
            'content_id': content_id,
            'reason': reason.strip(),
            'reporter_email': reporter_email,
            'severity': severity,
            'status': 'pending',  # pending, reviewed, resolved
            'created_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'reviewed_by': None,
            'reviewed_at': None,
            'resolution': None
        }
        # Persist directly to blockchain
        # Log to blockchain
        try:
            Blockchain.add_page(
                data={
                    'action': 'flag_content',
                    'flag_id': flag_entry['id'],
                    'content_type': content_type,
                    'content_id': content_id,
                    'reporter_email': reporter_email,
                    'severity': severity,
                    'timestamp': flag_entry['created_at']
                },
                validator=reporter_email
            )
        except Exception as e:
            print(f"Failed to log flag to blockchain: {e}")
        
        return True, f"Content flagged successfully (ID: {flag_entry['id']})"
    
    @staticmethod
    def review_flag(flag_id: str, moderator_email: str, resolution: str, action_taken: Optional[str] = None) -> Tuple[bool, str]:
        """Review and resolve a content flag"""
        if not ModerationBackend.can_moderate(moderator_email):
            return False, "You don't have moderation privileges"
        logs = ModerationBackend.load_moderation_logs()
        flag = next((log for log in logs if log.get('id') == flag_id), None)

        if not flag:
            return False, "Flag not found"
        
        if flag['status'] != 'pending':
            return False, "Flag has already been reviewed"
        
        if not resolution or len(resolution.strip()) < 10:
            return False, "Resolution explanation must be at least 10 characters"
        
        # Update flag status
        flag['status'] = 'reviewed'
        flag['reviewed_by'] = moderator_email
        flag['reviewed_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        flag['resolution'] = resolution.strip()
        flag['action_taken'] = action_taken
        
        # Persist directly to blockchain
        # Log to blockchain
        try:
            Blockchain.add_page(
                data={
                    'action': 'review_flag',
                    'flag_id': flag_id,
                    'moderator_email': moderator_email,
                    'resolution': resolution.strip(),
                    'action_taken': action_taken,
                    'timestamp': flag['reviewed_at']
                },
                validator=moderator_email
            )
        except Exception as e:
            print(f"Failed to log flag review to blockchain: {e}")
        
        return True, "Flag reviewed and resolved"
    
    @staticmethod
    def get_pending_flags(moderator_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pending flags for review"""
        logs = ModerationBackend.load_moderation_logs()
        pending_flags = [log for log in logs if log.get('action') == ModerationAction.FLAG_CONTENT 
                        and log.get('status') == 'pending']

        # Sort by severity and creation date
        severity_order = {ModerationSeverity.CRITICAL: 0, ModerationSeverity.HIGH: 1, 
                         ModerationSeverity.MEDIUM: 2, ModerationSeverity.LOW: 3}

        pending_flags.sort(key=lambda x: (severity_order.get(x.get('severity', 'low'), 3), x.get('created_at', '')))

        return pending_flags
    
    @staticmethod
    def get_moderation_stats(moderator_email: Optional[str] = None) -> Dict[str, Any]:
        """Get moderation statistics"""
        logs = ModerationBackend.load_moderation_logs()
        
        stats: Dict[str, Any] = {
            'total_flags': len([log for log in logs if log.get('action') == ModerationAction.FLAG_CONTENT]),
            'pending_flags': len([log for log in logs if log.get('action') == ModerationAction.FLAG_CONTENT 
                                 and log.get('status') == 'pending']),
            'reviewed_flags': len([log for log in logs if log.get('action') == ModerationAction.FLAG_CONTENT 
                                  and log.get('status') == 'reviewed']),
            'flags_by_severity': {
                'critical': len([log for log in logs if log.get('severity') == ModerationSeverity.CRITICAL]),
                'high': len([log for log in logs if log.get('severity') == ModerationSeverity.HIGH]),
                'medium': len([log for log in logs if log.get('severity') == ModerationSeverity.MEDIUM]),
                'low': len([log for log in logs if log.get('severity') == ModerationSeverity.LOW])
            }
        }
        
        if moderator_email:
            stats['reviewed_by_moderator'] = len([log for log in logs 
                                                 if log.get('reviewed_by') == moderator_email])
        
        return stats
    
    @staticmethod
    def warn_user(target_email: str, moderator_email: str, reason: str) -> Tuple[bool, str]:
        """Issue a warning to a user"""
        if not ModerationBackend.can_moderate(moderator_email):
            return False, "You don't have moderation privileges"
        
        if not reason or len(reason.strip()) < 10:
            return False, "Warning reason must be at least 10 characters"
        
        logs = ModerationBackend.load_moderation_logs()
        
        warning = {
            'id': str(uuid.uuid4()),
            'action': ModerationAction.WARN_USER,
            'target_email': target_email,
            'moderator_email': moderator_email,
            'reason': reason.strip(),
            'created_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        # Persist directly to blockchain
        # Log to blockchain
        try:
            Blockchain.add_page(
                data={
                    'action': 'warn_user',
                    'warning_id': warning['id'],
                    'target_email': target_email,
                    'moderator_email': moderator_email,
                    'reason': reason.strip(),
                    'timestamp': warning['created_at']
                },
                validator=moderator_email
            )
        except Exception as e:
            print(f"Failed to log warning to blockchain: {e}")
        
        return True, f"Warning issued to {target_email}"
    
    @staticmethod
    def get_user_warnings(user_email: str) -> List[Dict[str, Any]]:
        """Get all warnings for a specific user"""
        logs = ModerationBackend.load_moderation_logs()
        return [log for log in logs if log.get('action') == ModerationAction.WARN_USER 
                and log.get('target_email') == user_email]