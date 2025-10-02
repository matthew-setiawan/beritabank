import os
import json
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

def generate_daily_summary(user_description: str) -> dict:
    """
    Generate daily financial summary and advice for a user based on their description.
    
    Args:
        user_description (str): User's financial goals, current investments, and interests
    
    Returns:
        dict: JSON with summary and advice in both English and Indonesian, plus search results
    """
    try:
        # Create the prompt for Perplexity
        prompt = f"""
        Based on this user's financial profile: {user_description}
        
        Provide a realistic, balanced daily financial summary and advice. Be honest about market conditions - don't sugarcoat or be overly optimistic.
        
        CRITICAL: Return ONLY valid JSON. No explanations, no extra text, no markdown formatting. Start with {{ and end with }}.
        
        {{
            "summary_en": "For EACH distinct interest mentioned by the user (assets, sectors, banks, platforms, regions), write a concise update for TODAY (1-3 sentences). Start each with the interest name (e.g., 'Bitcoin:'). Use SEMICOLONS (;) to separate different interests.",
            "summary_id": "Indonesian translation of summary_en using the SAME semicolon separators.",
            "advice_en": "Provide STRUCTURED, actionable guidance grouped by interest as numbered points. Each item must include Action, Rationale, and Risk in one compact line. Use SEMICOLONS (;) to separate different items and interests.",
            "advice_id": "Indonesian translation of advice_en using the SAME semicolon separators."
        }}
        
        Guidelines:
        - Identify interests from the user's profile (e.g., Bitcoin, ETH, specific banks/platforms, sectors, regions). If none are explicit, infer 1-3 most relevant interests from context.
        - SUMMARY: 1-3 sentences per interest. Include both positive and negative developments, and today's context. Separate interests with semicolons (;).
        - ADVICE: 1-2 numbered items per interest. Each item must include Action, Rationale, and Risk in one compact line.
        - Maintain balance: acknowledge volatility, uncertainty, and potential downsides. Avoid hype.
        - Use semicolons (;) as separators - this is JSON-safe and easy to split.
        - RETURN ONLY THE JSON OBJECT - NO OTHER TEXT.
        """
        
        # Call Perplexity to get the response
        perplexity_response = call_perplexity_chat(prompt)
        
        if not perplexity_response or 'error' in perplexity_response:
            return {
                'success': False,
                'error': f"Perplexity API error: {perplexity_response.get('error', 'Unknown error')}"
            }
        
        # Extract content from Perplexity response
        content = perplexity_response.get('content', '')
        search_results = perplexity_response.get('search_results', [])
        
        # Process search results to add image URLs
        enhanced_search_results = []
        for result in search_results:
            enhanced_result = {
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'date': result.get('date', ''),
                'snippet': result.get('snippet', ''),
                'image_url': ''
            }
            
            # Get image URL for the title
            try:
                from models.imageretriever import get_first_image_url
                image_url = get_first_image_url(result.get('title', ''))
                if image_url:
                    enhanced_result['image_url'] = image_url
            except Exception as e:
                print(f"Warning: Could not get image for '{result.get('title', '')}': {e}")
                # Continue without image URL
            
            enhanced_search_results.append(enhanced_result)
        
        # Try to parse the JSON from the content
        try:
            # First try direct parsing
            parsed_json = json.loads(content)
            return {
                    'success': True,
                    'summary_en': parsed_json.get('summary_en', ''),
                    'summary_id': parsed_json.get('summary_id', ''),
                    'advice_en': parsed_json.get('advice_en', ''),
                    'advice_id': parsed_json.get('advice_id', ''),
                    'search_results': enhanced_search_results
            }
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the content
            try:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    parsed_json = json.loads(json_str)
                    return {
                        'success': True,
                        'summary_en': parsed_json.get('summary_en', ''),
                        'summary_id': parsed_json.get('summary_id', ''),
                        'advice_en': parsed_json.get('advice_en', ''),
                        'advice_id': parsed_json.get('advice_id', ''),
                        'search_results': enhanced_search_results
                    }
                else:
                    # If no JSON found, return the raw content
                    return {
                        'success': True,
                        'summary_en': content,
                        'summary_id': '',
                        'advice_en': '',
                        'advice_id': '',
                        'search_results': enhanced_search_results
                    }
            except Exception as e:
                # If JSON parsing fails, return the raw content
                return {
                    'success': True,
                    'summary_en': content,
                    'summary_id': '',
                    'advice_en': '',
                    'advice_id': '',
                    'search_results': enhanced_search_results
                }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }

# Test function
if __name__ == "__main__":
    # Test with sample user description
    test_description = """
    The user is interested in Bitcoin, Ethereum, and XRP investment.
    """
    
    print("Testing Daily Summarizer...")
    result = generate_daily_summary(test_description)
    
    print(f"Result: {result}")
    
    # Save to JSON file
    try:
        with open('daily_summary_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("Daily summary saved to 'daily_summary_result.json'")
    except Exception as e:
        print(f"Error saving to JSON: {e}")
