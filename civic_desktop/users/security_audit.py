"""
SECURITY AUDIT MODULE - Comprehensive security validation and reporting
Provides audit functions for authentication, founder keys, and user management
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import hashlib

class SecurityAuditor:
    """Comprehensive security audit functions for user management"""
    
    def __init__(self, config_path: str = None):
        """Initialize security auditor"""
        self.config_path = config_path or "config/dev_config.json"
        self.config = self._load_config()
        self.audit_log_path = Path(self.config.get('audit_log_path', 'users/security_audit_log.json'))
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
        return {}
    
    def log_security_event(self, event_type: str, user_email: str, details: Dict[str, Any], 
                          severity: str = "info") -> bool:
        """
        Log security event with comprehensive details
        
        Args:
            event_type: Type of security event (login_attempt, founder_key_usage, etc.)
            user_email: User associated with the event
            details: Additional event details
            severity: Event severity (info, warning, critical)
        
        Returns:
            bool: Success status
        """
        try:
            # Load existing audit log
            audit_log = self._load_audit_log()
            
            # Create event record
            event = {
                'event_id': hashlib.sha256(f"{datetime.now().isoformat()}{user_email}{event_type}".encode()).hexdigest()[:16],
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'user_email': user_email,
                'severity': severity,
                'details': details,
                'recorded_by': 'security_auditor'
            }
            
            # Add to log
            audit_log['events'].append(event)
            audit_log['metadata']['total_events'] = len(audit_log['events'])
            audit_log['metadata']['last_event'] = datetime.now().isoformat()
            
            # Save updated log
            self._save_audit_log(audit_log)
            
            # Also record to blockchain if available
            self._record_to_blockchain(event)
            
            return True
            
        except Exception as e:
            print(f"Error logging security event: {e}")
            return False
    
    def _load_audit_log(self) -> Dict[str, Any]:
        """Load security audit log"""
        if self.audit_log_path.exists():
            try:
                with open(self.audit_log_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Initialize new log
        return {
            'events': [],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'total_events': 0,
                'last_event': None
            }
        }
    
    def _save_audit_log(self, audit_log: Dict[str, Any]):
        """Save security audit log"""
        try:
            with open(self.audit_log_path, 'w', encoding='utf-8') as f:
                json.dump(audit_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving audit log: {e}")
    
    def _record_to_blockchain(self, event: Dict[str, Any]):
        """Record security event to blockchain"""
        try:
            from blockchain.blockchain import add_user_action
            
            blockchain_data = {
                'event_type': event['event_type'],
                'timestamp': event['timestamp'],
                'severity': event['severity'],
                'event_id': event['event_id'],
                'details_hash': hashlib.sha256(json.dumps(event['details'], sort_keys=True).encode()).hexdigest()
            }
            
            add_user_action(
                action_type='security_event',
                user_email=event['user_email'],
                data=blockchain_data
            )
        except Exception as e:
            # Blockchain recording is best-effort, don't fail if unavailable
            pass
    
    def audit_founder_key_usage(self) -> Dict[str, Any]:
        """
        Audit founder key system for security compliance
        
        Returns:
            Dict with audit results
        """
        try:
            # Try multiple import paths for flexibility
            try:
                from users.hardcoded_founder_keys import HardcodedFounderKeys
            except ImportError:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent))
                from hardcoded_founder_keys import HardcodedFounderKeys
            
            # Get key status
            key_status = HardcodedFounderKeys.get_key_status()
            
            # Check for anomalies
            issues = []
            warnings = []
            
            # Verify single-use enforcement
            used_keys = key_status.get('used_key_details', {})
            for key_hash, usage_info in used_keys.items():
                # Verify key is marked as used in system
                if not HardcodedFounderKeys.is_key_available(key_hash):
                    continue  # This is expected - key should not be available
                else:
                    issues.append(f"Key {usage_info.get('founder_id')} marked as used but still available")
            
            # Check usage timestamps
            for key_hash, usage_info in used_keys.items():
                try:
                    used_at = datetime.fromisoformat(usage_info['used_at'])
                    if used_at > datetime.now():
                        issues.append(f"Invalid timestamp for {usage_info.get('founder_id')}")
                except Exception:
                    issues.append(f"Invalid timestamp format for {usage_info.get('founder_id')}")
            
            # Calculate usage rate
            total_keys = key_status.get('total_keys', 0)
            used_count = key_status.get('used_keys', 0)
            usage_rate = (used_count / total_keys * 100) if total_keys > 0 else 0
            
            if usage_rate > 80:
                warnings.append(f"High founder key usage rate: {usage_rate:.1f}%")
            
            return {
                'status': 'passed' if not issues else 'failed',
                'timestamp': datetime.now().isoformat(),
                'key_status': key_status,
                'usage_rate': usage_rate,
                'issues': issues,
                'warnings': warnings,
                'details': {
                    'total_keys': total_keys,
                    'used_keys': used_count,
                    'available_keys': key_status.get('available_keys', 0),
                    'single_use_enforced': len(issues) == 0
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def audit_authentication_security(self, users_db_path: str = None) -> Dict[str, Any]:
        """
        Audit authentication security measures
        
        Returns:
            Dict with audit results
        """
        try:
            users_db_path = Path(users_db_path or self.config.get('users_db_path', 'users/users_db.json'))
            
            if not users_db_path.exists():
                return {
                    'status': 'error',
                    'error': 'Users database not found',
                    'timestamp': datetime.now().isoformat()
                }
            
            with open(users_db_path, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            users = users_data.get('users', [])
            
            issues = []
            warnings = []
            stats = {
                'total_users': len(users),
                'locked_accounts': 0,
                'recent_login_failures': 0,
                'weak_passwords': 0,  # Would need to check against policy
                'missing_2fa': 0,
                'inactive_accounts': 0
            }
            
            # Analyze each user account
            for user in users:
                # Check for locked accounts
                if user.get('locked_until'):
                    try:
                        locked_until = datetime.fromisoformat(user['locked_until'])
                        if locked_until > datetime.now():
                            stats['locked_accounts'] += 1
                    except Exception:
                        pass
                
                # Check for recent login failures
                if user.get('login_attempts', 0) > 0:
                    stats['recent_login_failures'] += 1
                
                # Check for missing password hash (critical issue)
                if not user.get('password_hash'):
                    issues.append(f"User {user.get('email')} missing password hash")
                
                # Check for inactive accounts (no login in 90+ days)
                if user.get('last_login'):
                    try:
                        last_login = datetime.fromisoformat(user['last_login'])
                        if datetime.now() - last_login > timedelta(days=90):
                            stats['inactive_accounts'] += 1
                    except Exception:
                        pass
                elif user.get('created_at'):
                    # Never logged in - check account age
                    try:
                        created_at = datetime.fromisoformat(user['created_at'])
                        if datetime.now() - created_at > timedelta(days=30):
                            warnings.append(f"User {user.get('email')} never logged in (created {created_at.date()})")
                    except Exception:
                        pass
            
            # Determine overall status
            status = 'passed'
            if issues:
                status = 'failed'
            elif warnings:
                status = 'passed_with_warnings'
            
            return {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'statistics': stats,
                'issues': issues,
                'warnings': warnings,
                'recommendations': self._generate_auth_recommendations(stats, issues, warnings)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_auth_recommendations(self, stats: Dict, issues: List, warnings: List) -> List[str]:
        """Generate security recommendations based on audit results"""
        recommendations = []
        
        if stats['locked_accounts'] > 0:
            recommendations.append(f"Review {stats['locked_accounts']} locked accounts for potential security incidents")
        
        if stats['recent_login_failures'] > 0:
            recommendations.append(f"Investigate {stats['recent_login_failures']} accounts with recent failed login attempts")
        
        if stats['inactive_accounts'] > 5:
            recommendations.append(f"Consider archiving {stats['inactive_accounts']} inactive accounts")
        
        if len(issues) > 0:
            recommendations.append("Address critical security issues immediately")
        
        return recommendations
    
    def audit_session_security(self, sessions_db_path: str = None) -> Dict[str, Any]:
        """
        Audit session management security
        
        Returns:
            Dict with audit results
        """
        try:
            sessions_db_path = Path(sessions_db_path or self.config.get('sessions_db_path', 'users/sessions_db.json'))
            
            if not sessions_db_path.exists():
                return {
                    'status': 'no_sessions',
                    'message': 'No active sessions found',
                    'timestamp': datetime.now().isoformat()
                }
            
            with open(sessions_db_path, 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
            
            active_sessions = sessions_data.get('active_sessions', {})
            
            issues = []
            warnings = []
            stats = {
                'total_sessions': len(active_sessions),
                'expired_sessions': 0,
                'long_running_sessions': 0,
                'suspicious_sessions': 0
            }
            
            # Analyze sessions
            for session_id, session in active_sessions.items():
                # Check for expired sessions
                try:
                    expires_at = datetime.fromisoformat(session['expires_at'])
                    if expires_at < datetime.now():
                        stats['expired_sessions'] += 1
                        issues.append(f"Expired session not cleaned up: {session_id[:16]}")
                except Exception:
                    issues.append(f"Invalid expiration timestamp: {session_id[:16]}")
                
                # Check for long-running sessions (>7 days)
                try:
                    created_at = datetime.fromisoformat(session['created_at'])
                    age = datetime.now() - created_at
                    if age > timedelta(days=7):
                        stats['long_running_sessions'] += 1
                        warnings.append(f"Long-running session detected: {age.days} days")
                except Exception:
                    pass
            
            status = 'passed'
            if issues:
                status = 'failed'
            elif warnings:
                status = 'passed_with_warnings'
            
            return {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'statistics': stats,
                'issues': issues,
                'warnings': warnings,
                'recommendations': [
                    "Implement automatic session cleanup for expired sessions",
                    "Consider implementing session rotation for long-running sessions",
                    "Monitor for suspicious session patterns"
                ] if issues or warnings else []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive security audit report
        
        Returns:
            Dict with complete audit results
        """
        report = {
            'report_id': hashlib.sha256(datetime.now().isoformat().encode()).hexdigest()[:16],
            'timestamp': datetime.now().isoformat(),
            'audits': {}
        }
        
        # Run all audits
        report['audits']['founder_keys'] = self.audit_founder_key_usage()
        report['audits']['authentication'] = self.audit_authentication_security()
        report['audits']['sessions'] = self.audit_session_security()
        
        # Determine overall status
        all_passed = all(
            audit.get('status') in ['passed', 'passed_with_warnings', 'no_sessions']
            for audit in report['audits'].values()
        )
        
        report['overall_status'] = 'passed' if all_passed else 'failed'
        
        # Collect all issues and warnings
        all_issues = []
        all_warnings = []
        
        for audit_name, audit_results in report['audits'].items():
            if audit_results.get('issues'):
                all_issues.extend([f"[{audit_name}] {issue}" for issue in audit_results['issues']])
            if audit_results.get('warnings'):
                all_warnings.extend([f"[{audit_name}] {warning}" for warning in audit_results['warnings']])
        
        report['summary'] = {
            'total_issues': len(all_issues),
            'total_warnings': len(all_warnings),
            'issues': all_issues,
            'warnings': all_warnings
        }
        
        return report
    
    def get_recent_security_events(self, hours: int = 24, severity: str = None) -> List[Dict[str, Any]]:
        """
        Get recent security events from audit log
        
        Args:
            hours: Number of hours to look back
            severity: Filter by severity (info, warning, critical)
        
        Returns:
            List of security events
        """
        try:
            audit_log = self._load_audit_log()
            events = audit_log.get('events', [])
            
            # Filter by time
            cutoff = datetime.now() - timedelta(hours=hours)
            recent_events = [
                event for event in events
                if datetime.fromisoformat(event['timestamp']) > cutoff
            ]
            
            # Filter by severity if specified
            if severity:
                recent_events = [
                    event for event in recent_events
                    if event.get('severity') == severity
                ]
            
            return sorted(recent_events, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            print(f"Error retrieving security events: {e}")
            return []


# Convenience function for quick audits
def run_security_audit(output_file: str = None) -> Dict[str, Any]:
    """
    Run comprehensive security audit and optionally save to file
    
    Args:
        output_file: Optional path to save report
    
    Returns:
        Audit report dictionary
    """
    auditor = SecurityAuditor()
    report = auditor.generate_comprehensive_report()
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ Security audit report saved to: {output_file}")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
    
    return report


if __name__ == "__main__":
    # Run audit when executed directly
    print("🔒 Running Security Audit...")
    print("=" * 60)
    
    report = run_security_audit("users/security_audit_report.json")
    
    print(f"\n📊 Overall Status: {report['overall_status'].upper()}")
    print(f"⏰ Report Time: {report['timestamp']}")
    
    if report['summary']['total_issues'] > 0:
        print(f"\n❌ Critical Issues: {report['summary']['total_issues']}")
        for issue in report['summary']['issues']:
            print(f"   • {issue}")
    
    if report['summary']['total_warnings'] > 0:
        print(f"\n⚠️ Warnings: {report['summary']['total_warnings']}")
        for warning in report['summary']['warnings'][:5]:  # Show first 5
            print(f"   • {warning}")
        if len(report['summary']['warnings']) > 5:
            print(f"   ... and {len(report['summary']['warnings']) - 5} more")
    
    if report['overall_status'] == 'passed' and report['summary']['total_warnings'] == 0:
        print("\n✅ All security checks passed!")
    
    print("\n" + "=" * 60)
