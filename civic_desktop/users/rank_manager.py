"""
Rank Management System for Civic Engagement Platform

Handles user rank progression, verification requirements, and automatic promotions.
"""

from datetime import datetime
from typing import Tuple, Optional, Dict, Any
import os
import json

from civic_desktop.utils.validation import DataValidator
from civic_desktop.users.constants import USER_ROLES, MANDATORY_TRAINING_PATHS, MINIMUM_AGE_FOR_FULL_CITIZENSHIP


class RankManager:
    """Manages user rank progression and verification requirements"""
    
    @staticmethod
    def determine_initial_rank(user_data: Dict[str, Any]) -> str:
        """Determine initial rank based on user registration data"""
        
        # Check if birth date is provided and user is under 18
        birth_date = user_data.get('birth_date', '')
        if birth_date:
            valid, message, age = DataValidator.validate_birth_date(birth_date)
            if valid and age < MINIMUM_AGE_FOR_FULL_CITIZENSHIP:
                return "Junior Contract Citizen"
        
        # Check if identity verification is complete
        if not RankManager._is_identity_verified(user_data):
            return "Prospect Contract Citizen"
        
        # If verified but no training completion data, assign Probation
        return "Probation Contract Citizen"
    
    @staticmethod
    def _is_identity_verified(user_data: Dict[str, Any]) -> bool:
        """Check if user has completed identity verification"""
        # For now, assume not verified unless explicitly marked
        return user_data.get('identity_verified', False)
    
    @staticmethod
    def check_promotion_eligibility(user_email: str) -> Tuple[Optional[str], str]:
        """Check if user can be promoted to next rank"""
        from civic_desktop.users.backend import UserBackend
        from civic_desktop.training.backend import TrainingBackend
        
        user = UserBackend.get_user(user_email)
        if not user:
            return None, "User not found"
        
        current_rank = user.get('role', '')
        
        if current_rank == "Junior Contract Citizen":
            # Check if user has reached 18
            birth_date = user.get('birth_date', '')
            if birth_date:
                valid, message, age = DataValidator.validate_birth_date(birth_date)
                if valid and age >= MINIMUM_AGE_FOR_FULL_CITIZENSHIP:
                    return "Prospect Contract Citizen", "Reached age of majority"
            return None, "Still under 18 years old"
        
        elif current_rank == "Prospect Contract Citizen":
            # Check if verification is complete
            if RankManager._check_verification_complete(user):
                return "Probation Contract Citizen", "Identity verification complete"
            return None, "Identity verification pending"
        
        elif current_rank == "Probation Contract Citizen":
            # Check if mandatory training is complete
            if RankManager._check_training_complete(user_email):
                return "Contract Citizen", "Civic training certification complete"
            return None, "Mandatory training incomplete"
        
        return None, "No promotion available"
    
    @staticmethod
    def _check_verification_complete(user: Dict[str, Any]) -> bool:
        """Check if all verification requirements are met"""
        required_verifications = ["identity", "address", "email"]
        
        for verification in required_verifications:
            status = user.get(f'{verification}_verified', False)
            if not status:
                return False
        
        return True
    
    @staticmethod
    def _check_training_complete(user_email: str) -> bool:
        """Check if mandatory training is complete"""
        try:
            from civic_desktop.training.backend import TrainingBackend
            required_courses = MANDATORY_TRAINING_PATHS.get("Probation_to_Citizen", [])
            
            for course in required_courses:
                if not TrainingBackend.is_course_completed(user_email, course):
                    return False
            
            return True
        except ImportError:
            # If training backend not available, assume incomplete
            return False
    
    @staticmethod
    def promote_user(user_email: str, new_rank: str, reason: str) -> bool:
        """Promote user to new rank with blockchain record"""
        from civic_desktop.users.backend import UserBackend
        
        try:
            # Get current user data
            user = UserBackend.get_user(user_email)
            if not user:
                return False
            
            old_rank = user.get('role', 'Unknown')
            
            # Update user record
            success = UserBackend.update_user_role(user_email, new_rank)
            if not success:
                return False
            
            # Record promotion in blockchain
            try:
                from civic_desktop.blockchain.blockchain import Blockchain
                Blockchain.add_page(
                    action_type="rank_promotion",
                    data={
                        'user_email': user_email,
                        'old_rank': old_rank,
                        'new_rank': new_rank,
                        'reason': reason,
                        'promotion_date': datetime.now().isoformat()
                    },
                    user_email=user_email
                )
            except ImportError:
                # Blockchain not available, continue without recording
                pass
            
            return True
            
        except Exception as e:
            print(f"Error promoting user {user_email}: {e}")
            return False
    
    @staticmethod
    def check_permission(user_email: str, permission: str) -> bool:
        """Check if user has specific permission based on their rank"""
        from civic_desktop.users.backend import UserBackend
        
        user = UserBackend.get_user(user_email)
        if not user:
            return False
        
        user_rank = user.get('role', '')
        rank_info = USER_ROLES.get(user_rank, {})
        
        # Check if permission is explicitly granted
        permissions = rank_info.get('permissions', [])
        if permission in permissions:
            return True
        
        # Check if permission is restricted
        restrictions = rank_info.get('restrictions', [])
        if permission in restrictions:
            return False
        
        # Default to false for unknown permissions
        return False
    
    @staticmethod
    def get_rank_info(rank: str) -> Dict[str, Any]:
        """Get detailed information about a rank"""
        return USER_ROLES.get(rank, {})
    
    @staticmethod
    def get_next_rank_requirements(user_email: str) -> Dict[str, Any]:
        """Get requirements for promotion to next rank"""
        from civic_desktop.users.backend import UserBackend
        
        user = UserBackend.get_user(user_email)
        if not user:
            return {}
        
        current_rank = user.get('role', '')
        next_rank, reason = RankManager.check_promotion_eligibility(user_email)
        
        if not next_rank:
            return {"message": reason, "requirements": []}
        
        next_rank_info = USER_ROLES.get(next_rank, {})
        requirements = []
        
        if current_rank == "Junior Contract Citizen":
            birth_date = user.get('birth_date', '')
            if birth_date:
                valid, message, age = DataValidator.validate_birth_date(birth_date)
                if valid:
                    years_until_18 = MINIMUM_AGE_FOR_FULL_CITIZENSHIP - age
                    if years_until_18 > 0:
                        requirements.append(f"Wait {years_until_18} years until 18th birthday")
        
        elif current_rank == "Prospect Contract Citizen":
            required_verifications = ["identity", "address", "email"]
            for verification in required_verifications:
                if not user.get(f'{verification}_verified', False):
                    requirements.append(f"Complete {verification} verification")
        
        elif current_rank == "Probation Contract Citizen":
            required_courses = MANDATORY_TRAINING_PATHS.get("Probation_to_Citizen", [])
            for course in required_courses:
                requirements.append(f"Complete training course: {course}")
        
        return {
            "next_rank": next_rank,
            "requirements": requirements,
            "rank_info": next_rank_info
        }

    @staticmethod
    def auto_check_promotions():
        """Check all users for automatic promotion eligibility"""
        from civic_desktop.users.backend import UserBackend
        
        promoted_users = []
        
        try:
            users = UserBackend.get_all_users()
            
            for user in users:
                user_email = user.get('email', '')
                next_rank, reason = RankManager.check_promotion_eligibility(user_email)
                
                if next_rank:
                    success = RankManager.promote_user(user_email, next_rank, f"Automatic promotion: {reason}")
                    if success:
                        promoted_users.append({
                            'email': user_email,
                            'new_rank': next_rank,
                            'reason': reason
                        })
            
            return promoted_users
            
        except Exception as e:
            print(f"Error during automatic promotion check: {e}")
            return []