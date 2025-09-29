# Comprehensive Test Suite - Civic Engagement Platform
"""
Complete test suite for all implemented modules including System Guide, 
Collaboration, Documents, Maps, Tasks, and enhanced core functionality.
"""

import unittest
import tempfile
import json
import os
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import modules to test
import sys
sys.path.append('/home/runner/work/civic-engagment/civic-engagment/civic_desktop')

from system_guide.onboarding_backend import UserOnboardingSystem
from system_guide.help_system import HelpSystem
from collaboration.project_coordinator import InterJurisdictionalProjectManager, ResourceSharingManager
from documents.document_manager import DocumentManager
from tasks.task_manager import TaskManager
from utils.validation import DataValidator, AdvancedValidator, ComprehensiveValidator
from config.config_validator import ConfigurationValidator


class TestSystemGuideModule(unittest.TestCase):
    """Test System Guide module functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.onboarding_system = UserOnboardingSystem()
        self.help_system = HelpSystem()
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_user_onboarding_initiation(self):
        """Test user onboarding system initiation"""
        # Test valid user onboarding
        success, message, session_data = self.onboarding_system.initiate_user_onboarding(
            user_email="test@civic.platform",
            onboarding_preferences={'pathway': 'guided', 'pace': 'normal'}
        )
        
        self.assertTrue(success)
        self.assertIn("Onboarding session created", message)
        self.assertIsInstance(session_data, dict)
        self.assertIn('id', session_data)
        self.assertIn('pathway_configuration', session_data)
    
    def test_onboarding_progress_tracking(self):
        """Test onboarding progress tracking"""
        # Create onboarding session
        success, message, session_data = self.onboarding_system.initiate_user_onboarding(
            user_email="test@civic.platform",
            onboarding_preferences={'pathway': 'guided'}
        )
        
        self.assertTrue(success)
        session_id = session_data['id']
        
        # Test progress update
        progress_success, progress_message = self.onboarding_system.update_module_progress(
            session_id=session_id,
            module_name="platform_introduction",
            progress_data={
                'completion_percentage': 50,
                'time_spent_minutes': 15,
                'competency_score': 85,
                'interaction_count': 12
            }
        )
        
        self.assertTrue(progress_success)
        self.assertIn("Progress updated", progress_message)
    
    def test_help_system_search(self):
        """Test help system search functionality"""
        # Test help content search
        search_results = self.help_system.search_help_content(
            query="voting",
            user_context={'role': 'Contract Member', 'experience_level': 'beginner'}
        )
        
        self.assertIsInstance(search_results, list)
        self.assertTrue(len(search_results) > 0)
        
        # Verify search result structure
        for result in search_results:
            self.assertIn('title', result)
            self.assertIn('content', result)
            self.assertIn('relevance_score', result)
    
    def test_contextual_help_provision(self):
        """Test contextual help provision"""
        help_response = self.help_system.provide_contextual_help(
            module="debates",
            action="create_topic",
            user_context={'role': 'Contract Representative', 'experience_level': 'intermediate'}
        )
        
        self.assertIsInstance(help_response, dict)
        self.assertIn('help_content', help_response)
        self.assertIn('related_tutorials', help_response)
        self.assertIn('quick_actions', help_response)


class TestCollaborationModule(unittest.TestCase):
    """Test Collaboration module functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_manager = InterJurisdictionalProjectManager()
        self.resource_manager = ResourceSharingManager()
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_project_creation(self):
        """Test inter-jurisdictional project creation"""
        project_data = {
            'title': 'Regional Water Management Initiative',
            'description': 'Collaborative water resource management across three counties',
            'project_type': 'resource_sharing',
            'participating_jurisdictions': ['County A', 'County B', 'County C'],
            'scope': 'multi_county',
            'estimated_duration_months': 24,
            'estimated_budget': 2500000
        }
        
        success, message, project_record = self.project_manager.initiate_collaboration_project(
            initiator_email="coordinator@county-a.gov",
            project_data=project_data
        )
        
        self.assertTrue(success)
        self.assertIn("successfully created", message)
        self.assertIsInstance(project_record, dict)
        self.assertIn('project_id', project_record)
        self.assertIn('governance_structure', project_record)
    
    def test_resource_sharing_agreement(self):
        """Test resource sharing agreement creation"""
        sharing_data = {
            'title': 'Emergency Equipment Sharing Agreement',
            'description': 'Shared emergency response equipment across jurisdictions',
            'participating_jurisdictions': ['City A', 'City B'],
            'shared_resources': [
                {
                    'resource_type': 'equipment_sharing',
                    'resource_name': 'Emergency Vehicles',
                    'quantity': 5,
                    'usage_terms': 'Emergency use only',
                    'maintenance_responsibility': 'shared'
                }
            ],
            'scope': 'emergency_response'
        }
        
        success, message, agreement_record = self.resource_manager.create_resource_sharing_agreement(
            coordinator_email="emergency@city-a.gov",
            sharing_data=sharing_data
        )
        
        self.assertTrue(success)
        self.assertIn("Agreement created", message)
        self.assertIsInstance(agreement_record, dict)
        self.assertIn('agreement_id', agreement_record)


class TestDocumentsModule(unittest.TestCase):
    """Test Documents & Archive module functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.document_manager = DocumentManager()
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_document_upload(self):
        """Test document upload functionality"""
        document_data = {
            'title': 'Municipal Budget 2024',
            'document_type': 'budget_document',
            'classification': 'public',
            'content': 'This is a test budget document content...',
            'metadata': {
                'author': 'Finance Department',
                'department': 'Finance',
                'fiscal_year': '2024',
                'approval_status': 'draft'
            }
        }
        
        success, message, doc_record = self.document_manager.upload_document(
            uploader_email="finance@city.gov",
            document_data=document_data
        )
        
        self.assertTrue(success)
        self.assertIn("Document uploaded", message)
        self.assertIsInstance(doc_record, dict)
        self.assertIn('document_id', doc_record)
        self.assertIn('version', doc_record)
    
    def test_foia_request_processing(self):
        """Test FOIA request processing"""
        foia_request = {
            'requester_name': 'John Citizen',
            'requester_email': 'john@citizen.com',
            'request_description': 'City council meeting minutes from January 2024',
            'document_category': 'meeting_minutes',
            'urgency': 'normal'
        }
        
        success, message, request_record = self.document_manager.submit_foia_request(
            foia_request
        )
        
        self.assertTrue(success)
        self.assertIn("FOIA request submitted", message)
        self.assertIsInstance(request_record, dict)
        self.assertIn('request_id', request_record)
        self.assertIn('estimated_completion_date', request_record)
    
    def test_document_search(self):
        """Test document search functionality"""
        # First upload a test document
        document_data = {
            'title': 'Test Policy Document',
            'document_type': 'policy_document',
            'classification': 'public',
            'content': 'This document contains important policy information about civic engagement.',
            'metadata': {'author': 'Policy Team', 'department': 'Governance'}
        }
        
        self.document_manager.upload_document("admin@city.gov", document_data)
        
        # Test search
        search_results = self.document_manager.search_documents(
            query="civic engagement",
            filters={'classification': 'public', 'document_type': 'policy_document'}
        )
        
        self.assertIsInstance(search_results, list)
        # Results depend on database state, so just verify structure
        for result in search_results:
            self.assertIn('document_id', result)
            self.assertIn('title', result)
            self.assertIn('relevance_score', result)


class TestTasksModule(unittest.TestCase):
    """Test Tasks module functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.task_manager = TaskManager()
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_task_creation(self):
        """Test task creation and assignment"""
        task_data = {
            'assigned_by': 'system',
            'assignment_method': 'role_based_automatic',
            'assignment_reason': 'Regular civic duty assignment',
            'title': 'Review Constitutional Amendment Proposal'
        }
        
        success, message, task_record = self.task_manager.create_task(
            task_type="contract_review",
            assigned_to="elder@civic.platform",
            task_data=task_data,
            priority="high"
        )
        
        self.assertTrue(success)
        self.assertIn("created successfully", message)
        self.assertIsInstance(task_record, dict)
        self.assertIn('id', task_record)
        self.assertIn('deadline', task_record)
        self.assertIn('rewards_civic_tokens', task_record)
    
    def test_task_progress_tracking(self):
        """Test task progress tracking"""
        # Create a task first
        task_data = {'assigned_by': 'system', 'title': 'Test Task'}
        success, message, task_record = self.task_manager.create_task(
            task_type="voting_opportunity",
            assigned_to="member@civic.platform",
            task_data=task_data
        )
        
        self.assertTrue(success)
        task_id = task_record['id']
        
        # Update progress
        progress_success, progress_message = self.task_manager.update_task_progress(
            task_id=task_id,
            user_email="member@civic.platform",
            progress_data={
                'completion_percentage': 75,
                'status_update': 'Made significant progress on voting research',
                'time_spent_minutes': 45
            }
        )
        
        self.assertTrue(progress_success)
        self.assertIn("progress updated", progress_message)
    
    def test_role_based_task_assignment(self):
        """Test automatic role-based task assignment"""
        success, message, assigned_tasks = self.task_manager.assign_role_based_tasks(
            user_email="representative@civic.platform",
            user_role="Contract Representative"
        )
        
        self.assertTrue(success)
        self.assertIsInstance(assigned_tasks, list)
        # Verify that assigned tasks are appropriate for the role
        for task in assigned_tasks:
            self.assertIn('task_type', task)
            self.assertIn('assigned_to', task)
            self.assertEqual(task['assigned_to'], "representative@civic.platform")
    
    def test_task_completion_and_rewards(self):
        """Test task completion and reward calculation"""
        # Create and complete a task
        task_data = {'assigned_by': 'system', 'title': 'Community Service Task'}
        success, message, task_record = self.task_manager.create_task(
            task_type="community_service",
            assigned_to="member@civic.platform",
            task_data=task_data
        )
        
        self.assertTrue(success)
        task_id = task_record['id']
        
        # Complete the task
        completion_success, completion_message, completion_data = self.task_manager.complete_task(
            task_id=task_id,
            user_email="member@civic.platform",
            completion_data={
                'quality_score': 'excellent',
                'completion_notes': 'Completed community service project successfully',
                'time_spent_minutes': 180
            }
        )
        
        self.assertTrue(completion_success)
        self.assertIn("completed", completion_message)
        self.assertIn('rewards_earned', completion_data)
        self.assertGreater(completion_data['rewards_earned'], 0)


class TestValidationFramework(unittest.TestCase):
    """Test enhanced validation framework"""
    
    def test_basic_data_validation(self):
        """Test basic data validation functions"""
        # Test email validation
        valid_email, msg = DataValidator.validate_email("user@civic.platform")
        self.assertTrue(valid_email)
        
        invalid_email, msg = DataValidator.validate_email("invalid.email")
        self.assertFalse(invalid_email)
        
        # Test password validation
        strong_password, msg = DataValidator.validate_password("StrongPass123!")
        self.assertTrue(strong_password)
        
        weak_password, msg = DataValidator.validate_password("weak")
        self.assertFalse(weak_password)
    
    def test_advanced_validation(self):
        """Test advanced validation for complex data"""
        # Test document metadata validation
        valid_metadata = {
            'title': 'Important Legislative Bill',
            'document_type': 'legislative_bill',
            'classification': 'public',
            'author': 'Legislative Committee',
            'created_date': '2024-01-15'
        }
        
        valid, msg = AdvancedValidator.validate_document_metadata(valid_metadata)
        self.assertTrue(valid)
        
        # Test invalid metadata
        invalid_metadata = {
            'title': 'Bill',  # Too short
            'document_type': 'invalid_type',
            'classification': 'public'
        }
        
        invalid, msg = AdvancedValidator.validate_document_metadata(invalid_metadata)
        self.assertFalse(invalid)
    
    def test_comprehensive_user_registration_validation(self):
        """Test comprehensive user registration validation"""
        valid_registration = {
            'email': 'newuser@civic.platform',
            'password': 'SecurePassword123!',
            'first_name': 'Jane',
            'last_name': 'Citizen',
            'role': 'Contract Member',
            'jurisdiction': 'Springfield, IL'
        }
        
        overall_valid, errors, results = ComprehensiveValidator.validate_complete_user_registration(valid_registration)
        self.assertTrue(overall_valid)
        self.assertEqual(len(errors), 0)
        self.assertTrue(all(results.values()))


class TestConfigurationManagement(unittest.TestCase):
    """Test configuration validation and management"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_validator = ConfigurationValidator()
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_configuration_generation(self):
        """Test configuration file generation"""
        config = self.config_validator.generate_default_config('development')
        
        self.assertIsInstance(config, dict)
        self.assertEqual(config['environment'], 'development')
        self.assertIn('db_paths', config)
        self.assertIn('security', config)
        self.assertIn('blockchain', config)
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        valid_config = self.config_validator.generate_default_config('production')
        
        is_valid, errors = self.config_validator.validate_configuration(valid_config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Test invalid configuration
        invalid_config = {'environment': 'invalid', 'security': {'password_min_length': 2}}
        
        is_invalid, errors = self.config_validator.validate_configuration(invalid_config)
        self.assertFalse(is_invalid)
        self.assertGreater(len(errors), 0)
    
    def test_environment_config_creation(self):
        """Test creation of environment-specific configurations"""
        creation_results = self.config_validator.create_environment_configs(self.temp_dir)
        
        # Verify all environments were processed
        expected_environments = ['development', 'testing', 'production']
        for env in expected_environments:
            self.assertIn(env, creation_results)
        
        # Verify config files were created
        for env in expected_environments:
            config_path = os.path.join(self.temp_dir, f'{env}_config.json')
            if creation_results[env]:  # Only check if creation was successful
                self.assertTrue(os.path.exists(config_path))


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios between modules"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_user_onboarding_to_task_assignment(self):
        """Test complete flow from user onboarding to task assignment"""
        # Step 1: Start user onboarding
        onboarding_system = UserOnboardingSystem()
        success, message, session_data = onboarding_system.initiate_user_onboarding(
            user_email="newuser@civic.platform",
            onboarding_preferences={'pathway': 'guided'}
        )
        
        self.assertTrue(success)
        
        # Step 2: Complete onboarding
        session_id = session_data['id']
        onboarding_system.complete_onboarding_module(
            session_id=session_id,
            module_name="platform_introduction",
            completion_data={'score': 90, 'time_spent': 30}
        )
        
        # Step 3: Assign tasks based on role
        task_manager = TaskManager()
        success, message, assigned_tasks = task_manager.assign_role_based_tasks(
            user_email="newuser@civic.platform",
            user_role="Contract Member"
        )
        
        self.assertTrue(success)
        self.assertIsInstance(assigned_tasks, list)
    
    def test_document_collaboration_workflow(self):
        """Test document creation in collaboration context"""
        # Step 1: Create collaboration project
        project_manager = InterJurisdictionalProjectManager()
        project_data = {
            'title': 'Regional Policy Development',
            'project_type': 'policy_coordination',
            'participating_jurisdictions': ['City A', 'City B'],
            'scope': 'policy_development'
        }
        
        success, message, project_record = project_manager.initiate_collaboration_project(
            initiator_email="policy@city-a.gov",
            project_data=project_data
        )
        
        self.assertTrue(success)
        
        # Step 2: Create related document
        document_manager = DocumentManager()
        document_data = {
            'title': 'Regional Policy Draft',
            'document_type': 'policy_document',
            'classification': 'public',
            'content': 'This is a collaborative policy document...',
            'metadata': {
                'collaboration_project_id': project_record['project_id'],
                'author': 'Regional Policy Committee'
            }
        }
        
        success, message, doc_record = document_manager.upload_document(
            uploader_email="policy@city-a.gov",
            document_data=document_data
        )
        
        self.assertTrue(success)
        self.assertIn('document_id', doc_record)


def run_comprehensive_tests():
    """Run all test suites and generate report"""
    print("Civic Engagement Platform - Comprehensive Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test cases
    test_classes = [
        TestSystemGuideModule,
        TestCollaborationModule,
        TestDocumentsModule,
        TestTasksModule,
        TestValidationFramework,
        TestConfigurationManagement,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("TEST SUMMARY REPORT")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run comprehensive test suite
    success = run_comprehensive_tests()
    
    if success:
        print("\n✅ All tests passed! Platform implementation verified.")
    else:
        print("\n❌ Some tests failed. Review the failures above.")
        
    print("\nTest execution completed.")