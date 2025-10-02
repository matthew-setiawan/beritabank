import os
import json
from dotenv import load_dotenv
from perplexity import Perplexity

load_dotenv()

def call_perplexity_search(queries: list, max_results: int = 1) -> dict:
    """
    Call Perplexity AI search API with the given queries.
    
    Args:
        queries (list): List of search queries
        max_results (int): Maximum number of results to return
    
    Returns:
        dict: Response from Perplexity API with success/error status
    """
    try:
        from perplexity import Perplexity
        
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            return {
                'success': False,
                'error': 'PERPLEXITY_API_KEY not found in environment variables'
            }
        
        client = Perplexity(api_key=api_key)
        
        search = client.search.create(
            query=queries
        )
        print("Testing Content:")
        print(search)
        print("")
        
        # Return the raw response
        return {
            'success': True,
            'raw_response': search,
            'results': search.results[:max_results] if hasattr(search, 'results') else [],
            'total_results': len(search.results) if hasattr(search, 'results') else 0
        }
        
    except ImportError:
        return {
            'success': False,
            'error': 'Perplexity SDK not installed. Run: pip install perplexity'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }

def call_perplexity_chat(prompt: str, model: str = "sonar-pro", max_tokens: int = 1000, temperature: float = 0.3) -> dict:
    """
    Call Perplexity AI chat API with the given prompt.
    
    Args:
        prompt (str): The prompt to send to Perplexity
        model (str): The model to use (default: sonar-pro)
        max_tokens (int): Maximum tokens to generate
        temperature (float): Temperature for response generation
    
    Returns:
        dict: Response from Perplexity API with success/error status
    """
    try:
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            return {
                'success': False,
                'error': 'PERPLEXITY_API_KEY not found in environment variables'
            }
        
        client = Perplexity(api_key=api_key)
        
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Convert to clean JSON format
        return convert_completion_to_json(completion)
        
    except ImportError:
        return {
            'success': False,
            'error': 'Perplexity SDK not installed. Run: pip install perplexity'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }

def convert_completion_to_json(completion) -> dict:
    """
    Convert Perplexity completion object to a clean JSON format.
    
    Args:
        completion: Perplexity completion object
    
    Returns:
        dict: Clean JSON representation of the completion
    """
    try:
        # Extract the main content
        content = completion.choices[0].message.content if completion.choices else ""
        
        # Extract citations if available
        citations = getattr(completion, 'citations', [])
        
        # Extract search results if available
        search_results = []
        if hasattr(completion, 'search_results') and completion.search_results:
            for result in completion.search_results:
                search_results.append({
                    'title': getattr(result, 'title', ''),
                    'url': getattr(result, 'url', ''),
                    'date': getattr(result, 'date', ''),
                    'snippet': getattr(result, 'snippet', '')
                })
        
        # Extract usage information
        usage_info = {}
        if hasattr(completion, 'usage') and completion.usage:
            usage_info = {
                'prompt_tokens': getattr(completion.usage, 'prompt_tokens', 0),
                'completion_tokens': getattr(completion.usage, 'completion_tokens', 0),
                'total_tokens': getattr(completion.usage, 'total_tokens', 0),
                'cost': {
                    'total_cost': getattr(completion.usage.cost, 'total_cost', 0) if hasattr(completion.usage, 'cost') else 0
                } if hasattr(completion.usage, 'cost') else {}
            }
        
        return {
            'id': getattr(completion, 'id', ''),
            'model': getattr(completion, 'model', ''),
            'content': content,
            'citations': citations,
            'search_results': search_results,
            'usage': usage_info,
            'created': getattr(completion, 'created', 0),
            'object': getattr(completion, 'object', '')
        }
        
    except Exception as e:
        return {
            'error': f'Failed to convert completion to JSON: {str(e)}',
            'raw_completion': str(completion)
        }

# Test function
if __name__ == "__main__":
    # Test Perplexity search
    print("Testing Perplexity search...")
    result = call_perplexity_search([
        "What is the current price of Bitcoin?"
    ])
    print(f"Search Result: {result}")
    
    # Test Perplexity chat
    print("\nTesting Perplexity chat...")
    result = call_perplexity_chat("What are your main financial goals right now?: saving for a house, Which banks or platforms do you currently use?: Mayapada Mobile, What are you currently investing in?: ETH and bitcoin, Are there specific assets, sectors, or topics you'd like to follow?: Bitcoin and ETH, What type of financial news matters most to you?: Market updates, Do you want news focused on your region, or global coverage?: Indonesian only -> Provide summary news for this user's interests. In the content provide a structured: summary and advice. 1 paragraph each")
    print(f"Chat Result: {result}")
    
    # Write chat result to JSON file for easier reading
    try:
        with open('perplexity_chat_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("Chat result saved to 'perplexity_chat_result.json'")
    except Exception as e:
        print(f"Error saving to JSON: {e}")
