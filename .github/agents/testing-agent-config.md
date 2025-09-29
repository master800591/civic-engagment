# 🧪 Testing Agent Configuration

## Agent Specialization: Comprehensive Testing & Quality Assurance

The Testing Agent specializes in creating, maintaining, and executing comprehensive test suites to ensure the reliability, security, and performance of the Civic Engagement Platform.

## Core Responsibilities

### 🔬 Test Development
- **Unit Testing**: Individual module and function testing
- **Integration Testing**: Cross-module workflow testing
- **End-to-End Testing**: Complete user journey testing
- **Performance Testing**: Load, stress, and scalability testing
- **Security Testing**: Vulnerability assessment and penetration testing

### 🎯 Quality Assurance
- **Test Coverage Analysis**: Ensure 90%+ code coverage for critical paths
- **Regression Testing**: Prevent introduction of new bugs
- **Compatibility Testing**: Multi-platform and browser testing
- **Accessibility Testing**: WCAG compliance validation
- **Usability Testing**: User experience validation

### 🤖 Test Automation
- **CI/CD Integration**: Automated testing in deployment pipeline
- **Test Data Management**: Consistent test data across environments
- **Test Reporting**: Comprehensive test result analysis
- **Test Maintenance**: Keep tests current with code changes
- **Performance Monitoring**: Continuous performance validation

## Testing Framework Architecture

### 🏗️ Test Structure
```
tests/
├── unit/                   # Unit tests for individual modules
│   ├── test_users/
│   ├── test_debates/
│   ├── test_moderation/
│   ├── test_blockchain/
│   ├── test_contracts/
│   └── test_utils/
├── integration/            # Cross-module integration tests
│   ├── test_user_workflows/
│   ├── test_governance_flows/
│   ├── test_api_integration/
│   └── test_blockchain_sync/
├── e2e/                   # End-to-end user journey tests
│   ├── test_citizen_journey/
│   ├── test_representative_workflow/
│   └── test_admin_functions/
├── performance/           # Performance and load tests
│   ├── test_blockchain_performance/
│   ├── test_database_performance/
│   └── test_ui_responsiveness/
├── security/              # Security-focused tests
│   ├── test_authentication/
│   ├── test_authorization/
│   ├── test_input_validation/
│   └── test_cryptography/
├── fixtures/              # Test data and mock objects
├── conftest.py           # Pytest configuration
└── requirements-test.txt  # Testing dependencies
```

### 🔧 Testing Infrastructure
```python
# conftest.py - Central test configuration
import pytest
import tempfile
import shutil
from civic_desktop.users.backend import UserBackend
from civic_desktop.blockchain.blockchain import Blockchain
from civic_desktop.users.session import SessionManager

@pytest.fixture
def test_config():
    """Provide test configuration"""
    return {
        'database_path': tempfile.mkdtemp(),
        'environment': 'test',
        'debug': True,
        'blockchain_path': tempfile.mkdtemp()
    }

@pytest.fixture
def clean_database(test_config):
    """Provide clean database for each test"""
    db_path = test_config['database_path']
    yield db_path
    shutil.rmtree(db_path, ignore_errors=True)

@pytest.fixture
def sample_users():
    """Provide sample user data for testing"""
    return [
        {
            'email': 'citizen@test.com',
            'first_name': 'Test',
            'last_name': 'Citizen',
            'role': 'Contract Citizen',
            'password': 'TestPassword123!'
        },
        {
            'email': 'rep@test.com',
            'first_name': 'Test',
            'last_name': 'Representative',
            'role': 'Contract Representative',
            'password': 'TestPassword456!'
        }
    ]

@pytest.fixture
def authenticated_session(sample_users):
    """Provide authenticated user session"""
    user = sample_users[0]
    UserBackend.register_user(user, "fake_id_path")
    SessionManager.login(user)
    yield SessionManager.get_current_user()
    SessionManager.logout()
```

## Test Categories and Examples

### 🧩 Unit Tests
```python
# tests/unit/test_users/test_authentication.py
import pytest
from civic_desktop.users.backend import UserBackend
from civic_desktop.users.auth import AuthenticationService

class TestUserAuthentication:
    """Test user authentication functionality"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "TestPassword123!"
        hashed = UserBackend.hash_password(password)
        
        assert hashed != password
        assert UserBackend.verify_password(password, hashed)
        assert not UserBackend.verify_password("wrong_password", hashed)
    
    def test_user_registration_validation(self):
        """Test user registration input validation"""
        valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'SecurePassword123!',
            'city': 'Test City',
            'state': 'TS',
            'country': 'Test Country'
        }
        
        # Test valid registration
        result, message = UserBackend.register_user(valid_data, "test_id_path")
        assert result is True
        
        # Test duplicate email
        result, message = UserBackend.register_user(valid_data, "test_id_path")
        assert result is False
        assert "already exists" in message.lower()
    
    def test_session_management(self):
        """Test user session creation and management"""
        from civic_desktop.users.session import SessionManager
        
        # Test session creation
        user_data = {'email': 'test@example.com', 'role': 'Contract Citizen'}
        SessionManager.login(user_data)
        
        assert SessionManager.is_authenticated()
        assert SessionManager.get_current_user()['email'] == 'test@example.com'
        
        # Test session cleanup
        SessionManager.logout()
        assert not SessionManager.is_authenticated()
        assert SessionManager.get_current_user() is None

class TestBlockchainIntegration:
    """Test blockchain functionality"""
    
    def test_block_creation(self):
        """Test blockchain block creation"""
        from civic_desktop.blockchain.blockchain import Blockchain
        
        test_data = {
            'action': 'test_action',
            'user': 'test@example.com',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        initial_height = Blockchain.get_current_height()
        success = Blockchain.add_page(test_data, 'test@example.com')
        
        assert success
        assert Blockchain.get_current_height() > initial_height
    
    def test_validator_signatures(self):
        """Test validator signature verification"""
        from civic_desktop.blockchain.signatures import ValidatorSignatures
        from civic_desktop.blockchain.blockchain import ValidatorRegistry
        
        # Create test validator
        test_email = 'validator@test.com'
        public_key, private_key = ValidatorSignatures.generate_key_pair()
        ValidatorRegistry.add_validator(test_email, public_key)
        
        # Test signing and verification
        test_data = "test_block_data"
        signature = ValidatorSignatures.sign_data(test_data, private_key)
        
        assert ValidatorSignatures.verify_signature(test_data, signature, public_key)
        assert not ValidatorSignatures.verify_signature("wrong_data", signature, public_key)
```

### 🔗 Integration Tests
```python
# tests/integration/test_governance_flows/test_election_workflow.py
import pytest
from civic_desktop.users.backend import UserBackend
from civic_desktop.users.elections import ElectionSystem
from civic_desktop.debates.backend import DebateBackend
from civic_desktop.blockchain.blockchain import Blockchain

class TestElectionWorkflow:
    """Test complete election workflow across modules"""
    
    @pytest.fixture
    def election_setup(self, clean_database):
        """Set up election test environment"""
        # Create candidates
        candidate1 = {
            'email': 'candidate1@test.com',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'role': 'Contract Citizen'
        }
        candidate2 = {
            'email': 'candidate2@test.com',
            'first_name': 'Bob',
            'last_name': 'Jones',
            'role': 'Contract Citizen'
        }
        
        UserBackend.register_user(candidate1, "id1_path")
        UserBackend.register_user(candidate2, "id2_path")
        
        # Create voters
        voters = []
        for i in range(5):
            voter = {
                'email': f'voter{i}@test.com',
                'first_name': f'Voter{i}',
                'last_name': 'Test',
                'role': 'Contract Citizen'
            }
            UserBackend.register_user(voter, f"voter{i}_id_path")
            voters.append(voter)
        
        return {
            'candidates': [candidate1, candidate2],
            'voters': voters
        }
    
    def test_complete_election_cycle(self, election_setup):
        """Test complete election from creation to results"""
        candidates = election_setup['candidates']
        voters = election_setup['voters']
        
        # 1. Create election
        election = ElectionSystem.create_election(
            position="Contract Representative",
            candidates=[c['email'] for c in candidates],
            duration_days=30
        )
        assert election is not None
        
        # 2. Verify debate topic creation
        debate_topic = DebateBackend.get_election_debate(election.id)
        assert debate_topic is not None
        assert debate_topic.title.contains("Election")
        
        # 3. Verify blockchain recording
        blockchain_records = Blockchain.get_pages_by_type("election_created")
        election_record = next((r for r in blockchain_records if r.data.get('election_id') == election.id), None)
        assert election_record is not None
        
        # 4. Test voting process
        votes_cast = 0
        for voter in voters[:3]:  # 3 voters vote for candidate1
            result = ElectionSystem.cast_vote(voter['email'], election.id, candidates[0]['email'])
            if result.success:
                votes_cast += 1
        
        for voter in voters[3:]:  # 2 voters vote for candidate2
            result = ElectionSystem.cast_vote(voter['email'], election.id, candidates[1]['email'])
            if result.success:
                votes_cast += 1
        
        assert votes_cast == 5
        
        # 5. Test election results
        results = ElectionSystem.get_election_results(election.id)
        assert results[candidates[0]['email']] == 3
        assert results[candidates[1]['email']] == 2
        
        # 6. Verify blockchain vote records
        vote_records = Blockchain.get_pages_by_type("election_vote")
        election_votes = [r for r in vote_records if r.data.get('election_id') == election.id]
        assert len(election_votes) == 5

class TestCrossModuleAuthentication:
    """Test authentication across different modules"""
    
    def test_authentication_propagation(self, sample_users):
        """Test that authentication works across all modules"""
        from civic_desktop.users.session import SessionManager
        from civic_desktop.debates.backend import DebateBackend
        from civic_desktop.moderation.backend import ModerationBackend
        from civic_desktop.contracts.backend import ContractBackend
        
        user = sample_users[0]
        UserBackend.register_user(user, "test_id_path")
        
        # Authenticate user
        SessionManager.login(user)
        
        # Test debates module recognizes authentication
        can_create_topic = DebateBackend.can_create_topic(user['email'])
        assert isinstance(can_create_topic, bool)
        
        # Test moderation module recognizes authentication
        can_moderate = ModerationBackend.can_moderate(user['email'])
        assert isinstance(can_moderate, bool)
        
        # Test contracts module recognizes authentication
        permissions = ContractBackend.get_user_permissions(user['email'])
        assert isinstance(permissions, list)
        assert 'basic_access' in permissions
```

### 🎭 End-to-End Tests
```python
# tests/e2e/test_citizen_journey/test_new_user_flow.py
import pytest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from civic_desktop.main_window import MainWindow

class TestNewUserJourney:
    """Test complete new user registration and first actions"""
    
    @pytest.fixture
    def app_window(self, qtbot):
        """Create main application window for testing"""
        window = MainWindow()
        qtbot.addWidget(window)
        return window
    
    def test_user_registration_flow(self, app_window, qtbot):
        """Test complete user registration through UI"""
        # Navigate to Users tab
        users_tab = app_window.findChild(QWidget, "users_tab")
        qtbot.mouseClick(users_tab, Qt.LeftButton)
        
        # Click register button
        register_button = app_window.findChild(QPushButton, "register_button")
        qtbot.mouseClick(register_button, Qt.LeftButton)
        
        # Fill registration form
        first_name_field = app_window.findChild(QLineEdit, "first_name")
        qtbot.keyClicks(first_name_field, "Test")
        
        last_name_field = app_window.findChild(QLineEdit, "last_name")
        qtbot.keyClicks(last_name_field, "User")
        
        email_field = app_window.findChild(QLineEdit, "email")
        qtbot.keyClicks(email_field, "test@example.com")
        
        password_field = app_window.findChild(QLineEdit, "password")
        qtbot.keyClicks(password_field, "SecurePassword123!")
        
        # Submit registration
        submit_button = app_window.findChild(QPushButton, "submit_registration")
        qtbot.mouseClick(submit_button, Qt.LeftButton)
        
        # Verify registration success message
        success_dialog = app_window.findChild(QMessageBox)
        assert success_dialog is not None
        assert "success" in success_dialog.text().lower()
    
    def test_first_debate_participation(self, app_window, qtbot, authenticated_session):
        """Test user's first debate participation"""
        # Navigate to Debates tab
        debates_tab = app_window.findChild(QWidget, "debates_tab")
        qtbot.mouseClick(debates_tab, Qt.LeftButton)
        
        # Find active debate topic
        debate_list = app_window.findChild(QListWidget, "debate_topics")
        if debate_list.count() > 0:
            qtbot.mouseClick(debate_list.item(0), Qt.LeftButton)
            
            # Add argument to debate
            argument_field = app_window.findChild(QTextEdit, "argument_text")
            qtbot.keyClicks(argument_field, "This is my first contribution to this important debate.")
            
            submit_argument = app_window.findChild(QPushButton, "submit_argument")
            qtbot.mouseClick(submit_argument, Qt.LeftButton)
            
            # Verify argument was added
            arguments_display = app_window.findChild(QWidget, "arguments_display")
            assert "This is my first contribution" in arguments_display.toPlainText()
```

### ⚡ Performance Tests
```python
# tests/performance/test_blockchain_performance.py
import pytest
import time
import threading
from civic_desktop.blockchain.blockchain import Blockchain

class TestBlockchainPerformance:
    """Test blockchain performance under various loads"""
    
    def test_large_block_creation(self):
        """Test performance with large data blocks"""
        large_data = {
            'action': 'performance_test',
            'data': 'x' * 10000,  # 10KB of data
            'timestamp': time.time()
        }
        
        start_time = time.time()
        success = Blockchain.add_page(large_data, 'test@example.com')
        end_time = time.time()
        
        assert success
        assert (end_time - start_time) < 1.0  # Should complete within 1 second
    
    def test_concurrent_block_creation(self):
        """Test blockchain performance under concurrent load"""
        def create_blocks(thread_id, num_blocks):
            for i in range(num_blocks):
                data = {
                    'action': f'concurrent_test_{thread_id}_{i}',
                    'thread_id': thread_id,
                    'block_number': i
                }
                Blockchain.add_page(data, f'test{thread_id}@example.com')
        
        # Create 5 threads, each creating 10 blocks
        threads = []
        start_time = time.time()
        
        for thread_id in range(5):
            thread = threading.Thread(target=create_blocks, args=(thread_id, 10))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All 50 blocks should be created within 10 seconds
        assert (end_time - start_time) < 10.0
        
        # Verify all blocks were created
        recent_blocks = Blockchain.get_recent_blocks(limit=60)
        concurrent_blocks = [b for b in recent_blocks if 'concurrent_test' in str(b)]
        assert len(concurrent_blocks) >= 50
    
    def test_database_query_performance(self):
        """Test database query performance with large datasets"""
        from civic_desktop.users.backend import UserBackend
        
        # Create many users for testing
        start_time = time.time()
        for i in range(100):
            user_data = {
                'email': f'perftest{i}@example.com',
                'first_name': f'User{i}',
                'last_name': 'Performance',
                'role': 'Contract Citizen'
            }
            UserBackend.register_user(user_data, f"perftest{i}_id")
        creation_time = time.time() - start_time
        
        # Test query performance
        start_time = time.time()
        all_users = UserBackend.load_users()
        query_time = time.time() - start_time
        
        assert len(all_users) >= 100
        assert creation_time < 30.0  # Creating 100 users should take less than 30 seconds
        assert query_time < 1.0      # Loading users should take less than 1 second
```

### 🔒 Security Tests
```python
# tests/security/test_authentication/test_auth_security.py
import pytest
from civic_desktop.users.backend import UserBackend
from civic_desktop.users.auth import AuthenticationService

class TestAuthenticationSecurity:
    """Test authentication security measures"""
    
    def test_password_strength_enforcement(self):
        """Test that weak passwords are rejected"""
        weak_passwords = [
            "123456",
            "password",
            "qwerty",
            "abc123",
            "password123"
        ]
        
        user_data = {
            'email': 'security@test.com',
            'first_name': 'Security',
            'last_name': 'Test'
        }
        
        for weak_password in weak_passwords:
            user_data['password'] = weak_password
            result, message = UserBackend.register_user(user_data, "test_id")
            assert not result
            assert "password" in message.lower()
    
    def test_brute_force_protection(self):
        """Test protection against brute force attacks"""
        # Register test user
        user_data = {
            'email': 'bruteforce@test.com',
            'password': 'CorrectPassword123!',
            'first_name': 'Brute',
            'last_name': 'Force'
        }
        UserBackend.register_user(user_data, "test_id")
        
        # Attempt multiple failed logins
        failed_attempts = 0
        for i in range(10):
            result = AuthenticationService.authenticate('bruteforce@test.com', 'WrongPassword')
            if not result.success:
                failed_attempts += 1
        
        # After multiple failures, account should be temporarily locked
        assert failed_attempts >= 5
        
        # Verify legitimate login is blocked temporarily
        result = AuthenticationService.authenticate('bruteforce@test.com', 'CorrectPassword123!')
        assert not result.success
        assert "temporarily locked" in result.message.lower()
    
    def test_session_security(self):
        """Test session security measures"""
        from civic_desktop.users.session import SessionManager
        
        user_data = {'email': 'session@test.com', 'role': 'Contract Citizen'}
        
        # Test session creation
        SessionManager.login(user_data)
        session_data = SessionManager.get_current_user()
        
        # Verify session data doesn't contain sensitive information
        assert 'password' not in session_data
        assert 'private_key' not in session_data
        
        # Test session timeout (if implemented)
        # This would require mocking time or waiting
        
        # Test session invalidation
        SessionManager.logout()
        assert not SessionManager.is_authenticated()

class TestInputValidationSecurity:
    """Test input validation security"""
    
    def test_sql_injection_prevention(self):
        """Test prevention of SQL injection attacks"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "1; DELETE FROM users"
        ]
        
        for malicious_input in malicious_inputs:
            # Test in email field
            user_data = {
                'email': malicious_input,
                'password': 'ValidPassword123!',
                'first_name': 'Test',
                'last_name': 'User'
            }
            result, message = UserBackend.register_user(user_data, "test_id")
            assert not result  # Should be rejected
    
    def test_xss_prevention(self):
        """Test prevention of XSS attacks"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            user_data = {
                'email': 'xss@test.com',
                'first_name': payload,
                'last_name': 'Test',
                'password': 'ValidPassword123!'
            }
            result, message = UserBackend.register_user(user_data, "test_id")
            # Input should be either rejected or properly escaped
            if result:
                saved_user = UserBackend.get_user_by_email('xss@test.com')
                assert payload not in saved_user['first_name']  # Should be escaped
```

## Test Automation and CI Integration

### 🤖 Automated Test Execution
```python
# tests/automation/test_runner.py
import subprocess
import sys
import json
from pathlib import Path

class AutomatedTestRunner:
    """Automated test execution and reporting"""
    
    def run_all_tests(self):
        """Run complete test suite with reporting"""
        test_results = {}
        
        # Run unit tests
        test_results['unit'] = self.run_test_category('tests/unit')
        
        # Run integration tests
        test_results['integration'] = self.run_test_category('tests/integration')
        
        # Run security tests
        test_results['security'] = self.run_test_category('tests/security')
        
        # Run performance tests
        test_results['performance'] = self.run_test_category('tests/performance')
        
        # Generate report
        self.generate_test_report(test_results)
        
        return test_results
    
    def run_test_category(self, test_path):
        """Run tests in specific category"""
        cmd = [
            sys.executable, '-m', 'pytest',
            test_path,
            '--verbose',
            '--tb=short',
            '--junitxml=test_results.xml',
            '--cov=civic_desktop',
            '--cov-report=html',
            '--cov-report=json'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    
    def generate_test_report(self, test_results):
        """Generate comprehensive test report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_categories': len(test_results),
                'passed_categories': sum(1 for r in test_results.values() if r['success']),
                'overall_success': all(r['success'] for r in test_results.values())
            },
            'details': test_results
        }
        
        # Save report
        with open('test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        self.generate_html_report(report)
    
    def generate_html_report(self, report):
        """Generate HTML test report"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Civic Engagement Platform - Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .pass { color: green; }
                .fail { color: red; }
                .summary { background: #f0f0f0; padding: 10px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>Test Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Timestamp: {timestamp}</p>
                <p>Overall Status: <span class="{overall_class}">{overall_status}</span></p>
                <p>Categories Passed: {passed}/{total}</p>
            </div>
            {category_details}
        </body>
        </html>
        """
        
        # Implementation would generate detailed HTML report
```

## Integration with Other Agents

### 🔍 Review Agent Coordination
- Submit test code for security review
- Validate test coverage meets security requirements
- Review test results for security implications

### 🔗 Integration Agent Coordination
- Test cross-module integrations thoroughly
- Validate API endpoints and responses
- Test external service integrations

### 📚 Documentation Agent Coordination
- Document testing procedures and standards
- Create testing guides for contributors
- Maintain test coverage documentation

### 🏗️ Build Agent Coordination
- Integrate tests into CI/CD pipeline
- Configure automated test execution
- Set up test result reporting and notifications

## Testing Standards and Best Practices

### 📊 Coverage Requirements
- **Critical Path Coverage**: 95%+ for authentication, governance, and blockchain
- **Overall Coverage**: 85%+ for all modules
- **Integration Coverage**: 80%+ for cross-module workflows
- **Security Coverage**: 100% for security-critical functions

### 🎯 Test Quality Standards
- Tests must be deterministic and repeatable
- Each test should test one specific behavior
- Tests should be independent and isolated
- Test data should be realistic but anonymized
- Performance tests should have baseline metrics

This Testing Agent configuration ensures comprehensive validation of platform functionality, security, and performance while maintaining high code quality standards.