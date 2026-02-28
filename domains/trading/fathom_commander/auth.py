"""
Fathom Authentication Manager
Secure credential handling for Kraken API access.
"""

import base64
import hashlib
import hmac
import os
import time
import urllib.parse
from typing import Optional


class CredentialManager:
    """
    Manages Kraken API credentials with security hardening.

    Security features:
    - Credentials loaded from environment (never hardcoded)
    - HMAC-SHA512 signing for private endpoints
    - Nonce generation for replay protection
    - No credential logging
    """

    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize credential manager.

        Args:
            api_key: Kraken API key (if None, loads from FATHOM_KRAKEN_API_KEY env)
            secret_key: Kraken secret key (if None, loads from FATHOM_KRAKEN_SECRET_KEY env)
        """
        self.api_key = api_key or os.getenv("FATHOM_KRAKEN_API_KEY") or os.getenv("KRAKEN_API_KEY")
        self.secret_key = secret_key or os.getenv("FATHOM_KRAKEN_SECRET_KEY") or os.getenv("KRAKEN_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise ValueError(
                "Kraken credentials not found. Set FATHOM_KRAKEN_API_KEY and "
                "FATHOM_KRAKEN_SECRET_KEY environment variables."
            )

    def generate_nonce(self) -> int:
        """
        Generate nonce for API request.

        Kraken requires strictly increasing nonces (millisecond precision).
        """
        return int(time.time() * 1000)

    def sign_request(self, url_path: str, data: dict) -> str:
        """
        Generate HMAC-SHA512 signature for Kraken private endpoint.

        Kraken signature algorithm:
        1. Concatenate nonce + POST data
        2. SHA256 hash the result
        3. Concatenate url_path + hash
        4. HMAC-SHA512 with base64-decoded secret
        5. Base64 encode the result

        Args:
            url_path: API endpoint path (e.g., "/0/private/Balance")
            data: POST data dictionary (must include 'nonce')

        Returns:
            Base64-encoded signature
        """
        # Encode POST data
        post_data = urllib.parse.urlencode(data)

        # SHA256(nonce + POST data)
        encoded = (str(data['nonce']) + post_data).encode()
        message = url_path.encode() + hashlib.sha256(encoded).digest()

        # HMAC-SHA512 with secret
        secret = base64.b64decode(self.secret_key)
        signature = hmac.new(secret, message, hashlib.sha512)

        return base64.b64encode(signature.digest()).decode()

    def get_headers(self, url_path: str, data: dict) -> dict:
        """
        Generate authentication headers for Kraken private endpoint.

        Args:
            url_path: API endpoint path
            data: POST data (nonce will be added if not present)

        Returns:
            Dict with API-Key and API-Sign headers
        """
        # Ensure nonce is present
        if 'nonce' not in data:
            data['nonce'] = self.generate_nonce()

        signature = self.sign_request(url_path, data)

        return {
            "API-Key": self.api_key,
            "API-Sign": signature
        }

    def validate_credentials(self) -> bool:
        """
        Check if credentials are present (not empty).

        Returns:
            True if both API key and secret are non-empty
        """
        return bool(self.api_key and self.secret_key)
