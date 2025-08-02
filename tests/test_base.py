"""Tests for the base module."""

import pytest
from unittest.mock import Mock, patch

from crack.base import KeyGen, CrackError, LicenseGenerationError, LicenseParsingError, PatchError


class MockKeyGen(KeyGen):
    """Mock implementation of KeyGen for testing."""
    
    def __init__(self, should_fail: str = None):
        super().__init__()
        self.should_fail = should_fail
    
    def generate(self, **kwargs):
        if self.should_fail == "generate":
            raise LicenseGenerationError("Mock generation error")
        return "mock-license-12345"
    
    def parse(self, licenses: str):
        if self.should_fail == "parse":
            raise LicenseParsingError("Mock parsing error")
        return {"license_id": "12345", "data": "mock"}
    
    def patch(self):
        if self.should_fail == "patch":
            raise PatchError("Mock patch error")
        return "mock-patch-info"


class TestKeyGen:
    """Test cases for the KeyGen base class."""
    
    def test_successful_run(self, capsys):
        """Test successful license generation process."""
        keygen = MockKeyGen()
        keygen.run()
        
        captured = capsys.readouterr()
        assert "Generated License:" in captured.out
        assert "mock-license-12345" in captured.out
        assert "Patch Information:" in captured.out
        assert "mock-patch-info" in captured.out
        assert "Parsed License Information:" in captured.out
    
    def test_run_without_patch(self, capsys):
        """Test license generation without patch."""
        keygen = MockKeyGen()
        keygen.run(patch=False)
        
        captured = capsys.readouterr()
        assert "Generated License:" in captured.out
        assert "Patch Information:" not in captured.out
        assert "Parsed License Information:" in captured.out
    
    def test_generation_failure(self):
        """Test handling of generation failure."""
        keygen = MockKeyGen(should_fail="generate")
        
        with pytest.raises(LicenseGenerationError):
            keygen.run()
    
    def test_parsing_failure(self):
        """Test handling of parsing failure."""
        keygen = MockKeyGen(should_fail="parse")
        
        with pytest.raises(LicenseParsingError):
            keygen.run()
    
    def test_patch_failure(self, capsys):
        """Test handling of patch failure."""
        keygen = MockKeyGen(should_fail="patch")
        keygen.run()
        
        captured = capsys.readouterr()
        assert "Warning: Patch generation failed" in captured.out
        assert "Parsed License Information:" in captured.out
    
    def test_abstract_methods(self):
        """Test that abstract methods must be implemented."""
        with pytest.raises(TypeError):
            KeyGen()


class TestExceptions:
    """Test cases for custom exceptions."""
    
    def test_crack_error_inheritance(self):
        """Test that all custom exceptions inherit from CrackError."""
        assert issubclass(LicenseGenerationError, CrackError)
        assert issubclass(LicenseParsingError, CrackError)
        assert issubclass(PatchError, CrackError)
    
    def test_exception_messages(self):
        """Test exception message handling."""
        msg = "Test error message"
        
        error = CrackError(msg)
        assert str(error) == msg
        
        error = LicenseGenerationError(msg)
        assert str(error) == msg
        
        error = LicenseParsingError(msg)
        assert str(error) == msg
        
        error = PatchError(msg)
        assert str(error) == msg
