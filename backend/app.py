"""
BeritaBank Backend Application
Main Flask application entry point
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.auth_utils import hash_password, verify_password, generate_token, require_auth
from models.claudiaai import claudiai

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
    
# Initialize CORS
CORS(app)
    
# MongoDB connection
connection_string = os.getenv('MONGODB_CONNECTION_STRING')
if not connection_string:
    raise ValueError("MONGODB_CONNECTION_STRING not found in environment variables")

client = MongoClient(connection_string)
db = client['beritabank']
collection = db['news_articles']
bank_collection = db['bank_information']
user_collection = db['users']


@app.route('/api/articles', methods=['GET'])
def get_articles():
    """
    Get latest articles from MongoDB sorted by importance score
    
    Query Parameters:
        limit (int): Number of articles to return (default: 20)
    
    Returns:
        JSON response with articles sorted by importance (descending) and creation date (descending)
    """
    try:
        # Get limit parameter from query string
        limit = request.args.get('limit', 30, type=int)
        
        # Validate limit parameter
        if limit <= 0:
            return jsonify({
                'success': False,
                'error': 'Limit must be a positive integer'
            }), 400
        
               # Query MongoDB: sort by date (descending), then importance (descending), then created_at (descending)
               # Limit the results and convert ObjectId to string
        articles = list(collection.find().sort([
                   ('date', -1),        # Sort by date descending (newest first)
                   ('importance', -1),  # Then by importance descending (5, 4, 3, 2, 1)
                   ('created_at', -1)   # Finally by creation date descending (newest first)
               ]).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for article in articles:
            article['_id'] = str(article['_id'])
        
        return jsonify({
            'success': True,
            'data': {
                'articles': articles,
                'count': len(articles),
                'limit': limit
            },
            'message': f'Retrieved {len(articles)} articles sorted by importance'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve articles: {str(e)}'
        }), 500

@app.route('/api/banks', methods=['GET'])
def get_bank_info():
    """
    Get bank information documents from MongoDB
    Query params:
      - limit (int, optional): number of records to return (default 50, max 200)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        if limit <= 0:
            return jsonify({'success': False, 'error': 'Limit must be a positive integer'}), 400
        if limit > 200:
            limit = 200

        banks = list(
            bank_collection
            .find()
            .sort([
                ('updated_at', -1),  # newest updates first
                ('created_at', -1),
                ('name', 1),
            ])
            .limit(limit)
        )

        for b in banks:
            b['_id'] = str(b['_id'])

        return jsonify({
            'success': True,
            'data': {
                'banks': banks,
                'count': len(banks),
                'limit': limit,
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to retrieve banks: {str(e)}'}), 500

@app.route('/api/articles/<string:article_id>', methods=['GET'])
def get_article_by_id(article_id):
    """
    Get a single article by its MongoDB _id
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(article_id):
            return jsonify({
                'success': False,
                'error': 'Invalid article id'
            }), 400

        article = collection.find_one({'_id': ObjectId(article_id)})
        if not article:
            return jsonify({
                'success': False,
                'error': 'Article not found'
            }), 404

        # Convert ObjectId to string
        article['_id'] = str(article['_id'])

        return jsonify({
            'success': True,
            'data': article
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve article: {str(e)}'
        }), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Expected JSON:
    {
        "username": "string",
        "email": "string", 
        "password": "string",
        "desc": "string" (optional - user description/interests)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        print(data)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        desc = data.get('desc', '')  # Optional field, default to empty string
        
        # Validation
        if not username or not email or not password:
            return jsonify({'success': False, 'error': 'Username, email, and password are required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        existing_user = user_collection.find_one({
            '$or': [
                {'username': username},
                {'email': email}
            ]
        })
        
        if existing_user:
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 409
        
        # Hash password
        password_hash, salt = hash_password(password)
        
        # Generate token
        token = generate_token()
        
        # Generate daily summary for new user
        daily_summary = {
            'last_updated': datetime.now().isoformat(),
            'summary_en': '',
            'summary_id': '',
            'advice_en': '',
            'advice_id': '',
            'search_results': []
        }
        
        # If user provided description, generate daily summary
        if desc and desc.strip():
            try:
                from models.daily_summarizer import generate_daily_summary
                summary_result = generate_daily_summary(desc)
                
                if summary_result.get('success'):
                    daily_summary.update({
                        'summary_en': summary_result.get('summary_en', ''),
                        'summary_id': summary_result.get('summary_id', ''),
                        'advice_en': summary_result.get('advice_en', ''),
                        'advice_id': summary_result.get('advice_id', ''),
                        'search_results': summary_result.get('search_results', [])
                    })
            except Exception as e:
                print(f"Warning: Could not generate daily summary for new user: {e}")
                # Continue with registration even if daily summary fails
        
        # Create user document
        user_doc = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'salt': salt,
            'token': token,
            'desc': desc,
            'chat_history': [],  # Initialize empty chat history
            'daily_summary': daily_summary,  # Add daily summary
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        # Insert user
        result = user_collection.insert_one(user_doc)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user_id': str(result.inserted_id),
                'username': username,
                'email': email,
                'desc': desc,
                'token': token
            }
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login user
    
    Expected JSON:
    {
        "username": "string", (or email)
        "password": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        username_or_email = data.get('username')
        password = data.get('password')
        
        if not username_or_email or not password:
            return jsonify({'success': False, 'error': 'Username/email and password are required'}), 400
        
        # Find user by username or email
        user = user_collection.find_one({
            '$or': [
                {'username': username_or_email},
                {'email': username_or_email}
            ]
        })
        
        if not user:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash'], user['salt']):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Generate new token
        new_token = generate_token()
        
        # Update user with new token and last login
        user_collection.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'token': new_token,
                    'last_login': datetime.now().isoformat()
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user_id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'desc': user.get('desc', ''),
                'token': new_token
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth(user_collection)
def get_current_user():
    """
    Get current user information (protected route)
    """
    try:
        user = request.current_user
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'desc': user.get('desc', ''),
                'created_at': user['created_at'],
                'last_login': user.get('last_login')
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get user info: {str(e)}'}), 500

@app.route('/api/message', methods=['POST'])
@require_auth(user_collection)
def send_message():
    """
    Send a message to Claudia AI (protected route)
    
    Expected JSON:
    {
        "message": "string" (optional - if not provided, will trigger daily_intro or introduction),
        "language": "string" (optional - "en" for English, "id" for Indonesian, defaults to "en")
    }
    """
    try:
        user = request.current_user
        data = request.get_json()
        
        if not data:
            data = {}
        
        user_message = data.get('message', '')
        language = data.get('language', 'en')  # Default to English
        user_description = user.get('desc', '')
        chat_history = user.get('chat_history', [])
        
        # Determine the type of request
        if not user_message:
            # No message provided - determine if this is introduction or daily_intro
            if not chat_history:
                # No chat history - this is an introduction
                system_request = "introduction"
            else:
                # Has chat history - this is a daily intro
                system_request = "daily_intro"
        else:
            # Message provided - this is a response
            system_request = "response"
        
        # For response type, we need to include the current message in the context
        if system_request == "response":
            # Create a temporary chat history that includes the current message
            temp_chat_history = chat_history.copy()
            temp_chat_history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
        else:
            temp_chat_history = chat_history
        
        # Call Claudia AI
        claudia_response = claudiai(
            user_description=user_description,
            chat_history=temp_chat_history,
            system_request=system_request,
            language=language
        )
        print(claudia_response)
        if not claudia_response.get('success'):
            return jsonify({
                'success': False,
                'error': f'Claudia AI error: {claudia_response.get("error", "Unknown error")}'
            }), 500
        
        # Update chat history
        new_chat_history = chat_history.copy()
        
        # Add user message if provided
        if user_message:
            new_chat_history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
        
        # Add Claudia's response
        new_chat_history.append({
            'role': 'assistant',
            'content': claudia_response['message'],
            'timestamp': claudia_response['timestamp']
        })
        
        # Update user's chat history in database
        user_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'chat_history': new_chat_history}}
        )
        
        return jsonify({
            'success': True,
            'data': {
                'message': claudia_response['message'],
                'type': system_request,
                'timestamp': claudia_response['timestamp'],
                'chat_history': new_chat_history
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Message processing failed: {str(e)}'}), 500

@app.route('/api/daily-summary', methods=['GET'])
@require_auth(user_collection)
def get_daily_summary():
    """
    Get user's daily summary. If not updated today, generate new one.
    
    Headers:
        Authorization: Bearer <token>
    """
    try:
        # Get user from token
        user = request.current_user
        
        # Re-fetch user from database to get latest data
        user = user_collection.find_one({'_id': user['_id']})
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Check if daily summary exists and is from today
        daily_summary = user.get('daily_summary', {})
        print("daily_summary", daily_summary)
        last_updated = daily_summary.get('last_updated', '')
        print("last_updated", last_updated)
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        print("today", today)
        
        # Check if we need to update the daily summary
        if not last_updated or not last_updated.startswith(today):
            # Generate new daily summary
            if user.get('desc') and user.get('desc').strip():
                try:
                    from models.daily_summarizer import generate_daily_summary
                    summary_result = generate_daily_summary(user.get('desc'))
                    
                    if summary_result.get('success'):
                        # Update the daily summary
                        new_daily_summary = {
                            'last_updated': datetime.now().isoformat(),
                            'summary_en': summary_result.get('summary_en', ''),
                            'summary_id': summary_result.get('summary_id', ''),
                            'advice_en': summary_result.get('advice_en', ''),
                            'advice_id': summary_result.get('advice_id', ''),
                            'search_results': summary_result.get('search_results', [])
                        }
                        
                        # Update in database
                        user_collection.update_one(
                            {'_id': user['_id']},
                            {'$set': {'daily_summary': new_daily_summary}}
                        )
                        
                        daily_summary = new_daily_summary
                    else:
                        return jsonify({
                            'success': False,
                            'error': f'Failed to generate daily summary: {summary_result.get("error", "Unknown error")}'
                        }), 500
                        
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': f'Failed to generate daily summary: {str(e)}'
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': 'User description not found. Please update your profile first.'
                }), 400
        
        print("data test",{
            'success': True,
            'data': {
                'daily_summary': daily_summary,
                'user_desc': user.get('desc', '')
            }
        })
        return jsonify({
            'success': True,
            'data': {
                'daily_summary': daily_summary,
                'user_desc': user.get('desc', '')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to retrieve daily summary: {str(e)}'}), 500

@app.route('/api/update_desc', methods=['POST'])
@require_auth(user_collection)
def update_desc():
    """
    Update user's description/preferences based on their message.
    
    Headers:
        Authorization: Bearer <token>
    
    Expected JSON:
    {
        "message": "string" (user's request to update preferences)
    }
    """
    try:
        # Get user from token
        user = request.current_user
        
        # Get message from request
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        user_message = data['message']
        current_desc = user.get('desc', '')
        
        # Use preference updater to get new description and response
        try:
            from models.preference_updater import update_user_preferences
            update_result = update_user_preferences(current_desc, user_message)
            
            if not update_result.get('success'):
                return jsonify({
                    'success': False,
                    'error': f"Failed to update preferences: {update_result.get('error', 'Unknown error')}"
                }), 500
            
            new_desc = update_result.get('new_desc', current_desc)
            response_message = update_result.get('response', 'Preferences updated successfully')
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to process preference update: {str(e)}'
            }), 500
        
        # Determine if description actually changed (ignoring leading/trailing whitespace)
        desc_changed = (new_desc.strip() != current_desc.strip())
        print("desc_changed", desc_changed)

        # Update user's description in database only if changed
        if desc_changed:
            try:
                user_collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'desc': new_desc}}
                )
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Failed to update user description: {str(e)}'
                }), 500

            # Reset daily summary to force regeneration when description changes
            try:
                reset_daily_summary = {
                    'last_updated': '2001-01-01T00:00:00',  # Dummy date in the past
                    'summary_en': '',
                    'summary_id': '',
                    'advice_en': '',
                    'advice_id': '',
                    'search_results': []
                }
                user_collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'daily_summary': reset_daily_summary}}
                )
                daily_summary_reset = True
            except Exception as e:
                print(f"Warning: Could not reset daily summary: {e}")
                daily_summary_reset = False
                # Continue even if daily summary reset fails
        else:
            # No change; do not update DB or reset daily summary
            daily_summary_reset = False

        print({
            'success': True,
            'message': response_message,
            'type': 'desc_updated',
            'desc_updated': desc_changed,
            'data': {
                'new_desc': new_desc,
                'daily_summary_reset': daily_summary_reset
            }
        })

        return jsonify({
            'success': True,
            'message': response_message,
            'type': 'desc_updated',
            'desc_updated': desc_changed,
            'data': {
                'new_desc': new_desc,
                'daily_summary_reset': daily_summary_reset
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to update description: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)