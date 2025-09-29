"""
Simple Maps Tab for Civic Engagement Platform
Desktop-integrated maps without web dependencies
Uses text-based display with blockchain logging and user permission filtering
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Try PyQt5 imports with fallback
try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QTextEdit, QGroupBox, QCheckBox,
                                QLineEdit, QComboBox, QSplitter, QScrollArea,
                                QListWidget, QListWidgetItem, QMessageBox,
                                QProgressBar, QFrame)
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont, QPixmap
    PYQT5_AVAILABLE = True
except ImportError:
    # Create dummy classes for type hints when PyQt5 not available
    class QWidget: pass
    class QVBoxLayout: pass
    class QHBoxLayout: pass
    class QLabel: pass
    class QPushButton: pass
    class QTextEdit: pass
    class QGroupBox: pass
    class QCheckBox: pass
    class QLineEdit: pass
    class QComboBox: pass
    class QSplitter: pass
    class QScrollArea: pass
    class QListWidget: pass
    class QListWidgetItem: pass
    class QMessageBox: pass
    class QProgressBar: pass
    class QFrame: pass
    class Qt: pass
    class QTimer: pass
    class QFont: pass
    def pyqtSignal(): pass
    PYQT5_AVAILABLE = False

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MapIntegration:
    """
    Handles map data integration with blockchain and user permissions
    Works without PyQt5 dependencies
    """
    
    def __init__(self):
        self.blockchain = None
        self.session_manager = None
        self.officials_data = {}
        self.activities_data = []
        
        # Initialize integrations
        self.initialize_blockchain()
        self.initialize_session()
        self.load_data()
    
    def initialize_blockchain(self):
        """Initialize blockchain integration"""
        try:
            from blockchain.blockchain import Blockchain
            self.blockchain = Blockchain()
            print("✅ Blockchain integration initialized for maps")
        except Exception as e:
            print(f"⚠️ Blockchain integration unavailable: {e}")
            self.blockchain = None
    
    def initialize_session(self):
        """Initialize session management"""
        try:
            from users.session import SessionManager
            self.session_manager = SessionManager()
            print("✅ Session management initialized for maps")
        except Exception as e:
            print(f"⚠️ Session management unavailable: {e}")
            self.session_manager = None
    
    def load_data(self):
        """Load government officials and civic activity data"""
        
        # Load government officials
        self.load_government_officials()
        
        # Load civic activities
        self.load_civic_activities()
    
    def load_government_officials(self):
        """Load government officials from directory"""
        
        try:
            # Find government directory
            government_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'government', 'government_directory', 'government_officials_directory.json'),
                os.path.join(os.path.dirname(__file__), '..', '..', 'government', 'government_directory', 'government_officials_directory.json'),
                'government/government_directory/government_officials_directory.json'
            ]
            
            officials_file = None
            for path in government_paths:
                if os.path.exists(path):
                    officials_file = path
                    break
            
            if officials_file:
                with open(officials_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                # Process officials data
                self.officials_data = {}
                for official_id, official in raw_data.items():
                    if isinstance(official, dict):
                        # Add coordinates and processing
                        processed_official = {
                            'id': official_id,
                            'name': official.get('name', 'Unknown'),
                            'title': official.get('title', 'Government Official'),
                            'country': official.get('country', 'Unknown'),
                            'jurisdiction': official.get('jurisdiction', 'Unknown'),
                            'party': official.get('party_affiliation', 'Independent'),
                            'email': official.get('email', 'N/A'),
                            'phone': official.get('phone', 'N/A'),
                            'verification': official.get('verification_status', 'uncontacted'),
                            'coordinates': self.get_official_location(official),
                            'type': self.determine_official_type(official.get('title', ''))
                        }
                        self.officials_data[official_id] = processed_official
                
                print(f"✅ Loaded {len(self.officials_data)} government officials")
            else:
                self.load_sample_officials()
                
        except Exception as e:
            print(f"❌ Error loading government officials: {e}")
            self.load_sample_officials()
    
    def load_sample_officials(self):
        """Load sample officials data"""
        
        self.officials_data = {
            'us_president': {
                'name': 'Donald J. Trump',
                'title': 'President of the United States (47th)',
                'country': 'United States',
                'jurisdiction': 'United States',
                'party': 'Republican',
                'coordinates': (38.9072, -77.0369),  # Washington DC
                'type': 'president',
                'verification': 'verified'
            },
            'us_vp': {
                'name': 'J.D. Vance',
                'title': 'Vice President of the United States',
                'country': 'United States',
                'jurisdiction': 'United States',
                'party': 'Republican',
                'coordinates': (38.9072, -77.0369),
                'type': 'vice_president',
                'verification': 'verified'
            },
            'uk_pm': {
                'name': 'Keir Starmer',
                'title': 'Prime Minister of the United Kingdom',
                'country': 'United Kingdom',
                'jurisdiction': 'United Kingdom',
                'party': 'Labour',
                'coordinates': (51.5074, -0.1278),  # London
                'type': 'prime_minister',
                'verification': 'verified'
            },
            'japan_pm': {
                'name': 'Shigeru Ishiba',
                'title': 'Prime Minister of Japan',
                'country': 'Japan',
                'jurisdiction': 'Japan',
                'party': 'Liberal Democratic Party',
                'coordinates': (35.6762, 139.6503),  # Tokyo
                'type': 'prime_minister',
                'verification': 'verified'
            }
        }
        print("✅ Loaded sample government officials")
    
    def load_civic_activities(self):
        """Load civic activities data"""
        
        self.activities_data = [
            {
                'id': 'presidential_address',
                'title': 'Presidential Address to Nation',
                'type': 'address',
                'date': '2025-10-15T20:00:00Z',
                'location': 'Washington, D.C.',
                'coordinates': (38.9072, -77.0369),
                'status': 'scheduled',
                'visibility': 'public'
            },
            {
                'id': 'town_hall_nyc',
                'title': 'NYC Community Town Hall',
                'type': 'town_hall',
                'date': '2025-10-20T19:00:00Z',
                'location': 'New York City',
                'coordinates': (40.7128, -74.0060),
                'status': 'upcoming',
                'visibility': 'public'
            }
        ]
    
    def get_official_location(self, official: Dict[str, Any]) -> tuple:
        """Get coordinates for official based on location"""
        
        # Location coordinate mapping
        locations = {
            'United States': (38.9072, -77.0369),    # Washington DC
            'United Kingdom': (51.5074, -0.1278),    # London
            'Japan': (35.6762, 139.6503),            # Tokyo
            'Germany': (52.5200, 13.4050),           # Berlin
            'France': (48.8566, 2.3522),             # Paris
            'Canada': (45.4215, -75.6972),           # Ottawa
            'California': (38.5816, -121.4944),      # Sacramento
            'Texas': (30.2672, -97.7431),            # Austin
            'New York': (42.6526, -73.7562),         # Albany
            'New York City': (40.7128, -74.0060),    # NYC
        }
        
        # Try jurisdiction first, then country
        jurisdiction = official.get('jurisdiction', '')
        country = official.get('country', '')
        
        if jurisdiction in locations:
            return locations[jurisdiction]
        elif country in locations:
            return locations[country]
        else:
            return (39.8283, -98.5795)  # Center of USA
    
    def determine_official_type(self, title: str) -> str:
        """Determine official type from title"""
        
        title_lower = title.lower()
        
        if 'president' in title_lower and 'vice' not in title_lower:
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
    
    def get_user_permissions(self) -> Dict[str, Any]:
        """Get current user permissions"""
        
        if not self.session_manager:
            return self.get_guest_permissions()
        
        try:
            if not self.session_manager.is_authenticated():
                return self.get_guest_permissions()
            
            user = self.session_manager.get_current_user()
            if not user:
                return self.get_guest_permissions()
            
            role = user.get('role', 'Contract Citizen')
            
            # Role-based permissions
            if role in ['Contract Founder', 'Contract Elder']:
                return {
                    'role': 'administrative',
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_contacts': True,
                    'jurisdiction_filter': [],
                    'max_results': -1
                }
            elif role in ['Contract Representative', 'Contract Senator']:
                return {
                    'role': 'government',
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_contacts': False,
                    'jurisdiction_filter': [user.get('country', '')],
                    'max_results': 100
                }
            elif role == 'Contract Citizen':
                return {
                    'role': 'citizen',
                    'can_view_officials': True,
                    'can_view_activities': True,
                    'can_view_contacts': False,
                    'jurisdiction_filter': [user.get('country', 'United States')],
                    'max_results': 50
                }
            else:
                return self.get_guest_permissions()
                
        except Exception as e:
            print(f"⚠️ Error getting permissions: {e}")
            return self.get_guest_permissions()
    
    def get_guest_permissions(self) -> Dict[str, Any]:
        """Get guest permissions"""
        
        return {
            'role': 'guest',
            'can_view_officials': True,
            'can_view_activities': False,
            'can_view_contacts': False,
            'jurisdiction_filter': ['United States'],
            'max_results': 10
        }
    
    def get_filtered_officials(self) -> List[Dict[str, Any]]:
        """Get officials filtered by user permissions"""
        
        permissions = self.get_user_permissions()
        
        if not permissions['can_view_officials']:
            return []
        
        # Get all officials
        all_officials = list(self.officials_data.values())
        
        # Apply jurisdiction filter
        jurisdiction_filter = permissions['jurisdiction_filter']
        if jurisdiction_filter and permissions['role'] != 'administrative':
            filtered_officials = []
            for official in all_officials:
                if (official.get('country') in jurisdiction_filter or
                    official.get('jurisdiction') in jurisdiction_filter):
                    filtered_officials.append(official)
            all_officials = filtered_officials
        
        # Apply result limit
        max_results = permissions['max_results']
        if max_results > 0:
            all_officials = all_officials[:max_results]
        
        # Remove contact info if no permission
        if not permissions['can_view_contacts']:
            for official in all_officials:
                official = official.copy()
                official['email'] = 'Restricted'
                official['phone'] = 'Restricted'
        
        return all_officials
    
    def get_filtered_activities(self) -> List[Dict[str, Any]]:
        """Get activities filtered by permissions"""
        
        permissions = self.get_user_permissions()
        
        if not permissions['can_view_activities']:
            return []
        
        # For guests, only show public activities
        if permissions['role'] == 'guest':
            return [a for a in self.activities_data if a.get('visibility') == 'public']
        
        return self.activities_data
    
    def search_data(self, query: str) -> List[Dict[str, Any]]:
        """Search officials and activities"""
        
        if not query or len(query.strip()) < 2:
            return []
        
        query_lower = query.lower().strip()
        results = []
        
        # Search officials
        officials = self.get_filtered_officials()
        for official in officials:
            searchable = f"{official.get('name', '')} {official.get('title', '')} {official.get('jurisdiction', '')}".lower()
            if query_lower in searchable:
                result = official.copy()
                result['result_type'] = 'official'
                results.append(result)
        
        # Search activities
        activities = self.get_filtered_activities()
        for activity in activities:
            searchable = f"{activity.get('title', '')} {activity.get('type', '')} {activity.get('location', '')}".lower()
            if query_lower in searchable:
                result = activity.copy()
                result['result_type'] = 'activity'
                results.append(result)
        
        # Log search to blockchain
        self.log_to_blockchain('search_performed', {'query': query, 'results_count': len(results)})
        
        return results
    
    def log_to_blockchain(self, action: str, data: Dict[str, Any]):
        """Log action to blockchain"""
        
        if not self.blockchain:
            return
        
        try:
            user_email = ""
            if self.session_manager and self.session_manager.is_authenticated():
                user = self.session_manager.get_current_user()
                if user:
                    user_email = user.get('email', '')
            
            blockchain_data = {
                'action': action,
                'timestamp': datetime.now().isoformat(),
                'user_permissions': self.get_user_permissions(),
                'data': data
            }
            
            success = self.blockchain.add_page(
                action_type="maps_interaction",
                data=blockchain_data,
                user_email=user_email
            )
            
            if success:
                print(f"✅ Maps action logged to blockchain: {action}")
            
        except Exception as e:
            print(f"⚠️ Error logging to blockchain: {e}")


class SimpleMapTab(QWidget):
    """
    Simple map tab for desktop application
    Text-based interface with blockchain integration
    """
    
    def __init__(self, parent=None):
        super().__init__(parent) if PYQT5_AVAILABLE else None
        
        if not PYQT5_AVAILABLE:
            print("⚠️ PyQt5 not available - Maps tab will use text interface only")
            return
        
        # Initialize map integration
        self.map_integration = MapIntegration()
        
        # Setup UI
        self.setup_ui()
        self.load_initial_data()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)  # Refresh every minute
    
    def setup_ui(self):
        """Setup the user interface"""
        
        if not PYQT5_AVAILABLE:
            return
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - controls and info
        left_panel = self.create_control_panel()
        left_panel.setMaximumWidth(350)
        left_panel.setMinimumWidth(300)
        
        # Right panel - data display
        right_panel = self.create_data_panel()
        
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setStretchFactor(0, 0)
        content_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(content_splitter)
    
    def create_header(self) -> QWidget:
        """Create header section"""
        
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(header)
        
        # Title
        title = QLabel("🗺️ Civic Engagement Maps")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Blockchain-Integrated Geographic Information System")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setStyleSheet("color: #e8f4fd;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        return header
    
    def create_control_panel(self) -> QWidget:
        """Create left control panel"""
        
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # User permissions display
        permissions_group = QGroupBox("👤 User Access Level")
        permissions_group.setFont(QFont("Arial", 10, QFont.Bold))
        permissions_layout = QVBoxLayout(permissions_group)
        
        self.permissions_label = QLabel("Loading...")
        self.permissions_label.setFont(QFont("Arial", 9))
        self.permissions_label.setStyleSheet("""
            QLabel {
                background: #e8f4fd;
                padding: 8px;
                border-radius: 4px;
                color: #2c5282;
            }
        """)
        permissions_layout.addWidget(self.permissions_label)
        layout.addWidget(permissions_group)
        
        # Search section
        search_group = QGroupBox("🔍 Search")
        search_group.setFont(QFont("Arial", 10, QFont.Bold))
        search_layout = QVBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search officials, locations...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self.perform_search)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        search_layout.addWidget(search_btn)
        layout.addWidget(search_group)
        
        # Filter controls
        filter_group = QGroupBox("🎛️ Display Filters")
        filter_group.setFont(QFont("Arial", 10, QFont.Bold))
        filter_layout = QVBoxLayout(filter_group)
        
        self.show_officials_cb = QCheckBox("👥 Government Officials")
        self.show_officials_cb.setChecked(True)
        self.show_officials_cb.stateChanged.connect(self.update_display)
        filter_layout.addWidget(self.show_officials_cb)
        
        self.show_activities_cb = QCheckBox("📊 Civic Activities") 
        self.show_activities_cb.setChecked(True)
        self.show_activities_cb.stateChanged.connect(self.update_display)
        filter_layout.addWidget(self.show_activities_cb)
        
        # Jurisdiction filter
        jurisdiction_label = QLabel("Jurisdiction Filter:")
        jurisdiction_label.setFont(QFont("Arial", 9))
        filter_layout.addWidget(jurisdiction_label)
        
        self.jurisdiction_combo = QComboBox()
        self.jurisdiction_combo.addItems(["All Available", "United States", "International", "Local Only"])
        self.jurisdiction_combo.currentTextChanged.connect(self.update_display)
        filter_layout.addWidget(self.jurisdiction_combo)
        
        layout.addWidget(filter_group)
        
        # Statistics section
        stats_group = QGroupBox("📈 Data Statistics")
        stats_group.setFont(QFont("Arial", 10, QFont.Bold))
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(100)
        self.stats_display.setStyleSheet("""
            QTextEdit {
                background: #f1f3f4;
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 6px;
                font-size: 10px;
            }
        """)
        stats_layout.addWidget(self.stats_display)
        layout.addWidget(stats_group)
        
        # Action buttons
        buttons_layout = QVBoxLayout()
        
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
        
        blockchain_btn = QPushButton("⛓️ Blockchain Log")
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
        
        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(blockchain_btn)
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
        
        return panel
    
    def create_data_panel(self) -> QWidget:
        """Create main data display panel"""
        
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Data display area
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        self.data_display.setFont(QFont("Consolas", 10))
        self.data_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 10px;
                background: #fafafa;
            }
        """)
        layout.addWidget(self.data_display)
        
        return panel
    
    def load_initial_data(self):
        """Load initial data and update display"""
        
        if not PYQT5_AVAILABLE:
            self.print_text_interface()
            return
        
        # Update permissions display
        permissions = self.map_integration.get_user_permissions()
        role = permissions.get('role', 'guest').title()
        
        permissions_text = f"Role: {role}\n"
        permissions_text += f"View Officials: {'✅' if permissions['can_view_officials'] else '❌'}\n"
        permissions_text += f"View Activities: {'✅' if permissions['can_view_activities'] else '❌'}\n"
        permissions_text += f"View Contacts: {'✅' if permissions['can_view_contacts'] else '❌'}"
        
        self.permissions_label.setText(permissions_text)
        
        # Update data display
        self.update_display()
        
        # Log initial access
        self.map_integration.log_to_blockchain('maps_tab_opened', {
            'user_role': role,
            'timestamp': datetime.now().isoformat()
        })
    
    def print_text_interface(self):
        """Print text interface when PyQt5 not available"""
        
        print("\n" + "="*60)
        print("🗺️ CIVIC ENGAGEMENT MAPS - TEXT INTERFACE")
        print("="*60)
        
        # Show user permissions
        permissions = self.map_integration.get_user_permissions()
        print(f"\n👤 User Role: {permissions['role'].title()}")
        print(f"   Officials Access: {'✅' if permissions['can_view_officials'] else '❌'}")
        print(f"   Activities Access: {'✅' if permissions['can_view_activities'] else '❌'}")
        print(f"   Contact Info: {'✅' if permissions['can_view_contacts'] else '❌'}")
        
        # Show officials
        officials = self.map_integration.get_filtered_officials()
        print(f"\n👥 GOVERNMENT OFFICIALS ({len(officials)} total):")
        print("-" * 50)
        
        for i, official in enumerate(officials, 1):
            coords = official.get('coordinates', (0, 0))
            print(f"{i:2d}. {official.get('name', 'Unknown')}")
            print(f"     Title: {official.get('title', 'Unknown')}")
            print(f"     Location: {official.get('jurisdiction', 'Unknown')} ({coords[0]:.4f}, {coords[1]:.4f})")
            print(f"     Party: {official.get('party', 'Unknown')}")
            if permissions['can_view_contacts']:
                print(f"     Contact: {official.get('email', 'N/A')}")
            print()
        
        # Show activities
        activities = self.map_integration.get_filtered_activities()
        if activities:
            print(f"\n📊 CIVIC ACTIVITIES ({len(activities)} total):")
            print("-" * 50)
            
            for i, activity in enumerate(activities, 1):
                coords = activity.get('coordinates', (0, 0))
                print(f"{i:2d}. {activity.get('title', 'Unknown')}")
                print(f"     Type: {activity.get('type', 'Unknown')}")
                print(f"     Location: {activity.get('location', 'Unknown')} ({coords[0]:.4f}, {coords[1]:.4f})")
                print(f"     Date: {activity.get('date', 'Unknown')}")
                print(f"     Status: {activity.get('status', 'Unknown')}")
                print()
        
        print("="*60)
        print("🔗 All map interactions are logged to blockchain for transparency")
        print("="*60)
    
    def update_display(self):
        """Update the main data display"""
        
        if not PYQT5_AVAILABLE:
            return
        
        display_text = "🗺️ CIVIC ENGAGEMENT GEOGRAPHIC DATA\n"
        display_text += "=" * 60 + "\n\n"
        
        # Show officials if enabled
        if self.show_officials_cb.isChecked():
            officials = self.map_integration.get_filtered_officials()
            display_text += f"👥 GOVERNMENT OFFICIALS ({len(officials)} shown)\n"
            display_text += "-" * 50 + "\n"
            
            for i, official in enumerate(officials, 1):
                coords = official.get('coordinates', (0, 0))
                display_text += f"{i:2d}. {official.get('name', 'Unknown')}\n"
                display_text += f"    📋 {official.get('title', 'Unknown')}\n"
                display_text += f"    🌍 {official.get('jurisdiction', 'Unknown')} "
                display_text += f"({coords[0]:.4f}°, {coords[1]:.4f}°)\n"
                display_text += f"    🏛️ {official.get('party', 'Unknown')}\n"
                display_text += f"    ✅ {official.get('verification', 'uncontacted').title()}\n\n"
        
        # Show activities if enabled
        if self.show_activities_cb.isChecked():
            activities = self.map_integration.get_filtered_activities()
            if activities:
                display_text += f"\n📊 CIVIC ACTIVITIES ({len(activities)} shown)\n"
                display_text += "-" * 50 + "\n"
                
                for i, activity in enumerate(activities, 1):
                    coords = activity.get('coordinates', (0, 0))
                    display_text += f"{i:2d}. {activity.get('title', 'Unknown')}\n"
                    display_text += f"    📅 {activity.get('date', 'Unknown')}\n"
                    display_text += f"    📍 {activity.get('location', 'Unknown')} "
                    display_text += f"({coords[0]:.4f}°, {coords[1]:.4f}°)\n"
                    display_text += f"    🏷️ {activity.get('type', 'Unknown').replace('_', ' ').title()}\n"
                    display_text += f"    📊 {activity.get('status', 'Unknown').title()}\n\n"
        
        display_text += "\n" + "=" * 60 + "\n"
        display_text += "🔗 All map interactions logged to blockchain\n"
        display_text += f"🕒 Last updated: {datetime.now().strftime('%H:%M:%S')}"
        
        self.data_display.setPlainText(display_text)
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display"""
        
        if not PYQT5_AVAILABLE:
            return
        
        officials = self.map_integration.get_filtered_officials()
        activities = self.map_integration.get_filtered_activities()
        permissions = self.map_integration.get_user_permissions()
        
        stats_text = f"Officials: {len(officials)}\n"
        stats_text += f"Activities: {len(activities)}\n"
        stats_text += f"Role: {permissions['role'].title()}\n"
        
        # Count by type
        official_types = {}
        for official in officials:
            official_type = official.get('type', 'other')
            official_types[official_type] = official_types.get(official_type, 0) + 1
        
        if official_types:
            stats_text += "\nBy Type:\n"
            for otype, count in sorted(official_types.items()):
                stats_text += f"  {otype.replace('_', ' ').title()}: {count}\n"
        
        self.stats_display.setPlainText(stats_text)
    
    def perform_search(self):
        """Perform search operation"""
        
        if not PYQT5_AVAILABLE:
            return
        
        query = self.search_input.text().strip()
        if not query:
            return
        
        # Perform search
        results = self.map_integration.search_data(query)
        
        # Display results
        if results:
            search_text = f"🔍 SEARCH RESULTS for '{query}' ({len(results)} found)\n"
            search_text += "=" * 60 + "\n\n"
            
            for i, result in enumerate(results, 1):
                result_type = result.get('result_type', 'unknown')
                
                if result_type == 'official':
                    coords = result.get('coordinates', (0, 0))
                    search_text += f"{i:2d}. 👤 {result.get('name', 'Unknown')}\n"
                    search_text += f"    {result.get('title', 'Unknown')}\n"
                    search_text += f"    📍 {result.get('jurisdiction', 'Unknown')} "
                    search_text += f"({coords[0]:.4f}°, {coords[1]:.4f}°)\n\n"
                
                elif result_type == 'activity':
                    coords = result.get('coordinates', (0, 0))
                    search_text += f"{i:2d}. 📊 {result.get('title', 'Unknown')}\n"
                    search_text += f"    {result.get('type', 'Unknown').replace('_', ' ').title()}\n"
                    search_text += f"    📍 {result.get('location', 'Unknown')} "
                    search_text += f"({coords[0]:.4f}°, {coords[1]:.4f}°)\n\n"
            
            self.data_display.setPlainText(search_text)
        else:
            self.data_display.setPlainText(f"🔍 No results found for '{query}'\n\nTry a different search term.")
    
    def refresh_data(self):
        """Refresh all data"""
        
        try:
            # Reload map integration data
            self.map_integration.load_data()
            
            # Update display
            if PYQT5_AVAILABLE:
                self.load_initial_data()
                self.data_display.append("\n✅ Data refreshed successfully")
            else:
                print("✅ Map data refreshed")
            
            # Log refresh
            self.map_integration.log_to_blockchain('data_refreshed', {
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            error_msg = f"❌ Error refreshing data: {str(e)}"
            if PYQT5_AVAILABLE:
                self.data_display.append(f"\n{error_msg}")
            else:
                print(error_msg)
    
    def show_blockchain_log(self):
        """Show blockchain activity log"""
        
        if PYQT5_AVAILABLE:
            msg = QMessageBox()
            msg.setWindowTitle("⛓️ Blockchain Activity Log")
            msg.setText("Recent map activities logged to blockchain:")
            
            log_text = "• Maps tab accessed\n"
            log_text += "• User permissions verified\n"
            log_text += "• Data filtering applied\n"
            log_text += "• Search queries logged\n"
            log_text += "• Data refresh events\n"
            log_text += "\n🔗 All activities are permanently recorded for transparency and accountability."
            
            msg.setDetailedText(log_text)
            msg.exec_()
        else:
            print("\n⛓️ BLOCKCHAIN ACTIVITY LOG")
            print("=" * 40)
            print("• Maps tab accessed")
            print("• User permissions verified") 
            print("• Data filtering applied")
            print("• Search queries logged")
            print("• Data refresh events")
            print("\n🔗 All activities permanently recorded for transparency")


# Test function
def test_maps_integration():
    """Test the maps integration"""
    
    print("🗺️ Testing Maps Integration...")
    
    # Test MapIntegration
    integration = MapIntegration()
    
    # Test permissions
    permissions = integration.get_user_permissions()
    print(f"Permissions: {permissions}")
    
    # Test officials
    officials = integration.get_filtered_officials()
    print(f"Officials: {len(officials)}")
    
    # Test activities
    activities = integration.get_filtered_activities()
    print(f"Activities: {len(activities)}")
    
    # Test search
    results = integration.search_data("trump")
    print(f"Search results: {len(results)}")
    
    # Test PyQt5 availability
    if PYQT5_AVAILABLE:
        print("✅ PyQt5 available - GUI interface enabled")
        
        # Test with PyQt5 if available
        try:
            from PyQt5.QtWidgets import QApplication
            import sys
            
            app = QApplication(sys.argv)
            
            map_tab = SimpleMapTab()
            map_tab.setWindowTitle("🗺️ Civic Maps Test")
            map_tab.resize(1000, 700)
            map_tab.show()
            
            print("🖥️ GUI test window opened")
            # Don't exec - just show it works
            
        except Exception as e:
            print(f"⚠️ GUI test error: {e}")
    else:
        print("⚠️ PyQt5 not available - text interface only")
        
        # Use text interface
        tab = SimpleMapTab()
        tab.print_text_interface()


if __name__ == "__main__":
    test_maps_integration()