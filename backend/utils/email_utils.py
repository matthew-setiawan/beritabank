"""
Email utilities for BeritaBank
Handles email sending functionality
"""

import smtplib
import os
import json
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_email(message, subject="BeritaBank Notification", to_email=None):
    """
    Send an email using Gmail SMTP
    
    Args:
        message (str): The email message content
        subject (str): Email subject line (default: "BeritaBank Notification")
        to_email (str): Recipient email address (default: uses EMAIL_USERNAME from env)
    
    Returns:
        dict: Success status and message
    """
    try:
        # Get email credentials from environment variables
        email_username = os.getenv('EMAIL_USERNAME')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        # Use provided email or default to admin email
        recipient_email = to_email if to_email else email_username
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_username
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable TLS encryption
        server.login(email_username, email_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(email_username, recipient_email, text)
        server.quit()
        
        return {
            'success': True,
            'message': f'Email sent successfully to {recipient_email}'
        }
        
    except smtplib.SMTPAuthenticationError:
        return {
            'success': False,
            'error': 'Email authentication failed. Please check credentials.'
        }
    except smtplib.SMTPRecipientsRefused:
        return {
            'success': False,
            'error': 'Recipient email address is invalid.'
        }
    except smtplib.SMTPException as e:
        return {
            'success': False,
            'error': f'SMTP error occurred: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to send email: {str(e)}'
        }

def encrypt_code(verification_code, expiry_minutes=4):
    """
    Encrypt a verification code with expiry time
    
    Args:
        verification_code (str): The verification code to encrypt
        expiry_minutes (int): Minutes until expiry (default: 10)
    
    Returns:
        dict: Success status and encrypted code
    """
    try:
        # Get encryption key from environment or generate one
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key:
            # Generate a new key if none exists (for development)
            key = Fernet.generate_key()
            encryption_key = key.decode()
            print(f"WARNING: No ENCRYPTION_KEY found in environment. Generated new key: {encryption_key}")
            print("Please add this to your .env file: ENCRYPTION_KEY=" + encryption_key)
        
        # Initialize Fernet with the key
        f = Fernet(encryption_key.encode())
        
        # Calculate expiry time
        expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
        
        # Create data to encrypt
        data = {
            'code': verification_code,
            'expiry': expiry_time.isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        # Convert to JSON and encrypt
        json_data = json.dumps(data)
        encrypted_data = f.encrypt(json_data.encode())
        
        # Encode to base64 for safe transmission
        encrypted_code = base64.b64encode(encrypted_data).decode()
        
        return {
            'success': True,
            'encrypted_code': encrypted_code,
            'expires_at': expiry_time.isoformat(),
            'expires_in_minutes': expiry_minutes
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to encrypt code: {str(e)}'
        }

def decrypt_code(encrypted_code, provided_code):
    """
    Decrypt and verify a verification code
    
    Args:
        encrypted_code (str): The encrypted code from encrypt_code
        provided_code (str): The code provided by user for verification
    
    Returns:
        dict: Success status and verification result
    """
    try:
        # Get encryption key from environment
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key:
            return {
                'success': False,
                'error': 'Encryption key not found in environment variables'
            }
        
        # Initialize Fernet with the key
        f = Fernet(encryption_key.encode())
        
        # Decode from base64
        try:
            encrypted_data = base64.b64decode(encrypted_code.encode())
        except Exception:
            return {
                'success': False,
                'error': 'Invalid encrypted code format'
            }
        
        # Decrypt the data
        try:
            decrypted_data = f.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())
        except Exception:
            return {
                'success': False,
                'error': 'Failed to decrypt code or invalid format'
            }
        
        # Check if code matches
        if data['code'] != provided_code:
            return {
                'success': False,
                'error': 'Verification code does not match',
                'is_expired': False,
                'is_valid': False
            }
        
        # Check if code has expired
        expiry_time = datetime.fromisoformat(data['expiry'])
        current_time = datetime.now()
        
        if current_time > expiry_time:
            return {
                'success': False,
                'error': 'Verification code has expired',
                'is_expired': True,
                'is_valid': False,
                'expired_at': data['expiry']
            }
        
        # Calculate time remaining
        time_remaining = expiry_time - current_time
        minutes_remaining = int(time_remaining.total_seconds() / 60)
        
        return {
            'success': True,
            'message': 'Verification code is valid',
            'is_expired': False,
            'is_valid': True,
            'minutes_remaining': minutes_remaining,
            'expires_at': data['expiry'],
            'created_at': data['created_at']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to decrypt and verify code: {str(e)}'
        }

def send_verification_code(to_email, username=None):
    """
    Send a verification code to the specified email address
    
    Args:
        to_email (str): Recipient email address
        username (str): Username for personalization (optional)
    
    Returns:
        dict: Success status, verification code, and message
    """
    import random
    import string
    
    try:
        # Generate 6-digit verification code
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        # Create personalized greeting
        greeting = f"Hello {username}!" if username else "Hello!"
        
        # Create HTML email template
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .verification-code {{
                    background-color: #3498db;
                    color: white;
                    font-size: 32px;
                    font-weight: bold;
                    text-align: center;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    letter-spacing: 3px;
                }}
                .message {{
                    font-size: 16px;
                    margin: 20px 0;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #7f8c8d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🏦 BeritaBank</div>
                    <h2>Email Verification</h2>
                </div>
                
                <div class="message">
                    <p>{greeting}</p>
                    <p>Thank you for registering with BeritaBank! To complete your registration, please use the verification code below:</p>
                </div>
                
                <div class="verification-code">
                    {verification_code}
                </div>
                
                <div class="message">
                    <p>Enter this code in the verification field to activate your account.</p>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important:</strong> This code will expire in 10 minutes. Do not share this code with anyone.
                </div>
                
                <div class="footer">
                    <p>If you didn't request this verification, please ignore this email.</p>
                    <p>© 2024 BeritaBank. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        plain_text = f"""
        BeritaBank - Email Verification
        
        {greeting}
        
        Thank you for registering with BeritaBank! To complete your registration, please use the verification code below:
        
        VERIFICATION CODE: {verification_code}
        
        Enter this code in the verification field to activate your account.
        
        IMPORTANT: This code will expire in 10 minutes. Do not share this code with anyone.
        
        If you didn't request this verification, please ignore this email.
        
        © 2024 BeritaBank. All rights reserved.
        """
        
        # Send email with HTML content
        result = send_email(
            message=plain_text,
            subject="BeritaBank - Email Verification Code",
            to_email=to_email
        )
        
        if result['success']:
            return {
                'success': True,
                'verification_code': verification_code,
                'message': f'Verification code sent to {to_email}',
                'expires_in': '10 minutes'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to generate and send verification code: {str(e)}'
        }

if __name__ == "__main__":
    print("=== Testing Encryption/Decryption Functions ===")
    
    # Generate a test verification code
    import random
    import string
    test_code = ''.join(random.choices(string.digits, k=6))
    print(f"Generated Test Code: {test_code}")
    
    # Test encryption
    print("\n--- Testing Encryption ---")
    encrypt_result = encrypt_code(test_code, expiry_minutes=5)
    print(f"Encryption Success: {encrypt_result['success']}")
    if encrypt_result['success']:
        print(f"Encrypted Code: {encrypt_result['encrypted_code'][:50]}...")
        print(f"Expires at: {encrypt_result['expires_at']}")
        print(f"Expires in minutes: {encrypt_result['expires_in_minutes']}")
        
        # Test decryption with correct code
        print("\n--- Testing Decryption with Correct Code ---")
        decrypt_result = decrypt_code(encrypt_result['encrypted_code'], test_code)
        print(f"Decryption Success: {decrypt_result['success']}")
        if decrypt_result['success']:
            print(f"Code Valid: {decrypt_result['is_valid']}")
            print(f"Minutes Remaining: {decrypt_result['minutes_remaining']}")
            print(f"Created at: {decrypt_result['created_at']}")
            print(f"Expires at: {decrypt_result['expires_at']}")
        else:
            print(f"Decryption Error: {decrypt_result['error']}")
        
        # Test decryption with wrong code
        print("\n--- Testing Decryption with Wrong Code ---")
        wrong_decrypt = decrypt_code(encrypt_result['encrypted_code'], "999999")
        print(f"Wrong Code Test Success: {wrong_decrypt['success']} (should be False)")
        print(f"Wrong Code Error: {wrong_decrypt['error']}")
        print(f"Is Valid: {wrong_decrypt.get('is_valid', 'N/A')}")
        
        # Test decryption with another wrong code
        print("\n--- Testing Decryption with Another Wrong Code ---")
        another_wrong = decrypt_code(encrypt_result['encrypted_code'], "000000")
        print(f"Another Wrong Code Test: {another_wrong['success']} (should be False)")
        print(f"Error Message: {another_wrong['error']}")
        
    else:
        print(f"Encryption Error: {encrypt_result['error']}")
    
    print("\n=== Test Complete ===")
    print("All encryption/decryption tests completed!")
