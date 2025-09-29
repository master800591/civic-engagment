"""
Contract Senator Onboarding Module
Interactive training for senate deliberation and review
"""

contract_senator_modules = {
    'bicameral_responsibilities': {
        'title': 'Senate Deliberation and Review',
        'description': 'Understanding the deliberative role and bicameral system',
        'interactive_elements': [
            {
                'type': 'case_study',
                'title': 'Constitutional Review Process',
                'scenario': 'Reviewing Representative legislation for constitutional compliance',
                'steps': [
                    {
                        'step': 1,
                        'instruction': 'Analyze proposed legislation for constitutional issues',
                        'interaction_type': 'analysis',
                        'target_element': 'legislation_text',
                        'expected_outcome': 'User identifies potential constitutional concerns'
                    },
                    {
                        'step': 2,
                        'instruction': 'Collaborate with Elders on constitutional interpretation',
                        'interaction_type': 'collaboration',
                        'target_element': 'elder_consultation',
                        'expected_outcome': 'User demonstrates proper consultation process'
                    }
                ]
            }
        ],
        'progress_checkpoints': [
            {'checkpoint': 'constitutional_analysis', 'weight': 45},
            {'checkpoint': 'elder_collaboration', 'weight': 35},
            {'checkpoint': 'deliberative_process', 'weight': 20}
        ],
        'competency_questions': [
            {
                'question': 'What percentage vote is required for Senators to override an Elder veto?',
                'type': 'multiple_choice',
                'options': ['Simple majority (51%)', '60%', '67% supermajority', '75%'],
                'correct_answer': 2,
                'points': 35
            }
        ],
        'estimated_duration_minutes': 30
    },
    
    'constitutional_review': {
        'title': 'Constitutional Oversight Duties',
        'description': 'Learning constitutional review and Elder collaboration',
        'interactive_elements': [
            {
                'type': 'collaborative_exercise',
                'title': 'Elder-Senator Constitutional Review',
                'scenario': 'Joint review of potentially unconstitutional proposal',
                'steps': [
                    {
                        'step': 1,
                        'instruction': 'Request Elder constitutional interpretation',
                        'interaction_type': 'formal_request',
                        'expected_outcome': 'User follows proper protocol for Elder consultation'
                    },
                    {
                        'step': 2,
                        'instruction': 'Evaluate Elder guidance for legislative decision',
                        'interaction_type': 'decision_making',
                        'expected_outcome': 'User incorporates constitutional guidance appropriately'
                    }
                ]
            }
        ],
        'progress_checkpoints': [
            {'checkpoint': 'protocol_adherence', 'weight': 50},
            {'checkpoint': 'constitutional_understanding', 'weight': 50}
        ],
        'competency_questions': [
            {
                'question': 'When should Senators consult with Elders?',
                'type': 'multiple_choice',
                'options': [
                    'Only during emergencies',
                    'Before any legislative vote',
                    'When constitutional issues may be involved',
                    'Never - Senators act independently'
                ],
                'correct_answer': 2,
                'points': 30
            }
        ],
        'estimated_duration_minutes': 25
    }
}

__all__ = ['contract_senator_modules']