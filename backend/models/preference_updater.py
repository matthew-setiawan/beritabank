import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.perplexity_utils import call_perplexity_chat
except ImportError:
    try:
        from perplexity_utils import call_perplexity_chat
    except ImportError:
        print("Error: Could not import call_perplexity_chat")
        sys.exit(1)

load_dotenv()

def update_user_preferences(user_desc: str, message: str) -> dict:
    """
    Update user preferences based on their current description and a new message.
    
    Args:
        user_desc (str): Current user description/preferences
        message (str): User's message requesting preference changes
    
    Returns:
        dict: Updated description and response message
    """
    try:
        prompt = f"""
        You are a financial assistant managing a user's preference description.

        Current user preferences (user_desc):\n{user_desc}\n
        User's message:\n{message}\n
        You must return ONLY valid JSON with no extra text, using exactly one of these schemas:
        - If the message EXPLICITLY requests changes to preferences, return:
          {{
            "new_desc": "Updated user description reflecting the requested changes",
            "response": "Clear confirmation explaining what changed"
          }}
        - If the message is a QUESTION or does NOT clearly request preference changes, return:
          {{
            "response": "answer the question"
          }}

        UPDATE CONTROL RULES:
        1) NO UPDATE (default): If the user asks a question, requests information, or is unclear/ambiguous about changes, DO NOT update preferences. Use the response-only schema.
        2) ADDITIVE UPDATE: If the user asks to add interests or preferences, include them in new_desc while preserving existing relevant content.
        3) REMOVAL/OVERRIDE: If the user clearly wants to remove or replace interests, update new_desc accordingly removing the specified parts.
        4) SPECIFIC REPLACEMENTS: When user specifies replacements, apply them precisely in new_desc.
        5) AMBIGUOUS REQUESTS: Ask for clarification in response and DO NOT update (response-only schema).

        STYLE:
        - Keep new_desc concise, structured, and readable.
        - Maintain important existing preferences unless explicitly removed.
        - Do not include any explanation outside the JSON.
        """
        
        # Call Perplexity to process the preference update
        perplexity_response = call_perplexity_chat(
            prompt=prompt,
            model="sonar-pro",
            max_tokens=1000,
            temperature=0.3
        )
        
        # Handle response from call_perplexity_chat
        if not perplexity_response:
            return {
                'success': False,
                'error': "Perplexity API returned no response"
            }
        
        # Check if there's an error in the response
        if 'error' in perplexity_response:
            return {
                'success': False,
                'error': f"Perplexity API error: {perplexity_response.get('error', 'Unknown error')}"
            }
        
        content = perplexity_response.get('content', '')
        
        # Try to parse the JSON from the content
        try:
            import json
            import re
            
            # Look for JSON in the content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_json = json.loads(json_str)
                # If no new_desc present (response-only), default to current user_desc
                has_new_desc = isinstance(parsed_json.get('new_desc'), str) and parsed_json.get('new_desc').strip() != ''
                resolved_new_desc = parsed_json.get('new_desc') if has_new_desc else user_desc

                return {
                    'success': True,
                    'new_desc': resolved_new_desc,
                    'response': parsed_json.get('response', '')
                }
            else:
                # If no JSON found, return the raw content as response
                return {
                    'success': True,
                    'new_desc': user_desc,  # Keep original if parsing fails
                    'response': content
                }
                
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw content
            return {
                'success': True,
                'new_desc': user_desc,  # Keep original if parsing fails
                'response': content
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }

# Test function
if __name__ == "__main__":
    # Test with sample data
    test_desc = """
    Financial goals: saving for a house
    Current banks/platforms: Mayapada Mobile
    Current investments: ETH and Bitcoin
    Interested in: Bitcoin and ETH
    News preferences: Market updates
    Region focus: Indonesian only
    """
    
    test_message = "How is bitcoin doing?"
    
    print("Testing Preference Updater...")
    result = update_user_preferences(test_desc, test_message)
    
    print(f"Result: {result}")
    
    # Save to JSON file
    try:
        import json
        with open('preference_update_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("Preference update result saved to 'preference_update_result.json'")
    except Exception as e:
        print(f"Error saving to JSON: {e}")
