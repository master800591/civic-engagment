# Map View - Geographic Civic Engagement Interface
# PyQt5-based geographic visualization and location-based civic features

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QProgressBar, QTextEdit, QTabWidget,
    QListWidget, QListWidgetItem, QSplitter, QGroupBox,
    QComboBox, QCheckBox, QSpinBox, QSlider, QMessageBox,
    QDialog, QDialogButtonBox, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
    QFormLayout, QGridLayout, QWebEngineView
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QDate, QUrl
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

# Import backend components
try:
    from maps.geographic_manager import GeographicManager, JurisdictionManager
    from users.session import SessionManager
    from blockchain.blockchain import Blockchain
except ImportError as e:
    print(f"Warning: Import error in map view: {e}")


class LocationEventDialog(QDialog):
    """Dialog for creating location-based civic events"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Location-Based Event")
        self.setModal(True)
        self.resize(600, 500)
        self.event_data = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📍 Create Location-Based Civic Event")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # Event form
        form = QFormLayout()
        
        self.event_title = QLineEdit()
        self.event_title.setPlaceholderText("Enter event title...")
        form.addRow("Event Title:", self.event_title)
        
        self.event_type = QComboBox()
        self.event_type.addItems([
            "Town Hall Meeting",
            "Public Hearing",
            "Community Forum",
            "Voting Location",
            "Public Demonstration",
            "Government Office Hours",
            "Service Event",
            "Infrastructure Inspection"
        ])
        form.addRow("Event Type:", self.event_type)
        
        self.description = QTextEdit()
        self.description.setPlaceholderText("Describe the event purpose and agenda...")
        self.description.setMaximumHeight(80)
        form.addRow("Description:", self.description)
        
        # Location information
        location_group = QGroupBox("Location Information")
        location_layout = QFormLayout()
        
        self.venue_name = QLineEdit()
        self.venue_name.setPlaceholderText("Venue name...")
        location_layout.addRow("Venue:", self.venue_name)
        
        self.address = QLineEdit()
        self.address.setPlaceholderText("Street address...")
        location_layout.addRow("Address:", self.address)
        
        self.city = QLineEdit()
        self.city.setPlaceholderText("City...")
        location_layout.addRow("City:", self.city)
        
        self.coordinates = QLineEdit()
        self.coordinates.setPlaceholderText("Latitude, Longitude (optional)...")
        location_layout.addRow("Coordinates:", self.coordinates)
        
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # Event details
        details_group = QGroupBox("Event Details")
        details_layout = QFormLayout()
        
        self.event_date = QDateEdit()
        self.event_date.setDate(QDate.currentDate().addDays(7))
        details_layout.addRow("Date:", self.event_date)
        
        self.start_time = QLineEdit()
        self.start_time.setPlaceholderText("Start time (e.g., 7:00 PM)...")
        details_layout.addRow("Start Time:", self.start_time)
        
        self.duration = QLineEdit()
        self.duration.setPlaceholderText("Duration (e.g., 2 hours)...")
        details_layout.addRow("Duration:", self.duration)
        
        self.capacity = QLineEdit()
        self.capacity.setPlaceholderText("Maximum attendees...")
        details_layout.addRow("Capacity:", self.capacity)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Accessibility and contact
        contact_group = QGroupBox("Contact & Accessibility")
        contact_layout = QFormLayout()
        
        self.contact_person = QLineEdit()
        self.contact_person.setPlaceholderText("Contact person name...")
        contact_layout.addRow("Contact:", self.contact_person)
        
        self.contact_email = QLineEdit()
        self.contact_email.setPlaceholderText("Contact email...")
        contact_layout.addRow("Email:", self.contact_email)
        
        self.accessibility = QCheckBox("Wheelchair accessible")
        self.accessibility.setChecked(True)
        contact_layout.addWidget(self.accessibility)
        
        self.public_transit = QCheckBox("Public transit accessible")
        contact_layout.addWidget(self.public_transit)
        
        contact_group.setLayout(contact_layout)
        layout.addWidget(contact_group)
        
        layout.addLayout(form)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def accept(self):
        """Validate and collect event data"""
        
        if not self.event_title.text().strip():
            QMessageBox.warning(self, "Validation Error", "Event title is required.")
            return
        
        if not self.venue_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "Venue name is required.")
            return
        
        if not self.address.text().strip():
            QMessageBox.warning(self, "Validation Error", "Address is required.")
            return
        
        self.event_data = {
            'title': self.event_title.text().strip(),
            'type': self.event_type.currentText(),
            'description': self.description.toPlainText().strip(),
            'venue_name': self.venue_name.text().strip(),
            'address': self.address.text().strip(),
            'city': self.city.text().strip(),
            'coordinates': self.coordinates.text().strip(),
            'date': self.event_date.date().toString("yyyy-MM-dd"),
            'start_time': self.start_time.text().strip(),
            'duration': self.duration.text().strip(),
            'capacity': self.capacity.text().strip(),
            'contact_person': self.contact_person.text().strip(),
            'contact_email': self.contact_email.text().strip(),
            'wheelchair_accessible': self.accessibility.isChecked(),
            'public_transit_accessible': self.public_transit.isChecked(),
            'created_by': "current_user"  # Will be populated by parent
        }
        
        super().accept()


class JurisdictionBoundaryDialog(QDialog):
    """Dialog for managing jurisdiction boundaries"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Jurisdiction Boundaries")
        self.setModal(True)
        self.resize(700, 600)
        self.boundary_data = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🗺️ Jurisdiction Boundary Management")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # Jurisdiction form
        form = QFormLayout()
        
        self.jurisdiction_name = QLineEdit()
        self.jurisdiction_name.setPlaceholderText("Enter jurisdiction name...")
        form.addRow("Jurisdiction Name:", self.jurisdiction_name)
        
        self.jurisdiction_type = QComboBox()
        self.jurisdiction_type.addItems([
            "City",
            "County", 
            "State",
            "Congressional District",
            "School District",
            "Voting Precinct",
            "Police District",
            "Fire District"
        ])
        form.addRow("Type:", self.jurisdiction_type)
        
        self.parent_jurisdiction = QLineEdit()
        self.parent_jurisdiction.setPlaceholderText("Parent jurisdiction (if applicable)...")
        form.addRow("Parent Jurisdiction:", self.parent_jurisdiction)
        
        # Boundary definition
        boundary_group = QGroupBox("Boundary Definition")
        boundary_layout = QFormLayout()
        
        self.boundary_method = QComboBox()
        self.boundary_method.addItems([
            "Coordinate Points",
            "Street Boundaries",
            "Geographic Features",
            "GIS Shapefile"
        ])
        boundary_layout.addRow("Definition Method:", self.boundary_method)
        
        self.boundary_description = QTextEdit()
        self.boundary_description.setPlaceholderText(
            "Define the boundary using coordinates, street names, or description..."
        )
        self.boundary_description.setMaximumHeight(100)
        boundary_layout.addRow("Boundary Details:", self.boundary_description)
        
        boundary_group.setLayout(boundary_layout)
        layout.addWidget(boundary_group)
        
        # Population and demographics
        demo_group = QGroupBox("Demographics")
        demo_layout = QFormLayout()
        
        self.population = QLineEdit()
        self.population.setPlaceholderText("Estimated population...")
        demo_layout.addRow("Population:", self.population)
        
        self.area_sq_miles = QLineEdit()
        self.area_sq_miles.setPlaceholderText("Area in square miles...")
        demo_layout.addRow("Area (sq mi):", self.area_sq_miles)
        
        self.density = QLineEdit()
        self.density.setPlaceholderText("Population per square mile...")
        demo_layout.addRow("Density:", self.density)
        
        demo_group.setLayout(demo_layout)
        layout.addWidget(demo_group)
        
        # Government information
        gov_group = QGroupBox("Government Information")
        gov_layout = QFormLayout()
        
        self.governing_body = QLineEdit()
        self.governing_body.setPlaceholderText("e.g., City Council, County Commission...")
        gov_layout.addRow("Governing Body:", self.governing_body)
        
        self.officials = QTextEdit()
        self.officials.setPlaceholderText("List key officials (one per line)...")
        self.officials.setMaximumHeight(80)
        gov_layout.addRow("Key Officials:", self.officials)
        
        self.website = QLineEdit()
        self.website.setPlaceholderText("Official website URL...")
        gov_layout.addRow("Website:", self.website)
        
        gov_group.setLayout(gov_layout)
        layout.addWidget(gov_group)
        
        layout.addLayout(form)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def accept(self):
        """Validate and collect boundary data"""
        
        if not self.jurisdiction_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "Jurisdiction name is required.")
            return
        
        if not self.boundary_description.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Boundary description is required.")
            return
        
        self.boundary_data = {
            'name': self.jurisdiction_name.text().strip(),
            'type': self.jurisdiction_type.currentText(),
            'parent_jurisdiction': self.parent_jurisdiction.text().strip(),
            'boundary_method': self.boundary_method.currentText(),
            'boundary_description': self.boundary_description.toPlainText().strip(),
            'population': self.population.text().strip(),
            'area_sq_miles': self.area_sq_miles.text().strip(),
            'density': self.density.text().strip(),
            'governing_body': self.governing_body.text().strip(),
            'officials': [line.strip() for line in self.officials.toPlainText().split('\n') if line.strip()],
            'website': self.website.text().strip(),
            'created_by': "current_user"  # Will be populated by parent
        }
        
        super().accept()


class MapView(QWidget):
    """Main Map View widget for geographic civic engagement"""
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.geographic_manager = None
        self.jurisdiction_manager = None
        self.init_ui()
        self.load_user_session()
    
    def init_ui(self):
        """Initialize the map view interface"""
        
        layout = QVBoxLayout()
        
        # Tab header
        header_layout = QHBoxLayout()
        
        title = QLabel("🗺️ Geographic Civic Engagement")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Quick action buttons
        new_event_btn = QPushButton("📍 New Event")
        new_event_btn.clicked.connect(self.create_location_event)
        header_layout.addWidget(new_event_btn)
        
        boundaries_btn = QPushButton("🗺️ Manage Boundaries")
        boundaries_btn.clicked.connect(self.manage_boundaries)
        header_layout.addWidget(boundaries_btn)
        
        layout.addLayout(header_layout)
        
        # Main content - split between map and controls
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Map area
        map_widget = QWidget()
        map_layout = QVBoxLayout()
        
        # Map controls
        map_controls = QHBoxLayout()
        
        self.layer_selector = QComboBox()
        self.layer_selector.addItems([
            "Civic Events",
            "Voting Locations", 
            "Government Buildings",
            "Jurisdiction Boundaries",
            "Demographics",
            "All Layers"
        ])
        self.layer_selector.currentTextChanged.connect(self.update_map_layers)
        map_controls.addWidget(QLabel("Show:"))
        map_controls.addWidget(self.layer_selector)
        
        map_controls.addStretch()
        
        zoom_in_btn = QPushButton("🔍+")
        zoom_in_btn.clicked.connect(self.zoom_in)
        map_controls.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("🔍-")
        zoom_out_btn.clicked.connect(self.zoom_out)
        map_controls.addWidget(zoom_out_btn)
        
        map_layout.addLayout(map_controls)
        
        # Map display (using web view for interactive maps)
        try:
            self.map_view = QWebEngineView()
            # Load a simple OpenStreetMap view
            self.map_view.setHtml(self.generate_map_html())
            map_layout.addWidget(self.map_view)
        except ImportError:
            # Fallback if QWebEngineView not available
            map_placeholder = QLabel("🗺️ Interactive Map\n\n(Map visualization would appear here)")
            map_placeholder.setAlignment(Qt.AlignCenter)
            map_placeholder.setStyleSheet("QLabel { border: 2px dashed #ccc; background-color: #f9f9f9; font-size: 14px; }")
            map_placeholder.setMinimumSize(600, 400)
            map_layout.addWidget(map_placeholder)
            self.map_view = None
        
        map_widget.setLayout(map_layout)
        main_splitter.addWidget(map_widget)
        
        # Side panel with tabs
        side_panel = QTabWidget()
        
        # Events tab
        events_tab = QWidget()
        self.init_events_tab(events_tab)
        side_panel.addTab(events_tab, "📍 Events")
        
        # Jurisdictions tab
        jurisdictions_tab = QWidget()
        self.init_jurisdictions_tab(jurisdictions_tab)
        side_panel.addTab(jurisdictions_tab, "🏛️ Jurisdictions")
        
        # Locations tab
        locations_tab = QWidget()
        self.init_locations_tab(locations_tab)
        side_panel.addTab(locations_tab, "📍 Locations")
        
        main_splitter.addWidget(side_panel)
        main_splitter.setSizes([700, 300])  # Give more space to map
        
        layout.addWidget(main_splitter)
        
        self.setLayout(layout)
    
    def generate_map_html(self) -> str:
        """Generate HTML for interactive map"""
        
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Civic Engagement Map</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <style>
                #map { height: 100vh; width: 100%; }
                body { margin: 0; padding: 0; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <script>
                var map = L.map('map').setView([39.8283, -98.5795], 4); // Center of USA
                
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);
                
                // Sample civic locations
                var civicLocations = [
                    [40.7128, -74.0060, "New York City Hall", "Government Building"],
                    [34.0522, -118.2437, "Los Angeles City Hall", "Government Building"],
                    [41.8781, -87.6298, "Chicago City Hall", "Government Building"],
                    [29.7604, -95.3698, "Houston City Hall", "Government Building"]
                ];
                
                civicLocations.forEach(function(location) {
                    L.marker([location[0], location[1]])
                     .addTo(map)
                     .bindPopup('<b>' + location[2] + '</b><br>' + location[3]);
                });
                
                // Add sample civic events
                var eventIcon = L.divIcon({
                    className: 'custom-div-icon',
                    html: "📍",
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                });
                
                var sampleEvents = [
                    [40.7589, -73.9851, "Town Hall Meeting", "Community Forum - Jan 25, 7 PM"],
                    [34.0522, -118.2437, "Budget Hearing", "Public Budget Discussion - Jan 28, 6 PM"],
                    [41.8781, -87.6298, "Zoning Meeting", "Planning Commission - Jan 30, 7 PM"]
                ];
                
                sampleEvents.forEach(function(event) {
                    L.marker([event[0], event[1]], {icon: eventIcon})
                     .addTo(map)
                     .bindPopup('<b>' + event[2] + '</b><br>' + event[3]);
                });
            </script>
        </body>
        </html>
        """
    
    def init_events_tab(self, tab_widget):
        """Initialize the events tab"""
        
        layout = QVBoxLayout()
        
        # Events header
        header = QLabel("📍 Civic Events by Location")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header)
        
        # Events list
        self.events_list = QListWidget()
        
        # Sample events
        sample_events = [
            "📍 Town Hall Meeting - Main Library (Jan 25, 7 PM)",
            "🏛️ City Council Session - City Hall (Jan 28, 6 PM)",
            "👥 Community Forum - Community Center (Jan 30, 7 PM)",
            "🗳️ Budget Hearing - Municipal Building (Feb 2, 6:30 PM)",
            "📋 Planning Commission - Planning Office (Feb 5, 7 PM)"
        ]
        
        for event in sample_events:
            item = QListWidgetItem(event)
            self.events_list.addItem(item)
        
        self.events_list.itemDoubleClicked.connect(self.view_event_details)
        layout.addWidget(self.events_list)
        
        # Event actions
        actions_layout = QHBoxLayout()
        
        view_event_btn = QPushButton("👁️ View Details")
        view_event_btn.clicked.connect(self.view_selected_event)
        actions_layout.addWidget(view_event_btn)
        
        directions_btn = QPushButton("🧭 Get Directions")
        directions_btn.clicked.connect(self.get_directions)
        actions_layout.addWidget(directions_btn)
        
        layout.addLayout(actions_layout)
        
        tab_widget.setLayout(layout)
    
    def init_jurisdictions_tab(self, tab_widget):
        """Initialize the jurisdictions tab"""
        
        layout = QVBoxLayout()
        
        # Jurisdictions header
        header = QLabel("🏛️ Jurisdictional Information")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header)
        
        # Jurisdiction tree
        self.jurisdiction_tree = QTreeWidget()
        self.jurisdiction_tree.setHeaderLabels(["Jurisdiction", "Type", "Population"])
        
        # Sample jurisdiction hierarchy
        federal_item = QTreeWidgetItem(["United States", "Federal", "331,000,000"])
        
        state_item = QTreeWidgetItem(["Illinois", "State", "12,800,000"])
        federal_item.addChild(state_item)
        
        county_item = QTreeWidgetItem(["Cook County", "County", "5,200,000"])
        state_item.addChild(county_item)
        
        city_item = QTreeWidgetItem(["Chicago", "City", "2,700,000"])
        county_item.addChild(city_item)
        
        ward_item = QTreeWidgetItem(["Ward 1", "Ward", "45,000"])
        city_item.addChild(ward_item)
        
        self.jurisdiction_tree.addTopLevelItem(federal_item)
        self.jurisdiction_tree.expandAll()
        self.jurisdiction_tree.resizeColumnToContents(0)
        self.jurisdiction_tree.itemDoubleClicked.connect(self.view_jurisdiction_details)
        
        layout.addWidget(self.jurisdiction_tree)
        
        # Jurisdiction actions
        actions_layout = QHBoxLayout()
        
        view_jurisdiction_btn = QPushButton("👁️ View Details")
        view_jurisdiction_btn.clicked.connect(self.view_selected_jurisdiction)
        actions_layout.addWidget(view_jurisdiction_btn)
        
        representatives_btn = QPushButton("👤 Representatives")
        representatives_btn.clicked.connect(self.view_representatives)
        actions_layout.addWidget(representatives_btn)
        
        layout.addLayout(actions_layout)
        
        tab_widget.setLayout(layout)
    
    def init_locations_tab(self, tab_widget):
        """Initialize the locations tab"""
        
        layout = QVBoxLayout()
        
        # Locations header
        header = QLabel("📍 Key Civic Locations")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header)
        
        # Location categories
        categories_layout = QHBoxLayout()
        
        self.location_category = QComboBox()
        self.location_category.addItems([
            "All Locations",
            "Government Buildings",
            "Voting Locations",
            "Public Services",
            "Emergency Services",
            "Courts",
            "Libraries",
            "Parks & Recreation"
        ])
        self.location_category.currentTextChanged.connect(self.filter_locations)
        categories_layout.addWidget(QLabel("Category:"))
        categories_layout.addWidget(self.location_category)
        
        categories_layout.addStretch()
        
        layout.addLayout(categories_layout)
        
        # Locations list
        self.locations_list = QListWidget()
        
        # Sample locations
        sample_locations = [
            "🏛️ City Hall - 123 Main St",
            "🗳️ Voting Center - Community College",
            "👮 Police Station - 456 Oak Ave",
            "🚒 Fire Department - 789 Elm St",
            "⚖️ Municipal Court - 321 Court St",
            "📚 Central Library - 654 Library Ln",
            "🏥 Health Department - 987 Health Blvd",
            "🌳 Central Park - 147 Park Dr"
        ]
        
        for location in sample_locations:
            item = QListWidgetItem(location)
            self.locations_list.addItem(item)
        
        self.locations_list.itemDoubleClicked.connect(self.view_location_details)
        layout.addWidget(self.locations_list)
        
        # Location actions
        actions_layout = QHBoxLayout()
        
        view_location_btn = QPushButton("👁️ View Details")
        view_location_btn.clicked.connect(self.view_selected_location)
        actions_layout.addWidget(view_location_btn)
        
        services_btn = QPushButton("🔧 Services")
        services_btn.clicked.connect(self.view_location_services)
        actions_layout.addWidget(services_btn)
        
        layout.addLayout(actions_layout)
        
        tab_widget.setLayout(layout)
    
    def load_user_session(self):
        """Load current user session"""
        
        try:
            # Mock current user for testing
            self.current_user = {
                'email': 'test@example.com',
                'role': 'Contract Representative',
                'jurisdiction': 'City of Springfield'
            }
            
            if self.current_user:
                self.init_backend_managers()
        except Exception as e:
            print(f"Error loading user session: {e}")
    
    def init_backend_managers(self):
        """Initialize backend management systems"""
        
        try:
            # self.geographic_manager = GeographicManager()
            # self.jurisdiction_manager = JurisdictionManager()
            print("Geographic managers would be initialized here")
        except Exception as e:
            print(f"Error initializing geographic managers: {e}")
    
    def create_location_event(self):
        """Create a new location-based event"""
        
        if not self.current_user:
            QMessageBox.warning(self, "Authentication Required", 
                               "Please log in to create events.")
            return
        
        dialog = LocationEventDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            event_data = dialog.event_data
            event_data['created_by'] = self.current_user.get('email')
            
            try:
                # TODO: Use actual geographic manager
                # success, message = self.geographic_manager.create_location_event(event_data)
                success, message = True, "Event created successfully"
                
                if success:
                    QMessageBox.information(self, "Success", 
                                          f"Event '{event_data['title']}' created successfully!")
                    # Refresh events list and map
                    # self.refresh_events()
                else:
                    QMessageBox.warning(self, "Error", message)
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create event: {e}")
    
    def manage_boundaries(self):
        """Manage jurisdiction boundaries"""
        
        if not self.current_user:
            QMessageBox.warning(self, "Authentication Required", 
                               "Please log in to manage boundaries.")
            return
        
        dialog = JurisdictionBoundaryDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            boundary_data = dialog.boundary_data
            boundary_data['created_by'] = self.current_user.get('email')
            
            try:
                # TODO: Use actual jurisdiction manager
                # success, message = self.jurisdiction_manager.create_jurisdiction_boundary(boundary_data)
                success, message = True, "Boundary created successfully"
                
                if success:
                    QMessageBox.information(self, "Success", 
                                          f"Jurisdiction '{boundary_data['name']}' created successfully!")
                    # Refresh jurisdictions and map
                    # self.refresh_jurisdictions()
                else:
                    QMessageBox.warning(self, "Error", message)
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create boundary: {e}")
    
    def update_map_layers(self, layer_name):
        """Update map display based on selected layer"""
        
        print(f"Updating map to show layer: {layer_name}")
        # TODO: Update map visualization based on layer selection
    
    def zoom_in(self):
        """Zoom in on the map"""
        
        if self.map_view:
            self.map_view.page().runJavaScript("map.zoomIn();")
    
    def zoom_out(self):
        """Zoom out on the map"""
        
        if self.map_view:
            self.map_view.page().runJavaScript("map.zoomOut();")
    
    def view_event_details(self, item):
        """View details of selected event"""
        
        event_text = item.text()
        QMessageBox.information(self, "Event Details", 
                               f"Event: {event_text}\n\n"
                               "Detailed event information would be displayed here:\n"
                               "• Full description and agenda\n"
                               "• Registration requirements\n"
                               "• Accessibility information\n"
                               "• Contact details\n"
                               "• Directions and parking")
    
    def view_selected_event(self):
        """View details of currently selected event"""
        
        current_item = self.events_list.currentItem()
        if current_item:
            self.view_event_details(current_item)
    
    def get_directions(self):
        """Get directions to selected event location"""
        
        current_item = self.events_list.currentItem()
        if current_item:
            QMessageBox.information(self, "Directions", 
                                   f"Getting directions to: {current_item.text()}\n\n"
                                   "This would open:\n"
                                   "• Interactive map with route\n"
                                   "• Turn-by-turn directions\n"
                                   "• Public transit options\n"
                                   "• Parking information\n"
                                   "• Accessibility details")
    
    def view_jurisdiction_details(self, item, column):
        """View details of selected jurisdiction"""
        
        jurisdiction_name = item.text(0)
        jurisdiction_type = item.text(1)
        
        QMessageBox.information(self, "Jurisdiction Details", 
                               f"Jurisdiction: {jurisdiction_name}\n"
                               f"Type: {jurisdiction_type}\n\n"
                               "Detailed information would include:\n"
                               "• Government structure and officials\n"
                               "• Services provided\n"
                               "• Contact information\n"
                               "• Voting and representation\n"
                               "• Upcoming elections and meetings")
    
    def view_selected_jurisdiction(self):
        """View details of currently selected jurisdiction"""
        
        current_item = self.jurisdiction_tree.currentItem()
        if current_item:
            self.view_jurisdiction_details(current_item, 0)
    
    def view_representatives(self):
        """View representatives for selected jurisdiction"""
        
        current_item = self.jurisdiction_tree.currentItem()
        if current_item:
            jurisdiction_name = current_item.text(0)
            QMessageBox.information(self, "Representatives", 
                                   f"Representatives for {jurisdiction_name}:\n\n"
                                   "This would show:\n"
                                   "• Elected officials and their roles\n"
                                   "• Contact information\n"
                                   "• Terms of office\n"
                                   "• Committee assignments\n"
                                   "• Recent votes and positions")
    
    def filter_locations(self, category):
        """Filter locations by category"""
        
        print(f"Filtering locations by category: {category}")
        # TODO: Implement actual location filtering
    
    def view_location_details(self, item):
        """View details of selected location"""
        
        location_text = item.text()
        QMessageBox.information(self, "Location Details", 
                               f"Location: {location_text}\n\n"
                               "Detailed information would include:\n"
                               "• Address and contact information\n"
                               "• Hours of operation\n"
                               "• Services provided\n"
                               "• Accessibility features\n"
                               "• Public transit access\n"
                               "• Parking availability")
    
    def view_selected_location(self):
        """View details of currently selected location"""
        
        current_item = self.locations_list.currentItem()
        if current_item:
            self.view_location_details(current_item)
    
    def view_location_services(self):
        """View services available at selected location"""
        
        current_item = self.locations_list.currentItem()
        if current_item:
            location_text = current_item.text()
            QMessageBox.information(self, "Location Services", 
                                   f"Services at {location_text}:\n\n"
                                   "Available services would include:\n"
                                   "• Public services and departments\n"
                                   "• Service hours and requirements\n"
                                   "• Online alternatives\n"
                                   "• Required documents\n"
                                   "• Fees and processing times")


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    map_view = MapView()
    map_view.show()
    
    sys.exit(app.exec_())