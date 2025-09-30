#!/usr/bin/env python3
"""
PLATFORM REGISTRATION AND ONBOARDING MONITOR
Tracks registration, founder key usage, and onboarding completion
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


class RegistrationMonitor:
    """Monitor platform registration and onboarding activities"""
    
    def __init__(self):
        self.users_db_path = Path('users/users_db.json')
        self.blockchain_db_path = Path('blockchain/blockchain_db.json')
        self.founder_keys_path = Path('users/founder_keys/hardcoded_keys_usage.json')
        
    def load_users_data(self) -> Dict:
        """Load users database"""
        try:
            if self.users_db_path.exists():
                with open(self.users_db_path, 'r') as f:
                    return json.load(f)
            return {'users': [], 'metadata': {}}
        except Exception as e:
            print(f"Error loading users data: {e}")
            return {'users': [], 'metadata': {}}
    
    def load_blockchain_data(self) -> Dict:
        """Load blockchain database"""
        try:
            if self.blockchain_db_path.exists():
                with open(self.blockchain_db_path, 'r') as f:
                    return json.load(f)
            return {'pages': [], 'chapters': []}
        except Exception as e:
            print(f"Error loading blockchain data: {e}")
            return {'pages': [], 'chapters': []}
    
    def load_founder_key_usage(self) -> Dict:
        """Load founder key usage tracking"""
        try:
            if self.founder_keys_path.exists():
                with open(self.founder_keys_path, 'r') as f:
                    return json.load(f)
            return {'keys_used': [], 'last_updated': None}
        except Exception as e:
            print(f"Error loading founder key usage: {e}")
            return {'keys_used': [], 'last_updated': None}
    
    def get_recent_registrations(self, hours: int = 24) -> List[Dict]:
        """Get registrations from the last N hours"""
        users_data = self.load_users_data()
        now = datetime.now()
        threshold = now - timedelta(hours=hours)
        
        recent_users = []
        for user in users_data.get('users', []):
            try:
                created_at = datetime.fromisoformat(user.get('created_at', ''))
                if created_at > threshold:
                    recent_users.append(user)
            except (ValueError, TypeError):
                continue
        
        return recent_users
    
    def analyze_founder_key_usage(self) -> Dict:
        """Analyze founder key usage patterns"""
        users_data = self.load_users_data()
        founder_usage = self.load_founder_key_usage()
        
        founders = [u for u in users_data.get('users', []) if u.get('role') == 'contract_founder']
        
        analysis = {
            'total_founders': len(founders),
            'keys_used': len(founder_usage.get('keys_used', [])),
            'keys_available': 10 - len(founder_usage.get('keys_used', [])),
            'recent_founder_registrations': []
        }
        
        # Get recent founder registrations (last 7 days)
        now = datetime.now()
        threshold = now - timedelta(days=7)
        
        for founder in founders:
            try:
                created_at = datetime.fromisoformat(founder.get('created_at', ''))
                if created_at > threshold:
                    analysis['recent_founder_registrations'].append({
                        'name': f"{founder.get('first_name', '')} {founder.get('last_name', '')}",
                        'email': founder.get('email', ''),
                        'registered': founder.get('created_at', ''),
                        'founder_info': founder.get('metadata', {}).get('founder_info', {})
                    })
            except (ValueError, TypeError):
                continue
        
        return analysis
    
    def analyze_onboarding_status(self) -> Dict:
        """Analyze onboarding completion status"""
        users_data = self.load_users_data()
        
        total_users = len(users_data.get('users', []))
        if total_users == 0:
            return {
                'total_users': 0,
                'onboarding_complete': 0,
                'onboarding_incomplete': 0,
                'completion_rate': 0.0,
                'incomplete_users': []
            }
        
        complete_count = 0
        incomplete_users = []
        
        for user in users_data.get('users', []):
            onboarding_complete = user.get('onboarding_complete', False)
            
            if onboarding_complete:
                complete_count += 1
            else:
                # Check if user is recently registered (within 7 days)
                try:
                    created_at = datetime.fromisoformat(user.get('created_at', ''))
                    days_since_registration = (datetime.now() - created_at).days
                    
                    if days_since_registration > 7:
                        incomplete_users.append({
                            'name': f"{user.get('first_name', '')} {user.get('last_name', '')}",
                            'email': user.get('email', ''),
                            'registered': user.get('created_at', ''),
                            'days_since': days_since_registration
                        })
                except (ValueError, TypeError):
                    continue
        
        return {
            'total_users': total_users,
            'onboarding_complete': complete_count,
            'onboarding_incomplete': total_users - complete_count,
            'completion_rate': (complete_count / total_users) * 100,
            'incomplete_users': incomplete_users
        }
    
    def analyze_role_distribution(self) -> Dict:
        """Analyze user role distribution"""
        users_data = self.load_users_data()
        
        role_counts = defaultdict(int)
        for user in users_data.get('users', []):
            role = user.get('role', 'unknown')
            role_counts[role] += 1
        
        return dict(role_counts)
    
    def check_security_alerts(self) -> List[Dict]:
        """Check for security-related alerts"""
        alerts = []
        
        # Check for multiple failed login attempts (from blockchain)
        blockchain_data = self.load_blockchain_data()
        now = datetime.now()
        threshold = now - timedelta(hours=1)
        
        failed_attempts = defaultdict(int)
        for page in blockchain_data.get('pages', []):
            try:
                timestamp = datetime.fromisoformat(page.get('timestamp', ''))
                if timestamp > threshold and page.get('action_type') == 'failed_login':
                    user_email = page.get('data', {}).get('email', 'unknown')
                    failed_attempts[user_email] += 1
            except (ValueError, TypeError):
                continue
        
        for email, count in failed_attempts.items():
            if count >= 5:
                alerts.append({
                    'type': 'multiple_failed_logins',
                    'severity': 'high',
                    'email': email,
                    'count': count,
                    'message': f"Multiple failed login attempts detected for {email}"
                })
        
        # Check for rapid founder key usage
        founder_usage = self.load_founder_key_usage()
        keys_used_today = 0
        for key_usage in founder_usage.get('keys_used', []):
            try:
                used_at = datetime.fromisoformat(key_usage.get('used_at', ''))
                if (now - used_at).days == 0:
                    keys_used_today += 1
            except (ValueError, TypeError):
                continue
        
        if keys_used_today >= 3:
            alerts.append({
                'type': 'rapid_founder_key_usage',
                'severity': 'medium',
                'count': keys_used_today,
                'message': f"{keys_used_today} founder keys used today - verify legitimacy"
            })
        
        return alerts
    
    def generate_report(self, hours: int = 24) -> str:
        """Generate comprehensive monitoring report"""
        report_lines = []
        
        report_lines.append("=" * 80)
        report_lines.append("📊 CIVIC ENGAGEMENT PLATFORM - REGISTRATION MONITORING REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Monitoring Period: Last {hours} hours")
        report_lines.append("")
        
        # Recent registrations
        recent_users = self.get_recent_registrations(hours)
        report_lines.append(f"📝 RECENT REGISTRATIONS ({hours}h)")
        report_lines.append("-" * 80)
        report_lines.append(f"Total New Users: {len(recent_users)}")
        
        if recent_users:
            report_lines.append("\nNew Users:")
            for user in recent_users:
                report_lines.append(f"  • {user.get('first_name', '')} {user.get('last_name', '')}")
                report_lines.append(f"    Email: {user.get('email', '')}")
                report_lines.append(f"    Role: {user.get('role', 'unknown')}")
                report_lines.append(f"    Location: {user.get('city', '')}, {user.get('state', '')}")
                report_lines.append(f"    Registered: {user.get('created_at', '')}")
                report_lines.append("")
        else:
            report_lines.append("  No new registrations in this period")
        
        report_lines.append("")
        
        # Founder key usage
        founder_analysis = self.analyze_founder_key_usage()
        report_lines.append("🔑 FOUNDER KEY USAGE")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Founders: {founder_analysis['total_founders']}")
        report_lines.append(f"Keys Used: {founder_analysis['keys_used']}/10")
        report_lines.append(f"Keys Available: {founder_analysis['keys_available']}/10")
        
        if founder_analysis['recent_founder_registrations']:
            report_lines.append("\nRecent Founder Registrations (7 days):")
            for founder in founder_analysis['recent_founder_registrations']:
                report_lines.append(f"  • {founder['name']} ({founder['email']})")
                report_lines.append(f"    Registered: {founder['registered']}")
                if founder.get('founder_info'):
                    report_lines.append(f"    Key ID: {founder['founder_info'].get('founder_id', 'N/A')}")
                report_lines.append("")
        else:
            report_lines.append("  No recent founder registrations")
        
        report_lines.append("")
        
        # Onboarding status
        onboarding = self.analyze_onboarding_status()
        report_lines.append("✅ ONBOARDING STATUS")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Users: {onboarding['total_users']}")
        report_lines.append(f"Onboarding Complete: {onboarding['onboarding_complete']}")
        report_lines.append(f"Onboarding Incomplete: {onboarding['onboarding_incomplete']}")
        report_lines.append(f"Completion Rate: {onboarding['completion_rate']:.1f}%")
        
        if onboarding['incomplete_users']:
            report_lines.append(f"\n⚠️ Users with Incomplete Onboarding (>7 days):")
            for user in onboarding['incomplete_users'][:10]:  # Show up to 10
                report_lines.append(f"  • {user['name']} ({user['email']})")
                report_lines.append(f"    Days Since Registration: {user['days_since']}")
                report_lines.append("")
        
        report_lines.append("")
        
        # Role distribution
        role_dist = self.analyze_role_distribution()
        report_lines.append("👥 USER ROLE DISTRIBUTION")
        report_lines.append("-" * 80)
        for role, count in sorted(role_dist.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"  {role}: {count}")
        
        report_lines.append("")
        
        # Security alerts
        alerts = self.check_security_alerts()
        report_lines.append("🚨 SECURITY ALERTS")
        report_lines.append("-" * 80)
        
        if alerts:
            for alert in alerts:
                severity_icon = "🔴" if alert['severity'] == 'high' else "🟡"
                report_lines.append(f"{severity_icon} {alert['type'].upper()}")
                report_lines.append(f"  {alert['message']}")
                report_lines.append("")
        else:
            report_lines.append("  ✅ No security alerts")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("Report Complete")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def export_report(self, filename: str, hours: int = 24):
        """Export report to file"""
        report = self.generate_report(hours)
        
        output_path = Path('logs') / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"📄 Report exported to: {output_path}")
        return output_path


def main():
    """Main entry point for monitoring script"""
    parser = argparse.ArgumentParser(
        description='Monitor platform registration and onboarding'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours to look back for recent activity (default: 24)'
    )
    parser.add_argument(
        '--export',
        type=str,
        help='Export report to file (provide filename)'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuously (for daemon mode)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=3600,
        help='Interval in seconds for continuous mode (default: 3600)'
    )
    
    args = parser.parse_args()
    
    monitor = RegistrationMonitor()
    
    if args.continuous:
        import time
        print(f"🔄 Running in continuous mode (interval: {args.interval}s)")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                report = monitor.generate_report(args.hours)
                print(report)
                
                if args.export:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{args.export}_{timestamp}.txt"
                    monitor.export_report(filename, args.hours)
                
                print(f"\n⏰ Next check in {args.interval} seconds...\n")
                time.sleep(args.interval)
                
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped")
                break
    else:
        # Single run
        report = monitor.generate_report(args.hours)
        print(report)
        
        if args.export:
            monitor.export_report(args.export, args.hours)


if __name__ == "__main__":
    main()
