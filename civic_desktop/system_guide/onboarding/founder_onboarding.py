# Founder Onboarding Module
# Interactive onboarding for Contract Founders

from .tutorials import show_tutorial, show_help
from .progress import ProgressTracker, CompetencyScorer
from .support import Troubleshooter

class FounderOnboarding:
    def __init__(self, user):
        self.user = user
        self.progress = ProgressTracker(user, role='Founder')
        self.scorer = CompetencyScorer(user, role='Founder')
        self.troubleshooter = Troubleshooter(user)

    def start(self):
        show_tutorial('founder_intro')
        self.progress.checkpoint('Welcome')
        show_help('founder_dashboard')
        self.progress.checkpoint('Dashboard Tour')
        show_tutorial('founder_emergency')
        self.progress.checkpoint('Emergency Protocols')
        self.scorer.score('emergency_quiz')
        show_tutorial('founder_appointments')
        self.progress.checkpoint('Appointment Authority')
        self.troubleshooter.run()
        self.progress.complete()
