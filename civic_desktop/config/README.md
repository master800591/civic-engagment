# Configuration Module - Environment-Aware Configuration System

## Purpose
Environment-specific configuration management for development, testing, and production deployments with secure defaults and validation.

## Module Structure
```
config/
├── dev_config.json       # Development environment settings
├── test_config.json      # Test environment configuration
├── prod_config.json      # Production configuration
└── README.md             # Configuration documentation
```

## Configuration Files

### Development Configuration (dev_config.json)
```json
{
  "environment": "development",
  "debug": true,
  "blockchain_auto_rollup": false,
  "db_paths": {
    "users_db_path": "users/dev_users_db.json",
    "debates_db_path": "debates/dev_debates_db.json",
    "moderation_db_path": "moderation/dev_moderation_db.json",
    "blockchain_db_path": "blockchain/dev_blockchain_db.json",
    "validators_db_path": "blockchain/dev_validators_db.json",
    "contracts_db_path": "contracts/dev_contracts_db.json",
    "training_db_path": "training/dev_training_db.json",
    "crypto_db_path": "crypto/dev_crypto_db.json",
    "analytics_db_path": "analytics/dev_analytics_db.json",
    "events_db_path": "events/dev_events_db.json"
  },
  "security": {
    "password_min_length": 6,
    "session_timeout_minutes": 60,
    "max_login_attempts": 10,
    "encryption_key_size": 2048
  },
  "p2p": {
    "enabled": false,
    "port": 8333,
    "discovery_enabled": false,
    "max_peers": 5
  },
  "ui": {
    "theme": "default",
    "auto_refresh_seconds": 30,
    "notifications_enabled": true
  },
  "logging": {
    "level": "DEBUG",
    "file_logging": true,
    "console_logging": true
  }
}
```

### Test Configuration (test_config.json)
```json
{
  "environment": "test",
  "debug": true,
  "blockchain_auto_rollup": false,
  "db_paths": {
    "users_db_path": "users/test_users_db.json",
    "debates_db_path": "debates/test_debates_db.json",
    "moderation_db_path": "moderation/test_moderation_db.json",
    "blockchain_db_path": "blockchain/test_blockchain_db.json",
    "validators_db_path": "blockchain/test_validators_db.json",
    "contracts_db_path": "contracts/test_contracts_db.json",
    "training_db_path": "training/test_training_db.json",
    "crypto_db_path": "crypto/test_crypto_db.json",
    "analytics_db_path": "analytics/test_analytics_db.json",
    "events_db_path": "events/test_events_db.json"
  },
  "security": {
    "password_min_length": 4,
    "session_timeout_minutes": 30,
    "max_login_attempts": 20,
    "encryption_key_size": 1024
  },
  "p2p": {
    "enabled": false,
    "port": 8334,
    "discovery_enabled": false,
    "max_peers": 2
  },
  "testing": {
    "reset_db_on_start": true,
    "generate_test_data": true,
    "mock_external_services": true
  },
  "ui": {
    "theme": "test",
    "auto_refresh_seconds": 10,
    "notifications_enabled": false
  },
  "logging": {
    "level": "DEBUG",
    "file_logging": false,
    "console_logging": true
  }
}
```

### Production Configuration (prod_config.json)
```json
{
  "environment": "production",
  "debug": false,
  "blockchain_auto_rollup": true,
  "db_paths": {
    "users_db_path": "users/users_db.json",
    "debates_db_path": "debates/debates_db.json",
    "moderation_db_path": "moderation/moderation_db.json",
    "blockchain_db_path": "blockchain/blockchain_db.json",
    "validators_db_path": "blockchain/validators_db.json",
    "contracts_db_path": "contracts/contracts_db.json",
    "training_db_path": "training/training_db.json",
    "crypto_db_path": "crypto/crypto_db.json",
    "analytics_db_path": "analytics/analytics_db.json",
    "events_db_path": "events/events_db.json"
  },
  "security": {
    "password_min_length": 12,
    "session_timeout_minutes": 30,
    "max_login_attempts": 5,
    "encryption_key_size": 4096,
    "enforce_2fa": false,
    "audit_all_actions": true
  },
  "p2p": {
    "enabled": true,
    "port": 8333,
    "discovery_enabled": true,
    "max_peers": 20,
    "connection_timeout": 10
  },
  "backup": {
    "enabled": true,
    "interval_hours": 24,
    "retention_days": 90,
    "blockchain_backup": true
  },
  "ui": {
    "theme": "professional",
    "auto_refresh_seconds": 60,
    "notifications_enabled": true,
    "performance_mode": true
  },
  "logging": {
    "level": "INFO",
    "file_logging": true,
    "console_logging": false,
    "rotation_size_mb": 100,
    "retention_days": 30
  }
}
```

## AI Implementation Instructions

### Configuration Loading and Validation
```python
# Environment-Aware Configuration Loader
import json
import os
from typing import Dict, Any

class ConfigurationManager:
    def __init__(self):
        self.config = None
        self.environment = None
        self.load_configuration()
    
    def load_configuration(self):
        """Load configuration based on environment variable or default"""
        
        # Determine configuration file
        config_path = os.environ.get('CIVIC_CONFIG', 'config/prod_config.json')
        
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            self.environment = self.config.get('environment', 'production')
            
            # Validate configuration
            validation_result = self.validate_configuration(self.config)
            if not validation_result['valid']:
                raise ValueError(f"Configuration validation failed: {validation_result['errors']}")
            
            # Apply environment-specific processing
            self.config = self.process_environment_config(self.config)
            
            print(f"Configuration loaded successfully for {self.environment} environment")
            
        except FileNotFoundError:
            print(f"Configuration file not found: {config_path}")
            print("Loading default configuration...")
            self.config = self.get_default_configuration()
            self.environment = 'default'
        
        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Loading fallback configuration...")
            self.config = self.get_fallback_configuration()
            self.environment = 'fallback'
    
    def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration structure and values"""
        
        errors = []
        
        # Required sections
        required_sections = ['environment', 'db_paths', 'security', 'ui', 'logging']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Security validation
        if 'security' in config:
            security = config['security']
            
            if security.get('password_min_length', 0) < 4:
                errors.append("Password minimum length must be at least 4 characters")
            
            if security.get('session_timeout_minutes', 0) <= 0:
                errors.append("Session timeout must be positive")
            
            if security.get('encryption_key_size', 0) not in [1024, 2048, 4096]:
                errors.append("Encryption key size must be 1024, 2048, or 4096")
        
        # Database path validation
        if 'db_paths' in config:
            db_paths = config['db_paths']
            required_db_paths = [
                'users_db_path', 'debates_db_path', 'moderation_db_path',
                'blockchain_db_path', 'validators_db_path', 'contracts_db_path'
            ]
            
            for db_path_key in required_db_paths:
                if db_path_key not in db_paths:
                    errors.append(f"Missing database path: {db_path_key}")
        
        # P2P configuration validation
        if 'p2p' in config and config['p2p'].get('enabled', False):
            p2p = config['p2p']
            
            if not (1024 <= p2p.get('port', 0) <= 65535):
                errors.append("P2P port must be between 1024 and 65535")
            
            if p2p.get('max_peers', 0) <= 0:
                errors.append("Maximum peers must be positive")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_setting(self, key_path: str, default=None):
        """Get configuration setting using dot notation (e.g., 'security.password_min_length')"""
        
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == 'production'
    
    def is_testing(self) -> bool:
        """Check if running in test environment"""
        return self.environment == 'test'
    
    def get_db_path(self, db_name: str) -> str:
        """Get database file path for specific database"""
        return self.get_setting(f'db_paths.{db_name}_db_path', f'{db_name}/{db_name}_db.json')
    
    def get_fallback_configuration(self) -> Dict[str, Any]:
        """Fallback configuration for emergency situations"""
        return {
            'environment': 'fallback',
            'debug': False,
            'db_paths': {
                'users_db_path': 'users/users_db.json',
                'debates_db_path': 'debates/debates_db.json',
                'moderation_db_path': 'moderation/moderation_db.json',
                'blockchain_db_path': 'blockchain/blockchain_db.json',
                'validators_db_path': 'blockchain/validators_db.json',
                'contracts_db_path': 'contracts/contracts_db.json'
            },
            'security': {
                'password_min_length': 8,
                'session_timeout_minutes': 15,
                'max_login_attempts': 3,
                'encryption_key_size': 2048
            },
            'p2p': {
                'enabled': False
            },
            'ui': {
                'theme': 'safe_mode',
                'auto_refresh_seconds': 120,
                'notifications_enabled': False
            },
            'logging': {
                'level': 'ERROR',
                'file_logging': True,
                'console_logging': True
            }
        }

# Global configuration instance
CONFIG_MANAGER = ConfigurationManager()
ENV_CONFIG = CONFIG_MANAGER.config
```

## Environment Switching

### Command Line Environment Switching
```bash
# Windows PowerShell
$env:CIVIC_CONFIG="config/dev_config.json"; python main.py

# Windows Command Prompt  
set CIVIC_CONFIG=config/test_config.json && python main.py

# Linux/Mac
export CIVIC_CONFIG="config/dev_config.json" && python main.py
```

### Programmatic Environment Switching
```python
# For testing or development scripts
import os
os.environ['CIVIC_CONFIG'] = 'config/test_config.json'

# Then import main modules
from civic_desktop.main import main
```

## Security Considerations

### Development Environment
- Lower password requirements for ease of testing
- Extended session timeouts for development convenience
- Enhanced logging for debugging
- P2P networking typically disabled

### Production Environment  
- Strict security requirements (12+ character passwords, 2FA options)
- Short session timeouts for security
- Minimal logging to protect privacy
- Full P2P networking enabled
- Automatic backups and data retention

### Test Environment
- Fastest startup and reset capabilities
- Mock external services
- Generate test data automatically
- Reduced security for test convenience

## Usage Patterns

### Module Integration
```python
# Standard pattern for all modules
from civic_desktop.main import ENV_CONFIG

# Get database path
db_path = ENV_CONFIG.get('db_paths', {}).get('users_db_path', 'users/users_db.json')

# Get security setting
min_password_length = ENV_CONFIG.get('security', {}).get('password_min_length', 8)

# Check environment
if ENV_CONFIG.get('environment') == 'development':
    # Development-specific behavior
    enable_debug_features()
```

### Dynamic Configuration Updates
```python
# For runtime configuration changes (rare, use with caution)
def update_configuration_setting(key_path, new_value):
    """Update configuration setting at runtime"""
    # Only allow non-security critical settings
    allowed_runtime_changes = [
        'ui.auto_refresh_seconds',
        'logging.level', 
        'p2p.max_peers'
    ]
    
    if key_path not in allowed_runtime_changes:
        raise ValueError(f"Runtime configuration change not allowed for: {key_path}")
    
    # Update configuration
    CONFIG_MANAGER.set_setting(key_path, new_value)
```

## Testing Configuration

### Automated Tests
- Verify configuration loading for all environments
- Validate security setting enforcement
- Test fallback configuration activation
- Verify database path resolution

### Manual Testing Checklist
- [ ] Development environment loads correctly
- [ ] Test environment resets databases properly  
- [ ] Production environment enforces security requirements
- [ ] Environment switching works without restart
- [ ] Fallback configuration activates on corruption
- [ ] All database paths resolve correctly
- [ ] Security settings are enforced appropriately