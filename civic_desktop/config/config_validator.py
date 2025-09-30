# Configuration Validator - Environment-Aware Configuration Management
"""
Comprehensive configuration validation and environment management system
for the Civic Engagement Platform.
"""

import json
import os
from typing import Dict, Any, List, Tuple
import logging

class ConfigurationValidator:
    """Validates and manages environment-specific configurations"""
    
    def __init__(self):
        self.valid_environments = ['development', 'testing', 'production']
        # Required top-level keys for flat configuration structure
        self.required_db_paths = [
            'users_db_path', 'blockchain_db_path', 'debates_db_path',
            'moderation_db_path', 'contracts_db_path', 'training_db_path',
            'crypto_db_path', 'tasks_db_path', 'notifications_db_path',
            'analytics_db_path', 'events_db_path', 'communications_db_path',
            'surveys_db_path', 'petitions_db_path', 'documents_db_path',
            'transparency_db_path', 'collaboration_db_path'
        ]
        self.required_settings = [
            'debug_mode', 'auto_backup', 'blockchain_auto_sync',
            'task_auto_creation', 'task_notifications_enabled'
        ]
        
    def validate_configuration(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Comprehensive configuration validation for flat config structure"""
        errors = []
        
        # Validate environment
        environment = config.get('environment', 'production')
        if environment not in self.valid_environments:
            errors.append(f"Invalid environment: {environment}. Must be one of {self.valid_environments}")
        
        # Validate required database paths
        for db_path_key in self.required_db_paths:
            if db_path_key not in config:
                errors.append(f"Missing required database path: {db_path_key}")
        
        # Validate required settings
        for setting_key in self.required_settings:
            if setting_key not in config:
                errors.append(f"Missing required setting: {setting_key}")
        
        # Validate security settings
        errors.extend(self._validate_security_settings(config))
        
        # Validate task management settings
        errors.extend(self._validate_task_settings(config))
        
        # Environment-specific validation
        if environment == 'production':
            errors.extend(self._validate_production_requirements(config))
        
        return len(errors) == 0, errors
    
    def _validate_security_settings(self, config: Dict[str, Any]) -> List[str]:
        """Validate security-related settings in flat config"""
        errors = []
        
        # Password minimum length validation
        password_min_length = config.get('password_min_length', 0)
        if password_min_length < 8:
            errors.append("Password minimum length must be at least 8 characters")
        
        # Session timeout validation
        session_timeout = config.get('session_timeout_minutes', 0)
        if session_timeout < 15 or session_timeout > 1440:  # 15 minutes to 24 hours
            errors.append("Session timeout must be between 15 and 1440 minutes")
        
        # Max login attempts validation
        max_attempts = config.get('max_login_attempts', 0)
        if max_attempts < 3 or max_attempts > 10:
            errors.append("Max login attempts must be between 3 and 10")
        
        return errors
    
    def _validate_task_settings(self, config: Dict[str, Any]) -> List[str]:
        """Validate task management settings"""
        errors = []
        
        # Validate task reminder intervals if present
        if 'task_reminder_intervals' in config:
            intervals = config['task_reminder_intervals']
            if not isinstance(intervals, dict):
                errors.append("task_reminder_intervals must be a dictionary")
            else:
                required_priorities = ['low', 'normal', 'high', 'urgent', 'critical']
                for priority in required_priorities:
                    if priority not in intervals:
                        errors.append(f"Missing reminder interval for priority: {priority}")
                    elif not isinstance(intervals[priority], (int, float)) or intervals[priority] <= 0:
                        errors.append(f"Reminder interval for {priority} must be a positive number")
        
        # Validate validation thresholds if present
        if 'validation_thresholds' in config:
            thresholds = config['validation_thresholds']
            if not isinstance(thresholds, dict):
                errors.append("validation_thresholds must be a dictionary")
            else:
                required_levels = ['city', 'state', 'country', 'founder']
                for level in required_levels:
                    if level not in thresholds:
                        errors.append(f"Missing validation threshold for level: {level}")
                    elif not isinstance(thresholds[level], (int, float)) or not (0 < thresholds[level] <= 1):
                        errors.append(f"Validation threshold for {level} must be between 0 and 1")
        
        return errors
    
    def _validate_production_requirements(self, config: Dict[str, Any]) -> List[str]:
        """Validate production environment requirements"""
        errors = []
        
        # Production should have stricter password requirements
        password_min_length = config.get('password_min_length', 0)
        if password_min_length < 12:
            errors.append("Production environment requires minimum password length of 12")
        
        # Production should have shorter session timeouts
        session_timeout = config.get('session_timeout_minutes', 0)
        if session_timeout > 480:  # 8 hours
            errors.append("Production environment should have session timeout <= 8 hours (480 minutes)")
        
        # Production should have debug mode disabled
        if config.get('debug_mode', False):
            errors.append("Production environment should have debug_mode set to false")
        
        return errors
    
    def generate_default_config(self, environment: str = 'development') -> Dict[str, Any]:
        """Generate default flat configuration matching main.py structure"""
        from pathlib import Path
        
        # Determine base paths based on environment
        env_prefix = '' if environment == 'production' else f'{environment}_'
        
        base_config = {
            # Environment identifier
            'environment': environment,
            
            # Database paths (flat structure matching main.py)
            'users_db_path': f'users/{env_prefix}users_db.json',
            'blockchain_db_path': f'blockchain/{env_prefix}blockchain_db.json',
            'debates_db_path': f'debates/{env_prefix}debates_db.json',
            'moderation_db_path': f'moderation/{env_prefix}moderation_db.json',
            'contracts_db_path': f'contracts/{env_prefix}contracts_db.json',
            'training_db_path': f'training/{env_prefix}training_db.json',
            'crypto_db_path': f'crypto/{env_prefix}crypto_db.json',
            'tasks_db_path': f'tasks/{env_prefix}tasks_db.json',
            'notifications_db_path': f'tasks/{env_prefix}notifications_db.json',
            'task_integration_config_path': f'tasks/{env_prefix}integration_config.json',
            'analytics_db_path': f'analytics/{env_prefix}analytics_db.json',
            'events_db_path': f'events/{env_prefix}events_db.json',
            'communications_db_path': f'communications/{env_prefix}messages_db.json',
            'surveys_db_path': f'surveys/{env_prefix}surveys_db.json',
            'petitions_db_path': f'petitions/{env_prefix}petitions_db.json',
            'documents_db_path': f'documents/{env_prefix}documents_db.json',
            'transparency_db_path': f'transparency/{env_prefix}transparency_db.json',
            'collaboration_db_path': f'collaboration/{env_prefix}collaboration_db.json',
            
            # Key storage
            'private_keys_path': f'users/{env_prefix}private_keys',
            
            # Security settings (flat keys)
            'password_min_length': 8 if environment != 'production' else 12,
            'session_timeout_minutes': 480 if environment != 'production' else 240,
            'max_login_attempts': 5,
            'require_special_chars': environment == 'production',
            'lockout_duration_minutes': 30 if environment == 'production' else 5,
            
            # System settings
            'debug_mode': environment == 'development',
            'auto_backup': environment == 'production',
            'blockchain_auto_sync': True,
            'auto_update_check': environment == 'production',
            
            # Task management settings
            'task_auto_creation': True,
            'task_notifications_enabled': True,
            'validation_auto_assignment': True,
            'voting_auto_assignment': True,
            'contract_auto_assignment': True,
            'task_expiration_enabled': environment == 'production',
            'reminder_system_enabled': True,
            
            # Task reminder intervals (hours)
            'task_reminder_intervals': {
                'low': 48 if environment == 'production' else 2,
                'normal': 24 if environment == 'production' else 1,
                'high': 12 if environment == 'production' else 0.5,
                'urgent': 6 if environment == 'production' else 0.25,
                'critical': 2 if environment == 'production' else 0.1
            },
            
            # Validation thresholds
            'validation_thresholds': {
                'city': 0.33 if environment == 'production' else 0.20,
                'state': 0.25 if environment == 'production' else 0.15,
                'country': 0.20 if environment == 'production' else 0.10,
                'founder': 0.10 if environment == 'production' else 0.05
            },
            
            # Notification settings
            'email_enabled': False,
            'sms_enabled': False,
            'push_enabled': False,
            'in_app_enabled': True,
            'quiet_hours_enabled': environment == 'production',
            'quiet_start': '22:00' if environment == 'production' else '23:00',
            'quiet_end': '07:00' if environment == 'production' else '06:00',
            'batch_notifications': environment == 'production',
            'max_daily_notifications': 10 if environment == 'production' else 100,
            
            # Blockchain settings
            'validator_rotation_enabled': environment == 'production',
            'consensus_threshold': 0.67 if environment == 'production' else 0.51,
            'block_creation_interval': 300 if environment == 'production' else 60,
            'max_block_size': 1048576 if environment == 'production' else 2097152,
            'auto_validator_assignment': True,
            'backup_frequency_hours': 24 if environment == 'production' else 1,
            
            # UI settings
            'theme': 'civic_light' if environment == 'production' else 'civic_debug',
            'default_tab': 'tasks',
            'show_task_counter': True,
            'show_urgent_notifications': True,
            'auto_refresh_interval': 30 if environment == 'production' else 10,
            'compact_mode': False,
            
            # Integration settings
            'cross_module_sync': True,
            'auto_task_generation': True,
            'real_time_updates': True,
            'batch_processing': False,
            'integration_retry_attempts': 3 if environment == 'production' else 5,
            'integration_timeout_seconds': 30 if environment == 'production' else 10,
        }
        
        # Add testing-specific settings
        if environment == 'testing':
            base_config.update({
                'mock_external_services': True,
                'generate_test_data': True,
                'enable_test_users': True,
                'fast_task_creation': True,
                'skip_blockchain_verification': False,
                'verbose_logging': True
            })
        
        return base_config
    
    def create_environment_configs(self, base_path: str = 'config/') -> Dict[str, bool]:
        """Create configuration files for all environments"""
    def create_environment_configs(self, base_path: str = 'config/') -> Dict[str, bool]:
        """Create configuration files for all environments"""
        
        results = {}
        os.makedirs(base_path, exist_ok=True)
        
        for env in self.valid_environments:
            config = self.generate_default_config(env)
            config_path = os.path.join(base_path, f'{env}_config.json')
            
            try:
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                results[env] = True
                print(f"Created {env} configuration: {config_path}")
            except Exception as e:
                results[env] = False
                print(f"Failed to create {env} configuration: {e}")
        
        return results
    
    def test_configuration_switching(self, config_dir: str = 'config/') -> Dict[str, Any]:
        """Test configuration switching between environments"""
        
        test_results = {
            'environments_tested': [],
            'validation_results': {},
            'switching_success': {},
            'errors': []
        }
        
        for env in self.valid_environments:
            config_path = os.path.join(config_dir, f'{env}_config.json')
            
            try:
                # Load configuration
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Validate configuration
                is_valid, errors = self.validate_configuration(config)
                
                test_results['environments_tested'].append(env)
                test_results['validation_results'][env] = {
                    'valid': is_valid,
                    'errors': errors
                }
                test_results['switching_success'][env] = is_valid
                
                if not is_valid:
                    test_results['errors'].extend([f"{env}: {error}" for error in errors])
                
                print(f"Environment {env}: {'✓ Valid' if is_valid else '✗ Invalid'}")
                if errors:
                    for error in errors:
                        print(f"  - {error}")
                        
            except FileNotFoundError:
                error_msg = f"Configuration file not found: {config_path}"
                test_results['errors'].append(error_msg)
                test_results['switching_success'][env] = False
                print(f"Environment {env}: ✗ {error_msg}")
                
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON in {config_path}: {e}"
                test_results['errors'].append(error_msg)
                test_results['switching_success'][env] = False
                print(f"Environment {env}: ✗ {error_msg}")
        
        # Overall test success
        test_results['overall_success'] = all(test_results['switching_success'].values())
        
        return test_results


# Testing and usage example
if __name__ == "__main__":
    print("Configuration Validator - Civic Engagement Platform")
    print("=" * 60)
    
    validator = ConfigurationValidator()
    
    print("\n1. Creating environment-specific configurations...")
    creation_results = validator.create_environment_configs()
    
    for env, success in creation_results.items():
        status = "✓ Created" if success else "✗ Failed"
        print(f"  {env}: {status}")
    
    print("\n2. Testing configuration validation...")
    test_results = validator.test_configuration_switching()
    
    print(f"\nEnvironments tested: {len(test_results['environments_tested'])}")
    print(f"Overall test success: {'✓ Pass' if test_results['overall_success'] else '✗ Fail'}")
    
    if test_results['errors']:
        print(f"\nErrors found: {len(test_results['errors'])}")
        for error in test_results['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    print("\n3. Testing individual environment configuration...")
    test_config = validator.generate_default_config('development')
    is_valid, errors = validator.validate_configuration(test_config)
    
    print(f"Generated development config: {'✓ Valid' if is_valid else '✗ Invalid'}")
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    
    print("\nConfiguration validation testing completed!")