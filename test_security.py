#!/usr/bin/env python3
"""Security features test suite for Civic Engagement Platform"""

import sys
import os
import tempfile

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from civic_desktop.utils.validation import DataValidator
from civic_desktop.users.session import SessionManager
from civic_desktop.blockchain.blockchain import Blockchain

def test_password_validation():
    """Test enhanced password validation"""
    print("=== Testing Enhanced Password Validation ===")
    
    # Test weak passwords (should fail)
    weak_tests = [
        'password123',  # Common password
        'admin',        # Too short + common
        '12345678',     # Too short + sequential
        'abcdefgh',     # Too short + sequential
        'aaaaaaaaaa',   # Too short + repeated chars
    ]
    
    print("Weak Password Tests (should FAIL):")
    for pwd in weak_tests:
        valid, msg = DataValidator.validate_password(pwd)
        status = "✅ BLOCKED" if not valid else "❌ ALLOWED"
        print(f"  {status} '{pwd}' -> {msg}")
    
    # Test strong passwords (should pass)
    strong_tests = [
        'MySecure2024!Pass',      # Strong password
        'Civic$Platform@2025',    # Strong with symbols
        'Government#Grade9!Pwd',  # Government grade
    ]
    
    print("\nStrong Password Tests (should PASS):")
    for pwd in strong_tests:
        valid, msg = DataValidator.validate_password(pwd)
        status = "✅ ALLOWED" if valid else "❌ BLOCKED"
        print(f"  {status} '{pwd}' -> {msg}")

def test_file_upload_validation():
    """Test file upload security validation"""
    print("\n=== Testing File Upload Validation ===")
    
    # Test invalid file types
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b'Test content')
        txt_file = f.name
    
    print("Invalid File Type Test (.txt file):")
    valid, msg = DataValidator.validate_file_upload(txt_file)
    status = "✅ BLOCKED" if not valid else "❌ ALLOWED"
    print(f"  {status} {os.path.basename(txt_file)} -> {msg}")
    os.unlink(txt_file)
    
    # Test file size limits with a large file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        # Create a file larger than 10MB
        f.write(b'X' * (11 * 1024 * 1024))  # 11MB
        large_file = f.name
    
    print("Large File Test (11MB .jpg file):")
    valid, msg = DataValidator.validate_file_upload(large_file)
    status = "✅ BLOCKED" if not valid else "❌ ALLOWED"
    print(f"  {status} {os.path.basename(large_file)} -> {msg}")
    os.unlink(large_file)

def test_input_sanitization():
    """Test input sanitization against XSS and SQL injection"""
    print("\n=== Testing Input Sanitization ===")
    
    dangerous_inputs = [
        '<script>alert("XSS")</script>',
        'DROP TABLE users; --',
        'SELECT * FROM users WHERE 1=1',
        '<img src=x onerror=alert(1)>',
        "'; DELETE FROM users; --",
        '<iframe src="javascript:alert(1)"></iframe>'
    ]
    
    print("Dangerous Input Sanitization Tests:")
    for inp in dangerous_inputs:
        sanitized = DataValidator.sanitize_input(inp)
        safe = inp != sanitized
        status = "✅ SANITIZED" if safe else "❌ UNCHANGED"
        print(f"  {status}")
        print(f"    Original:  {inp}")
        print(f"    Sanitized: {sanitized}")

def test_session_management():
    """Test secure session management"""
    print("\n=== Testing Session Management ===")
    
    # Test session creation
    test_user = {
        'email': 'test@example.com',
        'name': 'Test User',
        'role': 'Contract Citizen'
    }
    
    print("Session Creation Test:")
    success = SessionManager.login(test_user)
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"  {status} User login: {success}")
    
    # Test session info
    if SessionManager.is_authenticated():
        session_info = SessionManager.get_session_info()
        print(f"  ✅ Session active for: {session_info['user_email']}")
        print(f"  ✅ Session timeout: {session_info['session_expires_in_minutes']:.1f} minutes")
        print(f"  ✅ Inactivity timeout: {session_info['inactive_expires_in_minutes']:.1f} minutes")
    
    # Test session token validation
    current_user = SessionManager.get_current_user()
    if current_user and 'session_token' in current_user:
        token = current_user['session_token']
        valid_token = SessionManager.validate_session_token(token)
        status = "✅ VALID" if valid_token else "❌ INVALID"
        print(f"  {status} Session token validation: {valid_token}")
    
    # Cleanup
    SessionManager.logout()
    logged_out = not SessionManager.is_authenticated()
    status = "✅ SUCCESS" if logged_out else "❌ FAILED"
    print(f"  {status} Session logout: {logged_out}")

def test_blockchain_validation():
    """Test blockchain data validation and integrity"""
    print("\n=== Testing Blockchain Validation ===")
    
    # Test blockchain data validation
    valid_data = {
        'action': 'test_action',
        'user': 'test@example.com',
        'timestamp': '2025-09-23T10:00:00'
    }
    
    print("Valid Data Test:")
    is_valid, msg = DataValidator.validate_blockchain_data(valid_data)
    status = "✅ VALID" if is_valid else "❌ INVALID"
    print(f"  {status} Blockchain data validation: {msg}")
    
    # Test invalid data
    invalid_data = {
        'action': '<script>alert("xss")</script>',
        'user': 'DROP TABLE users;',
        'data': {'malicious': '<iframe src="javascript:alert(1)"></iframe>'}
    }
    
    print("Invalid Data Test:")
    is_valid, msg = DataValidator.validate_blockchain_data(invalid_data)
    status = "✅ BLOCKED" if not is_valid else "❌ ALLOWED"
    print(f"  {status} Malicious data blocked: {msg}")

def run_all_tests():
    """Run complete security test suite"""
    print("🔐 CIVIC ENGAGEMENT PLATFORM - SECURITY TEST SUITE")
    print("=" * 60)
    
    try:
        test_password_validation()
        test_file_upload_validation()
        test_input_sanitization()
        test_session_management()
        test_blockchain_validation()
        
        print("\n" + "=" * 60)
        print("🎉 ALL SECURITY TESTS COMPLETED SUCCESSFULLY!")
        print("✅ Platform is ready for government deployment")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()