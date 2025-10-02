"""
Authentication helper utilities for BeritaBank Backend
"""

import hashlib
import secrets
from typing import Tuple
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """
    Hash password using Werkzeug's secure password hashing
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return generate_password_hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Plain text password
        hashed_password: Hashed password to verify against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return check_password_hash(hashed_password, password)

def generate_token(length: int = 32) -> str:
    """
    Generate a secure random token
    
    Args:
        length: Length of token in bytes
        
    Returns:
        str: Random token
    """
    return secrets.token_urlsafe(length)

def generate_reset_token() -> str:
    """
    Generate a password reset token
    
    Returns:
        str: Reset token
    """
    return generate_token(32)

def hash_token(token: str) -> str:
    """
    Hash a token for storage
    
    Args:
        token: Plain text token
        
    Returns:
        str: Hashed token
    """
    return hashlib.sha256(token.encode()).hexdigest()

def generate_api_key() -> Tuple[str, str]:
    """
    Generate API key and its hash
    
    Returns:
        tuple: (api_key, hashed_api_key)
    """
    api_key = generate_token(32)
    hashed_key = hash_token(api_key)
    return api_key, hashed_key

def verify_api_key(api_key: str, hashed_api_key: str) -> bool:
    """
    Verify API key against its hash
    
    Args:
        api_key: Plain text API key
        hashed_api_key: Hashed API key to verify against
        
    Returns:
        bool: True if API key matches, False otherwise
    """
    return hash_token(api_key) == hashed_api_key

def generate_session_id() -> str:
    """
    Generate a session ID
    
    Returns:
        str: Session ID
    """
    return generate_token(24)

def hash_session_id(session_id: str) -> str:
    """
    Hash a session ID for storage
    
    Args:
        session_id: Plain text session ID
        
    Returns:
        str: Hashed session ID
    """
    return hash_token(session_id)

def verify_session_id(session_id: str, hashed_session_id: str) -> bool:
    """
    Verify session ID against its hash
    
    Args:
        session_id: Plain text session ID
        hashed_session_id: Hashed session ID to verify against
        
    Returns:
        bool: True if session ID matches, False otherwise
    """
    return hash_token(session_id) == hashed_session_id

def generate_verification_code() -> str:
    """
    Generate a 6-digit verification code
    
    Returns:
        str: 6-digit verification code
    """
    import random
    return str(random.randint(100000, 999999))

def hash_verification_code(code: str) -> str:
    """
    Hash a verification code for storage
    
    Args:
        code: Plain text verification code
        
    Returns:
        str: Hashed verification code
    """
    return hash_token(code)

def verify_verification_code(code: str, hashed_code: str) -> bool:
    """
    Verify verification code against its hash
    
    Args:
        code: Plain text verification code
        hashed_code: Hashed verification code to verify against
        
    Returns:
        bool: True if verification code matches, False otherwise
    """
    return hash_token(code) == hashed_code

def generate_otp(length: int = 6) -> str:
    """
    Generate a one-time password
    
    Args:
        length: Length of OTP
        
    Returns:
        str: OTP
    """
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def hash_otp(otp: str) -> str:
    """
    Hash an OTP for storage
    
    Args:
        otp: Plain text OTP
        
    Returns:
        str: Hashed OTP
    """
    return hash_token(otp)

def verify_otp(otp: str, hashed_otp: str) -> bool:
    """
    Verify OTP against its hash
    
    Args:
        otp: Plain text OTP
        hashed_otp: Hashed OTP to verify against
        
    Returns:
        bool: True if OTP matches, False otherwise
    """
    return hash_token(otp) == hashed_otp
