"""
Data Encryption Utilities for Kitako MVP

This module provides utilities for encrypting sensitive data like
financial information, personal details, and file contents.
"""

import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
import logging

logger = logging.getLogger('kitako')


class DataEncryption:
    """
    Utility class for encrypting and decrypting sensitive data
    """
    
    def __init__(self, key=None):
        """Initialize with encryption key"""
        if key is None:
            key = settings.FIELD_ENCRYPTION_KEY
        
        # Derive a proper encryption key from the provided key
        self.key = self._derive_key(key.encode())
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: bytes) -> bytes:
        """Derive a proper encryption key from password"""
        # Use a fixed salt for consistency (in production, use a random salt per user)
        salt = b'kitako_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        if not data:
            return data
        
        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            return data  # Return original data if encryption fails
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            return encrypted_data  # Return original data if decryption fails
    
    def encrypt_file_content(self, file_content: bytes) -> bytes:
        """Encrypt file content"""
        try:
            return self.cipher.encrypt(file_content)
        except Exception as e:
            logger.error(f"File encryption failed: {str(e)}")
            return file_content
    
    def decrypt_file_content(self, encrypted_content: bytes) -> bytes:
        """Decrypt file content"""
        try:
            return self.cipher.decrypt(encrypted_content)
        except Exception as e:
            logger.error(f"File decryption failed: {str(e)}")
            return encrypted_content


class HashUtility:
    """
    Utility class for hashing sensitive data
    """
    
    @staticmethod
    def hash_data(data: str, salt: str = None) -> str:
        """Hash data with optional salt"""
        if salt is None:
            salt = 'kitako_default_salt'
        
        combined = f"{data}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def hash_file_content(file_content: bytes) -> str:
        """Generate hash of file content for integrity checking"""
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def verify_hash(data: str, hash_value: str, salt: str = None) -> bool:
        """Verify data against hash"""
        return HashUtility.hash_data(data, salt) == hash_value


class PrivacyUtility:
    """
    Utility class for privacy-related operations
    """
    
    @staticmethod
    def anonymize_email(email: str) -> str:
        """Anonymize email address"""
        if '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            anonymized_local = '*' * len(local)
        else:
            anonymized_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{anonymized_local}@{domain}"
    
    @staticmethod
    def anonymize_phone(phone: str) -> str:
        """Anonymize phone number"""
        if len(phone) <= 4:
            return '*' * len(phone)
        
        return phone[:2] + '*' * (len(phone) - 4) + phone[-2:]
    
    @staticmethod
    def anonymize_name(name: str) -> str:
        """Anonymize name"""
        if len(name) <= 2:
            return '*' * len(name)
        
        return name[0] + '*' * (len(name) - 2) + name[-1]
    
    @staticmethod
    def mask_financial_data(amount: float) -> str:
        """Mask financial amount for logging"""
        return f"₱{amount:.0f}***"


# Global instances
default_encryption = DataEncryption()


def encrypt_sensitive_field(value: str) -> str:
    """Encrypt a sensitive field value"""
    return default_encryption.encrypt(value)


def decrypt_sensitive_field(encrypted_value: str) -> str:
    """Decrypt a sensitive field value"""
    return default_encryption.decrypt(encrypted_value)


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data"""
    return HashUtility.hash_data(data)


def anonymize_for_logging(data: dict) -> dict:
    """Anonymize data for logging purposes"""
    anonymized = data.copy()
    
    # Anonymize common sensitive fields
    sensitive_fields = ['email', 'phone', 'phone_number', 'first_name', 'last_name']
    
    for field in sensitive_fields:
        if field in anonymized:
            if field == 'email':
                anonymized[field] = PrivacyUtility.anonymize_email(anonymized[field])
            elif field in ['phone', 'phone_number']:
                anonymized[field] = PrivacyUtility.anonymize_phone(anonymized[field])
            elif field in ['first_name', 'last_name']:
                anonymized[field] = PrivacyUtility.anonymize_name(anonymized[field])
    
    # Mask financial amounts
    financial_fields = ['amount', 'total_income', 'total_expenses', 'net_income']
    for field in financial_fields:
        if field in anonymized and isinstance(anonymized[field], (int, float)):
            anonymized[field] = PrivacyUtility.mask_financial_data(anonymized[field])
    
    return anonymized
