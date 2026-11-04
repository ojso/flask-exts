"""Symmetric encryption for secrets that must be recoverable in plaintext.

Unlike ``hasher.py`` (one-way, for verifying a value matches without storing
it) this module is for data the application needs to read back as-is --
TOTP secrets being the motivating case: Flask-Login/WTForms-style hashing
can't be used here because the raw secret has to be handed to ``pyotp``
again on every code verification.
"""

import base64
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class DecryptionError(Exception):
    """Raised when ciphertext is malformed, truncated, or fails authentication."""


class AesGcmEncryptor:
    """AES-256-GCM authenticated encryption for short secrets (TOTP seeds,

    API keys, etc.) that must be decryptable later, not just verifiable.

    Each call to :meth:`encrypt` uses a fresh random nonce; the nonce is
    stored alongside the ciphertext (nonce || ciphertext, base64-encoded)
    rather than reused, since AES-GCM nonce reuse breaks both
    confidentiality and authenticity.
    """

    nonce_size = 12  # 96 bits, the size AES-GCM is designed for

    def __init__(self, key: bytes):
        if not isinstance(key, bytes) or len(key) != 32:
            raise ValueError("AesGcmEncryptor key must be 32 raw bytes (AES-256).")
        self._aesgcm = AESGCM(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt ``plaintext``, returning a URL-safe base64 string.

        Args:
            plaintext: The secret to encrypt.

        Returns:
            str: ``nonce || ciphertext`` encoded as URL-safe base64.
        """
        nonce = os.urandom(self.nonce_size)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")

    def decrypt(self, token: str) -> str:
        """Decrypt a token produced by :meth:`encrypt`.

        Args:
            token: The encrypted token.

        Returns:
            str: The original plaintext.

        Raises:
            DecryptionError: If the token is malformed or fails
                authentication (wrong key, corrupted/tampered data).
        """
        try:
            raw = base64.urlsafe_b64decode(token.encode("ascii"))
        except (ValueError, TypeError) as error:
            raise DecryptionError("Malformed ciphertext.") from error

        if len(raw) <= self.nonce_size:
            raise DecryptionError("Ciphertext too short.")

        nonce, ciphertext = raw[: self.nonce_size], raw[self.nonce_size :]
        try:
            plaintext = self._aesgcm.decrypt(nonce, ciphertext, None)
        except InvalidTag as error:
            raise DecryptionError(
                "Ciphertext failed authentication (wrong key or tampered data)."
            ) from error
        return plaintext.decode("utf-8")
