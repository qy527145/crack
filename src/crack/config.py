"""Configuration management for the crack project."""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class CrackConfig:
    """Global configuration for crack tools."""
    
    # Default expiration date for licenses
    expire_date: str = "9999-12-31"
    
    # Server configuration
    server_host: str = "0.0.0.0"
    server_port: int = 5000
    server_uid: str = "crack"
    
    # Paths configuration
    base_path: Path = field(default_factory=lambda: Path(__file__).parent)
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # JetBrains specific configuration
    jetbrains_license_file: str = "licenses.json"
    jetbrains_license_base_file: str = "licenses_base.json"
    jetbrains_plugins_file: str = "plugins.json"
    jetbrains_cert_file: str = "cert.crt"
    jetbrains_key_file: str = "key.pem"
    jetbrains_pub_key_file: str = "key_pub.pem"
    
    # DBeaver specific configuration
    dbeaver_public_key_file: str = "dbeaver-ue-public.key"
    dbeaver_ee_public_key_file: str = "dbeaver-ee-public.key"
    
    # Typora specific configuration
    typora_install_path: str = r"D:\Program Files\Typora\resources"
    
    def __post_init__(self) -> None:
        """Post-initialization to handle environment variables."""
        # Override with environment variables if they exist
        self.expire_date = os.environ.get("EXPIRE_DATE", self.expire_date)
        self.server_host = os.environ.get("SERVER_HOST", self.server_host)
        self.server_port = int(os.environ.get("SERVER_PORT", str(self.server_port)))
        self.server_uid = os.environ.get("SERVER_UID", self.server_uid)
        self.log_level = os.environ.get("LOG_LEVEL", self.log_level)
        
        # Handle Typora path from environment
        typora_path = os.environ.get("TYPORA_PATH")
        if typora_path:
            self.typora_install_path = typora_path
    
    def get_module_path(self, module_name: str) -> Path:
        """Get the path for a specific module.
        
        Args:
            module_name: Name of the module (e.g., 'jetbrains', 'dbeaver')
            
        Returns:
            Path: Path to the module directory
        """
        return self.base_path / module_name
    
    def get_file_path(self, module_name: str, filename: str) -> Path:
        """Get the full path for a file in a specific module.
        
        Args:
            module_name: Name of the module
            filename: Name of the file
            
        Returns:
            Path: Full path to the file
        """
        return self.get_module_path(module_name) / filename
    
    def load_json_config(self, module_name: str, filename: str) -> Dict[str, Any]:
        """Load JSON configuration from a module.
        
        Args:
            module_name: Name of the module
            filename: Name of the JSON file
            
        Returns:
            Dict[str, Any]: Loaded JSON data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        file_path = self.get_file_path(module_name, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_json_config(self, module_name: str, filename: str, data: Dict[str, Any]) -> None:
        """Save JSON configuration to a module.
        
        Args:
            module_name: Name of the module
            filename: Name of the JSON file
            data: Data to save
        """
        file_path = self.get_file_path(module_name, filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def file_exists(self, module_name: str, filename: str) -> bool:
        """Check if a file exists in a module.
        
        Args:
            module_name: Name of the module
            filename: Name of the file
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return self.get_file_path(module_name, filename).exists()


# Global configuration instance
config = CrackConfig()


def get_config() -> CrackConfig:
    """Get the global configuration instance.
    
    Returns:
        CrackConfig: The global configuration instance
    """
    return config


def update_config(**kwargs: Any) -> None:
    """Update the global configuration.
    
    Args:
        **kwargs: Configuration parameters to update
    """
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration parameter: {key}")
