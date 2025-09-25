# Events Module - UI Components for Civic Event Management
"""
Events UI components providing:
- Calendar interface for event discovery and management
- Event creation wizards with constitutional review
- RSVP management and attendance tracking  
- Community organizing and coordination tools
"""

from typing import Optional, Any, Dict, List
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QCalendarWidget, QListWidget, QListWidgetItem, QTextEdit, QLineEdit, 
                            QComboBox, QDateTimeEdit, QSpinBox, QCheckBox, QGroupBox,
                            QTabWidget, QScrollArea, QMessageBox, QFormLayout, QFrame,
                            QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                            QDialog)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDateTime, QDate
from PyQt5.QtGui import QFont, QPixmap, QColor
from .event_manager import EventManager
from ..users.session import SessionManager
from ..users.backend import UserBackend

class CalendarTab(QWidget):
    """Main calendar interface for civic event management and community organizing"""
    
    # Signal for event updates
    event_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.event_manager = EventManager()
        self.selected_date = QDate.currentDate()
        self.current_events = []
        self.init_ui()
        
        # Auto-refresh timer for event updates
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_events)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes
    
    def init_ui(self):
        """Initialize the calendar interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Blockchain status and user role display
        user = SessionManager.get_current_user()
        role = user.get('role', 'Unknown') if user else 'Unknown'
        
        blockchain_status = QLabel("All civic events and attendance are <b>recorded on blockchain</b> for transparency.")
        blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
        blockchain_status.setAccessibleName("Blockchain Status")
        blockchain_status.setToolTip("All event activities are transparently recorded on the blockchain.")
        
        role_label = QLabel(f"Your Role: <b>{role}</b>")
        role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
        role_label.setAccessibleName("User Role")
        role_label.setToolTip("Your platform role determines event creation and management permissions.")
        
        # Event management buttons
        create_event_btn = QPushButton("Create New Event")
        create_event_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        create_event_btn.setAccessibleName("Create New Event Button")
        create_event_btn.setToolTip("Create a new civic event or community gathering.")
        create_event_btn.setMinimumHeight(40)
        create_event_btn.setMinimumWidth(180)
        create_event_btn.clicked.connect(self.open_event_creation_dialog)
        
        my_events_btn = QPushButton("My Events")
        my_events_btn.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
        my_events_btn.clicked.connect(self.show_my_events)
        
        top_layout = QVBoxLayout()
        top_layout.addWidget(blockchain_status)
        top_layout.addWidget(role_label)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(create_event_btn)
        button_layout.addWidget(my_events_btn)
        button_layout.addStretch()
        top_layout.addLayout(button_layout)
        
        layout.addLayout(top_layout)
        
        # Header
        header = QLabel("📅 Civic Events & Community Calendar")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
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
        
        # Create main calendar interface for logged-in users
        self.create_calendar_interface()
    
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
        
        title_label = QLabel("Calendar Access Required")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #495057; margin-bottom: 10px;")
        
        message_label = QLabel("Please log in to access the civic events calendar and create community events.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 16px; color: #6c757d; margin-bottom: 20px;")
        message_label.setWordWrap(True)
        
        frame_layout.addWidget(icon_label)
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(message_label)
        
        login_frame.setLayout(frame_layout)
        layout.addWidget(login_frame)
    
    def create_calendar_interface(self):
        """Create the main calendar interface for authenticated users"""
        layout = self.main_content.layout()
        
        # Main calendar layout with splitter
        splitter = QSplitter()
        
        # Left panel - Calendar and filters
        left_panel = self.create_calendar_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Event details and management
        right_panel = self.create_event_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        # Load initial events
        self.refresh_events()
    
    def create_calendar_panel(self) -> QWidget:
        """Create the left calendar and filters panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Calendar widget
        calendar_group = QGroupBox("Event Calendar")
        calendar_layout = QVBoxLayout()
        
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.setStyleSheet("""
            QCalendarWidget QToolButton {
                height: 40px;
                width: 80px;
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                background-color: #ecf0f1;
                border: none;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #bdc3c7;
            }
        """)
        calendar_layout.addWidget(self.calendar)
        calendar_group.setLayout(calendar_layout)
        layout.addWidget(calendar_group)
        
        # Event filters
        filters_group = QGroupBox("Event Filters")
        filters_layout = QFormLayout()
        
        self.event_type_filter = QComboBox()
        self.event_type_filter.addItems([
            "All Events",
            "Town Halls",
            "Public Meetings", 
            "Training Sessions",
            "Elections",
            "Debates",
            "Community Forums",
            "Working Groups",
            "Social Events"
        ])
        self.event_type_filter.currentTextChanged.connect(self.apply_filters)
        
        self.location_filter = QLineEdit()
        self.location_filter.setPlaceholderText("Filter by location...")
        self.location_filter.textChanged.connect(self.apply_filters)
        
        filters_layout.addRow("Event Type:", self.event_type_filter)
        filters_layout.addRow("Location:", self.location_filter)
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Quick stats
        stats_group = QGroupBox("Event Statistics")
        stats_layout = QVBoxLayout()
        
        self.total_events_label = QLabel("Total Events: Loading...")
        self.upcoming_events_label = QLabel("Upcoming: Loading...")
        self.my_events_label = QLabel("My Events: Loading...")
        
        stats_layout.addWidget(self.total_events_label)
        stats_layout.addWidget(self.upcoming_events_label)
        stats_layout.addWidget(self.my_events_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_event_panel(self) -> QWidget:
        """Create the right event details and management panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Event tabs
        self.event_tabs = QTabWidget()
        self.event_tabs.setStyleSheet("""
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
                background: #e67e22;
                color: white;
                font-weight: bold;
            }
        """)
        
        # Add event tabs
        self.event_tabs.addTab(self.create_events_list_tab(), "📋 Events")
        self.event_tabs.addTab(self.create_event_details_tab(), "📝 Details")
        self.event_tabs.addTab(self.create_rsvp_tab(), "✋ RSVP")
        self.event_tabs.addTab(self.create_attendance_tab(), "✅ Attendance")
        
        layout.addWidget(self.event_tabs)
        
        widget.setLayout(layout)
        return widget
    
    def create_events_list_tab(self) -> QWidget:
        """Create the events list tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Events for selected date
        date_label = QLabel(f"Events for {self.selected_date.toString('dddd, MMMM d, yyyy')}")
        date_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(date_label)
        
        self.events_list = QListWidget()
        self.events_list.itemClicked.connect(self.on_event_selected)
        layout.addWidget(self.events_list)
        
        # Event action buttons
        actions_layout = QHBoxLayout()
        
        self.rsvp_button = QPushButton("RSVP")
        self.rsvp_button.setStyleSheet("background-color: #007bff; color: white; padding: 8px 16px; border-radius: 5px;")
        self.rsvp_button.clicked.connect(self.quick_rsvp)
        self.rsvp_button.setEnabled(False)
        
        self.check_in_button = QPushButton("Check In")
        self.check_in_button.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px; border-radius: 5px;")
        self.check_in_button.clicked.connect(self.quick_check_in)
        self.check_in_button.setEnabled(False)
        
        actions_layout.addWidget(self.rsvp_button)
        actions_layout.addWidget(self.check_in_button)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_event_details_tab(self) -> QWidget:
        """Create the event details tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.event_details = QTextEdit()
        self.event_details.setReadOnly(True)
        layout.addWidget(self.event_details)
        
        widget.setLayout(layout)
        return widget
    
    def create_rsvp_tab(self) -> QWidget:
        """Create the RSVP management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        rsvp_group = QGroupBox("RSVP to Event")
        rsvp_layout = QFormLayout()
        
        self.rsvp_status = QComboBox()
        self.rsvp_status.addItems(["Attending", "Not Attending", "Maybe"])
        
        self.rsvp_notes = QTextEdit()
        self.rsvp_notes.setMaximumHeight(100)
        self.rsvp_notes.setPlaceholderText("Optional notes or special requirements...")
        
        submit_rsvp_btn = QPushButton("Submit RSVP")
        submit_rsvp_btn.setStyleSheet("background-color: #007bff; color: white; padding: 8px 16px; border-radius: 5px;")
        submit_rsvp_btn.clicked.connect(self.submit_rsvp)
        
        rsvp_layout.addRow("Status:", self.rsvp_status)
        rsvp_layout.addRow("Notes:", self.rsvp_notes)
        rsvp_layout.addRow("", submit_rsvp_btn)
        
        rsvp_group.setLayout(rsvp_layout)
        layout.addWidget(rsvp_group)
        
        # RSVP list for event organizers
        rsvp_list_group = QGroupBox("Event RSVPs")
        rsvp_list_layout = QVBoxLayout()
        
        self.rsvp_table = QTableWidget()
        self.rsvp_table.setColumnCount(4)
        self.rsvp_table.setHorizontalHeaderLabels(["Name", "Status", "RSVP Date", "Notes"])
        self.rsvp_table.horizontalHeader().setStretchLastSection(True)
        
        rsvp_list_layout.addWidget(self.rsvp_table)
        rsvp_list_group.setLayout(rsvp_list_layout)
        layout.addWidget(rsvp_list_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_attendance_tab(self) -> QWidget:
        """Create the attendance tracking tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        check_in_group = QGroupBox("Event Check-In")
        check_in_layout = QVBoxLayout()
        
        check_in_btn = QPushButton("Check In to Event")
        check_in_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 12px; border-radius: 5px; font-size: 16px;")
        check_in_btn.clicked.connect(self.check_in_to_event)
        
        check_in_layout.addWidget(check_in_btn)
        check_in_group.setLayout(check_in_layout)
        layout.addWidget(check_in_group)
        
        # Attendance list for event organizers
        attendance_group = QGroupBox("Event Attendance")
        attendance_layout = QVBoxLayout()
        
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(3)
        self.attendance_table.setHorizontalHeaderLabels(["Name", "Check-In Time", "Participation"])
        self.attendance_table.horizontalHeader().setStretchLastSection(True)
        
        attendance_layout.addWidget(self.attendance_table)
        attendance_group.setLayout(attendance_layout)
        layout.addWidget(attendance_group)
        
        widget.setLayout(layout)
        return widget
    
    def on_date_selected(self, date: QDate):
        """Handle date selection in calendar"""
        self.selected_date = date
        self.refresh_events_for_date(date)
    
    def refresh_events_for_date(self, date: QDate):
        """Refresh events list for selected date"""
        date_str = date.toString("yyyy-MM-dd")
        
        # Get events for this date
        filters = {
            'start_date': f"{date_str}T00:00:00",
            'end_date': f"{date_str}T23:59:59"
        }
        
        try:
            events = self.event_manager.get_events(filters)
            self.current_events = events
            
            # Update events list
            self.events_list.clear()
            for event in events:
                event_text = f"{event['title']} - {event['event_type']} ({event.get('start_datetime', '')[:5]})"
                item = QListWidgetItem(event_text)
                item.setData(Qt.UserRole, event)
                self.events_list.addItem(item)
            
            # Update date label
            date_label_text = f"Events for {date.toString('dddd, MMMM d, yyyy')} ({len(events)} events)"
            # Find and update the date label - would need reference to update
            
        except Exception as e:
            print(f"Error loading events for date: {e}")
    
    def on_event_selected(self, item):
        """Handle event selection from list"""
        if hasattr(item, 'data') and item.data(Qt.UserRole):
            event = item.data(Qt.UserRole)
            self.display_event_details(event)
            self.rsvp_button.setEnabled(True)
            self.check_in_button.setEnabled(True)
    
    def display_event_details(self, event: Dict[str, Any]):
        """Display detailed event information"""
        details_text = f"""
<h2>{event['title']}</h2>
<p><strong>Type:</strong> {event['event_type']}</p>
<p><strong>Organizer:</strong> {event['organizer_name']}</p>
<p><strong>Start:</strong> {event['start_datetime']}</p>
<p><strong>End:</strong> {event.get('end_datetime', 'Not specified')}</p>
<p><strong>Location:</strong> {event.get('location', 'Not specified')}</p>
<p><strong>Max Participants:</strong> {event.get('max_participants', 'Unlimited')}</p>
<p><strong>RSVP Required:</strong> {'Yes' if event.get('registration_required') else 'No'}</p>
<p><strong>Current RSVPs:</strong> {event.get('rsvp_count', 0)}</p>

<h3>Description:</h3>
<p>{event.get('description', 'No description provided')}</p>

<h3>Status:</h3>
<p>Constitutional Review: {event.get('constitutional_review_status', 'Unknown')}</p>
<p>Event Status: {event.get('status', 'Unknown')}</p>
        """.strip()
        
        self.event_details.setHtml(details_text)
    
    def refresh_events(self):
        """Refresh all events data"""
        if not SessionManager.is_authenticated():
            return
        
        try:
            # Update calendar events for current view
            self.refresh_events_for_date(self.selected_date)
            
            # Update statistics
            all_events = self.event_manager.get_events()
            user = SessionManager.get_current_user()
            user_events = self.event_manager.get_user_events(user['email']) if user else {'organized': [], 'rsvp': [], 'attended': []}
            
            # Update stats labels
            self.total_events_label.setText(f"Total Events: {len(all_events)}")
            
            # Count upcoming events
            upcoming_count = len([e for e in all_events if e.get('start_datetime', '') > datetime.now().isoformat()])
            self.upcoming_events_label.setText(f"Upcoming: {upcoming_count}")
            
            # Count user's events
            my_events_count = len(user_events.get('organized', [])) + len(user_events.get('rsvp', []))
            self.my_events_label.setText(f"My Events: {my_events_count}")
            
        except Exception as e:
            print(f"Error refreshing events: {e}")
    
    def apply_filters(self):
        """Apply event filters"""
        # This would implement filtering logic
        pass
    
    def open_event_creation_dialog(self):
        """Open event creation dialog"""
        dialog = EventCreationDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # Refresh events after creation
            self.refresh_events()
    
    def show_my_events(self):
        """Show user's events"""
        dialog = MyEventsDialog(self)
        dialog.exec_()
    
    def quick_rsvp(self):
        """Quick RSVP to selected event"""
        # This would implement quick RSVP functionality
        QMessageBox.information(self, "RSVP", "Quick RSVP functionality would be implemented here.")
    
    def quick_check_in(self):
        """Quick check-in to selected event"""
        # This would implement quick check-in functionality
        QMessageBox.information(self, "Check-In", "Quick check-in functionality would be implemented here.")
    
    def submit_rsvp(self):
        """Submit RSVP for current event"""
        # This would implement RSVP submission
        QMessageBox.information(self, "RSVP", "RSVP submission would be implemented here.")
    
    def check_in_to_event(self):
        """Check in to current event"""
        # This would implement event check-in
        QMessageBox.information(self, "Check-In", "Event check-in would be implemented here.")

class EventCreationDialog(QDialog):
    """Dialog for creating new events"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Event")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Event creation dialog would be implemented here with full form."))
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

class MyEventsDialog(QDialog):
    """Dialog for managing user's events"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("My Events")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("My events management dialog would be implemented here."))
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)