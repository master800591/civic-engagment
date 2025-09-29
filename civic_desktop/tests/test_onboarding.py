"""
Test Onboarding Modules
Comprehensive tests for the interactive onboarding system
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
import sys

# Add the civic_desktop directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from system_guide.onboarding_backend import UserOnboardingSystem
    from system_guide.onboarding import (
        ALL_ROLE_MODULES, 
        COMPETENCY_THRESHOLDS, 
        CHECKPOINT_WEIGHTS
    )
    from system_guide.onboarding.troubleshooting import (
        troubleshooting_workflows, 
        contextual_help_triggers
    )
except ImportError as e:
    print(f"Warning: Could not import onboarding modules: {e}")
    # Create mock objects for testing
    class MockUserOnboardingSystem:
        def __init__(self):
            pass
    UserOnboardingSystem = MockUserOnboardingSystem
    ALL_ROLE_MODULES = {}
    COMPETENCY_THRESHOLDS = {}
    CHECKPOINT_WEIGHTS = {}
    troubleshooting_workflows = {}
    contextual_help_triggers = {}


class TestOnboardingModules(unittest.TestCase):
    """Test individual onboarding modules structure and content"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_all_roles_have_modules(self):
        """Test that all expected roles have onboarding modules"""
        expected_roles = [
            'Contract Member',
            'Contract Representative', 
            'Contract Senator',
            'Contract Elder',
            'Contract Founder'
        ]
        
        for role in expected_roles:
            self.assertIn(role, ALL_ROLE_MODULES, f"Role {role} missing from ALL_ROLE_MODULES")
            self.assertIsInstance(ALL_ROLE_MODULES[role], dict, f"Modules for {role} should be a dictionary")
            self.assertGreater(len(ALL_ROLE_MODULES[role]), 0, f"Role {role} should have at least one module")
    
    def test_module_structure_completeness(self):
        """Test that all modules have required structure"""
        required_fields = ['title', 'description', 'interactive_elements', 'competency_questions']
        
        for role, modules in ALL_ROLE_MODULES.items():
            for module_name, module_data in modules.items():
                with self.subTest(role=role, module=module_name):
                    for field in required_fields:
                        self.assertIn(field, module_data, 
                                    f"Module {role}.{module_name} missing required field: {field}")
    
    def test_competency_questions_structure(self):
        """Test that competency questions have proper structure"""
        for role, modules in ALL_ROLE_MODULES.items():
            for module_name, module_data in modules.items():
                questions = module_data.get('competency_questions', [])
                
                for i, question in enumerate(questions):
                    with self.subTest(role=role, module=module_name, question=i):
                        self.assertIsInstance(question, dict, "Question should be a dictionary")
                        self.assertIn('question', question, "Question missing 'question' field")
                        self.assertIn('correct_answer', question, "Question missing 'correct_answer' field")
                        self.assertIn('points', question, "Question missing 'points' field")
                        
                        # Validate points are reasonable
                        points = question['points']
                        self.assertIsInstance(points, int, "Points should be an integer")
                        self.assertGreater(points, 0, "Points should be positive")
                        self.assertLessEqual(points, 100, "Points should not exceed 100")
    
    def test_interactive_elements_structure(self):
        """Test that interactive elements have proper structure"""
        for role, modules in ALL_ROLE_MODULES.items():
            for module_name, module_data in modules.items():
                elements = module_data.get('interactive_elements', [])
                
                for i, element in enumerate(elements):
                    with self.subTest(role=role, module=module_name, element=i):
                        self.assertIsInstance(element, dict, "Interactive element should be a dictionary")
                        self.assertIn('type', element, "Interactive element missing 'type' field")
                        
                        # Check type is valid
                        valid_types = ['tutorial', 'simulation', 'case_study', 'role_play', 'interactive_guide', 
                                     'constitutional_review', 'crisis_simulation', 'emergency_drill', 
                                     'collaborative_exercise', 'judicial_simulation']
                        self.assertIn(element['type'], valid_types, 
                                    f"Invalid interactive element type: {element['type']}")
    
    def test_competency_thresholds_valid(self):
        """Test that competency thresholds are reasonable"""
        for role, threshold in COMPETENCY_THRESHOLDS.items():
            with self.subTest(role=role):
                self.assertIsInstance(threshold, int, f"Threshold for {role} should be an integer")
                self.assertGreaterEqual(threshold, 0, f"Threshold for {role} should be non-negative")
                self.assertLessEqual(threshold, 100, f"Threshold for {role} should not exceed 100")
                
                # Check thresholds increase with role complexity
                if role == 'Contract Member':
                    self.assertLessEqual(threshold, 75, "Contract Member threshold should be reasonable for beginners")
                elif role == 'Contract Founder':
                    self.assertGreaterEqual(threshold, 90, "Contract Founder threshold should be high")


class TestOnboardingSystem(unittest.TestCase):
    """Test the onboarding system backend functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Mock the ENV_CONFIG to use temp directory
        with patch('system_guide.onboarding_backend.ENV_CONFIG', 
                  {'system_guide_db_path': os.path.join(self.temp_dir, 'onboarding_db.json')}):
            self.onboarding_system = UserOnboardingSystem()
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_system_initialization(self):
        """Test that onboarding system initializes correctly"""
        self.assertIsNotNone(self.onboarding_system)
        
        # Test pathways loading
        pathways = self.onboarding_system.load_onboarding_pathways()
        self.assertIsInstance(pathways, dict)
        self.assertGreater(len(pathways), 0)
    
    def test_user_onboarding_initiation(self):
        """Test user onboarding session creation"""
        if hasattr(self.onboarding_system, 'initiate_user_onboarding'):
            result = self.onboarding_system.initiate_user_onboarding(
                user_email="test@civic.platform",
                onboarding_preferences={'pathway': 'guided', 'pace': 'normal'}
            )
            
            # Handle both (success, message) and (success, session_data) return formats
            if len(result) == 2:
                success, data = result
                self.assertTrue(success, f"Onboarding initiation failed: {data}")
                
                if isinstance(data, dict):
                    # data is session_data
                    self.assertIn('id', data, "Session data should have an ID")
                    self.assertIn('user_email', data, "Session data should have user email") 
                else:
                    # data is message string, this is also valid
                    self.assertIsInstance(data, str)
            else:
                success, message, session_data = result
                self.assertTrue(success, f"Onboarding initiation failed: {message}")
                self.assertIsInstance(session_data, dict)
                self.assertIn('id', session_data)
    
    def test_module_content_loading(self):
        """Test module content loading"""
        if hasattr(self.onboarding_system, 'get_module_content'):
            # Test with a common module name
            content = self.onboarding_system.get_module_content('platform_introduction')
            
            self.assertIsInstance(content, dict)
            self.assertIn('title', content)
            self.assertIn('description', content)
    
    def test_pathway_prerequisites(self):
        """Test that pathway prerequisites are properly configured"""
        pathways = self.onboarding_system.load_onboarding_pathways()
        
        for role, pathway in pathways.items():
            prerequisites = pathway.get('prerequisites', [])
            self.assertIsInstance(prerequisites, list, f"Prerequisites for {role} should be a list")
            
            # Check that prerequisites refer to valid roles
            for prereq in prerequisites:
                self.assertIn(prereq, pathways.keys(), f"Invalid prerequisite '{prereq}' for {role}")


class TestTroubleshootingWorkflows(unittest.TestCase):
    """Test troubleshooting workflows and contextual help"""
    
    def test_troubleshooting_workflows_structure(self):
        """Test that troubleshooting workflows have proper structure"""
        for workflow_name, workflow_data in troubleshooting_workflows.items():
            with self.subTest(workflow=workflow_name):
                self.assertIsInstance(workflow_data, dict, "Workflow should be a dictionary")
                self.assertIn('title', workflow_data, f"Workflow {workflow_name} missing title")
                self.assertIn('steps', workflow_data, f"Workflow {workflow_name} missing steps")
                
                steps = workflow_data['steps']
                self.assertIsInstance(steps, list, "Steps should be a list")
                self.assertGreater(len(steps), 0, "Workflow should have at least one step")
                
                # Check step structure
                for i, step in enumerate(steps):
                    self.assertIsInstance(step, dict, f"Step {i} should be a dictionary")
                    self.assertIn('step', step, f"Step {i} missing step number")
                    self.assertIn('check', step, f"Step {i} missing check description")
                    self.assertIn('action', step, f"Step {i} missing action description")
    
    def test_contextual_help_triggers(self):
        """Test contextual help triggers configuration"""
        for trigger_name, trigger_data in contextual_help_triggers.items():
            with self.subTest(trigger=trigger_name):
                self.assertIsInstance(trigger_data, dict, "Trigger should be a dictionary")
                self.assertIn('trigger', trigger_data, f"Trigger {trigger_name} missing trigger condition")
                self.assertIn('recommended_action', trigger_data, f"Trigger {trigger_name} missing recommended action")
                self.assertIn('priority', trigger_data, f"Trigger {trigger_name} missing priority")
                
                # Check priority is valid
                priority = trigger_data['priority']
                valid_priorities = ['low', 'medium', 'high', 'critical']
                self.assertIn(priority, valid_priorities, f"Invalid priority: {priority}")


class TestOnboardingIntegration(unittest.TestCase):
    """Test integration between onboarding components"""
    
    def test_role_module_consistency(self):
        """Test consistency between role modules and system pathways"""
        if hasattr(UserOnboardingSystem, 'load_onboarding_pathways'):
            system = UserOnboardingSystem()
            pathways = system.load_onboarding_pathways()
            
            # Check that all roles in ALL_ROLE_MODULES are in pathways
            for role in ALL_ROLE_MODULES.keys():
                self.assertIn(role, pathways, f"Role {role} missing from system pathways")
            
            # Check that pathway modules exist in ALL_ROLE_MODULES
            for role, pathway in pathways.items():
                if role in ALL_ROLE_MODULES:
                    pathway_modules = set(pathway['modules'])
                    available_modules = set(ALL_ROLE_MODULES[role].keys())
                    
                    # At least some modules should match
                    self.assertTrue(
                        len(pathway_modules.intersection(available_modules)) > 0,
                        f"No matching modules between pathway and available modules for {role}"
                    )
    
    def test_competency_threshold_consistency(self):
        """Test that competency thresholds are consistent"""
        if hasattr(UserOnboardingSystem, 'load_onboarding_pathways'):
            system = UserOnboardingSystem()
            pathways = system.load_onboarding_pathways()
            
            for role, pathway in pathways.items():
                if role in COMPETENCY_THRESHOLDS:
                    pathway_threshold = pathway.get('competency_threshold')
                    module_threshold = COMPETENCY_THRESHOLDS[role]
                    
                    self.assertEqual(
                        pathway_threshold, module_threshold,
                        f"Competency threshold mismatch for {role}: pathway={pathway_threshold}, modules={module_threshold}"
                    )


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)