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
        
        Provide a structured daily financial summary and advice. Be honest about market conditions - don't sugarcoat or be overly optimistic.
        
        CRITICAL: Return ONLY valid JSON. No explanations, no extra text, no markdown formatting. Start with {{ and end with }}.
        
        {{
            "summary_en": "Write exactly 2 paragraphs separated by pipe (|): 1) Bank Condition - Focus on bank stability and default risk (not stock performance), assess if banks mentioned are safe for deposits. **Bold all bank names** | 2) Interests - If user mentions crypto/stocks, summarize current market conditions in a few sentences. **Bold all asset names** (Bitcoin, ETH, etc.). If no specific interests mentioned, skip this paragraph.",
            "summary_id": "Indonesian translation of summary_en with the SAME 2-paragraph structure and **bold formatting**.",
            "advice_en": "Provide exactly 3 structured advice sections separated by pipe (|), each with 2 sentences: 1) **Bank Money Decision:** Should they pull or keep money in banks mentioned | 2) **Stocks to Watch:** This is not related to banking -> should just be about stocks or crypto advice based on user's description | 3) **New Opportunities:** Suggest new opportunities not currently investing in like 'look at Bank XXX/Crypto XXX/Stock XXX''.",
            "advice_id": "Indonesian translation of advice_en with the SAME 3-section structure and **bold formatting**."
        }}
        
        Guidelines:
        - SUMMARY: 2 paragraphs separated by pipe (|) - Bank Condition (default risk focus) and Interests (crypto/stocks if mentioned)
        - ADVICE: Exactly 3 sections separated by pipe (|), each with 2 sentences - Bank Money Decision, Stocks to Watch, New Opportunities
        - FORMATTING: **Bold** all bank names, asset names (Bitcoin, ETH, etc.), and section headers (Bank Money Decision:, Stocks to Watch:, New Opportunities:)
        - SEPARATOR: Use pipe (|) ONLY for separating sections. Do NOT use pipe (|) for any other purpose in the content.
        - Be specific with recommendations (e.g., "XXX Bank or Mutual Funds XXX has very good interest rate, check it out")
        - Maintain balance: acknowledge risks and volatility
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
            with open('daily_summary_result.json', 'w', encoding='utf-8') as f:
                json.dump(json.loads(content), f, indent=2, ensure_ascii=False)
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
