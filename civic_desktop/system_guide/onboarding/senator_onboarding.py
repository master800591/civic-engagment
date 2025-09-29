# Senator Onboarding Module
# Interactive onboarding for Contract Senators

from .tutorials import show_tutorial, show_help
from .progress import ProgressTracker, CompetencyScorer
from .support import Troubleshooter

class SenatorOnboarding:
    def __init__(self, user):
        self.user = user
        self.progress = ProgressTracker(user, role='Senator')
        self.scorer = CompetencyScorer(user, role='Senator')
        self.troubleshooter = Troubleshooter(user)

    def start(self):
        show_tutorial('senator_intro')
        self.progress.checkpoint('Welcome')
        show_help('senator_dashboard')
        self.progress.checkpoint('Dashboard Tour')
        show_tutorial('senator_review')
        self.progress.checkpoint('Legislative Review')
        self.scorer.score('review_quiz')
        show_tutorial('senator_confirmation')
        self.progress.checkpoint('Confirmation Authority')
        self.troubleshooter.run()
        self.progress.complete()
