"""
Documents & Archive Module - __init__.py
Official document management and transparency system.
"""

# Module metadata
__version__ = "1.0.0"
__author__ = "Civic Engagement Platform"
__description__ = "Documents & Archive - Democratic transparency and records management"

# Import core components
from .document_manager import DocumentManager
from .archive_ui import DocumentsArchiveTab

__all__ = [
    'DocumentManager',
    'DocumentsArchiveTab'
]