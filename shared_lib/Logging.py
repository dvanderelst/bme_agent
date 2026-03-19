"""
Centralized logging module for the Agents project.
Provides consistent logging configuration and utilities.
"""

import logging
import sys
from typing import Optional, Dict, Any


class Logger:
    """Centralized logger with consistent configuration."""
    
    def __init__(self, name: str = "agents"):
        """Initialize logger with consistent configuration.
        
        Args:
            name: Logger name (default: 'agents')
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._configure_logger()
    
    def _configure_logger(self):
        """Configure logger with formatter and handlers."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message.
        
        Args:
            message: Debug message
            extra: Additional context data
        """
        if extra:
            # Remove 'message' key if present to avoid conflict with logging
            extra_copy = extra.copy()
            extra_copy.pop('message', None)
            self.logger.debug(message, extra=extra_copy)
        else:
            self.logger.debug(message)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message.
        
        Args:
            message: Info message
            extra: Additional context data
        """
        if extra:
            self.logger.info(message, extra=extra)
        else:
            self.logger.info(message)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message.
        
        Args:
            message: Warning message
            extra: Additional context data
        """
        if extra:
            self.logger.warning(message, extra=extra)
        else:
            self.logger.warning(message)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message.
        
        Args:
            message: Error message
            extra: Additional context data
        """
        if extra:
            self.logger.error(message, extra=extra)
        else:
            self.logger.error(message)
    
    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log exception with traceback.
        
        Args:
            message: Exception message
            extra: Additional context data
        """
        if extra:
            # Remove 'message' key if present to avoid conflict with logging
            extra_copy = extra.copy()
            extra_copy.pop('message', None)
            self.logger.exception(message, extra=extra_copy)
        else:
            self.logger.exception(message)


# Global logger instance
def get_logger(name: str = "agents") -> Logger:
    """Get logger instance.
    
    Args:
        name: Logger name (default: 'agents')
        
    Returns:
        Configured Logger instance
    """
    return Logger(name)


# Convenience functions for backward compatibility
def log_debug(message: str, context: Optional[Dict[str, Any]] = None):
    """Convenience function for debug logging."""
    get_logger().debug(message, extra=context)


def log_info(message: str, context: Optional[Dict[str, Any]] = None):
    """Convenience function for info logging."""
    get_logger().info(message, extra=context)


def log_warning(message: str, context: Optional[Dict[str, Any]] = None):
    """Convenience function for warning logging."""
    get_logger().warning(message, extra=context)


def log_error(message: str, context: Optional[Dict[str, Any]] = None):
    """Convenience function for error logging."""
    get_logger().error(message, extra=context)


def log_exception(message: str, context: Optional[Dict[str, Any]] = None):
    """Convenience function for exception logging."""
    get_logger().exception(message, extra=context)