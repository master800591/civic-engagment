"""
Petitions & Initiatives Module - __init__.py
Citizen-driven legislative process and signature collection system.
"""

# Module metadata
__version__ = "1.0.0"
__author__ = "Civic Engagement Platform"
__description__ = "Petitions & Initiatives - Democratic citizen empowerment system"

# Import core components
from .petition_system import PetitionSystem
from .initiatives_ui import PetitionsInitiativesTab

__all__ = [
    'PetitionSystem',
    'PetitionsInitiativesTab'
]