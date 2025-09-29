"""
Contract Elder Onboarding Module
Interactive training for constitutional interpretation and wisdom council duties
"""

contract_elder_modules = {
    'constitutional_interpretation': {
        'title': 'Constitutional Guardianship',
        'description': 'Understanding your role as constitutional interpreter and guardian',
        'interactive_elements': [
            {
                'type': 'constitutional_review',
                'title': 'Constitutional Compliance Review',
                'scenario': 'Review a proposed amendment for constitutional consistency',
                'steps': [
                    {
                        'step': 1,
                        'instruction': 'Analyze amendment text for constitutional conflicts',
                        'interaction_type': 'textual_analysis',
                        'target_element': 'amendment_text',
                        'expected_outcome': 'User identifies constitutional interpretation issues'
                    },
                    {
                        'step': 2,
                        'instruction': 'Write constitutional interpretation memo',
                        'interaction_type': 'document_creation',
                        'target_element': 'interpretation_memo',
                        'expected_outcome': 'User creates detailed constitutional analysis'
                    }
                ]
            }
        ],
        'progress_checkpoints': [
            {'checkpoint': 'constitutional_analysis', 'weight': 50},
            {'checkpoint': 'interpretation_quality', 'weight': 30},
            {'checkpoint': 'precedent_understanding', 'weight': 20}
        ],
        'competency_questions': [
            {
                'question': 'What is the primary constitutional power of Contract Elders?',
                'type': 'multiple_choice',
                'options': [
                    'Legislative initiative',
                    'Veto power over unconstitutional decisions',
                    'Budget authority',
                    'Administrative management'
                ],
                'correct_answer': 1,
                'points': 40
            }
        ],
        'estimated_duration_minutes': 40
    },
    
    'judicial_review_process': {
        'title': 'Judicial Review and Dispute Resolution',
        'description': 'Learning judicial review processes and conflict resolution',
        'interactive_elements': [
            {
                'type': 'judicial_simulation',
                'title': 'Constitutional Dispute Resolution',
                'scenario': 'Conflicting interpretations between branches of government',
                'steps': [
                    {
                        'step': 1,
                        'instruction': 'Review all parties\' constitutional arguments',
                        'interaction_type': 'comprehensive_review',
                        'expected_outcome': 'User demonstrates thorough constitutional analysis'
                    },
                    {
                        'step': 2,
                        'instruction': 'Provide binding constitutional interpretation',
                        'interaction_type': 'judicial_decision',
                        'expected_outcome': 'User creates clear constitutional precedent'
                    }
                ]
            }
        ],
        'progress_checkpoints': [
            {'checkpoint': 'comprehensive_analysis', 'weight': 45},
            {'checkpoint': 'precedent_creation', 'weight': 35},
            {'checkpoint': 'dispute_resolution', 'weight': 20}
        ],
        'competency_questions': [
            {
                'question': 'When creating constitutional precedent, what is most important?',
                'type': 'multiple_choice',
                'options': [
                    'Speed of decision',
                    'Popular opinion',
                    'Thorough analysis and clear reasoning',
                    'Political considerations'
                ],
                'correct_answer': 2,
                'points': 35
            }
        ],
        'estimated_duration_minutes': 35
    }
}

__all__ = ['contract_elder_modules']