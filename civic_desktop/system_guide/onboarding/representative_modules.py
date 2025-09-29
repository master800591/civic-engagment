"""
Contract Representative Onboarding Module
Interactive training for legislative representatives
"""

contract_representative_modules = {
    'legislative_responsibilities': {
        'title': 'Legislative Leadership and Responsibilities',
        'description': 'Understanding your role as a people\'s representative in governance',
        'interactive_elements': [
            {
                'type': 'simulation',
                'title': 'Legislative Process Simulation',
                'scenario': 'Budget Proposal Review',
                'steps': [
                    {
                        'step': 1,
                        'instruction': 'Review the proposed budget allocation for education',
                        'interaction_type': 'document_review',
                        'target_element': 'budget_document',
                        'expected_outcome': 'User demonstrates understanding of budget review process'
                    },
                    {
                        'step': 2,
                        'instruction': 'Create a position statement on the budget proposal',
                        'interaction_type': 'text_input',
                        'target_element': 'position_statement',
                        'expected_outcome': 'User submits coherent policy position'
                    }
                ]
            }
        ],
        'progress_checkpoints': [
            {'checkpoint': 'completed_simulation', 'weight': 40},
            {'checkpoint': 'demonstrated_analysis', 'weight': 35},
            {'checkpoint': 'effective_communication', 'weight': 25}
        ],
        'competency_questions': [
            {
                'question': 'What is the primary role of Contract Representatives?',
                'type': 'multiple_choice',
                'options': [
                    'Judicial review of laws',
                    'Direct representation of citizen interests',
                    'Constitutional interpretation',
                    'Administrative oversight only'
                ],
                'correct_answer': 1,
                'points': 30
            }
        ],
        'estimated_duration_minutes': 25
    },
    
    'debate_moderation': {
        'title': 'Debate Leadership and Moderation',
        'description': 'Learning to facilitate constructive civic debates',
        'interactive_elements': [
            {
                'type': 'role_play',
                'title': 'Debate Facilitation Practice',
                'scenario': 'Heated debate on local infrastructure spending',
                'steps': [
                    {
                        'step': 1,
                        'instruction': 'Establish ground rules for respectful discourse',
                        'interaction_type': 'rule_setting',
                        'expected_outcome': 'User sets clear, fair debate guidelines'
                    },
                    {
                        'step': 2,
                        'instruction': 'Manage conflicting viewpoints constructively',
                        'interaction_type': 'conflict_resolution',
                        'expected_outcome': 'User demonstrates effective moderation skills'
                    }
                ]
            }
        ],
        'progress_checkpoints': [
            {'checkpoint': 'facilitation_skills', 'weight': 60},
            {'checkpoint': 'conflict_management', 'weight': 40}
        ],
        'competency_questions': [
            {
                'question': 'When moderating a heated debate, what should be your first priority?',
                'type': 'multiple_choice',
                'options': [
                    'Take a side in the argument',
                    'Ensure all participants can express their views respectfully',
                    'End the debate immediately',
                    'Only allow certain viewpoints'
                ],
                'correct_answer': 1,
                'points': 25
            }
        ],
        'estimated_duration_minutes': 20
    }
}

__all__ = ['contract_representative_modules']