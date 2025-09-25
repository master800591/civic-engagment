"""
Transparency & Audit Module - __init__.py
Enhanced accountability and public oversight system.
"""

# Module metadata
__version__ = "1.0.0"
__author__ = "Civic Engagement Platform"
__description__ = "Transparency & Audit - Democratic accountability and oversight"

# Import core components
from .audit_engine import AuditEngine
from .oversight_ui import TransparencyAuditTab

__all__ = [
    'AuditEngine', 
    'TransparencyAuditTab'
]