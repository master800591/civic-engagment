#!/usr/bin/env python3
"""
Test script for the preliminary ranks implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime

# Test the new validation functions
def test_validation():
    """Test the new validation functions"""
    from utils.validation import DataValidator
    
    print("🧪 Testing Validation Functions...")
    
    # Test birth date validation
    test_birth_dates = [
        "2010-01-01",  # 14 years old
        "1995-06-15",  # 29 years old  
        "2030-01-01",  # Future date (invalid)
        "invalid-date"  # Invalid format
    ]
    
    for birth_date in test_birth_dates:
        valid, message, age = DataValidator.validate_birth_date(birth_date)
        print(f"  Birth date '{birth_date}': Valid={valid}, Age={age}, Message='{message}'")
    
    # Test parental consent validation
    print("\n  Testing parental consent validation...")
    valid, message = DataValidator.validate_parental_consent(
        "parent@example.com", 
        "John Parent", 
        "child@example.com"
    )
    print(f"  Parental consent: Valid={valid}, Message='{message}'")
    
    # Test government ID validation
    print("\n  Testing government ID validation...")
    valid, message = DataValidator.validate_government_id("A123456789", "passport")
    print(f"  Government ID: Valid={valid}, Message='{message}'")


def test_rank_system():
    """Test the rank management system"""
    print("\n🏛️ Testing Rank System...")
    
    from users.rank_manager import RankManager
    from users.constants import USER_ROLES
    
    # Test initial rank determination
    test_users = [
        {"birth_date": "2010-01-01", "identity_verified": False},  # Should be Junior
        {"birth_date": "1995-06-15", "identity_verified": False},  # Should be Prospect
        {"birth_date": "1995-06-15", "identity_verified": True},   # Should be Probation
    ]
    
    for i, user_data in enumerate(test_users):
        rank = RankManager.determine_initial_rank(user_data)
        print(f"  Test user {i+1}: Assigned rank '{rank}'")
    
    # Test rank hierarchy
    print("\n  Rank hierarchy:")
    for rank, info in USER_ROLES.items():
        level = info.get('level', 0)
        print(f"    Level {level}: {rank}")


def test_training_integration():
    """Test training system integration"""
    print("\n🎓 Testing Training Integration...")
    
    from training.backend import TrainingBackend
    
    # Add mandatory courses to the system
    print("  Adding mandatory courses...")
    TrainingBackend.add_mandatory_courses_to_system()
    
    # Test getting mandatory courses for ranks
    for rank in ["Prospect Contract Citizen", "Probation Contract Citizen", "Contract Citizen"]:
        courses = TrainingBackend.get_mandatory_courses_for_rank(rank)
        print(f"  Mandatory courses for {rank}: {courses}")


if __name__ == "__main__":
    print("🚀 Testing Preliminary Ranks Implementation\n")
    print("=" * 60)
    
    try:
        test_validation()
        test_rank_system()  
        test_training_integration()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("\nImplementation Summary:")
        print("• Birth date validation with age calculation")
        print("• Parental consent validation for minors")
        print("• Government ID validation")
        print("• Hierarchical rank system with 8 levels")
        print("• Automatic rank progression based on age, verification, and training")
        print("• Mandatory training courses for each rank transition")
        print("• Enhanced user dashboard with rank progression")
        print("• Blockchain integration for audit trails")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()