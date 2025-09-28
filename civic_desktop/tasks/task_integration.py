# Task Integration System - Cross-Module Integration and Automation
# Integrates task management with blockchain validation, elections, contracts, and other modules

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.task_manager import TaskManager, ValidationTaskHandler, VotingTaskHandler, ContractTaskHandler
from tasks.task_types import TaskType, TaskPriority, ValidationLevel

class TaskIntegrationManager:
    """Manages integration between task system and other platform modules"""
    
    def __init__(self):
        self.task_manager = TaskManager()
        self.integration_config = self._load_integration_config()
    
    def _load_integration_config(self) -> Dict[str, Any]:
        """Load integration configuration settings"""
        
        default_config = {
            'auto_task_creation': True,
            'notification_enabled': True,
            'blockchain_recording': True,
            'validation_thresholds': {
                'city': 0.33,
                'state': 0.25, 
                'country': 0.20,
                'founder': 0.10
            },
            'task_timeouts': {
                'blockchain_validation': 48,  # hours
                'voting_opportunity': 336,    # hours (14 days)
                'contract_review': 168,       # hours (7 days)
                'jury_duty': 24,              # hours
                'training_completion': 720    # hours (30 days)
            }
        }
        
        try:
            # Try to load from config file
            config_path = Path('tasks/integration_config.json')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    saved_config = json.load(f)
                default_config.update(saved_config)
        except Exception as e:
            print(f"Warning: Could not load integration config: {e}")
        
        return default_config
    
    # Blockchain Validation Integration
    def handle_validation_request(self, validation_request: Dict[str, Any]) -> List[str]:
        """Handle new blockchain validation request by creating tasks"""
        
        if not self.integration_config.get('auto_task_creation', True):
            return []
        
        try:
            # Extract validation details
            request_id = validation_request.get('request_id')
            validation_level = ValidationLevel(validation_request.get('validation_level', 'city'))
            block_data = validation_request.get('block_data', {})
            
            # Get eligible validators based on validation level and geography
            eligible_validators = self._get_eligible_validators(validation_level, validation_request)
            
            if not eligible_validators:
                print(f"Warning: No eligible validators found for request {request_id}")
                return []
            
            # Create validation tasks
            created_tasks = ValidationTaskHandler.create_validation_tasks(
                validation_request_id=request_id,
                eligible_validators=eligible_validators,
                validation_level=validation_level
            )
            
            print(f"Created {len(created_tasks)} validation tasks for request {request_id}")
            return created_tasks
            
        except Exception as e:
            print(f"Error handling validation request: {e}")
            return []
    
    def _get_eligible_validators(self, validation_level: ValidationLevel, 
                               validation_request: Dict[str, Any]) -> List[str]:
        """Get list of eligible validators for validation level"""
        
        try:
            # This would integrate with the user system to get validators
            # For now, return placeholder data
            
            if validation_level == ValidationLevel.FOUNDER:
                # Get Contract Founders
                return self._get_users_by_role('contract_founder')
            
            elif validation_level == ValidationLevel.CITY:
                # Get Contract Members in same city
                requester_city = validation_request.get('requester_location', {}).get('city')
                return self._get_users_by_location_and_role(requester_city, 'city', 'contract_member')
            
            elif validation_level == ValidationLevel.STATE:
                # Get Contract Members in same state
                requester_state = validation_request.get('requester_location', {}).get('state')
                return self._get_users_by_location_and_role(requester_state, 'state', 'contract_member')
            
            elif validation_level == ValidationLevel.COUNTRY:
                # Get Contract Members in same country
                requester_country = validation_request.get('requester_location', {}).get('country')
                return self._get_users_by_location_and_role(requester_country, 'country', 'contract_member')
            
            else:
                return []
                
        except Exception as e:
            print(f"Error getting eligible validators: {e}")
            return []
    
    def _get_users_by_role(self, role: str) -> List[str]:
        """Get users by role (placeholder for user system integration)"""
        
        try:
            # This would integrate with users.backend
            from users.backend import UserBackend
            
            # Get all users with specified role
            users = UserBackend.get_all_users()
            eligible_users = [
                user.get('email') for user in users 
                if user.get('role') == role
            ]
            
            return eligible_users
            
        except ImportError:
            # Fallback for testing
            return [f"test_{role}@example.com"]
    
    def _get_users_by_location_and_role(self, location: str, location_type: str, role: str) -> List[str]:
        """Get users by geographic location and role"""
        
        try:
            from users.backend import UserBackend
            
            users = UserBackend.get_all_users()
            eligible_users = []
            
            for user in users:
                user_role = user.get('role', '')
                user_location = user.get(location_type, '').lower()
                
                # Check if user has required role (or higher authority)
                if self._user_has_sufficient_role(user_role, role):
                    # Check geographic match
                    if location and user_location == location.lower():
                        eligible_users.append(user.get('email'))
            
            return eligible_users
            
        except ImportError:
            # Fallback for testing
            return [f"test_{role}_{location}@example.com"]
    
    def _user_has_sufficient_role(self, user_role: str, required_role: str) -> bool:
        """Check if user role meets or exceeds required role"""
        
        role_hierarchy = {
            'contract_member': 1,
            'contract_representative': 2,
            'contract_senator': 3,
            'contract_elder': 4,
            'contract_founder': 5
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    # Election and Voting Integration
    def handle_election_created(self, election_data: Dict[str, Any]) -> List[str]:
        """Handle new election by creating voting tasks for eligible voters"""
        
        if not self.integration_config.get('auto_task_creation', True):
            return []
        
        try:
            election_id = election_data.get('election_id')
            election_type = election_data.get('type', 'general')
            jurisdiction = election_data.get('jurisdiction', {})
            
            # Get eligible voters based on jurisdiction and election type
            eligible_voters = self._get_eligible_voters(election_data)
            
            if not eligible_voters:
                print(f"Warning: No eligible voters found for election {election_id}")
                return []
            
            # Create voting tasks
            created_tasks = VotingTaskHandler.create_voting_tasks(
                election_id=election_id,
                eligible_voters=eligible_voters,
                election_data=election_data
            )
            
            print(f"Created {len(created_tasks)} voting tasks for election {election_id}")
            return created_tasks
            
        except Exception as e:
            print(f"Error handling election creation: {e}")
            return []
    
    def _get_eligible_voters(self, election_data: Dict[str, Any]) -> List[str]:
        """Get eligible voters for election based on jurisdiction and type"""
        
        try:
            election_type = election_data.get('type', 'general')
            jurisdiction = election_data.get('jurisdiction', {})
            
            # All Contract Members can vote in general elections
            if election_type == 'general':
                eligible_users = self._get_users_by_role('contract_member')
            
            # Role-specific elections
            elif election_type == 'representative_election':
                # Geographic-based voting for representatives
                city = jurisdiction.get('city')
                state = jurisdiction.get('state')
                
                if city:
                    eligible_users = self._get_users_by_location_and_role(city, 'city', 'contract_member')
                elif state:
                    eligible_users = self._get_users_by_location_and_role(state, 'state', 'contract_member')
                else:
                    eligible_users = self._get_users_by_role('contract_member')
            
            elif election_type == 'senator_election':
                # Mixed election system for senators
                representatives = self._get_users_by_role('contract_representative')
                citizens = self._get_users_by_role('contract_member')
                elders = self._get_users_by_role('contract_elder')
                
                # Combine all eligible voters for senator elections
                eligible_users = list(set(representatives + citizens + elders))
            
            elif election_type == 'elder_election':
                # Representatives and Senators vote for Elders
                representatives = self._get_users_by_role('contract_representative')
                senators = self._get_users_by_role('contract_senator')
                
                eligible_users = list(set(representatives + senators))
            
            else:
                # Default to all Contract Members
                eligible_users = self._get_users_by_role('contract_member')
            
            return eligible_users
            
        except Exception as e:
            print(f"Error getting eligible voters: {e}")
            return []
    
    # Contract and Amendment Integration
    def handle_amendment_proposed(self, amendment_data: Dict[str, Any]) -> List[str]:
        """Handle new constitutional amendment by creating review tasks"""
        
        if not self.integration_config.get('auto_task_creation', True):
            return []
        
        try:
            amendment_id = amendment_data.get('amendment_id')
            amendment_type = amendment_data.get('type', 'constitutional')
            
            # Get required reviewers based on amendment type
            required_reviewers = self._get_required_reviewers(amendment_data)
            
            if not required_reviewers:
                print(f"Warning: No reviewers found for amendment {amendment_id}")
                return []
            
            # Create review tasks
            created_tasks = ContractTaskHandler.create_contract_review_tasks(
                amendment_id=amendment_id,
                reviewers=required_reviewers,
                amendment_data=amendment_data
            )
            
            print(f"Created {len(created_tasks)} review tasks for amendment {amendment_id}")
            return created_tasks
            
        except Exception as e:
            print(f"Error handling amendment proposal: {e}")
            return []
    
    def _get_required_reviewers(self, amendment_data: Dict[str, Any]) -> List[str]:
        """Get required reviewers for amendment based on type and scope"""
        
        try:
            amendment_type = amendment_data.get('type', 'constitutional')
            scope = amendment_data.get('scope', 'national')
            
            reviewers = []
            
            # Constitutional amendments require Elder review
            if amendment_type == 'constitutional':
                reviewers.extend(self._get_users_by_role('contract_elder'))
            
            # All amendments require Representative input
            if scope == 'local':
                # Local representatives only
                jurisdiction = amendment_data.get('jurisdiction', {})
                city = jurisdiction.get('city')
                if city:
                    local_reps = self._get_users_by_location_and_role(city, 'city', 'contract_representative')
                    reviewers.extend(local_reps)
            else:
                # All representatives for national scope
                reviewers.extend(self._get_users_by_role('contract_representative'))
            
            # Major amendments require Senator review
            if amendment_data.get('major_change', False):
                reviewers.extend(self._get_users_by_role('contract_senator'))
            
            # Remove duplicates
            return list(set(reviewers))
            
        except Exception as e:
            print(f"Error getting required reviewers: {e}")
            return []
    
    # Moderation Integration
    def handle_content_flagged(self, flag_data: Dict[str, Any]) -> List[str]:
        """Handle content flagging by creating moderation jury tasks"""
        
        if not self.integration_config.get('auto_task_creation', True):
            return []
        
        try:
            flag_id = flag_data.get('flag_id')
            severity = flag_data.get('severity', 'medium')
            content_type = flag_data.get('content_type')
            
            # Determine jury size based on severity
            jury_size = self._get_jury_size(severity)
            
            # Get available jurors
            available_jurors = self._get_available_jurors(flag_data)
            
            # Select jury members (random selection to ensure fairness)
            import random
            selected_jurors = random.sample(available_jurors, min(jury_size, len(available_jurors)))
            
            # Create jury duty tasks
            created_tasks = []
            for juror_email in selected_jurors:
                task_data = {
                    'flag_id': flag_id,
                    'content_type': content_type,
                    'severity': severity,
                    'jury_role': 'peer_juror',
                    'evidence_package': flag_data.get('evidence', {}),
                    'due_process_requirements': ['review_evidence', 'hear_defense', 'deliberate', 'vote']
                }
                
                success, message = self.task_manager.create_task(
                    task_type=TaskType.JURY_DUTY,
                    assigned_to=juror_email,
                    task_data=task_data,
                    priority=TaskPriority.HIGH if severity in ['high', 'critical'] else TaskPriority.NORMAL
                )
                
                if success:
                    task_id = message.split(' ')[1]  # Extract task ID
                    created_tasks.append(task_id)
            
            print(f"Created {len(created_tasks)} jury duty tasks for flag {flag_id}")
            return created_tasks
            
        except Exception as e:
            print(f"Error handling content flagging: {e}")
            return []
    
    def _get_jury_size(self, severity: str) -> int:
        """Get required jury size based on flag severity"""
        
        jury_sizes = {
            'low': 3,
            'medium': 5,
            'high': 7,
            'critical': 9,
            'constitutional': 12
        }
        
        return jury_sizes.get(severity, 5)
    
    def _get_available_jurors(self, flag_data: Dict[str, Any]) -> List[str]:
        """Get available jurors for content moderation"""
        
        try:
            # All Contract Members are eligible for jury duty
            potential_jurors = self._get_users_by_role('contract_member')
            
            # Exclude involved parties
            reporter = flag_data.get('reporter_email')
            content_author = flag_data.get('content_author_email')
            
            available_jurors = [
                juror for juror in potential_jurors
                if juror not in [reporter, content_author]
            ]
            
            # TODO: Add additional filtering:
            # - Exclude users with conflicts of interest
            # - Prefer users with moderation training
            # - Consider geographic representation
            
            return available_jurors
            
        except Exception as e:
            print(f"Error getting available jurors: {e}")
            return []
    
    # Training Integration
    def handle_training_required(self, training_requirement: Dict[str, Any]) -> List[str]:
        """Handle training requirements by creating training tasks"""
        
        if not self.integration_config.get('auto_task_creation', True):
            return []
        
        try:
            course_id = training_requirement.get('course_id')
            required_for_roles = training_requirement.get('required_roles', ['contract_member'])
            deadline = training_requirement.get('deadline')
            
            # Get users who need this training
            users_needing_training = []
            
            for role in required_for_roles:
                role_users = self._get_users_by_role(role)
                
                # Filter out users who already completed the training
                for user_email in role_users:
                    if not self._user_completed_training(user_email, course_id):
                        users_needing_training.append(user_email)
            
            # Remove duplicates
            users_needing_training = list(set(users_needing_training))
            
            # Create training tasks
            created_tasks = []
            for user_email in users_needing_training:
                task_data = {
                    'course_id': course_id,
                    'course_name': training_requirement.get('course_name'),
                    'required_for_role': True,
                    'completion_criteria': training_requirement.get('completion_criteria', {}),
                    'certification_available': training_requirement.get('certification', False)
                }
                
                success, message = self.task_manager.create_task(
                    task_type=TaskType.TRAINING_COMPLETION,
                    assigned_to=user_email,
                    task_data=task_data,
                    priority=TaskPriority.NORMAL
                )
                
                if success:
                    task_id = message.split(' ')[1]
                    created_tasks.append(task_id)
            
            print(f"Created {len(created_tasks)} training tasks for course {course_id}")
            return created_tasks
            
        except Exception as e:
            print(f"Error handling training requirement: {e}")
            return []
    
    def _user_completed_training(self, user_email: str, course_id: str) -> bool:
        """Check if user has completed specific training course"""
        
        try:
            # This would integrate with the training module
            # For now, return False to create tasks
            return False
            
        except Exception as e:
            print(f"Error checking training completion: {e}")
            return False
    
    # Automatic Task Management
    def process_expired_tasks(self) -> Dict[str, int]:
        """Process expired tasks and handle consequences"""
        
        expired_task_ids = self.task_manager.expire_overdue_tasks()
        
        consequences = {
            'tasks_expired': len(expired_task_ids),
            'penalties_applied': 0,
            'notifications_sent': 0,
            'escalations_created': 0
        }
        
        for task_id in expired_task_ids:
            task = self.task_manager.get_task_by_id(task_id)
            if not task:
                continue
            
            # Apply consequences based on task type
            if task['task_type'] == TaskType.BLOCKCHAIN_VALIDATION.value:
                # Validation expiry might trigger alternative validation
                self._handle_validation_expiry(task)
                consequences['escalations_created'] += 1
            
            elif task['task_type'] == TaskType.VOTING_OPPORTUNITY.value:
                # Missed voting might result in reduced civic participation score
                self._handle_missed_voting(task)
                consequences['penalties_applied'] += 1
            
            elif task['task_type'] == TaskType.JURY_DUTY.value:
                # Missed jury duty is a serious civic obligation failure
                self._handle_missed_jury_duty(task)
                consequences['penalties_applied'] += 1
            
            # Send expiration notification
            self._send_expiration_notification(task)
            consequences['notifications_sent'] += 1
        
        return consequences
    
    def _handle_validation_expiry(self, task: Dict[str, Any]):
        """Handle expired validation task by triggering alternative validation"""
        
        validation_request_id = task['data'].get('validation_request_id')
        validation_level = task['data'].get('validation_level')
        
        # Trigger escalated validation or alternative validators
        print(f"Validation task expired for request {validation_request_id}, triggering escalation")
        
        # This could create new validation requests at different levels
        # or notify administrators about the validation failure
    
    def _handle_missed_voting(self, task: Dict[str, Any]):
        """Handle missed voting by recording civic participation impact"""
        
        election_id = task['data'].get('election_id')
        user_email = task['assigned_to']
        
        print(f"User {user_email} missed voting in election {election_id}")
        
        # This could integrate with a civic participation scoring system
        # or trigger additional civic education requirements
    
    def _handle_missed_jury_duty(self, task: Dict[str, Any]):
        """Handle missed jury duty with appropriate consequences"""
        
        flag_id = task['data'].get('flag_id')
        user_email = task['assigned_to']
        
        print(f"User {user_email} missed jury duty for flag {flag_id}")
        
        # Jury duty is a critical civic obligation
        # This might trigger additional training requirements or
        # temporary restriction from certain platform privileges
    
    def _send_expiration_notification(self, task: Dict[str, Any]):
        """Send notification about task expiration"""
        
        user_email = task['assigned_to']
        task_type = task['task_type']
        
        print(f"Sending expiration notification to {user_email} for {task_type}")
        
        # This would integrate with the notification system
        # to send appropriate notifications to the user
    
    # Performance and Analytics
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get statistics about task integration performance"""
        
        stats = {
            'auto_tasks_created_today': self._count_auto_tasks_today(),
            'integration_success_rate': self._calculate_integration_success_rate(),
            'average_task_response_time': self._calculate_average_response_time(),
            'cross_module_efficiency': self._calculate_cross_module_efficiency(),
            'user_engagement_metrics': self._get_user_engagement_metrics()
        }
        
        return stats
    
    def _count_auto_tasks_today(self) -> int:
        """Count automatically created tasks today"""
        
        today = datetime.now().date()
        all_tasks = self.task_manager.get_all_active_tasks()
        
        auto_tasks_today = 0
        for task in all_tasks:
            created_date = datetime.fromisoformat(task['created_at']).date()
            if created_date == today:
                # Check if task was auto-created (vs manually created)
                if task['data'].get('auto_created', True):
                    auto_tasks_today += 1
        
        return auto_tasks_today
    
    def _calculate_integration_success_rate(self) -> float:
        """Calculate success rate of cross-module integrations"""
        
        # This would track successful vs failed integration attempts
        # For now, return a placeholder value
        return 95.5
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average time from trigger event to task creation"""
        
        # This would track timing metrics for integration performance
        # For now, return a placeholder value (in seconds)
        return 2.3
    
    def _calculate_cross_module_efficiency(self) -> float:
        """Calculate efficiency of cross-module task coordination"""
        
        # This would measure how well tasks coordinate across modules
        # For now, return a placeholder value
        return 87.2
    
    def _get_user_engagement_metrics(self) -> Dict[str, float]:
        """Get user engagement metrics from task completion patterns"""
        
        return {
            'task_completion_rate': 78.9,
            'average_completion_time_hours': 18.5,
            'user_satisfaction_score': 4.2,
            'repeat_engagement_rate': 65.3
        }

# Specialized Integration Handlers
class BlockchainTaskIntegration:
    """Specialized integration for blockchain validation tasks"""
    
    def __init__(self, integration_manager: TaskIntegrationManager):
        self.integration_manager = integration_manager
    
    def create_validation_cascade(self, initial_request: Dict[str, Any]) -> List[str]:
        """Create cascading validation requests across multiple levels"""
        
        all_tasks = []
        
        # Start with city-level validation
        city_tasks = self.integration_manager.handle_validation_request({
            **initial_request,
            'validation_level': ValidationLevel.CITY.value
        })
        all_tasks.extend(city_tasks)
        
        # If city validation insufficient, escalate to state level
        if len(city_tasks) < 3:  # Minimum validator threshold
            state_tasks = self.integration_manager.handle_validation_request({
                **initial_request,
                'validation_level': ValidationLevel.STATE.value
            })
            all_tasks.extend(state_tasks)
        
        # Constitutional issues require Elder validation
        if initial_request.get('constitutional_impact', False):
            founder_tasks = self.integration_manager.handle_validation_request({
                **initial_request,
                'validation_level': ValidationLevel.FOUNDER.value
            })
            all_tasks.extend(founder_tasks)
        
        return all_tasks

class ElectionTaskIntegration:
    """Specialized integration for election and voting tasks"""
    
    def __init__(self, integration_manager: TaskIntegrationManager):
        self.integration_manager = integration_manager
    
    def create_election_cycle_tasks(self, election_cycle_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Create comprehensive tasks for complete election cycle"""
        
        cycle_tasks = {
            'candidate_registration': [],
            'campaign_oversight': [],
            'voting_tasks': [],
            'result_verification': []
        }
        
        # Create voting tasks for all elections in cycle
        for election in election_cycle_data.get('elections', []):
            voting_tasks = self.integration_manager.handle_election_created(election)
            cycle_tasks['voting_tasks'].extend(voting_tasks)
        
        # Create oversight tasks for campaign period
        campaign_overseers = self.integration_manager._get_users_by_role('contract_senator')
        for overseer in campaign_overseers:
            # Create campaign oversight tasks
            pass  # Implementation would create specific oversight tasks
        
        return cycle_tasks

# Export main classes
__all__ = [
    'TaskIntegrationManager', 
    'BlockchainTaskIntegration', 
    'ElectionTaskIntegration'
]