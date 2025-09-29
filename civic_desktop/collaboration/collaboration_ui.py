# Collaboration UI - Inter-Jurisdictional Cooperation Interface
# PyQt5-based collaboration and working group management

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QProgressBar, QTextEdit, QTabWidget,
    QListWidget, QListWidgetItem, QSplitter, QGroupBox,
    QComboBox, QCheckBox, QSpinBox, QSlider, QMessageBox,
    QDialog, QDialogButtonBox, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
    QFormLayout, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QDate
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

# Import backend components
try:
    from collaboration.project_coordinator import InterJurisdictionalProjectManager, ResourceSharingManager
    from users.session import SessionManager
    from blockchain.blockchain import Blockchain
except ImportError as e:
    print(f"Warning: Import error in collaboration UI: {e}")


class ProjectCreationDialog(QDialog):
    """Dialog for creating new inter-jurisdictional projects"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Collaboration Project")
        self.setModal(True)
        self.resize(600, 500)
        self.project_data = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🤝 Create Inter-Jurisdictional Project")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # Form layout
        form = QFormLayout()
        
        # Project basics
        self.project_title = QLineEdit()
        self.project_title.setPlaceholderText("Enter project title...")
        form.addRow("Project Title:", self.project_title)
        
        self.project_type = QComboBox()
        self.project_type.addItems([
            "Resource Sharing",
            "Policy Coordination", 
            "Emergency Response",
            "Infrastructure Development",
            "Joint Service Delivery",
            "Research Collaboration",
            "Environmental Protection",
            "Economic Development"
        ])
        form.addRow("Project Type:", self.project_type)
        
        # Description
        self.description = QTextEdit()
        self.description.setPlaceholderText("Describe the project goals, scope, and expected outcomes...")
        self.description.setMaximumHeight(100)
        form.addRow("Description:", self.description)
        
        # Participating jurisdictions
        self.jurisdictions = QListWidget()
        self.jurisdictions.setSelectionMode(QListWidget.MultiSelection)
        
        # Add sample jurisdictions
        sample_jurisdictions = [
            "City of Springfield",
            "Metro County",
            "State of Illinois", 
            "Federal Emergency Management",
            "Regional Transit Authority",
            "State Environmental Agency"
        ]
        
        for jurisdiction in sample_jurisdictions:
            item = QListWidgetItem(jurisdiction)
            self.jurisdictions.addItem(item)
        
        form.addRow("Participating Jurisdictions:", self.jurisdictions)
        
        # Timeline
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        form.addRow("Start Date:", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(90))
        form.addRow("End Date:", self.end_date)
        
        # Budget estimate
        self.budget = QLineEdit()
        self.budget.setPlaceholderText("Enter estimated budget (optional)")
        form.addRow("Budget Estimate:", self.budget)
        
        # Priority level
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Normal", "High", "Critical"])
        self.priority.setCurrentText("Normal")
        form.addRow("Priority Level:", self.priority)
        
        layout.addLayout(form)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def accept(self):
        """Validate and collect project data"""
        
        if not self.project_title.text().strip():
            QMessageBox.warning(self, "Validation Error", "Project title is required.")
            return
        
        if not self.description.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Project description is required.")
            return
        
        selected_jurisdictions = [
            item.text() for item in self.jurisdictions.selectedItems()
        ]
        
        if len(selected_jurisdictions) < 2:
            QMessageBox.warning(self, "Validation Error", "At least 2 jurisdictions must be selected.")
            return
        
        self.project_data = {
            'title': self.project_title.text().strip(),
            'type': self.project_type.currentText(),
            'description': self.description.toPlainText().strip(),
            'participating_jurisdictions': selected_jurisdictions,
            'start_date': self.start_date.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date.date().toString("yyyy-MM-dd"),
            'budget_estimate': self.budget.text().strip(),
            'priority': self.priority.currentText(),
            'created_by': "current_user"  # Will be populated by parent
        }
        
        super().accept()


class ResourceSharingDialog(QDialog):
    """Dialog for creating resource sharing agreements"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Resource Sharing Agreement")
        self.setModal(True)
        self.resize(650, 600)
        self.agreement_data = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🔄 Create Resource Sharing Agreement")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # Form layout
        form = QFormLayout()
        
        # Agreement basics
        self.agreement_title = QLineEdit()
        self.agreement_title.setPlaceholderText("Enter agreement title...")
        form.addRow("Agreement Title:", self.agreement_title)
        
        self.resource_category = QComboBox()
        self.resource_category.addItems([
            "Personnel Sharing",
            "Equipment Sharing",
            "Facility Sharing",
            "Emergency Services",
            "Technology Resources",
            "Knowledge & Expertise",
            "Transportation Services",
            "Financial Resources"
        ])
        form.addRow("Resource Category:", self.resource_category)
        
        # Description
        self.description = QTextEdit()
        self.description.setPlaceholderText("Describe the resources, terms, and usage conditions...")
        self.description.setMaximumHeight(100)
        form.addRow("Description:", self.description)
        
        # Resource details
        resource_group = QGroupBox("Resource Details")
        resource_layout = QFormLayout()
        
        self.resource_type = QLineEdit()
        self.resource_type.setPlaceholderText("e.g., Fire trucks, IT specialists, Meeting rooms")
        resource_layout.addRow("Specific Resources:", self.resource_type)
        
        self.availability = QLineEdit()
        self.availability.setPlaceholderText("e.g., 24/7, Business hours, On-demand")
        resource_layout.addRow("Availability:", self.availability)
        
        self.capacity = QLineEdit()
        self.capacity.setPlaceholderText("e.g., 5 vehicles, 10 personnel, 200 seat capacity")
        resource_layout.addRow("Capacity/Quantity:", self.capacity)
        
        resource_group.setLayout(resource_layout)
        layout.addWidget(resource_group)
        
        # Cost allocation
        cost_group = QGroupBox("Cost Allocation")
        cost_layout = QFormLayout()
        
        self.cost_method = QComboBox()
        self.cost_method.addItems([
            "Usage-based billing",
            "Fixed monthly fee",
            "Reciprocal sharing",
            "Cost per incident",
            "Annual subscription",
            "No cost sharing"
        ])
        cost_layout.addRow("Billing Method:", self.cost_method)
        
        self.cost_rate = QLineEdit()
        self.cost_rate.setPlaceholderText("e.g., $50/hour, $500/month, No charge")
        cost_layout.addRow("Rate/Fee:", self.cost_rate)
        
        cost_group.setLayout(cost_layout)
        layout.addWidget(cost_group)
        
        # Participating entities
        participants_group = QGroupBox("Participating Entities")
        participants_layout = QVBoxLayout()
        
        self.participants = QListWidget()
        self.participants.setSelectionMode(QListWidget.MultiSelection)
        
        # Add sample participants
        sample_participants = [
            "City Emergency Services",
            "County Fire Department",
            "State Police",
            "Regional Hospital System",
            "Municipal IT Department",
            "County Public Works"
        ]
        
        for participant in sample_participants:
            item = QListWidgetItem(participant)
            self.participants.addItem(item)
        
        participants_layout.addWidget(self.participants)
        participants_group.setLayout(participants_layout)
        layout.addWidget(participants_group)
        
        # Agreement terms
        self.agreement_duration = QComboBox()
        self.agreement_duration.addItems([
            "6 months", "1 year", "2 years", "3 years", "5 years", "Indefinite"
        ])
        form.addRow("Agreement Duration:", self.agreement_duration)
        
        layout.addLayout(form)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def accept(self):
        """Validate and collect agreement data"""
        
        if not self.agreement_title.text().strip():
            QMessageBox.warning(self, "Validation Error", "Agreement title is required.")
            return
        
        if not self.description.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Agreement description is required.")
            return
        
        selected_participants = [
            item.text() for item in self.participants.selectedItems()
        ]
        
        if len(selected_participants) < 2:
            QMessageBox.warning(self, "Validation Error", "At least 2 participating entities must be selected.")
            return
        
        self.agreement_data = {
            'title': self.agreement_title.text().strip(),
            'category': self.resource_category.currentText(),
            'description': self.description.toPlainText().strip(),
            'resource_type': self.resource_type.text().strip(),
            'availability': self.availability.text().strip(),
            'capacity': self.capacity.text().strip(),
            'cost_method': self.cost_method.currentText(),
            'cost_rate': self.cost_rate.text().strip(),
            'participants': selected_participants,
            'duration': self.agreement_duration.currentText(),
            'created_by': "current_user"  # Will be populated by parent
        }
        
        super().accept()


class WorkingGroupWidget(QWidget):
    """Widget for managing working groups"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("👥 Working Groups")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        create_group_btn = QPushButton("➕ Create Working Group")
        create_group_btn.clicked.connect(self.create_working_group)
        header_layout.addWidget(create_group_btn)
        
        layout.addLayout(header_layout)
        
        # Working groups list
        self.groups_table = QTableWidget()
        self.groups_table.setColumnCount(6)
        self.groups_table.setHorizontalHeaderLabels([
            "Group Name", "Focus Area", "Members", "Status", "Last Activity", "Actions"
        ])
        
        # Sample working groups
        sample_groups = [
            {
                "name": "Regional Transportation Committee",
                "focus": "Transportation Planning",
                "members": 12,
                "status": "Active",
                "last_activity": "2024-01-15"
            },
            {
                "name": "Emergency Preparedness Task Force",
                "focus": "Emergency Response",
                "members": 8,
                "status": "Active", 
                "last_activity": "2024-01-10"
            },
            {
                "name": "Environmental Protection Working Group",
                "focus": "Environmental Policy",
                "members": 15,
                "status": "Planning",
                "last_activity": "2024-01-08"
            }
        ]
        
        self.groups_table.setRowCount(len(sample_groups))
        
        for i, group in enumerate(sample_groups):
            self.groups_table.setItem(i, 0, QTableWidgetItem(group["name"]))
            self.groups_table.setItem(i, 1, QTableWidgetItem(group["focus"]))
            self.groups_table.setItem(i, 2, QTableWidgetItem(str(group["members"])))
            self.groups_table.setItem(i, 3, QTableWidgetItem(group["status"]))
            self.groups_table.setItem(i, 4, QTableWidgetItem(group["last_activity"]))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QPushButton("👁️ View")
            view_btn.clicked.connect(lambda checked, name=group["name"]: self.view_group(name))
            actions_layout.addWidget(view_btn)
            
            join_btn = QPushButton("👤 Join")
            join_btn.clicked.connect(lambda checked, name=group["name"]: self.join_group(name))
            actions_layout.addWidget(join_btn)
            
            actions_widget.setLayout(actions_layout)
            self.groups_table.setCellWidget(i, 5, actions_widget)
        
        self.groups_table.resizeColumnsToContents()
        layout.addWidget(self.groups_table)
        
        self.setLayout(layout)
    
    def create_working_group(self):
        """Create a new working group"""
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Working Group")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Form
        form = QFormLayout()
        
        group_name = QLineEdit()
        group_name.setPlaceholderText("Enter group name...")
        form.addRow("Group Name:", group_name)
        
        focus_area = QComboBox()
        focus_area.addItems([
            "Transportation", "Emergency Response", "Environmental",
            "Economic Development", "Public Health", "Education",
            "Infrastructure", "Technology", "Public Safety"
        ])
        form.addRow("Focus Area:", focus_area)
        
        description = QTextEdit()
        description.setPlaceholderText("Describe the group's purpose and goals...")
        description.setMaximumHeight(100)
        form.addRow("Description:", description)
        
        layout.addLayout(form)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            if group_name.text().strip():
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Working group '{group_name.text()}' created successfully!"
                )
                # TODO: Add to table and save to backend
            else:
                QMessageBox.warning(self, "Error", "Group name is required.")
    
    def view_group(self, group_name):
        """View working group details"""
        
        QMessageBox.information(
            self,
            "Working Group Details",
            f"Viewing details for: {group_name}\n\n"
            "This would show:\n"
            "• Group members and roles\n"
            "• Recent activities and discussions\n"
            "• Shared documents and resources\n"
            "• Meeting schedules and minutes\n"
            "• Task assignments and progress"
        )
    
    def join_group(self, group_name):
        """Join a working group"""
        
        reply = QMessageBox.question(
            self,
            "Join Working Group",
            f"Do you want to join the working group: {group_name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                "Success",
                f"You have successfully joined: {group_name}"
            )


class CollaborationTab(QWidget):
    """Main Collaboration Tab widget"""
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.project_manager = None
        self.resource_manager = None
        self.init_ui()
        self.load_user_session()
    
    def init_ui(self):
        """Initialize the collaboration interface"""
        
        layout = QVBoxLayout()
        
        # Tab header
        header_layout = QHBoxLayout()
        
        title = QLabel("🤝 Inter-Jurisdictional Collaboration")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Quick action buttons
        new_project_btn = QPushButton("🚀 New Project")
        new_project_btn.clicked.connect(self.create_new_project)
        header_layout.addWidget(new_project_btn)
        
        new_agreement_btn = QPushButton("📋 New Agreement")
        new_agreement_btn.clicked.connect(self.create_resource_agreement)
        header_layout.addWidget(new_agreement_btn)
        
        layout.addLayout(header_layout)
        
        # Main content tabs
        self.content_tabs = QTabWidget()
        
        # Projects tab
        self.projects_tab = QWidget()
        self.init_projects_tab()
        self.content_tabs.addTab(self.projects_tab, "🚀 Projects")
        
        # Resource sharing tab
        self.resources_tab = QWidget()
        self.init_resources_tab()
        self.content_tabs.addTab(self.resources_tab, "🔄 Resource Sharing")
        
        # Working groups tab
        self.groups_tab = WorkingGroupWidget()
        self.content_tabs.addTab(self.groups_tab, "👥 Working Groups")
        
        # Dashboard tab
        self.dashboard_tab = QWidget()
        self.init_dashboard_tab()
        self.content_tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        
        layout.addWidget(self.content_tabs)
        
        self.setLayout(layout)
    
    def init_projects_tab(self):
        """Initialize the projects tab"""
        
        layout = QVBoxLayout()
        
        # Projects header
        header_layout = QHBoxLayout()
        
        header = QLabel("🚀 Inter-Jurisdictional Projects")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        filter_combo = QComboBox()
        filter_combo.addItems(["All Projects", "Active", "Planning", "Completed", "On Hold"])
        header_layout.addWidget(filter_combo)
        
        layout.addLayout(header_layout)
        
        # Projects table
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(7)
        self.projects_table.setHorizontalHeaderLabels([
            "Project Name", "Type", "Jurisdictions", "Status", "Progress", "Due Date", "Actions"
        ])
        
        # Sample projects
        sample_projects = [
            {
                "name": "Regional Transit Integration",
                "type": "Infrastructure",
                "jurisdictions": "City, County, State",
                "status": "Active",
                "progress": 65,
                "due_date": "2024-06-30"
            },
            {
                "name": "Emergency Response Coordination",
                "type": "Emergency Services",
                "jurisdictions": "3 Counties, State",
                "status": "Active",
                "progress": 40,
                "due_date": "2024-04-15"
            },
            {
                "name": "Joint Environmental Study",
                "type": "Research",
                "jurisdictions": "2 Cities, Federal",
                "status": "Planning",
                "progress": 15,
                "due_date": "2024-12-31"
            }
        ]
        
        self.projects_table.setRowCount(len(sample_projects))
        
        for i, project in enumerate(sample_projects):
            self.projects_table.setItem(i, 0, QTableWidgetItem(project["name"]))
            self.projects_table.setItem(i, 1, QTableWidgetItem(project["type"]))
            self.projects_table.setItem(i, 2, QTableWidgetItem(project["jurisdictions"]))
            self.projects_table.setItem(i, 3, QTableWidgetItem(project["status"]))
            
            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setValue(project["progress"])
            self.projects_table.setCellWidget(i, 4, progress_bar)
            
            self.projects_table.setItem(i, 5, QTableWidgetItem(project["due_date"]))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QPushButton("👁️ View")
            view_btn.clicked.connect(lambda checked, name=project["name"]: self.view_project(name))
            actions_layout.addWidget(view_btn)
            
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.clicked.connect(lambda checked, name=project["name"]: self.edit_project(name))
            actions_layout.addWidget(edit_btn)
            
            actions_widget.setLayout(actions_layout)
            self.projects_table.setCellWidget(i, 6, actions_widget)
        
        self.projects_table.resizeColumnsToContents()
        layout.addWidget(self.projects_table)
        
        self.projects_tab.setLayout(layout)
    
    def init_resources_tab(self):
        """Initialize the resource sharing tab"""
        
        layout = QVBoxLayout()
        
        # Resources header
        header_layout = QHBoxLayout()
        
        header = QLabel("🔄 Resource Sharing Agreements")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        category_filter = QComboBox()
        category_filter.addItems([
            "All Categories", "Personnel", "Equipment", "Facilities", 
            "Emergency Services", "Technology", "Financial"
        ])
        header_layout.addWidget(category_filter)
        
        layout.addLayout(header_layout)
        
        # Resources table
        self.resources_table = QTableWidget()
        self.resources_table.setColumnCount(6)
        self.resources_table.setHorizontalHeaderLabels([
            "Agreement Name", "Resource Type", "Participants", "Status", "Usage", "Actions"
        ])
        
        # Sample resource sharing agreements
        sample_resources = [
            {
                "name": "Emergency Vehicle Sharing",
                "type": "Equipment",
                "participants": "5 Fire Departments",
                "status": "Active",
                "usage": "High"
            },
            {
                "name": "IT Support Specialists",
                "type": "Personnel",
                "participants": "3 Cities",
                "status": "Active",
                "usage": "Medium"
            },
            {
                "name": "Conference Room Network",
                "type": "Facilities",
                "participants": "County, 2 Cities",
                "status": "Active",
                "usage": "Low"
            }
        ]
        
        self.resources_table.setRowCount(len(sample_resources))
        
        for i, resource in enumerate(sample_resources):
            self.resources_table.setItem(i, 0, QTableWidgetItem(resource["name"]))
            self.resources_table.setItem(i, 1, QTableWidgetItem(resource["type"]))
            self.resources_table.setItem(i, 2, QTableWidgetItem(resource["participants"]))
            self.resources_table.setItem(i, 3, QTableWidgetItem(resource["status"]))
            self.resources_table.setItem(i, 4, QTableWidgetItem(resource["usage"]))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QPushButton("👁️ View")
            view_btn.clicked.connect(lambda checked, name=resource["name"]: self.view_resource(name))
            actions_layout.addWidget(view_btn)
            
            use_btn = QPushButton("🔧 Use")
            use_btn.clicked.connect(lambda checked, name=resource["name"]: self.use_resource(name))
            actions_layout.addWidget(use_btn)
            
            actions_widget.setLayout(actions_layout)
            self.resources_table.setCellWidget(i, 5, actions_widget)
        
        self.resources_table.resizeColumnsToContents()
        layout.addWidget(self.resources_table)
        
        self.resources_tab.setLayout(layout)
    
    def init_dashboard_tab(self):
        """Initialize the collaboration dashboard"""
        
        layout = QVBoxLayout()
        
        # Dashboard header
        header = QLabel("📊 Collaboration Dashboard")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Metrics grid
        metrics_layout = QGridLayout()
        
        # Create metric cards
        metrics = [
            ("Active Projects", "5", "🚀"),
            ("Resource Agreements", "12", "🔄"),
            ("Working Groups", "8", "👥"),
            ("Cost Savings", "$125K", "💰"),
            ("Shared Resources", "23", "📦"),
            ("Collaboration Score", "87%", "📈")
        ]
        
        for i, (title, value, icon) in enumerate(metrics):
            card = self.create_metric_card(title, value, icon)
            row = i // 3
            col = i % 3
            metrics_layout.addWidget(card, row, col)
        
        layout.addLayout(metrics_layout)
        
        # Recent activity
        activity_group = QGroupBox("📋 Recent Activity")
        activity_layout = QVBoxLayout()
        
        activity_items = [
            "✅ Emergency Vehicle Sharing agreement activated",
            "🚀 Regional Transit Integration project milestone reached",
            "👥 New member joined Environmental Working Group",
            "📊 Monthly resource utilization report generated",
            "🔄 IT Support agreement renewed for 2 years"
        ]
        
        for item in activity_items:
            activity_label = QLabel(item)
            activity_layout.addWidget(activity_label)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        # Upcoming deadlines
        deadlines_group = QGroupBox("⏰ Upcoming Deadlines")
        deadlines_layout = QVBoxLayout()
        
        deadline_items = [
            "🚀 Emergency Response Coordination - Due: April 15",
            "📋 Quarterly resource review meeting - Due: March 30", 
            "👥 Environmental Working Group report - Due: April 5",
            "🔄 Equipment maintenance agreement renewal - Due: May 1"
        ]
        
        for item in deadline_items:
            deadline_label = QLabel(item)
            deadlines_layout.addWidget(deadline_label)
        
        deadlines_group.setLayout(deadlines_layout)
        layout.addWidget(deadlines_group)
        
        self.dashboard_tab.setLayout(layout)
    
    def create_metric_card(self, title, value, icon):
        """Create a metric display card"""
        
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 5px; padding: 10px; }")
        
        layout = QVBoxLayout()
        
        # Icon and value
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 20))
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(value_label)
        
        layout.addLayout(header_layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        layout.addWidget(title_label)
        
        card.setLayout(layout)
        return card
    
    def load_user_session(self):
        """Load current user session"""
        
        try:
            # self.current_user = SessionManager.get_current_user()
            # Mock current user for testing
            self.current_user = {
                'email': 'test@example.com',
                'role': 'Contract Representative',
                'jurisdiction': 'City of Springfield'
            }
            
            if self.current_user:
                self.init_backend_managers()
        except Exception as e:
            print(f"Error loading user session: {e}")
    
    def init_backend_managers(self):
        """Initialize backend management systems"""
        
        try:
            # self.project_manager = InterJurisdictionalProjectManager()
            # self.resource_manager = ResourceSharingManager()
            print("Backend managers would be initialized here")
        except Exception as e:
            print(f"Error initializing backend managers: {e}")
    
    def create_new_project(self):
        """Create a new inter-jurisdictional project"""
        
        if not self.current_user:
            QMessageBox.warning(self, "Authentication Required", 
                               "Please log in to create projects.")
            return
        
        dialog = ProjectCreationDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            project_data = dialog.project_data
            project_data['created_by'] = self.current_user.get('email')
            
            try:
                # TODO: Use actual project manager
                # success, message = self.project_manager.initiate_collaboration_project(
                #     self.current_user.get('email'), project_data
                # )
                success, message = True, "Project created successfully"
                
                if success:
                    QMessageBox.information(self, "Success", 
                                          f"Project '{project_data['title']}' created successfully!")
                    # Refresh projects table
                    # self.refresh_projects_table()
                else:
                    QMessageBox.warning(self, "Error", message)
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
    
    def create_resource_agreement(self):
        """Create a new resource sharing agreement"""
        
        if not self.current_user:
            QMessageBox.warning(self, "Authentication Required", 
                               "Please log in to create agreements.")
            return
        
        dialog = ResourceSharingDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            agreement_data = dialog.agreement_data
            agreement_data['created_by'] = self.current_user.get('email')
            
            try:
                # TODO: Use actual resource manager
                # success, message = self.resource_manager.create_resource_sharing_agreement(
                #     self.current_user.get('email'), agreement_data
                # )
                success, message = True, "Agreement created successfully"
                
                if success:
                    QMessageBox.information(self, "Success", 
                                          f"Agreement '{agreement_data['title']}' created successfully!")
                    # Refresh resources table
                    # self.refresh_resources_table()
                else:
                    QMessageBox.warning(self, "Error", message)
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create agreement: {e}")
    
    def view_project(self, project_name):
        """View project details"""
        
        QMessageBox.information(
            self,
            "Project Details",
            f"Viewing project: {project_name}\n\n"
            "This would show:\n"
            "• Project timeline and milestones\n"
            "• Participating jurisdictions and roles\n"
            "• Budget and resource allocation\n"
            "• Progress reports and updates\n"
            "• Communication and documents\n"
            "• Risk assessments and issues"
        )
    
    def edit_project(self, project_name):
        """Edit project details"""
        
        QMessageBox.information(
            self,
            "Edit Project",
            f"Editing project: {project_name}\n\n"
            "This would allow:\n"
            "• Updating project timeline\n"
            "• Modifying participant roles\n"
            "• Adjusting budget allocations\n"
            "• Adding new milestones\n"
            "• Updating status and progress\n"
            "• Managing risks and issues"
        )
    
    def view_resource(self, resource_name):
        """View resource agreement details"""
        
        QMessageBox.information(
            self,
            "Resource Agreement",
            f"Viewing agreement: {resource_name}\n\n"
            "This would show:\n"
            "• Resource specifications and capacity\n"
            "• Usage terms and conditions\n"
            "• Cost allocation and billing\n"
            "• Participating entities\n"
            "• Usage history and analytics\n"
            "• Performance metrics"
        )
    
    def use_resource(self, resource_name):
        """Request to use a shared resource"""
        
        reply = QMessageBox.question(
            self,
            "Resource Request",
            f"Request to use: {resource_name}\n\n"
            "This would:\n"
            "• Check resource availability\n"
            "• Submit usage request\n"
            "• Notify resource owners\n"
            "• Schedule usage time\n"
            "• Track usage and costs\n\n"
            "Continue with request?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                "Request Submitted",
                f"Resource request for '{resource_name}' has been submitted.\n\n"
                "You will receive confirmation and scheduling details shortly."
            )


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    collaboration_tab = CollaborationTab()
    collaboration_tab.show()
    
    sys.exit(app.exec_())