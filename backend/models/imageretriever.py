import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_first_image_url(query: str) -> str:
    """
    Get the first image URL from Google Custom Search API
    
    Args:
        query (str): Search query for the image
        
    Returns:
        str: URL of the first image found
        
    Raises:
        ValueError: If API key is not found
        Exception: If API request fails or no images found
    """
    # Get API key from environment (authenticates your requests)
    api_key = os.getenv('GOOGLE_CSE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_CSE_API_KEY not found in environment variables")
    
    # Get Custom Search Engine ID (specifies which search configuration to use)
    # Create one at: https://cse.google.com/ - set to search entire web (*)
    search_engine_id = os.getenv('GOOGLE_CSE_ID')
    if not search_engine_id:
        raise ValueError("GOOGLE_CSE_ID not found in environment variables. Create one at https://cse.google.com/")
    
    # Google Custom Search API endpoint
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        'searchType': 'image',
        'num': 1,  # Get only the first result
        'safe': 'medium'  # Safe search setting
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if we have search results
        if 'items' in data and len(data['items']) > 0:
            first_image = data['items'][0]
            return first_image['link']  # This is the image URL
        else:
            raise Exception("No images found for the query")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except KeyError as e:
        raise Exception(f"Unexpected API response format: {str(e)}")
    except Exception as e:
        raise Exception(f"Error getting image: {str(e)}")

if __name__ == "__main__":
    print("Testing image retriever...")
    result = get_first_image_url('BNI Siap Optimalkan Dana Rp55 Triliun untuk Dukung Pertumbuhan Ekonomi Nasional')
    print(f"Result: {result}")