# Debates Module - UI Components
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QListWidget, QTextEdit, QLineEdit, QComboBox, QMessageBox,
                            QFrame, QScrollArea, QSplitter, QGroupBox, QFormLayout, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from .backend import DebateBackend, DebateStatus, ArgumentType
from ..users.session import SessionManager
from ..users.backend import UserBackend


from typing import Optional

class CreateTopicDialog(QDialog):
    """User-friendly dialog for creating new debate topics"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("✨ Create New Debate Topic")
        self.setModal(True)  # Make it modal so it stays on top
        self.setFixedSize(700, 550)  # Fixed size for consistent experience
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border: 2px solid #007bff;
                border-radius: 10px;
            }
            QLabel {
                font-weight: bold;
                color: #343a40;
                font-size: 12px;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #dee2e6;
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #007bff;
                outline: none;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
            QPushButton#cancel {
                background-color: #6c757d;
            }
            QPushButton#cancel:hover {
                background-color: #545b62;
            }
        """)
        self.init_ui()
    
    def init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel("🗳️ Create a New Debate Topic")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #007bff; margin-bottom: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Instructions
        instructions = QLabel("Fill out the form below to create a new topic for democratic debate. Your topic will be reviewed and made available to the community.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 11px; color: #6c757d; margin-bottom: 15px; font-weight: normal;")
        layout.addWidget(instructions)
        
        # Form section
        form_group = QGroupBox("Topic Information")
        form_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; color: #495057; }")
        form_layout = QVBoxLayout()
        
        # Title input with character count
        form_layout.addWidget(QLabel("📝 Topic Title (required):"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter a clear, engaging title (e.g., 'Should we implement ranked choice voting?')")
        self.title_input.textChanged.connect(self.update_character_counts)
        form_layout.addWidget(self.title_input)
        
        self.title_count_label = QLabel("Characters: 0/100")
        self.title_count_label.setStyleSheet("font-size: 10px; color: #6c757d; font-weight: normal;")
        form_layout.addWidget(self.title_count_label)
        
        # Description input with character count
        form_layout.addWidget(QLabel("📋 Detailed Description (required):"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Provide context, background, and key points for discussion. What specific aspects should people debate?")
        self.description_input.setMinimumHeight(120)
        self.description_input.textChanged.connect(self.update_character_counts)
        form_layout.addWidget(self.description_input)
        
        self.desc_count_label = QLabel("Characters: 0/1000")
        self.desc_count_label.setStyleSheet("font-size: 10px; color: #6c757d; font-weight: normal;")
        form_layout.addWidget(self.desc_count_label)
        
        # Jurisdiction section
        jurisdiction_group = QGroupBox("Jurisdiction & Location")
        jurisdiction_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; color: #495057; }")
        jurisdiction_layout = QVBoxLayout()
        
        juris_row = QHBoxLayout()
        juris_row.addWidget(QLabel("🏛️ Governance Level:"))
        self.jurisdiction_combo = QComboBox()
        self.jurisdiction_combo.addItems(["city", "state", "country", "world"])
        self.jurisdiction_combo.setCurrentText("city")
        self.jurisdiction_combo.currentTextChanged.connect(self.update_location_options)
        juris_row.addWidget(self.jurisdiction_combo)
        
        juris_row.addWidget(QLabel("📍 Location:"))
        self.location_combo = QComboBox()
        self.location_combo.setMinimumWidth(200)
        juris_row.addWidget(self.location_combo)
        
        jurisdiction_layout.addLayout(juris_row)
        
        # Populate location options based on user's registered location
        self.update_location_options()
        
        jurisdiction_group.setLayout(jurisdiction_layout)
        form_layout.addWidget(jurisdiction_group)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
    # Add blockchain status, role, and export button at top for user-friendliness
    from ..users.session import SessionManager
    user = SessionManager.get_current_user()
    role = user.get('role', 'Unknown') if user else 'Unknown'
    blockchain_status = QLabel("All debate actions are <b>recorded on blockchain</b> for transparency.")
    blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
    blockchain_status.setAccessibleName("Blockchain Status")
    blockchain_status.setToolTip("All actions are securely recorded for audit and transparency.")
    role_label = QLabel(f"Your Role: <b>{role}</b>")
    role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
    role_label.setAccessibleName("User Role")
    role_label.setToolTip("Your current platform role.")
    export_btn = QPushButton("Export Debate Report")
    export_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 8px; padding: 12px 28px; font-size: 15px;")
    export_btn.setAccessibleName("Export Debate Report Button")
    export_btn.setToolTip("View and export blockchain-based debate reports.")
    export_btn.setMinimumHeight(40)
    export_btn.setMinimumWidth(180)
    export_btn.clicked.connect(self.open_reports_tab)
    top_layout = QVBoxLayout()
    top_layout.addWidget(blockchain_status)
    top_layout.addWidget(role_label)
    top_layout.addWidget(export_btn)
    layout.insertLayout(0, top_layout)

    # Buttons with better styling
    button_layout = QHBoxLayout()
    button_layout.addStretch()
    self.cancel_button = QPushButton("❌ Cancel")
    self.cancel_button.setObjectName("cancel")
    self.cancel_button.setAccessibleName("Cancel Button")
    self.cancel_button.setToolTip("Cancel topic creation.")
    self.cancel_button.setMinimumHeight(36)
    self.cancel_button.setMinimumWidth(120)
    self.cancel_button.clicked.connect(self.reject)
    button_layout.addWidget(self.cancel_button)
    self.create_button = QPushButton("✅ Create Topic")
    self.create_button.setAccessibleName("Create Topic Button")
    self.create_button.setToolTip("Submit your new debate topic.")
    self.create_button.setMinimumHeight(36)
    self.create_button.setMinimumWidth(140)
    self.create_button.clicked.connect(self.create_topic)
    self.create_button.setDefault(True)
    button_layout.addWidget(self.create_button)
    layout.addLayout(button_layout)
    self.setLayout(layout)
    self.title_input.setFocus()
    
    def update_location_options(self) -> None:
        """Update location dropdown based on jurisdiction level and user's registered location"""
        current_user = SessionManager.get_current_user()
        if not current_user:
            return
        
        jurisdiction = self.jurisdiction_combo.currentText()
        self.location_combo.clear()
        
        # Get user's registered location data
        user_city = current_user.get('city', '').strip()
        user_state = current_user.get('state', '').strip()
        user_country = current_user.get('country', '').strip()
        
        if jurisdiction == "world":
            # World-level topics
            self.location_combo.addItem("🌍 World", "world")
            
        elif jurisdiction == "country":
            # Can only create topics for user's country
            if user_country:
                self.location_combo.addItem(f"🏳️ {user_country}", user_country)
            else:
                self.location_combo.addItem("⚠️ Country not set in profile", "")
                
        elif jurisdiction == "state":
            # Can only create topics for user's state/province
            if user_state and user_country:
                self.location_combo.addItem(f"🏛️ {user_state}, {user_country}", f"{user_state}, {user_country}")
            else:
                self.location_combo.addItem("⚠️ State/Province not set in profile", "")
                
        elif jurisdiction == "city":
            # Can only create topics for user's city
            if user_city and user_state and user_country:
                self.location_combo.addItem(f"🏙️ {user_city}, {user_state}, {user_country}", f"{user_city}, {user_state}, {user_country}")
            else:
                self.location_combo.addItem("⚠️ City not set in profile", "")
        
        # If no valid option, show warning
        if self.location_combo.count() == 0 or (self.location_combo.count() == 1 and not self.location_combo.itemData(0)):
            self.location_combo.setStyleSheet("QComboBox { color: #dc3545; background-color: #f8d7da; }")
        else:
            self.location_combo.setStyleSheet("")
    
    def update_character_counts(self) -> None:
        """Update character count labels"""
        title_len = len(self.title_input.text())
        desc_len = len(self.description_input.toPlainText())
        
        # Update title count with color coding
        self.title_count_label.setText(f"Characters: {title_len}/100")
        if title_len > 100:
            self.title_count_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        elif title_len > 80:
            self.title_count_label.setStyleSheet("color: #fd7e14; font-weight: bold;")
        else:
            self.title_count_label.setStyleSheet("color: #28a745; font-weight: normal;")
        
        # Update description count with color coding
        self.desc_count_label.setText(f"Characters: {desc_len}/1000")
        if desc_len > 1000:
            self.desc_count_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        elif desc_len > 800:
            self.desc_count_label.setStyleSheet("color: #fd7e14; font-weight: bold;")
        else:
            self.desc_count_label.setStyleSheet("color: #28a745; font-weight: normal;")
    
    def create_topic(self) -> None:
        """Create the debate topic with comprehensive validation"""
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.critical(self, "❌ Authentication Required", 
                               "You must be logged in to create debate topics.\n\nPlease log in and try again.")
            return
        
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()
        jurisdiction = self.jurisdiction_combo.currentText()
        location_data = self.location_combo.currentData()
        location_text = self.location_combo.currentText()
        
        # Comprehensive validation with user-friendly messages
        if not title:
            QMessageBox.warning(self, "⚠️ Missing Title", 
                              "Please enter a title for your debate topic.\n\nA good title is clear and engaging!")
            self.title_input.setFocus()
            return
        
        if len(title) > 100:
            QMessageBox.warning(self, "⚠️ Title Too Long", 
                              f"Your title is {len(title)} characters long.\n\nPlease keep it under 100 characters for better readability.")
            self.title_input.setFocus()
            return
        
        if not description:
            QMessageBox.warning(self, "⚠️ Missing Description", 
                              "Please provide a description for your debate topic.\n\nHelp people understand what they'll be debating!")
            self.description_input.setFocus()
            return
        
        if len(description) > 1000:
            QMessageBox.warning(self, "⚠️ Description Too Long", 
                              f"Your description is {len(description)} characters long.\n\nPlease keep it under 1000 characters.")
            self.description_input.setFocus()
            return
        
        if not location_data or not location_text or "⚠️" in location_text:
            QMessageBox.warning(self, "⚠️ Invalid Location", 
                              "Please ensure your profile has complete location information.\n\nYou can only create debates for your registered location.\n\nUpdate your profile in the Users tab.")
            self.location_combo.setFocus()
            return
        
        # Show confirmation dialog
        clean_location = location_text.replace('🌍 ', '').replace('🏳️ ', '').replace('🏛️ ', '').replace('🏙️ ', '')
        confirm_msg = f"""🗳️ Ready to Create Debate Topic?

📝 Title: {title}
🏛️ Jurisdiction: {jurisdiction.title()}
📍 Location: {clean_location}

Your topic will be submitted for review and made available to the community for democratic debate."""
        
        reply = QMessageBox.question(self, "✅ Confirm Topic Creation", confirm_msg,
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        if reply != QMessageBox.Yes:
            return
        
        # Show progress/loading message
        progress_msg = QMessageBox(self)
        progress_msg.setWindowTitle("⏳ Creating Topic...")
        progress_msg.setText("Please wait while we create your debate topic...")
        progress_msg.setStandardButtons(QMessageBox.NoButton)
        progress_msg.show()
        progress_msg.repaint()  # Force immediate display
        
        try:
            success, message = DebateBackend.create_topic(
                title, description, user['email'], jurisdiction, location_data or clean_location
            )
            
            progress_msg.close()
            
            if success:
                QMessageBox.information(self, "🎉 Success!", 
                                      f"Your debate topic has been created successfully!\n\n{message}\n\nIt's now available for community discussion.")
                self.accept()  # Close dialog with success
            else:
                QMessageBox.critical(self, "❌ Creation Failed", 
                                   f"We couldn't create your debate topic:\n\n{message}\n\nPlease try again or contact support.")
        except Exception as e:
            progress_msg.close()
            QMessageBox.critical(self, "❌ Unexpected Error", 
                               f"An unexpected error occurred:\n\n{str(e)}\n\nPlease try again later.")


class DebateViewer(QWidget):
    """Widget for viewing and participating in debates"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.current_topic = None
        self.init_ui()
        self.load_topics()
    
    def init_ui(self) -> None:
        main_layout = QHBoxLayout()
        
        # Left panel - topic list
        left_panel = QFrame()
        left_layout = QVBoxLayout()
        
        # Topic filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Jurisdiction:"))
        self.filter_jurisdiction = QComboBox()
        self.filter_jurisdiction.addItems(["All", "city", "state", "country"])
        self.filter_jurisdiction.currentTextChanged.connect(self.filter_topics)
        filter_layout.addWidget(self.filter_jurisdiction)
        
        filter_layout.addWidget(QLabel("Location:"))
        self.filter_location = QLineEdit()
        self.filter_location.setPlaceholderText("Filter by location")
        self.filter_location.textChanged.connect(self.filter_topics)
        filter_layout.addWidget(self.filter_location)
        
        left_layout.addLayout(filter_layout)
        
        # Create topic button
        self.create_topic_btn = QPushButton("Create New Topic")
        self.create_topic_btn.clicked.connect(self.show_create_dialog)
        left_layout.addWidget(self.create_topic_btn)
        
        # Topic list
        left_layout.addWidget(QLabel("Debate Topics:"))
        self.topic_list = QListWidget()
        self.topic_list.itemClicked.connect(self.load_topic_details)
        left_layout.addWidget(self.topic_list)
        
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(350)
        
        # Right panel - topic details and arguments
        right_panel = QFrame()
        right_layout = QVBoxLayout()
        
        # Topic details
        self.topic_details = QGroupBox("Topic Details")
        details_layout = QVBoxLayout()
        self.topic_title = QLabel("Select a topic to view details")
        self.topic_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.topic_description = QLabel("")
        self.topic_description.setWordWrap(True)
        self.topic_info = QLabel("")
        
        details_layout.addWidget(self.topic_title)
        details_layout.addWidget(self.topic_description)
        details_layout.addWidget(self.topic_info)
        self.topic_details.setLayout(details_layout)
        right_layout.addWidget(self.topic_details)
        
        # Voting section
        voting_layout = QHBoxLayout()
        self.vote_for_btn = QPushButton("Vote For")
        self.vote_against_btn = QPushButton("Vote Against")
        self.vote_neutral_btn = QPushButton("Vote Neutral")
        
        self.vote_for_btn.clicked.connect(lambda: self.cast_vote("for"))
        self.vote_against_btn.clicked.connect(lambda: self.cast_vote("against"))
        self.vote_neutral_btn.clicked.connect(lambda: self.cast_vote("neutral"))
        
        voting_layout.addWidget(self.vote_for_btn)
        voting_layout.addWidget(self.vote_against_btn)
        voting_layout.addWidget(self.vote_neutral_btn)
        right_layout.addLayout(voting_layout)
        
        # Arguments section
        self.arguments_area = QGroupBox("Arguments")
        args_layout = QVBoxLayout()
        
        # Add argument form
        add_arg_layout = QVBoxLayout()
        add_arg_layout.addWidget(QLabel("Add Your Argument:"))
        
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position:"))
        self.position_combo = QComboBox()
        self.position_combo.addItems(["for", "against", "neutral"])
        position_layout.addWidget(self.position_combo)
        position_layout.addStretch()
        add_arg_layout.addLayout(position_layout)
        
        self.argument_input = QTextEdit()
        self.argument_input.setPlaceholderText("Enter your argument here...")
        self.argument_input.setMaximumHeight(100)
        add_arg_layout.addWidget(self.argument_input)
        
        self.add_argument_btn = QPushButton("Add Argument")
        self.add_argument_btn.clicked.connect(self.add_argument)
        add_arg_layout.addWidget(self.add_argument_btn)
        
        args_layout.addLayout(add_arg_layout)
        
        # Arguments display
        self.arguments_display = QScrollArea()
        self.arguments_widget = QWidget()
        self.arguments_layout = QVBoxLayout()
        self.arguments_widget.setLayout(self.arguments_layout)
        self.arguments_display.setWidget(self.arguments_widget)
        self.arguments_display.setWidgetResizable(True)
        args_layout.addWidget(self.arguments_display)
        
        self.arguments_area.setLayout(args_layout)
        right_layout.addWidget(self.arguments_area)
        
        right_panel.setLayout(right_layout)
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 650])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
    def load_topics(self):
        """Load all debate topics"""
        self.topic_list.clear()
        topics = DebateBackend.get_topics_by_jurisdiction()
        
        for topic in topics:
            item_text = f"{topic['title']} ({topic['jurisdiction']}: {topic['location']})"
            item = self.topic_list.addItem(item_text)
            # Store topic data with the item
            self.topic_list.item(self.topic_list.count() - 1).setData(Qt.UserRole, topic)
    
    def filter_topics(self):
        """Filter topics based on jurisdiction and location"""
        jurisdiction = self.filter_jurisdiction.currentText()
        location = self.filter_location.text().strip()
        
        self.topic_list.clear()
        
        if jurisdiction == "All":
            topics = DebateBackend.get_topics_by_jurisdiction()
        else:
            topics = DebateBackend.get_topics_by_jurisdiction(jurisdiction, location if location else None)
        
        for topic in topics:
            if not location or location.lower() in topic['location'].lower():
                item_text = f"{topic['title']} ({topic['jurisdiction']}: {topic['location']})"
                self.topic_list.addItem(item_text)
                self.topic_list.item(self.topic_list.count() - 1).setData(Qt.UserRole, topic)
    
    def load_topic_details(self, item):
        """Load details for selected topic"""
        topic = item.data(Qt.UserRole)
        if not topic:
            return
        
        self.current_topic = topic
        
        # Update topic details
        self.topic_title.setText(topic['title'])
        self.topic_description.setText(topic['description'])
        
        votes = topic.get('votes', {'for': 0, 'against': 0, 'neutral': 0})
        creator_display = UserBackend.get_user_display_name(topic['creator_email'])
        info_text = f"Creator: {creator_display}\n"
        info_text += f"Jurisdiction: {topic['jurisdiction']} - {topic['location']}\n"
        info_text += f"Votes: For: {votes['for']}, Against: {votes['against']}, Neutral: {votes['neutral']}\n"
        info_text += f"Created: {topic['created_at']}"
        self.topic_info.setText(info_text)
        
        # Load arguments
        self.load_arguments()
    
    def load_arguments(self):
        """Load arguments for current topic"""
        # Clear existing arguments
        for i in reversed(range(self.arguments_layout.count())):
            self.arguments_layout.itemAt(i).widget().setParent(None)
        
        if not self.current_topic:
            return
        
        arguments = self.current_topic.get('arguments', [])
        
        for arg in arguments:
            arg_widget = QFrame()
            arg_widget.setFrameStyle(QFrame.StyledPanel)
            arg_layout = QVBoxLayout()
            
            # Argument header with author display name
            author_display = UserBackend.get_user_display_name(arg['author_email'])
            header = QLabel(f"{arg['position'].upper()} - {author_display} - {arg['created_at']}")
            header.setStyleSheet("font-weight: bold; background-color: #f0f0f0; padding: 5px;")
            arg_layout.addWidget(header)
            
            # Argument content
            content = QLabel(arg['content'])
            content.setWordWrap(True)
            content.setMargin(10)
            arg_layout.addWidget(content)
            
            arg_widget.setLayout(arg_layout)
            self.arguments_layout.addWidget(arg_widget)
    
    def show_create_dialog(self):
        """Show user-friendly create topic dialog"""
        # Check if user is logged in first
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "🔒 Login Required", 
                              "You must be logged in to create debate topics.\n\nPlease log in first and try again.")
            return
        
        # Create and show the modal dialog
        dialog = CreateTopicDialog(self)
        result = dialog.exec_()  # Use exec_() for modal dialog
        
        # If topic was created successfully, refresh the topic list
        if result == QDialog.Accepted:
            self.load_topics()  # Refresh the topic list
            QMessageBox.information(self, "🔄 Topics Updated", 
                                  "The topic list has been refreshed with your new topic!")
    
    def cast_vote(self, vote):
        """Cast a vote on current topic"""
        if not self.current_topic:
            QMessageBox.warning(self, "No Topic", "Please select a topic first")
            return
        
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Required", "Please log in to vote")
            return
        
        success, message = DebateBackend.vote_on_topic(
            self.current_topic['id'], user['email'], vote
        )
        
        if success:
            QMessageBox.information(self, "Vote Cast", message)
            # Refresh topic details
            updated_topic = DebateBackend.get_topic_by_id(self.current_topic['id'])
            if updated_topic:
                self.current_topic = updated_topic
                self.load_topic_details(self.topic_list.currentItem())
        else:
            QMessageBox.warning(self, "Vote Failed", message)
    
    def add_argument(self):
        """Add an argument to current topic"""
        if not self.current_topic:
            QMessageBox.warning(self, "No Topic", "Please select a topic first")
            return
        
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Required", "Please log in to add arguments")
            return
        
        content = self.argument_input.toPlainText().strip()
        position = self.position_combo.currentText()
        
        if not content:
            QMessageBox.warning(self, "Missing Content", "Please enter your argument")
            return
        
        success, message = DebateBackend.add_argument(
            self.current_topic['id'], content, position, user['email']
        )
        
        if success:
            QMessageBox.information(self, "Argument Added", message)
            self.argument_input.clear()
            # Refresh arguments
            updated_topic = DebateBackend.get_topic_by_id(self.current_topic['id'])
            if updated_topic:
                self.current_topic = updated_topic
                self.load_arguments()
        else:
            QMessageBox.warning(self, "Failed", message)