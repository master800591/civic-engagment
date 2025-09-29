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
        self.required_sections = [
            'environment',
            'db_paths', 
            'security',
            'ui',
            'logging',
            'blockchain',
            'crypto',
            'features'
        ]
        
    def validate_configuration(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Comprehensive configuration validation"""
        errors = []
        
        # Check required sections
        for section in self.required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
                continue
                
            # Validate each section
            section_errors = self._validate_section(section, config[section])
            errors.extend(section_errors)
        
        # Environment-specific validation
        environment = config.get('environment', 'production')
        if environment not in self.valid_environments:
            errors.append(f"Invalid environment: {environment}. Must be one of {self.valid_environments}")
        
        # Cross-section validation
        cross_errors = self._validate_cross_sections(config)
        errors.extend(cross_errors)
        
        return len(errors) == 0, errors
    
    def _validate_section(self, section_name: str, section_data: Any) -> List[str]:
        """Validate individual configuration section"""
        errors = []
        
        if section_name == 'security':
            errors.extend(self._validate_security_section(section_data))
        elif section_name == 'db_paths':
            errors.extend(self._validate_db_paths_section(section_data))
        elif section_name == 'ui':
            errors.extend(self._validate_ui_section(section_data))
        elif section_name == 'logging':
            errors.extend(self._validate_logging_section(section_data))
        elif section_name == 'blockchain':
            errors.extend(self._validate_blockchain_section(section_data))
        elif section_name == 'crypto':
            errors.extend(self._validate_crypto_section(section_data))
        elif section_name == 'features':
            errors.extend(self._validate_features_section(section_data))
            
        return errors
    
    def _validate_security_section(self, security: Dict[str, Any]) -> List[str]:
        """Validate security configuration"""
        errors = []
        
        required_fields = ['password_min_length', 'session_timeout_minutes', 'max_login_attempts']
        for field in required_fields:
            if field not in security:
                errors.append(f"Security section missing required field: {field}")
        
        # Validate password requirements
        if security.get('password_min_length', 0) < 8:
            errors.append("Password minimum length must be at least 8 characters")
        
        # Validate session timeout
        session_timeout = security.get('session_timeout_minutes', 0)
        if session_timeout < 15 or session_timeout > 1440:  # 15 minutes to 24 hours
            errors.append("Session timeout must be between 15 and 1440 minutes")
        
        # Validate login attempts
        max_attempts = security.get('max_login_attempts', 0)
        if max_attempts < 3 or max_attempts > 10:
            errors.append("Max login attempts must be between 3 and 10")
        
        return errors
    
    def _validate_db_paths_section(self, db_paths: Dict[str, Any]) -> List[str]:
        """Validate database paths configuration"""
        errors = []
        
        required_paths = [
            'users_db', 'debates_db', 'moderation_db', 'blockchain_db',
            'contracts_db', 'training_db', 'crypto_db', 'tasks_db'
        ]
        
        for path_key in required_paths:
            if path_key not in db_paths:
                errors.append(f"Database paths missing required path: {path_key}")
                continue
                
            path = db_paths[path_key]
            if not isinstance(path, str) or not path:
                errors.append(f"Database path '{path_key}' must be a non-empty string")
                continue
                
            # Validate path format
            if not path.endswith('.json'):
                errors.append(f"Database path '{path_key}' must end with .json")
        
        return errors
    
    def _validate_ui_section(self, ui: Dict[str, Any]) -> List[str]:
        """Validate UI configuration"""
        errors = []
        
        required_fields = ['window_width', 'window_height', 'theme']
        for field in required_fields:
            if field not in ui:
                errors.append(f"UI section missing required field: {field}")
        
        # Validate window dimensions
        width = ui.get('window_width', 0)
        height = ui.get('window_height', 0)
        
        if not isinstance(width, int) or width < 800:
            errors.append("Window width must be an integer >= 800")
        
        if not isinstance(height, int) or height < 600:
            errors.append("Window height must be an integer >= 600")
        
        # Validate theme
        valid_themes = ['light', 'dark', 'auto']
        theme = ui.get('theme', '')
        if theme not in valid_themes:
            errors.append(f"Theme must be one of: {valid_themes}")
        
        return errors
    
    def _validate_logging_section(self, logging_config: Dict[str, Any]) -> List[str]:
        """Validate logging configuration"""
        errors = []
        
        required_fields = ['level', 'file_path', 'max_file_size_mb']
        for field in required_fields:
            if field not in logging_config:
                errors.append(f"Logging section missing required field: {field}")
        
        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        level = logging_config.get('level', '')
        if level not in valid_levels:
            errors.append(f"Log level must be one of: {valid_levels}")
        
        # Validate file size
        max_size = logging_config.get('max_file_size_mb', 0)
        if not isinstance(max_size, (int, float)) or max_size <= 0:
            errors.append("Max file size must be a positive number")
        
        return errors
    
    def _validate_blockchain_section(self, blockchain: Dict[str, Any]) -> List[str]:
        """Validate blockchain configuration"""
        errors = []
        
        required_fields = ['enabled', 'block_time_seconds', 'validator_count']
        for field in required_fields:
            if field not in blockchain:
                errors.append(f"Blockchain section missing required field: {field}")
        
        # Validate block time
        block_time = blockchain.get('block_time_seconds', 0)
        if not isinstance(block_time, (int, float)) or block_time < 1:
            errors.append("Block time must be a positive number >= 1 second")
        
        # Validate validator count
        validator_count = blockchain.get('validator_count', 0)
        if not isinstance(validator_count, int) or validator_count < 1:
            errors.append("Validator count must be a positive integer")
        
        return errors
    
    def _validate_crypto_section(self, crypto: Dict[str, Any]) -> List[str]:
        """Validate cryptocurrency configuration"""
        errors = []
        
        required_fields = ['enabled', 'initial_founder_balance', 'initial_member_balance']
        for field in required_fields:
            if field not in crypto:
                errors.append(f"Crypto section missing required field: {field}")
        
        # Validate balances
        founder_balance = crypto.get('initial_founder_balance', 0)
        member_balance = crypto.get('initial_member_balance', 0)
        
        if not isinstance(founder_balance, (int, float)) or founder_balance < 0:
            errors.append("Initial founder balance must be a non-negative number")
        
        if not isinstance(member_balance, (int, float)) or member_balance < 0:
            errors.append("Initial member balance must be a non-negative number")
        
        return errors
    
    def _validate_features_section(self, features: Dict[str, Any]) -> List[str]:
        """Validate features configuration"""
        errors = []
        
        feature_keys = [
            'debates_enabled', 'moderation_enabled', 'blockchain_enabled',
            'crypto_enabled', 'contracts_enabled', 'training_enabled'
        ]
        
        for feature in feature_keys:
            if feature in features:
                if not isinstance(features[feature], bool):
                    errors.append(f"Feature '{feature}' must be a boolean value")
        
        return errors
    
    def _validate_cross_sections(self, config: Dict[str, Any]) -> List[str]:
        """Validate relationships between configuration sections"""
        errors = []
        
        # If crypto is enabled, blockchain must be enabled
        crypto_enabled = config.get('crypto', {}).get('enabled', False)
        blockchain_enabled = config.get('blockchain', {}).get('enabled', False)
        
        if crypto_enabled and not blockchain_enabled:
            errors.append("Crypto features require blockchain to be enabled")
        
        # Production environment should have stricter security
        environment = config.get('environment', 'production')
        if environment == 'production':
            security = config.get('security', {})
            
            if security.get('password_min_length', 0) < 12:
                errors.append("Production environment requires minimum password length of 12")
            
            if security.get('session_timeout_minutes', 0) > 480:  # 8 hours
                errors.append("Production environment should have session timeout <= 8 hours")
        
        return errors
    
    def generate_default_config(self, environment: str = 'development') -> Dict[str, Any]:
        """Generate default configuration for specified environment"""
        
        base_config = {
            'environment': environment,
            'db_paths': {
                'users_db': 'data/users_db.json',
                'debates_db': 'data/debates_db.json',
                'moderation_db': 'data/moderation_db.json',
                'blockchain_db': 'data/blockchain_db.json',
                'contracts_db': 'data/contracts_db.json',
                'training_db': 'data/training_db.json',
                'crypto_db': 'data/crypto_db.json',
                'tasks_db': 'data/tasks_db.json',
                'collaboration_db': 'data/collaboration_db.json',
                'documents_db': 'data/documents_db.json',
                'maps_db': 'data/maps_db.json',
                'system_guide_db': 'data/system_guide_db.json'
            },
            'security': {
                'password_min_length': 8 if environment != 'production' else 12,
                'session_timeout_minutes': 480 if environment != 'production' else 240,
                'max_login_attempts': 5,
                'require_2fa': environment == 'production',
                'encryption_algorithm': 'AES-256',
                'key_rotation_days': 90
            },
            'ui': {
                'window_width': 1200,
                'window_height': 800,
                'theme': 'light',
                'auto_save_interval_seconds': 30,
                'animation_enabled': True,
                'accessibility_mode': False
            },
            'logging': {
                'level': 'DEBUG' if environment == 'development' else 'INFO',
                'file_path': f'logs/{environment}.log',
                'max_file_size_mb': 10,
                'backup_count': 5,
                'console_output': environment == 'development'
            },
            'blockchain': {
                'enabled': True,
                'block_time_seconds': 10 if environment != 'production' else 30,
                'validator_count': 3 if environment != 'production' else 7,
                'consensus_algorithm': 'PoA',
                'auto_backup': True,
                'backup_interval_hours': 6
            },
            'crypto': {
                'enabled': True,
                'initial_founder_balance': 1000,
                'initial_member_balance': 100,
                'token_symbol': 'CVC',
                'exchange_enabled': True,
                'staking_enabled': True,
                'reward_multiplier': 1.0
            },
            'features': {
                'debates_enabled': True,
                'moderation_enabled': True,
                'blockchain_enabled': True,
                'crypto_enabled': True,
                'contracts_enabled': True,
                'training_enabled': True,
                'collaboration_enabled': True,
                'documents_enabled': True,
                'maps_enabled': True,
                'tasks_enabled': True,
                'system_guide_enabled': True,
                'analytics_enabled': True
            },
            'network': {
                'p2p_enabled': environment == 'production',
                'p2p_port': 8080,
                'discovery_enabled': environment == 'production',
                'max_peers': 10,
                'connection_timeout_seconds': 30
            },
            'backup': {
                'enabled': True,
                'interval_hours': 24,
                'max_backups': 7,
                'backup_path': 'backups/',
                'compress_backups': True
            }
        }
        
        return base_config
    
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