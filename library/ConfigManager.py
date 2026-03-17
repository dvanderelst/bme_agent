"""
Simple Configuration Manager.
Loads configuration from secrets.toml with environment variable fallback.
"""

import os
import toml
from typing import Dict, Any, Optional


class ConfigManager:
    """Simple configuration manager with TOML and environment variable support."""
    
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
        
        # Load all environment variables that start with relevant prefixes
        for env_var, value in os.environ.items():
            # Include common config variables (remove prefix if present)
            if env_var.startswith(('MISTRAL_', 'BME_', 'MODERATOR_', 'AGENT_')):
                config_key = env_var.lower().replace('_', '')
                config[config_key] = value
            # Also include exact matches for common keys
            elif env_var in ['mistral_key', 'bme_agent', 'moderator_agent']:
                config[env_var] = value
        
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