"""
Onboarding Package - Interactive Role-Based User Training
Comprehensive onboarding modules for all civic engagement platform roles
"""

from .modules import contract_member_modules
from .representative_modules import contract_representative_modules
from .senator_modules import contract_senator_modules
from .elder_modules import contract_elder_modules
from .founder_modules import contract_founder_modules
from .troubleshooting import troubleshooting_workflows, contextual_help_triggers

# Combined module registry for easy access
ALL_ROLE_MODULES = {
    'Contract Member': contract_member_modules,
    'Contract Representative': contract_representative_modules,
    'Contract Senator': contract_senator_modules,
    'Contract Elder': contract_elder_modules,
    'Contract Founder': contract_founder_modules
}

# Competency scoring configuration
COMPETENCY_THRESHOLDS = {
    'Contract Member': 70,
    'Contract Representative': 80,
    'Contract Senator': 85,
    'Contract Elder': 90,
    'Contract Founder': 95
}

# Progress checkpoint weights
CHECKPOINT_WEIGHTS = {
    'tutorial_completion': 0.3,
    'interactive_exercises': 0.4,
    'competency_assessment': 0.3
}

__all__ = [
    'contract_member_modules',
    'contract_representative_modules', 
    'contract_senator_modules',
    'contract_elder_modules',
    'contract_founder_modules',
    'troubleshooting_workflows',
    'contextual_help_triggers',
    'ALL_ROLE_MODULES',
    'COMPETENCY_THRESHOLDS',
    'CHECKPOINT_WEIGHTS'
]