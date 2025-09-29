"""
Troubleshooting Workflow Integration
Comprehensive troubleshooting workflows for common platform issues
"""

troubleshooting_workflows = {
    'login_issues': {
        'title': 'Login and Authentication Troubleshooting',
        'description': 'Step-by-step resolution for login problems',
        'category': 'authentication',
        'severity': 'high',
        'steps': [
            {
                'step': 1,
                'check': 'Verify email address is correct',
                'action': 'Double-check email spelling and try again',
                'common_mistakes': [
                    'Typos in email address',
                    'Wrong domain (.com vs .org)',
                    'Extra spaces or characters'
                ]
            },
            {
                'step': 2,
                'check': 'Verify password is correct',
                'action': 'Use password reset if needed',
                'common_mistakes': [
                    'Caps lock enabled',
                    'Wrong password remembered',
                    'Password recently changed'
                ]
            },
            {
                'step': 3,
                'check': 'Check for account suspension',
                'action': 'Contact support if account appears suspended',
                'escalation_trigger': 'Account status indicates suspension'
            }
        ],
        'success_criteria': 'User successfully logs in',
        'escalation_path': 'Contact technical support team'
    },
    
    'navigation_confusion': {
        'title': 'Platform Navigation Help',
        'description': 'Guidance for users having trouble finding features',
        'category': 'usability',
        'severity': 'medium',
        'steps': [
            {
                'step': 1,
                'check': 'Identify current location in platform',
                'action': 'Look at active tab and breadcrumbs',
                'guidance': 'The active tab is highlighted and shows your current section'
            },
            {
                'step': 2,
                'check': 'Use search functionality',
                'action': 'Try platform search to find specific features',
                'guidance': 'Search box is available in the top navigation bar'
            },
            {
                'step': 3,
                'check': 'Access help system',
                'action': 'Use contextual help for current page',
                'guidance': 'Help button (?) provides page-specific assistance'
            }
        ],
        'success_criteria': 'User successfully navigates to desired feature',
        'escalation_path': 'Refer to onboarding tutorials'
    },
    
    'voting_errors': {
        'title': 'Voting and Participation Issues',
        'description': 'Resolving problems with voting and civic participation',
        'category': 'civic_participation',
        'severity': 'high',
        'steps': [
            {
                'step': 1,
                'check': 'Verify voting eligibility',
                'action': 'Check if user has proper role and is in correct jurisdiction',
                'requirements': [
                    'Active Contract Member status or higher',
                    'Proper jurisdiction for the vote',
                    'No current voting restrictions'
                ]
            },
            {
                'step': 2,
                'check': 'Confirm vote submission',
                'action': 'Look for confirmation message and blockchain record',
                'verification': 'Vote should appear in blockchain audit trail'
            },
            {
                'step': 3,
                'check': 'Technical voting interface issues',
                'action': 'Refresh page and retry, or use alternative access method',
                'escalation_trigger': 'Interface repeatedly fails to respond'
            }
        ],
        'success_criteria': 'Vote successfully recorded on blockchain',
        'escalation_path': 'Contact election administrators'
    },
    
    'debate_participation_issues': {
        'title': 'Debate Participation Problems',
        'description': 'Resolving issues with debate access and contribution',
        'category': 'civic_participation',
        'severity': 'medium',
        'steps': [
            {
                'step': 1,
                'check': 'Verify debate access permissions',
                'action': 'Ensure user has appropriate role for debate participation',
                'permissions': {
                    'Contract Member': 'Can view and participate in all public debates',
                    'Contract Representative': 'Can create topics and moderate discussions',
                    'Contract Senator': 'Can review and provide constitutional guidance',
                    'Contract Elder': 'Can veto unconstitutional topics or arguments'
                }
            },
            {
                'step': 2,
                'check': 'Review community guidelines',
                'action': 'Ensure contribution follows platform standards',
                'guidelines': [
                    'Respectful and civil discourse',
                    'Evidence-based arguments',
                    'Constructive contribution to discussion'
                ]
            },
            {
                'step': 3,
                'check': 'Technical submission issues',
                'action': 'Try refreshing page or using different browser',
                'escalation_trigger': 'Repeated technical failures'
            }
        ],
        'success_criteria': 'User successfully participates in debate',
        'escalation_path': 'Contact moderation team'
    }
}

# Contextual help integration
contextual_help_triggers = {
    'first_login': {
        'trigger': 'User logs in for first time',
        'recommended_action': 'Start platform onboarding tutorial',
        'priority': 'high'
    },
    'voting_page_visit': {
        'trigger': 'User visits voting interface',
        'recommended_action': 'Show voting process help if user hasn\'t voted before',
        'priority': 'medium'
    },
    'debate_creation_attempt': {
        'trigger': 'User tries to create debate without proper role',
        'recommended_action': 'Explain role requirements and how to gain permissions',
        'priority': 'high'
    },
    'repeated_navigation_issues': {
        'trigger': 'User visits same help topic multiple times',
        'recommended_action': 'Offer comprehensive navigation tutorial',
        'priority': 'medium'
    }
}

__all__ = ['troubleshooting_workflows', 'contextual_help_triggers']