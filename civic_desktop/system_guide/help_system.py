# Contextual Help System
# Comprehensive help and support system with search and troubleshooting

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Import application components
try:
    from main import ENV_CONFIG
    from users.session import SessionManager
    from blockchain.blockchain import Blockchain
except ImportError as e:
    print(f"Warning: Import error in help system: {e}")
    ENV_CONFIG = {}


class ContextualHelpSystem:
    """Comprehensive contextual help and support system"""
    
    def __init__(self):
        self.db_path = ENV_CONFIG.get('help_system_db_path', 'system_guide/help_db.json')
        self.ensure_database()
        self.help_content_cache = {}
        
        # Initialize help content
        self.help_categories = self.load_help_categories()
        self.troubleshooting_guides = self.load_troubleshooting_guides()
    
    def ensure_database(self):
        """Ensure help system database exists"""
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if not os.path.exists(self.db_path):
            initial_data = {
                'help_sessions': [],
                'search_history': [],
                'user_feedback': [],
                'troubleshooting_sessions': [],
                'help_analytics': {}
            }
            
            with open(self.db_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def load_help_categories(self) -> Dict[str, Dict]:
        """Load help content organized by categories"""
        
        return {
            "Getting Started": {
                "description": "Essential information for new users",
                "topics": {
                    "Platform Overview": """
                        # Platform Overview
                        
                        Welcome to the Civic Engagement Platform! This platform enables democratic participation through:
                        
                        ## Key Features
                        - **User Registration**: Secure identity verification and role assignment
                        - **Voting System**: Participate in elections and policy decisions
                        - **Debate Forums**: Engage in structured civic discussions
                        - **Blockchain Transparency**: All actions recorded for accountability
                        - **Moderation System**: Community-driven content oversight
                        
                        ## Getting Started Steps
                        1. Complete user registration with ID verification
                        2. Start the onboarding process for your civic role
                        3. Explore the various tabs and features
                        4. Participate in your first vote or debate
                        5. Complete the civic training modules
                        
                        ## Your Civic Role
                        Your role determines your permissions and responsibilities:
                        - **Contract Members**: Basic voting and participation rights
                        - **Contract Representatives**: Legislative and budgetary authority
                        - **Contract Senators**: Review and oversight responsibilities
                        - **Contract Elders**: Constitutional interpretation and guidance
                        - **Contract Founders**: Platform administration and emergency protocols
                    """,
                    
                    "Navigation Guide": """
                        # Navigation Guide
                        
                        ## Main Interface
                        The platform uses a tabbed interface for easy navigation:
                        
                        ### Core Tabs
                        - **Users**: Login, registration, and user management
                        - **Tasks**: Centralized civic duty management
                        - **Debates**: Topic creation and discussion participation
                        - **Voting**: Election participation and results
                        - **Blockchain**: Transparency and audit trail
                        
                        ### Extended Features
                        - **Contracts**: Governance framework and amendments
                        - **Training**: Civic education modules
                        - **Crypto/Wallet**: CivicCoin management and rewards
                        - **Analytics**: Platform statistics and insights
                        - **Events**: Civic event coordination
                        - **Communications**: Secure messaging system
                        
                        ### Navigation Tips
                        - Use tab shortcuts (Ctrl+1, Ctrl+2, etc.)
                        - Look for context menus (right-click)
                        - Check notification badges for updates
                        - Use the search function in each module
                        - Access quick help from any tab
                    """,
                    
                    "Account Setup": """
                        # Account Setup Guide
                        
                        ## Registration Process
                        1. **Personal Information**: Provide accurate name and contact details
                        2. **Location Verification**: Confirm your civic jurisdiction
                        3. **ID Document Upload**: Government-issued ID for verification
                        4. **Password Creation**: Strong password with security requirements
                        5. **Terms Agreement**: Review and accept platform terms
                        6. **Blockchain Registration**: Automatic secure key generation
                        
                        ## Security Setup
                        - Your private keys are stored locally and never transmitted
                        - Enable two-factor authentication if available
                        - Keep your password secure and change it regularly
                        - Report any suspicious account activity immediately
                        
                        ## Role Assignment
                        - New users start as Contract Members
                        - Participate in elections to advance to higher roles
                        - Each role has specific training requirements
                        - Role changes are recorded on the blockchain
                    """
                }
            },
            
            "User Registration": {
                "description": "Registration process and account management",
                "topics": {
                    "Registration Requirements": """
                        # Registration Requirements
                        
                        ## Required Information
                        - **Full Legal Name**: Must match government ID
                        - **Email Address**: Unique and accessible for notifications
                        - **Physical Address**: For jurisdictional voting eligibility
                        - **Phone Number**: Optional but recommended for security
                        - **Government ID**: Driver's license, passport, or state ID
                        
                        ## Verification Process
                        1. Submit registration form with required information
                        2. Upload clear photo of government-issued ID
                        3. Wait for verification (usually 24-48 hours)
                        4. Receive email confirmation when approved
                        5. Complete initial security setup
                        
                        ## Common Issues
                        - **ID Photo Quality**: Ensure clear, readable image
                        - **Name Matching**: Name must exactly match ID
                        - **Duplicate Accounts**: One account per person only
                        - **Address Verification**: Must be current legal address
                    """,
                    
                    "Troubleshooting Registration": """
                        # Registration Troubleshooting
                        
                        ## Common Problems and Solutions
                        
                        ### "Email Already Registered"
                        - Check if you already have an account
                        - Use password reset if you forgot credentials
                        - Contact support if you believe this is an error
                        
                        ### "ID Verification Failed"
                        - Ensure ID photo is clear and readable
                        - Check that all information matches exactly
                        - Try uploading a different format (JPG, PNG)
                        - Contact support for manual review
                        
                        ### "Invalid Address"
                        - Provide complete street address
                        - Use standard postal abbreviations
                        - Ensure address is within supported jurisdiction
                        
                        ### "Password Requirements Not Met"
                        - Minimum 8 characters
                        - Include uppercase and lowercase letters
                        - Include at least one number
                        - Include at least one special character
                    """
                }
            },
            
            "Voting & Elections": {
                "description": "How to participate in voting and elections",
                "topics": {
                    "Voting Process": """
                        # Voting Process Guide
                        
                        ## Types of Votes
                        - **Policy Proposals**: Vote on platform policies and procedures
                        - **Budget Allocations**: Decide on resource distribution
                        - **Representative Elections**: Choose your representatives
                        - **Constitutional Amendments**: Vote on governance changes
                        - **Emergency Measures**: Respond to urgent platform issues
                        
                        ## How to Vote
                        1. **Check Eligibility**: Ensure you're registered and verified
                        2. **Review Information**: Read proposals and candidate information
                        3. **Access Ballot**: Navigate to the voting interface
                        4. **Make Selection**: Choose your preferred option
                        5. **Confirm Vote**: Review and submit your ballot
                        6. **Verify Recording**: Check that your vote was recorded
                        
                        ## Voting Rights
                        - All verified Contract Members can vote on most issues
                        - Some votes may be restricted by role or jurisdiction
                        - Votes are secret but blockchain-verified for integrity
                        - You can change your vote before the deadline
                    """,
                    
                    "Election Calendar": """
                        # Election Calendar and Schedules
                        
                        ## Regular Elections
                        - **Representative Elections**: Every 2 years
                        - **Senator Elections**: Every 6 years (staggered)
                        - **Elder Elections**: Every 4 years
                        - **Special Elections**: As needed for vacant positions
                        
                        ## Voting Periods
                        - Most votes are open for 7-14 days
                        - Emergency votes may have shorter periods
                        - Constitutional amendments require 30-day periods
                        - Check individual vote details for specific deadlines
                        
                        ## Important Dates
                        - Candidate filing deadlines
                        - Campaign period start/end dates
                        - Voter registration deadlines
                        - Ballot access dates
                        - Results announcement schedules
                    """
                }
            },
            
            "Debate Participation": {
                "description": "Guidelines for participating in civic debates",
                "topics": {
                    "Debate Rules": """
                        # Debate Participation Rules
                        
                        ## Community Guidelines
                        - **Respectful Communication**: Treat all participants with respect
                        - **Factual Arguments**: Support positions with evidence and logic
                        - **No Personal Attacks**: Focus on ideas, not individuals
                        - **Constructive Engagement**: Aim to build understanding
                        - **Topic Relevance**: Stay on topic and avoid derailment
                        
                        ## Participation Process
                        1. **Read Topic Information**: Understand the issue being debated
                        2. **Review Existing Arguments**: See what others have said
                        3. **Prepare Your Position**: Gather facts and organize thoughts
                        4. **Submit Argument**: Post your contribution to the debate
                        5. **Engage Constructively**: Respond to others respectfully
                        6. **Vote on Quality**: Rate argument quality and usefulness
                        
                        ## Moderation
                        - Community members can flag inappropriate content
                        - Moderators review flagged content for violations
                        - Warnings are given for minor violations
                        - Serious violations may result in participation restrictions
                    """,
                    
                    "Creating Quality Arguments": """
                        # Creating Quality Arguments
                        
                        ## Argument Structure
                        1. **Clear Position**: State your stance clearly
                        2. **Supporting Evidence**: Provide facts, data, or examples
                        3. **Logical Reasoning**: Explain how evidence supports position
                        4. **Address Counterarguments**: Acknowledge opposing views
                        5. **Conclusion**: Summarize your main points
                        
                        ## Quality Criteria
                        - **Accuracy**: Information should be factual and verifiable
                        - **Relevance**: Content should directly address the topic
                        - **Clarity**: Arguments should be easy to understand
                        - **Civility**: Tone should be respectful and professional
                        - **Originality**: Add new perspectives or information
                        
                        ## Research Tips
                        - Use reliable, authoritative sources
                        - Check multiple sources for verification
                        - Cite sources when possible
                        - Distinguish between facts and opinions
                        - Consider diverse viewpoints
                    """
                }
            },
            
            "Blockchain & Security": {
                "description": "Understanding blockchain transparency and security",
                "topics": {
                    "Blockchain Basics": """
                        # Blockchain Transparency System
                        
                        ## What is Recorded
                        - All user actions and votes
                        - Debate participation and arguments
                        - Contract amendments and governance decisions
                        - Moderation actions and appeals
                        - System administration activities
                        
                        ## Why Blockchain?
                        - **Transparency**: All actions are publicly verifiable
                        - **Integrity**: Records cannot be altered or deleted
                        - **Accountability**: Officials and users are held accountable
                        - **Auditability**: Complete history is available for review
                        - **Trust**: Reduces need to trust central authorities
                        
                        ## Your Privacy
                        - Personal information is encrypted and protected
                        - Only necessary information is recorded publicly
                        - You control access to your private data
                        - Voting choices may be recorded but kept anonymous
                        - Contact support with privacy concerns
                    """,
                    
                    "Security Best Practices": """
                        # Security Best Practices
                        
                        ## Account Security
                        - Use a strong, unique password
                        - Enable two-factor authentication if available
                        - Log out when using shared computers
                        - Regularly review account activity
                        - Report suspicious activity immediately
                        
                        ## Private Key Security
                        - Your private keys are stored locally on your device
                        - Never share your private keys with anyone
                        - Keep backups in secure locations
                        - Use strong device passwords and encryption
                        - Contact support if you suspect key compromise
                        
                        ## Safe Browsing
                        - Always access the platform from official sources
                        - Be cautious of phishing attempts
                        - Verify URLs before entering credentials
                        - Keep your browser and device updated
                        - Use antivirus software and firewalls
                    """
                }
            },
            
            "Troubleshooting": {
                "description": "Common issues and their solutions",
                "topics": {
                    "Technical Issues": """
                        # Technical Troubleshooting
                        
                        ## Login Problems
                        - **Forgot Password**: Use password reset feature
                        - **Account Locked**: Contact support for assistance
                        - **Browser Issues**: Try clearing cache and cookies
                        - **Connection Problems**: Check internet connectivity
                        
                        ## Interface Issues
                        - **Slow Loading**: Close other applications, check internet speed
                        - **Display Problems**: Try refreshing the page or restarting app
                        - **Missing Features**: Ensure you have appropriate permissions
                        - **Button Not Working**: Try right-clicking for context menu
                        
                        ## Data Issues
                        - **Missing Information**: Check if data finished loading
                        - **Sync Problems**: Wait for blockchain synchronization
                        - **Outdated Information**: Refresh the interface
                        - **Lost Data**: Check if autosave is enabled
                    """,
                    
                    "Performance Optimization": """
                        # Performance Optimization
                        
                        ## System Requirements
                        - Modern web browser or desktop application
                        - Stable internet connection
                        - Adequate available memory (1GB+ recommended)
                        - Updated operating system
                        
                        ## Optimization Tips
                        - Close unnecessary browser tabs
                        - Restart application periodically
                        - Clear browser cache regularly
                        - Disable unnecessary browser extensions
                        - Use wired internet connection when possible
                        
                        ## When to Contact Support
                        - Persistent performance issues
                        - Application crashes or freezes
                        - Data synchronization problems
                        - Features not working as expected
                    """
                }
            },
            
            "Contact Support": {
                "description": "How to get help and contact support",
                "topics": {
                    "Support Options": """
                        # Getting Support
                        
                        ## Self-Help Resources
                        - **Help Documentation**: Comprehensive guides and tutorials
                        - **Video Tutorials**: Step-by-step visual instructions
                        - **Community Forums**: Get help from other users
                        - **FAQ Section**: Answers to frequently asked questions
                        - **Troubleshooting Guides**: Solutions for common problems
                        
                        ## Contacting Support
                        - **Help Desk**: Submit support tickets for technical issues
                        - **Live Chat**: Real-time assistance during business hours
                        - **Email Support**: Detailed assistance for complex issues
                        - **Phone Support**: Urgent issues and account problems
                        - **Community Moderators**: Platform-specific questions
                        
                        ## What to Include
                        - Detailed description of the problem
                        - Steps you've already tried
                        - Screenshots or error messages
                        - Your browser/device information
                        - When the problem started occurring
                    """,
                    
                    "Support Response Times": """
                        # Support Response Times
                        
                        ## Priority Levels
                        - **Critical**: Security issues, account compromise (1-2 hours)
                        - **High**: Cannot access account, voting problems (4-8 hours)
                        - **Medium**: Feature not working, performance issues (1-2 business days)
                        - **Low**: General questions, feature requests (3-5 business days)
                        
                        ## Business Hours
                        - Monday-Friday: 8 AM - 6 PM (local time)
                        - Weekend: Limited support for critical issues
                        - Holidays: Emergency support only
                        
                        ## Emergency Support
                        - Security breaches or account compromise
                        - System-wide outages affecting voting
                        - Data integrity or blockchain issues
                        - Election-related technical problems
                    """
                }
            }
        }
    
    def load_troubleshooting_guides(self) -> Dict[str, Dict]:
        """Load detailed troubleshooting guides"""
        
        return {
            "login_issues": {
                "title": "Login and Authentication Issues",
                "steps": [
                    {
                        "step": 1,
                        "title": "Verify Credentials",
                        "description": "Ensure your email and password are correct",
                        "actions": [
                            "Double-check email spelling",
                            "Try typing password manually",
                            "Check for caps lock",
                            "Verify account exists"
                        ]
                    },
                    {
                        "step": 2,
                        "title": "Clear Browser Data",
                        "description": "Clear cached data that might be causing issues",
                        "actions": [
                            "Clear browser cache",
                            "Clear cookies",
                            "Disable browser extensions",
                            "Try incognito/private mode"
                        ]
                    },
                    {
                        "step": 3,
                        "title": "Reset Password",
                        "description": "Use password reset if credentials don't work",
                        "actions": [
                            "Click 'Forgot Password' link",
                            "Check email for reset instructions",
                            "Follow reset process",
                            "Create new strong password"
                        ]
                    },
                    {
                        "step": 4,
                        "title": "Contact Support",
                        "description": "Get help if other steps don't work",
                        "actions": [
                            "Prepare account information",
                            "Document error messages",
                            "Submit support ticket",
                            "Wait for assistance"
                        ]
                    }
                ]
            },
            
            "voting_problems": {
                "title": "Voting and Election Problems",
                "steps": [
                    {
                        "step": 1,
                        "title": "Check Eligibility",
                        "description": "Verify you're eligible to vote",
                        "actions": [
                            "Confirm account is verified",
                            "Check voting period is active",
                            "Verify role permissions",
                            "Check jurisdiction requirements"
                        ]
                    },
                    {
                        "step": 2,
                        "title": "Access Ballot",
                        "description": "Navigate to the correct voting interface",
                        "actions": [
                            "Go to voting tab",
                            "Select active election",
                            "Verify ballot loads completely",
                            "Check for any error messages"
                        ]
                    },
                    {
                        "step": 3,
                        "title": "Submit Vote",
                        "description": "Complete the voting process",
                        "actions": [
                            "Make your selections",
                            "Review choices carefully",
                            "Submit ballot",
                            "Verify confirmation received"
                        ]
                    },
                    {
                        "step": 4,
                        "title": "Verify Recording",
                        "description": "Confirm your vote was recorded",
                        "actions": [
                            "Check blockchain record",
                            "Verify vote timestamp",
                            "Save confirmation",
                            "Report discrepancies"
                        ]
                    }
                ]
            },
            
            "performance_issues": {
                "title": "Performance and Speed Issues",
                "steps": [
                    {
                        "step": 1,
                        "title": "Check System Resources",
                        "description": "Verify your system has adequate resources",
                        "actions": [
                            "Close unnecessary applications",
                            "Check available memory",
                            "Monitor CPU usage",
                            "Ensure sufficient disk space"
                        ]
                    },
                    {
                        "step": 2,
                        "title": "Optimize Network",
                        "description": "Improve network connectivity",
                        "actions": [
                            "Test internet speed",
                            "Use wired connection",
                            "Close bandwidth-heavy applications",
                            "Restart router if needed"
                        ]
                    },
                    {
                        "step": 3,
                        "title": "Browser Optimization",
                        "description": "Optimize browser performance",
                        "actions": [
                            "Clear browser cache",
                            "Disable unnecessary extensions",
                            "Update browser",
                            "Try different browser"
                        ]
                    },
                    {
                        "step": 4,
                        "title": "Application Restart",
                        "description": "Restart the application",
                        "actions": [
                            "Close application completely",
                            "Wait 30 seconds",
                            "Restart application",
                            "Test performance"
                        ]
                    }
                ]
            }
        }
    
    def search_help_content(self, query: str) -> List[Dict]:
        """Search help content for relevant topics"""
        
        try:
            query_lower = query.lower()
            results = []
            
            # Search through all categories and topics
            for category_name, category_data in self.help_categories.items():
                for topic_name, topic_content in category_data['topics'].items():
                    
                    # Search in topic title and content
                    if (query_lower in topic_name.lower() or 
                        query_lower in topic_content.lower()):
                        
                        # Calculate relevance score
                        relevance = self.calculate_relevance(query_lower, topic_name, topic_content)
                        
                        results.append({
                            'category': category_name,
                            'title': topic_name,
                            'content': topic_content[:500] + "..." if len(topic_content) > 500 else topic_content,
                            'relevance': relevance,
                            'type': 'help_topic'
                        })
            
            # Search troubleshooting guides
            for guide_id, guide_data in self.troubleshooting_guides.items():
                if query_lower in guide_data['title'].lower():
                    results.append({
                        'category': 'Troubleshooting',
                        'title': guide_data['title'],
                        'content': f"Step-by-step guide with {len(guide_data['steps'])} steps",
                        'relevance': 0.8,
                        'type': 'troubleshooting_guide',
                        'guide_id': guide_id
                    })
            
            # Sort by relevance
            results.sort(key=lambda x: x['relevance'], reverse=True)
            
            # Record search
            self.record_search(query, len(results))
            
            return results[:10]  # Return top 10 results
            
        except Exception as e:
            print(f"Error searching help content: {e}")
            return []
    
    def calculate_relevance(self, query: str, title: str, content: str) -> float:
        """Calculate relevance score for search results"""
        
        score = 0.0
        
        # Title match is highly relevant
        if query in title.lower():
            score += 1.0
        
        # Count query word matches in content
        query_words = query.split()
        content_lower = content.lower()
        
        for word in query_words:
            if word in content_lower:
                score += 0.3
        
        # Boost score for exact phrase matches
        if query in content_lower:
            score += 0.5
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_category_help(self, category: str) -> str:
        """Get all help content for a specific category"""
        
        try:
            if category not in self.help_categories:
                return f"Help category '{category}' not found."
            
            category_data = self.help_categories[category]
            content = f"# {category}\n\n{category_data['description']}\n\n"
            
            for topic_name, topic_content in category_data['topics'].items():
                content += f"## {topic_name}\n\n{topic_content}\n\n---\n\n"
            
            # Record category access
            self.record_category_access(category)
            
            return content
            
        except Exception as e:
            return f"Error loading help category: {e}"
    
    def get_troubleshooting_guide(self, guide_id: str) -> Dict:
        """Get detailed troubleshooting guide"""
        
        try:
            if guide_id not in self.troubleshooting_guides:
                return {'error': f"Troubleshooting guide '{guide_id}' not found"}
            
            guide = self.troubleshooting_guides[guide_id]
            
            # Record troubleshooting access
            self.record_troubleshooting_access(guide_id)
            
            return guide
            
        except Exception as e:
            return {'error': f"Error loading troubleshooting guide: {e}"}
    
    def start_help_session(self, user_email: str, help_request: Dict) -> str:
        """Start a help session for tracking and analytics"""
        
        try:
            session_id = str(datetime.now().timestamp())
            
            help_session = {
                'session_id': session_id,
                'user_email': user_email,
                'help_request': help_request,
                'started_at': datetime.now().isoformat(),
                'interactions': [],
                'resolved': False,
                'feedback': None
            }
            
            # Save help session
            data = self.load_data()
            data['help_sessions'].append(help_session)
            self.save_data(data)
            
            # Record on blockchain
            try:
                Blockchain.add_page(
                    action_type="help_session_started",
                    data={
                        'session_id': session_id,
                        'help_request_type': help_request.get('type', 'general'),
                        'category': help_request.get('category'),
                        'urgency': help_request.get('urgency', 'normal')
                    },
                    user_email=user_email
                )
            except Exception as e:
                print(f"Warning: Failed to record help session on blockchain: {e}")
            
            return session_id
            
        except Exception as e:
            print(f"Error starting help session: {e}")
            return None
    
    def record_search(self, query: str, results_count: int):
        """Record search activity for analytics"""
        
        try:
            current_user = SessionManager.get_current_user()
            user_email = current_user.get('email') if current_user else 'anonymous'
            
            search_record = {
                'timestamp': datetime.now().isoformat(),
                'user_email': user_email,
                'query': query,
                'results_count': results_count
            }
            
            data = self.load_data()
            data['search_history'].append(search_record)
            self.save_data(data)
            
        except Exception as e:
            print(f"Error recording search: {e}")
    
    def record_category_access(self, category: str):
        """Record category access for analytics"""
        
        try:
            current_user = SessionManager.get_current_user()
            user_email = current_user.get('email') if current_user else 'anonymous'
            
            access_record = {
                'timestamp': datetime.now().isoformat(),
                'user_email': user_email,
                'category': category,
                'type': 'category_access'
            }
            
            data = self.load_data()
            if 'category_access' not in data:
                data['category_access'] = []
            data['category_access'].append(access_record)
            self.save_data(data)
            
        except Exception as e:
            print(f"Error recording category access: {e}")
    
    def record_troubleshooting_access(self, guide_id: str):
        """Record troubleshooting guide access"""
        
        try:
            current_user = SessionManager.get_current_user()
            user_email = current_user.get('email') if current_user else 'anonymous'
            
            access_record = {
                'timestamp': datetime.now().isoformat(),
                'user_email': user_email,
                'guide_id': guide_id,
                'type': 'troubleshooting_access'
            }
            
            data = self.load_data()
            if 'troubleshooting_access' not in data:
                data['troubleshooting_access'] = []
            data['troubleshooting_access'].append(access_record)
            self.save_data(data)
            
        except Exception as e:
            print(f"Error recording troubleshooting access: {e}")
    
    def get_help_analytics(self) -> Dict:
        """Get help system analytics and usage statistics"""
        
        try:
            data = self.load_data()
            
            analytics = {
                'total_help_sessions': len(data.get('help_sessions', [])),
                'total_searches': len(data.get('search_history', [])),
                'popular_categories': self.get_popular_categories(data),
                'common_search_terms': self.get_common_search_terms(data),
                'troubleshooting_usage': self.get_troubleshooting_usage(data),
                'user_satisfaction': self.get_user_satisfaction(data)
            }
            
            return analytics
            
        except Exception as e:
            print(f"Error getting help analytics: {e}")
            return {}
    
    def get_popular_categories(self, data: Dict) -> List[Dict]:
        """Get most accessed help categories"""
        
        category_counts = {}
        
        for access in data.get('category_access', []):
            category = access['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        popular = [{'category': cat, 'count': count} 
                  for cat, count in category_counts.items()]
        popular.sort(key=lambda x: x['count'], reverse=True)
        
        return popular[:5]
    
    def get_common_search_terms(self, data: Dict) -> List[Dict]:
        """Get most common search terms"""
        
        term_counts = {}
        
        for search in data.get('search_history', []):
            query = search['query'].lower()
            for word in query.split():
                if len(word) > 3:  # Ignore short words
                    term_counts[word] = term_counts.get(word, 0) + 1
        
        common = [{'term': term, 'count': count} 
                 for term, count in term_counts.items()]
        common.sort(key=lambda x: x['count'], reverse=True)
        
        return common[:10]
    
    def get_troubleshooting_usage(self, data: Dict) -> List[Dict]:
        """Get troubleshooting guide usage statistics"""
        
        guide_counts = {}
        
        for access in data.get('troubleshooting_access', []):
            guide_id = access['guide_id']
            guide_counts[guide_id] = guide_counts.get(guide_id, 0) + 1
        
        usage = [{'guide_id': guide, 'count': count} 
                for guide, count in guide_counts.items()]
        usage.sort(key=lambda x: x['count'], reverse=True)
        
        return usage
    
    def get_user_satisfaction(self, data: Dict) -> Dict:
        """Calculate user satisfaction metrics"""
        
        feedback_data = data.get('user_feedback', [])
        
        if not feedback_data:
            return {'average_rating': 0, 'total_feedback': 0}
        
        total_rating = sum(f.get('rating', 0) for f in feedback_data)
        average_rating = total_rating / len(feedback_data)
        
        return {
            'average_rating': round(average_rating, 2),
            'total_feedback': len(feedback_data),
            'positive_feedback': len([f for f in feedback_data if f.get('rating', 0) >= 4]),
            'negative_feedback': len([f for f in feedback_data if f.get('rating', 0) <= 2])
        }
    
    def load_data(self) -> Dict:
        """Load help system database"""
        
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.ensure_database()
            return self.load_data()
        except json.JSONDecodeError:
            self.ensure_database()
            return self.load_data()
    
    def save_data(self, data: Dict):
        """Save help system database"""
        
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving help data: {e}")


# Export the main class
__all__ = ['ContextualHelpSystem']