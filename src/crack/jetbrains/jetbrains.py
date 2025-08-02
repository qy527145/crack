"""JetBrains license generation module."""

import json
import os
from base64 import b64encode, b64decode
from pathlib import Path
from typing import Any, Dict, Optional

from crypto_plus import CryptoPlus

from crack.base import KeyGen, LicenseGenerationError, LicenseParsingError, PatchError
from crack.config import get_config

# Power result template for patching
POWER_RESULT_TEMPLATE = (
    "EQUAL,{arg},65537,860106576952879101192782278876319243486072481962999610484027161162448933268423045647258145695082284265933019120714643752088997312766689988016808929265129401027490891810902278465065056686129972085119605237470899952751915070244375173428976413406363879128531449407795115913715863867259163957682164040613505040314747660800424242248055421184038777878268502955477482203711835548014501087778959157112423823275878824729132393281517778742463067583320091009916141454657614089600126948087954465055321987012989937065785013284988096504657892738536613208311013047138019418152103262155848541574327484510025594166239784429845180875774012229784878903603491426732347994359380330103328705981064044872334790365894924494923595382470094461546336020961505275530597716457288511366082299255537762891238136381924520749228412559219346777184174219999640906007205260040707839706131662149325151230558316068068139406816080119906833578907759960298749494098180107991752250725928647349597506532778539709852254478061194098069801549845163358315116260915270480057699929968468068015735162890213859113563672040630687357054902747438421559817252127187138838514773245413540030800888215961904267348727206110582505606182944023582459006406137831940959195566364811905585377246353->{result}"
)


class JetbrainsKeyGen(KeyGen):
    """JetBrains license key generator.

    This class handles the generation, parsing, and patching of JetBrains
    software licenses including IDEs and plugins.
    """

    def __init__(self) -> None:
        """Initialize the JetBrains key generator.

        Raises:
            LicenseGenerationError: If initialization fails.
        """
        super().__init__()
        self.config = get_config()

        try:
            self._initialize_crypto()
            self._load_certificate()
            self._load_license_data()
        except Exception as e:
            raise LicenseGenerationError(f"Failed to initialize JetBrains key generator: {e}") from e

    def _initialize_crypto(self) -> None:
        """Initialize cryptographic components."""
        module_path = self.config.get_module_path("jetbrains")
        key_path = module_path / self.config.jetbrains_key_file

        try:
            # Try to load existing key
            self.crypto_plus = CryptoPlus.load(str(key_path))
            self.logger.info("Loaded existing RSA key")
        except (FileNotFoundError, Exception):
            # Generate new key if loading fails
            self.logger.info("Generating new RSA key")
            self.crypto_plus = CryptoPlus.generate_rsa()

            # Change to module directory for file operations
            original_cwd = os.getcwd()
            try:
                os.chdir(module_path)
                self.crypto_plus.dump()
                self.crypto_plus.dump_cert(subject_name="Crack", issuer_name="JetProfile CA")
                self.logger.info("Generated and saved new RSA key and certificate")
            finally:
                os.chdir(original_cwd)

    def _load_certificate(self) -> None:
        """Load the certificate for license signing."""
        cert_path = self.config.get_file_path("jetbrains", self.config.jetbrains_cert_file)

        try:
            with open(cert_path, 'r', encoding='utf-8') as f:
                cert_content = f.read()

            # Extract certificate content (remove header and footer)
            cert_lines = cert_content.split('\n')
            self.certificate_text = "".join(cert_lines[1:-2])
            self.certificate = CryptoPlus.loads(self.certificate_text).key
            self.logger.info("Certificate loaded successfully")
        except FileNotFoundError:
            raise LicenseGenerationError(f"Certificate file not found: {cert_path}")
        except Exception as e:
            raise LicenseGenerationError(f"Failed to load certificate: {e}")

    def _load_license_data(self) -> None:
        """Load license template data."""
        try:
            self.license_data = self.config.load_json_config("jetbrains", self.config.jetbrains_license_file)
            self.logger.info("License data loaded successfully")
        except FileNotFoundError:
            raise LicenseGenerationError(
                f"License data file not found: {self.config.jetbrains_license_file}"
            )
        except json.JSONDecodeError as e:
            raise LicenseGenerationError(f"Invalid JSON in license data file: {e}")

    def generate(self, license_id: Optional[str] = None, license_name: Optional[str] = None, **kwargs: Any) -> str:
        """Generate a JetBrains activation code.

        Args:
            license_id: Custom license ID (optional)
            license_name: Custom license name (optional)
            **kwargs: Additional parameters (ignored)

        Returns:
            str: Generated activation code

        Raises:
            LicenseGenerationError: If license generation fails
        """
        try:
            # Prepare license data
            license_data = self.license_data.copy()
            if license_id:
                license_data["licenseId"] = license_id
            if license_name:
                license_data["licenseeName"] = license_name

            # Generate activation code components
            current_license_id = license_data["licenseId"]
            license_info = json.dumps(license_data, separators=(",", ":"))

            # Sign the license information
            signature = self.crypto_plus.sign(license_info.encode(), "SHA1")

            # Construct activation code
            activation_code = (
                f"{current_license_id}-"
                f"{b64encode(license_info.encode()).decode()}-"
                f"{b64encode(signature).decode()}-"
                f"{self.certificate_text}"
            )

            self.logger.info(f"Generated activation code for license ID: {current_license_id}")
            return activation_code

        except Exception as e:
            raise LicenseGenerationError(f"Failed to generate JetBrains license: {e}") from e

    def parse(self, licenses: str) -> Dict[str, Any]:
        """Parse and verify a JetBrains activation code.

        Args:
            licenses: The activation code to parse

        Returns:
            Dict[str, Any]: Parsed license information

        Raises:
            LicenseParsingError: If parsing or verification fails
        """
        try:
            # Split activation code into components
            parts = licenses.split("-")
            if len(parts) != 4:
                raise LicenseParsingError("Invalid activation code format")

            license_id, license_info_b64, signature_b64, cert = parts

            # Decode components
            license_info = b64decode(license_info_b64)
            signature = b64decode(signature_b64)
            certificate = CryptoPlus.loads(cert)

            # Verify signature
            if not certificate.verify(license_info, signature, "SHA1"):
                raise LicenseParsingError("License signature verification failed")

            # Parse license information
            license_info_dict = json.loads(license_info.decode())

            # Verify license ID consistency
            if license_id != license_info_dict["licenseId"]:
                raise LicenseParsingError("License ID mismatch")

            self.logger.info(f"Successfully parsed license for ID: {license_id}")
            return license_info_dict

        except json.JSONDecodeError as e:
            raise LicenseParsingError(f"Invalid JSON in license data: {e}") from e
        except Exception as e:
            if isinstance(e, LicenseParsingError):
                raise
            raise LicenseParsingError(f"Failed to parse JetBrains license: {e}") from e

    def patch(self) -> str:
        """Generate patch information for JetBrains software.

        Returns:
            str: Patch information string

        Raises:
            PatchError: If patch generation fails
        """
        try:
            arg = int.from_bytes(self.certificate.signature, "big")
            result = pow(arg, 65537, self.crypto_plus.public_key.n)
            patch_info = POWER_RESULT_TEMPLATE.format(arg=arg, result=result)

            self.logger.info("Generated patch information")
            return patch_info

        except Exception as e:
            raise PatchError(f"Failed to generate JetBrains patch: {e}") from e


def main() -> None:
    """Main function for command-line usage."""
    try:
        from .plugins import JetBrainPlugin

        # Update plugins and generate licenses
        plugin_manager = JetBrainPlugin()
        plugin_manager.update().make_licenses()

        # Generate and display license
        keygen = JetbrainsKeyGen()
        keygen.run()

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
