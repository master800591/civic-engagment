# Training Backend - Course management, progress tracking, and certification system
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from ..users.backend import UserBackend
from ..users.session import SessionManager
from ..blockchain.blockchain import Blockchain
from ..blockchain.integration_manager import BlockchainIntegrationManager, record_training_action


class TrainingBackend:
    """Backend for managing civic training courses and user progress"""
    
    TRAINING_DB_PATH = os.path.join(os.path.dirname(__file__), 'training_db.json')
    USER_PROGRESS_DB_PATH = os.path.join(os.path.dirname(__file__), 'user_progress_db.json')
    
    @staticmethod
    def load_training_data() -> Dict[str, Any]:
        """Load training courses and content from database"""
        if os.path.exists(TrainingBackend.TRAINING_DB_PATH):
            with open(TrainingBackend.TRAINING_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"courses": [], "last_updated": datetime.now(timezone.utc).isoformat()}
    
    @staticmethod
    def save_training_data(data: Dict[str, Any]) -> None:
        """Save training data to database"""
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(TrainingBackend.TRAINING_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_user_progress() -> Dict[str, Any]:
        """Load user training progress from database"""
        if os.path.exists(TrainingBackend.USER_PROGRESS_DB_PATH):
            with open(TrainingBackend.USER_PROGRESS_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"user_progress": {}, "last_updated": datetime.now(timezone.utc).isoformat()}
    
    @staticmethod
    def save_user_progress(data: Dict[str, Any]) -> None:
        """Save user progress to database"""
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(TrainingBackend.USER_PROGRESS_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def initialize_default_courses() -> None:
        """Initialize the training system with default courses"""
        training_data = {
            "courses": [
                {
                    "id": "civic_fundamentals",
                    "title": "🏛️ Civic Fundamentals",
                    "description": "Essential knowledge for all Contract Citizens",
                    "required_for_roles": ["Contract Citizen"],
                    "estimated_time": "30 minutes",
                    "difficulty": "Beginner",
                    "modules": [
                        {
                            "id": "platform_overview",
                            "title": "Platform Overview",
                            "content": """
                            <h3>Welcome to the Civic Engagement Platform</h3>
                            <p>This platform is designed to enable true democratic participation through:</p>
                            <ul>
                                <li><strong>Transparent Governance:</strong> All actions recorded on blockchain</li>
                                <li><strong>Constitutional Protection:</strong> Rights that cannot be voted away</li>
                                <li><strong>Equal Participation:</strong> Every citizen has a voice in democracy</li>
                                <li><strong>Checks and Balances:</strong> No single person or group has absolute power</li>
                            </ul>
                            """,
                            "quiz": [
                                {
                                    "question": "What technology ensures transparency in governance?",
                                    "options": ["Blockchain", "Email", "Social Media", "Newspapers"],
                                    "correct": 0,
                                    "explanation": "Blockchain provides an immutable record of all governance actions."
                                }
                            ]
                        },
                        {
                            "id": "constitutional_rights",
                            "title": "Constitutional Rights",
                            "content": """
                            <h3>Your Fundamental Rights</h3>
                            <p>As a Contract Citizen, you have inalienable rights:</p>
                            <ul>
                                <li><strong>Free Expression:</strong> Right to speak and debate without fear</li>
                                <li><strong>Due Process:</strong> Fair treatment in all procedures</li>
                                <li><strong>Equal Participation:</strong> Equal access to democratic processes</li>
                                <li><strong>Privacy Protection:</strong> Personal data security</li>
                                <li><strong>Appeal Rights:</strong> Challenge any platform decisions</li>
                            </ul>
                            <p><em>These rights cannot be overridden by any vote or government action.</em></p>
                            """,
                            "quiz": [
                                {
                                    "question": "Can your constitutional rights be voted away by a majority?",
                                    "options": ["Yes, with 51% vote", "Yes, with 75% vote", "No, they are inalienable", "Only by Contract Founders"],
                                    "correct": 2,
                                    "explanation": "Constitutional rights are inalienable and cannot be overridden by any vote or authority."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "representative_training",
                    "title": "🗳️ Representative Leadership",
                    "description": "Training for Contract Representative candidates and elected officials",
                    "required_for_roles": ["Contract Representative"],
                    "prerequisite_courses": ["civic_fundamentals"],
                    "estimated_time": "2 hours",
                    "difficulty": "Intermediate",
                    "modules": [
                        {
                            "id": "legislative_powers",
                            "title": "Legislative Powers and Responsibilities",
                            "content": """
                            <h3>Your Role as a Contract Representative</h3>
                            <p>As an elected Representative, you have significant powers and responsibilities:</p>
                            
                            <h4>Powers:</h4>
                            <ul>
                                <li><strong>Legislative Initiative:</strong> Propose new laws and policies</li>
                                <li><strong>Budget Authority:</strong> Control government spending and resource allocation</li>
                                <li><strong>Impeachment Power:</strong> Remove corrupt officials (60% vote required)</li>
                                <li><strong>Platform Oversight:</strong> Investigate government operations</li>
                            </ul>
                            
                            <h4>Responsibilities:</h4>
                            <ul>
                                <li><strong>Represent Citizens:</strong> Act in the best interests of your constituents</li>
                                <li><strong>Constitutional Compliance:</strong> Ensure all proposals respect constitutional rights</li>
                                <li><strong>Transparency:</strong> Keep citizens informed of your actions and decisions</li>
                                <li><strong>Collaboration:</strong> Work with Senators and other Representatives</li>
                            </ul>
                            """,
                            "quiz": [
                                {
                                    "question": "What percentage of Representatives is needed to impeach an official?",
                                    "options": ["51%", "60%", "67%", "75%"],
                                    "correct": 1,
                                    "explanation": "Impeachment requires a 60% vote of Contract Representatives."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "senator_training",
                    "title": "🏛️ Senate Leadership",
                    "description": "Advanced training for Contract Senator candidates and officials",
                    "required_for_roles": ["Contract Senator"],
                    "prerequisite_courses": ["civic_fundamentals", "representative_training"],
                    "estimated_time": "3 hours",
                    "difficulty": "Advanced",
                    "modules": [
                        {
                            "id": "deliberative_process",
                            "title": "Deliberative Review and Decision Making",
                            "content": """
                            <h3>The Senate's Deliberative Role</h3>
                            <p>Contract Senators provide thoughtful review and check on Representative actions:</p>
                            
                            <h4>Key Responsibilities:</h4>
                            <ul>
                                <li><strong>Legislative Review:</strong> Carefully examine all Representative proposals</li>
                                <li><strong>Deliberative Delay:</strong> Require cooling-off periods for major decisions</li>
                                <li><strong>Confirmation Authority:</strong> Approve key appointments and platform changes</li>
                                <li><strong>Override Power:</strong> Override Elder vetoes with 67% supermajority</li>
                            </ul>
                            
                            <h4>Deliberative Process:</h4>
                            <ol>
                                <li><strong>Initial Review:</strong> Examine proposal for constitutional compliance and wisdom</li>
                                <li><strong>Committee Analysis:</strong> Detailed study of implications and consequences</li>
                                <li><strong>Public Comment:</strong> Gather citizen input on major decisions</li>
                                <li><strong>Final Vote:</strong> Approve, reject, or modify the proposal</li>
                            </ol>
                            """,
                            "quiz": [
                                {
                                    "question": "What majority do Senators need to override an Elder veto?",
                                    "options": ["51%", "60%", "67%", "75%"],
                                    "correct": 2,
                                    "explanation": "Senators need a 67% supermajority to override Elder vetoes."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "elder_training",
                    "title": "👴 Elder Wisdom Council",
                    "description": "Constitutional interpretation and wisdom council training",
                    "required_for_roles": ["Contract Elder"],
                    "prerequisite_courses": ["civic_fundamentals", "representative_training", "senator_training"],
                    "estimated_time": "4 hours",
                    "difficulty": "Expert",
                    "modules": [
                        {
                            "id": "constitutional_interpretation",
                            "title": "Constitutional Interpretation and Judicial Review",
                            "content": """
                            <h3>The Elder's Constitutional Role</h3>
                            <p>Contract Elders serve as the constitutional conscience of the platform:</p>
                            
                            <h4>Primary Duties:</h4>
                            <ul>
                                <li><strong>Constitutional Veto:</strong> Block proposals that violate core principles (60% Elder consensus)</li>
                                <li><strong>Judicial Review:</strong> Interpret governance contracts and resolve disputes</li>
                                <li><strong>Elder Veto:</strong> Override harmful legislative decisions (75% Elder consensus)</li>
                                <li><strong>Appointment Authority:</strong> Nominate candidates for critical positions</li>
                            </ul>
                            
                            <h4>Constitutional Analysis Framework:</h4>
                            <ol>
                                <li><strong>Rights Impact:</strong> Does this affect fundamental citizen rights?</li>
                                <li><strong>Democratic Principles:</strong> Does this strengthen or weaken democracy?</li>
                                <li><strong>Checks and Balances:</strong> Does this concentrate power inappropriately?</li>
                                <li><strong>Long-term Consequences:</strong> What are the implications for future generations?</li>
                            </ol>
                            """,
                            "quiz": [
                                {
                                    "question": "What percentage of Elders is needed for a constitutional veto?",
                                    "options": ["51%", "60%", "67%", "75%"],
                                    "correct": 1,
                                    "explanation": "Constitutional vetoes require 60% of Contract Elders to agree."
                                }
                            ]
                        }
                    ]
                }
            ],
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        TrainingBackend.save_training_data(training_data)
    
    @staticmethod
    def get_available_courses(user_email: str) -> List[Dict[str, Any]]:
        """Get courses available to a user based on their role and completed training"""
        user = UserBackend.get_user_by_email(user_email)
        if not user:
            return []
        
        training_data = TrainingBackend.load_training_data()
        if not training_data.get("courses"):
            TrainingBackend.initialize_default_courses()
            training_data = TrainingBackend.load_training_data()
        
        user_roles = user.get('roles', [])
        progress_data = TrainingBackend.load_user_progress()
        user_progress = progress_data.get("user_progress", {}).get(user_email, {})
        completed_courses = user_progress.get("completed_courses", [])
        
        available_courses = []
        for course in training_data["courses"]:
            # Check if user has required role
            required_roles = course.get("required_for_roles", [])
            if any(role in user_roles for role in required_roles) or not required_roles:
                # Check prerequisites
                prerequisites = course.get("prerequisite_courses", [])
                if all(prereq in completed_courses for prereq in prerequisites):
                    available_courses.append(course)
        
        return available_courses
    
    @staticmethod
    def get_course_by_id(course_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific course by ID"""
        training_data = TrainingBackend.load_training_data()
        for course in training_data.get("courses", []):
            if course["id"] == course_id:
                return course
        return None
    
    @staticmethod
    def get_user_progress(user_email: str) -> Dict[str, Any]:
        """Get training progress for a specific user"""
        progress_data = TrainingBackend.load_user_progress()
        return progress_data.get("user_progress", {}).get(user_email, {
            "completed_courses": [],
            "current_course": None,
            "module_progress": {},
            "quiz_scores": {},
            "certifications": [],
            "total_training_time": 0
        })
    
    @staticmethod
    def start_course(user_email: str, course_id: str) -> Tuple[bool, str]:
        """Start a course for a user"""
        try:
            course = TrainingBackend.get_course_by_id(course_id)
            if not course:
                return False, "Course not found"
            
            # Check if user is eligible
            available_courses = TrainingBackend.get_available_courses(user_email)
            if not any(c["id"] == course_id for c in available_courses):
                return False, "You are not eligible for this course"
            
            # Update user progress
            progress_data = TrainingBackend.load_user_progress()
            if user_email not in progress_data["user_progress"]:
                progress_data["user_progress"][user_email] = {
                    "completed_courses": [],
                    "current_course": None,
                    "module_progress": {},
                    "quiz_scores": {},
                    "certifications": [],
                    "total_training_time": 0
                }
            
            user_progress = progress_data["user_progress"][user_email]
            user_progress["current_course"] = course_id
            user_progress["module_progress"][course_id] = {
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_modules": [],
                "current_module": 0
            }
            
            TrainingBackend.save_user_progress(progress_data)
            
            # Record in blockchain
            Blockchain.add_page(
                data={
                    "action_type": "training_course_started",
                    "user_email": user_email,
                    "course_id": course_id,
                    "course_title": course["title"],
                    "course_description": course["description"],
                    "estimated_time": course["estimated_time"],
                    "difficulty": course["difficulty"],
                    "prerequisite_courses": course.get("prerequisite_courses", []),
                    "required_for_roles": course.get("required_for_roles", []),
                    "modules": [
                        {
                            "id": module["id"],
                            "title": module["title"],
                            "content_hash": hash(module["content"]),  # Store content hash for verification
                            "has_quiz": bool(module.get("quiz", []))
                        }
                        for module in course["modules"]
                    ],
                    "started_at": datetime.now(timezone.utc).isoformat()
                },
                validator=user_email
            )
            
            return True, f"Started course: {course['title']}"
            
        except Exception as e:
            return False, f"Error starting course: {str(e)}"
    
    @staticmethod
    def complete_module(user_email: str, course_id: str, module_id: str, quiz_score: float = 0.0) -> Tuple[bool, str]:
        """Mark a module as completed for a user"""
        try:
            course = TrainingBackend.get_course_by_id(course_id)
            if not course:
                return False, "Course not found"
            
            # Find the specific module
            module = None
            for mod in course["modules"]:
                if mod["id"] == module_id:
                    module = mod
                    break
            
            if not module:
                return False, "Module not found"
            
            progress_data = TrainingBackend.load_user_progress()
            user_progress = progress_data["user_progress"].get(user_email, {})
            
            if course_id not in user_progress.get("module_progress", {}):
                return False, "Course not started"
            
            module_progress = user_progress["module_progress"][course_id]
            if module_id not in module_progress["completed_modules"]:
                module_progress["completed_modules"].append(module_id)
                
                # Record quiz score
                if quiz_score > 0:
                    if course_id not in user_progress["quiz_scores"]:
                        user_progress["quiz_scores"][course_id] = {}
                    user_progress["quiz_scores"][course_id][module_id] = quiz_score
            
            TrainingBackend.save_user_progress(progress_data)
            
            # Record module completion and content on blockchain
            blockchain_data = {
                "action_type": "training_module_completed",
                "user_email": user_email,
                "course_id": course_id,
                "course_title": course["title"],
                "module_id": module_id,
                "module_title": module["title"],
                "module_content": module["content"],  # Store full lesson content
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "content_hash": hash(module["content"])  # Content verification hash
            }
            
            # Add quiz results if available
            if quiz_score > 0 and module.get("quiz"):
                blockchain_data.update({
                    "quiz_taken": True,
                    "quiz_score": quiz_score,
                    "quiz_passed": quiz_score >= 70.0,
                    "quiz_questions": [
                        {
                            "question": q["question"],
                            "options": q["options"],
                            "correct_answer": q["correct"],
                            "explanation": q.get("explanation", "")
                        }
                        for q in module["quiz"]
                    ]
                })
            else:
                blockchain_data["quiz_taken"] = False
            
            # Store on blockchain for permanent record
            Blockchain.add_page(
                data=blockchain_data,
                validator=user_email
            )
            
            # Check if course is completed
            total_modules = len(course["modules"])
            completed_modules = len(module_progress["completed_modules"])
            
            if completed_modules >= total_modules:
                return TrainingBackend.complete_course(user_email, course_id)
            
            return True, f"Module completed: {module['title']} (Score: {quiz_score:.1f}%)"
            
        except Exception as e:
            return False, f"Error completing module: {str(e)}"
    
    @staticmethod
    def complete_course(user_email: str, course_id: str) -> Tuple[bool, str]:
        """Mark a course as completed and issue certification"""
        try:
            course = TrainingBackend.get_course_by_id(course_id)
            if not course:
                return False, "Course not found"
            
            progress_data = TrainingBackend.load_user_progress()
            user_progress = progress_data["user_progress"][user_email]
            
            # Add to completed courses
            if course_id not in user_progress["completed_courses"]:
                user_progress["completed_courses"].append(course_id)
            
            # Issue certification
            certification = {
                "course_id": course_id,
                "course_title": course["title"],
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "certification_id": f"CERT_{course_id}_{user_email}_{datetime.now().strftime('%Y%m%d')}"
            }
            user_progress["certifications"].append(certification)
            
            # Clear current course
            user_progress["current_course"] = None
            
            TrainingBackend.save_user_progress(progress_data)
            
            # Record in blockchain with complete course information
            Blockchain.add_page(
                data={
                    "action_type": "training_course_completed",
                    "user_email": user_email,
                    "course_id": course_id,
                    "course_title": course["title"],
                    "course_description": course["description"],
                    "certification_id": certification["certification_id"],
                    "completed_at": certification["completed_at"],
                    "total_modules": len(course["modules"]),
                    "quiz_scores": user_progress.get("quiz_scores", {}).get(course_id, {}),
                    "average_score": sum(user_progress.get("quiz_scores", {}).get(course_id, {}).values()) / max(1, len(user_progress.get("quiz_scores", {}).get(course_id, {}))),
                    "course_content_summary": {
                        "modules_completed": [
                            {
                                "id": module["id"],
                                "title": module["title"],
                                "content_hash": hash(module["content"])
                            }
                            for module in course["modules"]
                        ]
                    }
                },
                validator=user_email
            )
            
            return True, f"🎉 Course completed! Certification issued: {certification['certification_id']}"
            
        except Exception as e:
            return False, f"Error completing course: {str(e)}"
    
    @staticmethod
    def get_required_training_for_role(role: str) -> List[str]:
        """Get list of required courses for a specific role"""
        training_data = TrainingBackend.load_training_data()
        required_courses = []
        
        for course in training_data.get("courses", []):
            required_roles = course.get("required_for_roles", [])
            if role in required_roles:
                required_courses.append(course["id"])
        
        return required_courses
    
    @staticmethod
    def check_training_requirements(user_email: str, target_role: str) -> Tuple[bool, List[str]]:
        """Check if user has completed required training for a role"""
        user_progress = TrainingBackend.get_user_progress(user_email)
        completed_courses = user_progress.get("completed_courses", [])
        required_courses = TrainingBackend.get_required_training_for_role(target_role)
        
        missing_courses = [course for course in required_courses if course not in completed_courses]
        
        return len(missing_courses) == 0, missing_courses
    
    @staticmethod
    def get_blockchain_training_records(user_email: str) -> List[Dict[str, Any]]:
        """Retrieve all training-related blockchain records for a user"""
        try:
            # Get all blockchain pages
            blockchain_data = Blockchain.load_chain()
            training_records = []
            
            for page in blockchain_data.get("pages", []):
                if page.get("validator") == user_email and page.get("data", {}).get("action_type", "").startswith("training_"):
                    training_records.append({
                        "timestamp": page.get("timestamp"),
                        "action_type": page.get("data", {}).get("action_type"),
                        "data": page.get("data", {}),
                        "hash": page.get("hash"),
                        "index": page.get("index")
                    })
            
            return sorted(training_records, key=lambda x: x["timestamp"])
            
        except Exception as e:
            print(f"Error retrieving blockchain training records: {e}")
            return []
    
    @staticmethod
    def verify_certification_on_blockchain(certification_id: str, user_email: str) -> bool:
        """Verify a certification exists on the blockchain"""
        try:
            training_records = TrainingBackend.get_blockchain_training_records(user_email)
            
            for record in training_records:
                if (record["action_type"] == "training_course_completed" and 
                    record["data"].get("certification_id") == certification_id):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error verifying certification: {e}")
            return False
    
    @staticmethod
    def get_lesson_content_from_blockchain(user_email: str, course_id: str, module_id: str) -> Optional[str]:
        """Retrieve the original lesson content from blockchain records"""
        try:
            training_records = TrainingBackend.get_blockchain_training_records(user_email)
            
            for record in training_records:
                if (record["action_type"] == "training_module_completed" and
                    record["data"].get("course_id") == course_id and
                    record["data"].get("module_id") == module_id):
                    return record["data"].get("module_content")
            
            return None
            
        except Exception as e:
            print(f"Error retrieving lesson content from blockchain: {e}")
            return None