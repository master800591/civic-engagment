"""
Centralized logging configuration for the Civic Engagement Platform
Provides structured logging with proper log levels and file output
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

# Default log levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class CivicLogger:
    """Centralized logger for the civic engagement platform"""
    
    _instance: Optional['CivicLogger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            CivicLogger._initialized = True
    
    def _setup_logging(self):
        """Initialize logging configuration"""
        # Create logs directory
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Get log level from environment or config
        log_level = os.environ.get('CIVIC_LOG_LEVEL', 'INFO').upper()
        log_level = LOG_LEVELS.get(log_level, logging.INFO)
        
        # Create root logger
        self.logger = logging.getLogger('civic_platform')
        self.logger.setLevel(log_level)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler for all logs
        log_file = os.path.join(log_dir, 'civic_platform.log')
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Error file handler for errors only
        error_file = os.path.join(log_dir, 'civic_platform_errors.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_file, maxBytes=5*1024*1024, backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        
        # Only add console handler in development
        if os.environ.get('CIVIC_ENV', 'development') == 'development':
            self.logger.addHandler(console_handler)
        
        # Log initialization
        self.logger.info("Civic Platform logging system initialized")
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """Get a logger instance for a specific module"""
        if name:
            return logging.getLogger(f'civic_platform.{name}')
        return self.logger

# Convenience function for getting loggers
def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance for the civic platform"""
    civic_logger = CivicLogger()
    return civic_logger.get_logger(name)

# Module-specific loggers
def get_user_logger() -> logging.Logger:
    """Get logger for user-related operations"""
    return get_logger('users')

def get_debate_logger() -> logging.Logger:
    """Get logger for debate-related operations"""
    return get_logger('debates')

def get_blockchain_logger() -> logging.Logger:
    """Get logger for blockchain operations"""
    return get_logger('blockchain')

def get_moderation_logger() -> logging.Logger:
    """Get logger for moderation operations"""
    return get_logger('moderation')

def get_security_logger() -> logging.Logger:
    """Get logger for security events"""
    return get_logger('security')