# Surveys & Polling Module - Democratic Opinion Gathering & Research System
"""
Backend components for surveys, polling, and referendum management.
Provides comprehensive opinion collection, statistical analysis, and research tools.
Supports anonymous and verified responses with privacy protections.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import uuid
from ..main import ENV_CONFIG
from ..users.session import SessionManager
from ..blockchain.blockchain import Blockchain

class SurveyEngine:
    """Core engine for survey creation, management, and statistical analysis"""
    
    def __init__(self):
        self.db_path = ENV_CONFIG.get('surveys_db_path', 'surveys/surveys_db.json')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def load_surveys_data(self) -> Dict[str, Any]:
        """Load surveys database with comprehensive data structure"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.create_default_surveys_structure()
        except Exception as e:
            print(f"Error loading surveys data: {e}")
            return self.create_default_surveys_structure()
    
    def save_surveys_data(self, data: Dict[str, Any]) -> bool:
        """Save surveys data with error handling"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving surveys data: {e}")
            return False
    
    def create_default_surveys_structure(self) -> Dict[str, Any]:
        """Create default surveys database structure"""
        return {
            'surveys': [],
            'polls': [],
            'referendums': [],
            'responses': {},
            'analytics': {
                'total_surveys': 0,
                'total_responses': 0,
                'active_surveys': 0,
                'participation_rate': 0.0
            },
            'demographics': {},
            'research_projects': [],
            'version': '1.0.0',
            'last_updated': datetime.now().isoformat()
        }
    
    def create_survey(self, creator_email: str, title: str, description: str, 
                     questions: List[Dict], target_audience: List[str], 
                     survey_type: str = 'opinion', privacy_mode: str = 'anonymous',
                     duration_days: int = 30) -> Tuple[bool, str]:
        """Create a new survey with comprehensive configuration"""
        
        # Validate creator permissions
        user = SessionManager.get_current_user()
        if not user or user['email'] != creator_email:
            return False, "Authentication required"
        
        if not self.can_create_survey(user.get('role', '')):
            return False, "Insufficient permissions to create surveys"
        
        # Validate survey data
        if not all([title.strip(), description.strip(), questions]):
            return False, "Missing required survey information"
        
        # Validate questions structure
        for i, question in enumerate(questions):
            if not isinstance(question, dict) or 'question' not in question:
                return False, f"Invalid question format at index {i}"
            
            if 'type' not in question:
                question['type'] = 'multiple_choice'  # Default type
        
        try:
            data = self.load_surveys_data()
            
            # Create survey object
            survey = {
                'id': str(uuid.uuid4()),
                'title': title.strip(),
                'description': description.strip(),
                'creator_email': creator_email,
                'creator_role': user.get('role', 'Unknown'),
                'questions': questions,
                'target_audience': target_audience,
                'survey_type': survey_type,  # opinion, research, referendum, policy
                'privacy_mode': privacy_mode,  # anonymous, verified, public
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'ends_at': (datetime.now() + timedelta(days=duration_days)).isoformat(),
                'response_count': 0,
                'settings': {
                    'allow_multiple_responses': privacy_mode == 'anonymous',
                    'require_authentication': privacy_mode in ['verified', 'public'],
                    'show_results_live': survey_type in ['opinion', 'poll'],
                    'demographic_collection': survey_type in ['research', 'policy']
                }
            }
            
            # Add to database
            data['surveys'].append(survey)
            data['analytics']['total_surveys'] += 1
            data['analytics']['active_surveys'] += 1
            data['last_updated'] = datetime.now().isoformat()
            
            # Save data
            if self.save_surveys_data(data):
                # Record on blockchain for transparency
                Blockchain.add_page(
                    action_type="survey_created",
                    data={
                        'survey_id': survey['id'],
                        'title': title,
                        'creator': creator_email,
                        'type': survey_type,
                        'privacy_mode': privacy_mode,
                        'target_audience': target_audience
                    },
                    user_email=creator_email
                )
                
                return True, f"Survey '{title}' created successfully"
            else:
                return False, "Failed to save survey data"
                
        except Exception as e:
            return False, f"Error creating survey: {str(e)}"
    
    def get_surveys(self, user_email: str = None, status_filter: str = 'all') -> List[Dict]:
        """Get surveys based on user permissions and filters"""
        try:
            data = self.load_surveys_data()
            surveys = data.get('surveys', [])
            
            # Filter by status
            if status_filter != 'all':
                surveys = [s for s in surveys if s['status'] == status_filter]
            
            # Filter by target audience if user specified
            if user_email:
                user = SessionManager.get_current_user()
                if user:
                    user_role = user.get('role', '')
                    
                    # Filter surveys user is eligible for
                    eligible_surveys = []
                    for survey in surveys:
                        target_audience = survey.get('target_audience', [])
                        
                        if ('all_citizens' in target_audience or 
                            'public' in target_audience or
                            user_role in target_audience or
                            user_email == survey.get('creator_email')):
                            eligible_surveys.append(survey)
                    
                    surveys = eligible_surveys
            
            # Sort by creation date (newest first)
            surveys.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return surveys
            
        except Exception as e:
            print(f"Error getting surveys: {e}")
            return []
    
    def submit_survey_response(self, survey_id: str, responses: Dict[str, Any], 
                              respondent_email: str = None) -> Tuple[bool, str]:
        """Submit survey response with privacy protection and validation"""
        
        try:
            data = self.load_surveys_data()
            
            # Find survey
            survey = None
            for s in data['surveys']:
                if s['id'] == survey_id:
                    survey = s
                    break
            
            if not survey:
                return False, "Survey not found"
            
            # Check if survey is active
            if survey['status'] != 'active':
                return False, "Survey is not currently active"
            
            # Check if survey has ended
            end_time = datetime.fromisoformat(survey['ends_at'])
            if datetime.now() > end_time:
                return False, "Survey has ended"
            
            # Validate authentication requirements
            if survey['settings']['require_authentication'] and not respondent_email:
                return False, "Authentication required for this survey"
            
            # Check for duplicate responses if not allowed
            if (not survey['settings']['allow_multiple_responses'] and 
                respondent_email and 
                self.has_responded(survey_id, respondent_email)):
                return False, "You have already responded to this survey"
            
            # Validate responses
            if not self.validate_survey_responses(survey['questions'], responses):
                return False, "Invalid response format"
            
            # Create response record
            response_id = str(uuid.uuid4())
            response_record = {
                'id': response_id,
                'survey_id': survey_id,
                'responses': responses,
                'submitted_at': datetime.now().isoformat(),
                'privacy_mode': survey['privacy_mode']
            }
            
            # Add demographic info if authenticated and survey requires it
            if (respondent_email and survey['settings']['demographic_collection']):
                user = SessionManager.get_current_user()
                if user:
                    response_record['demographics'] = {
                        'role': user.get('role', 'Unknown'),
                        'city': user.get('city', 'Unknown'),
                        'state': user.get('state', 'Unknown')
                    }
            
            # Store response (with or without identifying information)
            if survey['privacy_mode'] == 'anonymous':
                # Anonymous - no email stored
                response_record['respondent_hash'] = hash(respondent_email or 'anonymous')
            else:
                # Verified or public - store email
                response_record['respondent_email'] = respondent_email
            
            # Add to responses
            if survey_id not in data['responses']:
                data['responses'][survey_id] = []
            
            data['responses'][survey_id].append(response_record)
            
            # Update survey response count
            for s in data['surveys']:
                if s['id'] == survey_id:
                    s['response_count'] = len(data['responses'][survey_id])
                    break
            
            # Update analytics
            data['analytics']['total_responses'] += 1
            data['last_updated'] = datetime.now().isoformat()
            
            # Save data
            if self.save_surveys_data(data):
                # Record on blockchain
                blockchain_data = {
                    'survey_id': survey_id,
                    'response_id': response_id,
                    'privacy_mode': survey['privacy_mode'],
                    'response_count': len(data['responses'][survey_id])
                }
                
                # Only log email hash for privacy
                if respondent_email:
                    blockchain_data['respondent_hash'] = str(hash(respondent_email))
                
                Blockchain.add_page(
                    action_type="survey_response_submitted",
                    data=blockchain_data,
                    user_email=respondent_email or 'anonymous'
                )
                
                return True, "Survey response submitted successfully"
            else:
                return False, "Failed to save response"
                
        except Exception as e:
            return False, f"Error submitting response: {str(e)}"
    
    def get_survey_results(self, survey_id: str, requester_email: str) -> Optional[Dict]:
        """Get survey results with role-based access control"""
        
        try:
            data = self.load_surveys_data()
            
            # Find survey
            survey = None
            for s in data['surveys']:
                if s['id'] == survey_id:
                    survey = s
                    break
            
            if not survey:
                return None
            
            # Check access permissions
            user = SessionManager.get_current_user()
            if not user or user['email'] != requester_email:
                return None
            
            # Check if user can view results
            can_view = (
                requester_email == survey['creator_email'] or  # Creator
                self.can_view_all_results(user.get('role', '')) or  # Admin/Elder
                survey['settings']['show_results_live']  # Public results
            )
            
            if not can_view:
                return None
            
            # Get responses
            responses = data['responses'].get(survey_id, [])
            
            # Calculate statistics
            results = {
                'survey': survey,
                'total_responses': len(responses),
                'questions_analysis': self.analyze_survey_responses(survey['questions'], responses),
                'demographic_breakdown': self.get_demographic_breakdown(responses),
                'response_timeline': self.get_response_timeline(responses),
                'completion_rate': self.calculate_completion_rate(survey['questions'], responses)
            }
            
            return results
            
        except Exception as e:
            print(f"Error getting survey results: {e}")
            return None
    
    def analyze_survey_responses(self, questions: List[Dict], responses: List[Dict]) -> List[Dict]:
        """Perform statistical analysis on survey responses"""
        
        analysis = []
        
        for i, question in enumerate(questions):
            question_analysis = {
                'question': question['question'],
                'type': question['type'],
                'total_responses': 0,
                'statistics': {}
            }
            
            # Collect responses for this question
            question_responses = []
            for response in responses:
                if str(i) in response['responses']:
                    question_responses.append(response['responses'][str(i)])
            
            question_analysis['total_responses'] = len(question_responses)
            
            if question['type'] == 'multiple_choice':
                # Count each option
                option_counts = {}
                for response in question_responses:
                    if response in option_counts:
                        option_counts[response] += 1
                    else:
                        option_counts[response] = 1
                
                question_analysis['statistics'] = {
                    'option_counts': option_counts,
                    'percentages': {
                        option: (count / len(question_responses)) * 100 
                        if question_responses else 0
                        for option, count in option_counts.items()
                    }
                }
            
            elif question['type'] in ['rating', 'scale']:
                # Calculate average, min, max
                numeric_responses = [float(r) for r in question_responses if r.replace('.', '').isdigit()]
                
                if numeric_responses:
                    question_analysis['statistics'] = {
                        'average': sum(numeric_responses) / len(numeric_responses),
                        'minimum': min(numeric_responses),
                        'maximum': max(numeric_responses),
                        'count': len(numeric_responses)
                    }
            
            elif question['type'] == 'text':
                # Text analysis
                question_analysis['statistics'] = {
                    'response_count': len(question_responses),
                    'average_length': sum(len(r) for r in question_responses) / len(question_responses) if question_responses else 0
                }
            
            analysis.append(question_analysis)
        
        return analysis
    
    def get_demographic_breakdown(self, responses: List[Dict]) -> Dict[str, Any]:
        """Analyze demographic data from responses"""
        
        breakdown = {
            'by_role': {},
            'by_location': {},
            'total_with_demographics': 0
        }
        
        for response in responses:
            if 'demographics' in response:
                breakdown['total_with_demographics'] += 1
                
                # Role breakdown
                role = response['demographics'].get('role', 'Unknown')
                breakdown['by_role'][role] = breakdown['by_role'].get(role, 0) + 1
                
                # Location breakdown
                city = response['demographics'].get('city', 'Unknown')
                state = response['demographics'].get('state', 'Unknown')
                location = f"{city}, {state}"
                breakdown['by_location'][location] = breakdown['by_location'].get(location, 0) + 1
        
        return breakdown
    
    def get_response_timeline(self, responses: List[Dict]) -> List[Dict]:
        """Create timeline of response submission"""
        
        timeline = []
        responses_by_date = {}
        
        for response in responses:
            date = response['submitted_at'][:10]  # YYYY-MM-DD
            responses_by_date[date] = responses_by_date.get(date, 0) + 1
        
        for date, count in sorted(responses_by_date.items()):
            timeline.append({
                'date': date,
                'responses': count
            })
        
        return timeline
    
    def calculate_completion_rate(self, questions: List[Dict], responses: List[Dict]) -> float:
        """Calculate survey completion rate"""
        
        if not responses:
            return 0.0
        
        total_questions = len(questions)
        completed_responses = 0
        
        for response in responses:
            answered_questions = len([q for q in response['responses'].values() if q])
            completion_rate = answered_questions / total_questions
            
            if completion_rate >= 0.8:  # 80% completion threshold
                completed_responses += 1
        
        return (completed_responses / len(responses)) * 100
    
    def validate_survey_responses(self, questions: List[Dict], responses: Dict[str, Any]) -> bool:
        """Validate survey responses against question structure"""
        
        try:
            for i, question in enumerate(questions):
                question_key = str(i)
                
                if question.get('required', False) and question_key not in responses:
                    return False
                
                if question_key in responses:
                    response_value = responses[question_key]
                    
                    # Type-specific validation
                    if question['type'] == 'multiple_choice':
                        valid_options = question.get('options', [])
                        if valid_options and response_value not in valid_options:
                            return False
                    
                    elif question['type'] in ['rating', 'scale']:
                        try:
                            rating = float(response_value)
                            min_val = question.get('min_value', 1)
                            max_val = question.get('max_value', 5)
                            
                            if not (min_val <= rating <= max_val):
                                return False
                        except (ValueError, TypeError):
                            return False
            
            return True
            
        except Exception as e:
            print(f"Response validation error: {e}")
            return False
    
    def has_responded(self, survey_id: str, user_email: str) -> bool:
        """Check if user has already responded to survey"""
        
        try:
            data = self.load_surveys_data()
            responses = data['responses'].get(survey_id, [])
            
            for response in responses:
                if response.get('respondent_email') == user_email:
                    return True
                
                # Check hash for anonymous surveys
                if response.get('respondent_hash') == hash(user_email):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking response history: {e}")
            return False
    
    def can_create_survey(self, role: str) -> bool:
        """Check if user role can create surveys"""
        authorized_roles = [
            'Contract Elder', 'Contract Representative', 'Contract Senator', 
            'Contract Founder', 'CEO', 'Admin'
        ]
        return role in authorized_roles
    
    def can_view_all_results(self, role: str) -> bool:
        """Check if user role can view all survey results"""
        admin_roles = ['Contract Elder', 'Contract Founder', 'CEO', 'Admin']
        return role in admin_roles
    
    def get_survey_statistics(self) -> Dict[str, Any]:
        """Get overall survey system statistics"""
        
        try:
            data = self.load_surveys_data()
            
            return {
                'total_surveys': data['analytics'].get('total_surveys', 0),
                'active_surveys': data['analytics'].get('active_surveys', 0),
                'total_responses': data['analytics'].get('total_responses', 0),
                'surveys_by_type': self.count_surveys_by_type(),
                'recent_activity': self.get_recent_survey_activity(),
                'participation_trends': self.calculate_participation_trends()
            }
            
        except Exception as e:
            print(f"Error getting survey statistics: {e}")
            return {}
    
    def count_surveys_by_type(self) -> Dict[str, int]:
        """Count surveys by type"""
        
        try:
            data = self.load_surveys_data()
            surveys = data.get('surveys', [])
            
            type_counts = {}
            for survey in surveys:
                survey_type = survey.get('survey_type', 'unknown')
                type_counts[survey_type] = type_counts.get(survey_type, 0) + 1
            
            return type_counts
            
        except Exception:
            return {}
    
    def get_recent_survey_activity(self) -> List[Dict]:
        """Get recent survey activity"""
        
        try:
            data = self.load_surveys_data()
            surveys = data.get('surveys', [])
            
            # Get surveys created in last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            recent_surveys = []
            for survey in surveys:
                created_at = datetime.fromisoformat(survey['created_at'])
                if created_at > thirty_days_ago:
                    recent_surveys.append({
                        'title': survey['title'],
                        'created_at': survey['created_at'],
                        'response_count': survey['response_count'],
                        'creator': survey['creator_email']
                    })
            
            return sorted(recent_surveys, key=lambda x: x['created_at'], reverse=True)
            
        except Exception:
            return []
    
    def calculate_participation_trends(self) -> Dict[str, float]:
        """Calculate participation trends and rates"""
        
        try:
            data = self.load_surveys_data()
            surveys = data.get('surveys', [])
            responses = data.get('responses', {})
            
            if not surveys:
                return {'average_response_rate': 0.0, 'trend': 'stable'}
            
            total_responses = sum(len(responses.get(s['id'], [])) for s in surveys)
            average_responses_per_survey = total_responses / len(surveys) if surveys else 0
            
            # Simple trend calculation (would be more sophisticated in production)
            recent_surveys = [s for s in surveys 
                            if datetime.fromisoformat(s['created_at']) > datetime.now() - timedelta(days=30)]
            
            if recent_surveys:
                recent_responses = sum(len(responses.get(s['id'], [])) for s in recent_surveys)
                recent_average = recent_responses / len(recent_surveys)
                
                if recent_average > average_responses_per_survey * 1.1:
                    trend = 'increasing'
                elif recent_average < average_responses_per_survey * 0.9:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            return {
                'average_response_rate': average_responses_per_survey,
                'trend': trend,
                'recent_activity': len(recent_surveys)
            }
            
        except Exception:
            return {'average_response_rate': 0.0, 'trend': 'stable'}