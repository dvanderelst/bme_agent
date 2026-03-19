"""
Configuration loader for the Anthropic library.
Reads anthropic_lib/config.toml.
"""

import os
import toml
from typing import Any, Optional

_config_path = os.path.join(os.path.dirname(__file__), "config.toml")
_data = toml.load(_config_path).get("anthropic", {})


def get(key: str, default: Optional[Any] = None) -> Any:
    """Get a configuration value by key."""
    return _data.get(key, default)
