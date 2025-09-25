# Analytics Module - UI Components for Data Visualization
"""
Analytics UI components providing:
- Interactive dashboards for civic engagement metrics
- Data visualizations and charts
- Report generation and export capabilities
- Real-time analytics monitoring
"""

from typing import Optional, Any, Dict, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTabWidget, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem,
                            QComboBox, QDateEdit, QTextEdit, QProgressBar, QMessageBox,
                            QHeaderView, QFrame, QSplitter, QListWidget, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QColor, QPalette
from .backend import AnalyticsEngine
from ..users.session import SessionManager
from ..users.backend import UserBackend

class AnalyticsTab(QWidget):
    """Main analytics interface for data-driven governance insights"""
    
    # Signal for refreshing other tabs
    analytics_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.analytics_engine = AnalyticsEngine()
        self.current_report = None
        self.auto_refresh_enabled = True
        self.init_ui()
        
        # Auto-refresh timer for real-time updates
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_analytics)
        self.refresh_timer.start(60000)  # Refresh every minute
    
    def init_ui(self):
        """Initialize the analytics interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Blockchain status and user role display
        user = SessionManager.get_current_user()
        role = user.get('role', 'Unknown') if user else 'Unknown'
        
        blockchain_status = QLabel("All analytics queries and reports are <b>recorded on blockchain</b> for transparency.")
        blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
        blockchain_status.setAccessibleName("Blockchain Status")
        blockchain_status.setToolTip("All analytics activities are transparently recorded on the blockchain.")
        
        role_label = QLabel(f"Your Role: <b>{role}</b>")
        role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
        role_label.setAccessibleName("User Role")
        role_label.setToolTip("Your current platform role determines analytics access levels.")
        
        # Export and settings buttons
        export_btn = QPushButton("Export Analytics Report")
        export_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        export_btn.setAccessibleName("Export Analytics Report Button")
        export_btn.setToolTip("Generate and export comprehensive analytics reports.")
        export_btn.setMinimumHeight(40)
        export_btn.setMinimumWidth(200)
        export_btn.clicked.connect(self.export_report)
        
        auto_refresh_btn = QPushButton("Toggle Auto-Refresh")
        auto_refresh_btn.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        auto_refresh_btn.clicked.connect(self.toggle_auto_refresh)
        
        top_layout = QVBoxLayout()
        top_layout.addWidget(blockchain_status)
        top_layout.addWidget(role_label)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(export_btn)
        button_layout.addWidget(auto_refresh_btn)
        button_layout.addStretch()
        top_layout.addLayout(button_layout)
        
        layout.addLayout(top_layout)
        
        # Header
        header = QLabel("📊 Analytics & Governance Insights")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
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
        
        # Create main analytics interface for logged-in users
        self.create_analytics_interface()
    
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
        
        icon_label = QLabel("🔒")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; color: #6c757d;")
        
        title_label = QLabel("Analytics Access Required")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #495057; margin-bottom: 10px;")
        
        message_label = QLabel("Please log in to access platform analytics and governance insights.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 16px; color: #6c757d; margin-bottom: 20px;")
        message_label.setWordWrap(True)
        
        frame_layout.addWidget(icon_label)
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(message_label)
        
        login_frame.setLayout(frame_layout)
        layout.addWidget(login_frame)
    
    def create_analytics_interface(self):
        """Create the main analytics interface for authenticated users"""
        layout = self.main_content.layout()
        
        # Main analytics tabs
        self.analytics_tabs = QTabWidget()
        self.analytics_tabs.setStyleSheet("""
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
                background: #3498db;
                color: white;
                font-weight: bold;
            }
        """)
        
        # Add analytics tabs
        self.analytics_tabs.addTab(self.create_participation_tab(), "📈 Participation")
        self.analytics_tabs.addTab(self.create_governance_tab(), "🏛️ Governance")
        self.analytics_tabs.addTab(self.create_platform_tab(), "⚙️ Platform Health")
        self.analytics_tabs.addTab(self.create_reports_tab(), "📋 Reports")
        
        layout.addWidget(self.analytics_tabs)
        
        # Load initial analytics data
        self.refresh_analytics()
    
    def create_participation_tab(self) -> QWidget:
        """Create the participation analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Summary metrics
        metrics_group = QGroupBox("Civic Engagement Metrics")
        metrics_layout = QGridLayout()
        
        self.total_users_label = QLabel("Total Users: Loading...")
        self.debate_engagement_label = QLabel("Debate Actions: Loading...")
        self.voting_participation_label = QLabel("Votes Cast: Loading...")
        self.training_completions_label = QLabel("Training Completions: Loading...")
        
        metrics_layout.addWidget(self.total_users_label, 0, 0)
        metrics_layout.addWidget(self.debate_engagement_label, 0, 1)
        metrics_layout.addWidget(self.voting_participation_label, 1, 0)
        metrics_layout.addWidget(self.training_completions_label, 1, 1)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # Top contributors table
        contributors_group = QGroupBox("Top Contributors")
        contributors_layout = QVBoxLayout()
        
        self.contributors_table = QTableWidget()
        self.contributors_table.setColumnCount(6)
        self.contributors_table.setHorizontalHeaderLabels([
            "User", "Total Actions", "Debates", "Votes", "Training", "Moderation"
        ])
        self.contributors_table.horizontalHeader().setStretchLastSection(True)
        
        contributors_layout.addWidget(self.contributors_table)
        contributors_group.setLayout(contributors_layout)
        layout.addWidget(contributors_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_governance_tab(self) -> QWidget:
        """Create the governance effectiveness tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Governance metrics
        governance_group = QGroupBox("Governance Effectiveness")
        governance_layout = QGridLayout()
        
        self.decisions_label = QLabel("Decisions Made: Loading...")
        self.amendments_label = QLabel("Amendment Proposals: Loading...")
        self.elder_reviews_label = QLabel("Elder Reviews: Loading...")
        self.compliance_label = QLabel("Constitutional Compliance: Loading...")
        
        governance_layout.addWidget(self.decisions_label, 0, 0)
        governance_layout.addWidget(self.amendments_label, 0, 1)
        governance_layout.addWidget(self.elder_reviews_label, 1, 0)
        governance_layout.addWidget(self.compliance_label, 1, 1)
        
        governance_group.setLayout(governance_layout)
        layout.addWidget(governance_group)
        
        # Governance timeline
        timeline_group = QGroupBox("Recent Governance Activity")
        timeline_layout = QVBoxLayout()
        
        self.governance_timeline = QListWidget()
        timeline_layout.addWidget(self.governance_timeline)
        
        timeline_group.setLayout(timeline_layout)
        layout.addWidget(timeline_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_platform_tab(self) -> QWidget:
        """Create the platform health tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Health metrics
        health_group = QGroupBox("Platform Health Status")
        health_layout = QVBoxLayout()
        
        self.health_score_label = QLabel("Health Score: Loading...")
        self.health_score_progress = QProgressBar()
        self.health_score_progress.setRange(0, 100)
        
        self.total_actions_label = QLabel("Total Actions: Loading...")
        self.error_count_label = QLabel("Error Count: Loading...")
        self.security_events_label = QLabel("Security Events: Loading...")
        self.system_status_label = QLabel("System Status: Loading...")
        
        health_layout.addWidget(self.health_score_label)
        health_layout.addWidget(self.health_score_progress)
        health_layout.addWidget(self.total_actions_label)
        health_layout.addWidget(self.error_count_label)
        health_layout.addWidget(self.security_events_label)
        health_layout.addWidget(self.system_status_label)
        
        health_group.setLayout(health_layout)
        layout.addWidget(health_group)
        
        # Performance metrics
        performance_group = QGroupBox("Performance Metrics")
        performance_layout = QVBoxLayout()
        
        self.performance_info = QTextEdit()
        self.performance_info.setReadOnly(True)
        self.performance_info.setMaximumHeight(200)
        
        performance_layout.addWidget(self.performance_info)
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_reports_tab(self) -> QWidget:
        """Create the reports generation tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Report generation controls
        controls_group = QGroupBox("Report Generation")
        controls_layout = QVBoxLayout()
        
        report_type_layout = QHBoxLayout()
        report_type_layout.addWidget(QLabel("Report Type:"))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Participation Analytics",
            "Governance Effectiveness", 
            "Platform Health",
            "Comprehensive Report"
        ])
        report_type_layout.addWidget(self.report_type_combo)
        
        generate_btn = QPushButton("Generate Report")
        generate_btn.setStyleSheet("background-color: #007bff; color: white; padding: 8px 16px; border-radius: 5px;")
        generate_btn.clicked.connect(self.generate_custom_report)
        report_type_layout.addWidget(generate_btn)
        
        controls_layout.addLayout(report_type_layout)
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Report display area
        display_group = QGroupBox("Generated Report")
        display_layout = QVBoxLayout()
        
        self.report_display = QTextEdit()
        self.report_display.setReadOnly(True)
        
        display_layout.addWidget(self.report_display)
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        widget.setLayout(layout)
        return widget
    
    def refresh_analytics(self):
        """Refresh all analytics data"""
        if not SessionManager.is_authenticated():
            return
        
        try:
            # Update participation analytics
            participation_data = self.analytics_engine.generate_participation_analytics()
            self.update_participation_display(participation_data)
            
            # Update governance analytics
            governance_data = self.analytics_engine.generate_governance_analytics()
            self.update_governance_display(governance_data)
            
            # Update platform health analytics
            health_data = self.analytics_engine.generate_platform_health_analytics()
            self.update_platform_display(health_data)
            
        except Exception as e:
            print(f"Error refreshing analytics: {e}")
    
    def update_participation_display(self, data: Dict[str, Any]):
        """Update the participation analytics display"""
        if 'error' in data:
            return
            
        self.total_users_label.setText(f"Total Users: {data.get('total_users', 0)}")
        self.debate_engagement_label.setText(f"Debate Actions: {data.get('debate_engagement', 0)}")
        self.voting_participation_label.setText(f"Votes Cast: {data.get('voting_participation', 0)}")
        self.training_completions_label.setText(f"Training Completions: {data.get('training_completions', 0)}")
        
        # Update contributors table
        contributors = data.get('top_contributors', [])
        self.contributors_table.setRowCount(len(contributors))
        
        for i, contributor in enumerate(contributors):
            self.contributors_table.setItem(i, 0, QTableWidgetItem(contributor.get('email', '')))
            self.contributors_table.setItem(i, 1, QTableWidgetItem(str(contributor.get('total_actions', 0))))
            self.contributors_table.setItem(i, 2, QTableWidgetItem(str(contributor.get('debates', 0))))
            self.contributors_table.setItem(i, 3, QTableWidgetItem(str(contributor.get('votes', 0))))
            self.contributors_table.setItem(i, 4, QTableWidgetItem(str(contributor.get('training', 0))))
            self.contributors_table.setItem(i, 5, QTableWidgetItem(str(contributor.get('moderation', 0))))
    
    def update_governance_display(self, data: Dict[str, Any]):
        """Update the governance analytics display"""
        if 'error' in data:
            return
            
        self.decisions_label.setText(f"Decisions Made: {data.get('decisions_made', 0)}")
        self.amendments_label.setText(f"Amendment Proposals: {data.get('amendment_proposals', 0)}")
        self.elder_reviews_label.setText(f"Elder Reviews: {data.get('elder_reviews', 0)}")
        self.compliance_label.setText(f"Constitutional Compliance: {data.get('constitutional_compliance', 0)}")
        
        # Update governance timeline
        self.governance_timeline.clear()
        timeline = data.get('governance_timeline', [])
        
        for event in timeline[-20:]:  # Show last 20 events
            event_text = f"[{event.get('type', '')}] {event.get('action', '')} - {event.get('timestamp', '')}"
            self.governance_timeline.addItem(event_text)
    
    def update_platform_display(self, data: Dict[str, Any]):
        """Update the platform health display"""
        if 'error' in data:
            return
        
        health_score = data.get('platform_health_score', 0)
        self.health_score_label.setText(f"Health Score: {health_score}%")
        self.health_score_progress.setValue(int(health_score))
        
        # Set progress bar color based on health score
        if health_score >= 90:
            color = "#28a745"  # Green
        elif health_score >= 70:
            color = "#ffc107"  # Yellow
        else:
            color = "#dc3545"  # Red
            
        self.health_score_progress.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        
        self.total_actions_label.setText(f"Total Actions: {data.get('total_platform_actions', 0)}")
        self.error_count_label.setText(f"Error Count: {data.get('error_count', 0)}")
        self.security_events_label.setText(f"Security Events: {data.get('security_events', 0)}")
        self.system_status_label.setText(f"System Status: {data.get('system_status', 'Unknown')}")
        
        # Update performance metrics
        performance = data.get('performance_metrics', {})
        performance_text = f"""
Performance Metrics:
- Total Transactions: {performance.get('total_transactions', 0)}
- Daily Average: {performance.get('daily_average', 0):.1f}
- Peak Activity: {performance.get('peak_activity', 0)}
- System Uptime: {performance.get('system_uptime', 'N/A')}

Recent Activity: {data.get('recent_activity_count', 0)} actions in the last 30 days
        """.strip()
        
        self.performance_info.setPlainText(performance_text)
    
    def generate_custom_report(self):
        """Generate a custom analytics report"""
        report_type_map = {
            "Participation Analytics": "participation",
            "Governance Effectiveness": "governance",
            "Platform Health": "platform_health",
            "Comprehensive Report": "comprehensive"
        }
        
        selected_type = self.report_type_combo.currentText()
        report_type = report_type_map.get(selected_type, "participation")
        
        try:
            report_data = self.analytics_engine.export_analytics_report(report_type)
            
            if 'error' in report_data:
                QMessageBox.warning(self, "Report Generation Error", 
                                  f"Error generating report: {report_data['error']}")
                return
            
            # Format and display the report
            self.format_and_display_report(report_data)
            self.current_report = report_data
            
        except Exception as e:
            QMessageBox.critical(self, "Report Error", f"Failed to generate report: {e}")
    
    def format_and_display_report(self, report_data: Dict[str, Any]):
        """Format and display the generated report"""
        report_text = f"""
CIVIC ENGAGEMENT PLATFORM - ANALYTICS REPORT
Report Type: {report_data.get('report_type', 'Unknown')}
Generated By: {report_data.get('exported_by', 'Unknown')}
Generated At: {report_data.get('export_timestamp', 'Unknown')}

{'-' * 60}

"""
        
        data = report_data.get('data', {})
        
        if isinstance(data, dict):
            if 'participation' in data:
                report_text += self._format_participation_section(data['participation'])
            if 'governance' in data:
                report_text += self._format_governance_section(data['governance'])
            if 'platform_health' in data:
                report_text += self._format_health_section(data['platform_health'])
            
            # If it's not a comprehensive report, format the single section
            if 'total_users' in data:  # Participation report
                report_text += self._format_participation_section(data)
            elif 'decisions_made' in data:  # Governance report
                report_text += self._format_governance_section(data)
            elif 'platform_health_score' in data:  # Health report
                report_text += self._format_health_section(data)
        
        self.report_display.setPlainText(report_text)
    
    def _format_participation_section(self, data: Dict[str, Any]) -> str:
        """Format participation analytics section"""
        section = """
PARTICIPATION ANALYTICS:
------------------------
Total Users: {total_users}
Debate Engagement: {debate_engagement} actions
Voting Participation: {voting_participation} votes
Training Completions: {training_completions}

Engagement Trends: {trend_status}

Top Contributors:
""".format(
            total_users=data.get('total_users', 0),
            debate_engagement=data.get('debate_engagement', 0),
            voting_participation=data.get('voting_participation', 0),
            training_completions=data.get('training_completions', 0),
            trend_status=data.get('engagement_trends', {}).get('trend', 'N/A')
        )
        
        contributors = data.get('top_contributors', [])[:5]  # Top 5
        for i, contributor in enumerate(contributors, 1):
            section += f"  {i}. {contributor.get('email', 'Unknown')} - {contributor.get('total_actions', 0)} actions\n"
        
        return section + "\n"
    
    def _format_governance_section(self, data: Dict[str, Any]) -> str:
        """Format governance analytics section"""
        section = """
GOVERNANCE EFFECTIVENESS:
-------------------------
Decisions Made: {decisions}
Amendment Proposals: {amendments}
Elder Reviews: {elder_reviews}
Constitutional Compliance Events: {compliance}

Decision Efficiency: {efficiency:.1f}%
Constitutional Health: {health_status}

""".format(
            decisions=data.get('decisions_made', 0),
            amendments=data.get('amendment_proposals', 0),
            elder_reviews=data.get('elder_reviews', 0),
            compliance=data.get('constitutional_compliance', 0),
            efficiency=data.get('decision_efficiency', {}).get('efficiency_score', 0),
            health_status=data.get('constitutional_health', {}).get('health_status', 'Unknown')
        )
        
        return section
    
    def _format_health_section(self, data: Dict[str, Any]) -> str:
        """Format platform health section"""
        section = """
PLATFORM HEALTH:
----------------
Health Score: {health_score}%
Total Platform Actions: {total_actions}
Error Count: {errors}
Security Events: {security}
System Status: {status}

Performance Metrics:
- Recent Activity (30 days): {recent_activity}
- Daily Average: {daily_avg:.1f}

""".format(
            health_score=data.get('platform_health_score', 0),
            total_actions=data.get('total_platform_actions', 0),
            errors=data.get('error_count', 0),
            security=data.get('security_events', 0),
            status=data.get('system_status', 'Unknown'),
            recent_activity=data.get('recent_activity_count', 0),
            daily_avg=data.get('performance_metrics', {}).get('daily_average', 0)
        )
        
        return section
    
    def export_report(self):
        """Export comprehensive analytics report"""
        try:
            report_data = self.analytics_engine.export_analytics_report("comprehensive")
            
            if 'error' in report_data:
                QMessageBox.warning(self, "Export Error", 
                                  f"Error exporting report: {report_data['error']}")
                return
            
            # In a real implementation, this would save to file
            # For now, just show success message
            QMessageBox.information(self, "Export Successful", 
                                  "Analytics report has been generated and recorded on blockchain.")
            
            # Format and display the report
            self.format_and_display_report(report_data)
            self.current_report = report_data
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export report: {e}")
    
    def toggle_auto_refresh(self):
        """Toggle automatic refresh of analytics data"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        
        if self.auto_refresh_enabled:
            self.refresh_timer.start(60000)
            QMessageBox.information(self, "Auto-Refresh", "Auto-refresh enabled. Analytics will update every minute.")
        else:
            self.refresh_timer.stop()
            QMessageBox.information(self, "Auto-Refresh", "Auto-refresh disabled. Use manual refresh as needed.")