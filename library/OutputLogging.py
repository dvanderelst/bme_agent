"""
Output logging module for Mistral AI agent management.
Provides functionality to log console output to markdown files for documentation and debugging.
"""

import atexit
import os
from typing import Optional, Callable, Any
from datetime import datetime


class OutputLogger:
    """
    Singleton class for managing output logging to files.
    
    This class provides a simple way to enable/disable file logging
    and configure where output should be saved.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the logger with default settings."""
        self._enabled = False
        self._log_dir = "logs"
        self._log_file = None
        self._current_file = None
        
    @property
    def enabled(self) -> bool:
        """Check if logging to file is enabled."""
        return self._enabled
    
    @property
    def log_file(self) -> Optional[str]:
        """Get the current log file path."""
        return self._log_file
    
    def enable_logging(self, filename: Optional[str] = None, log_dir: str = "logs") -> str:
        """
        Enable logging to a markdown file.
        
        Args:
            filename: Name of the log file (without extension). 
                     If None, uses timestamp-based name.
            log_dir: Directory to save log files. Default: 'logs'
            
        Returns:
            str: Path to the log file being used
            
        Example:
            >>> OutputLogger().enable_logging("agent_setup")
            >>> # Logs will be saved to logs/agent_setup_2024-02-15.md
        """
        self._log_dir = log_dir
        
        # Create log directory if it doesn't exist
        os.makedirs(self._log_dir, exist_ok=True)
        
        # Generate filename with timestamp if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"output_{timestamp}"
        else:
            # Remove .md extension if provided
            filename = filename.replace('.md', '')
        
        self._log_file = os.path.join(self._log_dir, f"{filename}.md")
        self._enabled = True
        
        # Open the file for writing
        self._current_file = open(self._log_file, 'w', encoding='utf-8')
        atexit.register(self.disable_logging)

        # Write header
        self._write_header()
        
        return self._log_file
    
    def _write_header(self):
        """Write markdown header to the log file."""
        if self._current_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._current_file.write(f"# Mistral AI Agent Management Log\n\n")
            self._current_file.write(f"**Generated:** {timestamp}\n\n")
            self._current_file.write("---\n\n")
            self._current_file.flush()
    
    def disable_logging(self):
        """Disable logging to file."""
        self._enabled = False
        if self._current_file:
            self._current_file.close()
            self._current_file = None
        self._log_file = None
    
    def log(self, content: str):
        """
        Log content to the current log file if logging is enabled.
        Also prints to console for real-time feedback.
        
        Args:
            content: Text content to log (will be written as-is)
        """
        if self._enabled and self._current_file:
            self._current_file.write(content)
            self._current_file.write('\n')  # Add newline
            self._current_file.flush()  # Ensure it's written immediately
        
        # Always print to console for real-time feedback
        print(content)
    
    def log_section(self, title: str, level: int = 2):
        """
        Log a section header.
        
        Args:
            title: Section title
            level: Markdown header level (1-6)
        """
        if self._enabled and self._current_file:
            header = '#' * level + f" {title}\n\n"
            self._current_file.write(header)
            self._current_file.flush()
    
    def log_code_block(self, code: str, language: str = "python"):
        """
        Log a code block with syntax highlighting.
        
        Args:
            code: Code content
            language: Programming language for syntax highlighting
        """
        if self._enabled and self._current_file:
            self._current_file.write(f"```{language}\n")
            self._current_file.write(code)
            self._current_file.write("\n```\n\n")
            self._current_file.flush()


def log_output(func: Callable) -> Callable:
    """
    Decorator to automatically log a function's console output to a markdown file.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function that logs output
        
    Example:
        >>> @log_output
        ... def my_function():
        ...     print("This will be logged to file")
    """
    def wrapper(*args, **kwargs):
        # Get the logger instance
        logger = OutputLogger()
        
        # Only log if logging is enabled
        if logger.enabled:
            # Capture stdout
            import sys
            from io import StringIO
            
            # Save original stdout
            original_stdout = sys.stdout
            
            try:
                # Create a StringIO object to capture output
                captured_output = StringIO()
                sys.stdout = captured_output
                
                # Call the original function
                result = func(*args, **kwargs)
                
                # Restore stdout
                sys.stdout = original_stdout
                
                # Get the captured output
                output = captured_output.getvalue()
                
                # Log it
                if output.strip():
                    logger.log(f"```\n{output.strip()}\n```\n")
                
                return result
                
            except Exception as e:
                # Restore stdout on error
                sys.stdout = original_stdout
                raise e
        else:
            # Logging disabled, just call the function normally
            return func(*args, **kwargs)
    
    return wrapper


def start_logging(filename: Optional[str] = None, log_dir: str = "logs") -> str:
    """
    Convenience function to start logging.
    
    Args:
        filename: Name of the log file
        log_dir: Directory to save logs
        
    Returns:
        str: Path to the log file
    """
    logger = OutputLogger()
    return logger.enable_logging(filename, log_dir)


def stop_logging():
    """Convenience function to stop logging."""
    logger = OutputLogger()
    logger.disable_logging()


def log_to_file(content: str, filename: Optional[str] = None, log_dir: str = "logs"):
    """
    Convenience function to log content directly to a file.
    
    Args:
        content: Content to log
        filename: Name of the log file
        log_dir: Directory to save logs
        
    Returns:
        str: Path to the log file
    """
    logger = OutputLogger()
    if not logger.enabled:
        logger.enable_logging(filename, log_dir)
    logger.log(content)
    return logger.log_file