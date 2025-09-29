# User Onboarding Backend System
# Comprehensive role-based onboarding logic with competency tracking

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

# Import application components
try:
    from main import ENV_CONFIG
    # from users.backend import UserBackend  # Commented out to avoid merge conflicts
    from blockchain.blockchain import Blockchain
    from utils.validation import DataValidator
except ImportError as e:
    print(f"Warning: Import error in onboarding backend: {e}")
    ENV_CONFIG = {}


class UserOnboardingSystem:
    """Comprehensive user onboarding system with role-based pathways"""
    
    def __init__(self):
        self.db_path = ENV_CONFIG.get('system_guide_db_path', 'system_guide/onboarding_db.json')
        self.ensure_database()
        self.module_content_cache = {}
        
        # Initialize onboarding pathways configuration
        self.onboarding_pathways = self.load_onboarding_pathways()
    
    def ensure_database(self):
        """Ensure onboarding database exists"""
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if not os.path.exists(self.db_path):
            initial_data = {
                'onboarding_sessions': [],
                'help_sessions': [],
                'diagnostic_sessions': [],
                'module_completions': [],
                'user_progress': {},
                'competency_tracking': {}
            }
            
            with open(self.db_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def load_onboarding_pathways(self) -> Dict[str, Dict]:
        """Load role-based onboarding pathway configurations"""
        
        return {
            'Contract Member': {
                'modules': [
                    'platform_introduction',
                    'democratic_participation_basics',
                    'debate_participation',
                    'voting_system',
                    'petition_creation',
                    'civic_events_attendance',
                    'privacy_and_security'
                ],
                'estimated_duration_minutes': 45,
                'complexity_level': 'beginner',
                'interactive_elements': True,
                'prerequisites': [],
                'competency_threshold': 70
            },
            'Contract Representative': {
                'modules': [
                    'platform_introduction',
                    'legislative_responsibilities',
                    'debate_moderation',
                    'constituent_communication',
                    'budget_management',
                    'committee_coordination',
                    'transparency_requirements'
                ],
                'estimated_duration_minutes': 90,
                'complexity_level': 'intermediate',
                'interactive_elements': True,
                'prerequisites': ['Contract Member'],
                'competency_threshold': 80
            },
            'Contract Senator': {
                'modules': [
                    'platform_introduction',
                    'bicameral_responsibilities',
                    'constitutional_review',
                    'elder_coordination',
                    'cross_jurisdictional_cooperation',
                    'legislative_oversight',
                    'judicial_appointment_process'
                ],
                'estimated_duration_minutes': 120,
                'complexity_level': 'advanced',
                'interactive_elements': True,
                'prerequisites': ['Contract Representative'],
                'competency_threshold': 85
            },
            'Contract Elder': {
                'modules': [
                    'platform_introduction',
                    'constitutional_interpretation',
                    'judicial_review_process',
                    'elder_council_operations',
                    'constitutional_enforcement',
                    'crisis_management',
                    'wisdom_council_duties'
                ],
                'estimated_duration_minutes': 150,
                'complexity_level': 'expert',
                'interactive_elements': True,
                'prerequisites': ['Contract Senator'],
                'competency_threshold': 90
            },
            'Contract Founder': {
                'modules': [
                    'platform_administration',
                    'emergency_protocols',
                    'constitutional_amendments',
                    'system_integrity_management',
                    'crisis_leadership',
                    'platform_evolution',
                    'legacy_planning'
                ],
                'estimated_duration_minutes': 180,
                'complexity_level': 'master',
                'interactive_elements': True,
                'prerequisites': ['Contract Elder'],
                'competency_threshold': 95
            }
        }
    
    def initiate_user_onboarding(self, user_email: str, onboarding_preferences: Dict) -> Tuple[bool, Any]:
        """Initiate personalized user onboarding based on role and preferences"""
        
        try:
            # Load user profile for customization
            # user_backend = UserBackend()
            # user = user_backend.get_user(user_email)
            # Temporary mock user for testing
            user = {'role': 'Contract Member', 'experience_level': 'beginner'}
            if not user:
                return False, "Invalid user for onboarding"
            
            # Get role-specific onboarding pathway
            user_role = user.get('role', 'Contract Member')
            onboarding_pathway = self.onboarding_pathways.get(user_role, self.onboarding_pathways['Contract Member'])
            
            # Check prerequisites
            if not self.check_prerequisites(user_email, onboarding_pathway.get('prerequisites', [])):
                return False, f"Prerequisites not met for {user_role} onboarding"
            
            # Create customized pathway based on user preferences
            customized_pathway = self.customize_onboarding_pathway(onboarding_pathway, onboarding_preferences, user)
            
            # Create onboarding session
            onboarding_session = {
                'id': str(uuid.uuid4()),
                'user_email': user_email,
                'user_role': user_role,
                'pathway_configuration': customized_pathway,
                'progress_tracking': {
                    'completed_modules': [],
                    'current_module_index': 0,
                    'competency_assessments': {},
                    'time_spent_per_module': {},
                    'interaction_metrics': {}
                },
                'started_at': datetime.now().isoformat(),
                'estimated_completion_time': customized_pathway['estimated_duration_minutes'],
                'completion_status': 'in_progress',
                'milestone_achievements': [],
                'support_interactions': []
            }
            
            # Initialize first module
            first_module = customized_pathway['modules'][0]
            module_initialization = self.initialize_onboarding_module(first_module, onboarding_session)
            onboarding_session['current_module'] = module_initialization
            
            # Save onboarding session
            self.save_onboarding_session(onboarding_session)
            
            # Record onboarding initiation on blockchain
            try:
                Blockchain.add_page(
                    action_type="user_onboarding_initiated",
                    data={
                        'onboarding_id': onboarding_session['id'],
                        'user_email': user_email,
                        'user_role': user_role,
                        'pathway_selected': customized_pathway['modules'],
                        'estimated_duration': customized_pathway['estimated_duration_minutes']
                    },
                    user_email=user_email
                )
            except Exception as e:
                print(f"Warning: Failed to record onboarding initiation on blockchain: {e}")
            
            return True, onboarding_session
            
        except Exception as e:
            return False, f"Error initiating onboarding: {e}"
    
    def customize_onboarding_pathway(self, base_pathway: Dict, preferences: Dict, user: Dict) -> Dict:
        """Customize onboarding pathway based on user preferences and profile"""
        
        customized = base_pathway.copy()
        
        # Adjust based on user experience level
        experience_level = preferences.get('experience_level', user.get('experience_level', 'beginner'))
        
        if experience_level == 'experienced':
            # Skip basic modules for experienced users
            modules = customized['modules']
            if 'platform_introduction' in modules and len(modules) > 1:
                modules.remove('platform_introduction')
            customized['estimated_duration_minutes'] = int(customized['estimated_duration_minutes'] * 0.8)
        
        elif experience_level == 'expert':
            # Focus on advanced topics only
            advanced_modules = [m for m in customized['modules'] if 'advanced' in m or 'constitutional' in m or 'crisis' in m]
            if advanced_modules:
                customized['modules'] = advanced_modules
                customized['estimated_duration_minutes'] = int(customized['estimated_duration_minutes'] * 0.6)
        
        # Adjust for learning pace preference
        learning_pace = preferences.get('learning_pace', 'normal')
        
        if learning_pace == 'accelerated':
            customized['estimated_duration_minutes'] = int(customized['estimated_duration_minutes'] * 0.75)
        elif learning_pace == 'thorough':
            customized['estimated_duration_minutes'] = int(customized['estimated_duration_minutes'] * 1.25)
        
        # Add focus areas based on user interests
        focus_areas = preferences.get('focus_areas', [])
        if 'blockchain' in focus_areas:
            if 'blockchain_fundamentals' not in customized['modules']:
                customized['modules'].append('blockchain_fundamentals')
        
        if 'security' in focus_areas:
            if 'privacy_and_security' not in customized['modules']:
                customized['modules'].append('privacy_and_security')
        
        return customized
    
    def check_prerequisites(self, user_email: str, prerequisites: List[str]) -> bool:
        """Check if user has completed prerequisite roles/training"""
        
        if not prerequisites:
            return True
        
        try:
            # user_backend = UserBackend()
            # user = user_backend.get_user(user_email)
            # Temporary mock for testing
            user = {'role': 'Contract Member'}
            
            if not user:
                return False
            
            # Check role progression
            current_role = user.get('role', 'Contract Member')
            role_hierarchy = ['Contract Member', 'Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder']
            
            current_level = role_hierarchy.index(current_role) if current_role in role_hierarchy else 0
            
            for prerequisite in prerequisites:
                if prerequisite in role_hierarchy:
                    prereq_level = role_hierarchy.index(prerequisite)
                    if current_level < prereq_level:
                        return False
            
            return True
            
        except Exception as e:
            print(f"Error checking prerequisites: {e}")
            return False
    
    def initialize_onboarding_module(self, module_name: str, onboarding_session: Dict) -> Dict:
        """Initialize a specific onboarding module"""
        
        try:
            module_content = self.get_module_content(module_name)
            
            module_initialization = {
                'module_name': module_name,
                'content': module_content,
                'started_at': datetime.now().isoformat(),
                'status': 'active',
                'progress_percentage': 0,
                'interactions_completed': [],
                'time_spent_seconds': 0
            }
            
            return module_initialization
            
        except Exception as e:
            return {
                'module_name': module_name,
                'error': f"Failed to initialize module: {e}",
                'status': 'error'
            }
    
    def get_module_content(self, module_name: str) -> Dict:
        """Get content for a specific module"""
        
        # Cache module content for performance
        if module_name in self.module_content_cache:
            return self.module_content_cache[module_name]
        
        # Module content definitions
        module_content = self.get_default_module_content(module_name)
        
        # Cache the content
        self.module_content_cache[module_name] = module_content
        
        return module_content
    
    def get_default_module_content(self, module_name: str) -> Dict:
        """Get default content for modules"""
        
        content_library = {
            'platform_introduction': {
                'title': 'Platform Introduction',
                'description': 'Welcome to the Civic Engagement Platform! Learn about democratic participation and your role in governance.',
                'learning_objectives': [
                    'Understand the platform\'s democratic mission',
                    'Learn about civic roles and responsibilities',
                    'Navigate the main interface features',
                    'Understand blockchain transparency'
                ],
                'questions': [
                    {
                        'text': 'What is the primary purpose of the Civic Engagement Platform?',
                        'options': [
                            'Social networking',
                            'Democratic participation and governance',
                            'Business networking',
                            'Entertainment'
                        ],
                        'correct': 1,
                        'points': 10
                    }
                ],
                'scenarios': [
                    {
                        'title': 'New User Registration',
                        'description': 'You are helping a friend register for the platform. What steps would you recommend?',
                        'actions': [
                            {'id': 'verify_id', 'label': 'Verify government ID first', 'points': 15, 'feedback': 'Correct! ID verification ensures platform integrity.'},
                            {'id': 'skip_verification', 'label': 'Skip verification for now', 'points': 0, 'feedback': 'Incorrect. Verification is required for security.'}
                        ]
                    }
                ],
                'exercises': [
                    {
                        'type': 'text_input',
                        'title': 'Platform Vision',
                        'instructions': 'In your own words, describe what democratic participation means to you.',
                        'min_length': 50
                    }
                ]
            },
            'democratic_participation_basics': {
                'title': 'Democratic Participation Basics',
                'description': 'Learn the fundamentals of civic engagement and democratic processes.',
                'learning_objectives': [
                    'Understand voting rights and responsibilities',
                    'Learn about debate participation',
                    'Understand petition processes',
                    'Learn about transparency in government'
                ],
                'questions': [
                    {
                        'text': 'What are the key components of democratic participation?',
                        'options': [
                            'Voting only',
                            'Voting, debate, transparency, and accountability',
                            'Following rules only',
                            'Paying taxes'
                        ],
                        'correct': 1,
                        'points': 10
                    }
                ],
                'scenarios': [
                    {
                        'title': 'Voting Decision',
                        'description': 'There\'s an important local vote coming up. How do you prepare?',
                        'actions': [
                            {'id': 'research_issues', 'label': 'Research the issues thoroughly', 'points': 20, 'feedback': 'Excellent! Informed voting is crucial.'},
                            {'id': 'vote_randomly', 'label': 'Vote based on first impression', 'points': 0, 'feedback': 'Not recommended. Research leads to better decisions.'}
                        ]
                    }
                ],
                'exercises': [
                    {
                        'type': 'selection',
                        'title': 'Civic Responsibilities',
                        'instructions': 'Select the civic responsibilities that apply to all citizens:',
                        'options': ['Vote in elections', 'Serve on juries', 'Pay taxes', 'Run for office', 'Participate in community discussions']
                    }
                ]
            },
            'debate_participation': {
                'title': 'Debate Participation',
                'description': 'Learn how to engage constructively in civic debates and discussions.',
                'learning_objectives': [
                    'Understand debate etiquette and rules',
                    'Learn to present logical arguments',
                    'Practice respectful disagreement',
                    'Understand moderation processes'
                ],
                'questions': [
                    {
                        'text': 'What makes a debate argument effective?',
                        'options': [
                            'Being the loudest',
                            'Using facts and logical reasoning',
                            'Personal attacks',
                            'Emotional appeals only'
                        ],
                        'correct': 1,
                        'points': 15
                    }
                ],
                'scenarios': [
                    {
                        'title': 'Heated Debate',
                        'description': 'Someone in a debate is using personal attacks. How do you respond?',
                        'actions': [
                            {'id': 'flag_moderator', 'label': 'Flag for moderator review', 'points': 20, 'feedback': 'Good choice! Moderators maintain debate quality.'},
                            {'id': 'respond_personally', 'label': 'Respond with personal attacks', 'points': 0, 'feedback': 'This escalates the problem and violates debate rules.'}
                        ]
                    }
                ],
                'exercises': [
                    {
                        'type': 'text_input',
                        'title': 'Argument Construction',
                        'instructions': 'Write a brief argument for or against increasing public transportation funding. Use facts and logic.',
                        'min_length': 100
                    }
                ]
            },
            'voting_system': {
                'title': 'Voting System',
                'description': 'Understand how voting works on the platform and your voting rights.',
                'learning_objectives': [
                    'Learn about different types of votes',
                    'Understand voting eligibility',
                    'Practice using the voting interface',
                    'Learn about vote verification'
                ],
                'questions': [
                    {
                        'text': 'When are you eligible to vote on platform proposals?',
                        'options': [
                            'Only if you\'re a representative',
                            'If you\'re a verified platform member',
                            'Only during election periods',
                            'Never, only elders vote'
                        ],
                        'correct': 1,
                        'points': 10
                    }
                ],
                'scenarios': [
                    {
                        'title': 'Voting Deadline',
                        'description': 'An important vote deadline is approaching and you haven\'t decided yet. What do you do?',
                        'actions': [
                            {'id': 'research_quickly', 'label': 'Do quick research and vote', 'points': 15, 'feedback': 'Good! Quick but informed decisions are valuable.'},
                            {'id': 'skip_vote', 'label': 'Skip this vote', 'points': 5, 'feedback': 'Your voice matters! Try to participate when possible.'}
                        ]
                    }
                ],
                'exercises': [
                    {
                        'type': 'selection',
                        'title': 'Vote Types',
                        'instructions': 'Which types of votes might you encounter?',
                        'options': ['Policy proposals', 'Budget allocations', 'Representative elections', 'Constitutional amendments', 'Emergency measures']
                    }
                ]
            }
        }
        
        return content_library.get(module_name, {
            'title': module_name.replace('_', ' ').title(),
            'description': f'Content for {module_name}',
            'learning_objectives': ['Learn about ' + module_name.replace('_', ' ')],
            'questions': [],
            'scenarios': [],
            'exercises': []
        })
    
    def complete_module(self, session_id: str, module_name: str, completion_data: Dict) -> Tuple[bool, str]:
        """Mark a module as completed and update progress"""
        
        try:
            # Load onboarding session
            session = self.get_onboarding_session_by_id(session_id)
            if not session:
                return False, "Onboarding session not found"
            
            # Validate completion data
            competency_score = completion_data.get('competency_score', 0)
            required_threshold = session['pathway_configuration'].get('competency_threshold', 70)
            
            if competency_score < required_threshold:
                return False, f"Competency score {competency_score}% below required threshold {required_threshold}%"
            
            # Update progress tracking
            progress = session['progress_tracking']
            progress['completed_modules'].append(module_name)
            progress['competency_assessments'][module_name] = competency_score
            progress['time_spent_per_module'][module_name] = completion_data.get('time_spent_minutes', 0)
            progress['interaction_metrics'][module_name] = completion_data.get('interaction_metrics', {})
            
            # Move to next module
            current_index = progress['current_module_index']
            pathway_modules = session['pathway_configuration']['modules']
            
            if current_index + 1 < len(pathway_modules):
                # Move to next module
                progress['current_module_index'] = current_index + 1
                next_module = pathway_modules[current_index + 1]
                session['current_module'] = self.initialize_onboarding_module(next_module, session)
            else:
                # Onboarding complete
                session['completion_status'] = 'completed'
                session['completed_at'] = datetime.now().isoformat()
                session['current_module'] = None
                
                # Calculate overall competency score
                overall_score = sum(progress['competency_assessments'].values()) / len(progress['competency_assessments'])
                session['final_competency_score'] = overall_score
            
            # Save updated session
            self.save_onboarding_session(session, update=True)
            
            # Record module completion on blockchain
            try:
                Blockchain.add_page(
                    action_type="onboarding_module_completed",
                    data={
                        'session_id': session_id,
                        'module_name': module_name,
                        'competency_score': competency_score,
                        'completion_time': completion_data.get('completion_time'),
                        'time_spent_minutes': completion_data.get('time_spent_minutes', 0)
                    },
                    user_email=session['user_email']
                )
            except Exception as e:
                print(f"Warning: Failed to record module completion on blockchain: {e}")
            
            return True, "Module completed successfully"
            
        except Exception as e:
            return False, f"Error completing module: {e}"
    
    def get_next_module(self, session: Dict) -> Optional[Dict]:
        """Get the next module in the onboarding pathway"""
        
        try:
            progress = session['progress_tracking']
            current_index = progress['current_module_index']
            pathway_modules = session['pathway_configuration']['modules']
            
            if current_index < len(pathway_modules):
                next_module_name = pathway_modules[current_index]
                return self.initialize_onboarding_module(next_module_name, session)
            
            return None  # No more modules
            
        except Exception as e:
            print(f"Error getting next module: {e}")
            return None
    
    def get_onboarding_session(self, user_email: str) -> Optional[Dict]:
        """Get current onboarding session for user"""
        
        try:
            data = self.load_data()
            
            for session in data['onboarding_sessions']:
                if session['user_email'] == user_email and session['completion_status'] == 'in_progress':
                    return session
            
            return None
            
        except Exception as e:
            print(f"Error getting onboarding session: {e}")
            return None
    
    def get_onboarding_session_by_id(self, session_id: str) -> Optional[Dict]:
        """Get onboarding session by ID"""
        
        try:
            data = self.load_data()
            
            for session in data['onboarding_sessions']:
                if session['id'] == session_id:
                    return session
            
            return None
            
        except Exception as e:
            print(f"Error getting onboarding session by ID: {e}")
            return None
    
    def save_onboarding_session(self, session: Dict, update: bool = False):
        """Save or update onboarding session"""
        
        try:
            data = self.load_data()
            
            if update:
                # Update existing session
                for i, existing_session in enumerate(data['onboarding_sessions']):
                    if existing_session['id'] == session['id']:
                        data['onboarding_sessions'][i] = session
                        break
            else:
                # Add new session
                data['onboarding_sessions'].append(session)
            
            self.save_data(data)
            
        except Exception as e:
            print(f"Error saving onboarding session: {e}")
    
    def get_user_progress_summary(self, user_email: str) -> Dict:
        """Get comprehensive progress summary for user"""
        
        try:
            data = self.load_data()
            
            # Find all sessions for user
            user_sessions = [s for s in data['onboarding_sessions'] if s['user_email'] == user_email]
            
            if not user_sessions:
                return {'status': 'not_started'}
            
            # Get most recent session
            latest_session = max(user_sessions, key=lambda s: s.get('started_at', ''))
            
            progress_summary = {
                'status': latest_session['completion_status'],
                'user_role': latest_session['user_role'],
                'modules_completed': len(latest_session['progress_tracking']['completed_modules']),
                'total_modules': len(latest_session['pathway_configuration']['modules']),
                'overall_competency': 0,
                'time_spent_total': sum(latest_session['progress_tracking']['time_spent_per_module'].values()),
                'achievements': latest_session.get('milestone_achievements', []),
                'started_at': latest_session['started_at'],
                'estimated_completion': latest_session.get('completed_at')
            }
            
            # Calculate overall competency
            competency_scores = latest_session['progress_tracking']['competency_assessments']
            if competency_scores:
                progress_summary['overall_competency'] = sum(competency_scores.values()) / len(competency_scores)
            
            return progress_summary
            
        except Exception as e:
            print(f"Error getting user progress summary: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def load_data(self) -> Dict:
        """Load onboarding database"""
        
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.ensure_database()
            return self.load_data()
        except json.JSONDecodeError:
            # Reset corrupted database
            self.ensure_database()
            return self.load_data()
    
    def save_data(self, data: Dict):
        """Save onboarding database"""
        
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving onboarding data: {e}")


# Export the main class
__all__ = ['UserOnboardingSystem']