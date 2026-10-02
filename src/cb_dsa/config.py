import json
import os
from pathlib import Path
from typing import Dict, Any

CONFIG_FILE_NAME = "dsa-config.json"

DEFAULT_CONFIG = {
    "default_language": ".py",
    "structure": "category",  # flat or category
    "folder_format": "{id}_{name}",
    "file_name_format": "{id}_{name}_soln",
    "doc_name_format": "{id}_{name}_doc"
}

def load_config(base_dir: str) -> Dict[str, Any]:
    config_path = os.path.join(base_dir, CONFIG_FILE_NAME)
    if not os.path.exists(config_path):
        return DEFAULT_CONFIG.copy()
    
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            user_config = json.load(f)
            # Merge with default config to ensure all keys exist
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)
            return config
        except json.JSONDecodeError:
            return DEFAULT_CONFIG.copy()

def save_config(base_dir: str, config: Dict[str, Any]):
    config_path = os.path.join(base_dir, CONFIG_FILE_NAME)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
