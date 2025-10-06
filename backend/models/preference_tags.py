"""
Preference Tags Generator
Generates bank and asset preferences based on user descriptions using OpenAI
"""

import json
import sys
import os

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.openai_utils import call_openai

def generate_preference_tags(user_desc):
    """
    Generate bank and asset preference tags based on user description
    
    Args:
        user_desc (str): User's description of their interests/preferences
    
    Returns:
        dict: Success status and generated tags
    """
    try:
        if not user_desc or not user_desc.strip():
            return {
                'success': False,
                'error': 'User description is required'
            }
        
        # Create prompt for OpenAI
        prompt = f"""
        Based on the following user description, generate relevant bank and asset preferences.
        
        User Description: "{user_desc}"
        
        Please analyze this description and generate:
        1. A list of relevant banks (Indonesian banks like BCA, Mandiri, BRI, BNI, Mayapada, etc.)
        2. A list of relevant assets (Bitcoin, Ethereum, Real Estate, Gold, Stocks, Bonds, etc.)
        
        Return ONLY a valid JSON object in this exact format:
        {{
            "banks": ["Bank1", "Bank2", "Bank3"],
            "assets": ["Asset1", "Asset2", "Asset3"]
        }}
        
        Guidelines:
        - For BANKS: Only include banks that are explicitly mentioned by name in the user's description. Do NOT infer banks from general terms like "traditional banking", "digital banking", etc. Only include if the user specifically mentions bank names like "BCA", "Mandiri", "Mayapada", etc.
        - For ASSETS: Include asset types that match the user's investment profile, even if mentioned generally (Bitcoin, Ethereum, Real Estate, Gold, Stocks, Bonds, Mutual Funds, etc.)
        - Use common Indonesian bank names (BCA, Mandiri, BRI, BNI, Mayapada, CIMB, etc.) ONLY if explicitly mentioned
        - Use common asset types (Bitcoin, Ethereum, Real Estate, Gold, Stocks, Bonds, Mutual Funds, etc.)
        - Be specific and relevant to the user's description
        - If no banks or assets are explicitly mentioned or relevant, use empty arrays []
        - Return ONLY the JSON, no other text
        """
        
        # Call OpenAI
        response = call_openai(
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=500,
            temperature=0.3
        )
        
        # Check if response contains error
        if response.startswith("Error:"):
            return {
                'success': False,
                'error': response
            }
        
        # Try to parse JSON response
        try:
            # Clean the response to extract JSON
            response = response.strip()
            
            # Find JSON object in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return {
                    'success': False,
                    'error': 'No valid JSON found in OpenAI response'
                }
            
            json_str = response[start_idx:end_idx]
            tags = json.loads(json_str)
            
            # Validate the structure
            if not isinstance(tags, dict) or 'banks' not in tags or 'assets' not in tags:
                return {
                    'success': False,
                    'error': 'Invalid JSON structure returned by OpenAI'
                }
            
            # Ensure arrays are not empty and contain strings
            if not isinstance(tags['banks'], list) or not isinstance(tags['assets'], list):
                return {
                    'success': False,
                    'error': 'Banks and assets must be arrays'
                }
            
            # Empty arrays are allowed if nothing is relevant
            
            # Validate that all items are strings
            for bank in tags['banks']:
                if not isinstance(bank, str) or not bank.strip():
                    return {
                        'success': False,
                        'error': 'All bank names must be non-empty strings'
                    }
            
            for asset in tags['assets']:
                if not isinstance(asset, str) or not asset.strip():
                    return {
                        'success': False,
                        'error': 'All asset names must be non-empty strings'
                    }
            
            return {
                'success': True,
                'data': {
                    'banks': [bank.strip() for bank in tags['banks']],
                    'assets': [asset.strip() for asset in tags['assets']]
                }
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Failed to parse JSON response: {str(e)}'
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to generate preference tags: {str(e)}'
        }

def test_preference_tags():
    """
    Test function for preference tags generation
    """
    test_descriptions = [
        "What bank are you currently depositing your money in?: Bank Mayapada, What types of investments are you most interested in?: Bitcoin, How do you usually approach investing?: I prefer safer, stable options, How would you like the news presented?: Simple and easy-to-understand",
        "I prefer traditional banking and real estate investments"
    ]
    
    print("🧪 Testing Preference Tags Generation")
    print("=" * 50)
    
    for i, desc in enumerate(test_descriptions, 1):
        print(f"\nTest {i}: {desc}")
        print("-" * 30)
        
        result = generate_preference_tags(desc)
        
        if result['success']:
            print("✅ Success!")
            print(f"Banks: {result['data']['banks']}")
            print(f"Assets: {result['data']['assets']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")

if __name__ == "__main__":
    test_preference_tags()
