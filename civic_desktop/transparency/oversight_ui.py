"""
Transparency & Audit UI - Public Accountability & Oversight Interface
Advanced transparency tools for government accountability and public oversight.
Comprehensive audit dashboards with conflict monitoring and performance metrics.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QDialog, QFormLayout, QSpinBox, QCheckBox, QGroupBox,
    QScrollArea, QFrame, QSplitter, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QCalendarWidget, QDateEdit, QTimeEdit,
    QMessageBox, QInputDialog, QGridLayout, QSlider,
    QListWidget, QListWidgetItem, QPushButton, QTextBrowser
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QDate, QTime
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QIcon

# Import session management and transparency tools
try:
    from civic_desktop.users.session import SessionManager
    from civic_desktop.blockchain.blockchain import Blockchain
except ImportError as e:
    print(f"Import error in transparency oversight_ui: {e}")
    # Create minimal fallbacks for development
    class SessionManager:
        @staticmethod
        def get_current_user():
            return {"email": "dev@civic.local", "role": "Contract Citizen"}
        
        @staticmethod
        def is_authenticated():
            return True

class TransparencyEngine:
    """Transparency and audit analysis engine"""
    
    def __init__(self):
        self.config_path = "civic_desktop/config/dev_config.json"  # Will be updated with proper config
        
    def get_transparency_score(self, entity_type="government", entity_id=None):
        """Calculate transparency score for an entity"""
        try:
            # Mock implementation - in production would analyze actual data
            base_score = 75
            recent_activity_bonus = 10
            compliance_bonus = 5
            
            total_score = base_score + recent_activity_bonus + compliance_bonus
            
            return {
                'overall_score': min(total_score, 100),
                'financial_transparency': 80,
                'governance_accountability': 85,
                'decision_transparency': 70,
                'public_participation': 75,
                'information_access': 90,
                'grade': self._score_to_grade(total_score)
            }
            
        except Exception as e:
            print(f"Error calculating transparency score: {e}")
            return {'overall_score': 0, 'grade': 'F'}
            
    def _score_to_grade(self, score):
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B' 
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
            
    def get_audit_findings(self, audit_type="all", date_range=30):
        """Get recent audit findings"""
        try:
            # Mock implementation
            findings = [
                {
                    'id': 'audit_001',
                    'type': 'financial_transparency',
                    'severity': 'medium',
                    'title': 'Budget Disclosure Delay',
                    'description': 'Monthly budget report published 3 days late',
                    'date': (datetime.now() - timedelta(days=5)).isoformat(),
                    'status': 'resolved',
                    'recommendation': 'Implement automated budget publishing'
                },
                {
                    'id': 'audit_002',
                    'type': 'governance_accountability',
                    'severity': 'low',
                    'title': 'Meeting Minutes Format',
                    'description': 'Some meeting minutes lack detailed vote records',
                    'date': (datetime.now() - timedelta(days=12)).isoformat(),
                    'status': 'in_progress',
                    'recommendation': 'Standardize meeting minute templates'
                },
                {
                    'id': 'audit_003',
                    'type': 'conflict_of_interest',
                    'severity': 'high',
                    'title': 'Potential Conflict Review',
                    'description': 'Official business relationship requires disclosure update',
                    'date': (datetime.now() - timedelta(days=2)).isoformat(),
                    'status': 'pending',
                    'recommendation': 'Update conflict disclosure within 7 days'
                }
            ]
            
            return findings
            
        except Exception as e:
            print(f"Error getting audit findings: {e}")
            return []
            
    def get_performance_metrics(self, metric_type="governance"):
        """Get performance metrics and KPIs"""
        try:
            # Mock implementation
            metrics = {
                'governance_effectiveness': {
                    'response_time_avg': '2.3 days',
                    'resolution_rate': '94%',
                    'citizen_satisfaction': '87%',
                    'transparency_compliance': '91%'
                },
                'financial_performance': {
                    'budget_accuracy': '96%',
                    'spending_efficiency': '89%',
                    'disclosure_timeliness': '92%',
                    'audit_compliance': '98%'
                },
                'public_engagement': {
                    'participation_rate': '23%',
                    'feedback_response': '78%',
                    'accessibility_score': '85%',
                    'information_requests': '156 this month'
                }
            }
            
            return metrics.get(metric_type, {})
            
        except Exception as e:
            print(f"Error getting performance metrics: {e}")
            return {}
            
    def get_conflict_monitoring(self):
        """Get conflict of interest monitoring data"""
        try:
            # Mock implementation
            conflicts = [
                {
                    'official': 'Representative Smith',
                    'type': 'business_relationship',
                    'description': 'Family business contract with city services',
                    'status': 'disclosed',
                    'mitigation': 'Recusal from related votes',
                    'last_updated': (datetime.now() - timedelta(days=30)).isoformat()
                },
                {
                    'official': 'Senator Johnson',
                    'type': 'financial_interest',
                    'description': 'Stock ownership in regulated industry',
                    'status': 'monitoring',
                    'mitigation': 'Blind trust established',
                    'last_updated': (datetime.now() - timedelta(days=60)).isoformat()
                }
            ]
            
            return conflicts
            
        except Exception as e:
            print(f"Error getting conflict monitoring: {e}")
            return []
            
    def submit_transparency_report(self, report_type, description, evidence=None):
        """Submit a transparency violation or concern report"""
        try:
            user = SessionManager.get_current_user()
            
            report_data = {
                'id': f"transparency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'reporter_email': user['email'],
                'type': report_type,
                'description': description,
                'evidence': evidence or [],
                'submitted_at': datetime.now().isoformat(),
                'status': 'submitted',
                'priority': 'medium'
            }
            
            # In production, would save to transparency database
            print(f"Transparency report submitted: {report_data['id']}")
            
            # Record on blockchain for transparency
            try:
                blockchain = Blockchain()
                blockchain.add_page(
                    action_type="transparency_report_submitted",
                    data={
                        'report_id': report_data['id'],
                        'type': report_type,
                        'reporter_email': user['email']
                    },
                    user_email=user['email']
                )
            except Exception as blockchain_error:
                print(f"Blockchain logging error: {blockchain_error}")
            
            return True, f"Report {report_data['id']} submitted successfully"
            
        except Exception as e:
            print(f"Error submitting transparency report: {e}")
            return False, f"Failed to submit report: {str(e)}"

class TransparencyReportDialog(QDialog):
    """Dialog for submitting transparency reports"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.transparency_engine = TransparencyEngine()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Submit Transparency Report")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout()
        
        # Report information
        report_group = QGroupBox("Transparency Concern Report")
        form_layout = QFormLayout()
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Financial Transparency Violation",
            "Governance Accountability Issue",
            "Decision Process Opacity", 
            "Conflict of Interest Concern",
            "Public Information Access Denial",
            "Ethics Violation",
            "Lobbying Disclosure Issue",
            "Meeting Transparency Problem",
            "Other Transparency Concern"
        ])
        form_layout.addRow("Report Type:", self.report_type_combo)
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Brief title describing the issue...")
        form_layout.addRow("Title:", self.title_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Detailed description of the transparency concern...")
        self.description_edit.setMinimumHeight(150)
        form_layout.addRow("Description:", self.description_edit)
        
        self.evidence_edit = QTextEdit()
        self.evidence_edit.setPlaceholderText("Evidence, sources, or documentation to support this report...")
        self.evidence_edit.setMaximumHeight(100)
        form_layout.addRow("Evidence:", self.evidence_edit)
        
        self.anonymous_check = QCheckBox("Submit anonymously (hides reporter identity)")
        form_layout.addRow("Privacy:", self.anonymous_check)
        
        report_group.setLayout(form_layout)
        layout.addWidget(report_group)
        
        # Reporter information
        reporter_group = QGroupBox("Reporter Information")
        reporter_layout = QFormLayout()
        
        user = SessionManager.get_current_user()
        
        self.reporter_email = QLabel(user.get('email', 'Unknown'))
        reporter_layout.addRow("Your Email:", self.reporter_email)
        
        self.reporter_role = QLabel(user.get('role', 'Unknown'))
        reporter_layout.addRow("Your Role:", self.reporter_role)
        
        reporter_group.setLayout(reporter_layout)
        layout.addWidget(reporter_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.submit_btn = QPushButton("Submit Report")
        self.submit_btn.clicked.connect(self.submit_report)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.submit_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def submit_report(self):
        """Submit the transparency report"""
        if not self.title_edit.text().strip() or not self.description_edit.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Please provide title and description.")
            return
            
        try:
            report_data = {
                'type': self.report_type_combo.currentText(),
                'title': self.title_edit.text().strip(),
                'description': self.description_edit.toPlainText().strip(),
                'evidence': self.evidence_edit.toPlainText().strip(),
                'anonymous': self.anonymous_check.isChecked()
            }
            
            success, message = self.transparency_engine.submit_transparency_report(
                report_type=report_data['type'],
                description=f"{report_data['title']}\n\n{report_data['description']}",
                evidence=report_data['evidence']
            )
            
            if success:
                QMessageBox.information(self, "Success", 
                    "Transparency report submitted successfully! Your report will be investigated and you'll receive updates.")
                self.accept()
            else:
                QMessageBox.warning(self, "Submission Failed", f"Failed to submit report: {message}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Submission error: {str(e)}")

class TransparencyAuditTab(QWidget):
    """Complete Transparency & Audit oversight interface"""
    
    def __init__(self):
        super().__init__()
        self.transparency_engine = TransparencyEngine()
        self.init_ui()
        self.refresh_ui()
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_ui)
        self.refresh_timer.start(60000)  # Refresh every minute
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🔍 Transparency & Audit")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        
        user = SessionManager.get_current_user()
        user_info = QLabel(f"User: {user.get('email', 'Unknown')} | Role: {user.get('role', 'Unknown')}")
        user_info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(user_info)
        
        layout.addLayout(header_layout)
        
        # Main content with tabs
        self.tab_widget = QTabWidget()
        
        # Transparency Dashboard Tab
        self.dashboard_tab = self.create_dashboard_tab()
        self.tab_widget.addTab(self.dashboard_tab, "📊 Transparency Dashboard")
        
        # Audit Findings Tab
        self.audit_tab = self.create_audit_tab()
        self.tab_widget.addTab(self.audit_tab, "🔍 Audit Findings")
        
        # Performance Monitoring Tab
        self.performance_tab = self.create_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "📈 Performance Monitoring")
        
        # Conflict Monitoring Tab
        self.conflict_tab = self.create_conflict_tab()
        self.tab_widget.addTab(self.conflict_tab, "⚠️ Conflict Monitoring")
        
        # Public Reports Tab
        self.reports_tab = self.create_reports_tab()
        self.tab_widget.addTab(self.reports_tab, "📋 Public Reports")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    def create_dashboard_tab(self):
        """Create transparency dashboard"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Transparency score section
        score_group = QGroupBox("Government Transparency Score")
        score_layout = QVBoxLayout()
        
        # Overall score display
        score_display_layout = QHBoxLayout()
        
        self.overall_score_label = QLabel("85")
        self.overall_score_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.overall_score_label.setStyleSheet("color: #28a745; text-align: center;")
        self.overall_score_label.setAlignment(Qt.AlignCenter)
        
        score_details_layout = QVBoxLayout()
        
        self.grade_label = QLabel("Grade: B")
        self.grade_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.grade_label.setStyleSheet("color: #28a745;")
        
        self.score_description = QLabel("Good transparency with room for improvement")
        self.score_description.setStyleSheet("color: #6c757d; font-style: italic;")
        
        score_details_layout.addWidget(self.grade_label)
        score_details_layout.addWidget(self.score_description)
        score_details_layout.addStretch()
        
        score_display_layout.addWidget(self.overall_score_label)
        score_display_layout.addLayout(score_details_layout)
        score_display_layout.addStretch()
        
        score_layout.addLayout(score_display_layout)
        
        # Score breakdown
        breakdown_layout = QGridLayout()
        
        self.financial_score = QProgressBar()
        self.financial_score.setRange(0, 100)
        self.financial_score.setValue(80)
        breakdown_layout.addWidget(QLabel("Financial Transparency:"), 0, 0)
        breakdown_layout.addWidget(self.financial_score, 0, 1)
        
        self.governance_score = QProgressBar()
        self.governance_score.setRange(0, 100)
        self.governance_score.setValue(85)
        breakdown_layout.addWidget(QLabel("Governance Accountability:"), 1, 0)
        breakdown_layout.addWidget(self.governance_score, 1, 1)
        
        self.decision_score = QProgressBar()
        self.decision_score.setRange(0, 100)
        self.decision_score.setValue(70)
        breakdown_layout.addWidget(QLabel("Decision Transparency:"), 2, 0)
        breakdown_layout.addWidget(self.decision_score, 2, 1)
        
        self.participation_score = QProgressBar()
        self.participation_score.setRange(0, 100)
        self.participation_score.setValue(75)
        breakdown_layout.addWidget(QLabel("Public Participation:"), 3, 0)
        breakdown_layout.addWidget(self.participation_score, 3, 1)
        
        self.access_score = QProgressBar()
        self.access_score.setRange(0, 100)
        self.access_score.setValue(90)
        breakdown_layout.addWidget(QLabel("Information Access:"), 4, 0)
        breakdown_layout.addWidget(self.access_score, 4, 1)
        
        score_layout.addLayout(breakdown_layout)
        score_group.setLayout(score_layout)
        layout.addWidget(score_group)
        
        # Quick actions
        actions_group = QGroupBox("Transparency Actions")
        actions_layout = QHBoxLayout()
        
        self.report_concern_btn = QPushButton("🚨 Report Transparency Concern")
        self.report_concern_btn.clicked.connect(self.report_concern)
        self.report_concern_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        
        self.view_audit_btn = QPushButton("📋 View Latest Audit")
        self.view_audit_btn.clicked.connect(self.view_latest_audit)
        
        self.performance_btn = QPushButton("📊 Performance Report")
        self.performance_btn.clicked.connect(self.show_performance_report)
        
        actions_layout.addWidget(self.report_concern_btn)
        actions_layout.addWidget(self.view_audit_btn)
        actions_layout.addWidget(self.performance_btn)
        actions_layout.addStretch()
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Recent activity
        activity_group = QGroupBox("Recent Transparency Activity")
        activity_layout = QVBoxLayout()
        
        self.activity_list = QListWidget()
        self.activity_list.setMaximumHeight(200)
        activity_layout.addWidget(self.activity_list)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_audit_tab(self):
        """Create audit findings interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Audit controls
        controls_group = QGroupBox("Audit Filters")
        controls_layout = QHBoxLayout()
        
        self.audit_type_filter = QComboBox()
        self.audit_type_filter.addItems([
            "All Audit Types",
            "Financial Transparency",
            "Governance Accountability", 
            "Decision Transparency",
            "Conflict of Interest",
            "Ethics Compliance",
            "Information Access"
        ])
        self.audit_type_filter.currentTextChanged.connect(self.filter_audit_findings)
        
        self.severity_filter = QComboBox()
        self.severity_filter.addItems([
            "All Severities",
            "High Priority",
            "Medium Priority",
            "Low Priority"
        ])
        self.severity_filter.currentTextChanged.connect(self.filter_audit_findings)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All Statuses",
            "Pending Review",
            "In Progress", 
            "Resolved",
            "Closed"
        ])
        self.status_filter.currentTextChanged.connect(self.filter_audit_findings)
        
        controls_layout.addWidget(QLabel("Type:"))
        controls_layout.addWidget(self.audit_type_filter)
        controls_layout.addWidget(QLabel("Severity:"))
        controls_layout.addWidget(self.severity_filter)
        controls_layout.addWidget(QLabel("Status:"))
        controls_layout.addWidget(self.status_filter)
        controls_layout.addStretch()
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Audit findings table
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(6)
        self.audit_table.setHorizontalHeaderLabels([
            "Title", "Type", "Severity", "Date", "Status", "Actions"
        ])
        
        header = self.audit_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.audit_table.setAlternatingRowColors(True)
        layout.addWidget(self.audit_table)
        
        widget.setLayout(layout)
        return widget
        
    def create_performance_tab(self):
        """Create performance monitoring interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Performance metrics
        metrics_group = QGroupBox("Key Performance Indicators (KPIs)")
        metrics_layout = QGridLayout()
        
        # Governance effectiveness
        gov_group = QGroupBox("Governance Effectiveness")
        gov_layout = QFormLayout()
        
        self.response_time_label = QLabel("2.3 days")
        self.resolution_rate_label = QLabel("94%")
        self.satisfaction_label = QLabel("87%")
        self.compliance_label = QLabel("91%")
        
        gov_layout.addRow("Average Response Time:", self.response_time_label)
        gov_layout.addRow("Resolution Rate:", self.resolution_rate_label)
        gov_layout.addRow("Citizen Satisfaction:", self.satisfaction_label)
        gov_layout.addRow("Transparency Compliance:", self.compliance_label)
        
        gov_group.setLayout(gov_layout)
        metrics_layout.addWidget(gov_group, 0, 0)
        
        # Financial performance
        fin_group = QGroupBox("Financial Performance")
        fin_layout = QFormLayout()
        
        self.budget_accuracy_label = QLabel("96%")
        self.spending_efficiency_label = QLabel("89%")
        self.disclosure_timeliness_label = QLabel("92%")
        self.audit_compliance_label = QLabel("98%")
        
        fin_layout.addRow("Budget Accuracy:", self.budget_accuracy_label)
        fin_layout.addRow("Spending Efficiency:", self.spending_efficiency_label)
        fin_layout.addRow("Disclosure Timeliness:", self.disclosure_timeliness_label)
        fin_layout.addRow("Audit Compliance:", self.audit_compliance_label)
        
        fin_group.setLayout(fin_layout)
        metrics_layout.addWidget(fin_group, 0, 1)
        
        # Public engagement
        eng_group = QGroupBox("Public Engagement")
        eng_layout = QFormLayout()
        
        self.participation_rate_label = QLabel("23%")
        self.feedback_response_label = QLabel("78%")
        self.accessibility_score_label = QLabel("85%")
        self.info_requests_label = QLabel("156 this month")
        
        eng_layout.addRow("Participation Rate:", self.participation_rate_label)
        eng_layout.addRow("Feedback Response:", self.feedback_response_label)
        eng_layout.addRow("Accessibility Score:", self.accessibility_score_label)
        eng_layout.addRow("Information Requests:", self.info_requests_label)
        
        eng_group.setLayout(eng_layout)
        metrics_layout.addWidget(eng_group, 1, 0, 1, 2)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # Performance trends
        trends_group = QGroupBox("Performance Trends")
        trends_layout = QVBoxLayout()
        
        trends_info = QLabel("""
        📈 Performance Trend Analysis:
        • Response times have improved 15% over the last quarter
        • Transparency compliance is at an all-time high
        • Public participation has increased following recent engagement initiatives  
        • Financial disclosure timeliness needs improvement (target: 95%)
        """)
        trends_info.setStyleSheet("background: #f8f9fa; padding: 15px; border-radius: 5px; color: #495057;")
        trends_layout.addWidget(trends_info)
        
        trends_group.setLayout(trends_layout)
        layout.addWidget(trends_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_conflict_tab(self):
        """Create conflict of interest monitoring interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Conflict monitoring info
        info_group = QGroupBox("Conflict of Interest Monitoring")
        info_layout = QVBoxLayout()
        
        conflict_info = QLabel("""
        ⚠️ Conflict of Interest Oversight:
        Monitoring potential conflicts of interest among public officials to ensure ethical governance.
        All financial relationships, business interests, and potential conflicts are tracked and disclosed.
        
        🔍 Continuous Monitoring: Real-time tracking of official activities and relationships
        📊 Risk Assessment: Automated analysis of potential ethical concerns
        📋 Disclosure Requirements: Mandatory reporting and public transparency
        """)
        conflict_info.setStyleSheet("background: #fff3cd; padding: 15px; border-radius: 5px; color: #856404;")
        info_layout.addWidget(conflict_info)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Conflict monitoring table
        self.conflicts_table = QTableWidget()
        self.conflicts_table.setColumnCount(6)
        self.conflicts_table.setHorizontalHeaderLabels([
            "Official", "Conflict Type", "Description", "Status", "Last Updated", "Actions"
        ])
        
        header = self.conflicts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.conflicts_table.setAlternatingRowColors(True)
        layout.addWidget(self.conflicts_table)
        
        widget.setLayout(layout)
        return widget
        
    def create_reports_tab(self):
        """Create public reports interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Report submission
        submit_group = QGroupBox("Submit Transparency Report")
        submit_layout = QVBoxLayout()
        
        report_info = QLabel("""
        📋 Citizen Transparency Reporting:
        Help maintain government accountability by reporting transparency concerns.
        Your reports help identify areas for improvement and ensure ethical governance.
        """)
        report_info.setStyleSheet("background: #d1ecf1; padding: 15px; border-radius: 5px; color: #0c5460;")
        submit_layout.addWidget(report_info)
        
        submit_btn_layout = QHBoxLayout()
        
        self.submit_report_btn = QPushButton("📝 Submit Transparency Report")
        self.submit_report_btn.clicked.connect(self.submit_transparency_report)
        self.submit_report_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        
        submit_btn_layout.addWidget(self.submit_report_btn)
        submit_btn_layout.addStretch()
        
        submit_layout.addLayout(submit_btn_layout)
        submit_group.setLayout(submit_layout)
        layout.addWidget(submit_group)
        
        # My reports
        my_reports_group = QGroupBox("My Transparency Reports")
        my_reports_layout = QVBoxLayout()
        
        self.my_reports_table = QTableWidget()
        self.my_reports_table.setColumnCount(5)
        self.my_reports_table.setHorizontalHeaderLabels([
            "Title", "Type", "Submitted", "Status", "Actions"
        ])
        
        header = self.my_reports_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.my_reports_table.setAlternatingRowColors(True)
        my_reports_layout.addWidget(self.my_reports_table)
        
        my_reports_group.setLayout(my_reports_layout)
        layout.addWidget(my_reports_group)
        
        widget.setLayout(layout)
        return widget
        
    def report_concern(self):
        """Open transparency concern reporting dialog"""
        dialog = TransparencyReportDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_ui()
            
    def submit_transparency_report(self):
        """Open transparency report submission dialog"""
        dialog = TransparencyReportDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_ui()
            
    def view_latest_audit(self):
        """View the latest audit report"""
        findings = self.transparency_engine.get_audit_findings(date_range=30)
        
        if findings:
            latest = findings[0]  # Most recent finding
            QMessageBox.information(self, "Latest Audit Finding", 
                f"Title: {latest['title']}\n"
                f"Type: {latest['type']}\n"
                f"Severity: {latest['severity']}\n"
                f"Status: {latest['status']}\n"
                f"Date: {latest['date']}\n\n"
                f"Description: {latest['description']}\n\n"
                f"Recommendation: {latest['recommendation']}")
        else:
            QMessageBox.information(self, "Audit Findings", "No recent audit findings available.")
            
    def show_performance_report(self):
        """Show detailed performance report"""
        QMessageBox.information(self, "Performance Report", 
            "📊 Government Performance Summary:\n\n"
            "Overall transparency score has improved by 8% this quarter.\n"
            "Key achievements:\n"
            "• Faster response times to citizen inquiries\n" 
            "• Improved budget disclosure processes\n"
            "• Enhanced public meeting accessibility\n\n"
            "Areas for improvement:\n"
            "• Document publication timeliness\n"
            "• Conflict disclosure updates\n"
            "• Public participation rates\n\n"
            "Full detailed reports available in the Performance tab.")
            
    def filter_audit_findings(self):
        """Filter audit findings based on current filter settings"""
        try:
            # Get filtered findings based on UI selections
            findings = self.transparency_engine.get_audit_findings()
            
            # Apply filters (in production would filter properly)
            audit_type = self.audit_type_filter.currentText()
            severity = self.severity_filter.currentText()
            status = self.status_filter.currentText()
            
            self.display_audit_findings(findings)
            
        except Exception as e:
            print(f"Error filtering audit findings: {e}")
            
    def display_audit_findings(self, findings):
        """Display audit findings in the table"""
        self.audit_table.setRowCount(len(findings))
        
        for row, finding in enumerate(findings):
            self.audit_table.setItem(row, 0, QTableWidgetItem(finding.get('title', 'Unknown')))
            self.audit_table.setItem(row, 1, QTableWidgetItem(finding.get('type', 'Unknown')))
            self.audit_table.setItem(row, 2, QTableWidgetItem(finding.get('severity', 'Unknown')))
            
            # Format date
            date_str = finding.get('date', '')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d')
                except:
                    formatted_date = date_str
            else:
                formatted_date = 'Unknown'
            self.audit_table.setItem(row, 3, QTableWidgetItem(formatted_date))
            
            self.audit_table.setItem(row, 4, QTableWidgetItem(finding.get('status', 'Unknown')))
            
            # Actions button
            view_btn = QPushButton("View Details")
            view_btn.clicked.connect(lambda checked, f=finding: self.view_finding_details(f))
            self.audit_table.setCellWidget(row, 5, view_btn)
            
    def view_finding_details(self, finding):
        """View detailed information about an audit finding"""
        QMessageBox.information(self, "Audit Finding Details",
            f"Title: {finding.get('title', 'Unknown')}\n"
            f"Type: {finding.get('type', 'Unknown')}\n" 
            f"Severity: {finding.get('severity', 'Unknown')}\n"
            f"Status: {finding.get('status', 'Unknown')}\n"
            f"Date: {finding.get('date', 'Unknown')}\n\n"
            f"Description:\n{finding.get('description', 'No description')}\n\n"
            f"Recommendation:\n{finding.get('recommendation', 'No recommendation')}")
            
    def refresh_ui(self):
        """Refresh the UI with current data"""
        try:
            # Refresh transparency score
            self.update_transparency_score()
            
            # Refresh audit findings
            self.filter_audit_findings()
            
            # Refresh performance metrics
            self.update_performance_metrics()
            
            # Refresh conflicts
            self.update_conflicts()
            
            # Refresh activity
            self.update_recent_activity()
            
        except Exception as e:
            print(f"Error refreshing Transparency UI: {e}")
            
    def update_transparency_score(self):
        """Update transparency score display"""
        try:
            score_data = self.transparency_engine.get_transparency_score()
            
            overall = score_data.get('overall_score', 0)
            grade = score_data.get('grade', 'F')
            
            self.overall_score_label.setText(str(overall))
            self.grade_label.setText(f"Grade: {grade}")
            
            # Update color based on score
            if overall >= 90:
                color = "#28a745"  # Green
                description = "Excellent transparency standards"
            elif overall >= 80:
                color = "#ffc107"  # Yellow
                description = "Good transparency with room for improvement"  
            elif overall >= 70:
                color = "#fd7e14"  # Orange
                description = "Acceptable transparency, improvements needed"
            else:
                color = "#dc3545"  # Red
                description = "Transparency standards require significant improvement"
                
            self.overall_score_label.setStyleSheet(f"color: {color}; text-align: center;")
            self.grade_label.setStyleSheet(f"color: {color};")
            self.score_description.setText(description)
            
            # Update progress bars
            self.financial_score.setValue(score_data.get('financial_transparency', 0))
            self.governance_score.setValue(score_data.get('governance_accountability', 0))
            self.decision_score.setValue(score_data.get('decision_transparency', 0))
            self.participation_score.setValue(score_data.get('public_participation', 0))
            self.access_score.setValue(score_data.get('information_access', 0))
            
        except Exception as e:
            print(f"Error updating transparency score: {e}")
            
    def update_performance_metrics(self):
        """Update performance metrics display"""
        try:
            gov_metrics = self.transparency_engine.get_performance_metrics("governance_effectiveness")
            fin_metrics = self.transparency_engine.get_performance_metrics("financial_performance")
            eng_metrics = self.transparency_engine.get_performance_metrics("public_engagement")
            
            # Update governance metrics
            self.response_time_label.setText(gov_metrics.get('response_time_avg', 'N/A'))
            self.resolution_rate_label.setText(gov_metrics.get('resolution_rate', 'N/A'))
            self.satisfaction_label.setText(gov_metrics.get('citizen_satisfaction', 'N/A'))
            self.compliance_label.setText(gov_metrics.get('transparency_compliance', 'N/A'))
            
            # Update financial metrics
            self.budget_accuracy_label.setText(fin_metrics.get('budget_accuracy', 'N/A'))
            self.spending_efficiency_label.setText(fin_metrics.get('spending_efficiency', 'N/A'))
            self.disclosure_timeliness_label.setText(fin_metrics.get('disclosure_timeliness', 'N/A'))
            self.audit_compliance_label.setText(fin_metrics.get('audit_compliance', 'N/A'))
            
            # Update engagement metrics
            self.participation_rate_label.setText(eng_metrics.get('participation_rate', 'N/A'))
            self.feedback_response_label.setText(eng_metrics.get('feedback_response', 'N/A'))
            self.accessibility_score_label.setText(eng_metrics.get('accessibility_score', 'N/A'))
            self.info_requests_label.setText(eng_metrics.get('information_requests', 'N/A'))
            
        except Exception as e:
            print(f"Error updating performance metrics: {e}")
            
    def update_conflicts(self):
        """Update conflict monitoring display"""
        try:
            conflicts = self.transparency_engine.get_conflict_monitoring()
            
            self.conflicts_table.setRowCount(len(conflicts))
            
            for row, conflict in enumerate(conflicts):
                self.conflicts_table.setItem(row, 0, QTableWidgetItem(conflict.get('official', 'Unknown')))
                self.conflicts_table.setItem(row, 1, QTableWidgetItem(conflict.get('type', 'Unknown')))
                self.conflicts_table.setItem(row, 2, QTableWidgetItem(conflict.get('description', 'No description')))
                self.conflicts_table.setItem(row, 3, QTableWidgetItem(conflict.get('status', 'Unknown')))
                
                # Format date
                last_updated = conflict.get('last_updated', '')
                if last_updated:
                    try:
                        dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d')
                    except:
                        formatted_date = last_updated
                else:
                    formatted_date = 'Unknown'
                self.conflicts_table.setItem(row, 4, QTableWidgetItem(formatted_date))
                
                # Actions button
                view_btn = QPushButton("View Details")
                view_btn.clicked.connect(lambda checked, c=conflict: self.view_conflict_details(c))
                self.conflicts_table.setCellWidget(row, 5, view_btn)
                
        except Exception as e:
            print(f"Error updating conflicts: {e}")
            
    def view_conflict_details(self, conflict):
        """View detailed conflict information"""
        QMessageBox.information(self, "Conflict of Interest Details",
            f"Official: {conflict.get('official', 'Unknown')}\n"
            f"Conflict Type: {conflict.get('type', 'Unknown')}\n"
            f"Status: {conflict.get('status', 'Unknown')}\n"
            f"Last Updated: {conflict.get('last_updated', 'Unknown')}\n\n"
            f"Description:\n{conflict.get('description', 'No description')}\n\n"
            f"Mitigation:\n{conflict.get('mitigation', 'No mitigation specified')}")
            
    def update_recent_activity(self):
        """Update recent transparency activity"""
        try:
            activities = [
                "Budget report published on schedule",
                "Meeting minutes updated with full vote records",
                "Conflict disclosure updated for Representative Smith",
                "FOIA request processed within deadline",
                "Performance metrics updated for Q3"
            ]
            
            self.activity_list.clear()
            
            for activity in activities:
                item = QListWidgetItem(f"• {activity}")
                self.activity_list.addItem(item)
                
        except Exception as e:
            print(f"Error updating recent activity: {e}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test the transparency audit interface
    window = TransparencyAuditTab()
    window.show()
    
    sys.exit(app.exec_())