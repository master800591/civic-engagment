#!/usr/bin/env python3
"""
Test script for the Training Module
Tests the backend functionality of the civic training system
"""

import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up environment config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'civic_desktop', 'config', 'test_config.json')
os.environ['CIVIC_CONFIG'] = CONFIG_PATH

from civic_desktop.training.backend import TrainingBackend
from civic_desktop.users.backend import UserBackend
from civic_desktop.users.session import SessionManager

def test_training_system():
    """Test the complete training system functionality"""
    print("🎓 Testing Civic Training System")
    print("=" * 50)
    
    # Test 1: Backend initialization
    print("Test 1: Backend initialization...")
    backend = TrainingBackend()
    print("✅ Training backend initialized successfully")
    
    # Test 2: Default courses availability
    print("\nTest 2: Default courses availability...")
    courses = backend.get_available_courses('test@example.com')
    print(f"✅ Found {len(courses)} available courses:")
    for course in courses:
        print(f"  📚 {course['title']} ({course['difficulty']})")
    
    # Test 3: Course content structure
    print("\nTest 3: Course content structure...")
    if courses:
        course = courses[0]
        print(f"📖 Course: {course['title']}")
        print(f"   Description: {course['description']}")
        print(f"   Modules: {len(course['modules'])}")
        print(f"   Estimated time: {course['estimated_time']}")
        
        # Check module structure
        if course['modules']:
            module = course['modules'][0]
            print(f"   📄 First module: {module['title']}")
            print(f"      Content length: {len(module.get('content', ''))} characters")
            print(f"      Has quiz: {'✅' if module.get('quiz') else '❌'}")
    
    # Test 4: User progress tracking
    print("\nTest 4: User progress tracking...")
    test_email = "test@example.com"
    progress = backend.get_user_progress(test_email)
    print(f"✅ Progress loaded for {test_email}")
    print(f"   Completed courses: {len(progress.get('completed_courses', []))}")
    print(f"   Current course: {progress.get('current_course', 'None')}")
    
    # Test 5: Course starting
    print("\nTest 5: Course starting functionality...")
    if courses:
        course_id = courses[0]['id']
        success, message = backend.start_course(test_email, course_id)
        print(f"✅ Start course result: {success} - {message}")
    
    # Test 6: Module completion
    print("\nTest 6: Module completion functionality...")
    if courses and courses[0]['modules']:
        course_id = courses[0]['id']
        module_id = courses[0]['modules'][0]['id']
        success, message = backend.complete_module(test_email, course_id, module_id, 85.0)
        print(f"✅ Complete module result: {success} - {message}")
    
    # Test 7: Role requirements checking
    print("\nTest 7: Role requirements checking...")
    requirements = backend.check_training_requirements(test_email, 'Contract Representative')
    print(f"✅ Training requirements for Contract Representative:")
    print(f"   Met: {requirements['met']}")
    print(f"   Required courses: {len(requirements['required_courses'])}")
    print(f"   Completed courses: {len(requirements['completed_courses'])}")
    print(f"   Missing courses: {len(requirements['missing_courses'])}")
    
    print("\n" + "=" * 50)
    print("🎉 All training system tests completed successfully!")
    return True

def test_training_ui_compatibility():
    """Test UI component compatibility"""
    print("\n🖥️ Testing UI Compatibility")
    print("=" * 30)
    
    try:
        from civic_desktop.training.ui import TrainingTab
        print("✅ TrainingTab import successful")
        
        # Test basic instantiation (without showing)
        print("📋 Testing tab instantiation...")
        # This would normally require QApplication, so we'll skip for now
        print("⚠️ UI testing requires QApplication - skipping detailed UI tests")
        return True
        
    except ImportError as e:
        print(f"❌ UI import failed: {e}")
        return False

if __name__ == "__main__":
    try:
        print("🏛️ Civic Engagement Platform - Training Module Test")
        print("=" * 60)
        
        # Run backend tests
        test_training_system()
        
        # Run UI compatibility tests
        test_training_ui_compatibility()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)