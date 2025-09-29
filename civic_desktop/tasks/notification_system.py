# Task Notification System - Comprehensive notification and alert system
# Handles task notifications, reminders, and user communication

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum
import uuid

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.task_types import TaskType, TaskPriority, TaskStatus

class NotificationType(Enum):
    """Types of task notifications"""
    TASK_CREATED = "task_created"
    TASK_REMINDER = "task_reminder"
    TASK_URGENT = "task_urgent"
    TASK_OVERDUE = "task_overdue"
    TASK_COMPLETED = "task_completed"
    TASK_DEFERRED = "task_deferred"
    TASK_EXPIRED = "task_expired"
    TASK_ESCALATED = "task_escalated"

class NotificationChannel(Enum):
    """Available notification channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"  # For future mobile integration
    SMS = "sms"    # For critical notifications

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class TaskNotificationSystem:
    """Comprehensive task notification and alert system"""
    
    def __init__(self, db_path: str = None):
        """Initialize notification system"""
        
        if db_path is None:
            try:
                from main import ENV_CONFIG
                self.db_path = Path(ENV_CONFIG.get('notifications_db_path', 'tasks/notifications_db.json'))
            except ImportError:
                self.db_path = Path('tasks/notifications_db.json')
        else:
            self.db_path = Path(db_path)
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database if it doesn't exist
        if not self.db_path.exists():
            self._initialize_database()
        
        # Load notification preferences
        self.notification_preferences = self._load_notification_preferences()
    
    def _initialize_database(self):
        """Initialize notification database"""
        
        initial_data = {
            'notifications': [],
            'notification_history': [],
            'user_preferences': {},
            'delivery_log': [],
            'statistics': {
                'total_sent': 0,
                'delivery_success_rate': 100.0,
                'average_delivery_time': 0.0
            },
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.db_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    def _load_database(self) -> Dict[str, Any]:
        """Load notification database"""
        
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._initialize_database()
            return self._load_database()
    
    def _save_database(self, data: Dict[str, Any]):
        """Save notification database"""
        
        data['last_updated'] = datetime.now().isoformat()
        
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_notification_preferences(self) -> Dict[str, Any]:
        """Load default notification preferences"""
        
        return {
            'default_channels': [NotificationChannel.IN_APP.value],
            'priority_channels': {
                NotificationPriority.LOW.value: [NotificationChannel.IN_APP.value],
                NotificationPriority.NORMAL.value: [NotificationChannel.IN_APP.value],
                NotificationPriority.HIGH.value: [NotificationChannel.IN_APP.value, NotificationChannel.EMAIL.value],
                NotificationPriority.URGENT.value: [NotificationChannel.IN_APP.value, NotificationChannel.EMAIL.value],
                NotificationPriority.CRITICAL.value: [NotificationChannel.IN_APP.value, NotificationChannel.EMAIL.value, NotificationChannel.SMS.value]
            },
            'reminder_intervals': {
                TaskPriority.LOW.value: [timedelta(days=1)],
                TaskPriority.NORMAL.value: [timedelta(hours=24), timedelta(hours=4)],
                TaskPriority.HIGH.value: [timedelta(hours=12), timedelta(hours=2)],
                TaskPriority.URGENT.value: [timedelta(hours=6), timedelta(hours=1)],
                TaskPriority.CRITICAL.value: [timedelta(hours=2), timedelta(minutes=30)]
            },
            'quiet_hours': {
                'enabled': True,
                'start_time': '22:00',
                'end_time': '07:00'
            }
        }
    
    def send_task_notification(self, user_email: str, task: Dict[str, Any], 
                              notification_type: NotificationType, 
                              additional_data: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Send task notification to user"""
        
        try:
            # Generate notification
            notification = self._create_notification(user_email, task, notification_type, additional_data)
            
            # Determine notification priority and channels
            priority = self._determine_notification_priority(task, notification_type)
            channels = self._get_notification_channels(user_email, priority)
            
            # Check quiet hours
            if self._is_quiet_hours(user_email) and priority not in [NotificationPriority.URGENT, NotificationPriority.CRITICAL]:
                # Defer notification until after quiet hours
                return self._defer_notification(notification, channels)
            
            # Send notification via all applicable channels
            delivery_results = []
            for channel in channels:
                success, message = self._send_via_channel(notification, channel)
                delivery_results.append((channel.value, success, message))
            
            # Save notification to database
            db_data = self._load_database()
            db_data['notifications'].append(notification)
            
            # Log delivery results
            delivery_log_entry = {
                'notification_id': notification['notification_id'],
                'timestamp': datetime.now().isoformat(),
                'delivery_results': delivery_results,
                'success_count': len([r for r in delivery_results if r[1]]),
                'total_attempts': len(delivery_results)
            }
            
            db_data['delivery_log'].append(delivery_log_entry)
            
            # Update statistics
            db_data['statistics']['total_sent'] += 1
            
            self._save_database(db_data)
            
            # Return success if at least one channel succeeded
            success_count = delivery_log_entry['success_count']
            if success_count > 0:
                return True, f"Notification sent via {success_count}/{len(delivery_results)} channels"
            else:
                return False, "Failed to deliver notification via any channel"
                
        except Exception as e:
            return False, f"Error sending notification: {str(e)}"
    
    def _create_notification(self, user_email: str, task: Dict[str, Any], 
                            notification_type: NotificationType, 
                            additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create notification object"""
        
        notification_templates = self._get_notification_templates()
        template = notification_templates.get(notification_type.value, {})
        
        # Format notification content
        title = self._format_notification_title(template.get('title', 'Task Notification'), task)
        message = self._format_notification_message(template.get('message', 'Task update'), task)
        
        notification = {
            'notification_id': str(uuid.uuid4()),
            'user_email': user_email,
            'task_id': task['task_id'],
            'task_type': task['task_type'],
            'notification_type': notification_type.value,
            'title': title,
            'message': message,
            'created_at': datetime.now().isoformat(),
            'read': False,
            'dismissed': False,
            'additional_data': additional_data or {},
            'metadata': {
                'task_priority': task.get('priority', TaskPriority.NORMAL.value),
                'task_deadline': task.get('deadline'),
                'task_status': task.get('status', TaskStatus.PENDING.value)
            }
        }
        
        return notification
    
    def _get_notification_templates(self) -> Dict[str, Dict[str, str]]:
        """Get notification message templates"""
        
        return {
            NotificationType.TASK_CREATED.value: {
                'title': '📋 New Task Assigned',
                'message': 'You have been assigned a new {task_type} task. Deadline: {deadline}'
            },
            NotificationType.TASK_REMINDER.value: {
                'title': '⏰ Task Reminder',
                'message': 'Reminder: Your {task_type} task is due {deadline}. Please complete it soon.'
            },
            NotificationType.TASK_URGENT.value: {
                'title': '🚨 Urgent Task',
                'message': 'URGENT: Your {task_type} task requires immediate attention. Deadline: {deadline}'
            },
            NotificationType.TASK_OVERDUE.value: {
                'title': '⚠️ Overdue Task',
                'message': 'Your {task_type} task is now overdue. Original deadline was {deadline}.'
            },
            NotificationType.TASK_COMPLETED.value: {
                'title': '✅ Task Completed',
                'message': 'Great job! Your {task_type} task has been completed successfully.'
            },
            NotificationType.TASK_DEFERRED.value: {
                'title': '⏸️ Task Deferred',
                'message': 'Your {task_type} task has been deferred. New deadline: {deadline}'
            },
            NotificationType.TASK_EXPIRED.value: {
                'title': '❌ Task Expired',
                'message': 'Your {task_type} task has expired. Please contact support if needed.'
            },
            NotificationType.TASK_ESCALATED.value: {
                'title': '🔺 Task Escalated',
                'message': 'Your {task_type} task has been escalated due to missed deadline.'
            }
        }
    
    def _format_notification_title(self, template: str, task: Dict[str, Any]) -> str:
        """Format notification title with task data"""
        
        task_type_display = task['task_type'].replace('_', ' ').title()
        
        return template.format(
            task_type=task_type_display,
            deadline=self._format_deadline_for_notification(task.get('deadline')),
            priority=task.get('priority', '').title()
        )
    
    def _format_notification_message(self, template: str, task: Dict[str, Any]) -> str:
        """Format notification message with task data"""
        
        task_type_display = task['task_type'].replace('_', ' ').title()
        
        return template.format(
            task_type=task_type_display,
            deadline=self._format_deadline_for_notification(task.get('deadline')),
            priority=task.get('priority', '').title(),
            task_id=task.get('task_id', 'Unknown')
        )
    
    def _format_deadline_for_notification(self, deadline_str: str) -> str:
        """Format deadline for notification display"""
        
        if not deadline_str:
            return "No deadline"
        
        try:
            deadline = datetime.fromisoformat(deadline_str)
            now = datetime.now()
            
            if deadline < now:
                return "Overdue"
            
            time_diff = deadline - now
            
            if time_diff.days > 1:
                return f"in {time_diff.days} days"
            elif time_diff.days == 1:
                return "tomorrow"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                return f"in {hours} hour{'s' if hours > 1 else ''}"
            else:
                minutes = time_diff.seconds // 60
                return f"in {minutes} minute{'s' if minutes != 1 else ''}"
                
        except Exception:
            return deadline_str
    
    def _determine_notification_priority(self, task: Dict[str, Any], 
                                       notification_type: NotificationType) -> NotificationPriority:
        """Determine notification priority based on task and notification type"""
        
        task_priority = TaskPriority(task.get('priority', TaskPriority.NORMAL.value))
        
        # Critical notifications
        if notification_type in [NotificationType.TASK_OVERDUE, NotificationType.TASK_EXPIRED]:
            return NotificationPriority.CRITICAL
        
        # Urgent notifications
        if notification_type == NotificationType.TASK_URGENT:
            return NotificationPriority.URGENT
        
        # High priority notifications
        if (notification_type == NotificationType.TASK_REMINDER and 
            task_priority in [TaskPriority.HIGH, TaskPriority.URGENT]):
            return NotificationPriority.HIGH
        
        # Map task priority to notification priority
        priority_mapping = {
            TaskPriority.LOW: NotificationPriority.LOW,
            TaskPriority.NORMAL: NotificationPriority.NORMAL,
            TaskPriority.HIGH: NotificationPriority.HIGH,
            TaskPriority.URGENT: NotificationPriority.URGENT,
            TaskPriority.CRITICAL: NotificationPriority.CRITICAL
        }
        
        return priority_mapping.get(task_priority, NotificationPriority.NORMAL)
    
    def _get_notification_channels(self, user_email: str, 
                                  priority: NotificationPriority) -> List[NotificationChannel]:
        """Get appropriate notification channels for user and priority"""
        
        # Get user preferences (if available)
        db_data = self._load_database()
        user_prefs = db_data['user_preferences'].get(user_email, {})
        
        # Use user preferences or defaults
        if 'priority_channels' in user_prefs:
            channel_names = user_prefs['priority_channels'].get(priority.value, ['in_app'])
        else:
            channel_names = self.notification_preferences['priority_channels'][priority.value]
        
        # Convert to NotificationChannel objects
        channels = []
        for channel_name in channel_names:
            try:
                channel = NotificationChannel(channel_name)
                channels.append(channel)
            except ValueError:
                continue  # Skip invalid channel names
        
        return channels if channels else [NotificationChannel.IN_APP]
    
    def _is_quiet_hours(self, user_email: str) -> bool:
        """Check if current time is within user's quiet hours"""
        
        # Get user preferences
        db_data = self._load_database()
        user_prefs = db_data['user_preferences'].get(user_email, {})
        
        quiet_hours = user_prefs.get('quiet_hours', self.notification_preferences['quiet_hours'])
        
        if not quiet_hours.get('enabled', False):
            return False
        
        try:
            now = datetime.now()
            current_time = now.time()
            
            start_time = datetime.strptime(quiet_hours['start_time'], '%H:%M').time()
            end_time = datetime.strptime(quiet_hours['end_time'], '%H:%M').time()
            
            # Handle overnight quiet hours (e.g., 22:00 to 07:00)
            if start_time > end_time:
                return current_time >= start_time or current_time <= end_time
            else:
                return start_time <= current_time <= end_time
                
        except Exception:
            return False
    
    def _defer_notification(self, notification: Dict[str, Any], 
                           channels: List[NotificationChannel]) -> Tuple[bool, str]:
        """Defer notification until after quiet hours"""
        
        # Calculate when to send the notification
        user_email = notification['user_email']
        db_data = self._load_database()
        user_prefs = db_data['user_preferences'].get(user_email, {})
        
        quiet_hours = user_prefs.get('quiet_hours', self.notification_preferences['quiet_hours'])
        end_time = datetime.strptime(quiet_hours['end_time'], '%H:%M').time()
        
        tomorrow = datetime.now().date() + timedelta(days=1)
        send_time = datetime.combine(tomorrow, end_time)
        
        # Add to deferred notifications
        deferred_notification = {
            **notification,
            'deferred': True,
            'send_at': send_time.isoformat(),
            'channels': [c.value for c in channels]
        }
        
        if 'deferred_notifications' not in db_data:
            db_data['deferred_notifications'] = []
        
        db_data['deferred_notifications'].append(deferred_notification)
        self._save_database(db_data)
        
        return True, f"Notification deferred until {send_time.strftime('%H:%M')}"
    
    def _send_via_channel(self, notification: Dict[str, Any], 
                         channel: NotificationChannel) -> Tuple[bool, str]:
        """Send notification via specific channel"""
        
        try:
            if channel == NotificationChannel.IN_APP:
                return self._send_in_app_notification(notification)
            elif channel == NotificationChannel.EMAIL:
                return self._send_email_notification(notification)
            elif channel == NotificationChannel.PUSH:
                return self._send_push_notification(notification)
            elif channel == NotificationChannel.SMS:
                return self._send_sms_notification(notification)
            else:
                return False, f"Unknown channel: {channel.value}"
                
        except Exception as e:
            return False, f"Error sending via {channel.value}: {str(e)}"
    
    def _send_in_app_notification(self, notification: Dict[str, Any]) -> Tuple[bool, str]:
        """Send in-app notification (store in database for UI display)"""
        
        # In-app notifications are stored in the database and displayed by the UI
        # This is already done in the main send_task_notification method
        print(f"IN-APP NOTIFICATION: {notification['title']} -> {notification['user_email']}")
        return True, "In-app notification queued"
    
    def _send_email_notification(self, notification: Dict[str, Any]) -> Tuple[bool, str]:
        """Send email notification (placeholder for email integration)"""
        
        # This would integrate with an email service (SMTP, SendGrid, etc.)
        print(f"EMAIL NOTIFICATION: {notification['title']} -> {notification['user_email']}")
        print(f"  Message: {notification['message']}")
        
        # Simulate email sending
        # In a real implementation, this would:
        # 1. Format email template
        # 2. Send via email service
        # 3. Handle delivery confirmation
        
        return True, "Email sent successfully"
    
    def _send_push_notification(self, notification: Dict[str, Any]) -> Tuple[bool, str]:
        """Send push notification (placeholder for mobile push integration)"""
        
        # This would integrate with push notification services (FCM, APNS, etc.)
        print(f"PUSH NOTIFICATION: {notification['title']} -> {notification['user_email']}")
        
        # For now, not implemented
        return False, "Push notifications not yet implemented"
    
    def _send_sms_notification(self, notification: Dict[str, Any]) -> Tuple[bool, str]:
        """Send SMS notification (placeholder for SMS integration)"""
        
        # This would integrate with SMS services (Twilio, etc.)
        print(f"SMS NOTIFICATION: {notification['title']} -> {notification['user_email']}")
        
        # For now, not implemented
        return False, "SMS notifications not yet implemented"
    
    def process_deferred_notifications(self) -> int:
        """Process deferred notifications that are ready to send"""
        
        db_data = self._load_database()
        deferred_notifications = db_data.get('deferred_notifications', [])
        
        if not deferred_notifications:
            return 0
        
        current_time = datetime.now()
        sent_count = 0
        remaining_notifications = []
        
        for notification in deferred_notifications:
            send_time = datetime.fromisoformat(notification['send_at'])
            
            if current_time >= send_time:
                # Time to send the notification
                channels = [NotificationChannel(c) for c in notification['channels']]
                
                # Remove deferred fields
                clean_notification = {k: v for k, v in notification.items() 
                                    if k not in ['deferred', 'send_at', 'channels']}
                
                # Send via each channel
                for channel in channels:
                    self._send_via_channel(clean_notification, channel)
                
                sent_count += 1
            else:
                # Keep for later
                remaining_notifications.append(notification)
        
        # Update database with remaining notifications
        db_data['deferred_notifications'] = remaining_notifications
        self._save_database(db_data)
        
        return sent_count
    
    def create_reminder_notifications(self, task: Dict[str, Any]) -> List[str]:
        """Create reminder notifications for task based on deadline and priority"""
        
        task_priority = TaskPriority(task.get('priority', TaskPriority.NORMAL.value))
        reminder_intervals = self.notification_preferences['reminder_intervals'][task_priority.value]
        
        deadline = datetime.fromisoformat(task['deadline'])
        created_reminders = []
        
        for interval in reminder_intervals:
            reminder_time = deadline - interval
            
            # Only create reminders for future times
            if reminder_time > datetime.now():
                # Create scheduled reminder
                reminder_notification = {
                    'notification_id': str(uuid.uuid4()),
                    'user_email': task['assigned_to'],
                    'task_id': task['task_id'],
                    'notification_type': NotificationType.TASK_REMINDER.value,
                    'scheduled_for': reminder_time.isoformat(),
                    'task_data': task
                }
                
                # Add to scheduled notifications
                db_data = self._load_database()
                if 'scheduled_notifications' not in db_data:
                    db_data['scheduled_notifications'] = []
                
                db_data['scheduled_notifications'].append(reminder_notification)
                self._save_database(db_data)
                
                created_reminders.append(reminder_notification['notification_id'])
        
        return created_reminders
    
    def process_scheduled_notifications(self) -> int:
        """Process scheduled notifications (reminders, etc.) that are due"""
        
        db_data = self._load_database()
        scheduled_notifications = db_data.get('scheduled_notifications', [])
        
        if not scheduled_notifications:
            return 0
        
        current_time = datetime.now()
        processed_count = 0
        remaining_notifications = []
        
        for scheduled_notification in scheduled_notifications:
            scheduled_time = datetime.fromisoformat(scheduled_notification['scheduled_for'])
            
            if current_time >= scheduled_time:
                # Time to send the notification
                task = scheduled_notification['task_data']
                notification_type = NotificationType(scheduled_notification['notification_type'])
                
                self.send_task_notification(
                    user_email=scheduled_notification['user_email'],
                    task=task,
                    notification_type=notification_type
                )
                
                processed_count += 1
            else:
                # Keep for later
                remaining_notifications.append(scheduled_notification)
        
        # Update database with remaining notifications
        db_data['scheduled_notifications'] = remaining_notifications
        self._save_database(db_data)
        
        return processed_count
    
    def get_user_notifications(self, user_email: str, 
                              unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for specific user"""
        
        db_data = self._load_database()
        user_notifications = []
        
        for notification in db_data['notifications']:
            if notification['user_email'] == user_email:
                if unread_only and notification.get('read', False):
                    continue
                
                user_notifications.append(notification)
        
        # Sort by creation time (newest first)
        user_notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        return user_notifications
    
    def mark_notification_read(self, notification_id: str, user_email: str) -> Tuple[bool, str]:
        """Mark notification as read"""
        
        db_data = self._load_database()
        
        for notification in db_data['notifications']:
            if (notification['notification_id'] == notification_id and 
                notification['user_email'] == user_email):
                
                notification['read'] = True
                notification['read_at'] = datetime.now().isoformat()
                
                self._save_database(db_data)
                return True, "Notification marked as read"
        
        return False, "Notification not found"
    
    def dismiss_notification(self, notification_id: str, user_email: str) -> Tuple[bool, str]:
        """Dismiss notification"""
        
        db_data = self._load_database()
        
        for notification in db_data['notifications']:
            if (notification['notification_id'] == notification_id and 
                notification['user_email'] == user_email):
                
                notification['dismissed'] = True
                notification['dismissed_at'] = datetime.now().isoformat()
                
                self._save_database(db_data)
                return True, "Notification dismissed"
        
        return False, "Notification not found"
    
    def update_user_preferences(self, user_email: str, 
                               preferences: Dict[str, Any]) -> Tuple[bool, str]:
        """Update user notification preferences"""
        
        try:
            db_data = self._load_database()
            
            if 'user_preferences' not in db_data:
                db_data['user_preferences'] = {}
            
            db_data['user_preferences'][user_email] = preferences
            self._save_database(db_data)
            
            return True, "Notification preferences updated"
            
        except Exception as e:
            return False, f"Error updating preferences: {str(e)}"
    
    def get_notification_statistics(self) -> Dict[str, Any]:
        """Get notification system statistics"""
        
        db_data = self._load_database()
        
        total_notifications = len(db_data['notifications'])
        unread_count = len([n for n in db_data['notifications'] if not n.get('read', False)])
        
        # Calculate delivery success rate
        delivery_logs = db_data.get('delivery_log', [])
        if delivery_logs:
            total_attempts = sum(log['total_attempts'] for log in delivery_logs)
            successful_deliveries = sum(log['success_count'] for log in delivery_logs)
            success_rate = (successful_deliveries / total_attempts * 100) if total_attempts > 0 else 100
        else:
            success_rate = 100
        
        return {
            'total_notifications': total_notifications,
            'unread_notifications': unread_count,
            'delivery_success_rate': round(success_rate, 2),
            'deferred_notifications': len(db_data.get('deferred_notifications', [])),
            'scheduled_notifications': len(db_data.get('scheduled_notifications', [])),
            'last_updated': db_data.get('last_updated')
        }

# Export main class
__all__ = [
    'TaskNotificationSystem', 
    'NotificationType', 
    'NotificationChannel', 
    'NotificationPriority'
]