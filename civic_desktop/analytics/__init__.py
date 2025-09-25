# Analytics Module - Data-Driven Governance Insights
"""
Analytics module providing comprehensive platform analytics including:
- Participation metrics and civic engagement analysis
- Governance effectiveness monitoring and reporting
- Platform health and performance tracking
- Transparent report generation with blockchain audit trails
"""

from .backend import AnalyticsEngine
from .reports_ui import AnalyticsTab

__all__ = ['AnalyticsEngine', 'AnalyticsTab']