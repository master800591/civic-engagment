"""
Comprehensive Configuration System Tests
Tests configuration loading, validation, environment switching, and security
"""

import pytest
import json
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_validator import ConfigurationValidator


class TestConfigurationValidator:
    """Test configuration validation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = ConfigurationValidator()
    
    def test_validator_initialization(self):
        """Test validator initializes with correct settings"""
        assert self.validator.valid_environments == ['development', 'testing', 'production']
        assert len(self.validator.required_db_paths) > 0
        assert len(self.validator.required_settings) > 0
    
    def test_generate_development_config(self):
        """Test development config generation"""
        config = self.validator.generate_default_config('development')
        
        assert config['environment'] == 'development'
        assert config['debug_mode'] is True
        assert config['password_min_length'] == 8
        assert config['session_timeout_minutes'] == 480
        assert 'development_' in config['users_db_path']
        
    def test_generate_testing_config(self):
        """Test testing config generation"""
        config = self.validator.generate_default_config('testing')
        
        assert config['environment'] == 'testing'
        assert config['debug_mode'] is False
        assert 'testing_' in config['users_db_path']
        assert 'mock_external_services' in config
        assert config['mock_external_services'] is True
        
    def test_generate_production_config(self):
        """Test production config generation"""
        config = self.validator.generate_default_config('production')
        
        assert config['environment'] == 'production'
        assert config['debug_mode'] is False
        assert config['password_min_length'] == 12
        assert config['session_timeout_minutes'] == 240
        assert config['auto_backup'] is True
        assert 'users_db.json' in config['users_db_path']
        assert 'production_' not in config['users_db_path']
    
    def test_validate_valid_config(self):
        """Test validation passes for valid config"""
        config = self.validator.generate_default_config('development')
        is_valid, errors = self.validator.validate_configuration(config)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_missing_environment(self):
        """Test validation fails when environment is missing"""
        config = self.validator.generate_default_config('development')
        del config['environment']
        
        is_valid, errors = self.validator.validate_configuration(config)
        
        # Should still pass but use default 'production' environment
        # However, it will fail production requirements
        assert is_valid is False
    
    def test_validate_missing_db_paths(self):
        """Test validation fails when required db paths are missing"""
        config = self.validator.generate_default_config('development')
        del config['users_db_path']
        del config['blockchain_db_path']
        
        is_valid, errors = self.validator.validate_configuration(config)
        
        assert is_valid is False
        assert any('users_db_path' in error for error in errors)
        assert any('blockchain_db_path' in error for error in errors)
    
    def test_validate_missing_settings(self):
        """Test validation fails when required settings are missing"""
        config = self.validator.generate_default_config('development')
        del config['debug_mode']
        del config['task_auto_creation']
        
        is_valid, errors = self.validator.validate_configuration(config)
        
        assert is_valid is False
        assert any('debug_mode' in error for error in errors)
        assert any('task_auto_creation' in error for error in errors)


class TestSecurityValidation:
    """Test security settings validation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = ConfigurationValidator()
    
    def test_password_min_length_validation(self):
        """Test password minimum length validation"""
        config = self.validator.generate_default_config('development')
        
        # Test too short
        config['password_min_length'] = 4
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is False
        assert any('Password minimum length' in error for error in errors)
        
        # Test valid
        config['password_min_length'] = 8
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is True
    
    def test_session_timeout_validation(self):
        """Test session timeout validation"""
        config = self.validator.generate_default_config('development')
        
        # Test too short
        config['session_timeout_minutes'] = 5
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is False
        assert any('Session timeout' in error for error in errors)
        
        # Test too long
        config['session_timeout_minutes'] = 2000
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is False
        
        # Test valid
        config['session_timeout_minutes'] = 120
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is True
    
    def test_max_login_attempts_validation(self):
        """Test max login attempts validation"""
        config = self.validator.generate_default_config('development')
        
        # Test too few
        config['max_login_attempts'] = 2
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is False
        assert any('Max login attempts' in error for error in errors)
        
        # Test too many
        config['max_login_attempts'] = 15
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is False
        
        # Test valid
        config['max_login_attempts'] = 5
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is True
    
    def test_production_security_requirements(self):
        """Test production environment has stricter security"""
        config = self.validator.generate_default_config('production')
        
        # Production should require 12+ character passwords
        assert config['password_min_length'] >= 12
        
        # Production should have shorter session timeouts
        assert config['session_timeout_minutes'] <= 480
        
        # Production should not have debug mode
        assert config['debug_mode'] is False


class TestTaskManagementValidation:
    """Test task management settings validation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = ConfigurationValidator()
    
    def test_task_reminder_intervals_validation(self):
        """Test task reminder intervals validation"""
        config = self.validator.generate_default_config('development')
        
        # Test invalid intervals (negative)
        config['task_reminder_intervals']['low'] = -5
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is False
        assert any('Reminder interval' in error for error in errors)
        
        # Test valid intervals
        config['task_reminder_intervals']['low'] = 24
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is True
    
    def test_validation_thresholds_validation(self):
        """Test validation thresholds validation"""
        config = self.validator.generate_default_config('development')
        
        # Test invalid threshold (> 1)
        config['validation_thresholds']['city'] = 1.5
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is False
        assert any('Validation threshold' in error for error in errors)
        
        # Test invalid threshold (<= 0)
        config['validation_thresholds']['city'] = 0
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is False
        
        # Test valid threshold
        config['validation_thresholds']['city'] = 0.33
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is True
    
    def test_missing_task_priority_levels(self):
        """Test validation fails when task priorities are missing"""
        config = self.validator.generate_default_config('development')
        
        del config['task_reminder_intervals']['urgent']
        is_valid, errors = self.validator.validate_configuration(config)
        assert is_valid is False
        assert any('urgent' in error for error in errors)


class TestEnvironmentSwitching:
    """Test environment switching functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = ConfigurationValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_all_environment_configs(self):
        """Test creating config files for all environments"""
        results = self.validator.create_environment_configs(self.temp_dir)
        
        assert results['development'] is True
        assert results['testing'] is True
        assert results['production'] is True
        
        # Verify files were created
        dev_config = Path(self.temp_dir) / 'development_config.json'
        test_config = Path(self.temp_dir) / 'testing_config.json'
        prod_config = Path(self.temp_dir) / 'production_config.json'
        
        assert dev_config.exists()
        assert test_config.exists()
        assert prod_config.exists()
    
    def test_config_files_are_valid_json(self):
        """Test created config files are valid JSON"""
        self.validator.create_environment_configs(self.temp_dir)
        
        for env in ['development', 'testing', 'production']:
            config_file = Path(self.temp_dir) / f'{env}_config.json'
            with open(config_file, 'r') as f:
                config = json.load(f)  # Should not raise
            assert config['environment'] == env
    
    def test_config_switching_validation(self):
        """Test configuration switching between environments"""
        self.validator.create_environment_configs(self.temp_dir)
        
        test_results = self.validator.test_configuration_switching(self.temp_dir)
        
        assert test_results['overall_success'] is True
        assert len(test_results['environments_tested']) == 3
        assert test_results['switching_success']['development'] is True
        assert test_results['switching_success']['testing'] is True
        assert test_results['switching_success']['production'] is True
    
    def test_invalid_config_detected(self):
        """Test that invalid configs are detected during switching"""
        # Create an invalid config
        invalid_config = {'environment': 'development', 'invalid': True}
        invalid_path = Path(self.temp_dir) / 'development_config.json'
        
        with open(invalid_path, 'w') as f:
            json.dump(invalid_config, f)
        
        test_results = self.validator.test_configuration_switching(self.temp_dir)
        
        assert test_results['overall_success'] is False
        assert len(test_results['errors']) > 0


class TestConfigurationIntegration:
    """Integration tests for configuration system"""
    
    def test_config_matches_main_structure(self):
        """Test that generated configs match main.py expectations"""
        validator = ConfigurationValidator()
        config = validator.generate_default_config('development')
        
        # Check all expected keys from main.py
        expected_keys = [
            'users_db_path', 'blockchain_db_path', 'debates_db_path',
            'moderation_db_path', 'contracts_db_path', 'training_db_path',
            'crypto_db_path', 'tasks_db_path', 'notifications_db_path',
            'private_keys_path', 'debug_mode', 'auto_backup',
            'task_auto_creation', 'task_notifications_enabled',
            'task_reminder_intervals', 'validation_thresholds'
        ]
        
        for key in expected_keys:
            assert key in config, f"Missing expected key: {key}"
    
    def test_environment_specific_differences(self):
        """Test that different environments have appropriate differences"""
        validator = ConfigurationValidator()
        
        dev_config = validator.generate_default_config('development')
        prod_config = validator.generate_default_config('production')
        
        # Development should be more permissive
        assert dev_config['debug_mode'] is True
        assert prod_config['debug_mode'] is False
        
        assert dev_config['password_min_length'] < prod_config['password_min_length']
        assert dev_config['session_timeout_minutes'] > prod_config['session_timeout_minutes']
        
        # Database paths should differ
        assert 'development_' in dev_config['users_db_path']
        assert 'development_' not in prod_config['users_db_path']


def run_tests():
    """Run all configuration tests"""
    pytest.main([__file__, '-v', '-s'])


if __name__ == '__main__':
    run_tests()
