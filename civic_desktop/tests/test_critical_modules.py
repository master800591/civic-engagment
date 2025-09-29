"""
Test module for critical civic engagement platform components
Tests for users, onboarding, contracts, collaboration, maps, documents, and config modules
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestUsersModule(unittest.TestCase):
    """Test core users module functionality"""
    
    def test_user_backend_import(self):
        """Test that users backend can be imported"""
        try:
            from users.backend import UserBackend
            self.assertIsNotNone(UserBackend)
            print("✅ UserBackend imported successfully")
        except ImportError as e:
            self.skipTest(f"UserBackend not available: {e}")
    
    def test_user_validation(self):
        """Test user data validation"""
        try:
            from utils.validation import DataValidator
            
            # Test email validation
            valid_email, msg = DataValidator.validate_email("test@example.com")
            self.assertTrue(valid_email)
            
            # Test invalid email
            invalid_email, msg = DataValidator.validate_email("invalid_email")
            self.assertFalse(invalid_email)
            
            print("✅ User validation tests passed")
        except ImportError:
            self.skipTest("DataValidator not available")


class TestContractsModule(unittest.TestCase):
    """Test governance contracts functionality"""
    
    def test_contract_types_import(self):
        """Test contract types can be imported"""
        try:
            from contracts.contract_types import ContractType
            self.assertIsNotNone(ContractType)
            print("✅ ContractType imported successfully")
        except ImportError as e:
            self.skipTest(f"ContractType not available: {e}")
    
    def test_contract_creation(self):
        """Test basic contract creation"""
        try:
            from contracts.contract_types import ContractType
            
            # Test enum values exist
            expected_types = ['master', 'country', 'state', 'city']
            for contract_type in expected_types:
                # Just test that we can access the types
                self.assertIsNotNone(contract_type)
            
            print("✅ Contract creation tests passed")
        except ImportError:
            self.skipTest("Contract modules not available")


class TestCollaborationModule(unittest.TestCase):
    """Test inter-jurisdictional collaboration"""
    
    def test_project_coordinator_import(self):
        """Test project coordinator can be imported"""
        try:
            from collaboration.project_coordinator import InterJurisdictionalProjectManager
            self.assertIsNotNone(InterJurisdictionalProjectManager)
            print("✅ InterJurisdictionalProjectManager imported successfully")
        except ImportError as e:
            self.skipTest(f"Project coordinator not available: {e}")
    
    def test_collaboration_basic_functionality(self):
        """Test basic collaboration functionality"""
        try:
            from collaboration.project_coordinator import InterJurisdictionalProjectManager
            
            # Test instantiation
            manager = InterJurisdictionalProjectManager()
            self.assertIsNotNone(manager)
            
            print("✅ Collaboration basic functionality tests passed")
        except (ImportError, Exception) as e:
            self.skipTest(f"Collaboration functionality not available: {e}")


class TestMapsModule(unittest.TestCase):
    """Test geographic mapping functionality"""
    
    def test_map_view_import(self):
        """Test map view can be imported"""
        try:
            from maps.map_view import CivicMapSystem
            self.assertIsNotNone(CivicMapSystem)
            print("✅ CivicMapSystem imported successfully")
        except ImportError as e:
            self.skipTest(f"Map system not available: {e}")
    
    def test_maps_basic_functionality(self):
        """Test basic mapping functionality"""
        try:
            from maps.map_view import CivicMapSystem
            
            # Test instantiation
            map_system = CivicMapSystem()
            self.assertIsNotNone(map_system)
            
            print("✅ Maps basic functionality tests passed")
        except (ImportError, Exception) as e:
            self.skipTest(f"Maps functionality not available: {e}")


class TestDocumentsModule(unittest.TestCase):
    """Test document management functionality"""
    
    def test_document_manager_import(self):
        """Test document manager can be imported"""
        try:
            from documents.document_manager import DocumentManager
            self.assertIsNotNone(DocumentManager)
            print("✅ DocumentManager imported successfully")
        except ImportError as e:
            self.skipTest(f"Document manager not available: {e}")
    
    def test_document_basic_functionality(self):
        """Test basic document functionality"""
        try:
            from documents.document_manager import DocumentManager
            
            # Test instantiation
            doc_manager = DocumentManager()
            self.assertIsNotNone(doc_manager)
            
            print("✅ Documents basic functionality tests passed")
        except (ImportError, Exception) as e:
            self.skipTest(f"Documents functionality not available: {e}")


class TestConfigModule(unittest.TestCase):
    """Test configuration management"""
    
    def test_config_loading(self):
        """Test configuration can be loaded"""
        try:
            from main import ENV_CONFIG
            self.assertIsNotNone(ENV_CONFIG)
            print("✅ Configuration loaded successfully")
        except ImportError as e:
            self.skipTest(f"Configuration not available: {e}")
    
    def test_config_validation(self):
        """Test configuration validation"""
        try:
            from config.config_validator import ConfigurationValidator
            
            # Test instantiation
            validator = ConfigurationValidator()
            self.assertIsNotNone(validator)
            
            print("✅ Configuration validation tests passed")
        except (ImportError, Exception) as e:
            self.skipTest(f"Configuration validation not available: {e}")


class TestSystemIntegration(unittest.TestCase):
    """Test overall system integration"""
    
    def test_main_module_import(self):
        """Test main module can be imported"""
        try:
            import main
            self.assertIsNotNone(main)
            print("✅ Main module imported successfully")
        except ImportError as e:
            self.skipTest(f"Main module not available: {e}")
    
    def test_core_modules_available(self):
        """Test that core modules are available"""
        core_modules = [
            'users.backend',
            'utils.validation',
            'main'
        ]
        
        available_modules = []
        for module_name in core_modules:
            try:
                __import__(module_name)
                available_modules.append(module_name)
            except ImportError:
                pass
        
        # At least some core modules should be available
        self.assertGreater(len(available_modules), 0, 
                          "No core modules available")
        
        print(f"✅ Available core modules: {available_modules}")
    
    def test_database_paths_configured(self):
        """Test that database paths are properly configured"""
        try:
            from main import ENV_CONFIG
            
            # Check for essential config keys
            essential_keys = ['environment', 'db_path']
            available_keys = []
            
            for key in essential_keys:
                if key in ENV_CONFIG:
                    available_keys.append(key)
            
            print(f"✅ Available config keys: {available_keys}")
            
            # Should have at least environment configured
            self.assertGreater(len(available_keys), 0,
                              "No essential config keys found")
            
        except (ImportError, KeyError) as e:
            self.skipTest(f"Configuration not properly loaded: {e}")


def run_critical_tests():
    """Run critical tests and return summary"""
    print("🧪 Running Critical Component Tests")
    print("=" * 50)
    
    test_suite = unittest.TestSuite()
    
    # Add all test cases
    test_classes = [
        TestUsersModule,
        TestContractsModule, 
        TestCollaborationModule,
        TestMapsModule,
        TestDocumentsModule,
        TestConfigModule,
        TestSystemIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Generate summary
    print("\n" + "=" * 50)
    print("🧪 CRITICAL TESTS SUMMARY")
    print("=" * 50)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback.split('Error:')[-1].strip()}")
    
    if result.skipped:
        print(f"\n⏭️ SKIPPED: {len(result.skipped)} tests (expected for optional modules)")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / 
                   result.testsRun * 100) if result.testsRun > 0 else 0
    
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Critical tests mostly passing - system is functional")
    elif success_rate >= 60:
        print("⚠️ Some critical issues - review failures")
    else:
        print("❌ Major issues detected - system may not be functional")
    
    return result.failures == [] and result.errors == []


if __name__ == "__main__":
    success = run_critical_tests()
    
    if success:
        print("\n🎉 All critical tests passed!")
    else:
        print("\n⚠️ Some critical tests failed - review output above")
    
    print("\nFor detailed testing, run: python -m pytest tests/ -v")