"""
Simple Configuration Manager.
Loads configuration from secrets.toml with environment variable fallback.
"""

import logging
import os
import toml
from typing import Dict, Any, Optional


class ConfigManager:
    """Simple configuration manager with TOML and environment variable support."""
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from secrets.toml with environment variable fallback.
        All keys are normalized to lowercase so callers can use either case."""
        config = {}

        # Try to load from .streamlit/secrets.toml
        secrets_path = ".streamlit/secrets.toml"
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, "r") as f:
                    config.update({k.lower(): v for k, v in toml.load(f).items()})
            except Exception as e:
                logging.warning("Could not load secrets.toml: %s", e)

        # Load environment variables, normalizing keys to lowercase
        for env_var, value in os.environ.items():
            config[env_var.lower()] = value

        return config

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a configuration value by key (case-insensitive)."""
        return self._config.get(key.lower(), default)
    
    def __getattr__(self, name: str) -> Any:
        """Allow attribute-style access to config values."""
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")


# Global configuration instance
config = ConfigManager()