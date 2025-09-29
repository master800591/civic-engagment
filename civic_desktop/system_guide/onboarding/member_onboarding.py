# Member Onboarding Module
# Interactive onboarding for Contract Members

from .tutorials import show_tutorial, show_help
from .progress import ProgressTracker, CompetencyScorer
from .support import Troubleshooter

class MemberOnboarding:
    def __init__(self, user):
        self.user = user
        self.progress = ProgressTracker(user, role='Member')
        self.scorer = CompetencyScorer(user, role='Member')
        self.troubleshooter = Troubleshooter(user)

    def start(self):
        show_tutorial('member_intro')
        self.progress.checkpoint('Welcome')
        show_help('member_dashboard')
        self.progress.checkpoint('Dashboard Tour')
        show_tutorial('member_debate')
        self.progress.checkpoint('Debate Participation')
        self.scorer.score('debate_quiz')
        show_tutorial('member_voting')
        self.progress.checkpoint('Voting Rights')
        self.troubleshooter.run()
        self.progress.complete()
