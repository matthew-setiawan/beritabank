"""
Decorators for BeritaBank Backend
"""

import time
from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.logger import get_logger

logger = get_logger(__name__)

def rate_limit(limit: int, per: int = 60):
    """
    Rate limiting decorator
    
    Args:
        limit: Number of requests allowed
        per: Time period in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # In a production environment, you would use Redis or similar
            # for distributed rate limiting. For now, this is a simple in-memory implementation.
            
            # Get client identifier (IP address or user ID)
            client_id = request.remote_addr
            if hasattr(g, 'user_id'):
                client_id = g.user_id
            
            # Check rate limit (simplified implementation)
            # In production, use Redis with sliding window or token bucket algorithm
            current_time = time.time()
            window_start = current_time - per
            
            # For now, just log the rate limit check
            logger.info(f"Rate limit check for {client_id}: {limit} requests per {per} seconds")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator to require admin privileges
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        
        # Check if user has admin role
        # This would typically involve querying the database
        # For now, we'll implement a simple check
        
        from models.user import User
        user = User.find_by_id(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_json(*required_fields):
    """
    Decorator to validate JSON request data
    
    Args:
        required_fields: List of required field names
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body is required'}), 400
            
            # Check required fields
            missing_fields = []
            for field in required_fields:
                if field not in data or not data[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def cache_response(ttl: int = 300):
    """
    Decorator to cache response (simplified implementation)
    
    Args:
        ttl: Time to live in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # In a production environment, you would use Redis or similar
            # for response caching. For now, this is a placeholder.
            
            # Generate cache key based on request
            cache_key = f"{request.endpoint}:{request.args}:{request.remote_addr}"
            
            # Check cache (simplified)
            # cached_response = cache.get(cache_key)
            # if cached_response:
            #     return cached_response
            
            # Execute function
            response = f(*args, **kwargs)
            
            # Store in cache (simplified)
            # cache.set(cache_key, response, ttl)
            
            return response
        
        return decorated_function
    return decorator

def log_request(f):
    """
    Decorator to log HTTP requests
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")
        
        # Execute function
        response = f(*args, **kwargs)
        
        # Log response
        duration = time.time() - start_time
        logger.info(f"Response: {response[1] if isinstance(response, tuple) else 200} in {duration:.3f}s")
        
        return response
    
    return decorated_function

def handle_errors(f):
    """
    Decorator to handle common errors
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"ValueError in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Invalid input data', 'details': str(e)}), 400
        except KeyError as e:
            logger.error(f"KeyError in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Missing required data', 'details': str(e)}), 400
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
    
    return decorated_function

def require_verification(f):
    """
    Decorator to require email verification
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        
        from models.user import User
        user = User.find_by_id(current_user_id)
        
        if not user or not user.is_verified:
            return jsonify({'error': 'Email verification required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_content_type(content_type: str = 'application/json'):
    """
    Decorator to validate content type
    
    Args:
        content_type: Expected content type
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.content_type != content_type:
                return jsonify({
                    'error': f'Content-Type must be {content_type}'
                }), 415
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def track_usage(f):
    """
    Decorator to track API usage
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Track usage metrics
        # In production, you would store this in a database or analytics service
        
        usage_data = {
            'endpoint': request.endpoint,
            'method': request.method,
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr,
            'timestamp': time.time()
        }
        
        # Store usage data (simplified)
        logger.info(f"API Usage: {usage_data}")
        
        return f(*args, **kwargs)
    
    return decorated_function
