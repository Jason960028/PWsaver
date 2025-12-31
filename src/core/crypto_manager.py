import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    @staticmethod
    def generate_salt(size: int = 16) -> bytes:
        """Generates a random salt."""
        return os.urandom(size)

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        Derives a cryptographic key from the given password and salt.
        Returns a URL-safe base64-encoded key suitable for Fernet.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key)

    @staticmethod
    def encrypt_data(data: str, key: bytes) -> bytes:
        """Encrypts data using the provided Fernet key."""
        f = Fernet(key)
        return f.encrypt(data.encode())

    @staticmethod
    def decrypt_data(token: bytes, key: bytes) -> str:
        """Decrypts data using the provided Fernet key."""
        f = Fernet(key)
        return f.decrypt(token).decode()
