"""
System Configuration Manager
Manages CCTV-DF Layer settings and monitored directories
"""

import json
import os


class Config:
    """Configuration management for CCTV-DF Layer"""
    
    CONFIG_FILE = "system_config.json"
    
    DEFAULT_CONFIG = {
        "monitored_directory": "",
        "auto_hash_enabled": True,
        "alert_enabled": True,
        "file_extensions": [".mp4", ".avi", ".mkv", ".mov", ".jpg", ".jpeg", ".png"],
        "max_alerts": 1000,
        "system_name": "CCTV-DF Layer v1.0",
        "framework": "NIST SP 800-86"
    }
    
    @classmethod
    def load_config(cls):
        """Load configuration from file"""
        if not os.path.exists(cls.CONFIG_FILE):
            # Create default config
            cls.save_config(cls.DEFAULT_CONFIG)
            return cls.DEFAULT_CONFIG.copy()
        
        try:
            with open(cls.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in cls.DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save_config(cls, config):
        """Save configuration to file"""
        try:
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    @classmethod
    def get(cls, key, default=None):
        """Get a specific configuration value"""
        config = cls.load_config()
        return config.get(key, default)
    
    @classmethod
    def set(cls, key, value):
        """Set a specific configuration value"""
        config = cls.load_config()
        config[key] = value
        return cls.save_config(config)
    
    @classmethod
    def reset_to_defaults(cls):
        """Reset configuration to defaults"""
        return cls.save_config(cls.DEFAULT_CONFIG.copy())
