"""
Contract Amendment UI System
User interface components for the hierarchical contract amendment system.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLabel, QPushButton, QTextEdit, QComboBox, 
                             QTableWidget, QTableWidgetItem, QDialog,
                             QFormLayout, QLineEdit, QMessageBox, QProgressBar,
                             QSplitter, QGroupBox, QRadioButton, QButtonGroup,
                             QScrollArea, QFrame, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from datetime import datetime, timezone

from .amendment_system import (ContractAmendmentManager, AmendmentProposal, 
                              JurisdictionLevel, AmendmentStatus, ChangeType)

class AmendmentProposalDialog(QDialog):
    """Dialog for creating new amendment proposals"""
    
    def __init__(self, parent=None, user_email="", user_name="", user_jurisdiction=""):
        super().__init__(parent)
        self.user_email = user_email
        self.user_name = user_name
        self.user_jurisdiction = user_jurisdiction
        
        self.setWindowTitle("Propose Contract Amendment")
        self.setModal(True)
        self.resize(700, 600)
        
        self.amendment_manager = ContractAmendmentManager()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<h2>Propose Constitutional Amendment</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        
        # Article Section
        self.article_section_edit = QLineEdit()
        self.article_section_edit.setPlaceholderText("e.g., ARTICLE I.1.A or ARTICLE IV.2")
        form_layout.addRow("Article Section:", self.article_section_edit)
        
        # Change Type
        self.change_type_combo = QComboBox()
        for change_type in ChangeType:
            self.change_type_combo.addItem(change_type.value.title(), change_type)
        form_layout.addRow("Change Type:", self.change_type_combo)
        
        # Current Text
        self.current_text_edit = QTextEdit()
        self.current_text_edit.setMaximumHeight(100)
        self.current_text_edit.setPlaceholderText("Enter the current text you want to change...")
        form_layout.addRow("Current Text:", self.current_text_edit)
        
        # Proposed Text
        self.proposed_text_edit = QTextEdit()
        self.proposed_text_edit.setMaximumHeight(100)
        self.proposed_text_edit.setPlaceholderText("Enter your proposed new text...")
        form_layout.addRow("Proposed Text:", self.proposed_text_edit)
        
        # Rationale
        self.rationale_edit = QTextEdit()
        self.rationale_edit.setMaximumHeight(120)
        self.rationale_edit.setPlaceholderText("Explain why this change is needed and how it will benefit the community...")
        form_layout.addRow("Rationale:", self.rationale_edit)
        
        # Jurisdiction Level
        self.jurisdiction_combo = QComboBox()
        self.jurisdiction_combo.addItem("City/Town", JurisdictionLevel.CITY)
        self.jurisdiction_combo.addItem("State/Province", JurisdictionLevel.STATE)
        self.jurisdiction_combo.addItem("Country", JurisdictionLevel.COUNTRY)
        self.jurisdiction_combo.addItem("World", JurisdictionLevel.WORLD)
        form_layout.addRow("Starting Level:", self.jurisdiction_combo)
        
        # Jurisdiction Name
        self.jurisdiction_name_edit = QLineEdit()
        self.jurisdiction_name_edit.setText(self.user_jurisdiction)
        self.jurisdiction_name_edit.setPlaceholderText("e.g., Springfield, Illinois")
        form_layout.addRow("Jurisdiction Name:", self.jurisdiction_name_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        submit_btn = QPushButton("Submit Proposal")
        submit_btn.clicked.connect(self.submit_proposal)
        button_layout.addWidget(submit_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)

    def submit_proposal(self):
        """Submit the amendment proposal"""
        # Validate inputs
        if not all([
            self.article_section_edit.text().strip(),
            self.current_text_edit.toPlainText().strip(),
            self.proposed_text_edit.toPlainText().strip(),
            self.rationale_edit.toPlainText().strip(),
            self.jurisdiction_name_edit.text().strip()
        ]):
            QMessageBox.warning(self, "Incomplete Form", 
                              "Please fill in all required fields.")
            return
        
        try:
            # Submit proposal
            amendment_id = self.amendment_manager.propose_amendment(
                proposer_email=self.user_email,
                proposer_name=self.user_name,
                article_section=self.article_section_edit.text().strip(),
                change_type=self.change_type_combo.currentData(),
                current_text=self.current_text_edit.toPlainText().strip(),
                proposed_text=self.proposed_text_edit.toPlainText().strip(),
                rationale=self.rationale_edit.toPlainText().strip(),
                jurisdiction_level=self.jurisdiction_combo.currentData(),
                jurisdiction_name=self.jurisdiction_name_edit.text().strip()
            )
            
            QMessageBox.information(self, "Proposal Submitted", 
                                  f"Your amendment proposal has been submitted!\n\n"
                                  f"Amendment ID: {amendment_id}\n"
                                  f"It will now go through the local debate and approval process.")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to submit proposal: {str(e)}")

class AmendmentDetailDialog(QDialog):
    """Dialog showing detailed view of an amendment"""
    
    def __init__(self, amendment: AmendmentProposal, parent=None):
        super().__init__(parent)
        self.amendment = amendment
        self.amendment_manager = ContractAmendmentManager()
        
        self.setWindowTitle(f"Amendment Details - {amendment.id}")
        self.setModal(True)
        self.resize(800, 700)
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"<h2>Amendment {self.amendment.id}</h2>")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Main content in tabs
        tabs = QTabWidget()
        
        # Details tab
        details_tab = self.create_details_tab()
        tabs.addTab(details_tab, "📋 Details")
        
        # Voting tab
        voting_tab = self.create_voting_tab()
        tabs.addTab(voting_tab, "🗳️ Voting")
        
        # Comments/Debate tab
        comments_tab = self.create_comments_tab()
        tabs.addTab(comments_tab, "💬 Debate")
        
        # History tab
        history_tab = self.create_history_tab()
        tabs.addTab(history_tab, "📚 History")
        
        layout.addWidget(tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        if self.amendment.status == AmendmentStatus.SUBMITTED:
            start_debate_btn = QPushButton("Start Local Debate")
            start_debate_btn.clicked.connect(self.start_debate)
            button_layout.addWidget(start_debate_btn)
        
        if self.amendment.status == AmendmentStatus.LOCAL_DEBATE:
            start_voting_btn = QPushButton("Start Voting Period")
            start_voting_btn.clicked.connect(self.start_voting)
            button_layout.addWidget(start_voting_btn)
        
        if (self.amendment.status == AmendmentStatus.LOCAL_APPROVED and 
            self.amendment.escalation_eligible_date and
            datetime.now(timezone.utc) >= self.amendment.escalation_eligible_date):
            escalate_btn = QPushButton("Escalate to Next Level")
            escalate_btn.clicked.connect(self.escalate_amendment)
            button_layout.addWidget(escalate_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)

    def create_details_tab(self) -> QWidget:
        """Create the details tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Amendment info
        info_group = QGroupBox("Amendment Information")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("ID:", QLabel(self.amendment.id))
        info_layout.addRow("Proposer:", QLabel(f"{self.amendment.proposer_name} ({self.amendment.proposer_email})"))
        info_layout.addRow("Article Section:", QLabel(self.amendment.article_section))
        info_layout.addRow("Change Type:", QLabel(self.amendment.change_type.value.title()))
        info_layout.addRow("Status:", QLabel(self.amendment.status.value.replace('_', ' ').title()))
        info_layout.addRow("Jurisdiction:", QLabel(f"{self.amendment.jurisdiction_level.value.title()}: {self.amendment.jurisdiction_name}"))
        info_layout.addRow("Created:", QLabel(self.amendment.created_at.strftime("%Y-%m-%d %H:%M UTC")))
        
        layout.addWidget(info_group)
        
        # Text comparison
        text_group = QGroupBox("Proposed Changes")
        text_layout = QVBoxLayout(text_group)
        
        # Current text
        text_layout.addWidget(QLabel("<b>Current Text:</b>"))
        current_text = QTextEdit()
        current_text.setPlainText(self.amendment.current_text)
        current_text.setReadOnly(True)
        current_text.setMaximumHeight(100)
        text_layout.addWidget(current_text)
        
        # Proposed text
        text_layout.addWidget(QLabel("<b>Proposed Text:</b>"))
        proposed_text = QTextEdit()
        proposed_text.setPlainText(self.amendment.proposed_text)
        proposed_text.setReadOnly(True)
        proposed_text.setMaximumHeight(100)
        text_layout.addWidget(proposed_text)
        
        # Rationale
        text_layout.addWidget(QLabel("<b>Rationale:</b>"))
        rationale = QTextEdit()
        rationale.setPlainText(self.amendment.rationale)
        rationale.setReadOnly(True)
        rationale.setMaximumHeight(100)
        text_layout.addWidget(rationale)
        
        layout.addWidget(text_group)
        
        return widget

    def create_voting_tab(self) -> QWidget:
        """Create the voting tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Voting status
        status_group = QGroupBox("Voting Status")
        status_layout = QVBoxLayout(status_group)
        
        if self.amendment.status in [AmendmentStatus.LOCAL_VOTING, AmendmentStatus.LOCAL_APPROVED, AmendmentStatus.LOCAL_REJECTED]:
            # Progress bar
            total_votes = self.amendment.votes_for + self.amendment.votes_against + self.amendment.votes_abstain
            if self.amendment.total_eligible_voters > 0:
                participation = (total_votes / self.amendment.total_eligible_voters) * 100
                progress = QProgressBar()
                progress.setMaximum(100)
                progress.setValue(int(participation))
                progress.setFormat(f"Participation: {participation:.1f}% ({total_votes}/{self.amendment.total_eligible_voters})")
                status_layout.addWidget(progress)
            
            # Vote breakdown
            vote_layout = QHBoxLayout()
            
            for_votes = QLabel(f"✅ For: {self.amendment.votes_for}")
            for_votes.setStyleSheet("color: green; font-weight: bold;")
            vote_layout.addWidget(for_votes)
            
            against_votes = QLabel(f"❌ Against: {self.amendment.votes_against}")  
            against_votes.setStyleSheet("color: red; font-weight: bold;")
            vote_layout.addWidget(against_votes)
            
            abstain_votes = QLabel(f"⚪ Abstain: {self.amendment.votes_abstain}")
            abstain_votes.setStyleSheet("color: gray; font-weight: bold;")
            vote_layout.addWidget(abstain_votes)
            
            status_layout.addLayout(vote_layout)
            
            # Approval percentage
            decisive_votes = self.amendment.votes_for + self.amendment.votes_against
            if decisive_votes > 0:
                approval_pct = (self.amendment.votes_for / decisive_votes) * 100
                approval_label = QLabel(f"Approval: {approval_pct:.1f}% (50% required)")
                if approval_pct >= 50:
                    approval_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
                else:
                    approval_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
                status_layout.addWidget(approval_label)
        
        else:
            status_layout.addWidget(QLabel("Voting has not started yet."))
        
        layout.addWidget(status_group)
        
        # Voting interface (if voting is active)
        if self.amendment.status == AmendmentStatus.LOCAL_VOTING:
            vote_group = QGroupBox("Cast Your Vote")
            vote_layout = QVBoxLayout(vote_group)
            
            # Vote options
            self.vote_group = QButtonGroup()
            
            for_radio = QRadioButton("✅ Vote FOR this amendment")
            against_radio = QRadioButton("❌ Vote AGAINST this amendment")
            abstain_radio = QRadioButton("⚪ ABSTAIN from voting")
            
            self.vote_group.addButton(for_radio, 1)
            self.vote_group.addButton(against_radio, 2)
            self.vote_group.addButton(abstain_radio, 3)
            
            vote_layout.addWidget(for_radio)
            vote_layout.addWidget(against_radio)
            vote_layout.addWidget(abstain_radio)
            
            # Submit vote button
            submit_vote_btn = QPushButton("Submit Vote")
            submit_vote_btn.clicked.connect(self.submit_vote)
            vote_layout.addWidget(submit_vote_btn)
            
            layout.addWidget(vote_group)
        
        return widget

    def create_comments_tab(self) -> QWidget:
        """Create the comments/debate tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Comments list
        comments_group = QGroupBox("Debate Comments")
        comments_layout = QVBoxLayout(comments_group)
        
        comments_scroll = QScrollArea()
        comments_widget = QWidget()
        comments_list_layout = QVBoxLayout(comments_widget)
        
        for comment in self.amendment.comments:
            comment_frame = QFrame()
            comment_frame.setFrameStyle(QFrame.Box)
            comment_layout = QVBoxLayout(comment_frame)
            
            # Header with commenter and timestamp
            header = QLabel(f"<b>{comment.get('commenter_name', 'Anonymous')}</b> - {comment.get('timestamp', 'Unknown time')}")
            if comment.get('is_support') is True:
                header.setStyleSheet("color: green;")
            elif comment.get('is_support') is False:
                header.setStyleSheet("color: red;")
            comment_layout.addWidget(header)
            
            # Comment text
            text = QLabel(comment.get('comment_text', ''))
            text.setWordWrap(True)
            comment_layout.addWidget(text)
            
            comments_list_layout.addWidget(comment_frame)
        
        if not self.amendment.comments:
            no_comments = QLabel("No comments yet.")
            no_comments.setAlignment(Qt.AlignCenter)
            no_comments.setStyleSheet("color: gray; font-style: italic;")
            comments_list_layout.addWidget(no_comments)
        
        comments_scroll.setWidget(comments_widget)
        comments_layout.addWidget(comments_scroll)
        
        layout.addWidget(comments_group)
        
        # Add comment interface (if debate is active)
        if self.amendment.status in [AmendmentStatus.LOCAL_DEBATE, AmendmentStatus.LOCAL_VOTING]:
            add_comment_group = QGroupBox("Add Your Comment")
            add_comment_layout = QVBoxLayout(add_comment_group)
            
            # Position buttons
            position_layout = QHBoxLayout()
            self.comment_position_group = QButtonGroup()
            
            support_radio = QRadioButton("I support this amendment")
            oppose_radio = QRadioButton("I oppose this amendment")
            neutral_radio = QRadioButton("Neutral/Questions only")
            
            self.comment_position_group.addButton(support_radio, 1)
            self.comment_position_group.addButton(oppose_radio, 2)
            self.comment_position_group.addButton(neutral_radio, 3)
            
            position_layout.addWidget(support_radio)
            position_layout.addWidget(oppose_radio)
            position_layout.addWidget(neutral_radio)
            
            add_comment_layout.addLayout(position_layout)
            
            # Comment text
            self.comment_text = QTextEdit()
            self.comment_text.setPlaceholderText("Share your thoughts, questions, or concerns about this amendment...")
            self.comment_text.setMaximumHeight(100)
            add_comment_layout.addWidget(self.comment_text)
            
            # Submit button
            submit_comment_btn = QPushButton("Add Comment")
            submit_comment_btn.clicked.connect(self.submit_comment)
            add_comment_layout.addWidget(submit_comment_btn)
            
            layout.addWidget(add_comment_group)
        
        return widget

    def create_history_tab(self) -> QWidget:
        """Create the history tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        history_group = QGroupBox("Amendment Progress History")
        history_layout = QVBoxLayout(history_group)
        
        # Timeline
        for entry in self.amendment.approval_history:
            entry_frame = QFrame()
            entry_frame.setFrameStyle(QFrame.Box)
            entry_layout = QVBoxLayout(entry_frame)
            
            # Header
            level = entry.get('level', 'Unknown').title()
            jurisdiction = entry.get('jurisdiction', 'Unknown')
            date = entry.get('approved_date', 'Unknown date')
            
            header = QLabel(f"<b>✅ Approved at {level} Level</b>")
            header.setStyleSheet("color: green; font-size: 14px;")
            entry_layout.addWidget(header)
            
            # Details
            details = QLabel(f"Jurisdiction: {jurisdiction}\nDate: {date}")
            entry_layout.addWidget(details)
            
            # Vote breakdown
            votes_for = entry.get('votes_for', 0)
            votes_against = entry.get('votes_against', 0)
            approval_pct = entry.get('approval_percentage', 0) * 100
            
            votes_label = QLabel(f"Votes: {votes_for} for, {votes_against} against ({approval_pct:.1f}% approval)")
            entry_layout.addWidget(votes_label)
            
            history_layout.addWidget(entry_frame)
        
        if not self.amendment.approval_history:
            no_history = QLabel("No approval history yet.")
            no_history.setAlignment(Qt.AlignCenter)
            no_history.setStyleSheet("color: gray; font-style: italic;")
            history_layout.addWidget(no_history)
        
        layout.addWidget(history_group)
        
        return widget

    def start_debate(self):
        """Start the local debate period"""
        success = self.amendment_manager.start_local_debate(self.amendment.id)
        if success:
            QMessageBox.information(self, "Debate Started", 
                                  "The local debate period has begun! Citizens can now comment and discuss this amendment.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to start debate period.")

    def start_voting(self):
        """Start the voting period"""
        success = self.amendment_manager.start_voting_period(self.amendment.id)
        if success:
            QMessageBox.information(self, "Voting Started", 
                                  "The voting period has begun! Citizens can now vote on this amendment.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to start voting period.")

    def submit_vote(self):
        """Submit a vote"""
        selected = self.vote_group.checkedId()
        if selected == -1:
            QMessageBox.warning(self, "No Selection", "Please select your vote option.")
            return
        
        vote_map = {1: 'for', 2: 'against', 3: 'abstain'}
        vote = vote_map[selected]
        
        # In a real system, would get actual user email
        success = self.amendment_manager.cast_vote(self.amendment.id, "current_user@example.com", vote)
        
        if success:
            QMessageBox.information(self, "Vote Recorded", f"Your vote ({vote}) has been recorded!")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to record your vote.")

    def submit_comment(self):
        """Submit a comment"""
        comment_text = self.comment_text.toPlainText().strip()
        if not comment_text:
            QMessageBox.warning(self, "Empty Comment", "Please enter a comment.")
            return
        
        position_id = self.comment_position_group.checkedId()
        is_support = None
        if position_id == 1:
            is_support = True
        elif position_id == 2:
            is_support = False
        
        # In a real system, would get actual user info
        success = self.amendment_manager.add_comment(
            self.amendment.id, 
            "current_user@example.com",
            "Current User",
            comment_text,
            is_support
        )
        
        if success:
            QMessageBox.information(self, "Comment Added", "Your comment has been added to the debate!")
            self.comment_text.clear()
            self.comment_position_group.setExclusive(False)
            for button in self.comment_position_group.buttons():
                button.setChecked(False)
            self.comment_position_group.setExclusive(True)
        else:
            QMessageBox.warning(self, "Error", "Failed to add your comment.")

    def escalate_amendment(self):
        """Escalate amendment to next level"""
        success = self.amendment_manager.escalate_amendment(self.amendment.id)
        if success:
            QMessageBox.information(self, "Amendment Escalated", 
                                  "This amendment has been escalated to the next jurisdiction level!")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to escalate amendment.")

class ContractAmendmentTab(QWidget):
    """Main tab widget for contract amendments"""
    
    def __init__(self):
        super().__init__()
        self.amendment_manager = ContractAmendmentManager()
        self.user_email = "current_user@example.com"  # Would get from session
        self.user_name = "Current User"  # Would get from session
        self.user_jurisdiction = "Example City, Example State"  # Would get from user profile
        
        self.setup_ui()
        self.refresh_amendments()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("<h1>📜 Contract Amendment System</h1>")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Description
        description = QLabel(
            "Propose and vote on constitutional amendments through hierarchical governance. "
            "Amendments start at the local level and can progress through City → State → Country → World levels."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-style: italic; color: gray; margin: 10px;")
        layout.addWidget(description)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        propose_btn = QPushButton("📝 Propose Amendment")
        propose_btn.clicked.connect(self.propose_amendment)
        controls_layout.addWidget(propose_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_amendments)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Amendments table
        self.amendments_table = QTableWidget()
        self.amendments_table.setColumnCount(8)
        self.amendments_table.setHorizontalHeaderLabels([
            "ID", "Article", "Type", "Status", "Jurisdiction", "Proposer", "Created", "Action"
        ])
        self.amendments_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Make amendments table read-only to prevent editing of reports
        self.amendments_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.amendments_table)

    def propose_amendment(self):
        """Open dialog to propose new amendment"""
        dialog = AmendmentProposalDialog(self, self.user_email, self.user_name, self.user_jurisdiction)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_amendments()

    def refresh_amendments(self):
        """Refresh the amendments table"""
        self.amendment_manager.load_amendments()
        amendments = list(self.amendment_manager.amendments.values())
        
        self.amendments_table.setRowCount(len(amendments))
        
        for row, amendment in enumerate(amendments):
            # ID
            id_item = QTableWidgetItem(amendment.id)
            self.amendments_table.setItem(row, 0, id_item)
            
            # Article
            article_item = QTableWidgetItem(amendment.article_section)
            self.amendments_table.setItem(row, 1, article_item)
            
            # Type
            type_item = QTableWidgetItem(amendment.change_type.value.title())
            self.amendments_table.setItem(row, 2, type_item)
            
            # Status
            status_item = QTableWidgetItem(amendment.status.value.replace('_', ' ').title())
            if amendment.status in [AmendmentStatus.LOCAL_APPROVED, AmendmentStatus.IMPLEMENTED]:
                status_item.setBackground(Qt.green)
            elif amendment.status in [AmendmentStatus.LOCAL_REJECTED, AmendmentStatus.REJECTED]:
                status_item.setBackground(Qt.red)
            elif amendment.status == AmendmentStatus.LOCAL_VOTING:
                status_item.setBackground(Qt.yellow)
            self.amendments_table.setItem(row, 3, status_item)
            
            # Jurisdiction
            jurisdiction_item = QTableWidgetItem(f"{amendment.jurisdiction_level.value.title()}: {amendment.jurisdiction_name}")
            self.amendments_table.setItem(row, 4, jurisdiction_item)
            
            # Proposer
            proposer_item = QTableWidgetItem(amendment.proposer_name)
            self.amendments_table.setItem(row, 5, proposer_item)
            
            # Created
            created_item = QTableWidgetItem(amendment.created_at.strftime("%Y-%m-%d"))
            self.amendments_table.setItem(row, 6, created_item)
            
            # Action button
            view_btn = QPushButton("View Details")
            view_btn.clicked.connect(lambda checked, a=amendment: self.view_amendment(a))
            self.amendments_table.setCellWidget(row, 7, view_btn)
        
        # Resize columns to content
        self.amendments_table.resizeColumnsToContents()

    def view_amendment(self, amendment: AmendmentProposal):
        """View amendment details"""
        dialog = AmendmentDetailDialog(amendment, self)
        dialog.exec_()