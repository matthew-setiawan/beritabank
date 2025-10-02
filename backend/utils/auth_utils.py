"""
Authentication utility functions for BeritaBank
"""
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import request, jsonify


def hash_password(password):
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash, salt


def verify_password(password, password_hash, salt):
    """Verify a password against its hash"""
    return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash


def generate_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def require_auth(user_collection):
    """Decorator factory to require authentication for protected routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            
            if not token:
                return jsonify({'success': False, 'error': 'No authorization token provided'}), 401
            
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Find user by token
            user = user_collection.find_one({'token': token})
            
            if not user:
                return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
            
            # Check if token is expired (optional: add expiration logic)
            # For now, tokens don't expire, but you can add expiration logic here
            
            # Add user info to request context
            request.current_user = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
