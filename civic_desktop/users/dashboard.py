from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QGroupBox, 
    QHBoxLayout, QProgressBar, QScrollArea
)
from PyQt5.QtCore import Qt
from .session import SessionManager
from .election_ui import ElectionWidget
from .elections import ElectionManager
from .rank_manager import RankManager
from .constants import USER_ROLES

class UserDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Dashboard")
        self.layout = QVBoxLayout()
        self.info_label = QLabel()
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.logout_button)
        self.setLayout(self.layout)
        self.candidate_buttons = []
        self.election_widgets = []
        self.refresh()

    def refresh(self):
        user = SessionManager.get_current_user()
        
        # Remove old widgets
        for btn in getattr(self, 'candidate_buttons', []):
            self.layout.removeWidget(btn)
            btn.deleteLater()
        for ew in getattr(self, 'election_widgets', []):
            self.layout.removeWidget(ew)
            ew.deleteLater()
        self.candidate_buttons = []
        self.election_widgets = []
        
        if user:
            # Enhanced user info with rank status
            self.update_user_info_display(user)
            
            # Add rank progression section
            self.add_rank_progression_section(user)
            
            # Show elections (existing functionality)
            self.add_elections_section(user)
        else:
            self.info_label.setText("Not logged in.")

    def update_user_info_display(self, user):
        """Update user info display with rank information"""
        role = user.get('role', 'Unknown')
        rank_info = USER_ROLES.get(role, {})
        level = rank_info.get('level', 0)
        
        # Create status indicator based on rank
        if role == "Junior Contract Citizen":
            status_icon = "👤"
            status_text = "Junior Citizen (Under 18)"
        elif role == "Prospect Contract Citizen":
            status_icon = "📋"
            status_text = "Prospect Citizen (Verification Pending)"
        elif role == "Probation Contract Citizen":
            status_icon = "🎓"
            status_text = "Probation Citizen (Training Required)"
        elif role == "Contract Citizen":
            status_icon = "✅"
            status_text = "Contract Citizen (Full Access)"
        else:
            status_icon = "🏛️"
            status_text = role
        
        info_text = f"""
        <h3>{status_icon} {status_text}</h3>
        <p><strong>Name:</strong> {user['first_name']} {user['last_name']}</p>
        <p><strong>Email:</strong> {user['email']}</p>
        <p><strong>Level:</strong> {level}/8</p>
        <p><strong>All Roles:</strong> {', '.join(user.get('roles', []))}</p>
        """
        
        self.info_label.setText(info_text)

    def add_rank_progression_section(self, user):
        """Add rank progression information and requirements"""
        rank_group = QGroupBox("🎯 Rank Progression")
        rank_layout = QVBoxLayout()
        
        # Get progression requirements
        requirements = RankManager.get_next_rank_requirements(user['email'])
        
        if requirements.get('next_rank'):
            next_rank = requirements['next_rank']
            req_list = requirements.get('requirements', [])
            
            # Show next rank info
            next_rank_label = QLabel(f"<h4>Next Rank: {next_rank}</h4>")
            rank_layout.addWidget(next_rank_label)
            
            if req_list:
                requirements_label = QLabel("<strong>Requirements to complete:</strong>")
                rank_layout.addWidget(requirements_label)
                
                for req in req_list:
                    req_label = QLabel(f"• {req}")
                    req_label.setWordWrap(True)
                    rank_layout.addWidget(req_label)
            
            # Add promotion check button
            check_promotion_btn = QPushButton("Check for Promotion")
            check_promotion_btn.clicked.connect(self.check_promotion)
            rank_layout.addWidget(check_promotion_btn)
        else:
            message = requirements.get('message', 'No promotion available')
            status_label = QLabel(f"<em>{message}</em>")
            rank_layout.addWidget(status_label)
        
        # Show verification status for lower ranks
        current_role = user.get('role', '')
        if current_role in ["Prospect Contract Citizen", "Probation Contract Citizen"]:
            self.add_verification_status(user, rank_layout)
        
        rank_group.setLayout(rank_layout)
        self.layout.addWidget(rank_group)

    def add_verification_status(self, user, layout):
        """Add verification status indicators"""
        verification_group = QGroupBox("📋 Verification Status")
        verification_layout = QVBoxLayout()
        
        verifications = [
            ("Identity", user.get('identity_verified', False)),
            ("Address", user.get('address_verified', False)),
            ("Email", user.get('email_verified', False))
        ]
        
        for name, status in verifications:
            status_text = "✅ Complete" if status else "⏳ Pending"
            color = "green" if status else "orange"
            
            status_label = QLabel(f"<span style='color: {color}'>{name}: {status_text}</span>")
            verification_layout.addWidget(status_label)
        
        verification_group.setLayout(verification_layout)
        layout.addWidget(verification_group)

    def add_elections_section(self, user):
        """Add elections section (existing functionality)"""
        for jur in ['city', 'state', 'country']:
            elections = [e for e in ElectionManager.load_elections() 
                        if e['jurisdiction'] == jur and e['value'] == user[jur] and e['status'] == 'open']
            
            for election in elections:
                ew = ElectionWidget(jur, user[jur], election['role'])
                self.layout.addWidget(ew)
                self.election_widgets.append(ew)
                
                # Add candidate button if not already a candidate
                if user['email'] not in election['candidates']:
                    btn = QPushButton(f"Nominate Myself for {election['role']} in {user[jur]}")
                    btn.clicked.connect(lambda _, eid=election['id'], email=user['email']: 
                                      self.nominate_self(eid, email))
                    self.layout.addWidget(btn)
                    self.candidate_buttons.append(btn)

    def check_promotion(self):
        """Check if user can be promoted and handle promotion"""
        user = SessionManager.get_current_user()
        if not user:
            return
        
        next_rank, reason = RankManager.check_promotion_eligibility(user['email'])
        
        if next_rank:
            reply = QMessageBox.question(
                self, 
                "Promotion Available",
                f"You are eligible for promotion to {next_rank}!\n\nReason: {reason}\n\nWould you like to be promoted now?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = RankManager.promote_user(user['email'], next_rank, reason)
                if success:
                    QMessageBox.information(
                        self, 
                        "Promotion Successful",
                        f"Congratulations! You have been promoted to {next_rank}."
                    )
                    # Update session and refresh dashboard
                    SessionManager.refresh_user_session()
                    self.refresh()
                else:
                    QMessageBox.warning(
                        self, 
                        "Promotion Failed",
                        "There was an error processing your promotion. Please try again."
                    )
        else:
            QMessageBox.information(
                self, 
                "No Promotion Available",
                f"Current status: {reason}"
            )

    def logout(self):
        SessionManager.logout()
        self.refresh()

    def nominate_self(self, election_id, user_email):
        ElectionManager.add_candidate(election_id, user_email)
        QMessageBox.information(self, "Nominated", "You have been nominated as a candidate.")
        self.refresh()
