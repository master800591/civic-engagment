"""
Contract Founder Onboarding Module
Interactive training for platform administration and emergency protocols
"""

contract_founder_modules = {
    'platform_administration': {
        'title': 'Platform Leadership and Crisis Management',
        'description': 'Understanding ultimate platform responsibility and emergency protocols',
        'interactive_elements': [
            {
                'type': 'crisis_simulation',
                'title': 'Emergency Protocol Activation',
                'scenario': 'Platform-threatening security incident requiring immediate response',
                'steps': [
                    {
                        'step': 1,
                        'instruction': 'Assess the severity of the security threat',
                        'interaction_type': 'decision_making',
                        'target_element': 'threat_assessment',
                        'expected_outcome': 'User demonstrates proper threat evaluation'
                    },
                    {
                        'step': 2,
                        'instruction': 'Coordinate with other Founders for consensus decision',
                        'interaction_type': 'collaboration',
                        'target_element': 'founder_consensus',
                        'expected_outcome': 'User follows proper consensus protocols'
                    }
                ]
            }
        ],
        'progress_checkpoints': [
            {'checkpoint': 'crisis_assessment', 'weight': 40},
            {'checkpoint': 'consensus_building', 'weight': 35},
            {'checkpoint': 'protocol_execution', 'weight': 25}
        ],
        'competency_questions': [
            {
                'question': 'What percentage of Contract Founders must agree for emergency protocol activation?',
                'type': 'multiple_choice',
                'options': ['Simple majority (51%)', '60%', '67%', '75% supermajority'],
                'correct_answer': 3,
                'points': 45
            }
        ],
        'estimated_duration_minutes': 45
    },
    
    'emergency_protocols': {
        'title': 'Emergency Response and Crisis Leadership',
        'description': 'Learning emergency protocols and crisis management',
        'interactive_elements': [
            {
                'type': 'emergency_drill',
                'title': 'Platform Security Crisis Response',
                'scenario': 'Critical security breach requiring immediate founder intervention',
                'steps': [
                    {
                        'step': 1,
                        'instruction': 'Activate emergency response protocols',
                        'interaction_type': 'protocol_activation',
                        'expected_outcome': 'User correctly initiates emergency procedures'
                    },
                    {
                        'step': 2,
                        'instruction': 'Coordinate multi-founder emergency response',
                        'interaction_type': 'crisis_coordination',
                        'expected_outcome': 'User effectively manages emergency team response'
                    }
                ]
            }
        ],
        'progress_checkpoints': [
            {'checkpoint': 'emergency_response', 'weight': 50},
            {'checkpoint': 'crisis_leadership', 'weight': 35},
            {'checkpoint': 'team_coordination', 'weight': 15}
        ],
        'competency_questions': [
            {
                'question': 'During a platform emergency, what is the first priority?',
                'type': 'multiple_choice',
                'options': [
                    'Maintaining user access',
                    'Platform security and integrity',
                    'Public relations',
                    'Cost minimization'
                ],
                'correct_answer': 1,
                'points': 40
            }
        ],
        'estimated_duration_minutes': 40
    }
}

__all__ = ['contract_founder_modules']