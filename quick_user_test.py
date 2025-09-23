#!/usr/bin/env python3
"""
Quick User Test for Civic Engagement Platform
Tests basic functionality that should work with GUI application
"""

import sys
import os
import tempfile
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from civic_desktop.users.session import SessionManager
from civic_desktop.users.backend import UserBackend
from civic_desktop.blockchain.blockchain import Blockchain
from civic_desktop.utils.validation import DataValidator

def test_basic_functionality():
    """Test basic platform functionality"""
    print("🚀 CIVIC ENGAGEMENT PLATFORM - QUICK USER TEST")
    print("=" * 60)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Password Validation
    print("\n🔐 Testing Password Validation...")
    tests_total += 1
    
    # Test weak password
    weak_valid, weak_msg = DataValidator.validate_password("weak123")
    # Test strong password  
    strong_valid, strong_msg = DataValidator.validate_password("SecurePassword123!")
    
    if not weak_valid and strong_valid:
        print("✅ Password validation working correctly")
        tests_passed += 1
    else:
        print(f"❌ Password validation failed: weak={weak_valid}, strong={strong_valid}")
        print(f"   Weak message: {weak_msg}")
        print(f"   Strong message: {strong_msg}")
    
    # Test 2: Input Sanitization
    print("\n🛡️ Testing Input Sanitization...")
    tests_total += 1
    
    dangerous_input = '<script>alert("XSS")</script>'
    sanitized = DataValidator.sanitize_input(dangerous_input)
    
    if sanitized != dangerous_input:
        print("✅ Input sanitization working correctly")
        print(f"   Original: {dangerous_input}")
        print(f"   Sanitized: {sanitized}")
        tests_passed += 1
    else:
        print("❌ Input sanitization failed - dangerous input not modified")
    
    # Test 3: File Upload Validation
    print("\n📁 Testing File Upload Validation...")
    tests_total += 1
    
    try:
        # Create a fake executable file
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
            f.write(b'Fake executable')
            exe_path = f.name
        
        valid, message = DataValidator.validate_file_upload(exe_path)
        os.unlink(exe_path)  # Clean up
        
        if not valid:
            print("✅ File upload validation working correctly")
            print(f"   Blocked executable: {message}")
            tests_passed += 1
        else:
            print("❌ File upload validation failed - executable allowed")
            
    except Exception as e:
        print(f"❌ File upload validation error: {e}")
    
    # Test 4: Blockchain Loading
    print("\n⛓️ Testing Blockchain Loading...")
    tests_total += 1
    
    try:
        chain_data = Blockchain.load_chain()
        if 'pages' in chain_data:
            page_count = len(chain_data.get('pages', []))
            print(f"✅ Blockchain loaded successfully with {page_count} pages")
            tests_passed += 1
        else:
            print("❌ Blockchain load failed - no pages found")
    except Exception as e:
        print(f"❌ Blockchain load error: {e}")
    
    # Test 5: User Loading (from blockchain)
    print("\n👤 Testing User Loading...")
    tests_total += 1
    
    try:
        users = UserBackend.load_users()
        user_count = len(users)
        print(f"✅ User loading successful - found {user_count} users")
        tests_passed += 1
        
        # Show some user info if available
        if users:
            for i, user in enumerate(users[:3]):  # Show first 3 users
                email = user.get('email', 'Unknown')
                role = user.get('role', 'Unknown')
                print(f"   User {i+1}: {email} ({role})")
                
    except Exception as e:
        print(f"❌ User loading error: {e}")
    
    # Test 6: Session Management
    print("\n🔑 Testing Session Management...")
    tests_total += 1
    
    try:
        # Test session when not authenticated
        is_auth_before = SessionManager.is_authenticated()
        session_info = SessionManager.get_session_info()
        
        # Should not be authenticated and should return proper status
        if not is_auth_before and isinstance(session_info, dict):
            print("✅ Session management working correctly")
            if 'message' in session_info:
                print(f"   Status: {session_info['message']}")
            else:
                print(f"   Authenticated: {session_info.get('authenticated', False)}")
            tests_passed += 1
        else:
            print("❌ Session management unexpected state")
            print(f"   Authenticated: {is_auth_before}")
            print(f"   Session info: {session_info}")
            
    except Exception as e:
        print(f"❌ Session management error: {e}")
    
    # Final Results
    print("\n" + "=" * 60)
    print("📊 QUICK TEST RESULTS")
    print("=" * 60)
    
    success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
    
    print(f"✅ Tests Passed: {tests_passed}/{tests_total}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT: Core platform functionality working!")
    elif success_rate >= 80:
        print("✅ GOOD: Platform mostly functional")
    elif success_rate >= 60:
        print("⚠️ FAIR: Some issues but basic functionality works")
    else:
        print("❌ POOR: Significant functionality problems")
    
    print(f"\nTest Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return success_rate >= 80

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)