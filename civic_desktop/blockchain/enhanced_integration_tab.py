"""
Enhanced Blockchain Integration Dashboard
Shows comprehensive blockchain integration across all modules
"""

import sys
from datetime import datetime, timezone
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTabWidget, QTextEdit, QLabel, QProgressBar,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QGroupBox, QScrollArea, QFrame, QSplitter, QAbstractItemView)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

from ..blockchain.blockchain import Blockchain, ValidatorRegistry
from ..blockchain.integration_manager import BlockchainIntegrationManager
from ..users.session import SessionManager


class IntegrationAnalyticsWorker(QThread):
    """Background worker for analytics calculations"""
    analytics_ready = pyqtSignal(dict)
    
    def run(self):
        try:
            # Generate comprehensive analytics
            module_stats = BlockchainIntegrationManager.get_module_statistics()
            health_report = BlockchainIntegrationManager.generate_integration_health_report()
            connection_map = BlockchainIntegrationManager.create_module_connection_map()
            
            analytics = {
                'module_stats': module_stats,
                'health_report': health_report,
                'connection_map': connection_map,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.analytics_ready.emit(analytics)
        except Exception as e:
            print(f"Analytics calculation error: {e}")


class EnhancedBlockchainTab(QWidget):
    """Enhanced blockchain tab with comprehensive integration monitoring"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_worker = None
        self.current_analytics = None
        self.init_ui()
        self.setup_auto_refresh()
        
    def init_ui(self):
        layout = QVBoxLayout()
        # Blockchain status and user role display
        from civic_desktop.users.session import SessionManager
        user = SessionManager.get_current_user()
        role = user.get('role', 'Unknown') if user else 'Unknown'
        blockchain_status = QLabel("All integration analytics are <b>recorded on blockchain</b> for audit and transparency.")
        blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
        role_label = QLabel(f"Your Role: <b>{role}</b>")
        role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
        export_btn = QPushButton("Export Integration Report")
        export_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 5px; padding: 8px 18px;")
        export_btn.clicked.connect(self.open_reports_tab)
        top_layout = QVBoxLayout()
        top_layout.addWidget(blockchain_status)
        top_layout.addWidget(role_label)
        top_layout.addWidget(export_btn)
        layout.addLayout(top_layout)
        # Header with title and status
        header_layout = QHBoxLayout()
        title_label = QLabel("🔗 Enhanced Blockchain Integration Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.status_label = QLabel("🔄 Loading...")
        header_layout.addWidget(self.status_label)
        refresh_btn = QPushButton("🔄 Refresh Analytics")
        refresh_btn.clicked.connect(self.refresh_analytics)
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)
        # Create tabbed interface
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_overview_tab(), "📊 Overview")
        self.tab_widget.addTab(self.create_analytics_tab(), "📈 Analytics")
        self.tab_widget.addTab(self.create_dependencies_tab(), "🔗 Dependencies")
        self.tab_widget.addTab(self.create_health_tab(), "🏥 Health")
        self.tab_widget.addTab(self.create_activity_tab(), "👤 User Activity")
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        self.refresh_analytics()

    def open_reports_tab(self):
        mw = self.parent()
        while mw and not hasattr(mw, 'tabs'):
            mw = mw.parent()
        if mw and hasattr(mw, 'tabs'):
            for i in range(mw.tabs.count()):
                if mw.tabs.tabText(i).lower().startswith("📊 reports") or mw.tabs.tabText(i).lower().startswith("reports"):
                    mw.tabs.setCurrentIndex(i)
                    break
    
    def create_overview_tab(self) -> QWidget:
        """Create the integration overview tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Summary statistics
        summary_group = QGroupBox("Integration Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(200)
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Module connection visualization
        connections_group = QGroupBox("Module Connections")
        connections_layout = QVBoxLayout()
        
        self.connections_text = QTextEdit()
        self.connections_text.setReadOnly(True)
        connections_layout.addWidget(self.connections_text)
        
        connections_group.setLayout(connections_layout)
        layout.addWidget(connections_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_analytics_tab(self) -> QWidget:
        """Create the module analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Module statistics table
        stats_group = QGroupBox("Module Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(['Module', 'Total Actions', 'Active Users', 'Health Status'])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Make statistics table read-only to prevent editing of reports
        self.stats_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stats_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        stats_layout.addWidget(self.stats_table)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Performance metrics
        performance_group = QGroupBox("Performance Metrics")
        performance_layout = QVBoxLayout()
        
        self.performance_text = QTextEdit()
        self.performance_text.setMaximumHeight(200)
        self.performance_text.setReadOnly(True)
        performance_layout.addWidget(self.performance_text)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_dependencies_tab(self) -> QWidget:
        """Create the cross-module dependencies tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Current user analysis
        user_analysis_group = QGroupBox("Current User Analysis")
        user_layout = QVBoxLayout()
        
        self.user_analysis_text = QTextEdit()
        self.user_analysis_text.setReadOnly(True)
        user_layout.addWidget(self.user_analysis_text)
        
        user_analysis_group.setLayout(user_layout)
        layout.addWidget(user_analysis_group)
        
        # System-wide dependencies
        system_deps_group = QGroupBox("System Dependencies")
        system_layout = QVBoxLayout()
        
        self.system_deps_text = QTextEdit()
        self.system_deps_text.setReadOnly(True)
        system_layout.addWidget(self.system_deps_text)
        
        system_deps_group.setLayout(system_layout)
        layout.addWidget(system_deps_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_health_tab(self) -> QWidget:
        """Create the health monitoring tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Overall health status
        health_status_group = QGroupBox("Overall System Health")
        health_layout = QVBoxLayout()
        
        self.health_status_label = QLabel("🔄 Calculating...")
        health_status_font = QFont()
        health_status_font.setPointSize(14)
        health_status_font.setBold(True)
        self.health_status_label.setFont(health_status_font)
        health_layout.addWidget(self.health_status_label)
        
        self.health_progress = QProgressBar()
        self.health_progress.setRange(0, 100)
        health_layout.addWidget(self.health_progress)
        
        health_status_group.setLayout(health_layout)
        layout.addWidget(health_status_group)
        
        # Detailed health report
        health_details_group = QGroupBox("Detailed Health Report")
        details_layout = QVBoxLayout()
        
        self.health_details_text = QTextEdit()
        self.health_details_text.setReadOnly(True)
        details_layout.addWidget(self.health_details_text)
        
        health_details_group.setLayout(details_layout)
        layout.addWidget(health_details_group)
        
        # Recommendations
        recommendations_group = QGroupBox("Recommendations")
        rec_layout = QVBoxLayout()
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setMaximumHeight(150)
        self.recommendations_text.setReadOnly(True)
        rec_layout.addWidget(self.recommendations_text)
        
        recommendations_group.setLayout(rec_layout)
        layout.addWidget(recommendations_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_activity_tab(self) -> QWidget:
        """Create the user activity analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Top contributors
        contributors_group = QGroupBox("Top Contributors")
        contrib_layout = QVBoxLayout()
        
        self.contributors_table = QTableWidget()
        self.contributors_table.setColumnCount(3)
        self.contributors_table.setHorizontalHeaderLabels(['Email', 'Total Actions', 'Trust Score'])
        self.contributors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.contributors_table.setMaximumHeight(200)
        # Make contributors table read-only to prevent editing of reports
        self.contributors_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.contributors_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        contrib_layout.addWidget(self.contributors_table)
        
        contributors_group.setLayout(contrib_layout)
        layout.addWidget(contributors_group)
        
        # Activity patterns
        patterns_group = QGroupBox("Activity Patterns")
        patterns_layout = QVBoxLayout()
        
        self.patterns_text = QTextEdit()
        self.patterns_text.setReadOnly(True)
        patterns_layout.addWidget(self.patterns_text)
        
        patterns_group.setLayout(patterns_layout)
        layout.addWidget(patterns_group)
        
        widget.setLayout(layout)
        return widget
    
    def setup_auto_refresh(self):
        """Setup automatic refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_analytics)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def refresh_analytics(self):
        """Refresh all analytics data"""
        self.status_label.setText("🔄 Refreshing...")
        
        if self.analytics_worker and self.analytics_worker.isRunning():
            return
        
        self.analytics_worker = IntegrationAnalyticsWorker()
        self.analytics_worker.analytics_ready.connect(self.update_display)
        self.analytics_worker.start()
    
    def update_display(self, analytics: dict):
        """Update all display elements with new analytics"""
        try:
            self.current_analytics = analytics
            
            # Update overview tab
            self.update_overview_tab(analytics)
            
            # Update analytics tab
            self.update_analytics_tab(analytics)
            
            # Update dependencies tab
            self.update_dependencies_tab(analytics)
            
            # Update health tab
            self.update_health_tab(analytics)
            
            # Update activity tab
            self.update_activity_tab(analytics)
            
            # Update status
            self.status_label.setText(f"✅ Updated at {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
    
    def update_overview_tab(self, analytics: dict):
        """Update the overview tab"""
        module_stats = analytics.get('module_stats', {})
        connection_map = analytics.get('connection_map', {})
        
        # Summary text
        summary = f"""
🔗 Enhanced Blockchain Integration Summary
═══════════════════════════════════════════

📊 Total Blockchain Pages: {module_stats.get('total_pages', 0)}
👥 Total Users: {module_stats.get('users', {}).get('total', 0)}
🏃 Active Users (30 days): {module_stats.get('users', {}).get('active_last_30_days', 0)}
⛓️ Active Validators: {module_stats.get('blockchain', {}).get('validators', 0)}
🔒 Chain Integrity: {'✅ Valid' if module_stats.get('blockchain', {}).get('chain_integrity') else '❌ Compromised'}

Module Activity:
├── 💬 Debates: {module_stats.get('debates', {}).get('topics', 0)} topics, {module_stats.get('debates', {}).get('arguments', 0)} arguments, {module_stats.get('debates', {}).get('votes', 0)} votes
├── 🛡️ Moderation: {module_stats.get('moderation', {}).get('flags', 0)} flags, {module_stats.get('moderation', {}).get('reviews', 0)} reviews
├── 🎓 Training: {module_stats.get('training', {}).get('courses_started', 0)} courses started, {module_stats.get('training', {}).get('certifications', 0)} certifications
└── 🏛️ Governance: {module_stats.get('governance', {}).get('elections', 0)} elections, {module_stats.get('governance', {}).get('proposals', 0)} proposals
"""
        self.summary_text.setPlainText(summary)
        
        # Connection visualization
        connections = connection_map.get('interaction_summary', {})
        connection_text = "🔗 Module Interaction Summary:\\n"
        connection_text += "═══════════════════════════════\\n\\n"
        
        for interaction, count in connections.items():
            modules = interaction.replace('_', ' → ').title()
            connection_text += f"{modules}: {count} interactions\\n"
        
        if not connections:
            connection_text += "No module interactions recorded yet."
        
        self.connections_text.setPlainText(connection_text)
    
    def update_analytics_tab(self, analytics: dict):
        """Update the analytics tab"""
        module_stats = analytics.get('module_stats', {})
        health_report = analytics.get('health_report', {})
        
        # Update statistics table
        modules = ['users', 'debates', 'moderation', 'training', 'governance', 'blockchain']
        self.stats_table.setRowCount(len(modules))
        
        for i, module in enumerate(modules):
            module_data = module_stats.get(module, {})
            health_status = health_report.get('module_status', {}).get(module, {}).get('status', 'unknown')
            
            self.stats_table.setItem(i, 0, QTableWidgetItem(module.title()))
            
            # Calculate total actions based on module
            if module == 'users':
                total_actions = module_data.get('total', 0)
            elif module == 'debates':
                total_actions = module_data.get('topics', 0) + module_data.get('arguments', 0) + module_data.get('votes', 0)
            elif module == 'moderation':
                total_actions = module_data.get('flags', 0) + module_data.get('reviews', 0)
            elif module == 'training':
                total_actions = module_data.get('courses_started', 0) + module_data.get('certifications', 0)
            elif module == 'governance':
                total_actions = module_data.get('elections', 0) + module_data.get('proposals', 0)
            elif module == 'blockchain':
                total_actions = module_data.get('validators', 0)
            else:
                total_actions = 0
            
            self.stats_table.setItem(i, 1, QTableWidgetItem(str(total_actions)))
            self.stats_table.setItem(i, 2, QTableWidgetItem(str(module_stats.get('users', {}).get('active_last_30_days', 0))))
            
            # Color-code health status
            status_item = QTableWidgetItem(health_status.title())
            if health_status == 'healthy':
                status_item.setBackground(QColor(200, 255, 200))
            elif health_status == 'warning':
                status_item.setBackground(QColor(255, 255, 200))
            elif health_status == 'critical':
                status_item.setBackground(QColor(255, 200, 200))
            
            self.stats_table.setItem(i, 3, status_item)
        
        # Performance metrics
        performance_text = f"""
⚡ Performance Metrics
═══════════════════════

📊 Average Quiz Score: {module_stats.get('training', {}).get('avg_score', 0):.1f}%
⏱️ Average Flag Resolution: {module_stats.get('moderation', {}).get('avg_resolution_time', 0):.1f} hours
🎯 Active Topics: {module_stats.get('debates', {}).get('active_topics', 0)}
👑 Top Contributors: {len(module_stats.get('top_contributors', []))}

📈 Recent Activity Trends:
• Users joined in last 30 days: {module_stats.get('users', {}).get('active_last_30_days', 0)}
• Debate engagement: {module_stats.get('debates', {}).get('arguments', 0) / max(module_stats.get('debates', {}).get('topics', 1), 1):.1f} arguments per topic
• Moderation workload: {module_stats.get('moderation', {}).get('flags', 0)} pending flags
"""
        self.performance_text.setPlainText(performance_text)
    
    def update_dependencies_tab(self, analytics: dict):
        """Update the dependencies tab"""
        # Current user analysis
        user = SessionManager.get_current_user()
        if user:
            user_deps = BlockchainIntegrationManager.get_cross_module_dependencies(user['email'])
            user_activity = BlockchainIntegrationManager.get_user_activity_summary(user['email'])
            
            user_text = f"""
👤 Current User: {user['email']}
═══════════════════════════════════

🏆 Trust Score: {user_deps.get('blockchain_trust_score', 0):.1f}/100
📊 Total Actions: {user_activity.get('total_actions', 0)}
📅 Member Since: {user_activity.get('registration_date', 'Unknown')}

Module Participation:
├── 💬 Debates: {user_activity.get('debates', {}).get('topics_created', 0)} topics, {user_activity.get('debates', {}).get('votes_cast', 0)} votes
├── 🛡️ Moderation: {user_activity.get('moderation', {}).get('flags_submitted', 0)} flags submitted
├── 🎓 Training: {user_activity.get('training', {}).get('certifications_earned', 0)} certifications
└── ⛓️ Blockchain: {user_activity.get('blockchain_participation', {}).get('blocks_validated', 0)} blocks validated

Permissions & Restrictions:
"""
            
            permissions = BlockchainIntegrationManager.get_user_permissions(user['email'])
            for perm, value in permissions.items():
                if isinstance(value, bool):
                    status = "✅" if value else "❌"
                    user_text += f"• {perm.replace('_', ' ').title()}: {status}\\n"
            
            if permissions.get('restrictions'):
                user_text += "\\n⚠️ Active Restrictions:\\n"
                for restriction in permissions['restrictions']:
                    user_text += f"• {restriction}\\n"
            
            if user_deps.get('recommended_actions'):
                user_text += "\\n💡 Recommended Actions:\\n"
                for action in user_deps['recommended_actions']:
                    user_text += f"• {action}\\n"
            
            self.user_analysis_text.setPlainText(user_text)
        else:
            self.user_analysis_text.setPlainText("Please log in to see user analysis.")
        
        # System dependencies
        connection_map = analytics.get('connection_map', {})
        system_text = f"""
🔗 System-Wide Dependencies
═══════════════════════════

Module Interaction Patterns:
"""
        
        edges = connection_map.get('edges', [])
        for edge in edges:
            system_text += f"• {edge['source'].title()} → {edge['target'].title()}: {edge['type'].replace('_', ' ').title()} (Strength: {edge['strength']})\\n"
        
        if not edges:
            system_text += "No interaction patterns recorded yet."
        
        self.system_deps_text.setPlainText(system_text)
    
    def update_health_tab(self, analytics: dict):
        """Update the health monitoring tab"""
        health_report = analytics.get('health_report', {})
        
        # Overall health status
        overall_health = health_report.get('overall_health', 'unknown')
        health_colors = {
            'healthy': ('🟢 System Healthy', 90, QColor(200, 255, 200)),
            'warning': ('🟡 System Warning', 60, QColor(255, 255, 200)),
            'degraded': ('🟠 System Degraded', 40, QColor(255, 200, 150)),
            'critical': ('🔴 System Critical', 20, QColor(255, 200, 200))
        }
        
        status_text, progress_value, color = health_colors.get(overall_health, ('❓ Unknown', 0, QColor(200, 200, 200)))
        
        self.health_status_label.setText(status_text)
        self.health_progress.setValue(progress_value)
        
        # Style the progress bar
        self.health_progress.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color.name()};
            }}
        """)
        
        # Detailed health report
        details_text = f"""
🏥 Detailed Health Analysis
═══════════════════════════

Overall Status: {overall_health.upper()}

Module Health Status:
"""
        
        module_status = health_report.get('module_status', {})
        for module, status_data in module_status.items():
            status = status_data.get('status', 'unknown')
            issues = status_data.get('issues', [])
            
            status_icon = {'healthy': '✅', 'warning': '⚠️', 'critical': '❌'}.get(status, '❓')
            details_text += f"{status_icon} {module.title()}: {status.upper()}\\n"
            
            if issues:
                for issue in issues:
                    details_text += f"  • {issue}\\n"
            details_text += "\\n"
        
        # Integration metrics
        integration_metrics = health_report.get('integration_metrics', {})
        details_text += f"""
🔗 Integration Health:
• Cross-module consistency: {integration_metrics.get('cross_module_consistency', 'unknown').upper()}
• Data flow integrity: {integration_metrics.get('data_flow_integrity', 'unknown').upper()}
• Blockchain sync status: {integration_metrics.get('blockchain_sync_status', 'unknown').upper()}

📊 Performance Metrics:
• Total blockchain pages: {integration_metrics.get('performance_metrics', {}).get('total_blockchain_pages', 0)}
• Active modules: {integration_metrics.get('performance_metrics', {}).get('modules_with_activity', 0)}
• Blockchain validators: {integration_metrics.get('performance_metrics', {}).get('blockchain_validator_count', 0)}
"""
        
        if integration_metrics.get('integration_errors'):
            details_text += "\\n❌ Integration Errors:\\n"
            for error in integration_metrics['integration_errors']:
                details_text += f"  • {error}\\n"
        
        self.health_details_text.setPlainText(details_text)
        
        # Recommendations
        recommendations = health_report.get('recommendations', [])
        recommendations.extend(integration_metrics.get('recommended_optimizations', []))
        
        if recommendations:
            rec_text = "💡 Recommendations:\\n\\n"
            for i, rec in enumerate(recommendations, 1):
                rec_text += f"{i}. {rec}\\n"
        else:
            rec_text = "✅ No recommendations - system operating optimally!"
        
        self.recommendations_text.setPlainText(rec_text)
    
    def update_activity_tab(self, analytics: dict):
        """Update the user activity analysis tab"""
        module_stats = analytics.get('module_stats', {})
        
        # Top contributors table
        top_contributors = module_stats.get('top_contributors', [])
        self.contributors_table.setRowCount(len(top_contributors))
        
        for i, contributor in enumerate(top_contributors):
            email = contributor.get('email', '')
            actions = contributor.get('actions', 0)
            
            # Calculate trust score for each contributor
            try:
                user_deps = BlockchainIntegrationManager.get_cross_module_dependencies(email)
                trust_score = user_deps.get('blockchain_trust_score', 0.0)
            except:
                trust_score = 0.0
            
            self.contributors_table.setItem(i, 0, QTableWidgetItem(email))
            self.contributors_table.setItem(i, 1, QTableWidgetItem(str(actions)))
            self.contributors_table.setItem(i, 2, QTableWidgetItem(f"{trust_score:.1f}"))
        
        # Activity patterns
        activity_by_date = module_stats.get('activity_by_date', {})
        patterns_text = f"""
📈 Activity Patterns Analysis
═══════════════════════════

📅 Recent Activity (Last 7 Days):
"""
        
        # Show recent activity
        import datetime
        recent_dates = []
        today = datetime.datetime.now()
        for i in range(7):
            date = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            recent_dates.append(date)
        
        for date in reversed(recent_dates):
            activity_count = activity_by_date.get(date, 0)
            bar = "█" * min(activity_count, 20)  # Visual bar
            patterns_text += f"{date}: {bar} ({activity_count} actions)\\n"
        
        patterns_text += f"""

📊 User Engagement Metrics:
• Average actions per user: {module_stats.get('total_pages', 0) / max(module_stats.get('users', {}).get('total', 1), 1):.1f}
• Active user ratio: {module_stats.get('users', {}).get('active_last_30_days', 0) / max(module_stats.get('users', {}).get('total', 1), 1) * 100:.1f}%
• Most active contributors: {len(top_contributors)} users with significant activity

🏆 Platform Participation:
• Debate creators: {len([c for c in top_contributors if c.get('actions', 0) > 5])} active users
• Content moderators: Active moderation community
• Training participants: {module_stats.get('training', {}).get('certifications', 0)} certified users
"""
        
        self.patterns_text.setPlainText(patterns_text)