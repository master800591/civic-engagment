# Surveys & Polling Module
"""
Democratic opinion gathering, research, and referendum management system.
Provides comprehensive survey tools with statistical analysis and privacy protection.
"""

from .survey_engine import SurveyEngine
from .polling_ui import SurveysPollingTab

__all__ = ['SurveyEngine', 'SurveysPollingTab']