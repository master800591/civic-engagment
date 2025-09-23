from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from .session import SessionManager
from .election_ui import ElectionWidget
from .elections import ElectionManager

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
        # Remove old election widgets/buttons
        for btn in getattr(self, 'candidate_buttons', []):
            self.layout.removeWidget(btn)
            btn.deleteLater()
        for ew in getattr(self, 'election_widgets', []):
            self.layout.removeWidget(ew)
            ew.deleteLater()
        self.candidate_buttons = []
        self.election_widgets = []
        if user:
            self.info_label.setText(f"Logged in as: {user['first_name']} {user['last_name']}\nEmail: {user['email']}\nRoles: {', '.join(user.get('roles', []))}")
            # Show open elections for user's jurisdictions
            for jur in ['city', 'state', 'country']:
                elections = [e for e in ElectionManager.load_elections() if e['jurisdiction'] == jur and e['value'] == user[jur] and e['status'] == 'open']
                for election in elections:
                    ew = ElectionWidget(jur, user[jur], election['role'])
                    self.layout.addWidget(ew)
                    self.election_widgets.append(ew)
                    # Add candidate button if not already a candidate
                    if user['email'] not in election['candidates']:
                        btn = QPushButton(f"Nominate Myself for {election['role']} in {user[jur]}")
                        btn.clicked.connect(lambda _, eid=election['id'], email=user['email']: self.nominate_self(eid, email))
                        self.layout.addWidget(btn)
                        self.candidate_buttons.append(btn)
        else:
            self.info_label.setText("Not logged in.")

    def logout(self):
        SessionManager.logout()
        self.refresh()

    def nominate_self(self, election_id, user_email):
        ElectionManager.add_candidate(election_id, user_email)
        QMessageBox.information(self, "Nominated", "You have been nominated as a candidate.")
        self.refresh()
