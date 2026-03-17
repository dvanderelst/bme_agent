"""
Configuration Manager for Mistral AI Agents.
Handles loading configuration from secrets.toml with environment variable fallback.
"""

import os
import toml
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages application configuration with TOML and environment variable support."""
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from secrets.toml with environment variable fallback."""
        config = {}
        
        # Try to load from .streamlit/secrets.toml
        secrets_path = ".streamlit/secrets.toml"
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, "r") as f:
                    config.update(toml.load(f))
            except Exception as e:
                print(f"Warning: Could not load secrets.toml: {e}")
        
        # Fallback to environment variables
        env_mapping = {
            "MISTRAL_KEY": "mistral_key",
            "ZOTERO_AGENT": "zotero_agent",
            "ZOTERO_AGENT_LIBRARY": "zotero_agent_library",
            "BME_AGENT": "bme_agent",
            "BME_AGENT_LIBRARY": "bme_agent_library",
            "ZOTERO_API_KEY": "zotero_api_key",
            "ZOTERO_USER_ID": "zotero_user_id"
        }
        
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                config[config_key] = os.environ[env_var]
        
        # Add environment variables for new config values
        extra_env_mapping = {
            "TEACHER_AGENT": "teacher_agent",
            "TEACHER_AGENT_LIBRARY": "teacher_agent_library",
            "LIBRARY_ID": "library_id",
            "ROBOTICS_AGENT": "robotics_agent",
            "ROBOTICS_LIBRARY": "robotics_library"
        }
        
        for env_var, config_key in extra_env_mapping.items():
            if env_var in os.environ:
                config[config_key] = os.environ[env_var]
        
        return config
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a configuration value by key."""
        return self._config.get(key, default)
    
    def __getattr__(self, name: str) -> Any:
        """Allow attribute-style access to config values."""
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")


# Global configuration instance
config = ConfigManager()

# Convenience functions for backward compatibility
def get_mistral_key() -> str:
    """Get Mistral API key from configuration."""
    return config.get("mistral_key")

def get_zotero_agent() -> str:
    """Get Zotero agent ID from configuration."""
    return config.get("zotero_agent")

def get_zotero_agent_library() -> str:
    """Get Zotero agent library ID from configuration."""
    return config.get("zotero_agent_library")

def get_bme_agent() -> str:
    """Get BME agent ID from configuration."""
    return config.get("bme_agent")

def get_bme_agent_library() -> str:
    """Get BME agent library ID from configuration."""
    return config.get("bme_agent_library")

def get_zotero_api_key() -> str:
    """Get Zotero API key from configuration."""
    return config.get("zotero_api_key")

def get_zotero_user_id() -> str:
    """Get Zotero user ID from configuration."""
    return config.get("zotero_user_id")

def get_teacher_agent() -> str:
    """Get teacher agent ID from configuration."""
    return config.get("teacher_agent")

def get_teacher_agent_library() -> str:
    """Get teacher agent library ID from configuration."""
    return config.get("teacher_agent_library")

def get_library_id() -> str:
    """Get default library ID from configuration."""
    return config.get("library_id")

def get_robotics_agent() -> str:
    """Get robotics agent ID from configuration."""
    return config.get("robotics_agent")

def get_robotics_library() -> str:
    """Get robotics library ID from configuration."""
    return config.get("robotics_library")