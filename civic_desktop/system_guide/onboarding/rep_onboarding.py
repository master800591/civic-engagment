# Representative Onboarding Module
# Interactive onboarding for Contract Representatives

from .tutorials import show_tutorial, show_help
from .progress import ProgressTracker, CompetencyScorer
from .support import Troubleshooter

class RepOnboarding:
    def __init__(self, user):
        self.user = user
        self.progress = ProgressTracker(user, role='Rep')
        self.scorer = CompetencyScorer(user, role='Rep')
        self.troubleshooter = Troubleshooter(user)

    def start(self):
        show_tutorial('rep_intro')
        self.progress.checkpoint('Welcome')
        show_help('rep_dashboard')
        self.progress.checkpoint('Dashboard Tour')
        show_tutorial('rep_legislation')
        self.progress.checkpoint('Legislation Process')
        self.scorer.score('legislation_quiz')
        show_tutorial('rep_budget')
        self.progress.checkpoint('Budget Authority')
        self.troubleshooter.run()
        self.progress.complete()
