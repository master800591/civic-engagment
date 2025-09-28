# Task User Interface - Dashboard and Management Interface
# PyQt5-based task management interface for civic engagement platform

import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QGroupBox, QProgressBar, QComboBox, QLineEdit, QTextEdit, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout, QSpinBox, QDateTimeEdit, 
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QFrame, QSplitter, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDateTime
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QIcon

# Import task management components
from tasks.task_manager import TaskManager, Task
from tasks.task_types import (
    TaskType, TaskCategory, TaskPriority, TaskStatus, ValidationLevel, 
    TaskTypeManager, TaskTemplate
)

class TaskDashboard(QWidget):
    """Main task dashboard interface"""
    
    # Signals for task actions
    task_completed = pyqtSignal(str)  # task_id
    task_deferred = pyqtSignal(str)   # task_id
    task_updated = pyqtSignal()       # General update signal
    
    def __init__(self):
        super().__init__()
        self.task_manager = TaskManager()
        self.current_user = self.get_current_user()
        self.auto_refresh_timer = QTimer()
        
        # Initialize UI
        self.init_ui()
        
        # Set up auto-refresh for task updates
        self.auto_refresh_timer.timeout.connect(self.refresh_tasks)
        self.auto_refresh_timer.start(30000)  # Refresh every 30 seconds
        
        # Initial data load
        self.refresh_tasks()
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user from session manager"""
        try:
            # Import here to avoid circular dependencies
            from users.session import SessionManager
            return SessionManager.get_current_user()
        except ImportError:
            # Fallback for testing
            return {
                'email': 'test@example.com',
                'role': 'contract_member',
                'name': 'Test User'
            }
    
    def init_ui(self):
        """Initialize the task dashboard UI"""
        self.setWindowTitle("📋 Task Management Dashboard")
        self.setMinimumSize(1000, 700)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header section
        self.create_header_section(main_layout)
        
        # Content splitter (left panel + right panel)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Task list and filters
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Task details and actions
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (70% left, 30% right)
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.create_status_bar(main_layout)
        
        self.setLayout(main_layout)
        
        # Apply styles
        self.apply_styles()
    
    def create_header_section(self, layout):
        """Create header with task summary and quick actions"""
        
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        
        # Title and user info
        title_layout = QHBoxLayout()
        
        title_label = QLabel("📋 Task Management Dashboard")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        user_label = QLabel(f"👤 {self.current_user.get('name', 'User')} ({self.current_user.get('role', 'Member').replace('_', ' ').title()})")
        user_label.setFont(QFont("Arial", 10))
        title_layout.addWidget(user_label)
        
        header_layout.addLayout(title_layout)
        
        # Task summary cards
        self.summary_layout = QHBoxLayout()
        header_layout.addLayout(self.summary_layout)
        
        # Quick action buttons
        actions_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_tasks)
        actions_layout.addWidget(refresh_btn)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Tasks", "Pending", "In Progress", "High Priority", 
            "Validation Tasks", "Voting Tasks", "Contract Tasks"
        ])
        self.filter_combo.currentTextChanged.connect(self.filter_tasks)
        actions_layout.addWidget(self.filter_combo)
        
        actions_layout.addStretch()
        
        header_layout.addLayout(actions_layout)
        
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)
    
    def create_left_panel(self) -> QWidget:
        """Create left panel with task list"""
        
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # Tasks list header
        list_header = QLabel("📋 Your Tasks")
        list_header.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(list_header)
        
        # Task search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search tasks...")
        self.search_input.textChanged.connect(self.filter_tasks)
        search_layout.addWidget(self.search_input)
        
        left_layout.addLayout(search_layout)
        
        # Task list scroll area
        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tasks_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.tasks_widget = QWidget()
        self.tasks_layout = QVBoxLayout()
        self.tasks_widget.setLayout(self.tasks_layout)
        self.tasks_scroll.setWidget(self.tasks_widget)
        
        left_layout.addWidget(self.tasks_scroll)
        
        left_widget.setLayout(left_layout)
        return left_widget
    
    def create_right_panel(self) -> QWidget:
        """Create right panel with task details and actions"""
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Task details header
        details_header = QLabel("ℹ️ Task Details")
        details_header.setFont(QFont("Arial", 14, QFont.Bold))
        right_layout.addWidget(details_header)
        
        # Task details area
        self.details_area = QTextEdit()
        self.details_area.setReadOnly(True)
        self.details_area.setMaximumHeight(200)
        right_layout.addWidget(self.details_area)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()
        
        self.complete_btn = QPushButton("✅ Complete Task")
        self.complete_btn.clicked.connect(self.complete_selected_task)
        self.complete_btn.setEnabled(False)
        actions_layout.addWidget(self.complete_btn)
        
        self.defer_btn = QPushButton("⏸️ Defer Task")
        self.defer_btn.clicked.connect(self.defer_selected_task)
        self.defer_btn.setEnabled(False)
        actions_layout.addWidget(self.defer_btn)
        
        self.view_details_btn = QPushButton("👀 View Full Details")
        self.view_details_btn.clicked.connect(self.view_task_details)
        self.view_details_btn.setEnabled(False)
        actions_layout.addWidget(self.view_details_btn)
        
        actions_group.setLayout(actions_layout)
        right_layout.addWidget(actions_group)
        
        # Task statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("Loading statistics...")
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        right_layout.addStretch()
        
        right_widget.setLayout(right_layout)
        return right_widget
    
    def create_status_bar(self, layout):
        """Create status bar with last update time"""
        
        status_widget = QWidget()
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.last_update_label = QLabel("Last updated: Never")
        status_layout.addWidget(self.last_update_label)
        
        status_widget.setLayout(status_layout)
        layout.addWidget(status_widget)
    
    def create_task_summary_cards(self):
        """Create task summary cards showing counts"""
        
        # Clear existing cards
        for i in reversed(range(self.summary_layout.count())):
            child = self.summary_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get user tasks
        user_tasks = self.task_manager.get_user_tasks(self.current_user['email'])
        
        # Calculate counts
        pending_count = len([t for t in user_tasks if t['status'] == TaskStatus.PENDING.value])
        urgent_count = len([t for t in user_tasks if t['priority'] == TaskPriority.URGENT.value])
        overdue_count = len([t for t in user_tasks if self.is_overdue(t)])
        completed_today = len([t for t in user_tasks if self.completed_today(t)])
        
        # Create cards
        self.create_summary_card("📋 Pending", pending_count, "#3498db")
        self.create_summary_card("🚨 Urgent", urgent_count, "#e74c3c")
        self.create_summary_card("⏰ Overdue", overdue_count, "#f39c12")
        self.create_summary_card("✅ Today", completed_today, "#27ae60")
    
    def create_summary_card(self, title: str, count: int, color: str):
        """Create individual summary card"""
        
        card = QGroupBox()
        card.setMaximumWidth(150)
        card.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {color};
                border-radius: 10px;
                padding: 10px;
                background-color: white;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        count_label = QLabel(str(count))
        count_label.setFont(QFont("Arial", 24, QFont.Bold))
        count_label.setAlignment(Qt.AlignCenter)
        count_label.setStyleSheet(f"color: {color};")
        layout.addWidget(count_label)
        
        card.setLayout(layout)
        self.summary_layout.addWidget(card)
    
    def refresh_tasks(self):
        """Refresh task list and update UI"""
        
        try:
            # Update summary cards
            self.create_task_summary_cards()
            
            # Update task list
            self.update_task_list()
            
            # Update statistics
            self.update_statistics()
            
            # Update status
            self.status_label.setText("✅ Tasks refreshed")
            self.last_update_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error refreshing: {str(e)}")
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing tasks: {str(e)}")
    
    def update_task_list(self):
        """Update the task list display"""
        
        # Clear existing task cards
        for i in reversed(range(self.tasks_layout.count())):
            child = self.tasks_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get user tasks
        user_tasks = self.task_manager.get_user_tasks(self.current_user['email'])
        
        # Apply current filters
        filtered_tasks = self.apply_current_filters(user_tasks)
        
        # Create task cards
        for task in filtered_tasks:
            task_card = self.create_task_card(task)
            self.tasks_layout.addWidget(task_card)
        
        # Add stretch to push cards to top
        self.tasks_layout.addStretch()
        
        # Update selected task if no tasks
        if not filtered_tasks:
            self.selected_task = None
            self.update_task_details(None)
    
    def create_task_card(self, task: Dict[str, Any]) -> QWidget:
        """Create individual task card widget"""
        
        card = QGroupBox()
        card.setMaximumHeight(200)
        card.setStyleSheet(self.get_task_card_style(task))
        
        layout = QVBoxLayout()
        
        # Task header
        header_layout = QHBoxLayout()
        
        # Task icon and title
        display_info = TaskTypeManager.get_task_display_info(TaskType(task['task_type']))
        title = QLabel(f"{display_info['icon']} {display_info['name']}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Priority indicator
        priority_label = QLabel(f"🔥 {task['priority'].title()}")
        priority_label.setStyleSheet(f"color: {self.get_priority_color(task['priority'])};")
        header_layout.addWidget(priority_label)
        
        layout.addLayout(header_layout)
        
        # Task description
        description = self.format_task_description(task)
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(60)
        layout.addWidget(desc_label)
        
        # Progress bar
        progress = QProgressBar()
        progress.setValue(task['completion_percentage'])
        layout.addWidget(progress)
        
        # Deadline info
        deadline_layout = QHBoxLayout()
        
        deadline_text = self.format_deadline(task['deadline'])
        deadline_label = QLabel(f"⏰ {deadline_text}")
        deadline_layout.addWidget(deadline_label)
        
        deadline_layout.addStretch()
        
        time_remaining = self.calculate_time_remaining(task['deadline'])
        time_label = QLabel(f"⏳ {time_remaining}")
        if self.is_overdue(task):
            time_label.setStyleSheet("color: red; font-weight: bold;")
        deadline_layout.addWidget(time_label)
        
        layout.addLayout(deadline_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("📋 Select")
        select_btn.clicked.connect(lambda: self.select_task(task))
        button_layout.addWidget(select_btn)
        
        if task['task_type'] == TaskType.BLOCKCHAIN_VALIDATION.value:
            validate_btn = QPushButton("🔍 Validate")
            validate_btn.clicked.connect(lambda: self.open_validation_interface(task))
            button_layout.addWidget(validate_btn)
        elif task['task_type'] == TaskType.VOTING_OPPORTUNITY.value:
            vote_btn = QPushButton("🗳️ Vote")
            vote_btn.clicked.connect(lambda: self.open_voting_interface(task))
            button_layout.addWidget(vote_btn)
        elif task['task_type'] == TaskType.CONTRACT_REVIEW.value:
            review_btn = QPushButton("⚖️ Review")
            review_btn.clicked.connect(lambda: self.open_contract_interface(task))
            button_layout.addWidget(review_btn)
        
        layout.addLayout(button_layout)
        
        card.setLayout(layout)
        return card
    
    def select_task(self, task: Dict[str, Any]):
        """Select task and update details panel"""
        
        self.selected_task = task
        self.update_task_details(task)
        
        # Enable action buttons
        self.complete_btn.setEnabled(True)
        self.defer_btn.setEnabled(task.get('data', {}).get('can_be_deferred', True))
        self.view_details_btn.setEnabled(True)
        
        self.status_label.setText(f"Selected task: {task['task_type']}")
    
    def update_task_details(self, task: Optional[Dict[str, Any]]):
        """Update task details panel"""
        
        if not task:
            self.details_area.setText("No task selected")
            return
        
        details_text = f"""
        <h3>{TaskTypeManager.get_task_display_info(TaskType(task['task_type']))['icon']} {task['task_type'].replace('_', ' ').title()}</h3>
        
        <b>Status:</b> {task['status'].title()}<br>
        <b>Priority:</b> {task['priority'].title()}<br>
        <b>Created:</b> {self.format_datetime(task['created_at'])}<br>
        <b>Deadline:</b> {self.format_datetime(task['deadline'])}<br>
        <b>Progress:</b> {task['completion_percentage']}%<br>
        
        <br><b>Task Data:</b><br>
        {self.format_task_data(task['data'])}
        
        <br><b>Rewards:</b><br>
        {task['rewards'].get('reward_amount', 0)} {task['rewards'].get('reward_type', 'points')}
        """
        
        self.details_area.setHtml(details_text)
    
    def complete_selected_task(self):
        """Complete the currently selected task"""
        
        if not hasattr(self, 'selected_task') or not self.selected_task:
            QMessageBox.warning(self, "No Selection", "Please select a task to complete.")
            return
        
        # Show completion dialog
        dialog = TaskCompletionDialog(self.selected_task, self)
        if dialog.exec_() == QDialog.Accepted:
            completion_data = dialog.get_completion_data()
            
            success, message = self.task_manager.complete_task(
                self.selected_task['task_id'],
                self.current_user['email'],
                completion_data
            )
            
            if success:
                QMessageBox.information(self, "Task Completed", message)
                self.task_completed.emit(self.selected_task['task_id'])
                self.refresh_tasks()
            else:
                QMessageBox.warning(self, "Completion Failed", message)
    
    def defer_selected_task(self):
        """Defer the currently selected task"""
        
        if not hasattr(self, 'selected_task') or not self.selected_task:
            QMessageBox.warning(self, "No Selection", "Please select a task to defer.")
            return
        
        # Show deferral dialog
        dialog = TaskDeferralDialog(self.selected_task, self)
        if dialog.exec_() == QDialog.Accepted:
            reason, new_deadline = dialog.get_deferral_data()
            
            success, message = self.task_manager.defer_task(
                self.selected_task['task_id'],
                self.current_user['email'],
                reason,
                new_deadline
            )
            
            if success:
                QMessageBox.information(self, "Task Deferred", message)
                self.task_deferred.emit(self.selected_task['task_id'])
                self.refresh_tasks()
            else:
                QMessageBox.warning(self, "Deferral Failed", message)
    
    def view_task_details(self):
        """Open detailed task view dialog"""
        
        if not hasattr(self, 'selected_task') or not self.selected_task:
            QMessageBox.warning(self, "No Selection", "Please select a task to view.")
            return
        
        dialog = TaskDetailsDialog(self.selected_task, self)
        dialog.exec_()
    
    # Task action interfaces
    def open_validation_interface(self, task: Dict[str, Any]):
        """Open blockchain validation interface"""
        # This would open the validation module interface
        QMessageBox.information(self, "Validation", "Opening blockchain validation interface...")
    
    def open_voting_interface(self, task: Dict[str, Any]):
        """Open voting interface"""
        # This would open the voting module interface
        QMessageBox.information(self, "Voting", "Opening voting interface...")
    
    def open_contract_interface(self, task: Dict[str, Any]):
        """Open contract review interface"""
        # This would open the contracts module interface
        QMessageBox.information(self, "Contract Review", "Opening contract review interface...")
    
    # Utility methods
    def apply_current_filters(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply current filter settings to task list"""
        
        filter_text = self.filter_combo.currentText()
        search_text = self.search_input.text().lower()
        
        filtered_tasks = tasks
        
        # Apply category/status filters
        if filter_text == "Pending":
            filtered_tasks = [t for t in filtered_tasks if t['status'] == TaskStatus.PENDING.value]
        elif filter_text == "In Progress":
            filtered_tasks = [t for t in filtered_tasks if t['status'] == TaskStatus.IN_PROGRESS.value]
        elif filter_text == "High Priority":
            filtered_tasks = [t for t in filtered_tasks if t['priority'] in [TaskPriority.HIGH.value, TaskPriority.URGENT.value]]
        elif filter_text == "Validation Tasks":
            filtered_tasks = [t for t in filtered_tasks if t['category'] == TaskCategory.VALIDATION.value]
        elif filter_text == "Voting Tasks":
            filtered_tasks = [t for t in filtered_tasks if t['category'] == TaskCategory.VOTING.value]
        elif filter_text == "Contract Tasks":
            filtered_tasks = [t for t in filtered_tasks if t['category'] == TaskCategory.CONTRACTS.value]
        
        # Apply search filter
        if search_text:
            filtered_tasks = [
                t for t in filtered_tasks
                if (search_text in t['task_type'].lower() or 
                    search_text in str(t.get('data', {})).lower())
            ]
        
        return filtered_tasks
    
    def filter_tasks(self):
        """Apply filters and update task list"""
        self.update_task_list()
    
    def update_statistics(self):
        """Update task statistics display"""
        
        stats = self.task_manager.get_task_statistics()
        
        stats_text = f"""
        Total Tasks: {stats['total_tasks']}<br>
        Completion Rate: {stats['completion_rate']:.1f}%<br>
        Avg Completion: {stats['average_completion_hours']:.1f} hours<br>
        """
        
        self.stats_label.setText(stats_text)
    
    # Formatting and utility methods
    def is_overdue(self, task: Dict[str, Any]) -> bool:
        """Check if task is overdue"""
        deadline = datetime.fromisoformat(task['deadline'])
        return datetime.now() > deadline and task['status'] not in [TaskStatus.COMPLETED.value, TaskStatus.EXPIRED.value]
    
    def completed_today(self, task: Dict[str, Any]) -> bool:
        """Check if task was completed today"""
        if task['status'] != TaskStatus.COMPLETED.value or 'completed_at' not in task:
            return False
        
        completed = datetime.fromisoformat(task['completed_at'])
        return completed.date() == datetime.now().date()
    
    def format_deadline(self, deadline_str: str) -> str:
        """Format deadline for display"""
        deadline = datetime.fromisoformat(deadline_str)
        return deadline.strftime("%Y-%m-%d %H:%M")
    
    def format_datetime(self, datetime_str: str) -> str:
        """Format datetime for display"""
        dt = datetime.fromisoformat(datetime_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    
    def calculate_time_remaining(self, deadline_str: str) -> str:
        """Calculate and format time remaining until deadline"""
        deadline = datetime.fromisoformat(deadline_str)
        remaining = deadline - datetime.now()
        
        if remaining.total_seconds() < 0:
            return "Overdue"
        
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h"
        else:
            return "< 1h"
    
    def format_task_description(self, task: Dict[str, Any]) -> str:
        """Format task description for card display"""
        task_type_config = TaskTypeManager.get_task_config(TaskType(task['task_type']))
        base_description = task_type_config.get('description', 'Civic engagement task')
        
        # Add specific details based on task type
        if task['task_type'] == TaskType.BLOCKCHAIN_VALIDATION.value:
            validation_level = task['data'].get('validation_level', 'unknown')
            return f"{base_description} ({validation_level} level)"
        elif task['task_type'] == TaskType.VOTING_OPPORTUNITY.value:
            election_type = task['data'].get('election_type', 'general')
            return f"{base_description} ({election_type} election)"
        elif task['task_type'] == TaskType.CONTRACT_REVIEW.value:
            amendment_type = task['data'].get('amendment_type', 'constitutional')
            return f"{base_description} ({amendment_type})"
        
        return base_description
    
    def format_task_data(self, data: Dict[str, Any]) -> str:
        """Format task data for details display"""
        formatted_items = []
        
        for key, value in data.items():
            if key in ['deferral_history', 'notifications_sent']:
                continue  # Skip complex data
            
            formatted_key = key.replace('_', ' ').title()
            formatted_value = str(value)[:100]  # Truncate long values
            
            formatted_items.append(f"<b>{formatted_key}:</b> {formatted_value}")
        
        return "<br>".join(formatted_items) if formatted_items else "No additional data"
    
    def get_priority_color(self, priority: str) -> str:
        """Get color for priority level"""
        colors = {
            TaskPriority.LOW.value: "#95a5a6",
            TaskPriority.NORMAL.value: "#3498db",
            TaskPriority.HIGH.value: "#f39c12",
            TaskPriority.URGENT.value: "#e74c3c",
            TaskPriority.CRITICAL.value: "#8e44ad"
        }
        return colors.get(priority, "#3498db")
    
    def get_task_card_style(self, task: Dict[str, Any]) -> str:
        """Get CSS style for task card based on task properties"""
        
        base_style = """
            QGroupBox {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
                background-color: white;
            }
        """
        
        # Override border color for priority/status
        if self.is_overdue(task):
            return base_style.replace("#bdc3c7", "#e74c3c")
        elif task['priority'] == TaskPriority.URGENT.value:
            return base_style.replace("#bdc3c7", "#f39c12")
        elif task['status'] == TaskStatus.COMPLETED.value:
            return base_style.replace("#bdc3c7", "#27ae60")
        
        return base_style
    
    def apply_styles(self):
        """Apply custom styles to the dashboard"""
        
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QGroupBox {
                font-weight: bold;
                padding-top: 15px;
            }
            
            QPushButton {
                padding: 8px 16px;
                border: 2px solid #3498db;
                border-radius: 4px;
                background-color: #ecf0f1;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
            
            QPushButton:pressed {
                background-color: #2980b9;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
                border-color: #95a5a6;
                color: #7f8c8d;
            }
            
            QComboBox {
                padding: 5px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
            }
            
            QLineEdit {
                padding: 5px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
            }
            
            QScrollArea {
                border: none;
            }
        """)


class TaskCompletionDialog(QDialog):
    """Dialog for task completion with optional data entry"""
    
    def __init__(self, task: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.task = task
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Complete Task")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Task info
        info_label = QLabel(f"Completing: {self.task['task_type'].replace('_', ' ').title()}")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(info_label)
        
        # Completion notes
        layout.addWidget(QLabel("Completion Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        layout.addWidget(self.notes_input)
        
        # Additional fields based on task type
        if self.task['task_type'] == TaskType.BLOCKCHAIN_VALIDATION.value:
            layout.addWidget(QLabel("Validation Decision:"))
            self.validation_decision = QComboBox()
            self.validation_decision.addItems(["Approve", "Reject", "Request Changes"])
            layout.addWidget(self.validation_decision)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_completion_data(self) -> Dict[str, Any]:
        """Get completion data from dialog"""
        data = {
            'completion_notes': self.notes_input.toPlainText()
        }
        
        if hasattr(self, 'validation_decision'):
            data['validation_decision'] = self.validation_decision.currentText()
        
        return data


class TaskDeferralDialog(QDialog):
    """Dialog for task deferral with reason and new deadline"""
    
    def __init__(self, task: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.task = task
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Defer Task")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Task info
        info_label = QLabel(f"Deferring: {self.task['task_type'].replace('_', ' ').title()}")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(info_label)
        
        # Deferral reason
        layout.addWidget(QLabel("Reason for deferral:"))
        self.reason_input = QTextEdit()
        self.reason_input.setMaximumHeight(80)
        layout.addWidget(self.reason_input)
        
        # New deadline
        layout.addWidget(QLabel("New deadline:"))
        self.new_deadline = QDateTimeEdit()
        self.new_deadline.setCalendarPopup(True)
        
        # Set minimum to current deadline + 1 hour
        current_deadline = datetime.fromisoformat(self.task['deadline'])
        self.new_deadline.setMinimumDateTime(QDateTime.fromString(
            (current_deadline + timedelta(hours=1)).isoformat(), Qt.ISODate
        ))
        
        # Default to +24 hours
        self.new_deadline.setDateTime(QDateTime.fromString(
            (current_deadline + timedelta(hours=24)).isoformat(), Qt.ISODate
        ))
        
        layout.addWidget(self.new_deadline)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_deferral_data(self) -> tuple:
        """Get deferral data from dialog"""
        reason = self.reason_input.toPlainText()
        new_deadline = self.new_deadline.dateTime().toPyDateTime()
        return reason, new_deadline


class TaskDetailsDialog(QDialog):
    """Dialog showing complete task details"""
    
    def __init__(self, task: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.task = task
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Task Details")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Task header
        header = QLabel(f"{TaskTypeManager.get_task_display_info(TaskType(self.task['task_type']))['icon']} {self.task['task_type'].replace('_', ' ').title()}")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # Details text
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        
        # Format complete task details
        details_html = f"""
        <h3>Task Information</h3>
        <table>
            <tr><td><b>Task ID:</b></td><td>{self.task['task_id']}</td></tr>
            <tr><td><b>Type:</b></td><td>{self.task['task_type']}</td></tr>
            <tr><td><b>Category:</b></td><td>{self.task['category']}</td></tr>
            <tr><td><b>Status:</b></td><td>{self.task['status']}</td></tr>
            <tr><td><b>Priority:</b></td><td>{self.task['priority']}</td></tr>
            <tr><td><b>Progress:</b></td><td>{self.task['completion_percentage']}%</td></tr>
            <tr><td><b>Created:</b></td><td>{datetime.fromisoformat(self.task['created_at']).strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
            <tr><td><b>Deadline:</b></td><td>{datetime.fromisoformat(self.task['deadline']).strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
        </table>
        
        <h3>Task Data</h3>
        {self.format_detailed_data()}
        
        <h3>Rewards</h3>
        <b>Type:</b> {self.task['rewards'].get('reward_type', 'None')}<br>
        <b>Amount:</b> {self.task['rewards'].get('reward_amount', 0)}<br>
        
        <h3>Notifications</h3>
        {self.format_notifications()}
        """
        
        details_text.setHtml(details_html)
        layout.addWidget(details_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def format_detailed_data(self) -> str:
        """Format detailed task data"""
        data_html = "<table>"
        
        for key, value in self.task['data'].items():
            formatted_key = key.replace('_', ' ').title()
            
            if isinstance(value, list):
                formatted_value = "<br>".join([f"• {item}" for item in value])
            elif isinstance(value, dict):
                formatted_value = "<br>".join([f"<b>{k}:</b> {v}" for k, v in value.items()])
            else:
                formatted_value = str(value)
            
            data_html += f"<tr><td><b>{formatted_key}:</b></td><td>{formatted_value}</td></tr>"
        
        data_html += "</table>"
        return data_html
    
    def format_notifications(self) -> str:
        """Format notification history"""
        notifications = self.task.get('notifications_sent', [])
        
        if not notifications:
            return "No notifications sent"
        
        notifications_html = "<ul>"
        for notification in notifications:
            notifications_html += f"<li><b>{notification.get('type', 'Unknown')}:</b> {notification.get('message', 'No message')} ({notification.get('sent_at', 'Unknown time')})</li>"
        notifications_html += "</ul>"
        
        return notifications_html

# Export main class
__all__ = ['TaskDashboard', 'TaskCompletionDialog', 'TaskDeferralDialog', 'TaskDetailsDialog']