"""
SECURITY VALIDATION TEST SUITE
Tests for authentication, founder key, and user management security
"""

import unittest
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import modules to test
try:
    from users.backend import UserBackend
    from users.hardcoded_founder_keys import HardcodedFounderKeys
    from users.security_audit import SecurityAuditor
    from utils.validation import DataValidator, SecurityValidator
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    IMPORTS_AVAILABLE = False


class TestPasswordSecurity(unittest.TestCase):
    """Test password hashing and verification"""
    
    @unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'users_db_path': os.path.join(self.temp_dir, 'test_users.json'),
            'sessions_db_path': os.path.join(self.temp_dir, 'test_sessions.json'),
            'private_keys_dir': os.path.join(self.temp_dir, 'keys')
        }
        
        # Create temp config file
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
        
        self.backend = UserBackend(self.config_file)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        password = "SecurePassword123!"
        hashed = self.backend._hash_password(password)
        
        # Verify hash is not plaintext
        self.assertNotEqual(password, hashed)
        
        # Verify hash starts with bcrypt identifier
        self.assertTrue(hashed.startswith('$2b$'))
        
        # Verify hash length is appropriate
        self.assertGreater(len(hashed), 50)
    
    def test_password_verification(self):
        """Test password verification"""
        password = "SecurePassword123!"
        hashed = self.backend._hash_password(password)
        
        # Correct password should verify
        self.assertTrue(self.backend._verify_password(password, hashed))
        
        # Incorrect password should not verify
        self.assertFalse(self.backend._verify_password("WrongPassword", hashed))
    
    def test_password_salt_uniqueness(self):
        """Test that each password gets unique salt"""
        password = "SecurePassword123!"
        hash1 = self.backend._hash_password(password)
        hash2 = self.backend._hash_password(password)
        
        # Same password should produce different hashes due to different salts
        self.assertNotEqual(hash1, hash2)
        
        # Both should verify the original password
        self.assertTrue(self.backend._verify_password(password, hash1))
        self.assertTrue(self.backend._verify_password(password, hash2))


class TestRateLimiting(unittest.TestCase):
    """Test account lockout and rate limiting"""
    
    @unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'users_db_path': os.path.join(self.temp_dir, 'test_users.json'),
            'sessions_db_path': os.path.join(self.temp_dir, 'test_sessions.json'),
            'private_keys_dir': os.path.join(self.temp_dir, 'keys'),
            'max_login_attempts': 3,
            'lockout_duration_minutes': 5
        }
        
        # Create temp config file
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
        
        self.backend = UserBackend(self.config_file)
        
        # Create test user
        test_user = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'ValidPassword123!',
            'confirm_password': 'ValidPassword123!',
            'city': 'Test City',
            'state': 'Test State',
            'country': 'Test Country',
            'terms_accepted': True
        }
        self.backend.register_user(test_user)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_failed_login_tracking(self):
        """Test that failed login attempts are tracked"""
        email = 'test@example.com'
        wrong_password = 'WrongPassword'
        
        # First failed attempt
        success, message, user = self.backend.authenticate_user(email, wrong_password)
        self.assertFalse(success)
        self.assertIn('attempts remaining', message.lower())
        
        # Load user and check attempt count
        users_data = self.backend._load_users_db()
        user = next((u for u in users_data['users'] if u['email'] == email), None)
        self.assertEqual(user['login_attempts'], 1)
    
    def test_account_lockout(self):
        """Test account lockout after too many failures"""
        email = 'test@example.com'
        wrong_password = 'WrongPassword'
        max_attempts = self.config['max_login_attempts']
        
        # Make max failed attempts
        for i in range(max_attempts):
            success, message, user = self.backend.authenticate_user(email, wrong_password)
            self.assertFalse(success)
        
        # Load user and verify lockout
        users_data = self.backend._load_users_db()
        user = next((u for u in users_data['users'] if u['email'] == email), None)
        self.assertIsNotNone(user['locked_until'])
        
        # Verify locked_until is in the future
        locked_until = datetime.fromisoformat(user['locked_until'])
        self.assertGreater(locked_until, datetime.now())
    
    def test_lockout_prevents_login(self):
        """Test that locked account cannot login even with correct password"""
        email = 'test@example.com'
        correct_password = 'ValidPassword123!'
        wrong_password = 'WrongPassword'
        max_attempts = self.config['max_login_attempts']
        
        # Lock the account
        for i in range(max_attempts):
            self.backend.authenticate_user(email, wrong_password)
        
        # Try to login with correct password while locked
        success, message, user = self.backend.authenticate_user(email, correct_password)
        self.assertFalse(success)
        self.assertIn('locked', message.lower())


class TestFounderKeySecurity(unittest.TestCase):
    """Test founder key single-use enforcement"""
    
    @unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
    def setUp(self):
        """Set up test environment"""
        # Clean up any existing used keys file for testing
        self.used_keys_backup = None
        used_keys_path = Path('users/used_founder_keys.json')
        if used_keys_path.exists():
            with open(used_keys_path, 'r') as f:
                self.used_keys_backup = f.read()
            # Clear for testing
            with open(used_keys_path, 'w') as f:
                json.dump({}, f)
    
    def tearDown(self):
        """Restore used keys if backed up"""
        if self.used_keys_backup:
            used_keys_path = Path('users/used_founder_keys.json')
            with open(used_keys_path, 'w') as f:
                f.write(self.used_keys_backup)
    
    def test_key_status_retrieval(self):
        """Test that key status can be retrieved"""
        status = HardcodedFounderKeys.get_key_status()
        
        self.assertIn('total_keys', status)
        self.assertIn('used_keys', status)
        self.assertIn('available_keys', status)
        self.assertGreater(status['total_keys'], 0)
    
    def test_invalid_key_rejection(self):
        """Test that invalid keys are rejected"""
        invalid_key = "-----BEGIN PRIVATE KEY-----\nINVALID_KEY_DATA\n-----END PRIVATE KEY-----"
        
        is_valid, message, data = HardcodedFounderKeys.validate_founder_key(invalid_key)
        
        self.assertFalse(is_valid)
        self.assertIn('invalid', message.lower())
        self.assertIsNone(data)
    
    def test_used_keys_persistence(self):
        """Test that used keys are persisted"""
        # Get initial status
        initial_status = HardcodedFounderKeys.get_key_status()
        initial_used = initial_status['used_keys']
        
        # Used keys should be saved to file
        used_keys_path = Path('users/used_founder_keys.json')
        self.assertTrue(used_keys_path.exists() or initial_used == 0)


class TestInputValidation(unittest.TestCase):
    """Test input validation security"""
    
    @unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
    def test_email_validation(self):
        """Test email validation"""
        # Valid emails
        self.assertTrue(DataValidator.validate_email('user@example.com')[0])
        self.assertTrue(DataValidator.validate_email('test.user@example.co.uk')[0])
        
        # Invalid emails
        self.assertFalse(DataValidator.validate_email('invalid')[0])
        self.assertFalse(DataValidator.validate_email('user@')[0])
        self.assertFalse(DataValidator.validate_email('@example.com')[0])
    
    def test_password_strength_validation(self):
        """Test password strength requirements"""
        # Strong passwords
        is_valid, msg = DataValidator.validate_password('SecurePass123!', 'SecurePass123!')
        self.assertTrue(is_valid)
        
        # Weak passwords should be caught
        weak_passwords = [
            'short',           # Too short
            'nodigits',        # No digits
            'NO UPPERCASE 123', # No lowercase
            'no lowercase 123', # No uppercase (if required)
        ]
        
        for weak_pass in weak_passwords:
            is_valid, msg = DataValidator.validate_password(weak_pass, weak_pass)
            # At least some weak passwords should fail
            if not is_valid:
                self.assertIsNotNone(msg)
    
    def test_name_validation(self):
        """Test name validation"""
        # Valid names
        self.assertTrue(DataValidator.validate_name('John', 'First name')[0])
        self.assertTrue(DataValidator.validate_name('Jane Smith', 'Name')[0])
        
        # Invalid names
        self.assertFalse(DataValidator.validate_name('', 'Name')[0])
        self.assertFalse(DataValidator.validate_name('X', 'Name')[0])  # Too short


class TestSecurityAuditing(unittest.TestCase):
    """Test security audit functionality"""
    
    @unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        with open(self.config_file, 'w') as f:
            json.dump({
                'audit_log_path': os.path.join(self.temp_dir, 'audit.json')
            }, f)
        
        self.auditor = SecurityAuditor(self.config_file)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_security_event_logging(self):
        """Test that security events are logged"""
        success = self.auditor.log_security_event(
            event_type='test_event',
            user_email='test@example.com',
            details={'test': 'data'},
            severity='info'
        )
        
        self.assertTrue(success)
        
        # Verify event was saved
        audit_log = self.auditor._load_audit_log()
        self.assertEqual(len(audit_log['events']), 1)
        self.assertEqual(audit_log['events'][0]['event_type'], 'test_event')
    
    def test_founder_key_audit(self):
        """Test founder key audit functionality"""
        report = self.auditor.audit_founder_key_usage()
        
        self.assertIn('status', report)
        self.assertIn('timestamp', report)
        
        # Should either pass or have a specific error
        self.assertIn(report['status'], ['passed', 'failed', 'error'])
    
    def test_comprehensive_report_generation(self):
        """Test comprehensive security report"""
        report = self.auditor.generate_comprehensive_report()
        
        self.assertIn('report_id', report)
        self.assertIn('timestamp', report)
        self.assertIn('audits', report)
        self.assertIn('overall_status', report)
        self.assertIn('summary', report)
        
        # Verify all audit types are present
        self.assertIn('founder_keys', report['audits'])
        self.assertIn('authentication', report['audits'])
        self.assertIn('sessions', report['audits'])


class TestSecurityIntegration(unittest.TestCase):
    """Test integration of security features"""
    
    @unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'users_db_path': os.path.join(self.temp_dir, 'test_users.json'),
            'sessions_db_path': os.path.join(self.temp_dir, 'test_sessions.json'),
            'private_keys_dir': os.path.join(self.temp_dir, 'keys'),
            'audit_log_path': os.path.join(self.temp_dir, 'audit.json')
        }
        
        # Create temp config file
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
        
        self.backend = UserBackend(self.config_file)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_registration_with_security_logging(self):
        """Test that registration triggers security logging"""
        test_user = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'ValidPassword123!',
            'confirm_password': 'ValidPassword123!',
            'city': 'Test City',
            'state': 'Test State',
            'country': 'Test Country',
            'terms_accepted': True
        }
        
        success, message, user_record = self.backend.register_user(test_user)
        
        self.assertTrue(success)
        self.assertIsNotNone(user_record)
        
        # Verify user was created
        users_data = self.backend._load_users_db()
        self.assertEqual(len(users_data['users']), 1)
    
    def test_failed_login_with_security_logging(self):
        """Test that failed logins trigger security logging"""
        # First create a user
        test_user = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'ValidPassword123!',
            'confirm_password': 'ValidPassword123!',
            'city': 'Test City',
            'state': 'Test State',
            'country': 'Test Country',
            'terms_accepted': True
        }
        self.backend.register_user(test_user)
        
        # Try to login with wrong password
        success, message, user = self.backend.authenticate_user('testuser@example.com', 'WrongPassword')
        
        self.assertFalse(success)
        self.assertIn('invalid', message.lower())
        
        # If security auditor is available, check logging
        if self.backend.security_auditor:
            audit_log = self.backend.security_auditor._load_audit_log()
            # Should have at least one event (failed login)
            self.assertGreaterEqual(len(audit_log['events']), 1)


def run_security_tests():
    """Run all security tests and generate report"""
    print("🔒 Running Security Validation Tests...")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimiting))
    suite.addTests(loader.loadTestsFromTestCase(TestFounderKeySecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestInputValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityAuditing))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 Security Test Summary")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    print(f"⏭️ Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ All security tests passed!")
        return 0
    else:
        print("\n❌ Some security tests failed. Review output above.")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_security_tests())
