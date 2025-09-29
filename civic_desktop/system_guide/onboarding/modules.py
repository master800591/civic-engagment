"""
Interactive Onboarding Modules - Role-Based User Guidance
Comprehensive onboarding modules for all user roles with interactive tutorials and competency tracking
"""

# Contract Member Module
contract_member_modules = {
    'platform_introduction': {
        'title': 'Welcome to Civic Engagement Platform',
        'description': 'Introduction to democratic participation and platform basics',
        'interactive_elements': [
            {
                'type': 'tutorial',
                'title': 'Platform Tour',
                'steps': [
                    {
                        'step': 1,
                        'instruction': 'Navigate to the Debates tab to see current civic discussions',
                        'interaction_type': 'click',
                        'target_element': 'debates_tab',
                        'expected_outcome': 'User successfully navigates to debates section'
                    },
                    {
                        'step': 2,
                        'instruction': 'Click on a debate topic to view arguments and discussions',
                        'interaction_type': 'click',
                        'target_element': 'debate_topic',
                        'expected_outcome': 'User opens a debate and can see arguments'
                    }
                ]
            }
        ],
        'progress_checkpoints': [
            {'checkpoint': 'completed_tour', 'weight': 30},
            {'checkpoint': 'understood_navigation', 'weight': 40},
            {'checkpoint': 'explored_features', 'weight': 30}
        ],
        'competency_questions': [
            {
                'question': 'What is the primary purpose of the Civic Engagement Platform?',
                'type': 'multiple_choice',
                'options': [
                    'Social networking',
                    'Democratic participation and governance',
                    'Business networking',
                    'Entertainment'
                ],
                'correct_answer': 1,
                'points': 25
            }
        ],
        'estimated_duration_minutes': 15
    },
    
    'democratic_participation_basics': {
        'title': 'Democratic Participation Fundamentals',
        'description': 'Understanding your role as a Contract Member in democratic governance',
        'interactive_elements': [
            {
                'type': 'interactive_guide',
                'title': 'Understanding Your Rights and Responsibilities',
                'content': {
                    'rights': [
                        'Vote in all elections and referendums',
                        'Participate in debates and discussions',
                        'Submit petitions and initiatives',
                        'Appeal moderation decisions',
                        'Access public records and transparency reports'
                    ],
                    'responsibilities': [
                        'Engage respectfully with other citizens',
                        'Stay informed on civic issues',
                        'Participate in good faith',
                        'Report violations of community standards',
                        'Contribute constructively to discussions'
                    ]
                }
            }
        ],
        'progress_checkpoints': [
            {'checkpoint': 'understood_rights', 'weight': 50},
            {'checkpoint': 'understood_responsibilities', 'weight': 50}
        ],
        'competency_questions': [
            {
                'question': 'As a Contract Member, which of the following is NOT your responsibility?',
                'type': 'multiple_choice',
                'options': [
                    'Participate respectfully in debates',
                    'Moderate other users\' content',
                    'Stay informed on civic issues',
                    'Report community standards violations'
                ],
                'correct_answer': 1,
                'points': 25
            }
        ],
        'estimated_duration_minutes': 10
    }
}

# Export all modules
__all__ = [
    'contract_member_modules'
]