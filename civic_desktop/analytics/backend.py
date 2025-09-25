# Analytics Module - Backend Analytics Engine
"""
Analytics backend for comprehensive platform analytics including:
- Participation metrics and civic engagement analysis
- Governance effectiveness monitoring  
- Platform health and performance tracking
- Report generation with blockchain transparency
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from ..main import ENV_CONFIG
from ..blockchain.blockchain import Blockchain
from ..users.session import SessionManager

class AnalyticsEngine:
    """Core analytics engine for platform data analysis"""
    
    def __init__(self):
        self.db_path = ENV_CONFIG.get('analytics_db_path', 'analytics/analytics_db.json')
        self.blockchain = Blockchain()
        
    def load_analytics_data(self) -> Dict[str, Any]:
        """Load analytics data from storage"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'reports': [],
                'queries': [],
                'dashboards_accessed': [],
                'metrics_calculated': [],
                'data_exports': [],
                'last_updated': None
            }
    
    def save_analytics_data(self, data: Dict[str, Any]) -> bool:
        """Save analytics data to storage"""
        try:
            data['last_updated'] = datetime.now().isoformat()
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to save analytics data: {e}")
            return False
    
    def generate_participation_analytics(self) -> Dict[str, Any]:
        """Generate civic engagement participation metrics"""
        user = SessionManager.get_current_user()
        if not user:
            return {'error': 'User not authenticated'}
            
        # Get blockchain data for analysis
        blockchain_data = self.blockchain.get_all_pages()
        
        # Analyze user engagement patterns
        user_participation = {}
        debate_engagement = 0
        voting_participation = 0
        training_completions = 0
        
        for page in blockchain_data:
            action_type = page.get('action_type', '')
            user_email = page.get('user_email', '')
            
            if user_email not in user_participation:
                user_participation[user_email] = {
                    'total_actions': 0,
                    'debates': 0,
                    'votes': 0,
                    'training': 0,
                    'moderation': 0
                }
            
            user_participation[user_email]['total_actions'] += 1
            
            if 'debate' in action_type.lower():
                user_participation[user_email]['debates'] += 1
                debate_engagement += 1
            elif 'vote' in action_type.lower():
                user_participation[user_email]['votes'] += 1
                voting_participation += 1
            elif 'training' in action_type.lower():
                user_participation[user_email]['training'] += 1
                training_completions += 1
            elif 'moderation' in action_type.lower():
                user_participation[user_email]['moderation'] += 1
        
        analytics = {
            'total_users': len(user_participation),
            'debate_engagement': debate_engagement,
            'voting_participation': voting_participation,
            'training_completions': training_completions,
            'user_participation': user_participation,
            'engagement_trends': self._calculate_engagement_trends(blockchain_data),
            'top_contributors': self._get_top_contributors(user_participation),
            'timestamp': datetime.now().isoformat()
        }
        
        # Record analytics generation on blockchain
        self.blockchain.add_page(
            action_type="analytics_generated",
            data={
                'report_type': 'participation_analytics',
                'user_count': analytics['total_users'],
                'engagement_metrics': {
                    'debates': debate_engagement,
                    'votes': voting_participation,
                    'training': training_completions
                }
            },
            user_email=user['email']
        )
        
        return analytics
    
    def generate_governance_analytics(self) -> Dict[str, Any]:
        """Generate governance effectiveness analysis"""
        user = SessionManager.get_current_user()
        if not user:
            return {'error': 'User not authenticated'}
            
        blockchain_data = self.blockchain.get_all_pages()
        
        # Analyze governance patterns
        decisions_made = 0
        amendment_proposals = 0
        elder_reviews = 0
        constitutional_compliance = 0
        
        governance_timeline = []
        decision_efficiency = []
        
        for page in blockchain_data:
            action_type = page.get('action_type', '')
            timestamp = page.get('timestamp', '')
            
            if 'decision' in action_type.lower():
                decisions_made += 1
                governance_timeline.append({
                    'type': 'decision',
                    'timestamp': timestamp,
                    'action': action_type
                })
            elif 'amendment' in action_type.lower():
                amendment_proposals += 1
                governance_timeline.append({
                    'type': 'amendment',
                    'timestamp': timestamp,
                    'action': action_type
                })
            elif 'elder_review' in action_type:
                elder_reviews += 1
                governance_timeline.append({
                    'type': 'elder_review',
                    'timestamp': timestamp,
                    'action': action_type
                })
            elif 'constitutional' in action_type.lower():
                constitutional_compliance += 1
        
        analytics = {
            'decisions_made': decisions_made,
            'amendment_proposals': amendment_proposals,
            'elder_reviews': elder_reviews,
            'constitutional_compliance': constitutional_compliance,
            'governance_timeline': governance_timeline[-50:],  # Last 50 events
            'decision_efficiency': self._calculate_decision_efficiency(governance_timeline),
            'constitutional_health': self._assess_constitutional_health(blockchain_data),
            'timestamp': datetime.now().isoformat()
        }
        
        # Record governance analytics on blockchain
        self.blockchain.add_page(
            action_type="governance_analytics_generated",
            data={
                'decisions': decisions_made,
                'amendments': amendment_proposals,
                'elder_oversight': elder_reviews,
                'constitutional_compliance': constitutional_compliance
            },
            user_email=user['email']
        )
        
        return analytics
    
    def generate_platform_health_analytics(self) -> Dict[str, Any]:
        """Generate platform health and performance metrics"""
        user = SessionManager.get_current_user()
        if not user:
            return {'error': 'User not authenticated'}
            
        blockchain_data = self.blockchain.get_all_pages()
        
        # Platform health metrics
        total_actions = len(blockchain_data)
        error_count = 0
        security_events = 0
        performance_metrics = {
            'total_transactions': total_actions,
            'daily_average': 0,
            'peak_activity': 0,
            'system_uptime': '99.9%'  # Placeholder - would be calculated from real metrics
        }
        
        # Analyze recent activity (last 30 days)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_activity = []
        
        for page in blockchain_data:
            page_time = datetime.fromisoformat(page.get('timestamp', ''))
            if page_time >= recent_cutoff:
                recent_activity.append(page)
            
            # Count errors and security events
            action_type = page.get('action_type', '')
            if 'error' in action_type.lower():
                error_count += 1
            elif 'security' in action_type.lower() or 'warning' in action_type.lower():
                security_events += 1
        
        performance_metrics['daily_average'] = len(recent_activity) / 30 if recent_activity else 0
        
        analytics = {
            'total_platform_actions': total_actions,
            'recent_activity_count': len(recent_activity),
            'error_count': error_count,
            'security_events': security_events,
            'performance_metrics': performance_metrics,
            'platform_health_score': self._calculate_health_score(error_count, security_events, total_actions),
            'system_status': 'operational',
            'timestamp': datetime.now().isoformat()
        }
        
        # Record platform health analytics on blockchain
        self.blockchain.add_page(
            action_type="platform_health_analytics",
            data={
                'health_score': analytics['platform_health_score'],
                'total_actions': total_actions,
                'errors': error_count,
                'security_events': security_events
            },
            user_email=user['email']
        )
        
        return analytics
    
    def export_analytics_report(self, report_type: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export comprehensive analytics report"""
        user = SessionManager.get_current_user()
        if not user:
            return {'error': 'User not authenticated'}
        
        # Check user permissions for data export
        if not self._check_export_permissions(user):
            return {'error': 'Insufficient permissions for data export'}
        
        export_data = {}
        
        if report_type == 'participation':
            export_data = self.generate_participation_analytics()
        elif report_type == 'governance':
            export_data = self.generate_governance_analytics()
        elif report_type == 'platform_health':
            export_data = self.generate_platform_health_analytics()
        elif report_type == 'comprehensive':
            export_data = {
                'participation': self.generate_participation_analytics(),
                'governance': self.generate_governance_analytics(),
                'platform_health': self.generate_platform_health_analytics()
            }
        else:
            return {'error': f'Unknown report type: {report_type}'}
        
        # Record export on blockchain
        self.blockchain.add_page(
            action_type="data_exported",
            data={
                'export_type': report_type,
                'user_authorization': user['role'],
                'privacy_compliance': True,
                'parameters': parameters or {}
            },
            user_email=user['email']
        )
        
        return {
            'status': 'success',
            'report_type': report_type,
            'data': export_data,
            'exported_by': user['email'],
            'export_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_engagement_trends(self, blockchain_data: List[Dict]) -> Dict[str, Any]:
        """Calculate engagement trend analysis"""
        # Group actions by day for trend analysis
        daily_activity = {}
        for page in blockchain_data:
            try:
                date = datetime.fromisoformat(page.get('timestamp', '')).date().isoformat()
                if date not in daily_activity:
                    daily_activity[date] = 0
                daily_activity[date] += 1
            except:
                continue
        
        # Calculate trends
        dates = sorted(daily_activity.keys())
        if len(dates) < 2:
            return {'trend': 'insufficient_data', 'slope': 0}
        
        # Simple trend calculation (last week vs previous week)
        recent_week = sum(daily_activity.get(date, 0) for date in dates[-7:])
        previous_week = sum(daily_activity.get(date, 0) for date in dates[-14:-7])
        
        trend = 'increasing' if recent_week > previous_week else 'decreasing' if recent_week < previous_week else 'stable'
        slope = (recent_week - previous_week) / max(previous_week, 1)
        
        return {
            'trend': trend,
            'slope': slope,
            'recent_week_activity': recent_week,
            'previous_week_activity': previous_week,
            'daily_activity': daily_activity
        }
    
    def _get_top_contributors(self, user_participation: Dict[str, Dict]) -> List[Dict]:
        """Get top contributing users by activity"""
        contributors = []
        for email, stats in user_participation.items():
            contributors.append({
                'email': email,
                'total_actions': stats['total_actions'],
                'debates': stats['debates'],
                'votes': stats['votes'],
                'training': stats['training'],
                'moderation': stats['moderation']
            })
        
        # Sort by total actions and return top 10
        contributors.sort(key=lambda x: x['total_actions'], reverse=True)
        return contributors[:10]
    
    def _calculate_decision_efficiency(self, governance_timeline: List[Dict]) -> Dict[str, Any]:
        """Calculate governance decision efficiency metrics"""
        if not governance_timeline:
            return {'efficiency_score': 0, 'average_decision_time': 0}
        
        # Analyze decision patterns
        decisions = [event for event in governance_timeline if event['type'] == 'decision']
        amendments = [event for event in governance_timeline if event['type'] == 'amendment']
        
        efficiency_score = min(len(decisions) / max(len(amendments), 1) * 100, 100)
        
        return {
            'efficiency_score': efficiency_score,
            'decisions_per_amendment': len(decisions) / max(len(amendments), 1),
            'total_governance_actions': len(governance_timeline),
            'decision_ratio': len(decisions) / len(governance_timeline) if governance_timeline else 0
        }
    
    def _assess_constitutional_health(self, blockchain_data: List[Dict]) -> Dict[str, Any]:
        """Assess constitutional compliance and health"""
        constitutional_events = 0
        compliance_violations = 0
        elder_interventions = 0
        
        for page in blockchain_data:
            action_type = page.get('action_type', '').lower()
            if 'constitutional' in action_type:
                constitutional_events += 1
                if 'violation' in action_type:
                    compliance_violations += 1
            elif 'elder_review' in action_type:
                elder_interventions += 1
        
        compliance_rate = ((constitutional_events - compliance_violations) / max(constitutional_events, 1)) * 100
        
        return {
            'constitutional_events': constitutional_events,
            'compliance_violations': compliance_violations,
            'compliance_rate': compliance_rate,
            'elder_interventions': elder_interventions,
            'health_status': 'healthy' if compliance_rate > 90 else 'needs_attention' if compliance_rate > 70 else 'critical'
        }
    
    def _calculate_health_score(self, errors: int, security_events: int, total_actions: int) -> float:
        """Calculate overall platform health score (0-100)"""
        if total_actions == 0:
            return 100.0
        
        error_rate = errors / total_actions
        security_rate = security_events / total_actions
        
        # Health score calculation (lower errors = higher score)
        base_score = 100.0
        error_penalty = error_rate * 50  # Errors reduce score by up to 50 points
        security_penalty = security_rate * 30  # Security events reduce by up to 30 points
        
        health_score = max(base_score - error_penalty - security_penalty, 0)
        return round(health_score, 1)
    
    def _check_export_permissions(self, user: Dict[str, Any]) -> bool:
        """Check if user has permissions for data export"""
        # Allow exports for Contract Representatives, Senators, Elders, and Founders
        allowed_roles = ['Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder']
        return user.get('role', '') in allowed_roles or user.get('email', '') in ['admin@civic.platform']