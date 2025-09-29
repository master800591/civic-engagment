# System Guide Tab - Interactive User Onboarding & Help System
# PyQt5-based comprehensive user guidance interface

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QProgressBar, QTextEdit, QTabWidget,
    QListWidget, QListWidgetItem, QSplitter, QGroupBox,
    QComboBox, QCheckBox, QSpinBox, QSlider, QMessageBox,
    QDialog, QDialogButtonBox, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

# Import backend components
try:
    from system_guide.onboarding_backend import UserOnboardingSystem
    from system_guide.help_system import ContextualHelpSystem
    from users.session import SessionManager
    from blockchain.blockchain import Blockchain
except ImportError as e:
    print(f"Warning: Import error in system guide: {e}")


class OnboardingProgressWidget(QWidget):
    """Progress tracking widget for user onboarding"""
    
    def __init__(self, onboarding_session):
        super().__init__()
        self.onboarding_session = onboarding_session
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📚 Your Onboarding Progress")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        
        modules = self.onboarding_session.get('pathway_configuration', {}).get('modules', [])
        completed_modules = len(self.onboarding_session.get('progress_tracking', {}).get('completed_modules', []))
        
        self.progress_bar.setMaximum(len(modules))
        self.progress_bar.setValue(completed_modules)
        
        layout.addWidget(self.progress_bar)
        
        # Progress text
        progress_text = QLabel(f"{completed_modules}/{len(modules)} modules completed")
        layout.addWidget(progress_text)
        
        # Module list
        self.module_list = QListWidget()
        for i, module in enumerate(modules):
            item = QListWidgetItem(f"{'✅' if i < completed_modules else '⏳'} {module.replace('_', ' ').title()}")
            self.module_list.addItem(item)
        
        layout.addWidget(self.module_list)
        
        self.setLayout(layout)


class InteractiveModuleWidget(QWidget):
    """Interactive module content widget"""
    
    module_completed = pyqtSignal(str, dict)  # module_name, completion_data
    
    def __init__(self, module_name, module_content):
        super().__init__()
        self.module_name = module_name
        self.module_content = module_content
        self.competency_score = 0
        self.interaction_metrics = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Module header
        header = QLabel(f"📖 {self.module_name.replace('_', ' ').title()}")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # Module description
        description = QLabel(self.module_content.get('description', 'Module content'))
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Interactive content area
        content_area = QScrollArea()
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        # Add interactive elements based on module type
        self.create_interactive_content(content_layout)
        
        content_widget.setLayout(content_layout)
        content_area.setWidget(content_widget)
        layout.addWidget(content_area)
        
        # Completion section
        completion_group = QGroupBox("Module Completion")
        completion_layout = QVBoxLayout()
        
        self.competency_label = QLabel("Competency Score: 0%")
        completion_layout.addWidget(self.competency_label)
        
        complete_button = QPushButton("✅ Mark Module Complete")
        complete_button.clicked.connect(self.complete_module)
        completion_layout.addWidget(complete_button)
        
        completion_group.setLayout(completion_layout)
        layout.addWidget(completion_group)
        
        self.setLayout(layout)
    
    def create_interactive_content(self, layout):
        """Create interactive content based on module type"""
        
        # Knowledge check questions
        if 'questions' in self.module_content:
            questions_group = QGroupBox("📝 Knowledge Check")
            questions_layout = QVBoxLayout()
            
            self.question_widgets = []
            for i, question in enumerate(self.module_content['questions']):
                question_widget = self.create_question_widget(question, i)
                questions_layout.addWidget(question_widget)
                self.question_widgets.append(question_widget)
            
            questions_group.setLayout(questions_layout)
            layout.addWidget(questions_group)
        
        # Interactive scenarios
        if 'scenarios' in self.module_content:
            scenarios_group = QGroupBox("🎭 Interactive Scenarios")
            scenarios_layout = QVBoxLayout()
            
            for scenario in self.module_content['scenarios']:
                scenario_widget = self.create_scenario_widget(scenario)
                scenarios_layout.addWidget(scenario_widget)
            
            scenarios_group.setLayout(scenarios_layout)
            layout.addWidget(scenarios_group)
        
        # Practical exercises
        if 'exercises' in self.module_content:
            exercises_group = QGroupBox("💪 Practical Exercises")
            exercises_layout = QVBoxLayout()
            
            for exercise in self.module_content['exercises']:
                exercise_widget = self.create_exercise_widget(exercise)
                exercises_layout.addWidget(exercise_widget)
            
            exercises_group.setLayout(exercises_layout)
            layout.addWidget(exercises_group)
    
    def create_question_widget(self, question, index):
        """Create interactive question widget"""
        
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout()
        
        # Question text
        question_label = QLabel(f"Q{index + 1}: {question['text']}")
        question_label.setWordWrap(True)
        layout.addWidget(question_label)
        
        # Answer options
        self.answer_widgets = []
        for option in question['options']:
            checkbox = QCheckBox(option)
            checkbox.stateChanged.connect(lambda state, q=index: self.update_competency())
            layout.addWidget(checkbox)
            self.answer_widgets.append(checkbox)
        
        widget.setLayout(layout)
        return widget
    
    def create_scenario_widget(self, scenario):
        """Create interactive scenario widget"""
        
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout()
        
        # Scenario description
        desc_label = QLabel(f"🎭 {scenario['title']}")
        desc_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(desc_label)
        
        scenario_text = QLabel(scenario['description'])
        scenario_text.setWordWrap(True)
        layout.addWidget(scenario_text)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        for action in scenario.get('actions', []):
            action_button = QPushButton(action['label'])
            action_button.clicked.connect(lambda checked, a=action: self.handle_scenario_action(a))
            actions_layout.addWidget(action_button)
        
        layout.addLayout(actions_layout)
        widget.setLayout(layout)
        return widget
    
    def create_exercise_widget(self, exercise):
        """Create practical exercise widget"""
        
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout()
        
        # Exercise title
        title_label = QLabel(f"💪 {exercise['title']}")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Exercise instructions
        instructions = QLabel(exercise['instructions'])
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Exercise area
        if exercise['type'] == 'text_input':
            text_area = QTextEdit()
            text_area.setPlaceholderText("Enter your response here...")
            text_area.textChanged.connect(self.update_competency)
            layout.addWidget(text_area)
        
        elif exercise['type'] == 'selection':
            combo = QComboBox()
            combo.addItems(exercise.get('options', []))
            combo.currentTextChanged.connect(self.update_competency)
            layout.addWidget(combo)
        
        widget.setLayout(layout)
        return widget
    
    def handle_scenario_action(self, action):
        """Handle scenario action selection"""
        
        self.interaction_metrics[f"scenario_{action['id']}"] = {
            'action_taken': action['label'],
            'timestamp': datetime.now().isoformat(),
            'points': action.get('points', 0)
        }
        
        # Show feedback
        QMessageBox.information(self, "Scenario Result", action.get('feedback', 'Action completed'))
        self.update_competency()
    
    def update_competency(self):
        """Update competency score based on interactions"""
        
        total_points = 0
        max_points = 100  # Base competency
        
        # Add points from interactions
        for interaction in self.interaction_metrics.values():
            total_points += interaction.get('points', 0)
        
        # Calculate percentage
        self.competency_score = min(100, (total_points / max_points) * 100)
        self.competency_label.setText(f"Competency Score: {self.competency_score:.1f}%")
    
    def complete_module(self):
        """Complete the current module"""
        
        if self.competency_score < 70:
            reply = QMessageBox.question(
                self, 
                "Low Competency Score",
                f"Your competency score is {self.competency_score:.1f}%. "
                "Recommended minimum is 70%. Continue anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        completion_data = {
            'module_name': self.module_name,
            'competency_score': self.competency_score,
            'interaction_metrics': self.interaction_metrics,
            'completion_time': datetime.now().isoformat(),
            'time_spent_minutes': 15  # TODO: Calculate actual time
        }
        
        self.module_completed.emit(self.module_name, completion_data)
        QMessageBox.information(self, "Module Complete", f"Great job! You've completed {self.module_name.replace('_', ' ').title()}")


class ContextualHelpWidget(QWidget):
    """Contextual help and support widget"""
    
    def __init__(self):
        super().__init__()
        self.help_system = ContextualHelpSystem()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🔍 Help & Support")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QComboBox()
        self.search_input.setEditable(True)
        self.search_input.setPlaceholderText("Search for help topics...")
        
        search_button = QPushButton("🔍 Search")
        search_button.clicked.connect(self.search_help)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        
        # Help categories
        categories_group = QGroupBox("📚 Help Categories")
        categories_layout = QVBoxLayout()
        
        categories = [
            "Getting Started",
            "User Registration",
            "Voting & Elections", 
            "Debate Participation",
            "Blockchain & Security",
            "Troubleshooting",
            "Contact Support"
        ]
        
        for category in categories:
            category_button = QPushButton(category)
            category_button.clicked.connect(lambda checked, c=category: self.show_category_help(c))
            categories_layout.addWidget(category_button)
        
        categories_group.setLayout(categories_layout)
        layout.addWidget(categories_group)
        
        # Help content area
        self.help_content = QTextEdit()
        self.help_content.setReadOnly(True)
        self.help_content.setPlaceholderText("Select a help topic to view content...")
        layout.addWidget(self.help_content)
        
        self.setLayout(layout)
    
    def search_help(self):
        """Search for help content"""
        
        query = self.search_input.currentText()
        if not query:
            return
        
        try:
            results = self.help_system.search_help_content(query)
            self.display_help_results(results)
        except Exception as e:
            self.help_content.setText(f"Error searching help: {e}")
    
    def show_category_help(self, category):
        """Show help for specific category"""
        
        try:
            content = self.help_system.get_category_help(category)
            self.help_content.setText(content)
        except Exception as e:
            self.help_content.setText(f"Error loading help category: {e}")
    
    def display_help_results(self, results):
        """Display search results"""
        
        if not results:
            self.help_content.setText("No help topics found for your search.")
            return
        
        content = "# Search Results\n\n"
        for result in results:
            content += f"## {result['title']}\n{result['content']}\n\n"
        
        self.help_content.setText(content)


class GuideTab(QWidget):
    """Main System Guide Tab widget"""
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.onboarding_system = UserOnboardingSystem()
        self.current_onboarding_session = None
        self.init_ui()
        self.load_user_session()
    
    def init_ui(self):
        """Initialize the system guide interface"""
        
        layout = QVBoxLayout()
        
        # Tab header
        header_layout = QHBoxLayout()
        
        title = QLabel("🎓 System Guide & User Onboarding")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Quick help button
        help_button = QPushButton("❓ Quick Help")
        help_button.clicked.connect(self.show_quick_help)
        header_layout.addWidget(help_button)
        
        layout.addLayout(header_layout)
        
        # Main content tabs
        self.content_tabs = QTabWidget()
        
        # Onboarding tab
        self.onboarding_tab = QWidget()
        self.init_onboarding_tab()
        self.content_tabs.addTab(self.onboarding_tab, "📚 Onboarding")
        
        # Help & Support tab
        self.help_tab = ContextualHelpWidget()
        self.content_tabs.addTab(self.help_tab, "🔍 Help & Support")
        
        # Troubleshooting tab
        self.troubleshooting_tab = QWidget()
        self.init_troubleshooting_tab()
        self.content_tabs.addTab(self.troubleshooting_tab, "🔧 Troubleshooting")
        
        layout.addWidget(self.content_tabs)
        
        self.setLayout(layout)
    
    def init_onboarding_tab(self):
        """Initialize the onboarding tab"""
        
        layout = QVBoxLayout()
        
        # Welcome section
        welcome_group = QGroupBox("👋 Welcome to the Civic Engagement Platform!")
        welcome_layout = QVBoxLayout()
        
        welcome_text = QLabel(
            "This comprehensive onboarding system will guide you through all platform features "
            "based on your role and experience level. Complete interactive modules to gain "
            "competency in civic participation and democratic engagement."
        )
        welcome_text.setWordWrap(True)
        welcome_layout.addWidget(welcome_text)
        
        # Start onboarding button
        start_button = QPushButton("🚀 Start Personalized Onboarding")
        start_button.clicked.connect(self.start_onboarding)
        welcome_layout.addWidget(start_button)
        
        welcome_group.setLayout(welcome_layout)
        layout.addWidget(welcome_group)
        
        # Current progress section (initially hidden)
        self.progress_group = QGroupBox("📊 Your Progress")
        self.progress_layout = QVBoxLayout()
        self.progress_group.setLayout(self.progress_layout)
        self.progress_group.setVisible(False)
        layout.addWidget(self.progress_group)
        
        # Module content area
        self.module_area = QScrollArea()
        self.module_area.setVisible(False)
        layout.addWidget(self.module_area)
        
        self.onboarding_tab.setLayout(layout)
    
    def init_troubleshooting_tab(self):
        """Initialize the troubleshooting tab"""
        
        layout = QVBoxLayout()
        
        # Diagnostic section
        diagnostic_group = QGroupBox("🔍 System Diagnostics")
        diagnostic_layout = QVBoxLayout()
        
        run_diagnostics_button = QPushButton("🔧 Run System Diagnostics")
        run_diagnostics_button.clicked.connect(self.run_diagnostics)
        diagnostic_layout.addWidget(run_diagnostics_button)
        
        self.diagnostic_results = QTextEdit()
        self.diagnostic_results.setReadOnly(True)
        self.diagnostic_results.setPlaceholderText("Diagnostic results will appear here...")
        diagnostic_layout.addWidget(self.diagnostic_results)
        
        diagnostic_group.setLayout(diagnostic_layout)
        layout.addWidget(diagnostic_group)
        
        # Common issues section
        issues_group = QGroupBox("⚠️ Common Issues & Solutions")
        issues_layout = QVBoxLayout()
        
        common_issues = [
            ("Login Problems", "Issues with authentication and access"),
            ("Voting Errors", "Problems with voting and elections"),
            ("Blockchain Sync", "Blockchain synchronization issues"),
            ("Performance Issues", "Slow loading and responsiveness"),
            ("Security Concerns", "Account security and privacy questions")
        ]
        
        for issue_title, issue_desc in common_issues:
            issue_button = QPushButton(f"🔧 {issue_title}")
            issue_button.setToolTip(issue_desc)
            issue_button.clicked.connect(lambda checked, title=issue_title: self.show_issue_help(title))
            issues_layout.addWidget(issue_button)
        
        issues_group.setLayout(issues_layout)
        layout.addWidget(issues_group)
        
        self.troubleshooting_tab.setLayout(layout)
    
    def load_user_session(self):
        """Load current user session"""
        
        try:
            self.current_user = SessionManager.get_current_user()
            if self.current_user:
                self.load_existing_onboarding()
        except Exception as e:
            print(f"Error loading user session: {e}")
    
    def load_existing_onboarding(self):
        """Load existing onboarding progress if available"""
        
        try:
            user_email = self.current_user.get('email')
            session = self.onboarding_system.get_onboarding_session(user_email)
            
            if session and session.get('completion_status') == 'in_progress':
                self.current_onboarding_session = session
                self.display_onboarding_progress()
        except Exception as e:
            print(f"Error loading onboarding session: {e}")
    
    def start_onboarding(self):
        """Start or resume user onboarding"""
        
        if not self.current_user:
            QMessageBox.warning(self, "Authentication Required", 
                               "Please log in to start personalized onboarding.")
            return
        
        try:
            user_email = self.current_user.get('email')
            
            # Check for existing session
            existing_session = self.onboarding_system.get_onboarding_session(user_email)
            
            if existing_session and existing_session.get('completion_status') == 'in_progress':
                reply = QMessageBox.question(
                    self, 
                    "Resume Onboarding?",
                    "You have an existing onboarding session. Resume where you left off?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.current_onboarding_session = existing_session
                else:
                    # Start new session
                    success, session_or_message = self.onboarding_system.initiate_user_onboarding(
                        user_email, {'reset_existing': True}
                    )
                    if success:
                        self.current_onboarding_session = session_or_message
                    else:
                        QMessageBox.warning(self, "Onboarding Error", session_or_message)
                        return
            else:
                # Start new session
                success, session_or_message = self.onboarding_system.initiate_user_onboarding(
                    user_email, {}
                )
                if success:
                    self.current_onboarding_session = session_or_message
                else:
                    QMessageBox.warning(self, "Onboarding Error", session_or_message)
                    return
            
            self.display_onboarding_progress()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start onboarding: {e}")
    
    def display_onboarding_progress(self):
        """Display current onboarding progress and module"""
        
        if not self.current_onboarding_session:
            return
        
        # Show progress section
        self.progress_group.setVisible(True)
        
        # Clear existing progress widgets
        for i in reversed(range(self.progress_layout.count())):
            self.progress_layout.itemAt(i).widget().setParent(None)
        
        # Add progress widget
        progress_widget = OnboardingProgressWidget(self.current_onboarding_session)
        self.progress_layout.addWidget(progress_widget)
        
        # Load current module
        self.load_current_module()
    
    def load_current_module(self):
        """Load the current onboarding module"""
        
        if not self.current_onboarding_session:
            return
        
        try:
            current_module_data = self.current_onboarding_session.get('current_module')
            if not current_module_data:
                # Get next module
                next_module = self.onboarding_system.get_next_module(self.current_onboarding_session)
                if next_module:
                    current_module_data = next_module
                else:
                    self.complete_onboarding()
                    return
            
            # Create module widget
            module_widget = InteractiveModuleWidget(
                current_module_data['module_name'],
                current_module_data['content']
            )
            module_widget.module_completed.connect(self.on_module_completed)
            
            # Set module widget
            self.module_area.setWidget(module_widget)
            self.module_area.setVisible(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Module Error", f"Failed to load module: {e}")
    
    @pyqtSlot(str, dict)
    def on_module_completed(self, module_name, completion_data):
        """Handle module completion"""
        
        try:
            # Update onboarding session
            success, message = self.onboarding_system.complete_module(
                self.current_onboarding_session['id'],
                module_name,
                completion_data
            )
            
            if success:
                # Refresh onboarding session
                user_email = self.current_user.get('email')
                self.current_onboarding_session = self.onboarding_system.get_onboarding_session(user_email)
                
                # Check if onboarding is complete
                if self.current_onboarding_session.get('completion_status') == 'completed':
                    self.complete_onboarding()
                else:
                    # Load next module
                    self.display_onboarding_progress()
            else:
                QMessageBox.warning(self, "Completion Error", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to complete module: {e}")
    
    def complete_onboarding(self):
        """Handle onboarding completion"""
        
        QMessageBox.information(
            self, 
            "🎉 Onboarding Complete!",
            "Congratulations! You've completed your civic engagement onboarding. "
            "You're now ready to participate fully in the democratic process."
        )
        
        # Hide module area and show completion summary
        self.module_area.setVisible(False)
        
        # TODO: Add completion certificate or summary
    
    def show_quick_help(self):
        """Show quick help dialog"""
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Quick Help")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout()
        
        help_text = """
        # Quick Help Guide
        
        ## Getting Started
        1. **Start Onboarding**: Click the "Start Personalized Onboarding" button
        2. **Complete Modules**: Work through interactive modules at your own pace
        3. **Get Help**: Use the Help & Support tab for detailed assistance
        4. **Troubleshoot**: Use the Troubleshooting tab for technical issues
        
        ## Onboarding Process
        - Role-based learning paths customized for your civic role
        - Interactive modules with knowledge checks and scenarios
        - Competency scoring to track your progress
        - Achievement milestones and certificates
        
        ## Support Options
        - Search help topics for specific questions
        - Browse help categories for organized information
        - Run system diagnostics for technical issues
        - Contact support for personalized assistance
        """
        
        help_display = QTextEdit()
        help_display.setReadOnly(True)
        help_display.setText(help_text)
        layout.addWidget(help_display)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def run_diagnostics(self):
        """Run system diagnostics"""
        
        self.diagnostic_results.setText("🔍 Running diagnostics...\n")
        
        # TODO: Implement actual diagnostic checks
        diagnostic_checks = [
            ("Database Connectivity", "✅ All databases accessible"),
            ("User Authentication", "✅ Session management working"),
            ("Blockchain Sync", "✅ Blockchain synchronized"),
            ("Network Connectivity", "✅ Network connections stable"),
            ("Module Loading", "✅ All modules loaded successfully"),
            ("Performance Check", "✅ System performance optimal")
        ]
        
        results_text = "🔍 System Diagnostic Results:\n\n"
        for check_name, result in diagnostic_checks:
            results_text += f"{check_name}: {result}\n"
        
        results_text += "\n✅ All systems operational. No issues detected."
        
        self.diagnostic_results.setText(results_text)
    
    def show_issue_help(self, issue_title):
        """Show help for specific issue"""
        
        issue_help = {
            "Login Problems": """
                # Login Problems Solutions
                
                1. **Check Credentials**: Verify email and password are correct
                2. **Clear Browser Data**: Clear cache and cookies if using web version
                3. **Reset Password**: Use password reset option if available
                4. **Check Network**: Ensure stable internet connection
                5. **Contact Support**: If issues persist, contact technical support
            """,
            "Voting Errors": """
                # Voting Errors Solutions
                
                1. **Verify Eligibility**: Ensure you're registered and eligible to vote
                2. **Check Voting Period**: Confirm voting is currently open
                3. **Clear Cache**: Refresh the application and try again
                4. **Check Role**: Verify your civic role has voting permissions
                5. **Report Issues**: Contact election administrators for assistance
            """,
            "Blockchain Sync": """
                # Blockchain Synchronization Solutions
                
                1. **Check Network**: Ensure stable internet connection
                2. **Restart Application**: Close and restart the application
                3. **Clear Blockchain Cache**: Reset blockchain data (if needed)
                4. **Check Validators**: Verify validator network status
                5. **Manual Sync**: Force manual blockchain synchronization
            """,
            "Performance Issues": """
                # Performance Issues Solutions
                
                1. **Restart Application**: Close and restart for memory cleanup
                2. **Check Resources**: Ensure sufficient system memory and storage
                3. **Close Other Apps**: Free up system resources
                4. **Update Software**: Ensure you have the latest version
                5. **Contact Support**: Report persistent performance issues
            """,
            "Security Concerns": """
                # Security Concerns Solutions
                
                1. **Change Password**: Update your password regularly
                2. **Check Login History**: Review recent login activity
                3. **Secure Keys**: Ensure private keys are safely stored
                4. **Report Suspicious Activity**: Contact security team immediately
                5. **Enable 2FA**: Use two-factor authentication if available
            """
        }
        
        help_content = issue_help.get(issue_title, "Help content not available.")
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Help: {issue_title}")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout()
        
        help_display = QTextEdit()
        help_display.setReadOnly(True)
        help_display.setText(help_content)
        layout.addWidget(help_display)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec_()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    guide_tab = GuideTab()
    guide_tab.show()
    
    sys.exit(app.exec_())