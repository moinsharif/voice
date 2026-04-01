"""Encryption utilities for data at rest using AES-256-CBC and PBKDF2."""

import os
import json
from typing import Optional, Union
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class EncryptionManager:
    """Manages AES-256-CBC encryption/decryption with PBKDF2 key derivation.
    
    Features:
    - AES-256-CBC encryption for data at rest
    - PBKDF2 key derivation from passwords
    - Secure IV generation and storage
    - Support for bytes and string data
    """

    # Constants
    ALGORITHM = algorithms.AES
    CIPHER_MODE = modes.CBC
    KEY_SIZE = 32  # 256 bits for AES-256
    IV_SIZE = 16  # 128 bits for CBC mode
    PBKDF2_ITERATIONS = 100000
    PBKDF2_HASH_ALGORITHM = hashes.SHA256()
    SALT_SIZE = 16  # 128 bits

    def __init__(self, password: Optional[str] = None, salt: Optional[bytes] = None):
        """Initialize EncryptionManager.
        
        Args:
            password: Password for key derivation. If None, generates a random key.
            salt: Salt for PBKDF2. If None, generates a random salt.
        """
        self.backend = default_backend()
        
        if password is not None:
            if salt is None:
                self.salt = os.urandom(self.SALT_SIZE)
            else:
                self.salt = salt
            self.key = self._derive_key(password, self.salt)
        else:
            # Generate random key if no password provided
            self.key = os.urandom(self.KEY_SIZE)
            self.salt = None

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation
            
        Returns:
            Derived encryption key (32 bytes for AES-256)
        """
        kdf = PBKDF2HMAC(
            algorithm=self.PBKDF2_HASH_ALGORITHM,
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
            backend=self.backend,
        )
        return kdf.derive(password.encode())

    def encrypt(self, data: Union[bytes, str]) -> bytes:
        """Encrypt data using AES-256-CBC.
        
        Args:
            data: Data to encrypt (bytes or string)
            
        Returns:
            Encrypted data with IV prepended (IV + ciphertext)
        """
        if isinstance(data, str):
            data = data.encode()

        # Generate random IV
        iv = os.urandom(self.IV_SIZE)

        # Create cipher
        cipher = Cipher(
            self.ALGORITHM(self.key),
            self.CIPHER_MODE(iv),
            backend=self.backend,
        )
        encryptor = cipher.encryptor()

        # Encrypt data with PKCS7 padding
        ciphertext = encryptor.update(self._pad(data)) + encryptor.finalize()

        # Return IV + ciphertext
        return iv + ciphertext

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data encrypted with AES-256-CBC.
        
        Args:
            encrypted_data: Encrypted data with IV prepended
            
        Returns:
            Decrypted data (bytes)
        """
        # Extract IV and ciphertext
        iv = encrypted_data[:self.IV_SIZE]
        ciphertext = encrypted_data[self.IV_SIZE:]

        # Create cipher
        cipher = Cipher(
            self.ALGORITHM(self.key),
            self.CIPHER_MODE(iv),
            backend=self.backend,
        )
        decryptor = cipher.decryptor()

        # Decrypt data
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove PKCS7 padding
        return self._unpad(padded_data)

    def encrypt_string(self, data: str) -> str:
        """Encrypt string and return as hex string.
        
        Args:
            data: String to encrypt
            
        Returns:
            Encrypted data as hex string
        """
        encrypted = self.encrypt(data)
        return encrypted.hex()

    def decrypt_string(self, encrypted_hex: str) -> str:
        """Decrypt hex string and return as string.
        
        Args:
            encrypted_hex: Encrypted data as hex string
            
        Returns:
            Decrypted string
        """
        encrypted_data = bytes.fromhex(encrypted_hex)
        decrypted = self.decrypt(encrypted_data)
        return decrypted.decode()

    def encrypt_json(self, data: dict) -> str:
        """Encrypt JSON data and return as hex string.
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Encrypted JSON as hex string
        """
        json_str = json.dumps(data)
        return self.encrypt_string(json_str)

    def decrypt_json(self, encrypted_hex: str) -> dict:
        """Decrypt hex string and return as JSON dictionary.
        
        Args:
            encrypted_hex: Encrypted JSON as hex string
            
        Returns:
            Decrypted dictionary
        """
        decrypted_str = self.decrypt_string(encrypted_hex)
        return json.loads(decrypted_str)

    def get_salt(self) -> Optional[bytes]:
        """Get the salt used for key derivation.
        
        Returns:
            Salt bytes or None if key was randomly generated
        """
        return self.salt

    @staticmethod
    def _pad(data: bytes) -> bytes:
        """Apply PKCS7 padding to data.
        
        Args:
            data: Data to pad
            
        Returns:
            Padded data
        """
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length] * padding_length)
        return data + padding

    @staticmethod
    def _unpad(data: bytes) -> bytes:
        """Remove PKCS7 padding from data.
        
        Args:
            data: Padded data
            
        Returns:
            Unpadded data
        """
        padding_length = data[-1]
        return data[:-padding_length]
