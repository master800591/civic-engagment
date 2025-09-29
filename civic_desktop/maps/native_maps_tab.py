"""
Native Desktop Maps Module for Civic Engagement Platform
Integrated with blockchain, user permissions, and role-based data access
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QGroupBox, QCheckBox,
                           QLineEdit, QSplitter, QFrame, QComboBox,
                           QScrollArea, QListWidget, QListWidgetItem,
                           QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter, QPen, QBrush
from PyQt5.QtWidgets import QApplication

# Add parent directories for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import blockchain and user system
try:
    from blockchain.blockchain import Blockchain
    from users.session import SessionManager
    from government.government_directory.government_system import GovernmentIntegrationSystem
except ImportError as e:
    print(f"⚠️ Import warning: {e}")


class MapCanvas(QWidget):
    """
    Native canvas for drawing maps without web dependencies
    """
    
    location_clicked = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.officials = []
        self.activities = []
        self.user_location = None
        self.zoom_level = 1.0
        self.center_lat = 39.8283
        self.center_lon = -98.5795
        self.selected_official = None
        
        # Colors for different official types
        self.official_colors = {
            'president': QColor(255, 68, 68),      # Red
            'prime_minister': QColor(255, 68, 68), # Red
            'vice_president': QColor(255, 102, 102), # Light Red
            'governor': QColor(68, 68, 255),       # Blue
            'mayor': QColor(68, 255, 68),          # Green
            'senator': QColor(136, 68, 255),       # Purple
            'representative': QColor(68, 255, 255), # Cyan
            'other': QColor(128, 128, 128)         # Gray
        }
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
                border: 2px solid #4a90e2;
                border-radius: 8px;
            }
        """)
    
    def set_officials_data(self, officials: List[Dict]):
        """Set officials data for map display"""
        self.officials = officials
        self.update()
    
    def set_activities_data(self, activities: List[Dict]):
        """Set activities data for map display"""
        self.activities = activities
        self.update()
    
    def set_user_location(self, lat: float, lon: float):
        """Set user's location for location-based filtering"""
        self.user_location = (lat, lon)
        self.update()
    
    def coordinate_to_pixel(self, lat: float, lon: float) -> tuple:
        """Convert geographic coordinates to pixel coordinates"""
        width = self.width()
        height = self.height()
        
        # Simple mercator-like projection
        x = int((lon + 180) * width / 360)
        y = int((90 - lat) * height / 180)
        
        # Apply zoom and centering
        center_x = width // 2
        center_y = height // 2
        
        x = int((x - width // 2) * self.zoom_level + center_x)
        y = int((y - height // 2) * self.zoom_level + center_y)
        
        return (x, y)
    
    def pixel_to_coordinate(self, x: int, y: int) -> tuple:
        """Convert pixel coordinates to geographic coordinates"""
        width = self.width()
        height = self.height()
        
        # Reverse the coordinate transformation
        center_x = width // 2
        center_y = height // 2
        
        x = int((x - center_x) / self.zoom_level + width // 2)
        y = int((y - center_y) / self.zoom_level + height // 2)
        
        lon = (x * 360 / width) - 180
        lat = 90 - (y * 180 / height)
        
        return (lat, lon)
    
    def paintEvent(self, event):
        """Paint the map canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(240, 248, 255))
        
        # Draw grid lines for reference
        self.draw_grid(painter)
        
        # Draw country boundaries (simplified)
        self.draw_boundaries(painter)
        
        # Draw user location if available
        if self.user_location:
            self.draw_user_location(painter)
        
        # Draw officials
        self.draw_officials(painter)
        
        # Draw activities
        self.draw_activities(painter)
        
        # Draw legend
        self.draw_legend(painter)
    
    def draw_grid(self, painter: QPainter):
        """Draw reference grid"""
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DotLine))
        
        width = self.width()
        height = self.height()
        
        # Vertical lines (longitude)
        for i in range(0, width, 50):
            painter.drawLine(i, 0, i, height)
        
        # Horizontal lines (latitude)
        for i in range(0, height, 50):
            painter.drawLine(0, i, width, i)
    
    def draw_boundaries(self, painter: QPainter):
        """Draw simplified country/state boundaries"""
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        
        # Simplified US boundary
        us_points = [
            self.coordinate_to_pixel(49, -125),   # NW
            self.coordinate_to_pixel(49, -66),    # NE
            self.coordinate_to_pixel(25, -66),    # SE
            self.coordinate_to_pixel(25, -125),   # SW
            self.coordinate_to_pixel(49, -125)    # Back to NW
        ]
        
        for i in range(len(us_points) - 1):
            painter.drawLine(us_points[i][0], us_points[i][1],
                           us_points[i+1][0], us_points[i+1][1])
        
        # Add labels
        painter.setPen(QPen(QColor(80, 80, 80)))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        
        us_center = self.coordinate_to_pixel(39.8283, -98.5795)
        painter.drawText(us_center[0] - 30, us_center[1], "UNITED STATES")
    
    def draw_user_location(self, painter: QPainter):
        """Draw user's current location"""
        if not self.user_location:
            return
        
        lat, lon = self.user_location
        x, y = self.coordinate_to_pixel(lat, lon)
        
        # Draw user location marker
        painter.setBrush(QBrush(QColor(255, 0, 255)))  # Magenta
        painter.setPen(QPen(QColor(128, 0, 128), 3))
        painter.drawEllipse(x - 8, y - 8, 16, 16)
        
        # Add label
        painter.setPen(QPen(QColor(128, 0, 128)))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(x + 12, y - 5, "Your Location")
    
    def draw_officials(self, painter: QPainter):
        """Draw government officials on map"""
        for official in self.officials:
            lat = official.get('lat', 0)
            lon = official.get('lon', 0)
            
            if lat == 0 and lon == 0:
                continue
            
            x, y = self.coordinate_to_pixel(lat, lon)
            
            # Skip if outside visible area
            if x < 0 or x > self.width() or y < 0 or y > self.height():
                continue
            
            official_type = official.get('type', 'other')
            color = self.official_colors.get(official_type, self.official_colors['other'])
            
            # Draw official marker
            size = self.get_marker_size(official_type)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawEllipse(x - size//2, y - size//2, size, size)
            
            # Highlight if selected
            if self.selected_official and self.selected_official.get('id') == official.get('id'):
                painter.setPen(QPen(QColor(255, 255, 0), 4))  # Yellow highlight
                painter.setBrush(QBrush(Qt.NoBrush))
                painter.drawEllipse(x - size//2 - 3, y - size//2 - 3, size + 6, size + 6)
            
            # Add name label for important officials
            if official_type in ['president', 'prime_minister', 'governor']:
                painter.setPen(QPen(QColor(0, 0, 0)))
                painter.setFont(QFont("Arial", 8, QFont.Bold))
                name = official.get('name', 'Unknown')
                painter.drawText(x + size//2 + 2, y - 2, name.split()[-1])  # Last name only
    
    def draw_activities(self, painter: QPainter):
        """Draw civic activities on map"""
        for activity in self.activities:
            lat = activity.get('lat', 0)
            lon = activity.get('lon', 0)
            
            if lat == 0 and lon == 0:
                continue
            
            x, y = self.coordinate_to_pixel(lat, lon)
            
            # Skip if outside visible area
            if x < 0 or x > self.width() or y < 0 or y > self.height():
                continue
            
            activity_type = activity.get('type', 'other')
            color = self.get_activity_color(activity_type)
            
            # Draw activity marker (square)
            size = 12
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawRect(x - size//2, y - size//2, size, size)
            
            # Add activity icon/label
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            icon = self.get_activity_icon(activity_type)
            painter.drawText(x - 3, y + 3, icon)
    
    def draw_legend(self, painter: QPainter):
        """Draw map legend"""
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        
        # Legend background
        legend_width = 200
        legend_height = 150
        legend_x = self.width() - legend_width - 10
        legend_y = 10
        
        painter.drawRect(legend_x, legend_y, legend_width, legend_height)
        
        # Legend title
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(legend_x + 5, legend_y + 15, "Map Legend")
        
        # Legend items
        y_offset = 30
        legend_items = [
            ("President/PM", self.official_colors['president']),
            ("Governor", self.official_colors['governor']),
            ("Mayor", self.official_colors['mayor']),
            ("Activities", QColor(255, 165, 0))
        ]
        
        painter.setFont(QFont("Arial", 9))
        for label, color in legend_items:
            painter.setBrush(QBrush(color))
            painter.drawEllipse(legend_x + 5, legend_y + y_offset - 5, 10, 10)
            painter.drawText(legend_x + 20, legend_y + y_offset + 3, label)
            y_offset += 20
    
    def get_marker_size(self, official_type: str) -> int:
        """Get marker size based on official importance"""
        size_map = {
            'president': 16,
            'prime_minister': 16,
            'vice_president': 14,
            'governor': 12,
            'mayor': 10,
            'senator': 8,
            'representative': 6,
            'other': 6
        }
        return size_map.get(official_type, 6)
    
    def get_activity_color(self, activity_type: str) -> QColor:
        """Get color for activity type"""
        color_map = {
            'election': QColor(255, 0, 0),      # Red
            'town_hall': QColor(0, 0, 255),     # Blue
            'debate': QColor(0, 255, 0),        # Green
            'legislation': QColor(128, 0, 128), # Purple
            'emergency': QColor(255, 165, 0)    # Orange
        }
        return color_map.get(activity_type, QColor(128, 128, 128))
    
    def get_activity_icon(self, activity_type: str) -> str:
        """Get icon character for activity type"""
        icon_map = {
            'election': 'E',
            'town_hall': 'T',
            'debate': 'D',
            'legislation': 'L',
            'emergency': '!'
        }
        return icon_map.get(activity_type, '?')
    
    def mousePressEvent(self, event):
        """Handle mouse clicks on map"""
        x = event.x()
        y = event.y()
        
        # Check if click is on an official
        for official in self.officials:
            official_x, official_y = self.coordinate_to_pixel(
                official.get('lat', 0), official.get('lon', 0)
            )
            
            # Check if click is within marker bounds
            size = self.get_marker_size(official.get('type', 'other'))
            if (abs(x - official_x) <= size//2 and abs(y - official_y) <= size//2):
                self.selected_official = official
                self.location_clicked.emit(official)
                self.update()
                return
        
        # Check if click is on an activity
        for activity in self.activities:
            activity_x, activity_y = self.coordinate_to_pixel(
                activity.get('lat', 0), activity.get('lon', 0)
            )
            
            # Check if click is within marker bounds
            if (abs(x - activity_x) <= 6 and abs(y - activity_y) <= 6):
                self.location_clicked.emit(activity)
                return


class BlockchainMapIntegration:
    """
    Blockchain integration for map activities and location tracking
    """
    
    def __init__(self):
        self.blockchain = None
        try:
            self.blockchain = Blockchain()
        except Exception as e:
            print(f"⚠️ Blockchain integration warning: {e}")
    
    def log_map_access(self, user_email: str, action: str, data: Dict[str, Any]) -> bool:
        """Log map access to blockchain"""
        if not self.blockchain:
            return False
        
        try:
            action_data = {
                'action_type': 'map_access',
                'user_action': action,
                'timestamp': datetime.now().isoformat(),
                'location_data': data.get('location', {}),
                'official_viewed': data.get('official_id', ''),
                'activity_viewed': data.get('activity_id', ''),
                'user_permissions': data.get('permissions', [])
            }
            
            success = self.blockchain.add_page(
                action_type="map_interaction",
                data=action_data,
                user_email=user_email
            )
            
            if success:
                print(f"✅ Map activity logged to blockchain: {action}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error logging map activity: {e}")
            return False
    
    def log_location_access(self, user_email: str, lat: float, lon: float, 
                          jurisdiction: str = "") -> bool:
        """Log user location access for privacy tracking"""
        if not self.blockchain:
            return False
        
        try:
            location_data = {
                'action_type': 'location_access',
                'latitude': lat,
                'longitude': lon,
                'jurisdiction': jurisdiction,
                'timestamp': datetime.now().isoformat(),
                'privacy_level': 'user_location_tracking'
            }
            
            return self.blockchain.add_page(
                action_type="location_tracking",
                data=location_data,
                user_email=user_email
            )
            
        except Exception as e:
            print(f"❌ Error logging location access: {e}")
            return False


class UserPermissionManager:
    """
    Manages user permissions for map data access
    """
    
    def __init__(self):
        self.session_manager = None
        try:
            self.session_manager = SessionManager()
        except Exception as e:
            print(f"⚠️ Session manager warning: {e}")
    
    def get_user_permissions(self) -> Dict[str, Any]:
        """Get current user's map access permissions"""
        if not self.session_manager or not self.session_manager.is_authenticated():
            return {
                'can_view_officials': False,
                'can_view_activities': False,
                'can_view_location_data': False,
                'jurisdiction_filter': [],
                'role_level': 'guest'
            }
        
        try:
            user = self.session_manager.get_current_user()
            if not user:
                return self.get_guest_permissions()
            
            user_role = user.get('role', 'Contract Citizen')
            
            # Role-based permissions
            if user_role in ['Contract Founder', 'Contract Elder']:
                return {
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_location_data': True,
                    'jurisdiction_filter': [],  # No restrictions
                    'role_level': 'administrative'
                }
            elif user_role in ['Contract Representative', 'Contract Senator']:
                return {
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_location_data': True,
                    'jurisdiction_filter': [user.get('jurisdiction', '')],
                    'role_level': 'government'
                }
            elif user_role == 'Contract Citizen':
                return {
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_location_data': False,
                    'jurisdiction_filter': [user.get('jurisdiction', ''), user.get('country', '')],
                    'role_level': 'citizen'
                }
            else:
                return self.get_guest_permissions()
                
        except Exception as e:
            print(f"❌ Error getting user permissions: {e}")
            return self.get_guest_permissions()
    
    def get_guest_permissions(self) -> Dict[str, Any]:
        """Get guest user permissions (limited access)"""
        return {
            'can_view_officials': True,
            'can_view_activities': False,
            'can_view_location_data': False,
            'jurisdiction_filter': ['United States'],  # Only US officials
            'role_level': 'guest'
        }
    
    def filter_officials_by_permission(self, officials: List[Dict], 
                                     permissions: Dict[str, Any]) -> List[Dict]:
        """Filter officials list based on user permissions"""
        if not permissions.get('can_view_officials', False):
            return []
        
        # No jurisdiction filter for admin roles
        if permissions.get('role_level') == 'administrative':
            return officials
        
        jurisdiction_filter = permissions.get('jurisdiction_filter', [])
        if not jurisdiction_filter:
            return officials
        
        # Filter by jurisdiction
        filtered_officials = []
        for official in officials:
            official_jurisdiction = official.get('jurisdiction', '')
            official_country = official.get('country', '')
            
            if (official_jurisdiction in jurisdiction_filter or 
                official_country in jurisdiction_filter):
                filtered_officials.append(official)
        
        return filtered_officials
    
    def filter_activities_by_permission(self, activities: List[Dict], 
                                      permissions: Dict[str, Any]) -> List[Dict]:
        """Filter activities list based on user permissions"""
        if not permissions.get('can_view_activities', False):
            return []
        
        # No jurisdiction filter for admin roles
        if permissions.get('role_level') == 'administrative':
            return activities
        
        # Citizens can only see public activities
        if permissions.get('role_level') == 'citizen':
            return [a for a in activities if a.get('visibility', 'public') == 'public']
        
        return activities


class NativeMapTab(QWidget):
    """
    Native desktop maps tab integrated with blockchain and user permissions
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize components
        self.blockchain_integration = BlockchainMapIntegration()
        self.permission_manager = UserPermissionManager()
        self.government_system = None
        
        try:
            self.government_system = GovernmentIntegrationSystem()
        except Exception as e:
            print(f"⚠️ Government system warning: {e}")
        
        # Data storage
        self.current_officials = []
        self.current_activities = []
        self.user_permissions = {}
        
        # UI setup
        self.setup_ui()
        self.load_user_permissions()
        self.load_initial_data()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def setup_ui(self):
        """Setup the native maps tab UI"""
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls and information
        left_panel = self.create_control_panel()
        left_panel.setMaximumWidth(300)
        left_panel.setMinimumWidth(250)
        
        # Right panel - Map canvas
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
        layout.setSpacing(10)
        
        # Title with user role
        self.title_label = QLabel("🗺️ Civic Maps")
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
                color: white;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(self.title_label)
        
        # User permissions display
        self.permissions_label = QLabel("Loading permissions...")
        self.permissions_label.setFont(QFont("Arial", 9))
        self.permissions_label.setStyleSheet("""
            QLabel {
                background: #e8f4fd;
                color: #2c5282;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #4a90e2;
            }
        """)
        layout.addWidget(self.permissions_label)
        
        # Search section
        search_group = self.create_search_section()
        layout.addWidget(search_group)
        
        # Filter controls
        filter_group = self.create_filter_controls()
        layout.addWidget(filter_group)
        
        # Statistics
        stats_group = self.create_statistics_section()
        layout.addWidget(stats_group)
        
        # Selected item info
        info_group = self.create_info_section()
        layout.addWidget(info_group)
        
        # Action buttons
        buttons_layout = self.create_action_buttons()
        layout.addLayout(buttons_layout)
        
        layout.addStretch()  # Push everything to top
        
        return panel
    
    def create_search_section(self) -> QGroupBox:
        """Create search functionality section"""
        
        group = QGroupBox("🔍 Search")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(group)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search officials, locations...")
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        layout.addWidget(self.search_input)
        
        # Search button
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self.perform_search)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        layout.addWidget(search_btn)
        
        return group
    
    def create_filter_controls(self) -> QGroupBox:
        """Create filter controls section"""
        
        group = QGroupBox("🎛️ Filters")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(group)
        
        # Official types filter
        self.show_officials = QCheckBox("👥 Government Officials")
        self.show_officials.setChecked(True)
        self.show_officials.stateChanged.connect(self.update_map_display)
        layout.addWidget(self.show_officials)
        
        self.show_activities = QCheckBox("📊 Civic Activities")
        self.show_activities.setChecked(True)
        self.show_activities.stateChanged.connect(self.update_map_display)
        layout.addWidget(self.show_activities)
        
        self.show_user_location = QCheckBox("📍 My Location")
        self.show_user_location.setChecked(False)
        self.show_user_location.stateChanged.connect(self.toggle_user_location)
        layout.addWidget(self.show_user_location)
        
        # Jurisdiction filter
        jurisdiction_label = QLabel("Jurisdiction:")
        jurisdiction_label.setFont(QFont("Arial", 9))
        layout.addWidget(jurisdiction_label)
        
        self.jurisdiction_combo = QComboBox()
        self.jurisdiction_combo.addItems(["All Available", "United States", "Local Only"])
        self.jurisdiction_combo.currentTextChanged.connect(self.update_map_display)
        self.jurisdiction_combo.setStyleSheet("""
            QComboBox {
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.jurisdiction_combo)
        
        return group
    
    def create_statistics_section(self) -> QGroupBox:
        """Create statistics display section"""
        
        group = QGroupBox("📈 Statistics")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(group)
        
        # Statistics display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(80)
        self.stats_text.setPlainText("Loading statistics...")
        self.stats_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px;
                font-size: 10px;
                background: #f9f9f9;
            }
        """)
        layout.addWidget(self.stats_text)
        
        return group
    
    def create_info_section(self) -> QGroupBox:
        """Create information display section"""
        
        group = QGroupBox("ℹ️ Selection Info")
        group.setFont(QFont("Arial", 10, QFont.Bold))
        layout = QVBoxLayout(group)
        
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setMaximumHeight(120)
        self.info_display.setPlainText("Click on map markers to view details")
        self.info_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px;
                font-size: 10px;
                background: #fafafa;
            }
        """)
        layout.addWidget(self.info_display)
        
        return group
    
    def create_action_buttons(self) -> QVBoxLayout:
        """Create action buttons"""
        
        layout = QVBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        # Blockchain log button
        blockchain_btn = QPushButton("⛓️ View Activity Log")
        blockchain_btn.clicked.connect(self.show_blockchain_log)
        blockchain_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        
        layout.addWidget(refresh_btn)
        layout.addWidget(blockchain_btn)
        
        return layout
    
    def create_map_panel(self) -> QWidget:
        """Create the main map display panel"""
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Map header
        header = QLabel("Interactive Civic Engagement Map - Desktop Native")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                padding: 8px;
                border-bottom: 2px solid #4a90e2;
                color: #333;
            }
        """)
        layout.addWidget(header)
        
        # Native map canvas
        self.map_canvas = MapCanvas()
        self.map_canvas.location_clicked.connect(self.on_location_clicked)
        layout.addWidget(self.map_canvas)
        
        return panel
    
    def load_user_permissions(self):
        """Load current user permissions and update UI"""
        
        self.user_permissions = self.permission_manager.get_user_permissions()
        
        # Update permissions display
        role_level = self.user_permissions.get('role_level', 'guest')
        can_view_officials = self.user_permissions.get('can_view_officials', False)
        can_view_activities = self.user_permissions.get('can_view_activities', False)
        
        permissions_text = f"Role: {role_level.title()}\n"
        permissions_text += f"Officials: {'✅' if can_view_officials else '❌'} "
        permissions_text += f"Activities: {'✅' if can_view_activities else '❌'}"
        
        self.permissions_label.setText(permissions_text)
        
        # Update title with role
        self.title_label.setText(f"🗺️ Civic Maps ({role_level.title()})")
        
        # Log permission check to blockchain
        if hasattr(self, 'blockchain_integration'):
            try:
                user_email = ""
                if hasattr(self, 'session_manager') and self.session_manager:
                    user = self.session_manager.get_current_user()
                    if user:
                        user_email = user.get('email', '')
                
                self.blockchain_integration.log_map_access(
                    user_email=user_email,
                    action="permissions_loaded",
                    data={'permissions': self.user_permissions}
                )
            except Exception as e:
                print(f"⚠️ Error logging permissions: {e}")
    
    def load_initial_data(self):
        """Load initial map data based on user permissions"""
        
        try:
            # Load government officials
            if self.government_system and self.user_permissions.get('can_view_officials', False):
                all_officials = self.load_officials_data()
                self.current_officials = self.permission_manager.filter_officials_by_permission(
                    all_officials, self.user_permissions
                )
            else:
                self.current_officials = []
            
            # Load civic activities
            if self.user_permissions.get('can_view_activities', False):
                all_activities = self.load_activities_data()
                self.current_activities = self.permission_manager.filter_activities_by_permission(
                    all_activities, self.user_permissions
                )
            else:
                self.current_activities = []
            
            # Update map display
            self.update_map_display()
            self.update_statistics()
            
        except Exception as e:
            print(f"❌ Error loading initial data: {e}")
            self.show_error_message(f"Error loading map data: {str(e)}")
    
    def load_officials_data(self) -> List[Dict]:
        """Load government officials data"""
        
        try:
            if self.government_system:
                # Get officials from government system
                officials_data = self.government_system.get_all_officials()
                
                # Convert to map format with coordinates
                map_officials = []
                
                for official_id, official in officials_data.items():
                    lat, lon = self.get_official_coordinates(official)
                    
                    if lat != 0 or lon != 0:  # Only include officials with valid coordinates
                        map_official = {
                            'id': official_id,
                            'name': official.get('name', 'Unknown'),
                            'title': official.get('title', 'Unknown Title'),
                            'lat': lat,
                            'lon': lon,
                            'type': self.determine_official_type(official.get('title', '')),
                            'party': official.get('party_affiliation', 'Independent'),
                            'contact': official.get('email', 'N/A'),
                            'phone': official.get('phone', 'N/A'),
                            'jurisdiction': official.get('jurisdiction', 'Unknown'),
                            'country': official.get('country', 'Unknown'),
                            'verification_status': official.get('verification_status', 'uncontacted')
                        }
                        map_officials.append(map_official)
                
                return map_officials
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error loading officials data: {e}")
            return []
    
    def load_activities_data(self) -> List[Dict]:
        """Load civic activities data"""
        
        # Sample activities - in production, integrate with Events module
        activities = [
            {
                'id': 'presidential_town_hall',
                'title': 'Presidential Town Hall',
                'type': 'town_hall',
                'lat': 38.9072,
                'lon': -77.0369,
                'date': '2025-10-15',
                'status': 'scheduled',
                'visibility': 'public'
            },
            {
                'id': 'local_election',
                'title': 'Local Elections',
                'type': 'election',
                'lat': 40.7128,
                'lon': -74.0060,
                'date': '2025-11-05',
                'status': 'upcoming',
                'visibility': 'public'
            }
        ]
        
        return activities
    
    def get_official_coordinates(self, official: Dict[str, Any]) -> tuple:
        """Get coordinates for government officials"""
        
        # Coordinate mapping for major government centers
        location_coords = {
            # United States
            "United States": (38.9072, -77.0369),  # Washington DC
            "California": (38.5816, -121.4944),    # Sacramento
            "Texas": (30.2672, -97.7431),          # Austin
            "Florida": (30.4518, -84.27277),       # Tallahassee
            "New York": (42.6526, -73.7562),       # Albany
            "New York City": (40.7128, -74.0060),  # NYC
            
            # International
            "United Kingdom": (51.5074, -0.1278),  # London
            "Germany": (52.5200, 13.4050),         # Berlin
            "France": (48.8566, 2.3522),           # Paris
            "Japan": (35.6762, 139.6503),          # Tokyo
            "Canada": (45.4215, -75.6972),         # Ottawa
            "Italy": (41.9028, 12.4964),           # Rome
        }
        
        # Try to get coordinates based on jurisdiction or country
        jurisdiction = official.get('jurisdiction', '')
        country = official.get('country', '')
        
        if jurisdiction in location_coords:
            return location_coords[jurisdiction]
        elif country in location_coords:
            return location_coords[country]
        else:
            # Default coordinates (center of USA)
            return (39.8283, -98.5795)
    
    def determine_official_type(self, title: str) -> str:
        """Determine official type from title"""
        
        title_lower = title.lower()
        
        if 'president' in title_lower:
            return 'president'
        elif 'prime minister' in title_lower:
            return 'prime_minister'
        elif 'vice president' in title_lower:
            return 'vice_president'
        elif 'governor' in title_lower:
            return 'governor'
        elif 'mayor' in title_lower:
            return 'mayor'
        elif 'senator' in title_lower:
            return 'senator'
        elif 'representative' in title_lower:
            return 'representative'
        else:
            return 'other'
    
    def update_map_display(self):
        """Update map canvas with current data and filters"""
        
        # Apply filters
        officials_to_show = []
        activities_to_show = []
        
        if self.show_officials.isChecked():
            officials_to_show = self.current_officials
        
        if self.show_activities.isChecked():
            activities_to_show = self.current_activities
        
        # Apply jurisdiction filter
        jurisdiction_filter = self.jurisdiction_combo.currentText()
        if jurisdiction_filter != "All Available":
            if jurisdiction_filter == "Local Only":
                # Filter by user's jurisdiction
                user_jurisdiction = self.user_permissions.get('jurisdiction_filter', [])
                officials_to_show = [
                    o for o in officials_to_show 
                    if o.get('jurisdiction') in user_jurisdiction or o.get('country') in user_jurisdiction
                ]
            elif jurisdiction_filter == "United States":
                officials_to_show = [
                    o for o in officials_to_show 
                    if o.get('country') == 'United States'
                ]
        
        # Update map canvas
        self.map_canvas.set_officials_data(officials_to_show)
        self.map_canvas.set_activities_data(activities_to_show)
    
    def update_statistics(self):
        """Update statistics display"""
        
        stats_text = f"Officials Visible: {len(self.current_officials)}\n"
        stats_text += f"Activities: {len(self.current_activities)}\n"
        stats_text += f"Permission Level: {self.user_permissions.get('role_level', 'guest').title()}\n"
        
        if self.user_permissions.get('jurisdiction_filter'):
            jurisdictions = ", ".join(self.user_permissions['jurisdiction_filter'])
            stats_text += f"Jurisdictions: {jurisdictions}"
        
        self.stats_text.setPlainText(stats_text)
    
    def perform_search(self):
        """Perform search functionality"""
        
        query = self.search_input.text().strip().lower()
        if not query:
            return
        
        # Search through officials
        found_officials = []
        for official in self.current_officials:
            if (query in official.get('name', '').lower() or
                query in official.get('title', '').lower() or
                query in official.get('jurisdiction', '').lower()):
                found_officials.append(official)
        
        # Update info display with search results
        if found_officials:
            result_text = f"Search Results for '{query}':\n\n"
            for official in found_officials[:3]:  # Show first 3 results
                result_text += f"• {official.get('name')} - {official.get('title')}\n"
            
            if len(found_officials) > 3:
                result_text += f"... and {len(found_officials) - 3} more results"
            
            self.info_display.setPlainText(result_text)
            
            # Highlight first result on map
            if found_officials:
                self.map_canvas.selected_official = found_officials[0]
                self.map_canvas.update()
        else:
            self.info_display.setPlainText(f"No results found for '{query}'")
        
        # Log search to blockchain
        try:
            user_email = ""
            if hasattr(self, 'session_manager') and self.session_manager:
                user = self.session_manager.get_current_user()
                if user:
                    user_email = user.get('email', '')
            
            self.blockchain_integration.log_map_access(
                user_email=user_email,
                action="search_performed",
                data={'search_query': query, 'results_count': len(found_officials)}
            )
        except Exception as e:
            print(f"⚠️ Error logging search: {e}")
    
    def toggle_user_location(self, checked: bool):
        """Toggle user location display"""
        
        if checked and self.user_permissions.get('can_view_location_data', False):
            # Set default user location (in production, get from GPS or user input)
            self.map_canvas.set_user_location(39.8283, -98.5795)
            
            # Log location access
            try:
                user_email = ""
                if hasattr(self, 'session_manager') and self.session_manager:
                    user = self.session_manager.get_current_user()
                    if user:
                        user_email = user.get('email', '')
                
                self.blockchain_integration.log_location_access(
                    user_email=user_email,
                    lat=39.8283,
                    lon=-98.5795,
                    jurisdiction="United States"
                )
            except Exception as e:
                print(f"⚠️ Error logging location access: {e}")
        else:
            self.map_canvas.set_user_location(0, 0)  # Remove user location
            
            if checked and not self.user_permissions.get('can_view_location_data', False):
                self.show_error_message("You don't have permission to view location data")
                self.show_user_location.setChecked(False)
    
    def on_location_clicked(self, item_data: Dict):
        """Handle location clicks on map"""
        
        # Display item information
        if 'title' in item_data:  # Official
            info_text = f"Official: {item_data.get('name', 'Unknown')}\n"
            info_text += f"Title: {item_data.get('title', 'Unknown')}\n"
            info_text += f"Party: {item_data.get('party', 'Unknown')}\n"
            info_text += f"Contact: {item_data.get('contact', 'N/A')}\n"
            info_text += f"Phone: {item_data.get('phone', 'N/A')}\n"
            info_text += f"Jurisdiction: {item_data.get('jurisdiction', 'Unknown')}"
        else:  # Activity
            info_text = f"Activity: {item_data.get('title', 'Unknown')}\n"
            info_text += f"Type: {item_data.get('type', 'Unknown')}\n"
            info_text += f"Date: {item_data.get('date', 'Unknown')}\n"
            info_text += f"Status: {item_data.get('status', 'Unknown')}"
        
        self.info_display.setPlainText(info_text)
        
        # Log interaction to blockchain
        try:
            user_email = ""
            if hasattr(self, 'session_manager') and self.session_manager:
                user = self.session_manager.get_current_user()
                if user:
                    user_email = user.get('email', '')
            
            self.blockchain_integration.log_map_access(
                user_email=user_email,
                action="location_clicked",
                data={
                    'official_id': item_data.get('id', ''),
                    'activity_id': item_data.get('id', ''),
                    'item_type': 'official' if 'title' in item_data else 'activity'
                }
            )
        except Exception as e:
            print(f"⚠️ Error logging location click: {e}")
    
    def refresh_data(self):
        """Refresh map data and permissions"""
        
        try:
            # Reload permissions (user role might have changed)
            self.load_user_permissions()
            
            # Reload data
            self.load_initial_data()
            
            self.info_display.setPlainText("✅ Data refreshed successfully")
            
        except Exception as e:
            self.show_error_message(f"Error refreshing data: {str(e)}")
    
    def show_blockchain_log(self):
        """Show blockchain activity log"""
        
        try:
            # Create simple dialog showing recent blockchain activities
            msg = QMessageBox()
            msg.setWindowTitle("⛓️ Blockchain Activity Log")
            msg.setText("Recent map activities logged to blockchain:")
            
            # In production, fetch actual blockchain entries
            log_text = "• Map access logged\n"
            log_text += "• Location click recorded\n"
            log_text += "• Search query logged\n"
            log_text += "• Permission check recorded\n"
            log_text += "\nAll activities are permanently recorded for transparency and auditing."
            
            msg.setDetailedText(log_text)
            msg.exec_()
            
        except Exception as e:
            self.show_error_message(f"Error accessing blockchain log: {str(e)}")
    
    def show_error_message(self, message: str):
        """Display error message"""
        
        self.info_display.setPlainText(f"❌ Error: {message}")
        print(f"❌ Map Tab Error: {message}")


# Test function for standalone execution
def test_native_map_tab():
    """Test the native map tab as standalone widget"""
    
    app = QApplication(sys.argv)
    
    # Create and show the native map tab
    map_tab = NativeMapTab()
    map_tab.setWindowTitle("🗺️ Civic Engagement Native Map")
    map_tab.resize(1200, 800)
    map_tab.show()
    
    print("🗺️ Native Map Tab Test Running...")
    print("📍 Features:")
    print("   • Native desktop map canvas")
    print("   • Blockchain integration")
    print("   • User permission restrictions")
    print("   • Role-based data filtering")
    print("   • Real-time government data")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_native_map_tab()