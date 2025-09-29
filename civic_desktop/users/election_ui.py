from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QLineEdit, QMessageBox
from .elections import ElectionManager
from .session import SessionManager

class ElectionWidget(QWidget):
    def __init__(self, jur, value, role, parent=None):
        super().__init__(parent)
        self.jur = jur
        self.value = value
        self.role = role
        self.election_id = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"{self.jur.title()} {self.value} {self.role.title()} Election")
        layout = QVBoxLayout()
        self.candidate_list = QListWidget()
        self.vote_input = QLineEdit()
        self.vote_input.setPlaceholderText("Enter candidate email to vote")
        self.vote_button = QPushButton("Vote")
        self.vote_button.clicked.connect(self.cast_vote)
        self.refresh_button = QPushButton("Refresh Candidates")
        self.refresh_button.clicked.connect(self.refresh_candidates)
        layout.addWidget(QLabel(f"Election for {self.role} in {self.value} ({self.jur})"))
        layout.addWidget(self.candidate_list)
        layout.addWidget(self.vote_input)
        layout.addWidget(self.vote_button)
        layout.addWidget(self.refresh_button)
        self.setLayout(layout)
        self.refresh_candidates()

    def refresh_candidates(self):
        # Find the open election for this jurisdiction/role
        for election in ElectionManager.load_elections():
            if (election['jurisdiction'] == self.jur and election['value'] == self.value and
                election['role'] == self.role and election['status'] == 'open'):
                self.election_id = election['id']
                self.candidate_list.clear()
                for c in election['candidates']:
                    self.candidate_list.addItem(c)
                return
        self.candidate_list.clear()
        self.candidate_list.addItem("No open election.")

    def cast_vote(self):
        if not self.election_id:
            QMessageBox.warning(self, "No Election", "No open election to vote in.")
            return
        candidate_email = self.vote_input.text().strip()
        if not candidate_email:
            QMessageBox.warning(self, "Missing", "Enter a candidate email.")
            return
        
        # Get current authenticated user
        current_user = SessionManager.get_current_user()
        if not current_user:
            QMessageBox.warning(self, "Authentication Required", "Please log in to vote.")
            return
        
        voter_email = current_user['email']
        ElectionManager.cast_vote(self.election_id, voter_email, candidate_email)
        QMessageBox.information(self, "Vote Cast", f"Vote for {candidate_email} submitted.")
        self.vote_input.clear()
