"""Shared TOML config loader for library-specific config files."""

import os
import toml
from typing import Any, Optional


def make_config_loader(config_path: str, section: str):
    """Return a get() function backed by one section of a TOML file."""
    data = toml.load(config_path).get(section, {})

    def get(key: str, default: Optional[Any] = None) -> Any:
        return data.get(key, default)

    return get
