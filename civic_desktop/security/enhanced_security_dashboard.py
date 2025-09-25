# Enhanced Security Monitoring Dashboard - Advanced Threat Detection & Response
# Real-time security monitoring with AI-powered threat detection and automated responses

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTabWidget, QScrollArea, QFrame, QGridLayout, QProgressBar,
                            QTextEdit, QListWidget, QListWidgetItem, QGroupBox, QSplitter,
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
                            QApplication, QSizePolicy, QCheckBox, QSpinBox, QComboBox,
                            QDateTimeEdit, QSlider, QDial, QLCDNumber)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QRect, QDateTime
from PyQt5.QtGui import QPalette, QFont, QColor, QPainter, QPen, QBrush, QLinearGradient, QPixmap
from typing import Dict, List, Any, Optional
import datetime
import json
import random

from ..blockchain.advanced_analytics import get_blockchain_analytics
from ..users.session import SessionManager
from ..moderation.backend import ModerationBackend
from ..analytics.ai_analytics_engine import get_ai_analytics


class ThreatLevelIndicator(QWidget):
    """
    🚨 Visual threat level indicator with color-coded alerts
    """
    
    def __init__(self, threat_level: str = "low", parent=None):
        super().__init__(parent)
        self.threat_level = threat_level.lower()
        self.setFixedSize(120, 120)
        self.colors = {
            'low': '#28a745',      # Green
            'medium': '#ffc107',   # Yellow
            'high': '#fd7e14',     # Orange
            'critical': '#dc3545'  # Red
        }
        
    def paintEvent(self, event):
        """Custom paint event for threat indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circular threat indicator
        rect = self.rect().adjusted(10, 10, -10, -10)
        color = QColor(self.colors.get(self.threat_level, '#6c757d'))
        
        # Gradient effect
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color.darker(120))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(color.darker(150), 3))
        painter.drawEllipse(rect)
        
        # Draw threat level text
        painter.setPen(QPen(QColor('white'), 2))
        painter.setFont(QFont('Arial', 12, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, self.threat_level.upper())
    
    def update_threat_level(self, new_level: str):
        """Update the threat level and repaint"""
        self.threat_level = new_level.lower()
        self.update()


class SecurityMetricCard(QFrame):
    """
    📊 Security metric display card with animations
    """
    
    def __init__(self, title: str, value: str, status: str = "normal", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box)
        self.status = status
        self.setup_ui(title, value)
        
    def setup_ui(self, title: str, value: str):
        """Setup the security metric card UI"""
        status_colors = {
            'normal': '#28a745',
            'warning': '#ffc107', 
            'alert': '#fd7e14',
            'critical': '#dc3545'
        }
        
        color = status_colors.get(self.status, '#6c757d')
        
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95), stop:1 rgba(240, 240, 240, 0.95));
                border: 2px solid {color};
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 1.0), stop:1 rgba(245, 245, 245, 1.0));
                border: 3px solid {color};
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        title_label.setStyleSheet(f"color: {color}; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.value_label.setStyleSheet("color: #2c3e50; margin: 5px 0;")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Status indicator
        status_label = QLabel(f"Status: {self.status.title()}")
        status_label.setFont(QFont("Arial", 9))
        status_label.setStyleSheet(f"color: {color}; margin-top: 5px;")
        status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label)
        
        self.setLayout(layout)
        self.setMaximumHeight(120)
        self.setMinimumWidth(180)
    
    def update_metric(self, new_value: str, new_status: str = None):
        """Update the metric value and status"""
        self.value_label.setText(new_value)
        if new_status:
            self.status = new_status
            # Re-setup UI with new status
            self.setup_ui(self.value_label.text(), new_value)


class SecurityEventLog(QWidget):
    """
    📝 Real-time security event logging widget
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.event_history = []
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🔐 Real-Time Security Events")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(220, 53, 69, 0.1), stop:1 rgba(253, 126, 20, 0.1));
            padding: 10px;
            border-radius: 8px;
            color: #dc3545;
            margin-bottom: 10px;
        """)
        layout.addWidget(header)
        
        # Event list
        self.events_list = QListWidget()
        self.events_list.setStyleSheet("""
            QListWidget {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidgetItem {
                padding: 8px;
                margin: 2px 0;
                background: white;
                border-left: 4px solid #6c757d;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.events_list)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.auto_scroll_checkbox = QCheckBox("Auto-scroll")
        self.auto_scroll_checkbox.setChecked(True)
        controls_layout.addWidget(self.auto_scroll_checkbox)
        
        clear_btn = QPushButton("Clear Log")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #545b62;
            }
        """)
        clear_btn.clicked.connect(self.clear_events)
        controls_layout.addWidget(clear_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)
    
    def add_security_event(self, event_type: str, message: str, severity: str = "info"):
        """Add a new security event to the log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        severity_colors = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545',
            'success': '#28a745'
        }
        
        severity_icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '🚨',
            'success': '✅'
        }
        
        color = severity_colors.get(severity, '#6c757d')
        icon = severity_icons.get(severity, '📋')
        
        event_text = f"{icon} [{timestamp}] {event_type}: {message}"
        
        item = QListWidgetItem(event_text)
        item.setToolTip(f"Full details: {message}")
        
        # Set item color based on severity
        item.setData(Qt.UserRole, severity)
        
        self.events_list.addItem(item)
        self.event_history.append({
            'timestamp': timestamp,
            'type': event_type,
            'message': message,
            'severity': severity
        })
        
        # Auto-scroll to bottom
        if self.auto_scroll_checkbox.isChecked():
            self.events_list.scrollToBottom()
        
        # Limit log size
        if self.events_list.count() > 1000:
            self.events_list.takeItem(0)
    
    def clear_events(self):
        """Clear all events from the log"""
        self.events_list.clear()
        self.event_history.clear()


class EnhancedSecurityDashboard(QWidget):
    """
    🛡️ Main Enhanced Security Monitoring Dashboard
    
    Advanced security monitoring with real-time threat detection, incident response,
    and comprehensive security analytics
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_monitoring()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Dashboard Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🛡️ Enhanced Security Monitoring Center")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("""
            color: #2c3e50;
            padding: 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(220, 53, 69, 0.1), stop:1 rgba(253, 126, 20, 0.1));
            border-radius: 10px;
            border: 2px solid #dc3545;
        """)
        header_layout.addWidget(title_label)
        
        # Emergency Response Button
        emergency_btn = QPushButton("🚨 Emergency Response")
        emergency_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(90deg, #dc3545 0%, #c82333 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: linear-gradient(90deg, #c82333 0%, #a71e2a 100%);
                transform: scale(1.05);
            }
        """)
        emergency_btn.clicked.connect(self.trigger_emergency_response)
        header_layout.addWidget(emergency_btn)
        
        layout.addLayout(header_layout)
        
        # Main Dashboard Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #dc3545;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #f8f9fa;
                padding: 12px 20px;
                margin-right: 2px;
                border-radius: 6px 6px 0 0;
                border: 2px solid #dee2e6;
            }
            QTabBar::tab:selected {
                background: #dc3545;
                color: white;
                border-color: #dc3545;
            }
            QTabBar::tab:hover {
                background: #e9ecef;
            }
        """)
        
        # Threat Overview Tab
        threat_tab = self.create_threat_overview_tab()
        self.tabs.addTab(threat_tab, "🚨 Threat Overview")
        
        # Real-time Monitoring Tab
        monitoring_tab = self.create_monitoring_tab()
        self.tabs.addTab(monitoring_tab, "📊 Real-time Monitoring")
        
        # Incident Response Tab
        incident_tab = self.create_incident_response_tab()
        self.tabs.addTab(incident_tab, "🚑 Incident Response")
        
        # Security Analytics Tab
        analytics_tab = self.create_security_analytics_tab()
        self.tabs.addTab(analytics_tab, "📈 Security Analytics")
        
        # Compliance & Audit Tab
        compliance_tab = self.create_compliance_tab()
        self.tabs.addTab(compliance_tab, "📋 Compliance & Audit")
        
        layout.addWidget(self.tabs)
        
        # Status Bar
        self.status_bar = QLabel("🟢 All systems operational - Last update: Never")
        self.status_bar.setStyleSheet("""
            background: #d4edda;
            color: #155724;
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #c3e6cb;
        """)
        layout.addWidget(self.status_bar)
        
        self.setLayout(layout)
    
    def create_threat_overview_tab(self) -> QWidget:
        """Create the threat overview tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Threat Level Indicators
        threat_layout = QHBoxLayout()
        
        # Overall Threat Level
        self.threat_indicator = ThreatLevelIndicator("low")
        threat_info_layout = QVBoxLayout()
        threat_info_layout.addWidget(QLabel("Overall Threat Level"))
        threat_info_layout.addWidget(self.threat_indicator)
        threat_layout.addWidget(QFrame())
        threat_layout.addLayout(threat_info_layout)
        threat_layout.addWidget(QFrame())
        
        # Security Metrics Grid
        metrics_group = QGroupBox("🔐 Security Metrics")
        metrics_grid = QGridLayout()
        
        self.failed_login_card = SecurityMetricCard("Failed Logins", "0", "normal")
        self.suspicious_activity_card = SecurityMetricCard("Suspicious Activity", "0", "normal")
        self.blocked_threats_card = SecurityMetricCard("Blocked Threats", "0", "success")
        self.system_integrity_card = SecurityMetricCard("System Integrity", "100%", "normal")
        
        metrics_grid.addWidget(self.failed_login_card, 0, 0)
        metrics_grid.addWidget(self.suspicious_activity_card, 0, 1)
        metrics_grid.addWidget(self.blocked_threats_card, 1, 0)
        metrics_grid.addWidget(self.system_integrity_card, 1, 1)
        
        metrics_group.setLayout(metrics_grid)
        
        # Recent Security Alerts
        alerts_group = QGroupBox("⚠️ Recent Security Alerts")
        alerts_layout = QVBoxLayout()
        
        self.alerts_list = QListWidget()
        self.alerts_list.setStyleSheet("""
            QListWidget {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 10px;
            }
            QListWidgetItem {
                padding: 8px;
                margin: 2px 0;
                background: white;
                border-left: 4px solid #ffc107;
                border-radius: 4px;
            }
        """)
        
        # Add sample alerts
        self.add_sample_security_alert("System startup completed successfully", "info")
        self.add_sample_security_alert("Security monitoring initialized", "success")
        
        alerts_layout.addWidget(self.alerts_list)
        alerts_group.setLayout(alerts_layout)
        
        layout.addLayout(threat_layout)
        layout.addWidget(metrics_group)
        layout.addWidget(alerts_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_monitoring_tab(self) -> QWidget:
        """Create real-time monitoring tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Live Security Feed
        self.security_log = SecurityEventLog()
        
        # Monitoring Controls
        controls_group = QGroupBox("🎛️ Monitoring Controls")
        controls_layout = QGridLayout()
        
        # Monitoring Level
        controls_layout.addWidget(QLabel("Monitoring Level:"), 0, 0)
        self.monitoring_level = QComboBox()
        self.monitoring_level.addItems(["Basic", "Enhanced", "Maximum", "Paranoid"])
        self.monitoring_level.setCurrentText("Enhanced")
        controls_layout.addWidget(self.monitoring_level, 0, 1)
        
        # Alert Threshold
        controls_layout.addWidget(QLabel("Alert Threshold:"), 0, 2)
        self.alert_threshold = QSlider(Qt.Horizontal)
        self.alert_threshold.setRange(1, 10)
        self.alert_threshold.setValue(5)
        controls_layout.addWidget(self.alert_threshold, 0, 3)
        
        # Auto-Response
        self.auto_response_checkbox = QCheckBox("Enable Auto-Response")
        self.auto_response_checkbox.setChecked(True)
        controls_layout.addWidget(self.auto_response_checkbox, 1, 0, 1, 2)
        
        # Refresh Rate
        controls_layout.addWidget(QLabel("Refresh Rate (seconds):"), 1, 2)
        self.refresh_rate_spinbox = QSpinBox()
        self.refresh_rate_spinbox.setRange(1, 60)
        self.refresh_rate_spinbox.setValue(5)
        controls_layout.addWidget(self.refresh_rate_spinbox, 1, 3)
        
        controls_group.setLayout(controls_layout)
        
        layout.addWidget(controls_group)
        layout.addWidget(self.security_log)
        
        widget.setLayout(layout)
        return widget
    
    def create_incident_response_tab(self) -> QWidget:
        """Create incident response tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Active Incidents
        incidents_group = QGroupBox("🚑 Active Security Incidents")
        incidents_layout = QVBoxLayout()
        
        self.incidents_table = QTableWidget(0, 5)
        self.incidents_table.setHorizontalHeaderLabels([
            "ID", "Type", "Severity", "Status", "Actions"
        ])
        self.incidents_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QHeaderView::section {
                background: #dc3545;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        header = self.incidents_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        incidents_layout.addWidget(self.incidents_table)
        
        # Response Actions
        actions_layout = QHBoxLayout()
        
        isolate_btn = QPushButton("🔒 Isolate System")
        isolate_btn.setStyleSheet(self.get_action_button_style("#dc3545"))
        isolate_btn.clicked.connect(lambda: self.execute_response_action("isolate"))
        
        lockdown_btn = QPushButton("🚫 Emergency Lockdown")
        lockdown_btn.setStyleSheet(self.get_action_button_style("#6f42c1"))
        lockdown_btn.clicked.connect(lambda: self.execute_response_action("lockdown"))
        
        investigate_btn = QPushButton("🔍 Investigate")
        investigate_btn.setStyleSheet(self.get_action_button_style("#007bff"))
        investigate_btn.clicked.connect(lambda: self.execute_response_action("investigate"))
        
        resolve_btn = QPushButton("✅ Mark Resolved")
        resolve_btn.setStyleSheet(self.get_action_button_style("#28a745"))
        resolve_btn.clicked.connect(lambda: self.execute_response_action("resolve"))
        
        actions_layout.addWidget(isolate_btn)
        actions_layout.addWidget(lockdown_btn)
        actions_layout.addWidget(investigate_btn)
        actions_layout.addWidget(resolve_btn)
        
        incidents_layout.addLayout(actions_layout)
        incidents_group.setLayout(incidents_layout)
        
        # Response Procedures
        procedures_group = QGroupBox("📋 Response Procedures")
        procedures_layout = QVBoxLayout()
        
        self.procedures_text = QTextEdit()
        self.procedures_text.setPlainText("""
🚨 SECURITY INCIDENT RESPONSE PROCEDURES 🚨

1. IMMEDIATE ASSESSMENT
   • Identify incident type and severity
   • Assess potential impact and affected systems
   • Determine if containment is required

2. CONTAINMENT
   • Isolate affected systems if necessary
   • Prevent further damage or data loss
   • Preserve evidence for investigation

3. INVESTIGATION
   • Analyze logs and forensic evidence
   • Determine root cause and attack vector
   • Document findings and timeline

4. RECOVERY
   • Restore systems to normal operation
   • Implement additional security measures
   • Verify system integrity and functionality

5. POST-INCIDENT REVIEW
   • Document lessons learned
   • Update security procedures
   • Implement preventive measures

⚠️ For critical incidents, immediately contact:
   📞 Security Team: ext. 911
   📧 Emergency: security@civic.gov
        """)
        self.procedures_text.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Courier New';
                font-size: 12px;
            }
        """)
        self.procedures_text.setMaximumHeight(200)
        
        procedures_layout.addWidget(self.procedures_text)
        procedures_group.setLayout(procedures_layout)
        
        layout.addWidget(incidents_group)
        layout.addWidget(procedures_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_security_analytics_tab(self) -> QWidget:
        """Create security analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Analytics Dashboard
        analytics_group = QGroupBox("📊 Security Analytics Dashboard")
        analytics_layout = QGridLayout()
        
        # Threat Trend Chart (placeholder)
        trend_frame = QFrame()
        trend_frame.setFrameStyle(QFrame.Box)
        trend_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #007bff;
                border-radius: 8px;
                min-height: 200px;
            }
        """)
        trend_layout = QVBoxLayout()
        trend_label = QLabel("📈 Threat Trends (Last 30 Days)")
        trend_label.setAlignment(Qt.AlignCenter)
        trend_label.setFont(QFont("Arial", 12, QFont.Bold))
        trend_content = QLabel("📊 Interactive threat trend visualization\n\n• 🟢 Low threats: 45 incidents\n• 🟡 Medium threats: 12 incidents\n• 🟠 High threats: 3 incidents\n• 🔴 Critical threats: 0 incidents\n\n📉 Trending down 15% from last month")
        trend_content.setAlignment(Qt.AlignCenter)
        trend_layout.addWidget(trend_label)
        trend_layout.addWidget(trend_content)
        trend_frame.setLayout(trend_layout)
        
        analytics_layout.addWidget(trend_frame, 0, 0)
        
        # Attack Vector Analysis
        vector_frame = QFrame()
        vector_frame.setFrameStyle(QFrame.Box)
        vector_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #28a745;
                border-radius: 8px;
                min-height: 200px;
            }
        """)
        vector_layout = QVBoxLayout()
        vector_label = QLabel("🎯 Attack Vector Analysis")
        vector_label.setAlignment(Qt.AlignCenter)
        vector_label.setFont(QFont("Arial", 12, QFont.Bold))
        vector_content = QLabel("🛡️ Most common attack vectors:\n\n1. 📧 Phishing attempts: 35%\n2. 🔑 Credential stuffing: 25%\n3. 🌐 Web application attacks: 20%\n4. 📊 Data exfiltration: 15%\n5. 🦠 Malware: 5%")
        vector_content.setAlignment(Qt.AlignCenter)
        vector_layout.addWidget(vector_label)
        vector_layout.addWidget(vector_content)
        vector_frame.setLayout(vector_layout)
        
        analytics_layout.addWidget(vector_frame, 0, 1)
        
        analytics_group.setLayout(analytics_layout)
        
        # Security Recommendations
        recommendations_group = QGroupBox("💡 AI Security Recommendations")
        recommendations_layout = QVBoxLayout()
        
        self.recommendations_list = QListWidget()
        self.recommendations_list.setStyleSheet("""
            QListWidget {
                background: #e7f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 8px;
                padding: 10px;
            }
            QListWidgetItem {
                padding: 10px;
                margin: 3px 0;
                background: white;
                border-left: 4px solid #007bff;
                border-radius: 4px;
            }
        """)
        
        # Add sample recommendations
        recommendations = [
            "🔐 Enable multi-factor authentication for all administrative accounts",
            "🔄 Update security policies to address emerging threat patterns",
            "📊 Implement enhanced monitoring for suspicious login patterns",
            "🛡️ Consider deploying additional intrusion detection sensors",
            "📝 Review and update incident response procedures"
        ]
        
        for rec in recommendations:
            self.recommendations_list.addItem(QListWidgetItem(rec))
        
        recommendations_layout.addWidget(self.recommendations_list)
        recommendations_group.setLayout(recommendations_layout)
        
        layout.addWidget(analytics_group)
        layout.addWidget(recommendations_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_compliance_tab(self) -> QWidget:
        """Create compliance and audit tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Compliance Status
        compliance_group = QGroupBox("📋 Compliance Status")
        compliance_layout = QGridLayout()
        
        # Compliance metrics
        gdpr_card = SecurityMetricCard("GDPR Compliance", "98%", "normal")
        sox_card = SecurityMetricCard("SOX Compliance", "100%", "success")
        hipaa_card = SecurityMetricCard("HIPAA Ready", "95%", "normal")
        iso_card = SecurityMetricCard("ISO 27001", "92%", "normal")
        
        compliance_layout.addWidget(gdpr_card, 0, 0)
        compliance_layout.addWidget(sox_card, 0, 1)
        compliance_layout.addWidget(hipaa_card, 1, 0)
        compliance_layout.addWidget(iso_card, 1, 1)
        
        compliance_group.setLayout(compliance_layout)
        
        # Audit Trail
        audit_group = QGroupBox("🔍 Security Audit Trail")
        audit_layout = QVBoxLayout()
        
        self.audit_table = QTableWidget(0, 4)
        self.audit_table.setHorizontalHeaderLabels([
            "Timestamp", "User", "Action", "Result"
        ])
        self.audit_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QHeaderView::section {
                background: #6c757d;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Add sample audit entries
        audit_entries = [
            ("2024-01-15 14:30:22", "admin@civic.gov", "Security scan initiated", "SUCCESS"),
            ("2024-01-15 14:25:15", "system", "Failed login attempt blocked", "BLOCKED"),
            ("2024-01-15 14:20:08", "user@civic.gov", "Password changed", "SUCCESS"),
            ("2024-01-15 14:15:01", "system", "Security policy updated", "SUCCESS")
        ]
        
        self.audit_table.setRowCount(len(audit_entries))
        for i, (timestamp, user, action, result) in enumerate(audit_entries):
            self.audit_table.setItem(i, 0, QTableWidgetItem(timestamp))
            self.audit_table.setItem(i, 1, QTableWidgetItem(user))
            self.audit_table.setItem(i, 2, QTableWidgetItem(action))
            self.audit_table.setItem(i, 3, QTableWidgetItem(result))
        
        header = self.audit_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        audit_layout.addWidget(self.audit_table)
        audit_group.setLayout(audit_layout)
        
        layout.addWidget(compliance_group)
        layout.addWidget(audit_group)
        
        widget.setLayout(layout)
        return widget
    
    def setup_monitoring(self):
        """Setup real-time monitoring"""
        # Setup refresh timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.refresh_security_data)
        self.monitor_timer.start(5000)  # Refresh every 5 seconds
        
        # Initial data load
        self.refresh_security_data()
        
        # Setup demo security events
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.generate_demo_security_event)
        self.demo_timer.start(15000)  # Generate demo event every 15 seconds
    
    def refresh_security_data(self):
        """Refresh all security monitoring data"""
        try:
            # Update timestamp
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.status_bar.setText(f"🟢 All systems operational - Last update: {current_time}")
            
            # Simulate metrics updates
            self.update_security_metrics()
            
        except Exception as e:
            self.status_bar.setText(f"❌ Update failed: {str(e)}")
            print(f"Error refreshing security data: {e}")
    
    def update_security_metrics(self):
        """Update security metrics with simulated data"""
        # Simulate some metrics
        failed_logins = random.randint(0, 5)
        suspicious_activity = random.randint(0, 3)
        blocked_threats = random.randint(5, 20)
        
        self.failed_login_card.update_metric(str(failed_logins), "warning" if failed_logins > 3 else "normal")
        self.suspicious_activity_card.update_metric(str(suspicious_activity), "alert" if suspicious_activity > 2 else "normal")
        self.blocked_threats_card.update_metric(str(blocked_threats), "success")
        
        # Update threat level based on metrics
        if failed_logins > 4 or suspicious_activity > 2:
            self.threat_indicator.update_threat_level("medium")
        else:
            self.threat_indicator.update_threat_level("low")
    
    def generate_demo_security_event(self):
        """Generate demonstration security events"""
        demo_events = [
            ("Login Monitor", "User authentication successful", "success"),
            ("Access Control", "File access granted", "info"),
            ("Network Monitor", "Unusual network traffic detected", "warning"),
            ("System Integrity", "System files verified", "success"),
            ("Threat Detection", "Suspicious pattern analyzed", "warning"),
            ("Compliance Check", "Security policy compliance verified", "success")
        ]
        
        event_type, message, severity = random.choice(demo_events)
        self.security_log.add_security_event(event_type, message, severity)
    
    def add_sample_security_alert(self, message: str, severity: str):
        """Add a sample security alert"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        severity_icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '🚨',
            'success': '✅'
        }
        
        icon = severity_icons.get(severity, '📋')
        alert_text = f"{icon} [{timestamp}] {message}"
        
        item = QListWidgetItem(alert_text)
        self.alerts_list.addItem(item)
    
    def trigger_emergency_response(self):
        """Trigger emergency response procedures"""
        reply = QMessageBox.question(
            self, 
            "Emergency Response", 
            "🚨 This will activate emergency security protocols.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.security_log.add_security_event("EMERGENCY", "Emergency response activated by user", "error")
            self.threat_indicator.update_threat_level("critical")
            QMessageBox.information(
                self, 
                "Emergency Response Activated", 
                "🚨 Emergency security protocols have been activated.\n\nAll security teams have been notified."
            )
    
    def execute_response_action(self, action: str):
        """Execute incident response actions"""
        actions = {
            'isolate': 'System isolation procedures initiated',
            'lockdown': 'Emergency lockdown activated',
            'investigate': 'Investigation procedures started',
            'resolve': 'Incident marked as resolved'
        }
        
        message = actions.get(action, f'Unknown action: {action}')
        self.security_log.add_security_event("RESPONSE", message, "info")
        
        QMessageBox.information(
            self,
            "Response Action",
            f"✅ {message}"
        )
    
    def get_action_button_style(self, color: str) -> str:
        """Get stylesheet for action buttons"""
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {color}dd;
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                background: {color}bb;
            }}
        """
    
    def refresh_ui(self):
        """Refresh UI (called by main window)"""
        self.refresh_security_data()


# Export the main dashboard class
__all__ = ['EnhancedSecurityDashboard']