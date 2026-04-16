"""Configuration loader for the Mistral library."""

import os
from shared_lib.lib_config import make_config_loader

get = make_config_loader(os.path.join(os.path.dirname(__file__), "config.toml"), "mistral")
