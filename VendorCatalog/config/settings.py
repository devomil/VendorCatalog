"""
Configuration settings for the Vendor Catalog application.
"""

import os
import json

# Application name
APP_NAME = "VendorCatalog"

# Database path
DATABASE_PATH = os.path.join(os.path.expanduser("~"), f".{APP_NAME}", "database.db")

# Log path
LOG_PATH = os.path.join(os.path.expanduser("~"), f".{APP_NAME}", "logs")

# Config path
CONFIG_PATH = os.path.join(os.path.expanduser("~"), f".{APP_NAME}", "config.json")

# Default configuration
DEFAULT_CONFIG = {
    "theme": "default",
    "debug_mode": False,
    "auto_backup": True,
    "backup_interval_days": 7,
    "max_backups": 5,
    "ui": {
        "font_size": 10,
        "window_width": 1024,
        "window_height": 768
    },
    "database": {
        "type": "sqlite",  # Options: sqlite, postgresql
        "host": "localhost",
        "port": 5432,
        "name": "vendor_catalog",
        "user": "postgres",
        "password": ""
    }
}

# Current configuration
config = {}

def initialize_settings():
    """Initialize application settings"""
    # Create application directories if they don't exist
    app_dir = os.path.dirname(DATABASE_PATH)
    log_dir = LOG_PATH
    
    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    
    # Load configuration
    global config
    config = load_config()

def load_config():
    """Load configuration from file"""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                user_config = json.load(f)
                
            # Merge with default config to ensure all keys exist
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)
            return config
        else:
            # Save default config
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG

def save_config(config_data):
    """Save configuration to file"""
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_setting(key, default=None):
    """Get a setting value"""
    keys = key.split('.')
    value = config
    
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default

def set_setting(key, value):
    """Set a setting value"""
    keys = key.split('.')
    current = config
    
    # Navigate to the correct level
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    # Set the value
    current[keys[-1]] = value
    
    # Save the updated config
    save_config(config)
    return True