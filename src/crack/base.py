"""Base classes and interfaces for license generation tools."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CrackError(Exception):
    """Base exception for all crack-related errors."""
    pass


class LicenseGenerationError(CrackError):
    """Raised when license generation fails."""
    pass


class LicenseParsingError(CrackError):
    """Raised when license parsing fails."""
    pass


class PatchError(CrackError):
    """Raised when patching fails."""
    pass


class KeyGen(ABC):
    """Abstract base class for all license generators.

    This class defines the interface that all license generation tools
    must implement. It provides a common structure for generating,
    parsing, and patching licenses.
    """

    def __init__(self) -> None:
        """Initialize the key generator."""
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def generate(self, **kwargs: Any) -> str:
        """Generate a license string.

        Args:
            **kwargs: Additional parameters for license generation.

        Returns:
            str: The generated license string.

        Raises:
            LicenseGenerationError: If license generation fails.
        """
        pass

    @abstractmethod
    def parse(self, licenses: str) -> Union[Dict[str, Any], str, bytes]:
        """Parse a license string and return the decoded information.

        Args:
            licenses: The license string to parse.

        Returns:
            Union[Dict[str, Any], str, bytes]: The parsed license information.

        Raises:
            LicenseParsingError: If license parsing fails.
        """
        pass

    @abstractmethod
    def patch(self) -> str:
        """Generate patch information for the software.

        Returns:
            str: Patch information or empty string if no patch is needed.

        Raises:
            PatchError: If patch generation fails.
        """
        return ""

    def run(self, patch: bool = True, **kwargs: Any) -> None:
        """Run the complete license generation process.

        This method orchestrates the entire process: generates a license,
        optionally creates patch information, and parses the license to
        verify its validity.

        Args:
            patch: Whether to generate patch information.
            **kwargs: Additional parameters passed to generate().

        Raises:
            CrackError: If any step in the process fails.
        """
        try:
            self.logger.info("Starting license generation process")

            # Generate license
            ciphertext_licenses = self.generate(**kwargs)
            self.logger.info("License generated successfully")
            print(f"Generated License:\n{ciphertext_licenses}\n")

            # Generate patch if requested
            if patch:
                try:
                    patch_info = self.patch()
                    if patch_info:
                        self.logger.info("Patch information generated")
                        print(f"Patch Information:\n{patch_info}\n")
                    else:
                        self.logger.info("No patch information needed")
                except PatchError as e:
                    self.logger.warning(f"Patch generation failed: {e}")
                    print(f"Warning: Patch generation failed: {e}\n")

            # Parse and verify license
            try:
                plaintext_licenses = self.parse(ciphertext_licenses)
                self.logger.info("License parsed and verified successfully")
                print(f"Parsed License Information:\n{plaintext_licenses}")
            except LicenseParsingError as e:
                self.logger.error(f"License parsing failed: {e}")
                print(f"Error: License parsing failed: {e}")
                raise

        except Exception as e:
            self.logger.error(f"License generation process failed: {e}")
            if not isinstance(e, CrackError):
                raise CrackError(f"Unexpected error during license generation: {e}") from e
            raise
