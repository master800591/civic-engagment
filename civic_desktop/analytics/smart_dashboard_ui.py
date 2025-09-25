# Smart AI-Powered Dashboard - Advanced Analytics & Intelligence Interface
# This creates an intelligent dashboard that leverages AI analytics for enhanced civic engagement

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTabWidget, QScrollArea, QFrame, QGridLayout, QProgressBar,
                            QTextEdit, QListWidget, QListWidgetItem, QGroupBox, QSplitter,
                            QComboBox, QSpinBox, QDateEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QApplication, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QPalette, QFont, QColor, QPainter, QPen, QBrush, QLinearGradient
from typing import Dict, List, Any, Optional
import datetime
import json

from .ai_analytics_engine import get_ai_analytics
from ..users.session import SessionManager
from ..blockchain.blockchain import Blockchain


class AnimatedMetricCard(QFrame):
    """
    🎨 Animated metric display card with smooth transitions and visual appeal
    """
    
    def __init__(self, title: str, value: str, subtitle: str = "", color: str = "#007bff", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background: linear-gradient(135deg, {color}15 0%, {color}25 100%);
                border: 2px solid {color}40;
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }}
            QFrame:hover {{
                background: linear-gradient(135deg, {color}25 0%, {color}35 100%);
                transform: scale(1.02);
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet(f"color: {color}; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.value_label.setStyleSheet("color: #2c3e50; margin: 5px 0;")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Arial", 10))
            subtitle_label.setStyleSheet("color: #6c757d; margin-top: 5px;")
            subtitle_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(subtitle_label)
        
        self.setLayout(layout)
        self.setMaximumHeight(120)
        self.setMinimumWidth(200)
    
    def update_value(self, new_value: str):
        """Update the metric value with animation"""
        self.value_label.setText(new_value)
        # Add smooth update animation here if needed


class AIInsightWidget(QWidget):
    """
    🤖 AI-powered insight display widget with intelligent recommendations
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.ai_engine = get_ai_analytics()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🧠 AI Civic Intelligence")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("""
            color: #2c3e50;
            padding: 10px;
            background: linear-gradient(90deg, #3498db20 0%, #9b59b620 100%);
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        layout.addWidget(header)
        
        # AI Insights Tabs
        self.insights_tabs = QTabWidget()
        self.insights_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
        """)
        
        # Personal Intelligence Tab
        personal_tab = self.create_personal_intelligence_tab()
        self.insights_tabs.addTab(personal_tab, "🎯 Personal Insights")
        
        # Community Intelligence Tab
        community_tab = self.create_community_intelligence_tab()
        self.insights_tabs.addTab(community_tab, "🏛️ Community Analytics")
        
        # Predictive Intelligence Tab
        predictive_tab = self.create_predictive_intelligence_tab()
        self.insights_tabs.addTab(predictive_tab, "🔮 Predictive Intelligence")
        
        # Security Intelligence Tab
        security_tab = self.create_security_intelligence_tab()
        self.insights_tabs.addTab(security_tab, "🛡️ Security Intelligence")
        
        layout.addWidget(self.insights_tabs)
        self.setLayout(layout)
    
    def create_personal_intelligence_tab(self) -> QWidget:
        """Create personalized AI insights tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Engagement Score Card
        self.engagement_card = AnimatedMetricCard(
            "Civic Engagement Score", 
            "Loading...", 
            "Your participation level",
            "#28a745"
        )
        
        # AI Recommendations
        recommendations_group = QGroupBox("🎯 AI-Powered Recommendations")
        recommendations_layout = QVBoxLayout()
        
        self.recommendations_list = QListWidget()
        self.recommendations_list.setStyleSheet("""
            QListWidget {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
            QListWidgetItem {
                padding: 8px;
                margin: 2px 0;
                background: white;
                border-left: 4px solid #007bff;
                border-radius: 4px;
            }
        """)
        recommendations_layout.addWidget(self.recommendations_list)
        recommendations_group.setLayout(recommendations_layout)
        
        # Civic Growth Path
        growth_group = QGroupBox("🌱 Your Civic Growth Path")
        growth_layout = QVBoxLayout()
        
        self.growth_progress = QProgressBar()
        self.growth_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background: #ecf0f1;
                height: 25px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: linear-gradient(90deg, #3498db 0%, #2ecc71 100%);
                border-radius: 6px;
            }
        """)
        self.growth_label = QLabel("Calculating your civic development...")
        self.growth_label.setStyleSheet("color: #6c757d; margin: 5px 0;")
        
        growth_layout.addWidget(self.growth_progress)
        growth_layout.addWidget(self.growth_label)
        growth_group.setLayout(growth_layout)
        
        # Layout assembly
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.engagement_card)
        
        layout.addLayout(top_layout)
        layout.addWidget(recommendations_group)
        layout.addWidget(growth_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_community_intelligence_tab(self) -> QWidget:
        """Create community analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Community Health Metrics
        metrics_layout = QGridLayout()
        
        self.democracy_score_card = AnimatedMetricCard(
            "Democracy Health", 
            "Loading...", 
            "Platform democratic quality",
            "#e74c3c"
        )
        
        self.participation_card = AnimatedMetricCard(
            "Participation Rate", 
            "Loading...", 
            "Active community members",
            "#f39c12"
        )
        
        self.consensus_card = AnimatedMetricCard(
            "Consensus Building", 
            "Loading...", 
            "Agreement achievement rate",
            "#9b59b6"
        )
        
        metrics_layout.addWidget(self.democracy_score_card, 0, 0)
        metrics_layout.addWidget(self.participation_card, 0, 1)
        metrics_layout.addWidget(self.consensus_card, 0, 2)
        
        # Community Insights
        insights_group = QGroupBox("🏛️ Community Intelligence Analysis")
        insights_layout = QVBoxLayout()
        
        self.community_insights = QTextEdit()
        self.community_insights.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        self.community_insights.setMaximumHeight(200)
        insights_layout.addWidget(self.community_insights)
        insights_group.setLayout(insights_layout)
        
        layout.addLayout(metrics_layout)
        layout.addWidget(insights_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_predictive_intelligence_tab(self) -> QWidget:
        """Create predictive analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Prediction Cards
        predictions_layout = QGridLayout()
        
        self.engagement_trend_card = AnimatedMetricCard(
            "Engagement Trend", 
            "Loading...", 
            "Predicted community direction",
            "#17a2b8"
        )
        
        self.governance_forecast_card = AnimatedMetricCard(
            "Governance Health", 
            "Loading...", 
            "System effectiveness forecast",
            "#28a745"
        )
        
        predictions_layout.addWidget(self.engagement_trend_card, 0, 0)
        predictions_layout.addWidget(self.governance_forecast_card, 0, 1)
        
        # Future Challenges Prediction
        challenges_group = QGroupBox("🔮 AI-Predicted Challenges & Opportunities")
        challenges_layout = QVBoxLayout()
        
        self.challenges_list = QListWidget()
        self.challenges_list.setStyleSheet("""
            QListWidget {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
            QListWidgetItem {
                padding: 10px;
                margin: 3px 0;
                background: white;
                border-left: 4px solid #ffc107;
                border-radius: 4px;
            }
        """)
        challenges_layout.addWidget(self.challenges_list)
        challenges_group.setLayout(challenges_layout)
        
        # Recommendations for Future
        future_recommendations_group = QGroupBox("📋 Strategic Recommendations")
        future_recommendations_layout = QVBoxLayout()
        
        self.future_recommendations = QTextEdit()
        self.future_recommendations.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
            }
        """)
        self.future_recommendations.setMaximumHeight(150)
        future_recommendations_layout.addWidget(self.future_recommendations)
        future_recommendations_group.setLayout(future_recommendations_layout)
        
        layout.addLayout(predictions_layout)
        layout.addWidget(challenges_group)
        layout.addWidget(future_recommendations_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_security_intelligence_tab(self) -> QWidget:
        """Create security and anomaly detection tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Security Status
        security_layout = QHBoxLayout()
        
        self.security_status_card = AnimatedMetricCard(
            "Platform Security", 
            "Loading...", 
            "Real-time threat assessment",
            "#dc3545"
        )
        
        self.anomaly_detection_card = AnimatedMetricCard(
            "Anomalies Detected", 
            "Loading...", 
            "Unusual patterns found",
            "#fd7e14"
        )
        
        security_layout.addWidget(self.security_status_card)
        security_layout.addWidget(self.anomaly_detection_card)
        
        # Security Alerts
        alerts_group = QGroupBox("🚨 Security Intelligence Alerts")
        alerts_layout = QVBoxLayout()
        
        self.security_alerts_table = QTableWidget(0, 4)
        self.security_alerts_table.setHorizontalHeaderLabels([
            "Alert Type", "Severity", "Description", "Timestamp"
        ])
        self.security_alerts_table.setStyleSheet("""
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
        header = self.security_alerts_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        alerts_layout.addWidget(self.security_alerts_table)
        alerts_group.setLayout(alerts_layout)
        
        # Security Recommendations
        security_recommendations_group = QGroupBox("🛡️ Security Recommendations")
        security_recommendations_layout = QVBoxLayout()
        
        self.security_recommendations = QTextEdit()
        self.security_recommendations.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
            }
        """)
        self.security_recommendations.setMaximumHeight(120)
        security_recommendations_layout.addWidget(self.security_recommendations)
        security_recommendations_group.setLayout(security_recommendations_layout)
        
        layout.addLayout(security_layout)
        layout.addWidget(alerts_group)
        layout.addWidget(security_recommendations_group)
        
        widget.setLayout(layout)
        return widget
    
    def refresh_ai_insights(self):
        """Refresh all AI insights with latest data"""
        try:
            user = SessionManager.get_current_user()
            if not user:
                self.show_login_required_message()
                return
            
            # Update personal insights
            self.update_personal_insights(user['email'])
            
            # Update community insights
            self.update_community_insights()
            
            # Update predictive insights
            self.update_predictive_insights()
            
            # Update security insights
            self.update_security_insights()
            
        except Exception as e:
            QMessageBox.warning(self, "AI Analysis Error", f"Failed to refresh AI insights: {str(e)}")
    
    def update_personal_insights(self, user_email: str):
        """Update personal AI insights"""
        try:
            # Get AI analysis for user
            engagement_analysis = self.ai_engine.analyze_user_engagement_patterns(user_email)
            
            # Update engagement score
            if 'engagement_score' in engagement_analysis:
                score = engagement_analysis['engagement_score']
                self.engagement_card.update_value(f"{score:.1f}/10")
                
                # Update growth progress
                self.growth_progress.setValue(int(score * 10))
                self.growth_label.setText(f"Civic Development Level: {engagement_analysis.get('civic_participation_grade', 'Unknown')}")
            
            # Update recommendations
            self.recommendations_list.clear()
            recommendations = engagement_analysis.get('personalized_recommendations', [])
            for recommendation in recommendations[:5]:  # Show top 5
                item = QListWidgetItem(recommendation)
                item.setToolTip(recommendation)  # Full text on hover
                self.recommendations_list.addItem(item)
            
            # Get personalized insights
            personal_insights = self.ai_engine.generate_personalized_civic_insights(user_email)
            
        except Exception as e:
            self.engagement_card.update_value("Error")
            print(f"Error updating personal insights: {e}")
    
    def update_community_insights(self):
        """Update community intelligence"""
        try:
            # Get governance effectiveness analysis
            governance_analysis = self.ai_engine.predict_governance_effectiveness()
            
            if 'democratic_health_index' in governance_analysis:
                health_score = governance_analysis['democratic_health_index']
                self.democracy_score_card.update_value(f"{health_score:.1f}/10")
            
            if 'performance_metrics' in governance_analysis:
                metrics = governance_analysis['performance_metrics']
                
                participation_rate = metrics.get('participation_rate', 0.0)
                self.participation_card.update_value(f"{participation_rate*100:.1f}%")
                
                consensus_score = metrics.get('consensus_building', 0.0)
                self.consensus_card.update_value(f"{consensus_score*100:.1f}%")
            
            # Update community insights text
            insights_text = "🏛️ Community Intelligence Analysis:\n\n"
            
            if 'recommendations' in governance_analysis:
                recommendations = governance_analysis['recommendations']
                
                insights_text += "📈 Immediate Improvements:\n"
                for action in recommendations.get('immediate_actions', []):
                    insights_text += f"• {action}\n"
                
                insights_text += "\n🎯 Strategic Focus Areas:\n"
                for strategy in recommendations.get('strategic_improvements', []):
                    insights_text += f"• {strategy}\n"
            
            self.community_insights.setPlainText(insights_text)
            
        except Exception as e:
            self.democracy_score_card.update_value("Error")
            print(f"Error updating community insights: {e}")
    
    def update_predictive_insights(self):
        """Update predictive intelligence"""
        try:
            # Get governance predictions
            governance_analysis = self.ai_engine.predict_governance_effectiveness()
            
            if 'system_predictions' in governance_analysis:
                predictions = governance_analysis['system_predictions']
                
                health_trend = predictions.get('overall_health_trend', 'Unknown')
                self.engagement_trend_card.update_value(health_trend.capitalize())
                
                stability = predictions.get('stability_forecast', 'Unknown')
                self.governance_forecast_card.update_value(stability.capitalize())
                
                # Update challenges list
                self.challenges_list.clear()
                challenges = predictions.get('predicted_challenges', [])
                for challenge in challenges:
                    challenge_text = f"⚠️ {challenge.get('challenge', 'Unknown Challenge')}"
                    likelihood = challenge.get('likelihood', 0.0)
                    impact = challenge.get('impact', 'Unknown')
                    
                    item_text = f"{challenge_text}\nLikelihood: {likelihood*100:.0f}% | Impact: {impact}"
                    item = QListWidgetItem(item_text)
                    self.challenges_list.addItem(item)
                
                # Add opportunities as well
                item = QListWidgetItem("🌟 Opportunity: Enhanced AI-driven civic engagement\nLikelihood: 85% | Impact: High")
                self.challenges_list.addItem(item)
                
                item = QListWidgetItem("🚀 Opportunity: Advanced blockchain transparency\nLikelihood: 90% | Impact: Medium")
                self.challenges_list.addItem(item)
            
            # Update strategic recommendations
            if 'recommendations' in governance_analysis:
                recommendations = governance_analysis['recommendations']
                strategy_text = "🔮 AI Strategic Recommendations:\n\n"
                
                for strategy in recommendations.get('strategic_improvements', []):
                    strategy_text += f"📋 {strategy}\n\n"
                
                strategy_text += "🛡️ Risk Mitigation Strategies:\n"
                for mitigation in recommendations.get('risk_mitigations', []):
                    strategy_text += f"• {mitigation}\n"
                
                self.future_recommendations.setPlainText(strategy_text)
            
        except Exception as e:
            self.engagement_trend_card.update_value("Error")
            print(f"Error updating predictive insights: {e}")
    
    def update_security_insights(self):
        """Update security intelligence"""
        try:
            # Get anomaly detection analysis
            anomaly_analysis = self.ai_engine.detect_platform_anomalies()
            
            # Update security status
            security_status = anomaly_analysis.get('security_status', 'Unknown')
            self.security_status_card.update_value(security_status.capitalize())
            
            # Update anomaly count
            anomaly_count = anomaly_analysis.get('anomalies_detected', 0)
            self.anomaly_detection_card.update_value(str(anomaly_count))
            
            # Update alerts table
            self.security_alerts_table.setRowCount(0)
            
            risk_assessment = anomaly_analysis.get('risk_assessment', {})
            all_issues = []
            
            # Add critical issues
            critical_issues = risk_assessment.get('critical_issues', [])
            for issue in critical_issues:
                all_issues.append(('Critical', issue))
            
            # Add medium issues
            medium_issues = risk_assessment.get('medium_issues', [])
            for issue in medium_issues:
                all_issues.append(('Medium', issue))
            
            # Add low issues
            low_issues = risk_assessment.get('low_issues', [])
            for issue in low_issues:
                all_issues.append(('Low', issue))
            
            # If no issues, add a positive message
            if not all_issues:
                self.security_alerts_table.setRowCount(1)
                self.security_alerts_table.setItem(0, 0, QTableWidgetItem("System Health"))
                self.security_alerts_table.setItem(0, 1, QTableWidgetItem("Good"))
                self.security_alerts_table.setItem(0, 2, QTableWidgetItem("No security anomalies detected. Platform operating normally."))
                self.security_alerts_table.setItem(0, 3, QTableWidgetItem(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
            else:
                # Populate with actual issues
                self.security_alerts_table.setRowCount(len(all_issues))
                for i, (severity, issue) in enumerate(all_issues):
                    self.security_alerts_table.setItem(i, 0, QTableWidgetItem("Security Alert"))
                    self.security_alerts_table.setItem(i, 1, QTableWidgetItem(severity))
                    self.security_alerts_table.setItem(i, 2, QTableWidgetItem(str(issue)[:100] + "..."))
                    self.security_alerts_table.setItem(i, 3, QTableWidgetItem(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
            
            # Update security recommendations
            recommendations = anomaly_analysis.get('recommendations', {})
            security_text = "🛡️ AI Security Recommendations:\n\n"
            
            immediate_actions = recommendations.get('immediate_actions', [])
            if immediate_actions:
                security_text += "⚡ Immediate Actions Required:\n"
                for action in immediate_actions:
                    security_text += f"• {action}\n"
                security_text += "\n"
            
            monitoring_suggestions = recommendations.get('monitoring_suggestions', [])
            if monitoring_suggestions:
                security_text += "👁️ Enhanced Monitoring:\n"
                for suggestion in monitoring_suggestions:
                    security_text += f"• {suggestion}\n"
                security_text += "\n"
            
            preventive_measures = recommendations.get('preventive_measures', [])
            if preventive_measures:
                security_text += "🔒 Preventive Measures:\n"
                for measure in preventive_measures:
                    security_text += f"• {measure}\n"
            
            if not immediate_actions and not monitoring_suggestions and not preventive_measures:
                security_text += "✅ Platform security is optimal. Continue current security protocols."
            
            self.security_recommendations.setPlainText(security_text)
            
        except Exception as e:
            self.security_status_card.update_value("Error")
            print(f"Error updating security insights: {e}")
    
    def show_login_required_message(self):
        """Show message when user needs to log in"""
        self.engagement_card.update_value("Login Required")
        self.recommendations_list.clear()
        item = QListWidgetItem("🔐 Please log in to see your personalized AI insights and recommendations")
        self.recommendations_list.addItem(item)


class SmartAIDashboard(QWidget):
    """
    🚀 Main Smart AI-Powered Dashboard Widget
    
    Combines all AI intelligence features into a comprehensive dashboard
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_auto_refresh()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Dashboard Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🤖 AI-Powered Civic Intelligence Dashboard")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("""
            color: #2c3e50;
            padding: 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(52, 152, 219, 0.1), stop:1 rgba(155, 89, 182, 0.1));
            border-radius: 10px;
            border: 2px solid #3498db;
        """)
        header_layout.addWidget(title_label)
        
        # Refresh Button
        refresh_btn = QPushButton("🔄 Refresh AI Analysis")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(90deg, #3498db 0%, #2ecc71 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: linear-gradient(90deg, #2980b9 0%, #27ae60 100%);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
        """)
        refresh_btn.clicked.connect(self.refresh_all_intelligence)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # AI Insights Widget
        self.ai_insights_widget = AIInsightWidget()
        layout.addWidget(self.ai_insights_widget)
        
        # Auto-update status
        self.status_label = QLabel("🔄 AI Analysis auto-updates every 30 seconds")
        self.status_label.setStyleSheet("""
            color: #6c757d;
            font-style: italic;
            padding: 5px;
            text-align: center;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Initial load
        QTimer.singleShot(1000, self.refresh_all_intelligence)  # Load after 1 second
    
    def setup_auto_refresh(self):
        """Setup automatic refresh of AI insights"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_intelligence)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def refresh_all_intelligence(self):
        """Refresh all AI intelligence data"""
        try:
            self.status_label.setText("🔄 Updating AI analysis...")
            QApplication.processEvents()  # Update UI immediately
            
            # Refresh AI insights
            self.ai_insights_widget.refresh_ai_insights()
            
            self.status_label.setText(f"✅ AI Analysis updated at {datetime.datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_label.setText(f"❌ AI Analysis failed: {str(e)}")
            print(f"Error refreshing AI intelligence: {e}")
    
    def refresh_ui(self):
        """Refresh UI (called by main window)"""
        self.refresh_all_intelligence()


# Export the main dashboard class
__all__ = ['SmartAIDashboard']