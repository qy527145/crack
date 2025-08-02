"""Tests for the config module."""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from crack.config import CrackConfig, get_config, update_config


class TestCrackConfig:
    """Test cases for CrackConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = CrackConfig()
        
        assert config.expire_date == "9999-12-31"
        assert config.server_host == "0.0.0.0"
        assert config.server_port == 5000
        assert config.server_uid == "crack"
        assert config.log_level == "INFO"
    
    def test_environment_override(self):
        """Test environment variable override."""
        env_vars = {
            "EXPIRE_DATE": "2025-12-31",
            "SERVER_HOST": "127.0.0.1",
            "SERVER_PORT": "8080",
            "SERVER_UID": "test-server",
            "LOG_LEVEL": "DEBUG",
        }
        
        with patch.dict(os.environ, env_vars):
            config = CrackConfig()
            
            assert config.expire_date == "2025-12-31"
            assert config.server_host == "127.0.0.1"
            assert config.server_port == 8080
            assert config.server_uid == "test-server"
            assert config.log_level == "DEBUG"
    
    def test_get_module_path(self):
        """Test module path generation."""
        config = CrackConfig()
        module_path = config.get_module_path("jetbrains")
        
        assert isinstance(module_path, Path)
        assert module_path.name == "jetbrains"
    
    def test_get_file_path(self):
        """Test file path generation."""
        config = CrackConfig()
        file_path = config.get_file_path("jetbrains", "test.json")
        
        assert isinstance(file_path, Path)
        assert file_path.name == "test.json"
        assert file_path.parent.name == "jetbrains"
    
    def test_file_exists(self):
        """Test file existence check."""
        config = CrackConfig()
        
        # Test with non-existent file
        assert not config.file_exists("test", "nonexistent.json")
    
    def test_json_config_operations(self):
        """Test JSON configuration save and load."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CrackConfig()
            config.base_path = Path(temp_dir)
            
            test_data = {"test": "value", "number": 42}
            
            # Test save
            config.save_json_config("test_module", "test.json", test_data)
            
            # Test file exists
            assert config.file_exists("test_module", "test.json")
            
            # Test load
            loaded_data = config.load_json_config("test_module", "test.json")
            assert loaded_data == test_data
    
    def test_load_nonexistent_json(self):
        """Test loading non-existent JSON file."""
        config = CrackConfig()
        
        with pytest.raises(FileNotFoundError):
            config.load_json_config("test", "nonexistent.json")
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CrackConfig()
            config.base_path = Path(temp_dir)
            
            # Create invalid JSON file
            invalid_json_path = config.get_file_path("test", "invalid.json")
            invalid_json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(invalid_json_path, 'w') as f:
                f.write("invalid json content")
            
            with pytest.raises(json.JSONDecodeError):
                config.load_json_config("test", "invalid.json")


class TestGlobalConfig:
    """Test cases for global configuration functions."""
    
    def test_get_config(self):
        """Test getting global configuration."""
        config = get_config()
        assert isinstance(config, CrackConfig)
    
    def test_update_config(self):
        """Test updating global configuration."""
        original_port = get_config().server_port
        
        try:
            update_config(server_port=9999)
            assert get_config().server_port == 9999
        finally:
            # Restore original value
            update_config(server_port=original_port)
    
    def test_update_invalid_config(self):
        """Test updating with invalid configuration key."""
        with pytest.raises(ValueError, match="Unknown configuration parameter"):
            update_config(invalid_key="value")
