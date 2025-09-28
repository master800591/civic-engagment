# Core Task Management and Assignment Logic
# Centralized task management system for civic engagement platform

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Import from other modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.task_types import (
    TaskType, TaskCategory, TaskPriority, TaskStatus, ValidationLevel, 
    RewardType, TaskTypeManager, TaskTemplate
)
from blockchain.blockchain import Blockchain
from users.session import SessionManager
from users.backend import UserBackend

@dataclass
class Task:
    """Task data structure for type safety and validation"""
    task_id: str
    task_type: TaskType
    category: TaskCategory
    assigned_to: str
    created_at: str
    deadline: str
    priority: TaskPriority
    status: TaskStatus
    data: Dict[str, Any]
    rewards: Dict[str, Any]
    completion_percentage: int = 0
    notifications_sent: List[str] = None
    related_tasks: List[str] = None
    completed_at: Optional[str] = None
    completed_by: Optional[str] = None
    
    def __post_init__(self):
        if self.notifications_sent is None:
            self.notifications_sent = []
        if self.related_tasks is None:
            self.related_tasks = []

class TaskManager:
    """Core task management and assignment logic"""
    
    def __init__(self, db_path: str = None):
        """Initialize task manager with database path"""
        if db_path is None:
            # Use environment-aware path from main config
            try:
                from main import ENV_CONFIG
                self.db_path = Path(ENV_CONFIG.get('tasks_db_path', 'tasks/tasks_db.json'))
            except ImportError:
                self.db_path = Path('tasks/tasks_db.json')
        else:
            self.db_path = Path(db_path)
            
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database if it doesn't exist
        if not self.db_path.exists():
            self._initialize_database()
    
    def _initialize_database(self):
        """Initialize empty task database"""
        initial_data = {
            'tasks': [],
            'task_assignments': [],
            'task_history': [],
            'task_statistics': {
                'total_created': 0,
                'total_completed': 0,
                'total_expired': 0,
                'completion_rate': 0.0
            },
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.db_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    def _load_database(self) -> Dict[str, Any]:
        """Load task database from JSON file"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._initialize_database()
            return self._load_database()
    
    def _save_database(self, data: Dict[str, Any]):
        """Save task database to JSON file"""
        data['last_updated'] = datetime.now().isoformat()
        
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_task(self, task_type: TaskType, assigned_to: str, 
                   task_data: Dict[str, Any], priority: TaskPriority = TaskPriority.NORMAL) -> Tuple[bool, str]:
        """Create new task and assign to user"""
        
        try:
            # Validate task data
            is_valid, validation_message = TaskTypeManager.validate_task_data(task_type, task_data)
            if not is_valid:
                return False, f"Task validation failed: {validation_message}"
            
            # Check if user exists and has required role
            user = UserBackend.get_user_by_email(assigned_to)
            if not user:
                return False, f"User not found: {assigned_to}"
            
            # Check role requirements
            available_tasks = TaskTypeManager.get_tasks_for_role(user.get('role', 'contract_member'))
            if task_type not in available_tasks:
                return False, f"User {assigned_to} not authorized for task type {task_type.value}"
            
            # Generate task ID and create task object
            task_id = str(uuid.uuid4())
            
            # Get task configuration
            config = TaskTypeManager.get_task_config(task_type)
            
            # Create task with all required fields
            task = Task(
                task_id=task_id,
                task_type=task_type,
                category=config.get('category', TaskCategory.ADMINISTRATIVE),
                assigned_to=assigned_to,
                created_at=datetime.now().isoformat(),
                deadline=TaskTypeManager.calculate_deadline(task_type).isoformat(),
                priority=priority,
                status=TaskStatus.PENDING,
                data=task_data,
                rewards=TaskTypeManager.get_task_reward_info(task_type)
            )
            
            # Save task to database
            db_data = self._load_database()
            db_data['tasks'].append(asdict(task))
            db_data['task_statistics']['total_created'] += 1
            self._save_database(db_data)
            
            # Send notification to user
            self._send_task_notification(assigned_to, task, 'created')
            
            # Record task creation on blockchain for transparency
            Blockchain.add_page(
                action_type="task_created",
                data={
                    'task_id': task_id,
                    'task_type': task_type.value,
                    'assigned_to': assigned_to,
                    'priority': priority.value,
                    'deadline': task.deadline
                },
                user_email=assigned_to
            )
            
            return True, f"Task {task_id} created successfully for {assigned_to}"
            
        except Exception as e:
            return False, f"Error creating task: {str(e)}"
    
    def get_user_tasks(self, user_email: str, status_filter: List[TaskStatus] = None, 
                      category_filter: List[TaskCategory] = None) -> List[Dict[str, Any]]:
        """Get tasks assigned to specific user with optional filtering"""
        
        db_data = self._load_database()
        user_tasks = []
        
        for task_dict in db_data['tasks']:
            if task_dict['assigned_to'] == user_email:
                # Apply status filter
                if status_filter:
                    task_status = TaskStatus(task_dict['status'])
                    if task_status not in status_filter:
                        continue
                
                # Apply category filter
                if category_filter:
                    task_category = TaskCategory(task_dict['category'])
                    if task_category not in category_filter:
                        continue
                
                user_tasks.append(task_dict)
        
        # Sort by priority and deadline
        user_tasks.sort(key=lambda x: (
            TaskPriority(x['priority']).value,
            x['deadline']
        ))
        
        return user_tasks
    
    def complete_task(self, task_id: str, completed_by: str, completion_data: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Mark task as completed and process rewards"""
        
        try:
            db_data = self._load_database()
            
            # Find task
            task_dict = None
            task_index = None
            
            for i, t in enumerate(db_data['tasks']):
                if t['task_id'] == task_id:
                    task_dict = t
                    task_index = i
                    break
            
            if not task_dict:
                return False, f"Task {task_id} not found"
            
            # Verify user authorization to complete task
            if task_dict['assigned_to'] != completed_by:
                # Check if user has authority to complete on behalf of others
                completer = UserBackend.get_user_by_email(completed_by)
                if not completer or completer.get('role') not in ['contract_elder', 'contract_founder']:
                    return False, f"User {completed_by} not authorized to complete task {task_id}"
            
            # Check if task is already completed
            if task_dict['status'] == TaskStatus.COMPLETED.value:
                return False, f"Task {task_id} already completed"
            
            # Update task status
            task_dict['status'] = TaskStatus.COMPLETED.value
            task_dict['completed_at'] = datetime.now().isoformat()
            task_dict['completed_by'] = completed_by
            task_dict['completion_percentage'] = 100
            
            if completion_data:
                task_dict['data'].update(completion_data)
            
            # Update database
            db_data['tasks'][task_index] = task_dict
            db_data['task_statistics']['total_completed'] += 1
            
            # Calculate completion rate
            total_created = db_data['task_statistics']['total_created']
            total_completed = db_data['task_statistics']['total_completed']
            db_data['task_statistics']['completion_rate'] = (total_completed / total_created * 100) if total_created > 0 else 0
            
            # Add to history
            db_data['task_history'].append({
                'action': 'completed',
                'task_id': task_id,
                'completed_by': completed_by,
                'timestamp': datetime.now().isoformat(),
                'completion_data': completion_data
            })
            
            self._save_database(db_data)
            
            # Process rewards
            self._process_task_rewards(task_dict, completed_by)
            
            # Send completion notification
            self._send_task_notification(completed_by, task_dict, 'completed')
            
            # Record completion on blockchain
            Blockchain.add_page(
                action_type="task_completed",
                data={
                    'task_id': task_id,
                    'task_type': task_dict['task_type'],
                    'completed_by': completed_by,
                    'completion_data': completion_data
                },
                user_email=completed_by
            )
            
            return True, f"Task {task_id} completed successfully"
            
        except Exception as e:
            return False, f"Error completing task: {str(e)}"
    
    def defer_task(self, task_id: str, deferred_by: str, reason: str = None, 
                  new_deadline: datetime = None) -> Tuple[bool, str]:
        """Defer task to later time with optional reason"""
        
        try:
            db_data = self._load_database()
            
            # Find task
            task_dict = None
            task_index = None
            
            for i, t in enumerate(db_data['tasks']):
                if t['task_id'] == task_id:
                    task_dict = t
                    task_index = i
                    break
            
            if not task_dict:
                return False, f"Task {task_id} not found"
            
            # Check if task can be deferred
            task_type = TaskType(task_dict['task_type'])
            config = TaskTypeManager.get_task_config(task_type)
            
            if not config.get('can_be_deferred', True):
                return False, f"Task {task_id} cannot be deferred"
            
            # Verify authorization
            if task_dict['assigned_to'] != deferred_by:
                return False, f"User {deferred_by} not authorized to defer task {task_id}"
            
            # Update task
            task_dict['status'] = TaskStatus.DEFERRED.value
            
            if new_deadline:
                task_dict['deadline'] = new_deadline.isoformat()
            else:
                # Add default deferral time (24 hours)
                current_deadline = datetime.fromisoformat(task_dict['deadline'])
                task_dict['deadline'] = (current_deadline + timedelta(hours=24)).isoformat()
            
            # Add deferral information to task data
            if 'deferral_history' not in task_dict['data']:
                task_dict['data']['deferral_history'] = []
            
            task_dict['data']['deferral_history'].append({
                'deferred_by': deferred_by,
                'deferred_at': datetime.now().isoformat(),
                'reason': reason,
                'new_deadline': task_dict['deadline']
            })
            
            # Update database
            db_data['tasks'][task_index] = task_dict
            self._save_database(db_data)
            
            # Record deferral on blockchain
            Blockchain.add_page(
                action_type="task_deferred",
                data={
                    'task_id': task_id,
                    'deferred_by': deferred_by,
                    'reason': reason,
                    'new_deadline': task_dict['deadline']
                },
                user_email=deferred_by
            )
            
            return True, f"Task {task_id} deferred successfully"
            
        except Exception as e:
            return False, f"Error deferring task: {str(e)}"
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task completion and performance statistics"""
        
        db_data = self._load_database()
        
        # Calculate current statistics
        tasks = db_data['tasks']
        total_tasks = len(tasks)
        
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len([t for t in tasks if t['status'] == status.value])
        
        priority_counts = {}
        for priority in TaskPriority:
            priority_counts[priority.value] = len([t for t in tasks if t['priority'] == priority.value])
        
        category_counts = {}
        for category in TaskCategory:
            category_counts[category.value] = len([t for t in tasks if t['category'] == category.value])
        
        # Calculate average completion time
        completed_tasks = [t for t in tasks if t['status'] == TaskStatus.COMPLETED.value and 'completed_at' in t]
        avg_completion_time = 0
        
        if completed_tasks:
            total_time = 0
            for task in completed_tasks:
                created = datetime.fromisoformat(task['created_at'])
                completed = datetime.fromisoformat(task['completed_at'])
                total_time += (completed - created).total_seconds()
            
            avg_completion_time = total_time / len(completed_tasks) / 3600  # Convert to hours
        
        return {
            'total_tasks': total_tasks,
            'status_breakdown': status_counts,
            'priority_breakdown': priority_counts,
            'category_breakdown': category_counts,
            'completion_rate': db_data['task_statistics']['completion_rate'],
            'average_completion_hours': round(avg_completion_time, 2),
            'last_updated': db_data['last_updated']
        }
    
    def expire_overdue_tasks(self) -> List[str]:
        """Expire tasks that are past their deadline"""
        
        db_data = self._load_database()
        expired_task_ids = []
        current_time = datetime.now()
        
        for i, task_dict in enumerate(db_data['tasks']):
            if task_dict['status'] in [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]:
                deadline = datetime.fromisoformat(task_dict['deadline'])
                
                if current_time > deadline:
                    # Mark as expired
                    task_dict['status'] = TaskStatus.EXPIRED.value
                    task_dict['expired_at'] = current_time.isoformat()
                    
                    expired_task_ids.append(task_dict['task_id'])
                    
                    # Send expiration notification
                    self._send_task_notification(task_dict['assigned_to'], task_dict, 'expired')
                    
                    # Record expiration on blockchain
                    Blockchain.add_page(
                        action_type="task_expired",
                        data={
                            'task_id': task_dict['task_id'],
                            'assigned_to': task_dict['assigned_to'],
                            'expired_at': task_dict['expired_at']
                        },
                        user_email=task_dict['assigned_to']
                    )
        
        if expired_task_ids:
            db_data['task_statistics']['total_expired'] += len(expired_task_ids)
            self._save_database(db_data)
        
        return expired_task_ids
    
    def _send_task_notification(self, user_email: str, task: Dict[str, Any], 
                              notification_type: str):
        """Send task notification to user (placeholder for notification system)"""
        
        # This will integrate with the notification system
        # For now, just log the notification
        notification_message = {
            'created': f"New task assigned: {task['task_type']}",
            'completed': f"Task completed: {task['task_type']}", 
            'expired': f"Task expired: {task['task_type']}",
            'reminder': f"Task deadline approaching: {task['task_type']}"
        }
        
        print(f"NOTIFICATION [{notification_type.upper()}] for {user_email}: {notification_message.get(notification_type, 'Task update')}")
        
        # Add notification to task history
        if 'notifications_sent' not in task:
            task['notifications_sent'] = []
        
        task['notifications_sent'].append({
            'type': notification_type,
            'sent_at': datetime.now().isoformat(),
            'message': notification_message.get(notification_type, 'Task update')
        })
    
    def _process_task_rewards(self, task: Dict[str, Any], completed_by: str):
        """Process rewards for task completion (placeholder for crypto module integration)"""
        
        # This will integrate with the crypto/rewards system
        reward_info = task.get('rewards', {})
        reward_type = reward_info.get('reward_type')
        reward_amount = reward_info.get('reward_amount', 0)
        
        if reward_amount > 0:
            print(f"REWARD: {completed_by} earned {reward_amount} {reward_type} for completing task {task['task_id']}")
            
            # Record reward on blockchain
            Blockchain.add_page(
                action_type="reward_distributed",
                data={
                    'recipient': completed_by,
                    'reward_type': reward_type,
                    'reward_amount': reward_amount,
                    'task_id': task['task_id'],
                    'earned_for': task['task_type']
                },
                user_email=completed_by
            )

    def get_all_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all active tasks across all users"""
        
        db_data = self._load_database()
        
        active_statuses = [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]
        active_tasks = [
            task for task in db_data['tasks'] 
            if task['status'] in active_statuses
        ]
        
        return active_tasks
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get specific task by ID"""
        
        db_data = self._load_database()
        
        for task in db_data['tasks']:
            if task['task_id'] == task_id:
                return task
        
        return None

# Specialized Task Handlers for different task types
class ValidationTaskHandler:
    """Handle blockchain validation tasks"""
    
    @staticmethod
    def create_validation_tasks(validation_request_id: str, eligible_validators: List[str], 
                              validation_level: ValidationLevel) -> List[str]:
        """Create validation tasks for eligible validators"""
        
        task_manager = TaskManager()
        created_task_ids = []
        
        for validator_email in eligible_validators:
            task_data = {
                'validation_request_id': validation_request_id,
                'validation_level': validation_level.value,
                'validation_requirements': f"Validate blockchain request at {validation_level.value} level",
                'estimated_time': '15 minutes'
            }
            
            success, message = task_manager.create_task(
                task_type=TaskType.BLOCKCHAIN_VALIDATION,
                assigned_to=validator_email,
                task_data=task_data,
                priority=TaskPriority.HIGH
            )
            
            if success:
                # Extract task ID from success message
                task_id = message.split(' ')[1]  # "Task {task_id} created successfully"
                created_task_ids.append(task_id)
        
        return created_task_ids

class VotingTaskHandler:
    """Handle voting and election tasks"""
    
    @staticmethod
    def create_voting_tasks(election_id: str, eligible_voters: List[str], 
                          election_data: Dict[str, Any]) -> List[str]:
        """Create voting tasks for eligible voters"""
        
        task_manager = TaskManager()
        created_task_ids = []
        
        for voter_email in eligible_voters:
            task_data = {
                'election_id': election_id,
                'election_type': election_data.get('type', 'general'),
                'ballot_items': election_data.get('ballot_items', []),
                'candidates': election_data.get('candidates', []),
                'voting_deadline': election_data.get('deadline')
            }
            
            success, message = task_manager.create_task(
                task_type=TaskType.VOTING_OPPORTUNITY,
                assigned_to=voter_email,
                task_data=task_data,
                priority=TaskPriority.HIGH
            )
            
            if success:
                task_id = message.split(' ')[1]
                created_task_ids.append(task_id)
        
        return created_task_ids

class ContractTaskHandler:
    """Handle contract and governance tasks"""
    
    @staticmethod
    def create_contract_review_tasks(amendment_id: str, reviewers: List[str], 
                                   amendment_data: Dict[str, Any]) -> List[str]:
        """Create contract review tasks for reviewers"""
        
        task_manager = TaskManager()
        created_task_ids = []
        
        for reviewer_email in reviewers:
            task_data = {
                'amendment_id': amendment_id,
                'amendment_type': amendment_data.get('type', 'constitutional'),
                'review_requirements': [
                    'constitutional_compliance',
                    'impact_analysis',
                    'precedent_review'
                ],
                'amendment_text': amendment_data.get('text', ''),
                'review_deadline': amendment_data.get('deadline')
            }
            
            success, message = task_manager.create_task(
                task_type=TaskType.CONTRACT_REVIEW,
                assigned_to=reviewer_email,
                task_data=task_data,
                priority=TaskPriority.NORMAL
            )
            
            if success:
                task_id = message.split(' ')[1]
                created_task_ids.append(task_id)
        
        return created_task_ids

# Export key classes and functions
__all__ = [
    'Task', 'TaskManager', 'ValidationTaskHandler', 'VotingTaskHandler', 'ContractTaskHandler'
]