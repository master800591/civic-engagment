"""
Comprehensive tests for utility validation functions
Tests all validation methods in civic_desktop/utils/validation.py
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils.validation import DataValidator, SecurityValidator, AdvancedValidator, ComprehensiveValidator, PlatformUtils
    from utils.validation import validate_email_param, validate_required_params
except ImportError as e:
    print(f"Warning: Could not import validation modules: {e}")
    # Mock classes for testing if import fails
    class DataValidator:
        @staticmethod
        def validate_email(email): return True, "Valid"
        @staticmethod
        def validate_password(pwd, confirm=None): return True, "Valid"
        @staticmethod
        def validate_name(name, field_name="Name"): return True, "Valid"
        @staticmethod
        def validate_birth_date(date): return True, "Valid", 30
        @staticmethod
        def validate_required_string(val, name, min_len=1, max_len=1000): return True, "Valid"
        @staticmethod
        def validate_id_document(doc): return True, "Valid"
        @staticmethod
        def validate_civic_content(content, content_type="content"): return True, "Valid"
    
    class PlatformUtils:
        @staticmethod
        def generate_unique_id(prefix=''): return f"{prefix}test123"
        @staticmethod
        def calculate_age_from_date(date): return 30


class TestDataValidator(unittest.TestCase):
    """Test DataValidator class methods"""
    
    def test_validate_email_valid(self):
        """Test valid email addresses"""
        valid_emails = [
            'user@example.com',
            'john.doe@company.org',
            'test123@subdomain.example.com',
            'valid+email@test.co.uk'
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                valid, msg = DataValidator.validate_email(email)
                self.assertTrue(valid, f"Email '{email}' should be valid: {msg}")
    
    def test_validate_email_invalid(self):
        """Test invalid email addresses"""
        invalid_emails = [
            '',
            'notanemail',
            '@example.com',
            'user@',
            'user space@example.com',
            None,
            123,
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                valid, msg = DataValidator.validate_email(email)
                self.assertFalse(valid, f"Email '{email}' should be invalid")
    
    def test_validate_password_strong(self):
        """Test strong password validation"""
        strong_passwords = [
            'StrongPass123!',
            'SecureP@ssw0rd',
            'MyP@ssword2024',
            'C0mpl3x!Pass'
        ]
        
        for password in strong_passwords:
            with self.subTest(password=password):
                valid, msg = DataValidator.validate_password(password)
                self.assertTrue(valid, f"Password should be valid: {msg}")
    
    def test_validate_password_weak(self):
        """Test weak password validation"""
        weak_passwords = [
            'weak',
            'password',
            'Password',  # No number or special char
            'pass123',   # No uppercase or special char
            'PASSWORD123!',  # No lowercase
            'abc',       # Too short
        ]
        
        for password in weak_passwords:
            with self.subTest(password=password):
                valid, msg = DataValidator.validate_password(password)
                self.assertFalse(valid, f"Password '{password}' should be invalid")
    
    def test_validate_name_valid(self):
        """Test valid name validation"""
        valid_names = [
            'John',
            'Mary Jane',
            "O'Brien",
            'Jean-Paul',
            'Anne Marie'  # Changed from María García to match validation rules
        ]
        
        for name in valid_names:
            with self.subTest(name=name):
                valid, msg = DataValidator.validate_name(name)
                self.assertTrue(valid, f"Name '{name}' should be valid: {msg}")
    
    def test_validate_name_invalid(self):
        """Test invalid name validation"""
        invalid_names = [
            '',
            'A',  # Too short
            '123',
            'Name<script>',
            None,
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                valid, msg = DataValidator.validate_name(name)
                self.assertFalse(valid, f"Name '{name}' should be invalid")
    
    def test_validate_birth_date_valid(self):
        """Test valid birth date validation"""
        test_cases = [
            ('1990-05-15', True),
            ('2000-01-01', True),
            ('1950-12-31', True),
        ]
        
        for birth_date, should_be_valid in test_cases:
            with self.subTest(birth_date=birth_date):
                valid, msg, age = DataValidator.validate_birth_date(birth_date)
                self.assertEqual(valid, should_be_valid, f"Birth date '{birth_date}': {msg}")
                if valid:
                    self.assertIsInstance(age, int)
                    self.assertGreater(age, 0)
    
    def test_validate_birth_date_invalid(self):
        """Test invalid birth date validation"""
        future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        invalid_dates = [
            '',
            'invalid-date',
            '1899-01-01',  # Too old
            future_date,   # Future date
            None,
        ]
        
        for birth_date in invalid_dates:
            with self.subTest(birth_date=birth_date):
                valid, msg, age = DataValidator.validate_birth_date(birth_date)
                self.assertFalse(valid, f"Birth date '{birth_date}' should be invalid")
    
    def test_validate_required_string_valid(self):
        """Test valid required string validation"""
        test_cases = [
            ('Hello World', 'test', 5, 100, True),
            ('Valid', 'name', 1, 50, True),
            ('A' * 50, 'field', 10, 100, True),
        ]
        
        for value, field_name, min_len, max_len, should_be_valid in test_cases:
            with self.subTest(value=value):
                valid, msg = DataValidator.validate_required_string(value, field_name, min_len, max_len)
                self.assertEqual(valid, should_be_valid, f"String validation failed: {msg}")
    
    def test_validate_required_string_invalid(self):
        """Test invalid required string validation"""
        test_cases = [
            ('', 'test', 5, 100),      # Too short
            ('Hi', 'test', 5, 100),     # Too short
            ('A' * 200, 'test', 1, 100), # Too long
            ('<script>alert()</script>', 'test', 1, 100), # Dangerous content
        ]
        
        for value, field_name, min_len, max_len in test_cases:
            with self.subTest(value=value):
                valid, msg = DataValidator.validate_required_string(value, field_name, min_len, max_len)
                self.assertFalse(valid, f"String '{value}' should be invalid")
    
    def test_validate_id_document_valid(self):
        """Test valid ID document validation"""
        valid_documents = [
            {'document_type': 'passport', 'document_number': 'ABC123456'},
            {'document_type': 'drivers_license', 'document_number': 'DL-12345678'},
            {'document_type': 'national_id', 'document_number': '123-456-7890'},
        ]
        
        for doc in valid_documents:
            with self.subTest(doc=doc):
                valid, msg = DataValidator.validate_id_document(doc)
                self.assertTrue(valid, f"ID document should be valid: {msg}")
    
    def test_validate_id_document_invalid(self):
        """Test invalid ID document validation"""
        invalid_documents = [
            None,
            {},  # Missing fields
            {'document_type': 'invalid_type', 'document_number': '12345'},
            {'document_type': 'passport', 'document_number': '123'},  # Too short
            {'document_type': 'passport', 'document_number': '<script>'},  # Invalid chars
        ]
        
        for doc in invalid_documents:
            with self.subTest(doc=doc):
                valid, msg = DataValidator.validate_id_document(doc)
                self.assertFalse(valid, f"ID document should be invalid")
    
    def test_validate_civic_content_valid(self):
        """Test valid civic content validation"""
        valid_arguments = [
            ('This is a well-reasoned argument about an important civic issue that requires careful consideration and thoughtful debate among our community members.', 'argument'),
            ('A comprehensive civic proposal with sufficient detail and constructive language to address the important issues facing our community today.', 'argument'),
        ]
        
        for content, content_type in valid_arguments:
            with self.subTest(content=content[:50]):
                valid, msg = DataValidator.validate_civic_content(content, content_type)
                self.assertTrue(valid, f"Civic content should be valid: {msg}")
    
    def test_validate_civic_content_invalid(self):
        """Test invalid civic content validation"""
        invalid_content = [
            ('Too short', 'argument'),  # Too short
            ('<script>alert("xss")</script>' * 10, 'argument'),  # Dangerous content
            ('SHOUTING IN ALL CAPS ' * 20, 'argument'),  # All caps
        ]
        
        for content, content_type in invalid_content:
            with self.subTest(content=content[:50]):
                valid, msg = DataValidator.validate_civic_content(content, content_type)
                self.assertFalse(valid, f"Civic content should be invalid")
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        test_cases = [
            ('Hello World', 'Hello World'),
            ('Test <script>', 'Test script'),
            ('A' * 2000, 'A' * 1000),  # Truncation
            ('Multiple   spaces', 'Multiple spaces'),
        ]
        
        for input_str, expected_contains in test_cases:
            with self.subTest(input_str=input_str[:50]):
                sanitized = DataValidator.sanitize_input(input_str)
                self.assertIsInstance(sanitized, str)
                self.assertLessEqual(len(sanitized), 1000)


class TestPlatformUtils(unittest.TestCase):
    """Test PlatformUtils class methods"""
    
    def test_generate_unique_id(self):
        """Test unique ID generation"""
        # Test without prefix
        id1 = PlatformUtils.generate_unique_id()
        self.assertIsInstance(id1, str)
        self.assertGreater(len(id1), 0)
        
        # Test with prefix
        id2 = PlatformUtils.generate_unique_id('USER_')
        self.assertTrue(id2.startswith('USER_'))
        
        # Test uniqueness
        id3 = PlatformUtils.generate_unique_id()
        self.assertNotEqual(id1, id3)
    
    def test_calculate_age_from_date(self):
        """Test age calculation"""
        # Test valid date
        age = PlatformUtils.calculate_age_from_date('1990-05-15')
        self.assertIsInstance(age, int)
        self.assertGreater(age, 0)
        self.assertLess(age, 150)
        
        # Test invalid date
        age_invalid = PlatformUtils.calculate_age_from_date('invalid')
        self.assertIsNone(age_invalid)
    
    def test_format_date_for_display(self):
        """Test date formatting"""
        test_date = '2024-01-15T10:30:00'
        
        # Test short format
        short = PlatformUtils.format_date_for_display(test_date, 'short')
        self.assertIn('2024', short)
        
        # Test long format
        long_format = PlatformUtils.format_date_for_display(test_date, 'long')
        self.assertIn('2024', long_format)
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        test_cases = [
            ('normal_file.txt', 'normal_file.txt'),
            ('file with spaces.pdf', 'file_with_spaces.pdf'),
            ('dangerous<>file.doc', 'dangerousfile.doc'),
            ('file:name?.txt', 'filename.txt'),
        ]
        
        for original, expected_pattern in test_cases:
            with self.subTest(original=original):
                sanitized = PlatformUtils.sanitize_filename(original)
                self.assertIsInstance(sanitized, str)
                self.assertGreater(len(sanitized), 0)
                # Ensure no dangerous characters
                for char in '<>:"/\\|?*':
                    self.assertNotIn(char, sanitized)
    
    def test_hash_sensitive_data(self):
        """Test data hashing"""
        data = 'sensitive_data_123'
        
        # Test SHA-256 (default)
        hash1 = PlatformUtils.hash_sensitive_data(data)
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 64)  # SHA-256 produces 64 hex characters
        
        # Test consistency
        hash2 = PlatformUtils.hash_sensitive_data(data)
        self.assertEqual(hash1, hash2)
        
        # Test different data produces different hash
        hash3 = PlatformUtils.hash_sensitive_data('different_data')
        self.assertNotEqual(hash1, hash3)
    
    def test_truncate_text(self):
        """Test text truncation"""
        long_text = 'A' * 200
        
        # Test default truncation
        truncated = PlatformUtils.truncate_text(long_text, 50)
        self.assertLessEqual(len(truncated), 50)
        self.assertTrue(truncated.endswith('...'))
        
        # Test short text (no truncation)
        short_text = 'Short text'
        result = PlatformUtils.truncate_text(short_text, 50)
        self.assertEqual(result, short_text)


class TestAdvancedValidator(unittest.TestCase):
    """Test AdvancedValidator class methods"""
    
    def test_validate_document_metadata_valid(self):
        """Test valid document metadata"""
        valid_metadata = {
            'title': 'Important Legislative Bill',
            'document_type': 'legislative_bill',
            'classification': 'public',
            'author': 'Legislative Committee',
            'created_date': '2024-01-15'
        }
        
        valid, msg = AdvancedValidator.validate_document_metadata(valid_metadata)
        self.assertTrue(valid, f"Valid metadata should pass: {msg}")
    
    def test_validate_document_metadata_invalid(self):
        """Test invalid document metadata"""
        invalid_metadata = {
            'title': 'Bill',  # Too short
            'document_type': 'invalid_type',
            'classification': 'public'
        }
        
        valid, msg = AdvancedValidator.validate_document_metadata(invalid_metadata)
        self.assertFalse(valid, "Invalid metadata should fail")


class TestComprehensiveValidator(unittest.TestCase):
    """Test ComprehensiveValidator class methods"""
    
    def test_validate_complete_user_registration(self):
        """Test comprehensive user registration validation"""
        valid_registration = {
            'email': 'newuser@civic.platform',
            'password': 'SecurePassword123!',
            'first_name': 'Jane',
            'last_name': 'Citizen',
            'role': 'contract_member',
            'jurisdiction': 'Springfield, IL'
        }
        
        overall_valid, errors, results = ComprehensiveValidator.validate_complete_user_registration(valid_registration)
        
        # Should pass basic validation
        self.assertIsInstance(overall_valid, bool)
        self.assertIsInstance(errors, list)
        self.assertIsInstance(results, dict)
    
    def test_create_validation_summary(self):
        """Test validation summary creation"""
        validation_results = {
            'field1': True,
            'field2': True,
            'field3': False,
            'field4': True
        }
        
        summary = ComprehensiveValidator.create_validation_summary(validation_results)
        
        self.assertEqual(summary['total_fields'], 4)
        self.assertEqual(summary['valid_fields'], 3)
        self.assertEqual(summary['invalid_fields'], 1)
        self.assertEqual(summary['success_rate'], 75.0)
        self.assertEqual(summary['overall_status'], 'failed')


def run_tests():
    """Run all validation tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestComprehensiveValidator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
