# Task Type Definitions and Categories
# Comprehensive task classification system for civic engagement platform

from enum import Enum
from datetime import datetime, timedelta
import uuid

class TaskType(Enum):
    """Core task types for civic engagement platform"""
    # Blockchain & Validation Tasks
    BLOCKCHAIN_VALIDATION = "blockchain_validation"
    BLOCK_SIGNING = "block_signing" 
    CONSENSUS_PARTICIPATION = "consensus_participation"
    
    # Democratic Participation Tasks
    VOTING_OPPORTUNITY = "voting_opportunity"
    ELECTION_PARTICIPATION = "election_participation"
    REFERENDUM_VOTING = "referendum_voting"
    
    # Governance & Contract Tasks
    CONTRACT_REVIEW = "contract_review"
    AMENDMENT_REVIEW = "amendment_review"
    CONSTITUTIONAL_ANALYSIS = "constitutional_analysis"
    
    # Civic Duties & Service
    JURY_DUTY = "jury_duty"
    MODERATION_REVIEW = "moderation_review"
    CONTENT_FLAGGING = "content_flagging"
    
    # Education & Training
    TRAINING_COMPLETION = "training_completion"
    CERTIFICATION_EXAM = "certification_exam"
    CIVIC_EDUCATION = "civic_education"
    
    # Community Engagement
    COMMUNITY_SERVICE = "community_service"
    PUBLIC_COMMENT = "public_comment"
    TOWN_HALL_PARTICIPATION = "town_hall_participation"
    
    # Administrative Tasks
    PROFILE_UPDATE = "profile_update"
    DOCUMENT_SUBMISSION = "document_submission"
    VERIFICATION_PROCESS = "verification_process"

class TaskCategory(Enum):
    """Task categories for organization and filtering"""
    VALIDATION = "validation"
    VOTING = "voting" 
    CONTRACTS = "contracts"
    MODERATION = "moderation"
    EDUCATION = "education"
    COMMUNITY = "community"
    ADMINISTRATIVE = "administrative"

class TaskPriority(Enum):
    """Task priority levels with urgency indicators"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class TaskStatus(Enum):
    """Task completion status tracking"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class ValidationLevel(Enum):
    """Blockchain validation levels for multi-level validation"""
    FOUNDER = "founder"
    CITY = "city"
    STATE = "state"
    COUNTRY = "country"
    GOVERNMENT = "government"

class RewardType(Enum):
    """Reward types for task completion"""
    CIVIC_TOKENS = "civic_tokens"
    PARTICIPATION_CREDITS = "participation_credits"
    GOVERNANCE_TOKENS = "governance_tokens"
    SERVICE_TOKENS = "service_tokens"
    CERTIFICATION_CREDITS = "certification_credits"
    REPUTATION_POINTS = "reputation_points"

# Task Type Configuration and Metadata
TASK_TYPE_CONFIG = {
    TaskType.BLOCKCHAIN_VALIDATION: {
        'category': TaskCategory.VALIDATION,
        'description': 'Validate blockchain transactions and consensus',
        'default_timeout': timedelta(hours=48),
        'reward_type': RewardType.CIVIC_TOKENS,
        'reward_amount': 10,
        'required_role': 'contract_member',
        'skill_requirements': ['blockchain_literacy', 'cryptographic_basics'],
        'estimated_time': timedelta(minutes=15),
        'can_be_deferred': True,
        'requires_training': False,
        'multi_user': True,  # Multiple users can work on this task
        'approval_required': False
    },
    
    TaskType.VOTING_OPPORTUNITY: {
        'category': TaskCategory.VOTING,
        'description': 'Participate in democratic elections and referendums',
        'default_timeout': 'election_deadline',  # Dynamic based on election
        'reward_type': RewardType.PARTICIPATION_CREDITS,
        'reward_amount': 5,
        'required_role': 'contract_member',
        'skill_requirements': ['civic_literacy'],
        'estimated_time': timedelta(minutes=10),
        'can_be_deferred': False,
        'requires_training': False,
        'multi_user': False,  # Individual voting
        'approval_required': False
    },
    
    TaskType.CONTRACT_REVIEW: {
        'category': TaskCategory.CONTRACTS,
        'description': 'Review constitutional amendments and governance contracts',
        'default_timeout': timedelta(days=7),
        'reward_type': RewardType.GOVERNANCE_TOKENS,
        'reward_amount': 25,
        'required_role': 'contract_representative',  # Or higher authority
        'skill_requirements': ['constitutional_law', 'governance_principles'],
        'estimated_time': timedelta(hours=2),
        'can_be_deferred': True,
        'requires_training': True,
        'multi_user': True,  # Multiple reviewers
        'approval_required': True  # Requires constitutional compliance
    },
    
    TaskType.JURY_DUTY: {
        'category': TaskCategory.MODERATION,
        'description': 'Participate in content moderation jury service',
        'default_timeout': timedelta(hours=24),
        'reward_type': RewardType.SERVICE_TOKENS,
        'reward_amount': 15,
        'required_role': 'contract_member',
        'skill_requirements': ['community_standards', 'due_process'],
        'estimated_time': timedelta(minutes=30),
        'can_be_deferred': True,
        'requires_training': True,
        'multi_user': True,  # Jury of peers
        'approval_required': False
    },
    
    TaskType.TRAINING_COMPLETION: {
        'category': TaskCategory.EDUCATION,
        'description': 'Complete required civic education and training modules',
        'default_timeout': timedelta(days=30),
        'reward_type': RewardType.CERTIFICATION_CREDITS,
        'reward_amount': 20,
        'required_role': 'contract_member',
        'skill_requirements': [],  # Learning opportunity
        'estimated_time': timedelta(hours=1),
        'can_be_deferred': True,
        'requires_training': False,  # This IS the training
        'multi_user': False,  # Individual learning
        'approval_required': False
    }
}

# Geographic Validation Requirements
GEOGRAPHIC_VALIDATION_REQUIREMENTS = {
    ValidationLevel.CITY: {
        'threshold_percentage': 33,
        'minimum_validators': 3,
        'geographic_scope': 'city',
        'description': 'City-level validation by local Contract Members'
    },
    ValidationLevel.STATE: {
        'threshold_percentage': 25,
        'minimum_validators': 5,
        'geographic_scope': 'state',
        'description': 'State-level validation by regional Contract Members'
    },
    ValidationLevel.COUNTRY: {
        'threshold_percentage': 20,
        'minimum_validators': 10,
        'geographic_scope': 'country', 
        'description': 'Country-level validation by national Contract Members'
    },
    ValidationLevel.FOUNDER: {
        'threshold_percentage': 10,
        'minimum_validators': 1,
        'geographic_scope': 'global',
        'description': 'Founder-level validation with constitutional authority'
    }
}

class TaskTypeManager:
    """Manage task types, categories, and configurations"""
    
    @staticmethod
    def get_task_config(task_type: TaskType) -> dict:
        """Get configuration for specific task type"""
        return TASK_TYPE_CONFIG.get(task_type, {})
    
    @staticmethod
    def get_tasks_by_category(category: TaskCategory) -> list:
        """Get all task types in a specific category"""
        return [
            task_type for task_type, config in TASK_TYPE_CONFIG.items()
            if config.get('category') == category
        ]
    
    @staticmethod
    def get_tasks_for_role(role: str) -> list:
        """Get available task types for user role"""
        available_tasks = []
        
        for task_type, config in TASK_TYPE_CONFIG.items():
            required_role = config.get('required_role')
            
            # Check if user role meets requirements
            if TaskTypeManager.role_meets_requirement(role, required_role):
                available_tasks.append(task_type)
        
        return available_tasks
    
    @staticmethod
    def role_meets_requirement(user_role: str, required_role: str) -> bool:
        """Check if user role meets task requirements"""
        
        # Role hierarchy for task assignment
        role_hierarchy = {
            'contract_member': 1,
            'contract_representative': 2, 
            'contract_senator': 3,
            'contract_elder': 4,
            'contract_founder': 5
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    @staticmethod
    def calculate_deadline(task_type: TaskType, creation_time: datetime = None) -> datetime:
        """Calculate task deadline based on type and creation time"""
        
        if creation_time is None:
            creation_time = datetime.now()
        
        config = TASK_TYPE_CONFIG.get(task_type, {})
        timeout = config.get('default_timeout')
        
        if isinstance(timeout, timedelta):
            return creation_time + timeout
        elif timeout == 'election_deadline':
            # Special handling for election deadlines
            return TaskTypeManager.get_next_election_deadline()
        else:
            # Default timeout if not specified
            return creation_time + timedelta(days=7)
    
    @staticmethod
    def get_next_election_deadline() -> datetime:
        """Get next election deadline from election system"""
        # This would integrate with the election system
        # For now, return a default future date
        return datetime.now() + timedelta(days=14)
    
    @staticmethod
    def get_task_reward_info(task_type: TaskType) -> dict:
        """Get reward information for task type"""
        config = TASK_TYPE_CONFIG.get(task_type, {})
        
        return {
            'reward_type': config.get('reward_type'),
            'reward_amount': config.get('reward_amount', 0),
            'description': config.get('description', 'Civic task completion')
        }
    
    @staticmethod
    def validate_task_data(task_type: TaskType, task_data: dict) -> tuple:
        """Validate task data against type requirements"""
        
        config = TASK_TYPE_CONFIG.get(task_type)
        if not config:
            return False, f"Unknown task type: {task_type}"
        
        # Required fields for all tasks
        required_fields = ['assigned_to', 'created_at']
        
        # Task-specific required fields
        if task_type == TaskType.BLOCKCHAIN_VALIDATION:
            required_fields.extend(['validation_request_id', 'validation_level'])
        elif task_type == TaskType.VOTING_OPPORTUNITY:
            required_fields.extend(['election_id', 'ballot_items'])
        elif task_type == TaskType.CONTRACT_REVIEW:
            required_fields.extend(['amendment_id', 'review_requirements'])
        
        # Check for required fields
        missing_fields = [field for field in required_fields if field not in task_data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, "Task data valid"
    
    @staticmethod
    def get_task_display_info(task_type: TaskType) -> dict:
        """Get display information for UI presentation"""
        
        display_icons = {
            TaskType.BLOCKCHAIN_VALIDATION: "🔍",
            TaskType.VOTING_OPPORTUNITY: "🗳️",
            TaskType.CONTRACT_REVIEW: "⚖️", 
            TaskType.JURY_DUTY: "👥",
            TaskType.TRAINING_COMPLETION: "📚",
            TaskType.COMMUNITY_SERVICE: "🤝",
            TaskType.PROFILE_UPDATE: "👤"
        }
        
        config = TASK_TYPE_CONFIG.get(task_type, {})
        
        return {
            'icon': display_icons.get(task_type, "📋"),
            'name': task_type.value.replace('_', ' ').title(),
            'description': config.get('description', 'Civic engagement task'),
            'category': config.get('category', TaskCategory.ADMINISTRATIVE).value,
            'estimated_time': config.get('estimated_time', timedelta(minutes=5)),
            'can_defer': config.get('can_be_deferred', True)
        }

# Task Creation Templates
class TaskTemplate:
    """Template system for creating standardized tasks"""
    
    @staticmethod
    def create_blockchain_validation_task(validation_request_id: str, 
                                        validation_level: ValidationLevel,
                                        assigned_to: str) -> dict:
        """Create blockchain validation task from template"""
        
        task_id = str(uuid.uuid4())
        
        return {
            'task_id': task_id,
            'task_type': TaskType.BLOCKCHAIN_VALIDATION,
            'category': TaskCategory.VALIDATION,
            'assigned_to': assigned_to,
            'created_at': datetime.now().isoformat(),
            'deadline': TaskTypeManager.calculate_deadline(TaskType.BLOCKCHAIN_VALIDATION).isoformat(),
            'priority': TaskPriority.HIGH,
            'status': TaskStatus.PENDING,
            'data': {
                'validation_request_id': validation_request_id,
                'validation_level': validation_level.value,
                'validation_requirements': GEOGRAPHIC_VALIDATION_REQUIREMENTS[validation_level],
                'estimated_completion_time': '15 minutes'
            },
            'rewards': TaskTypeManager.get_task_reward_info(TaskType.BLOCKCHAIN_VALIDATION),
            'completion_percentage': 0,
            'notifications_sent': [],
            'related_tasks': []
        }
    
    @staticmethod
    def create_voting_task(election_id: str, assigned_to: str, 
                          election_data: dict) -> dict:
        """Create voting opportunity task from template"""
        
        task_id = str(uuid.uuid4())
        
        return {
            'task_id': task_id,
            'task_type': TaskType.VOTING_OPPORTUNITY,
            'category': TaskCategory.VOTING,
            'assigned_to': assigned_to,
            'created_at': datetime.now().isoformat(),
            'deadline': election_data.get('voting_deadline', 
                       TaskTypeManager.calculate_deadline(TaskType.VOTING_OPPORTUNITY).isoformat()),
            'priority': TaskPriority.HIGH,
            'status': TaskStatus.PENDING,
            'data': {
                'election_id': election_id,
                'election_type': election_data.get('type', 'general'),
                'ballot_items': election_data.get('ballot_items', []),
                'candidates': election_data.get('candidates', []),
                'jurisdiction': election_data.get('jurisdiction', 'local')
            },
            'rewards': TaskTypeManager.get_task_reward_info(TaskType.VOTING_OPPORTUNITY),
            'completion_percentage': 0,
            'notifications_sent': [],
            'related_tasks': []
        }
    
    @staticmethod
    def create_contract_review_task(amendment_id: str, assigned_to: str,
                                  amendment_data: dict) -> dict:
        """Create contract review task from template"""
        
        task_id = str(uuid.uuid4())
        
        return {
            'task_id': task_id,
            'task_type': TaskType.CONTRACT_REVIEW,
            'category': TaskCategory.CONTRACTS,
            'assigned_to': assigned_to,
            'created_at': datetime.now().isoformat(),
            'deadline': TaskTypeManager.calculate_deadline(TaskType.CONTRACT_REVIEW).isoformat(),
            'priority': TaskPriority.NORMAL,
            'status': TaskStatus.PENDING,
            'data': {
                'amendment_id': amendment_id,
                'amendment_type': amendment_data.get('type', 'constitutional'),
                'review_requirements': [
                    'constitutional_compliance',
                    'impact_analysis', 
                    'precedent_review',
                    'stakeholder_analysis'
                ],
                'amendment_text': amendment_data.get('text', ''),
                'submission_deadline': amendment_data.get('review_deadline')
            },
            'rewards': TaskTypeManager.get_task_reward_info(TaskType.CONTRACT_REVIEW),
            'completion_percentage': 0,
            'notifications_sent': [],
            'related_tasks': []
        }

# Export key classes and functions
__all__ = [
    'TaskType', 'TaskCategory', 'TaskPriority', 'TaskStatus', 'ValidationLevel', 'RewardType',
    'TaskTypeManager', 'TaskTemplate', 'TASK_TYPE_CONFIG', 'GEOGRAPHIC_VALIDATION_REQUIREMENTS'
]