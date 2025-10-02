"""
Validation utilities for BeritaBank Backend
"""

import re
from typing import Optional

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    """
    Validate password strength
    
    Args:
        password: Password string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not password or len(password) < 8:
        return False
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (Indonesian format)
    
    Args:
        phone: Phone number string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Indonesian phone number patterns
    # Mobile: 08xx, +628xx, 628xx
    # Landline: 02x, 03x, 04x, 05x, 06x, 07x
    patterns = [
        r'^08\d{8,10}$',  # 08xx format
        r'^\+628\d{8,10}$',  # +628xx format
        r'^628\d{8,10}$',  # 628xx format
        r'^0[2-7]\d{7,9}$'  # Landline format
    ]
    
    return any(re.match(pattern, digits_only) for pattern in patterns)

def validate_username(username: str) -> bool:
    """
    Validate username format
    
    Args:
        username: Username string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not username:
        return False
    
    # Username should be 3-20 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not url:
        return False
    
    # Basic URL regex pattern
    pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))

def validate_bank_code(bank_code: str) -> bool:
    """
    Validate bank code format
    
    Args:
        bank_code: Bank code string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not bank_code:
        return False
    
    # Bank code should be 3-4 digits
    pattern = r'^\d{3,4}$'
    return bool(re.match(pattern, bank_code))

def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input
    
    Args:
        text: Input text to sanitize
        max_length: Maximum length to truncate to
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Truncate if max_length is specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

def validate_date_format(date_string: str, format_string: str = '%Y-%m-%d') -> bool:
    """
    Validate date string format
    
    Args:
        date_string: Date string to validate
        format_string: Expected date format
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not date_string:
        return False
    
    try:
        from datetime import datetime
        datetime.strptime(date_string, format_string)
        return True
    except ValueError:
        return False

def validate_pagination_params(page: int, per_page: int, max_per_page: int = 100) -> tuple:
    """
    Validate and sanitize pagination parameters
    
    Args:
        page: Page number
        per_page: Items per page
        max_per_page: Maximum allowed items per page
        
    Returns:
        tuple: (validated_page, validated_per_page)
    """
    # Ensure page is at least 1
    page = max(1, page) if page else 1
    
    # Ensure per_page is within limits
    per_page = max(1, min(per_page, max_per_page)) if per_page else 20
    
    return page, per_page
