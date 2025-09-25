# Security Module - Advanced Security Monitoring and Compliance
# Enterprise-grade security monitoring, threat detection, and compliance management

"""
Security Module for Civic Engagement Platform

This module provides comprehensive security monitoring, threat detection, 
compliance management, and audit capabilities for the civic engagement platform.

Components:
- Enhanced Security Dashboard: Real-time security monitoring and threat detection
- Security Notification System: Advanced alert management and real-time notifications  
- Advanced Compliance & Audit: Enterprise-grade governance compliance monitoring

Key Features:
- 🛡️ Real-time security monitoring with threat level indicators
- 🚨 Advanced threat detection with automated response capabilities
- 🔔 Comprehensive notification system with system tray integration
- 📋 Multi-framework compliance monitoring (GDPR, SOX, ISO27001, HIPAA, etc.)
- 🔍 Complete audit trail with blockchain integration
- ⚠️ Risk assessment and mitigation planning
- 📊 Security analytics with trend analysis
- 🚑 Incident response procedures and emergency protocols

Usage:
    from civic_desktop.security.enhanced_security_dashboard import EnhancedSecurityDashboard
    from civic_desktop.security.security_notification_system import SecurityNotificationCenter
    from civic_desktop.security.advanced_compliance_audit import AdvancedComplianceAuditSystem
"""

from typing import List, Dict, Any, Optional
import datetime

# Version information
__version__ = "1.0.0"
__author__ = "Civic Engagement Platform Team"
__license__ = "MIT"

# Module exports
__all__ = [
    'EnhancedSecurityDashboard',
    'SecurityNotificationCenter', 
    'AdvancedComplianceAuditSystem',
    'SecurityNotification',
    'ComplianceRule',
    'AuditEvent'
]

# Security module configuration
SECURITY_CONFIG = {
    'monitoring_enabled': True,
    'threat_detection_enabled': True,
    'notifications_enabled': True,
    'compliance_monitoring_enabled': True,
    'audit_logging_enabled': True,
    'emergency_response_enabled': True,
    
    # Monitoring intervals (in seconds)
    'security_refresh_interval': 5,
    'threat_check_interval': 10,
    'compliance_check_interval': 300,
    'audit_cleanup_interval': 3600,
    
    # Alert thresholds
    'threat_level_thresholds': {
        'low': 0.3,
        'medium': 0.6,
        'high': 0.8,
        'critical': 0.95
    },
    
    # Compliance frameworks
    'supported_frameworks': [
        'GDPR', 'SOX', 'ISO27001', 'HIPAA', 'PCI-DSS', 'NIST'
    ],
    
    # Security features
    'features': {
        'real_time_monitoring': True,
        'threat_detection': True,
        'incident_response': True,
        'compliance_tracking': True,
        'audit_trail': True,
        'risk_assessment': True,
        'security_analytics': True,
        'emergency_protocols': True,
        'system_tray_notifications': True,
        'blockchain_integration': True
    }
}

# Security event types
SECURITY_EVENT_TYPES = {
    'authentication': 'Authentication Events',
    'authorization': 'Authorization Events', 
    'data_access': 'Data Access Events',
    'system_access': 'System Access Events',
    'configuration_change': 'Configuration Changes',
    'security_violation': 'Security Violations',
    'compliance_check': 'Compliance Checks',
    'incident_response': 'Incident Response',
    'threat_detection': 'Threat Detection',
    'audit_activity': 'Audit Activities'
}

# Compliance framework definitions
COMPLIANCE_FRAMEWORKS = {
    'GDPR': {
        'name': 'General Data Protection Regulation',
        'description': 'EU data protection and privacy regulation',
        'requirements': [
            'Data processing consent',
            'Right to be forgotten',
            'Data breach notifications',
            'Privacy by design',
            'Data protection officer'
        ]
    },
    'SOX': {
        'name': 'Sarbanes-Oxley Act',
        'description': 'Financial reporting and corporate governance',
        'requirements': [
            'Internal controls',
            'Financial reporting accuracy',
            'Executive accountability',
            'Audit oversight',
            'Whistleblower protection'
        ]
    },
    'ISO27001': {
        'name': 'ISO/IEC 27001',
        'description': 'Information security management systems',
        'requirements': [
            'Risk assessment',
            'Security controls',
            'Incident management',
            'Business continuity',
            'Supplier relationships'
        ]
    },
    'HIPAA': {
        'name': 'Health Insurance Portability and Accountability Act',
        'description': 'Healthcare data protection',
        'requirements': [
            'Protected health information',
            'Access controls',
            'Audit logs',
            'Risk assessments',
            'Business associate agreements'
        ]
    }
}

# Risk levels and their characteristics
RISK_LEVELS = {
    'low': {
        'color': '#28a745',
        'icon': '🟢',
        'description': 'Minimal risk to operations',
        'response_time': '24 hours',
        'escalation': False
    },
    'medium': {
        'color': '#ffc107',
        'icon': '🟡', 
        'description': 'Moderate risk requiring monitoring',
        'response_time': '4 hours',
        'escalation': False
    },
    'high': {
        'color': '#fd7e14',
        'icon': '🟠',
        'description': 'High risk requiring immediate attention',
        'response_time': '1 hour',
        'escalation': True
    },
    'critical': {
        'color': '#dc3545',
        'icon': '🔴',
        'description': 'Critical risk requiring emergency response',
        'response_time': '15 minutes',
        'escalation': True
    }
}

def get_security_config() -> Dict[str, Any]:
    """Get the current security configuration"""
    return SECURITY_CONFIG.copy()

def get_supported_frameworks() -> List[str]:
    """Get list of supported compliance frameworks"""
    return SECURITY_CONFIG['supported_frameworks'].copy()

def get_framework_info(framework: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific compliance framework"""
    return COMPLIANCE_FRAMEWORKS.get(framework.upper())

def get_risk_level_info(level: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific risk level"""
    return RISK_LEVELS.get(level.lower())

def is_feature_enabled(feature: str) -> bool:
    """Check if a security feature is enabled"""
    return SECURITY_CONFIG['features'].get(feature, False)

def get_security_status() -> Dict[str, Any]:
    """Get overall security module status"""
    return {
        'version': __version__,
        'monitoring_active': SECURITY_CONFIG['monitoring_enabled'],
        'features_enabled': sum(1 for f in SECURITY_CONFIG['features'].values() if f),
        'frameworks_supported': len(SECURITY_CONFIG['supported_frameworks']),
        'last_updated': datetime.datetime.now().isoformat()
    }

# Initialize security module
print(f"🛡️ Security Module v{__version__} initialized")
print(f"   Features enabled: {sum(1 for f in SECURITY_CONFIG['features'].values() if f)}")
print(f"   Compliance frameworks: {len(SECURITY_CONFIG['supported_frameworks'])}")
print(f"   Monitoring: {'✅ Active' if SECURITY_CONFIG['monitoring_enabled'] else '❌ Disabled'}")