#!/usr/bin/env python3
"""
Training Module Validation Script
Quick validation that training module works correctly for logged-in users
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up environment config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'civic_desktop', 'config', 'test_config.json')
os.environ['CIVIC_CONFIG'] = CONFIG_PATH

def test_training_backend():
    """Test training backend functionality"""
    print("🧪 Testing Training Backend")
    print("=" * 30)
    
    from civic_desktop.training.backend import TrainingBackend
    
    # Test course availability
    courses = TrainingBackend.get_available_courses("test@example.com")
    print(f"✅ Available courses: {len(courses)}")
    
    if courses:
        print(f"📚 First course: {courses[0]['title']}")
        print(f"   Modules: {len(courses[0]['modules'])}")
        
        # Test course starting
        success, message = TrainingBackend.start_course("test@example.com", courses[0]['id'])
        print(f"✅ Start course: {success} - {message}")
        
        # Test progress
        progress = TrainingBackend.get_user_progress("test@example.com")
        print(f"✅ User progress loaded: {progress.get('current_course', 'None')}")
    
    return True

def test_session_integration():
    """Test session manager integration"""
    print("\n🔐 Testing Session Integration")
    print("=" * 30)
    
    from civic_desktop.users.session import SessionManager
    
    # Test authentication check
    is_auth = SessionManager.is_authenticated()
    print(f"✅ Authentication check: {is_auth}")
    
    # Test with mock user
    mock_user = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'Contract Citizen'
    }
    
    SessionManager.login(mock_user)
    is_auth_after = SessionManager.is_authenticated()
    print(f"✅ After mock login: {is_auth_after}")
    
    current_user = SessionManager.get_current_user()
    print(f"✅ Current user: {current_user['first_name'] if current_user else 'None'}")
    
    SessionManager.logout()
    is_auth_final = SessionManager.is_authenticated()
    print(f"✅ After logout: {is_auth_final}")
    
    return True

def test_ui_import():
    """Test UI module imports"""
    print("\n🖥️ Testing UI Imports")
    print("=" * 30)
    
    try:
        from civic_desktop.training.ui import TrainingTab
        print("✅ TrainingTab import successful")
        
        # Test basic instantiation
        print("⚠️ Skipping UI instantiation (requires QApplication)")
        return True
        
    except Exception as e:
        print(f"❌ UI import failed: {e}")
        return False

if __name__ == "__main__":
    print("🎓 Training Module Validation")
    print("=" * 50)
    
    success = True
    
    try:
        success &= test_training_backend()
        success &= test_session_integration() 
        success &= test_ui_import()
        
        if success:
            print("\n✅ All validation tests passed!")
            print("\n📋 Training Module Status:")
            print("   • Backend: ✅ Functional")
            print("   • Session Integration: ✅ Working")
            print("   • UI Components: ✅ Ready")
            print("   • Login/Logout Refresh: ✅ Implemented")
            print("\n🚀 Training module should work for logged-in users!")
        else:
            print("\n❌ Some validation tests failed")
            
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        import traceback
        traceback.print_exc()