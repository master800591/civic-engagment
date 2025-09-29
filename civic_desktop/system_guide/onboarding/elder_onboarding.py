# Elder Onboarding Module
# Interactive onboarding for Contract Elders

from .tutorials import show_tutorial, show_help
from .progress import ProgressTracker, CompetencyScorer
from .support import Troubleshooter

class ElderOnboarding:
    def __init__(self, user):
        self.user = user
        self.progress = ProgressTracker(user, role='Elder')
        self.scorer = CompetencyScorer(user, role='Elder')
        self.troubleshooter = Troubleshooter(user)

    def start(self):
        show_tutorial('elder_intro')
        self.progress.checkpoint('Welcome')
        show_help('elder_dashboard')
        self.progress.checkpoint('Dashboard Tour')
        show_tutorial('elder_veto')
        self.progress.checkpoint('Constitutional Veto')
        self.scorer.score('veto_quiz')
        show_tutorial('elder_judicial')
        self.progress.checkpoint('Judicial Review')
        self.troubleshooter.run()
        self.progress.complete()
