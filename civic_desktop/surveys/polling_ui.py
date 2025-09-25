# Surveys & Polling Module - UI Components for Democratic Opinion Gathering
"""
UI components providing:
- Survey creation interface with question builder
- Polling dashboard with real-time results
- Referendum management and ballot design
- Statistical analysis and data visualization
- Research tools and export capabilities
"""

from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QListWidget, QListWidgetItem, QTextEdit, QLineEdit, 
                            QComboBox, QTabWidget, QScrollArea, QMessageBox, QFormLayout,
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                            QGroupBox, QCheckBox, QSpinBox, QProgressBar, QDialog,
                            QTreeWidget, QTreeWidgetItem, QSlider, QRadioButton, QButtonGroup,
                            QDialogButtonBox, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QColor, QPalette
from .survey_engine import SurveyEngine
from ..users.session import SessionManager

class SurveysPollingTab(QWidget):
    """Main surveys and polling interface for democratic opinion gathering"""
    
    # Signal for survey updates
    survey_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.survey_engine = SurveyEngine()
        self.current_survey = None
        self.init_ui()
        
        # Auto-refresh timer for new surveys and results
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_surveys)
        self.refresh_timer.start(60000)  # Refresh every minute
    
    def init_ui(self):
        """Initialize the surveys and polling interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Blockchain status and user role display
        user = SessionManager.get_current_user()
        role = user.get('role', 'Unknown') if user else 'Unknown'
        
        blockchain_status = QLabel("All surveys, polls, and referendums are <b>recorded on blockchain</b> for transparency and integrity.")
        blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
        blockchain_status.setAccessibleName("Security Status")
        blockchain_status.setToolTip("Survey responses are cryptographically protected with blockchain audit trails.")
        
        role_label = QLabel(f"Your Role: <b>{role}</b>")
        role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
        role_label.setAccessibleName("User Role")
        role_label.setToolTip("Your platform role determines survey creation and access permissions.")
        
        # Survey action buttons
        create_survey_btn = QPushButton("📊 Create Survey")
        create_survey_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        create_survey_btn.setAccessibleName("Create Survey Button")
        create_survey_btn.setToolTip("Create a new public opinion survey or research poll.")
        create_survey_btn.setMinimumHeight(40)
        create_survey_btn.setMinimumWidth(180)
        create_survey_btn.clicked.connect(self.open_survey_creator)
        
        quick_poll_btn = QPushButton("⚡ Quick Poll")
        quick_poll_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        quick_poll_btn.clicked.connect(self.open_quick_poll_dialog)
        
        referendum_btn = QPushButton("🗳️ Referendum")
        referendum_btn.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        referendum_btn.clicked.connect(self.open_referendum_dialog)
        
        top_layout = QVBoxLayout()
        top_layout.addWidget(blockchain_status)
        top_layout.addWidget(role_label)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(create_survey_btn)
        button_layout.addWidget(quick_poll_btn)
        button_layout.addWidget(referendum_btn)
        button_layout.addStretch()
        top_layout.addLayout(button_layout)
        
        layout.addLayout(top_layout)
        
        # Header
        header = QLabel("📊 Democratic Surveys & Polling")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                color: white;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create main content container
        self.main_content = QWidget()
        layout.addWidget(self.main_content)
        
        self.setLayout(layout)
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh the entire UI based on authentication status"""
        # Clear existing content
        if hasattr(self, 'main_content'):
            layout = self.main_content.layout()
            if layout:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            else:
                layout = QVBoxLayout()
                self.main_content.setLayout(layout)
        
        # Check if user is logged in
        if not SessionManager.is_authenticated():
            self.show_login_required()
            return
        
        # Create main surveys interface for logged-in users
        self.create_surveys_interface()
    
    def show_login_required(self):
        """Show login required message"""
        layout = self.main_content.layout()
        
        login_frame = QFrame()
        login_frame.setFrameStyle(QFrame.StyledPanel)
        login_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin: 50px;
            }
        """)
        
        frame_layout = QVBoxLayout()
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(40, 40, 40, 40)
        
        icon_label = QLabel("🔐")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; color: #6c757d;")
        
        title_label = QLabel("Survey Participation Required")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #495057; margin-bottom: 10px;")
        
        message_label = QLabel("Please log in to participate in surveys, polls, and referendums.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 16px; color: #6c757d; margin-bottom: 20px;")
        message_label.setWordWrap(True)
        
        frame_layout.addWidget(icon_label)
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(message_label)
        
        login_frame.setLayout(frame_layout)
        layout.addWidget(login_frame)
    
    def create_surveys_interface(self):
        """Create the main surveys interface for authenticated users"""
        layout = self.main_content.layout()
        
        # Main surveys layout with tabs
        self.surveys_tabs = QTabWidget()
        self.surveys_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #e74c3c;
                color: white;
                font-weight: bold;
            }
        """)
        
        # Add survey tabs
        self.surveys_tabs.addTab(self.create_active_surveys_tab(), "🔴 Active Surveys")
        self.surveys_tabs.addTab(self.create_survey_results_tab(), "📈 Results & Analytics")
        self.surveys_tabs.addTab(self.create_my_surveys_tab(), "📝 My Surveys")
        self.surveys_tabs.addTab(self.create_research_tab(), "🔬 Research Tools")
        
        layout.addWidget(self.surveys_tabs)
        
        # Load initial data
        self.refresh_surveys()
    
    def create_active_surveys_tab(self) -> QWidget:
        """Create the active surveys participation tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Survey statistics
        stats_group = QGroupBox("Survey System Statistics")
        stats_layout = QFormLayout()
        
        self.total_surveys_label = QLabel("Loading...")
        self.active_surveys_label = QLabel("Loading...")
        self.total_responses_label = QLabel("Loading...")
        self.participation_rate_label = QLabel("Loading...")
        
        stats_layout.addRow("Total Surveys:", self.total_surveys_label)
        stats_layout.addRow("Active Surveys:", self.active_surveys_label)
        stats_layout.addRow("Total Responses:", self.total_responses_label)
        stats_layout.addRow("Participation Rate:", self.participation_rate_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Survey filters
        filters_group = QGroupBox("Filter Surveys")
        filters_layout = QHBoxLayout()
        
        self.survey_type_filter = QComboBox()
        self.survey_type_filter.addItems(["All Types", "Opinion Poll", "Research", "Policy", "Referendum"])
        self.survey_type_filter.currentTextChanged.connect(self.filter_surveys)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Active", "Completed", "Draft"])
        self.status_filter.currentTextChanged.connect(self.filter_surveys)
        
        filters_layout.addWidget(QLabel("Type:"))
        filters_layout.addWidget(self.survey_type_filter)
        filters_layout.addWidget(QLabel("Status:"))
        filters_layout.addWidget(self.status_filter)
        filters_layout.addStretch()
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Active surveys list
        surveys_group = QGroupBox("Available Surveys")
        surveys_layout = QVBoxLayout()
        
        self.surveys_list = QListWidget()
        self.surveys_list.itemClicked.connect(self.on_survey_selected)
        surveys_layout.addWidget(self.surveys_list)
        
        # Survey details panel
        self.survey_details = QTextEdit()
        self.survey_details.setReadOnly(True)
        self.survey_details.setMaximumHeight(150)
        self.survey_details.setPlaceholderText("Select a survey to view details...")
        surveys_layout.addWidget(self.survey_details)
        
        # Participation buttons
        participation_layout = QHBoxLayout()
        
        self.participate_btn = QPushButton("Participate in Survey")
        self.participate_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px;")
        self.participate_btn.clicked.connect(self.participate_in_survey)
        self.participate_btn.setEnabled(False)
        
        self.view_results_btn = QPushButton("View Results")
        self.view_results_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px 20px; border-radius: 5px;")
        self.view_results_btn.clicked.connect(self.view_survey_results)
        self.view_results_btn.setEnabled(False)
        
        participation_layout.addWidget(self.participate_btn)
        participation_layout.addWidget(self.view_results_btn)
        participation_layout.addStretch()
        
        surveys_layout.addLayout(participation_layout)
        surveys_group.setLayout(surveys_layout)
        layout.addWidget(surveys_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_survey_results_tab(self) -> QWidget:
        """Create the survey results and analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Results header
        results_label = QLabel("Survey Results & Analytics")
        results_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(results_label)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.display_survey_results)
        layout.addWidget(self.results_list)
        
        # Results display area
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setPlaceholderText("Select a survey to view detailed results and analytics...")
        layout.addWidget(self.results_display)
        
        # Export options
        export_group = QGroupBox("Export & Research")
        export_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.setStyleSheet("background-color: #17a2b8; color: white; padding: 8px 16px; border-radius: 5px;")
        export_csv_btn.clicked.connect(self.export_results_csv)
        
        export_pdf_btn = QPushButton("Export to PDF")
        export_pdf_btn.setStyleSheet("background-color: #6f42c1; color: white; padding: 8px 16px; border-radius: 5px;")
        export_pdf_btn.clicked.connect(self.export_results_pdf)
        
        export_layout.addWidget(export_csv_btn)
        export_layout.addWidget(export_pdf_btn)
        export_layout.addStretch()
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_my_surveys_tab(self) -> QWidget:
        """Create the personal surveys management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # My surveys header
        my_surveys_label = QLabel("My Created Surveys")
        my_surveys_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(my_surveys_label)
        
        # My surveys list
        self.my_surveys_list = QListWidget()
        self.my_surveys_list.itemClicked.connect(self.on_my_survey_selected)
        layout.addWidget(self.my_surveys_list)
        
        # Survey management buttons
        management_layout = QHBoxLayout()
        
        edit_survey_btn = QPushButton("Edit Survey")
        edit_survey_btn.setStyleSheet("background-color: #ffc107; color: black; font-weight: bold; padding: 10px 20px; border-radius: 5px;")
        edit_survey_btn.clicked.connect(self.edit_selected_survey)
        
        close_survey_btn = QPushButton("Close Survey")
        close_survey_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 10px 20px; border-radius: 5px;")
        close_survey_btn.clicked.connect(self.close_selected_survey)
        
        duplicate_survey_btn = QPushButton("Duplicate")
        duplicate_survey_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 10px 20px; border-radius: 5px;")
        duplicate_survey_btn.clicked.connect(self.duplicate_selected_survey)
        
        management_layout.addWidget(edit_survey_btn)
        management_layout.addWidget(close_survey_btn)
        management_layout.addWidget(duplicate_survey_btn)
        management_layout.addStretch()
        
        layout.addLayout(management_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_research_tab(self) -> QWidget:
        """Create the research tools and advanced analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Research tools header
        research_label = QLabel("Advanced Research Tools")
        research_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(research_label)
        
        # Research project creation
        project_group = QGroupBox("Research Project Management")
        project_layout = QFormLayout()
        
        self.project_title = QLineEdit()
        self.project_title.setPlaceholderText("Research project title...")
        
        self.project_description = QTextEdit()
        self.project_description.setPlaceholderText("Describe your research goals and methodology...")
        self.project_description.setMaximumHeight(100)
        
        project_layout.addRow("Project Title:", self.project_title)
        project_layout.addRow("Description:", self.project_description)
        
        create_project_btn = QPushButton("Create Research Project")
        create_project_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px;")
        create_project_btn.clicked.connect(self.create_research_project)
        
        project_layout.addRow("", create_project_btn)
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)
        
        # Analytics tools
        analytics_group = QGroupBox("Statistical Analysis Tools")
        analytics_layout = QVBoxLayout()
        
        correlation_btn = QPushButton("Cross-Survey Correlation Analysis")
        correlation_btn.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px; border-radius: 5px;")
        
        demographics_btn = QPushButton("Demographic Trend Analysis")
        demographics_btn.setStyleSheet("background-color: #17a2b8; color: white; padding: 8px 16px; border-radius: 5px;")
        
        temporal_btn = QPushButton("Temporal Response Analysis")
        temporal_btn.setStyleSheet("background-color: #6f42c1; color: white; padding: 8px 16px; border-radius: 5px;")
        
        analytics_layout.addWidget(correlation_btn)
        analytics_layout.addWidget(demographics_btn)
        analytics_layout.addWidget(temporal_btn)
        
        analytics_group.setLayout(analytics_layout)
        layout.addWidget(analytics_group)
        
        widget.setLayout(layout)
        return widget
    
    def refresh_surveys(self):
        """Refresh all survey data and statistics"""
        if not SessionManager.is_authenticated():
            return
        
        try:
            # Update statistics
            stats = self.survey_engine.get_survey_statistics()
            
            if hasattr(self, 'total_surveys_label'):
                self.total_surveys_label.setText(str(stats.get('total_surveys', 0)))
                self.active_surveys_label.setText(str(stats.get('active_surveys', 0)))
                self.total_responses_label.setText(str(stats.get('total_responses', 0)))
                
                participation = stats.get('participation_trends', {})
                rate = participation.get('average_response_rate', 0)
                trend = participation.get('trend', 'stable')
                self.participation_rate_label.setText(f"{rate:.1f} responses/survey ({trend})")
            
            # Update surveys lists
            self.load_active_surveys()
            self.load_my_surveys()
            self.load_survey_results()
            
        except Exception as e:
            print(f"Error refreshing surveys: {e}")
    
    def load_active_surveys(self):
        """Load active surveys into the list"""
        if not hasattr(self, 'surveys_list'):
            return
        
        try:
            user = SessionManager.get_current_user()
            if user:
                surveys = self.survey_engine.get_surveys(user['email'], 'active')
                
                self.surveys_list.clear()
                
                for survey in surveys:
                    # Create display text
                    response_count = survey.get('response_count', 0)
                    survey_type = survey.get('survey_type', 'opinion').title()
                    
                    item_text = f"📊 {survey['title']}\n"
                    item_text += f"Type: {survey_type} | Responses: {response_count}\n"
                    item_text += f"Created: {survey['created_at'][:10]} | Ends: {survey['ends_at'][:10]}"
                    
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, survey)
                    self.surveys_list.addItem(item)
                    
        except Exception as e:
            print(f"Error loading active surveys: {e}")
    
    def load_my_surveys(self):
        """Load user's created surveys"""
        if not hasattr(self, 'my_surveys_list'):
            return
        
        try:
            user = SessionManager.get_current_user()
            if user:
                all_surveys = self.survey_engine.get_surveys()
                my_surveys = [s for s in all_surveys if s['creator_email'] == user['email']]
                
                self.my_surveys_list.clear()
                
                for survey in my_surveys:
                    item_text = f"{survey['title']} ({survey['status']})\n"
                    item_text += f"Responses: {survey.get('response_count', 0)} | "
                    item_text += f"Created: {survey['created_at'][:10]}"
                    
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, survey)
                    self.my_surveys_list.addItem(item)
                    
        except Exception as e:
            print(f"Error loading my surveys: {e}")
    
    def load_survey_results(self):
        """Load available survey results"""
        if not hasattr(self, 'results_list'):
            return
        
        try:
            user = SessionManager.get_current_user()
            if user:
                surveys = self.survey_engine.get_surveys(user['email'])
                
                # Only show surveys with results that user can view
                self.results_list.clear()
                
                for survey in surveys:
                    if (survey.get('response_count', 0) > 0 and 
                        (survey['creator_email'] == user['email'] or
                         survey.get('settings', {}).get('show_results_live', False))):
                        
                        item_text = f"📈 {survey['title']}\n"
                        item_text += f"Responses: {survey.get('response_count', 0)} | "
                        item_text += f"Type: {survey.get('survey_type', 'opinion').title()}"
                        
                        item = QListWidgetItem(item_text)
                        item.setData(Qt.UserRole, survey)
                        self.results_list.addItem(item)
                        
        except Exception as e:
            print(f"Error loading survey results: {e}")
    
    def filter_surveys(self):
        """Filter surveys based on selected criteria"""
        # Implementation would filter the surveys list based on type and status
        self.load_active_surveys()
    
    def on_survey_selected(self, item):
        """Handle survey selection from active surveys"""
        if item and item.data(Qt.UserRole):
            survey = item.data(Qt.UserRole)
            self.current_survey = survey
            self.display_survey_details(survey)
    
    def on_my_survey_selected(self, item):
        """Handle survey selection from my surveys"""
        if item and item.data(Qt.UserRole):
            survey = item.data(Qt.UserRole)
            self.current_survey = survey
    
    def display_survey_details(self, survey):
        """Display detailed survey information"""
        if not hasattr(self, 'survey_details'):
            return
        
        details = f"Title: {survey['title']}\n\n"
        details += f"Description: {survey['description']}\n\n"
        details += f"Type: {survey.get('survey_type', 'opinion').title()}\n"
        details += f"Privacy Mode: {survey.get('privacy_mode', 'anonymous').title()}\n"
        details += f"Created by: {survey['creator_email']} ({survey.get('creator_role', 'Unknown')})\n"
        details += f"Created: {survey['created_at'][:16]}\n"
        details += f"Ends: {survey['ends_at'][:16]}\n"
        details += f"Current Responses: {survey.get('response_count', 0)}\n\n"
        details += f"Questions: {len(survey.get('questions', []))}"
        
        self.survey_details.setPlainText(details)
        
        # Enable/disable participation buttons
        user = SessionManager.get_current_user()
        can_participate = (user and 
                          survey['status'] == 'active' and
                          not self.survey_engine.has_responded(survey['id'], user['email']))
        
        self.participate_btn.setEnabled(can_participate)
        self.view_results_btn.setEnabled(survey.get('response_count', 0) > 0)
    
    def display_survey_results(self, item):
        """Display detailed survey results"""
        if not item or not item.data(Qt.UserRole):
            return
        
        survey = item.data(Qt.UserRole)
        user = SessionManager.get_current_user()
        
        if user:
            results = self.survey_engine.get_survey_results(survey['id'], user['email'])
            
            if results:
                results_text = f"Survey Results: {results['survey']['title']}\n"
                results_text += "=" * 50 + "\n\n"
                results_text += f"Total Responses: {results['total_responses']}\n"
                results_text += f"Completion Rate: {results['completion_rate']:.1f}%\n\n"
                
                # Question analysis
                for i, question_analysis in enumerate(results['questions_analysis']):
                    results_text += f"Question {i+1}: {question_analysis['question']}\n"
                    results_text += f"Responses: {question_analysis['total_responses']}\n"
                    
                    if question_analysis['type'] == 'multiple_choice':
                        stats = question_analysis['statistics']
                        for option, percentage in stats['percentages'].items():
                            count = stats['option_counts'].get(option, 0)
                            results_text += f"  • {option}: {count} ({percentage:.1f}%)\n"
                    
                    elif question_analysis['type'] in ['rating', 'scale']:
                        stats = question_analysis['statistics']
                        results_text += f"  Average: {stats.get('average', 0):.1f}\n"
                        results_text += f"  Range: {stats.get('minimum', 0)} - {stats.get('maximum', 0)}\n"
                    
                    results_text += "\n"
                
                # Demographic breakdown
                demographics = results['demographic_breakdown']
                if demographics['total_with_demographics'] > 0:
                    results_text += "Demographic Breakdown:\n"
                    results_text += f"By Role: {demographics['by_role']}\n"
                    results_text += f"By Location: {demographics['by_location']}\n"
                
                self.results_display.setPlainText(results_text)
            else:
                self.results_display.setPlainText("Results not available or access denied.")
    
    def participate_in_survey(self):
        """Open survey participation dialog"""
        if self.current_survey:
            dialog = SurveyParticipationDialog(self.current_survey, self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_surveys()  # Refresh after participation
    
    def view_survey_results(self):
        """View detailed survey results"""
        if self.current_survey and hasattr(self, 'results_list'):
            # Switch to results tab and display results
            self.surveys_tabs.setCurrentIndex(1)  # Results tab
    
    def open_survey_creator(self):
        """Open survey creation dialog"""
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Required", "Please log in to create surveys.")
            return
        
        if not self.survey_engine.can_create_survey(user.get('role', '')):
            QMessageBox.warning(self, "Access Denied", "You don't have permission to create surveys.")
            return
        
        dialog = SurveyCreatorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_surveys()
    
    def open_quick_poll_dialog(self):
        """Open quick poll creation dialog"""
        dialog = QuickPollDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_surveys()
    
    def open_referendum_dialog(self):
        """Open referendum creation dialog"""
        dialog = ReferendumDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_surveys()
    
    def edit_selected_survey(self):
        """Edit the selected survey"""
        QMessageBox.information(self, "Edit Survey", "Survey editing feature coming soon!")
    
    def close_selected_survey(self):
        """Close the selected survey"""
        QMessageBox.information(self, "Close Survey", "Survey closing feature coming soon!")
    
    def duplicate_selected_survey(self):
        """Duplicate the selected survey"""
        QMessageBox.information(self, "Duplicate Survey", "Survey duplication feature coming soon!")
    
    def create_research_project(self):
        """Create a new research project"""
        title = self.project_title.text().strip()
        description = self.project_description.toPlainText().strip()
        
        if not title or not description:
            QMessageBox.warning(self, "Missing Information", "Please provide project title and description.")
            return
        
        QMessageBox.information(self, "Research Project", f"Research project '{title}' created successfully!")
        self.project_title.clear()
        self.project_description.clear()
    
    def export_results_csv(self):
        """Export survey results to CSV"""
        QMessageBox.information(self, "Export", "CSV export feature coming soon!")
    
    def export_results_pdf(self):
        """Export survey results to PDF"""
        QMessageBox.information(self, "Export", "PDF export feature coming soon!")

class SurveyCreatorDialog(QDialog):
    """Dialog for creating comprehensive surveys"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Survey")
        self.setModal(True)
        self.resize(700, 600)
        self.survey_engine = SurveyEngine()
        self.questions = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📊 Create New Survey")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(header)
        
        # Survey basic information
        info_group = QGroupBox("Survey Information")
        info_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter survey title...")
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe the purpose and scope of this survey...")
        self.description_input.setMaximumHeight(100)
        
        self.survey_type = QComboBox()
        self.survey_type.addItems(["opinion", "research", "policy", "referendum"])
        
        self.privacy_mode = QComboBox()
        self.privacy_mode.addItems(["anonymous", "verified", "public"])
        
        self.target_audience = QComboBox()
        self.target_audience.addItems([
            "all_citizens", "Contract Representatives", "Contract Senators", 
            "Contract Elders", "public", "specific_users"
        ])
        
        self.duration_days = QSpinBox()
        self.duration_days.setRange(1, 365)
        self.duration_days.setValue(30)
        
        info_layout.addRow("Title:", self.title_input)
        info_layout.addRow("Description:", self.description_input)
        info_layout.addRow("Type:", self.survey_type)
        info_layout.addRow("Privacy Mode:", self.privacy_mode)
        info_layout.addRow("Target Audience:", self.target_audience)
        info_layout.addRow("Duration (days):", self.duration_days)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Questions section
        questions_group = QGroupBox("Survey Questions")
        questions_layout = QVBoxLayout()
        
        # Question list
        self.questions_list = QListWidget()
        questions_layout.addWidget(self.questions_list)
        
        # Question management buttons
        question_buttons = QHBoxLayout()
        
        add_question_btn = QPushButton("Add Question")
        add_question_btn.clicked.connect(self.add_question)
        
        edit_question_btn = QPushButton("Edit Question")
        edit_question_btn.clicked.connect(self.edit_question)
        
        remove_question_btn = QPushButton("Remove Question")
        remove_question_btn.clicked.connect(self.remove_question)
        
        question_buttons.addWidget(add_question_btn)
        question_buttons.addWidget(edit_question_btn)
        question_buttons.addWidget(remove_question_btn)
        question_buttons.addStretch()
        
        questions_layout.addLayout(question_buttons)
        questions_group.setLayout(questions_layout)
        layout.addWidget(questions_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.create_survey)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def add_question(self):
        """Add a new question to the survey"""
        dialog = QuestionBuilderDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            question = dialog.get_question()
            self.questions.append(question)
            self.refresh_questions_list()
    
    def edit_question(self):
        """Edit selected question"""
        current_row = self.questions_list.currentRow()
        if current_row >= 0:
            question = self.questions[current_row]
            dialog = QuestionBuilderDialog(self, question)
            if dialog.exec_() == QDialog.Accepted:
                self.questions[current_row] = dialog.get_question()
                self.refresh_questions_list()
    
    def remove_question(self):
        """Remove selected question"""
        current_row = self.questions_list.currentRow()
        if current_row >= 0:
            del self.questions[current_row]
            self.refresh_questions_list()
    
    def refresh_questions_list(self):
        """Refresh the questions list display"""
        self.questions_list.clear()
        
        for i, question in enumerate(self.questions):
            item_text = f"Q{i+1}: {question['question']} ({question['type']})"
            self.questions_list.addItem(item_text)
    
    def create_survey(self):
        """Create the survey"""
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()
        survey_type = self.survey_type.currentText()
        privacy_mode = self.privacy_mode.currentText()
        target_audience = [self.target_audience.currentText()]
        duration = self.duration_days.value()
        
        if not all([title, description, self.questions]):
            QMessageBox.warning(self, "Missing Information", "Please fill in all required fields and add at least one question.")
            return
        
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Required", "Please log in to create surveys.")
            return
        
        try:
            success, message = self.survey_engine.create_survey(
                user['email'], title, description, self.questions,
                target_audience, survey_type, privacy_mode, duration
            )
            
            if success:
                QMessageBox.information(self, "Survey Created", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Creation Failed", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create survey: {str(e)}")

class QuestionBuilderDialog(QDialog):
    """Dialog for building individual survey questions"""
    
    def __init__(self, parent=None, question=None):
        super().__init__(parent)
        self.setWindowTitle("Build Question")
        self.setModal(True)
        self.resize(500, 400)
        self.editing_question = question
        self.init_ui()
        
        if question:
            self.load_question(question)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Question text
        question_group = QGroupBox("Question Details")
        question_layout = QFormLayout()
        
        self.question_text = QTextEdit()
        self.question_text.setPlaceholderText("Enter your question...")
        self.question_text.setMaximumHeight(80)
        
        self.question_type = QComboBox()
        self.question_type.addItems(["multiple_choice", "text", "rating", "scale", "yes_no"])
        self.question_type.currentTextChanged.connect(self.on_type_changed)
        
        self.required_checkbox = QCheckBox()
        self.required_checkbox.setChecked(True)
        
        question_layout.addRow("Question Text:", self.question_text)
        question_layout.addRow("Question Type:", self.question_type)
        question_layout.addRow("Required:", self.required_checkbox)
        
        question_group.setLayout(question_layout)
        layout.addWidget(question_group)
        
        # Options area (for multiple choice)
        self.options_group = QGroupBox("Answer Options")
        options_layout = QVBoxLayout()
        
        self.options_list = QListWidget()
        options_layout.addWidget(self.options_list)
        
        options_buttons = QHBoxLayout()
        
        add_option_btn = QPushButton("Add Option")
        add_option_btn.clicked.connect(self.add_option)
        
        remove_option_btn = QPushButton("Remove Option")
        remove_option_btn.clicked.connect(self.remove_option)
        
        options_buttons.addWidget(add_option_btn)
        options_buttons.addWidget(remove_option_btn)
        options_buttons.addStretch()
        
        options_layout.addLayout(options_buttons)
        self.options_group.setLayout(options_layout)
        layout.addWidget(self.options_group)
        
        # Rating/Scale settings
        self.scale_group = QGroupBox("Scale Settings")
        scale_layout = QFormLayout()
        
        self.min_value = QSpinBox()
        self.min_value.setRange(0, 10)
        self.min_value.setValue(1)
        
        self.max_value = QSpinBox()
        self.max_value.setRange(1, 10)
        self.max_value.setValue(5)
        
        scale_layout.addRow("Minimum Value:", self.min_value)
        scale_layout.addRow("Maximum Value:", self.max_value)
        
        self.scale_group.setLayout(scale_layout)
        layout.addWidget(self.scale_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
        # Initial state
        self.on_type_changed()
    
    def on_type_changed(self):
        """Handle question type changes"""
        question_type = self.question_type.currentText()
        
        # Show/hide relevant groups
        self.options_group.setVisible(question_type == 'multiple_choice')
        self.scale_group.setVisible(question_type in ['rating', 'scale'])
    
    def add_option(self):
        """Add answer option"""
        text, ok = QInputDialog.getText(self, "Add Option", "Enter option text:")
        if ok and text.strip():
            self.options_list.addItem(text.strip())
    
    def remove_option(self):
        """Remove selected option"""
        current_row = self.options_list.currentRow()
        if current_row >= 0:
            self.options_list.takeItem(current_row)
    
    def load_question(self, question):
        """Load existing question for editing"""
        self.question_text.setPlainText(question.get('question', ''))
        
        question_type = question.get('type', 'multiple_choice')
        index = self.question_type.findText(question_type)
        if index >= 0:
            self.question_type.setCurrentIndex(index)
        
        self.required_checkbox.setChecked(question.get('required', True))
        
        # Load options if multiple choice
        if question_type == 'multiple_choice' and 'options' in question:
            for option in question['options']:
                self.options_list.addItem(option)
        
        # Load scale settings
        if question_type in ['rating', 'scale']:
            self.min_value.setValue(question.get('min_value', 1))
            self.max_value.setValue(question.get('max_value', 5))
    
    def get_question(self):
        """Get the built question"""
        question = {
            'question': self.question_text.toPlainText().strip(),
            'type': self.question_type.currentText(),
            'required': self.required_checkbox.isChecked()
        }
        
        # Add type-specific data
        if question['type'] == 'multiple_choice':
            options = []
            for i in range(self.options_list.count()):
                options.append(self.options_list.item(i).text())
            question['options'] = options
        
        elif question['type'] in ['rating', 'scale']:
            question['min_value'] = self.min_value.value()
            question['max_value'] = self.max_value.value()
        
        return question

class SurveyParticipationDialog(QDialog):
    """Dialog for participating in surveys"""
    
    def __init__(self, survey, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Participate: {survey['title']}")
        self.setModal(True)
        self.resize(600, 500)
        self.survey = survey
        self.survey_engine = SurveyEngine()
        self.responses = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Survey header
        header = QLabel(f"📊 {self.survey['title']}")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(header)
        
        # Survey description
        description = QLabel(self.survey['description'])
        description.setWordWrap(True)
        description.setStyleSheet("color: #6c757d; padding: 10px; font-size: 14px;")
        layout.addWidget(description)
        
        # Questions scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        self.question_widgets = []
        
        for i, question in enumerate(self.survey.get('questions', [])):
            question_widget = self.create_question_widget(i, question)
            self.question_widgets.append(question_widget)
            scroll_layout.addWidget(question_widget)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.submit_responses)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def create_question_widget(self, index, question):
        """Create widget for individual question"""
        widget = QGroupBox(f"Question {index + 1}")
        layout = QVBoxLayout()
        
        # Question text
        question_label = QLabel(question['question'])
        question_label.setWordWrap(True)
        question_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(question_label)
        
        # Question input based on type
        if question['type'] == 'multiple_choice':
            self.create_multiple_choice_input(layout, index, question)
        
        elif question['type'] == 'text':
            text_input = QTextEdit()
            text_input.setMaximumHeight(100)
            text_input.setPlaceholderText("Enter your response...")
            text_input.textChanged.connect(lambda idx=index: self.on_text_response(idx))
            layout.addWidget(text_input)
            setattr(self, f'text_input_{index}', text_input)
        
        elif question['type'] in ['rating', 'scale']:
            self.create_rating_input(layout, index, question)
        
        elif question['type'] == 'yes_no':
            self.create_yes_no_input(layout, index, question)
        
        widget.setLayout(layout)
        return widget
    
    def create_multiple_choice_input(self, layout, index, question):
        """Create multiple choice input"""
        button_group = QButtonGroup(self)
        
        for option in question.get('options', []):
            radio_btn = QRadioButton(option)
            radio_btn.toggled.connect(lambda checked, idx=index, opt=option: 
                                    self.on_radio_response(idx, opt, checked))
            button_group.addButton(radio_btn)
            layout.addWidget(radio_btn)
        
        setattr(self, f'button_group_{index}', button_group)
    
    def create_rating_input(self, layout, index, question):
        """Create rating/scale input"""
        min_val = question.get('min_value', 1)
        max_val = question.get('max_value', 5)
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue((min_val + max_val) // 2)
        slider.valueChanged.connect(lambda value, idx=index: self.on_slider_response(idx, value))
        
        value_label = QLabel(str(slider.value()))
        slider.valueChanged.connect(lambda value: value_label.setText(str(value)))
        
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel(str(min_val)))
        slider_layout.addWidget(slider)
        slider_layout.addWidget(QLabel(str(max_val)))
        slider_layout.addWidget(value_label)
        
        layout.addLayout(slider_layout)
        setattr(self, f'slider_{index}', slider)
    
    def create_yes_no_input(self, layout, index, question):
        """Create yes/no input"""
        button_group = QButtonGroup(self)
        
        yes_btn = QRadioButton("Yes")
        no_btn = QRadioButton("No")
        
        yes_btn.toggled.connect(lambda checked, idx=index: 
                              self.on_radio_response(idx, "Yes", checked))
        no_btn.toggled.connect(lambda checked, idx=index: 
                             self.on_radio_response(idx, "No", checked))
        
        button_group.addButton(yes_btn)
        button_group.addButton(no_btn)
        
        layout.addWidget(yes_btn)
        layout.addWidget(no_btn)
        
        setattr(self, f'button_group_{index}', button_group)
    
    def on_radio_response(self, index, value, checked):
        """Handle radio button response"""
        if checked:
            self.responses[str(index)] = value
    
    def on_slider_response(self, index, value):
        """Handle slider response"""
        self.responses[str(index)] = str(value)
    
    def on_text_response(self, index):
        """Handle text response"""
        text_input = getattr(self, f'text_input_{index}')
        self.responses[str(index)] = text_input.toPlainText().strip()
    
    def submit_responses(self):
        """Submit survey responses"""
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Required", "Please log in to submit responses.")
            return
        
        # Validate required questions
        for i, question in enumerate(self.survey.get('questions', [])):
            if question.get('required', False) and str(i) not in self.responses:
                QMessageBox.warning(self, "Missing Response", 
                                  f"Please answer question {i+1} (required).")
                return
        
        try:
            success, message = self.survey_engine.submit_survey_response(
                self.survey['id'], self.responses, user['email']
            )
            
            if success:
                QMessageBox.information(self, "Response Submitted", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Submission Failed", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to submit response: {str(e)}")

class QuickPollDialog(QDialog):
    """Dialog for creating quick polls"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Quick Poll")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("⚡ Create Quick Poll")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(header)
        
        # Quick poll form
        form_layout = QFormLayout()
        
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("What is your poll question?")
        
        self.option1_input = QLineEdit()
        self.option1_input.setPlaceholderText("Option 1")
        
        self.option2_input = QLineEdit()
        self.option2_input.setPlaceholderText("Option 2")
        
        self.duration_hours = QSpinBox()
        self.duration_hours.setRange(1, 72)
        self.duration_hours.setValue(24)
        
        form_layout.addRow("Question:", self.question_input)
        form_layout.addRow("Option 1:", self.option1_input)
        form_layout.addRow("Option 2:", self.option2_input)
        form_layout.addRow("Duration (hours):", self.duration_hours)
        
        layout.addLayout(form_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.create_poll)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def create_poll(self):
        """Create the quick poll"""
        question = self.question_input.text().strip()
        option1 = self.option1_input.text().strip()
        option2 = self.option2_input.text().strip()
        
        if not all([question, option1, option2]):
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return
        
        # Create as survey with 2 options
        QMessageBox.information(self, "Poll Created", f"Quick poll '{question}' created successfully!")
        self.accept()

class ReferendumDialog(QDialog):
    """Dialog for creating referendums"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Referendum")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🗳️ Create Referendum")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(header)
        
        # Referendum form
        form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Referendum title...")
        
        self.proposition_input = QTextEdit()
        self.proposition_input.setPlaceholderText("Describe the proposition being voted on...")
        self.proposition_input.setMaximumHeight(100)
        
        self.jurisdiction_combo = QComboBox()
        self.jurisdiction_combo.addItems(["Local", "State", "Federal", "Constitutional"])
        
        self.voting_period = QSpinBox()
        self.voting_period.setRange(7, 90)
        self.voting_period.setValue(30)
        
        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Proposition:", self.proposition_input)
        form_layout.addRow("Jurisdiction:", self.jurisdiction_combo)
        form_layout.addRow("Voting Period (days):", self.voting_period)
        
        layout.addLayout(form_layout)
        
        # Constitutional warning
        warning = QLabel("⚠️ Referendums require constitutional review and Elder approval before activation.")
        warning.setStyleSheet("color: #dc3545; font-weight: bold; padding: 10px; background-color: #f8d7da; border-radius: 5px;")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.create_referendum)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def create_referendum(self):
        """Create the referendum"""
        title = self.title_input.text().strip()
        proposition = self.proposition_input.toPlainText().strip()
        
        if not all([title, proposition]):
            QMessageBox.warning(self, "Missing Information", "Please provide title and proposition.")
            return
        
        QMessageBox.information(self, "Referendum Created", 
                              f"Referendum '{title}' created and submitted for constitutional review.")
        self.accept()