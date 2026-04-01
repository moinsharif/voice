"""Tests for encryption utilities."""

import pytest
import json
from src.utils.encryption import EncryptionManager


class TestEncryptionManagerBasic:
    """Test basic encryption/decryption functionality."""

    def test_encrypt_decrypt_bytes(self):
        """Test encrypting and decrypting bytes."""
        manager = EncryptionManager()
        original = b"Hello, World!"
        
        encrypted = manager.encrypt(original)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == original
        assert encrypted != original

    def test_encrypt_decrypt_string(self):
        """Test encrypting and decrypting strings."""
        manager = EncryptionManager()
        original = "Hello, World!"
        
        encrypted = manager.encrypt(original)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == original.encode()

    def test_encrypt_string_method(self):
        """Test encrypt_string and decrypt_string methods."""
        manager = EncryptionManager()
        original = "Test string"
        
        encrypted_hex = manager.encrypt_string(original)
        decrypted = manager.decrypt_string(encrypted_hex)
        
        assert decrypted == original
        assert isinstance(encrypted_hex, str)

    def test_encrypt_json(self):
        """Test encrypting and decrypting JSON data."""
        manager = EncryptionManager()
        original_data = {"name": "Alice", "age": 30, "active": True}
        
        encrypted_hex = manager.encrypt_json(original_data)
        decrypted_data = manager.decrypt_json(encrypted_hex)
        
        assert decrypted_data == original_data

    def test_different_encryptions_produce_different_ciphertexts(self):
        """Test that same plaintext produces different ciphertexts (due to random IV)."""
        manager = EncryptionManager()
        plaintext = b"Same message"
        
        encrypted1 = manager.encrypt(plaintext)
        encrypted2 = manager.encrypt(plaintext)
        
        # Different ciphertexts due to random IV
        assert encrypted1 != encrypted2
        # But both decrypt to same plaintext
        assert manager.decrypt(encrypted1) == plaintext
        assert manager.decrypt(encrypted2) == plaintext


class TestPBKDF2KeyDerivation:
    """Test PBKDF2 key derivation."""

    def test_same_password_same_salt_produces_same_key(self):
        """Test that same password and salt produce same key."""
        password = "test_password"
        salt = b"fixed_salt_16byt"  # 16 bytes
        
        manager1 = EncryptionManager(password=password, salt=salt)
        manager2 = EncryptionManager(password=password, salt=salt)
        
        assert manager1.key == manager2.key

    def test_different_passwords_produce_different_keys(self):
        """Test that different passwords produce different keys."""
        salt = b"fixed_salt_16byt"
        
        manager1 = EncryptionManager(password="password1", salt=salt)
        manager2 = EncryptionManager(password="password2", salt=salt)
        
        assert manager1.key != manager2.key

    def test_different_salts_produce_different_keys(self):
        """Test that different salts produce different keys."""
        password = "test_password"
        
        manager1 = EncryptionManager(password=password, salt=b"salt_one_16bytes")
        manager2 = EncryptionManager(password=password, salt=b"salt_two_16bytes")
        
        assert manager1.key != manager2.key

    def test_password_based_encryption_decryption(self):
        """Test encryption/decryption with password-derived key."""
        password = "my_secure_password"
        salt = b"fixed_salt_16byt"
        plaintext = b"Secret message"
        
        # Encrypt with password
        manager1 = EncryptionManager(password=password, salt=salt)
        encrypted = manager1.encrypt(plaintext)
        
        # Decrypt with same password and salt
        manager2 = EncryptionManager(password=password, salt=salt)
        decrypted = manager2.decrypt(encrypted)
        
        assert decrypted == plaintext

    def test_wrong_password_fails_decryption(self):
        """Test that wrong password produces garbage output."""
        password = "correct_password"
        wrong_password = "wrong_password"
        salt = b"fixed_salt_16byt"
        plaintext = b"Secret message"
        
        # Encrypt with correct password
        manager1 = EncryptionManager(password=password, salt=salt)
        encrypted = manager1.encrypt(plaintext)
        
        # Try to decrypt with wrong password
        manager2 = EncryptionManager(password=wrong_password, salt=salt)
        decrypted = manager2.decrypt(encrypted)
        
        # Decryption with wrong password produces garbage
        assert decrypted != plaintext

    def test_get_salt(self):
        """Test retrieving salt from manager."""
        password = "test_password"
        salt = b"fixed_salt_16byt"
        
        manager = EncryptionManager(password=password, salt=salt)
        assert manager.get_salt() == salt

    def test_random_key_has_no_salt(self):
        """Test that random key manager has no salt."""
        manager = EncryptionManager()
        assert manager.get_salt() is None


class TestEncryptionEdgeCases:
    """Test edge cases and special scenarios."""

    def test_encrypt_empty_bytes(self):
        """Test encrypting empty bytes."""
        manager = EncryptionManager()
        original = b""
        
        encrypted = manager.encrypt(original)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == original

    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        manager = EncryptionManager()
        original = ""
        
        encrypted_hex = manager.encrypt_string(original)
        decrypted = manager.decrypt_string(encrypted_hex)
        
        assert decrypted == original

    def test_encrypt_large_data(self):
        """Test encrypting large data."""
        manager = EncryptionManager()
        original = b"x" * 10000
        
        encrypted = manager.encrypt(original)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == original

    def test_encrypt_unicode_string(self):
        """Test encrypting unicode strings."""
        manager = EncryptionManager()
        original = "Hello 世界 🌍"
        
        encrypted_hex = manager.encrypt_string(original)
        decrypted = manager.decrypt_string(encrypted_hex)
        
        assert decrypted == original

    def test_encrypt_complex_json(self):
        """Test encrypting complex JSON structures."""
        manager = EncryptionManager()
        original_data = {
            "users": [
                {"id": 1, "name": "Alice", "tags": ["admin", "user"]},
                {"id": 2, "name": "Bob", "tags": ["user"]},
            ],
            "metadata": {
                "created": "2024-01-01",
                "version": 1.0,
                "active": True,
            },
        }
        
        encrypted_hex = manager.encrypt_json(original_data)
        decrypted_data = manager.decrypt_json(encrypted_hex)
        
        assert decrypted_data == original_data

    def test_encrypted_data_includes_iv(self):
        """Test that encrypted data includes IV."""
        manager = EncryptionManager()
        plaintext = b"test"
        
        encrypted = manager.encrypt(plaintext)
        
        # IV should be first 16 bytes
        assert len(encrypted) >= 16
        # Ciphertext should be at least 16 bytes (due to padding)
        assert len(encrypted) >= 32

    def test_different_ivs_in_consecutive_encryptions(self):
        """Test that consecutive encryptions use different IVs."""
        manager = EncryptionManager()
        plaintext = b"test"
        
        encrypted1 = manager.encrypt(plaintext)
        encrypted2 = manager.encrypt(plaintext)
        
        # Extract IVs (first 16 bytes)
        iv1 = encrypted1[:16]
        iv2 = encrypted2[:16]
        
        # IVs should be different
        assert iv1 != iv2


class TestEncryptionIntegration:
    """Integration tests for encryption scenarios."""

    def test_round_trip_with_password(self):
        """Test complete round-trip with password-based encryption."""
        password = "secure_password_123"
        salt = b"integration_test"
        
        # Original data
        original_data = {
            "user_id": "user_123",
            "preferences": {"theme": "dark", "language": "en"},
            "history": ["item1", "item2", "item3"],
        }
        
        # Encrypt
        manager1 = EncryptionManager(password=password, salt=salt)
        encrypted_hex = manager1.encrypt_json(original_data)
        
        # Decrypt with new manager instance
        manager2 = EncryptionManager(password=password, salt=salt)
        decrypted_data = manager2.decrypt_json(encrypted_hex)
        
        assert decrypted_data == original_data

    def test_multiple_managers_with_same_key(self):
        """Test that multiple managers with same key can decrypt each other's data."""
        password = "shared_password"
        salt = b"shared_salt_16by"
        plaintext = b"shared secret"
        
        manager1 = EncryptionManager(password=password, salt=salt)
        manager2 = EncryptionManager(password=password, salt=salt)
        
        # Manager1 encrypts
        encrypted = manager1.encrypt(plaintext)
        
        # Manager2 decrypts
        decrypted = manager2.decrypt(encrypted)
        
        assert decrypted == plaintext

    def test_encryption_preserves_data_integrity(self):
        """Test that encryption preserves data integrity."""
        manager = EncryptionManager()
        
        test_cases = [
            b"simple text",
            b"\x00\x01\x02\x03",  # binary data
            b"line1\nline2\nline3",  # multiline
            b"special!@#$%^&*()",  # special characters
        ]
        
        for original in test_cases:
            encrypted = manager.encrypt(original)
            decrypted = manager.decrypt(encrypted)
            assert decrypted == original


class TestEncryptionSecurity:
    """Test security properties of encryption."""

    def test_key_size_is_256_bits(self):
        """Test that derived key is 256 bits (32 bytes)."""
        manager = EncryptionManager(password="test", salt=b"salt_16_bytes!!")
        assert len(manager.key) == 32

    def test_iv_size_is_128_bits(self):
        """Test that IV is 128 bits (16 bytes)."""
        manager = EncryptionManager()
        plaintext = b"test"
        encrypted = manager.encrypt(plaintext)
        
        # IV is first 16 bytes
        iv = encrypted[:16]
        assert len(iv) == 16

    def test_salt_size_is_128_bits(self):
        """Test that generated salt is 128 bits (16 bytes)."""
        manager = EncryptionManager(password="test")
        assert len(manager.get_salt()) == 16

    def test_pbkdf2_iterations_is_high(self):
        """Test that PBKDF2 uses sufficient iterations."""
        # This is a constant check
        assert EncryptionManager.PBKDF2_ITERATIONS >= 100000

    def test_encrypted_data_not_readable_as_plaintext(self):
        """Test that encrypted data is not readable as plaintext."""
        manager = EncryptionManager()
        plaintext = b"Secret message"
        
        encrypted = manager.encrypt(plaintext)
        
        # Encrypted data should not contain plaintext
        assert plaintext not in encrypted
        # Encrypted data should not be valid UTF-8 (likely)
        try:
            encrypted.decode('utf-8')
            # If it decodes, it shouldn't match plaintext
            assert encrypted.decode('utf-8') != plaintext.decode('utf-8')
        except UnicodeDecodeError:
            # Expected - encrypted data is binary
            pass
