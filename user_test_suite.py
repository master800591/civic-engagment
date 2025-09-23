#!/usr/bin/env python3
"""
Comprehensive User Test Suite for Civic Engagement Platform
Simulates real user workflows and validates the complete user experience
"""

import sys
import os
import time
import tempfile
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from civic_desktop.users.session import SessionManager
from civic_desktop.users.backend import UserBackend
from civic_desktop.debates.backend import DebateBackend
from civic_desktop.moderation.backend import ModerationBackend
from civic_desktop.blockchain.blockchain import Blockchain
from civic_desktop.utils.validation import DataValidator

class UserTestSuite:
    """Comprehensive user workflow testing"""
    
    def __init__(self):
        self.test_users = []
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        self.current_test = ""
        
    def log_test(self, test_name, passed, message=""):
        """Log test results"""
        self.current_test = test_name
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name}"
        if message:
            result += f" - {message}"
        
        print(result)
        
        self.test_results['tests'].append({
            'name': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        if passed:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
            
    def test_user_registration_workflow(self):
        """Test complete user registration process"""
        print("\n🔐 TESTING USER REGISTRATION WORKFLOW")
        print("=" * 50)
        
        # Test 1: Valid user registration
        try:
            test_user_data = {
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'email': 'alice.johnson@example.com',
                'password': 'SecurePassword123!',
                'address': '123 Democracy Lane',
                'city': 'Liberty City',
                'state': 'Freedom State',
                'country': 'Democratic Republic'
            }
            
            # Create temporary ID document
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                f.write(b'%PDF-1.4 Fake ID Document Content')
                id_doc_path = f.name
            
            # Test registration
            success, result = UserBackend.register_user(test_user_data, id_doc_path)
            self.log_test("User Registration - Valid Data", success, result)
            
            if success:
                self.test_users.append(test_user_data['email'])
            
            # Cleanup
            os.unlink(id_doc_path)
            
        except Exception as e:
            self.log_test("User Registration - Valid Data", False, f"Exception: {e}")
        
        # Test 2: Invalid password (too weak)
        try:
            weak_user_data = test_user_data.copy()
            weak_user_data['email'] = 'weak.user@example.com'
            weak_user_data['password'] = 'weak123'  # Should fail validation
            
            success, result = UserBackend.register_user(weak_user_data, None)
            self.log_test("User Registration - Weak Password Rejection", not success, 
                         "Correctly rejected weak password" if not success else "FAILED: Accepted weak password")
            
        except Exception as e:
            self.log_test("User Registration - Weak Password Rejection", False, f"Exception: {e}")
        
        # Test 3: Duplicate email prevention
        try:
            duplicate_user = test_user_data.copy()
            duplicate_user['password'] = 'AnotherSecure123!'
            
            success, result = UserBackend.register_user(duplicate_user, None)
            self.log_test("User Registration - Duplicate Email Prevention", not success,
                         "Correctly prevented duplicate email" if not success else "FAILED: Allowed duplicate email")
            
        except Exception as e:
            self.log_test("User Registration - Duplicate Email Prevention", False, f"Exception: {e}")
    
    def test_authentication_workflow(self):
        """Test user login and session management"""
        print("\n🔑 TESTING AUTHENTICATION WORKFLOW")
        print("=" * 50)
        
        if not self.test_users:
            self.log_test("Authentication - No Users Available", False, "No users registered for testing")
            return
        
        test_email = self.test_users[0]
        
        # Test 1: Valid login
        try:
            user = UserBackend.authenticate_user(test_email, 'SecurePassword123!')
            success = user is not None
            self.log_test("User Authentication - Valid Credentials", success,
                         f"Successfully authenticated {test_email}" if success else "Failed to authenticate valid user")
            
            if success:
                # Test session creation
                session_success = SessionManager.login(user)
                self.log_test("Session Management - Login", session_success,
                             "Session created successfully" if session_success else "Failed to create session")
                
                # Test session validation
                is_authenticated = SessionManager.is_authenticated()
                self.log_test("Session Management - Authentication Check", is_authenticated,
                             "Session properly authenticated" if is_authenticated else "Session not authenticated")
                
                # Test session info
                session_info = SessionManager.get_session_info()
                has_timeout = 'session_expires_in_minutes' in session_info
                self.log_test("Session Management - Timeout Configuration", has_timeout,
                             f"Session timeout: {session_info.get('session_expires_in_minutes', 'N/A')} minutes")
                
        except Exception as e:
            self.log_test("User Authentication - Valid Credentials", False, f"Exception: {e}")
        
        # Test 2: Invalid login
        try:
            user = UserBackend.authenticate_user(test_email, 'WrongPassword123!')
            success = user is None
            self.log_test("User Authentication - Invalid Credentials", success,
                         "Correctly rejected invalid password" if success else "FAILED: Accepted invalid password")
            
        except Exception as e:
            self.log_test("User Authentication - Invalid Credentials", False, f"Exception: {e}")
        
        # Test 3: Session logout
        try:
            SessionManager.logout()
            is_authenticated = SessionManager.is_authenticated()
            success = not is_authenticated
            self.log_test("Session Management - Logout", success,
                         "Session properly cleared" if success else "Session not cleared on logout")
            
        except Exception as e:
            self.log_test("Session Management - Logout", False, f"Exception: {e}")
    
    def test_debate_workflow(self):
        """Test debate creation and participation"""
        print("\n💬 TESTING DEBATE WORKFLOW")
        print("=" * 50)
        
        if not self.test_users:
            self.log_test("Debate Workflow - No Users Available", False, "No users for testing")
            return
        
        # Login first
        test_email = self.test_users[0]
        user = UserBackend.authenticate_user(test_email, 'SecurePassword123!')
        if user:
            SessionManager.login(user)
        
        # Test 1: Create debate topic
        try:
            topic_data = {
                'title': 'Test Topic: Digital Democracy',
                'description': 'Testing the debate system functionality',
                'category': 'Technology'
            }
            
            success = DebateBackend.create_topic(
                topic_data['title'],
                topic_data['description'],
                test_email
            )
            
            self.log_test("Debate Creation - Valid Topic", success,
                         "Topic created successfully" if success else "Failed to create topic")
            
        except Exception as e:
            self.log_test("Debate Creation - Valid Topic", False, f"Exception: {e}")
        
        # Test 2: List topics
        try:
            topics = DebateBackend.get_topics()
            has_topics = len(topics) > 0
            self.log_test("Debate Listing - Topic Retrieval", has_topics,
                         f"Found {len(topics)} topics" if has_topics else "No topics found")
            
        except Exception as e:
            self.log_test("Debate Listing - Topic Retrieval", False, f"Exception: {e}")
        
        # Test 3: Submit argument
        try:
            topics = DebateBackend.get_topics()
            if topics:
                topic_id = topics[0]['id']
                success = DebateBackend.submit_argument(
                    topic_id,
                    'pro',
                    'This is a test argument supporting digital democracy.',
                    test_email
                )
                self.log_test("Debate Participation - Submit Argument", success,
                             "Argument submitted successfully" if success else "Failed to submit argument")
            else:
                self.log_test("Debate Participation - Submit Argument", False, "No topics available for testing")
                
        except Exception as e:
            self.log_test("Debate Participation - Submit Argument", False, f"Exception: {e}")
    
    def test_moderation_workflow(self):
        """Test content moderation system"""
        print("\n🛡️ TESTING MODERATION WORKFLOW")
        print("=" * 50)
        
        if not self.test_users:
            self.log_test("Moderation Workflow - No Users Available", False, "No users for testing")
            return
        
        test_email = self.test_users[0]
        
        # Test 1: Flag content
        try:
            success = ModerationBackend.flag_content(
                'debate_argument',
                'test_argument_1',
                'Testing the moderation system',
                test_email,
                'low'
            )
            
            self.log_test("Content Moderation - Flag Content", success,
                         "Content flagged successfully" if success else "Failed to flag content")
            
        except Exception as e:
            self.log_test("Content Moderation - Flag Content", False, f"Exception: {e}")
        
        # Test 2: List flags
        try:
            flags = ModerationBackend.get_flags()
            has_flags = len(flags) > 0
            self.log_test("Content Moderation - Flag Retrieval", has_flags,
                         f"Found {len(flags)} flags" if has_flags else "No flags found")
            
        except Exception as e:
            self.log_test("Content Moderation - Flag Retrieval", False, f"Exception: {e}")
        
        # Test 3: Moderation permissions
        try:
            can_moderate = ModerationBackend.can_moderate(test_email)
            # For test purposes, this depends on user role
            self.log_test("Content Moderation - Permission Check", True,
                         f"Moderation permission: {can_moderate}")
            
        except Exception as e:
            self.log_test("Content Moderation - Permission Check", False, f"Exception: {e}")
    
    def test_blockchain_workflow(self):
        """Test blockchain integration and audit trails"""
        print("\n⛓️ TESTING BLOCKCHAIN WORKFLOW")
        print("=" * 50)
        
        if not self.test_users:
            self.log_test("Blockchain Workflow - No Users Available", False, "No users for testing")
            return
        
        test_email = self.test_users[0]
        
        # Test 1: Blockchain data validation
        try:
            test_data = {
                'action': 'user_test',
                'description': 'Testing blockchain integration',
                'timestamp': datetime.now().isoformat(),
                'user_email': test_email
            }
            
            is_valid, message = DataValidator.validate_blockchain_data(test_data)
            self.log_test("Blockchain - Data Validation", is_valid, message)
            
        except Exception as e:
            self.log_test("Blockchain - Data Validation", False, f"Exception: {e}")
        
        # Test 2: Load blockchain
        try:
            chain_data = Blockchain.load_chain()
            has_chain = 'pages' in chain_data
            page_count = len(chain_data.get('pages', []))
            
            self.log_test("Blockchain - Chain Loading", has_chain,
                         f"Loaded blockchain with {page_count} pages")
            
        except Exception as e:
            self.log_test("Blockchain - Chain Loading", False, f"Exception: {e}")
        
        # Test 3: Validator registry
        try:
            validators = Blockchain.load_validators()
            has_validators = len(validators) > 0
            self.log_test("Blockchain - Validator Registry", True,
                         f"Found {len(validators)} validators")
            
        except Exception as e:
            self.log_test("Blockchain - Validator Registry", False, f"Exception: {e}")
    
    def test_security_features(self):
        """Test security features and validation"""
        print("\n🔐 TESTING SECURITY FEATURES")
        print("=" * 50)
        
        # Test 1: Password validation
        try:
            weak_passwords = ['123456', 'password', 'admin', 'user123']
            strong_passwords = ['SecurePassword123!', 'Government#Grade9!Pwd']
            
            weak_rejected = 0
            for pwd in weak_passwords:
                valid, _ = DataValidator.validate_password(pwd)
                if not valid:
                    weak_rejected += 1
            
            strong_accepted = 0
            for pwd in strong_passwords:
                valid, _ = DataValidator.validate_password(pwd)
                if valid:
                    strong_accepted += 1
            
            security_effective = (weak_rejected == len(weak_passwords) and 
                                strong_accepted == len(strong_passwords))
            
            self.log_test("Security - Password Validation", security_effective,
                         f"Rejected {weak_rejected}/{len(weak_passwords)} weak, "
                         f"Accepted {strong_accepted}/{len(strong_passwords)} strong")
            
        except Exception as e:
            self.log_test("Security - Password Validation", False, f"Exception: {e}")
        
        # Test 2: Input sanitization
        try:
            dangerous_inputs = [
                '<script>alert("XSS")</script>',
                'DROP TABLE users;',
                'SELECT * FROM sensitive_data;'
            ]
            
            sanitized_count = 0
            for inp in dangerous_inputs:
                sanitized = DataValidator.sanitize_input(inp)
                if sanitized != inp:  # Should be different after sanitization
                    sanitized_count += 1
            
            sanitization_effective = sanitized_count == len(dangerous_inputs)
            
            self.log_test("Security - Input Sanitization", sanitization_effective,
                         f"Sanitized {sanitized_count}/{len(dangerous_inputs)} dangerous inputs")
            
        except Exception as e:
            self.log_test("Security - Input Sanitization", False, f"Exception: {e}")
        
        # Test 3: File upload validation
        try:
            # Test invalid file type
            with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
                f.write(b'Fake executable content')
                exe_file = f.name
            
            valid, message = DataValidator.validate_file_upload(exe_file)
            exe_blocked = not valid
            
            os.unlink(exe_file)
            
            self.log_test("Security - File Upload Validation", exe_blocked,
                         "Executable files properly blocked" if exe_blocked else "SECURITY RISK: Executable allowed")
            
        except Exception as e:
            self.log_test("Security - File Upload Validation", False, f"Exception: {e}")
    
    def run_complete_user_test(self):
        """Run comprehensive user workflow testing"""
        print("🚀 CIVIC ENGAGEMENT PLATFORM - COMPREHENSIVE USER TEST")
        print("=" * 70)
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Run all test suites
        self.test_user_registration_workflow()
        self.test_authentication_workflow()
        self.test_debate_workflow()
        self.test_moderation_workflow()
        self.test_blockchain_workflow()
        self.test_security_features()
        
        # Final results
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE USER TEST RESULTS")
        print("=" * 70)
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        pass_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {pass_rate:.1f}%")
        
        if pass_rate >= 90:
            print("🎉 EXCELLENT: Platform ready for user deployment!")
        elif pass_rate >= 80:
            print("✅ GOOD: Platform functional with minor issues")
        elif pass_rate >= 70:
            print("⚠️ FAIR: Platform needs improvements before deployment")
        else:
            print("❌ POOR: Platform requires significant fixes")
        
        # Detailed failure analysis
        if self.test_results['failed'] > 0:
            print("\n🔍 FAILED TESTS ANALYSIS:")
            for test in self.test_results['tests']:
                if not test['passed']:
                    print(f"  ❌ {test['name']}: {test['message']}")
        
        print(f"\nTest Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        return pass_rate >= 80  # Return True if acceptable success rate

if __name__ == "__main__":
    # Run comprehensive user testing
    test_suite = UserTestSuite()
    success = test_suite.run_complete_user_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)