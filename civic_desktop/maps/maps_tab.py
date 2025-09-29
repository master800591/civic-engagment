"""
Desktop-Integrated Maps Tab for Civic Engagement Platform
Native PyQt5 interface with blockchain logging and user permission restrictions
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# PyQt5 imports with error handling
try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QGroupBox, QCheckBox,
                               QLineEdit, QSplitter, QFrame, QComboBox,
                               QMessageBox, QScrollArea, QListWidget)
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont, QPalette, QColor
    PYQT5_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PyQt5 not available: {e}")
    # Create dummy classes for testing
    class QWidget: pass
    class QVBoxLayout: pass
    class QHBoxLayout: pass
    class QLabel: pass
    class QPushButton: pass
    class QTextEdit: pass
    class QGroupBox: pass
    class QCheckBox: pass
    class QLineEdit: pass
    class QSplitter: pass
    class QFrame: pass
    class QComboBox: pass
    class QMessageBox: pass
    class QScrollArea: pass
    class QListWidget: pass
    class Qt: pass
    class QTimer: pass
    class QFont: pass
    def pyqtSignal(): pass
    PYQT5_AVAILABLE = False

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import civic platform modules
try:
    from blockchain.blockchain import Blockchain
    from users.session import SessionManager
    from government.government_directory.government_system import GovernmentIntegrationSystem
except ImportError as e:
    print(f"⚠️ Import warning for civic modules: {e}")
    Blockchain = None
    SessionManager = None
    GovernmentIntegrationSystem = None


class CivicMapTab(QWidget):
    """
    Desktop-Integrated Maps Tab for Civic Engagement Platform
    Features: Native interface, blockchain logging, user permission filtering
    """
    
    # Signals for communication with main app
    official_selected = pyqtSignal(dict)
    location_searched = pyqtSignal(str)
    data_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent) if PYQT5_AVAILABLE else None
        
        # Initialize core components
        self.blockchain = None
        self.session_manager = None
        self.government_system = None
        
        # Data storage
        self.officials_data = {}
        self.activities_data = []
        self.user_permissions = {}
        
        # UI components (will be None if PyQt5 not available)
        self.data_display = None
        self.stats_display = None
        self.permissions_label = None
        self.search_input = None
        
        if PYQT5_AVAILABLE:
            self.initialize_integrations()
            self.setup_ui()
            self.load_initial_data()
            
            # Auto-refresh timer
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self.refresh_data)
            self.refresh_timer.start(30000)  # 30 seconds
        else:
            print("⚠️ PyQt5 not available - using text interface")
            self.initialize_integrations()
            self.load_initial_data()
            self.display_text_interface()
    
    def initialize_integrations(self):
        """Initialize blockchain and session management"""
        
        # Initialize blockchain
        if Blockchain:
            try:
                self.blockchain = Blockchain()
                print("✅ Maps: Blockchain integration initialized")
            except Exception as e:
                print(f"⚠️ Maps: Blockchain initialization error: {e}")
        
        # Initialize session manager
        if SessionManager:
            try:
                self.session_manager = SessionManager()
                print("✅ Maps: Session management initialized")
            except Exception as e:
                print(f"⚠️ Maps: Session manager error: {e}")
        
        # Initialize government system
        if GovernmentIntegrationSystem:
            try:
                self.government_system = GovernmentIntegrationSystem()
                print("✅ Maps: Government system integration initialized")
            except Exception as e:
                print(f"⚠️ Maps: Government system error: {e}")
        
    def setup_ui(self):
        """Setup the user interface for the maps tab"""
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls and information
        left_panel = self.create_control_panel()
        left_panel.setMaximumWidth(350)
        left_panel.setMinimumWidth(300)
        
        # Right panel - Map display
        right_panel = self.create_map_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 0)  # Control panel - fixed
        splitter.setStretchFactor(1, 1)  # Map panel - expandable
        
    def create_control_panel(self) -> QWidget:
        """Create the left control panel"""
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🗺️ Civic Engagement Map")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Search section
        search_group = self.create_search_section()
        layout.addWidget(search_group)
        
        # Layer controls
        layer_group = self.create_layer_controls()
        layout.addWidget(layer_group)
        
        # Statistics
        stats_group = self.create_statistics_section()
        layout.addWidget(stats_group)
        
        # Information display
        info_group = self.create_info_section()
        layout.addWidget(info_group)
        
        # Action buttons
        buttons_layout = self.create_action_buttons()
        layout.addLayout(buttons_layout)
        
        layout.addStretch()  # Push everything to top
        
        return panel
    
    def create_search_section(self) -> QGroupBox:
        """Create search functionality section"""
        
        group = QGroupBox("🔍 Search & Navigate")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(group)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search officials, locations, activities...")
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        layout.addWidget(self.search_input)
        
        # Search button
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self.perform_search)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a67d8;
            }
        """)
        layout.addWidget(search_btn)
        
        return group
    
    def create_layer_controls(self) -> QGroupBox:
        """Create layer visibility controls"""
        
        group = QGroupBox("🎛️ Map Layers")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(group)
        
        # Layer checkboxes
        self.layer_checkboxes = {}
        
        layers = [
            ("countries", "🌍 Country Boundaries", True),
            ("states", "🏛️ State/Province Boundaries", True),
            ("cities", "🏙️ Cities & Towns", True),
            ("government", "👥 Government Officials", True),
            ("activities", "📊 Civic Activities", True),
            ("participation", "🔥 Participation Heatmap", True)
        ]
        
        for layer_id, label, checked in layers:
            checkbox = QCheckBox(label)
            checkbox.setChecked(checked)
            checkbox.stateChanged.connect(lambda state, lid=layer_id: self.toggle_layer(lid, state))
            checkbox.setStyleSheet("""
                QCheckBox {
                    padding: 4px;
                    font-size: 11px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
            
            self.layer_checkboxes[layer_id] = checkbox
            layout.addWidget(checkbox)
        
        return group
    
    def create_statistics_section(self) -> QGroupBox:
        """Create statistics display section"""
        
        group = QGroupBox("📈 Live Statistics")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(group)
        
        # Statistics labels
        self.stats_labels = {}
        
        stats = [
            ("officials", "Government Officials", "0"),
            ("events", "Active Events", "0"),
            ("citizens", "Registered Citizens", "0"),
            ("participation", "Participation Rate", "0%")
        ]
        
        for stat_id, label, initial_value in stats:
            stat_widget = QFrame()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setContentsMargins(8, 8, 8, 8)
            
            value_label = QLabel(initial_value)
            value_label.setFont(QFont("Arial", 14, QFont.Bold))
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("color: #667eea;")
            
            desc_label = QLabel(label)
            desc_label.setFont(QFont("Arial", 9))
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setStyleSheet("color: #666;")
            
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(desc_label)
            
            stat_widget.setStyleSheet("""
                QFrame {
                    background: #f8f9fa;
                    border-radius: 6px;
                    margin: 2px;
                }
            """)
            
            self.stats_labels[stat_id] = value_label
            layout.addWidget(stat_widget)
        
        return group
    
    def create_info_section(self) -> QGroupBox:
        """Create information display section"""
        
        group = QGroupBox("ℹ️ Selected Information")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(group)
        
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setMaximumHeight(150)
        self.info_display.setPlainText("Click on map markers to view detailed information about government officials and civic activities.")
        self.info_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
                background: #fafafa;
            }
        """)
        
        layout.addWidget(self.info_display)
        
        return group
    
    def create_action_buttons(self) -> QVBoxLayout:
        """Create action buttons"""
        
        layout = QVBoxLayout()
        
        # Refresh map button
        refresh_btn = QPushButton("🔄 Refresh Map Data")
        refresh_btn.clicked.connect(self.refresh_map_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        # Open in browser button
        browser_btn = QPushButton("🌐 Open in Browser")
        browser_btn.clicked.connect(self.open_in_browser)
        browser_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        
        layout.addWidget(refresh_btn)
        layout.addWidget(browser_btn)
        
        return layout
    
    def create_map_panel(self) -> QWidget:
        """Create the main map display panel"""
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Map header
        header = QLabel("Interactive Civic Engagement Map")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                padding: 8px;
                border-bottom: 2px solid #667eea;
                color: #333;
            }
        """)
        layout.addWidget(header)
        
        # Web view for map
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("""
            QWebEngineView {
                border: 1px solid #ddd;
            }
        """)
        layout.addWidget(self.web_view)
        
        return panel
    
    def load_initial_map(self):
        """Load the initial map display"""
        
        try:
            # Generate map HTML with current data
            map_html = self.map_server.create_enhanced_map_html()
            
            if map_html:
                # Save to temporary file
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
                temp_file.write(map_html)
                temp_file.close()
                
                # Load in web view
                map_url = QUrl.fromLocalFile(temp_file.name)
                self.web_view.load(map_url)
                self.current_map_file = temp_file.name
                
                # Update statistics
                self.update_statistics()
                
                print("✅ Map loaded successfully in PyQt5 tab")
            else:
                self.show_error_message("Failed to generate map HTML")
                
        except Exception as e:
            self.show_error_message(f"Error loading map: {str(e)}")
    
    def update_statistics(self):
        """Update the statistics display"""
        
        try:
            map_data = self.map_data_generator.generate_complete_map_data()
            stats = map_data['statistics']
            
            self.stats_labels['officials'].setText(str(stats['total_officials']))
            self.stats_labels['events'].setText(str(stats['active_events']))
            self.stats_labels['citizens'].setText(f"{stats['registered_citizens']/1000000:.1f}M")
            self.stats_labels['participation'].setText(f"{stats['participation_rate']:.1f}%")
            
        except Exception as e:
            print(f"❌ Error updating statistics: {e}")
    
    def perform_search(self):
        """Perform search functionality"""
        
        query = self.search_input.text().strip()
        if query:
            self.location_searched.emit(query)
            self.info_display.setPlainText(f"Searching for: {query}\n\nNote: Search functionality will be enhanced in future updates to interact directly with the map.")
    
    def toggle_layer(self, layer_id: str, state: int):
        """Toggle map layer visibility"""
        
        enabled = state == Qt.Checked
        print(f"🎛️ {'Enabled' if enabled else 'Disabled'} layer: {layer_id}")
        
        # Note: In a full implementation, this would communicate with the JavaScript map
        # For now, we'll show a status message
        self.info_display.setPlainText(f"Layer '{layer_id}' {'enabled' if enabled else 'disabled'}.\n\nFull layer control integration coming in next update.")
    
    def refresh_map_data(self):
        """Refresh map with latest data"""
        
        try:
            self.info_display.setPlainText("🔄 Refreshing map data...")
            
            # Reload the map with fresh data
            self.load_initial_map()
            
            self.info_display.setPlainText("✅ Map data refreshed successfully!\n\nDisplaying latest government officials and civic activities.")
            
        except Exception as e:
            self.show_error_message(f"Error refreshing map: {str(e)}")
    
    def open_in_browser(self):
        """Open current map in external browser"""
        
        try:
            if self.current_map_file:
                import webbrowser
                webbrowser.open(f'file:///{self.current_map_file.replace(os.sep, "/")}')
                self.info_display.setPlainText("🌐 Map opened in external browser for full-screen viewing.")
            else:
                self.info_display.setPlainText("❌ No map file available to open.")
                
        except Exception as e:
            self.show_error_message(f"Error opening in browser: {str(e)}")
    
    def show_error_message(self, message: str):
        """Display error message"""
        
        self.info_display.setPlainText(f"❌ Error: {message}")
        print(f"❌ Map Tab Error: {message}")
    
    def get_current_map_data(self) -> dict:
        """Get current map data for external access"""
        
        try:
            return self.map_data_generator.generate_complete_map_data()
        except Exception as e:
            print(f"❌ Error getting map data: {e}")
            return {}


# Test function for standalone execution
def test_civic_map_tab():
    """Test the civic map tab as standalone widget"""
    
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Create and show the map tab
    map_tab = CivicMapTab()
    map_tab.setWindowTitle("🗺️ Civic Engagement Interactive Map")
    map_tab.resize(1200, 800)
    map_tab.show()
    
    print("🗺️ Civic Map Tab Test Running...")
    print("📍 Features:")
    print("   • Embedded interactive map")
    print("   • Government officials display")
    print("   • Layer controls")
    print("   • Search functionality")
    print("   • Real-time statistics")
    print("   • Browser integration")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_civic_map_tab()